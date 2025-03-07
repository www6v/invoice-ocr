import os
import json
import shutil
import base64
import logging
import uuid
from ocr import correction, pdf2img, parse_pdf
from format_output import output_invoice, output_contract
from fastapi import FastAPI, Request, Body
from config import dir_path
app = FastAPI()

logging.basicConfig(filename="invoice_info.log", level=logging.INFO)

def base642file(base64_text, save_file):
    """
    以url安全模式解码后保存到本地
    :param base64_text: 编码后字符
    :param save_file: 保存地址
    :return:
    """
    base64_text = base64_text.replace("\n", "").replace("\r", "")

    # 尝试解码 Base64 字符串
    if len(base64_text) % 4 != 0:
        padding_num = 4 - len(base64_text) % 4
        base64_text += '=' * padding_num
    dStr = base64.urlsafe_b64decode(base64_text)
    with open(save_file, "wb") as file:
        file.write(dStr)

def save_origin_file(save_dir_path, file_content, file_type):
    if not os.path.exists(save_dir_path):
        os.makedirs(save_dir_path)
    else:
        shutil.rmtree(save_dir_path)
        os.makedirs(save_dir_path)
    logging.info(f"文件路径--{save_dir_path}")
    # 保存源文件
    base642file(base64_text=file_content, save_file=os.path.join(save_dir_path, f"origin.{file_type}"))

def task_invoice(info):
    # 创建文件目录
    file_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, info['body']['fileInfo']['fileId']))
    file_type = info['body']['fileInfo']['fileType']
    file_content = info['body']['fileInfo']['content']
    save_dir_path = os.path.join(dir_path, file_id)
    save_origin_file(save_dir_path, file_content, file_type)

    if file_type in ['pdf']:
        logging.info(f"文件类型--pdf")
        pdf2img(pdf_name=f"origin.pdf", save_dir_path=save_dir_path)
    elif file_type in ['jpeg', 'jpg', 'png', 'webp']:
        logging.info(f"文件类型--图片")
        correction(image_name=f"origin.{file_type}", save_dir_path=save_dir_path)
    else:
        return {"flowId": info['flowId'],
                "taskType": info['taskType'],
                "retStatus": 1,
                "retMsg": "文件类型错误，请上传pdf或图片",
                "result": {"invoiceList": []}}
    # 根据源文件类型，处理成矫正后图片
    ocr_res = output_invoice(save_dir_path)
    if ocr_res:
        res_info = {"flowId": info['flowId'],
                    "taskType": info['taskType'],
                    "retStatus": 0,
                    "retMsg": "处理成功",
                    "result": {"invoiceList": ocr_res}}
    else:
        res_info = {"flowId": info['flowId'],
                    "taskType": info['taskType'],
                    "retStatus": 1,
                    "retMsg": "解析信息失败",
                    "result": {"invoiceList": []}}
    return res_info

def task_contract(info):
    # 创建文件目录
    # info['body']是一个list目前业务逻辑只取一张
    """    {
        "flowId": "202408260000101002",
        "taskType": "002",
        "body": {
            "fileId": "123456789012345",
            "fileInfos": [
                {
                    "fileType": "jpg",
                    "content": "aldjfoafaavnnaoijdioajflfjlkadoiejoaf 121213131312..."
                },
                {
                    "fileType": "jpg",
                    "content": "aldjfoafaavnnaoijdioajflfjlkadoiejoaf adfafafaeaaa..."
                }
            ]
        }
    }"""

    print(info)
    print('---')

    file_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, info['body']['fileId']))
    file_type = info['body']['fileInfos'][0]['fileType']
    file_content = info['body']['fileInfos'][0]['content']
    save_dir_path = os.path.join(dir_path, file_id)
    save_origin_file(save_dir_path, file_content, file_type)
    # 根据源文件类型，处理成矫正后图片
    if file_type in ['pdf']:
        logging.info(f"文件类型--pdf")
        pdf2img(pdf_name=f"origin.pdf", save_dir_path=save_dir_path, correct_flag=False)
        ocr_res = output_contract([f for f in sorted(os.listdir(save_dir_path)) if ".png" in f], save_dir_path)
    elif file_type in ['jpeg', 'jpg', 'png', 'webp']:
        logging.info(f"文件类型--图片")
        ocr_res = output_contract([f for f in sorted(os.listdir(save_dir_path))], save_dir_path)
    else:
        return {"flowId": info['flowId'],
                "taskType": info['taskType'],
                "retStatus": 1,
                "retMsg": "文件类型错误，请上传pdf或图片",
                "result": {"contract": {}}}

    res_info = {"flowId": info['flowId'],
                "taskType": info['taskType'],
                "retStatus": 0,
                "retMsg": "处理成功",
                "result": {"contract": ocr_res}}
    return res_info

def task_list(info):
    """
    {"flowId": "202408260000101003",
    "taskType": "003",
    "body": {
    "fileInfo": {
    "fileId": "1234567890",
    "fileType": "pdf",
    "content": "aldjfoafaavnnaoijdioajflfjlkadoiejoaf dfalkapoijadfldkkkkkk..."}}}
    :param info:
    :return:
    """
    # 创建文件目录
    file_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, info['body']['fileInfo']['fileId']))
    file_type = info['body']['fileInfo']['fileType']
    file_content = info['body']['fileInfo']['content']
    save_dir_path = os.path.join(dir_path, file_id)
    save_origin_file(save_dir_path, file_content, file_type)
    # 根据源文件类型，处理成矫正后图片
    if file_type in ['pdf']:
        logging.info(f"文件类型--pdf")
        ocr_res = parse_pdf(f"{save_dir_path}/origin.pdf")
    else:
        return {"flowId": info['flowId'],
                "taskType": info['taskType'],
                "retStatus": 1,
                "retMsg": "文件类型错误，请上传pdf",
                "result": {"custList": [], "brhList": []}}

    res_info = {"flowId": info['flowId'],
                "taskType": info['taskType'],
                "retStatus": 0,
                "retMsg": "处理成功",
                "result": ocr_res}
    return res_info
@app.post("/api/v1/extract-key-info")
async def make_invoice_info(request: Request,
                            info: dict = Body(..., description="发票信息")):
    """
    1发票：传入文件pdf可多张图片，图片只一张
    2合同：每次都是作为一份文件
    3名单：按pdf进行解析
    :param request:
    :param info: 请求体
    :return: 响应体
    """
    if info['taskType'] in "001":
        logging.info(f"执行发票任务")
        try:
            res_info = task_invoice(info)
        except Exception as e:
            logging.error(f"{info['flowId']} Error: {e}")
            res_info = dict(flowId=info['flowId'],
                            taskType=info['taskType'],
                            result={"invoiceList": []},
                            retStatus=1,
                            retMsg=str(e))
    elif info['taskType'] in "002":
        logging.info(f"执行合同任务")
        try:
            res_info = task_contract(info)
        except Exception as e:
            logging.error(f"{info['flowId']} Error: {e}")
            res_info = dict(flowId=info['flowId'],
                            taskType=info['taskType'],
                            result={"contract": {}},
                            retStatus=1,
                            retMsg=str(e))
    elif info['taskType'] in "003":
        logging.info(f"执行名单任务")
        try:
            res_info = task_list(info)
        except Exception as e:
            logging.error(f"{info['flowId']} Error: {e}")
            res_info = dict(flowId=info['flowId'],
                            taskType=info['taskType'],
                            result={"custList": [], "brhList":[]},
                            retStatus=1,
                            retMsg=str(e))
    else:
        res_info = dict(flowId=info['flowId'],
                    taskType=info['taskType'],
                    result={},
                    retStatus=1,
                    retMsg="任务类型错误")

    return res_info


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9999)
