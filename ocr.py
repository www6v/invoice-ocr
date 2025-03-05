import re
import os
import json
import pymupdf
import zipfile
import xmltodict
import logging
import pdfplumber
from PIL import Image
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from paddlenlp import Taskflow
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from config import schema


# uie模型
ie_base = Taskflow(task='information_extraction',
                    model='uie-base',
                    position_prob=0.5,
                    precision='fp32',
                    batch_size=2,
                    task_path='/data/llm/models/uie_information_extraction/checkpoint/model_best',
                    max_seq_len=1024) # 基础模型-微调
ie_base.set_schema(schema=schema)
# 读光票证校正及多图拆分
card_detection_correction = pipeline(Tasks.card_detection_correction, model='/data/llm/models/cv_resnet18_card_correction')
# ppocr-v4

ocr = PaddleOCR(lang="ch",
                use_gpu=True,
                det_model_dir="/data/llm/models/ch_PP-OCRv4_det_server_infer/",
                use_angle_cls=True,
                ocr_version='PP-OCRv4',
                cls_model_dir="/data/llm/models/ch_ppocr_mobile_v2.0_cls_infer/",
                rec_model_dir="/data/llm/models/ch_PP-OCRv4_rec_server_infer/",
                det_limit_side_len=1000,
                warmup=True,
                det_db_score_mode="slow",
                rec_algorithm="CRNN",
                rec_batch_num=10
               )


def ocr_result(img_path):
# load dataset
    result = ocr.ocr(img_path)
    return result

def correction(image_name, save_dir_path):
    """
    parms dir_path: 待读取图片所在文件夹
    parms image_name: 待读取图片文件名称
    parms save_dir_path: 待保存图片文件夹
    return:
        polygons 框检得到的任意四边形四个顶点，依次为左上、右上、右下、左下
        scores 框检置信度，标识检测的可行度，值域 0 到 1 之间
        labels 卡证方向分类，枚举类型，0、1、2、3 依次表示卡证顺时针旋转 90度、180度、270度
        layout 复印件分类，枚举类型，0 表示非复印件，1 表示复印件
        output_imgs 矫正后的子图区域像素值
    """
    logging.info(f"矫正过程-文件路径{save_dir_path}/{image_name}")
    det_res = card_detection_correction(os.path.join(save_dir_path, image_name))
    # 转换成图片
    # 定义尺寸和DPI
    width_mm = 90
    height_mm = 52.5
    dpi = 300

    # 将毫米转换为像素：像素 = 毫米 * (DPI / 25.4)
    width_px = int(width_mm * (dpi / 25.4))
    height_px = int(height_mm * (dpi / 25.4))
    for i, res in enumerate(det_res['output_imgs']):
        image = Image.fromarray(res)
        fixed_size = (width_px, height_px)
        image = image.resize(fixed_size)
        # 设置DPI (例如，300 DPI)
        image.save(os.path.join(save_dir_path, f"correction_{i}_{image_name}"), lossless=True, dpi=(dpi, dpi))
    return det_res


def pdf2img_v2(pdf_name, save_dir_path, correct_flag=True):
    """
    parms pdf_name: 待读取pdf文件名称
    parms save_dir_path: pdf转成图片纠正后保存文件夹
    parms correct_flag: 是否纠正
    return: 纠正后详细信息
    """
    docs = pymupdf.open(os.path.join(save_dir_path, pdf_name))
    zoom_x = 1.33333333  # (1.33333333-->1056x816)   (2-->1584x1224)
    zoom_y = 1.33333333
    mat = pymupdf.Matrix(zoom_x, zoom_y).prerotate(0)
    logging.info(f"pdf页数--{docs.page_count}")
    for i in range(docs.page_count):
        page = docs.load_page(page_id=i) # 获取每一页
        pix = page.get_pixmap(matrix=mat, alpha=False)
        # 保存每一页到图片
        pix.save(os.path.join(save_dir_path, f"{page.number}.png"), jpg_quality=300)
        if correct_flag:
            logging.info("图片执行校正")
            correction(image_name=f"{page.number}.png", save_dir_path=save_dir_path)


def extract_font_names(save_dir_path, pdf_name):
    """
    后去每一页字体信息
    parms pdf_name: 待读取pdf文件名称
    return: 每页字体
    """
    font_names = {}
    docs = pymupdf.open(os.path.join(save_dir_path, pdf_name))

    for page_num, page in enumerate(docs):
        # 获取页面中所有字体信息
        fonts = page.get_fonts(full=True)
        font_names[page_num] = fonts
    docs.close()
    return font_names


def pdf2img(pdf_name, save_dir_path, correct_flag=True):
    """
    parms pdf_name: 待读取pdf文件名称
    parms save_dir_path: pdf转成图片纠正后保存文件夹
    parms correct_flag: 是否纠正
    return: 纠正后详细信息
    """
    # 指定DPI（300或更高）
    font_names = extract_font_names(save_dir_path=save_dir_path, pdf_name=pdf_name)
    images = convert_from_path(os.path.join(save_dir_path, pdf_name), dpi=300) 
    logging.info(f"pdf页数--{len(images)}")
    for i, image in enumerate(images):
        # 保存每一页到图片
        if correct_flag and (not font_names[i]):
            image.save(os.path.join(save_dir_path, f"{i}.png"), format='PNG')
            logging.info("图片执行校正")
            correction(image_name=f"{i}.png", save_dir_path=save_dir_path)
        else:
            image.save(os.path.join(save_dir_path, f"not_correction_{i}.png"), format='PNG')


def unzip_file(zip_path, unzip_path=None):
    """
    :param zip_path: ofd格式文件路径
    :param unzip_path: 解压后的文件存放目录
    :return: unzip_path
    """
    if not unzip_path:
        unzip_path = zip_path.split('.')[0]
    with zipfile.ZipFile(zip_path, 'r') as f:
        for file in f.namelist():
            f.extract(file, path=unzip_path)
    return unzip_path


def parse_ofd(path):
    """
    :param path: ofd文件存取路径
    """
    file_path = unzip_file(path)
    ofd_xml_path = f"{file_path}/OFD.xml"

    data_dict = {}
    # 解析发票类型

    with open(ofd_xml_path, "r", encoding="utf-8") as f:
        _text = f.read()
        tree = xmltodict.parse(_text)
        # 以下解析部分
        for row in tree['ofd:OFD']['ofd:DocBody']['ofd:DocInfo']['ofd:CustomDatas']['ofd:CustomData']:
            data_dict[row['@Name']] = row.get('#text')
    return data_dict

def parse_pdf(pdf_path):
    """
    :param path: ofd文件存取路径
    """
    res_dict = {}
    cust_lst = []
    brh_lst = []
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        total_lines_len = len(first_page.extract_text_lines())
        total_table_rows_len = sum([len(table) for table in first_page.extract_tables()])
        print("BBB", total_lines_len, total_table_rows_len)
        title_text = "".join([l['text'].strip().replace(" ", "") for l in
                              first_page.extract_text_lines()[:total_lines_len - total_table_rows_len - 1]])
        if "信用信息未披露" in title_text:
            list_type = "信用信息未披露名单"
        elif "持续逾期" in title_text:
            list_type = "持续逾期名单"
        elif "承兑人逾期" in title_text:
            list_type = "承兑人逾期名单"
        else:
            list_type = ""
        if re.findall(r'\d{4}年', title_text):
            list_year = re.findall(r'\d{4}年', title_text)[0].replace("年", "")
        else:
            list_year = ""
        if re.findall(r'\d{1,2}月', title_text):
            list_month = re.findall(r'\d{1,2}月', title_text)[0].replace("月", "").zfill(2)
        else:
            list_month = ""
        if re.findall(r'\d{1,2}[日号]', title_text):
            list_day = re.findall(r'\d{1,2}[日号]', title_text)[0].replace("日", "").replace("号", "").zfill(2)
        else:
            list_day = ""
        list_date = f"{list_year}{list_month}{list_day}"
        res_dict["listDate"] = list_date
        res_dict["listType"] = list_type

        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                if "企业名称" in table[0]:
                    for row in table[1:]:
                        row_dict = {"no": row[0], "name": row[1], "code": row[2]}
                        cust_lst.append(row_dict)
                elif "金融机构名称" in table[0]:
                    for row in table[1:]:
                        row_dict = {"no": row[0], "name": row[1], "code": row[2]}
                        brh_lst.append(row_dict)
                else:
                    continue
        res_dict["custList"] = cust_lst
        res_dict["brhList"] = brh_lst
    return res_dict



if __name__ == "__main__":
    det_res = card_detection_correction("/data/ocr-file/d5cdd08d-bab5-5774-a08d-b6a71722301f/0.png")
    # import pandas as pd
    # pdf_path = r'/data/jupyterfile/wwk/名单/截至2024年7月31日持续逾期名单.pdf'
    # res = parse_pdf(pdf_path)
    # cust_df = pd.DataFrame(res['custList'])
    # cust_df.to_excel('/data/jupyterfile/wwk/名单/截至2024年7月31日持续逾期名单.xlsx', index=False)
    # print(cust_df.head())
    # print(det_res['output_imgs'])
    print(len(det_res['output_imgs']))
