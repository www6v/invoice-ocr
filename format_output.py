import os
import re
import cn2an
import logging
from ocr import ie_base, ocr_result
# from vlm import qwen2_vl
from config import hans_num_pattern, code_pattern, y_m_d_pattern, letter_num_pattern, amt_num_pattern,contract_prompt, json_pattern
from vl.fileRead import bill_recognition, extract_content

def output_invoice(save_dir_path):
    ocr_res_lst = []
    for png_name in os.listdir(save_dir_path):
        if "correction" not in png_name:
            continue
        ocr_res = ocr_result(img_path=os.path.join(save_dir_path,png_name))
        text_ocr_res = ';'.join([data[-1][0] for data in ocr_res[0]])
        logging.info(f"OCR解析结果{text_ocr_res}")
        uie_res = (ie_base(text_ocr_res))[0]
        ocr_info = uie_res
        logging.info(f"UIE解析结果{ocr_info}")
        try:
            invoiceAmtChn = re.findall(hans_num_pattern,
                                       ocr_info.get('invoice-amt-chn', [{"text": ""}])[0]['text'].replace(";", ""))
            if invoiceAmtChn:
                invoiceAmtChn = invoiceAmtChn[0]
            invoiceTypeText = ocr_info.get('invoice-type', [{"text": ""}])[0]['text'].replace(";", "")

            invoiceNo = re.findall(code_pattern,
                                  ocr_info.get('invoice-no', [{"text": ""}])[0]['text'].replace(";", ""))
            if invoiceNo and (len(invoiceNo[0])==8 or len(invoiceNo[0])==20) :
                invoiceNo = invoiceNo[0]
            else:
                invoiceNo = ""

            if "电子" in invoiceTypeText and len(invoiceNo)==20:
                invoiceType = "IT00"
            elif ("专用" in invoiceTypeText) or ("支用" in invoiceTypeText) or ("用" in invoiceTypeText and "票" in invoiceTypeText):
                invoiceType = "IT01"
            elif "普通" in invoiceTypeText:
                invoiceType = "IT02"
            else:
                invoiceType = ""

            invoiceCode = re.findall(code_pattern,
                                    ocr_info.get('invoice-code', [{"text": ""}])[0]['text'].replace(";", ""))
            if invoiceCode:
                invoiceCode = invoiceCode[0]
            else:
                invoiceCode = ""

            invoiceDate = re.findall(y_m_d_pattern,
                                    ocr_info.get('invoice-date', [{"text": ""}])[0]['text'].replace(";", ""))
            logging.info(f"日期数据--{invoiceDate}")
            if invoiceDate:
                invoiceDate = invoiceDate[0].replace('年', '').replace('月', '').replace('日', '')
            else:
                invoiceDate = ""
            buyerSocialNo = re.findall(letter_num_pattern,
                                        ocr_info.get('invoice-buyer-id', [{"text": ""}])[0]['text'].replace(";", ""))
            if buyerSocialNo:
                buyerSocialNo = buyerSocialNo[0]
            else:
                buyerSocialNo = ""

            buyerName = ocr_info.get('invoice-buyer', [{"text": ""}])[0]['text']
            if buyerName:
                buyerName = buyerName.replace(";", "").replace("：", ":").replace("（", "(").replace("）", ")").split(":")[-1]
            else:
                buyerName = ""

            invoiceAmt = re.findall(amt_num_pattern,
                                    ocr_info.get('invoice-amt-num', [{"text": ""}])[0]['text'].replace(";", ""))
            if invoiceAmt:
                invoiceAmt = invoiceAmt[0]
            else:
                invoiceAmt = ""

            sellerName = ocr_info.get('invoice-seller', [{"text": ""}])[-1]['text']
            if sellerName:
                sellerName = sellerName.replace(";", "").replace("：",":").replace("（", "(").replace("）", ")").split(":")[-1]
            else:
                sellerName = ""

            sellerSocialNo = re.findall(letter_num_pattern,
                                       ocr_info.get('invoice-seller-id', [{"text": ""}])[-1]['text'].replace(";", ""))
            if sellerSocialNo:
                sellerSocialNo = sellerSocialNo[0]
            else:
                sellerSocialNo = ""

            invoiceAmtNoTax = re.findall(amt_num_pattern,
                                        ocr_info.get('invoice-amt-not-tax', [{"text": ""}])[0]['text'].replace(";", ""))
            if invoiceAmtNoTax:
                invoiceAmtNoTax = invoiceAmtNoTax[0]
            else:
                invoiceAmtNoTax = ""

            invoiceAmtTax = re.findall(amt_num_pattern,ocr_info.get('invoice-amt-tax', [{"text": ""}])[0]['text'].replace(";", ""))
            if invoiceAmtTax:
                invoiceAmtTax = invoiceAmtTax[0]
            else:
                invoiceAmtTax = ""

            invRemark = ""
            logging.info(f"大写数字--{invoiceAmtChn}")
            try:
                arabic_number = cn2an.cn2an(invoiceAmtChn.replace("整","").replace("元零","元").replace(" ","").replace("角整","角").replace("圆","元").replace("园","元"), "smart")
                invoiceAmt = str(float(arabic_number))
            except:
                try:
                    invoiceAmt = str(float(invoiceAmt.replace("。", ".")))
                except:
                    invoiceAmt = ""
            
            if (not invoiceAmtNoTax) and invoiceAmtTax and invoiceAmt:
                invoiceAmtNoTax = float(invoiceAmt) - float(invoiceAmtTax)

            tmp = {"invoiceType":invoiceType,
                "invoiceNo":invoiceNo,
                "invoiceCode":invoiceCode,
                "invoiceDate":invoiceDate,
                "buyerSocialNo":buyerSocialNo,
                "buyerName":buyerName,
                "invoiceAmt":invoiceAmt,
                "sellerName":sellerName,
                "sellerSocialNo":sellerSocialNo,
                "invoiceAmtNoTax":invoiceAmtNoTax,
                "invoiceAmtTax":invoiceAmtTax,
                "remark":invRemark}
            ocr_res_lst.append(tmp)
        except Exception as e:
            logging.error(f"uie解析失败--{e}")
            tmp = {
                   "invoiceType": "",
                   "invoiceNo": "",
                   "invoiceCode": "",
                   "invoiceDate": "",
                   "buyerSocialNo": "",
                   "buyerName": "",
                   "invoiceAmt": "",
                   "sellerName": "",
                   "sellerSocialNo": "",
                   "invoiceAmtNoTax": "",
                   "invoiceAmtTax": "",
                   "remark": ""}
            ocr_res_lst.append(tmp)
    return ocr_res_lst

def output_contract(png_list, save_dir_path):
    ocr_res_dict = {}
    message_content = []
    for png in png_list:
        message_content.append(
                        {
                            "type": "image",
                            "image": "file://" + f"{save_dir_path}/{png}"
                        })
    message_content.append({"type":"text",
                            "text":contract_prompt})
    messages = [{"role":"user",
                "content": message_content}]


    ##### qwen api
    file_path = f"{save_dir_path}/{png}"  ###
    biz_type = '1' ### 合同
    MIME_type = 'image'
    data = bill_recognition(file_path, biz_type, MIME_type)
    output_dict = extract_content(data, biz_type)
    
    ##### 本地qwen 
    # output_dict = qwen2_vl(messages, json_pattern)
    

    ocr_res_dict['contractNo'] = output_dict.get("合同编号", '')
    if "订单" in output_dict.get("合同类型", ''):
        contract_type = "TIT02"
    else:
        contract_type = "TIT01"
    ocr_res_dict['contractType'] = contract_type

    contract_date = re.findall(y_m_d_pattern,
                               output_dict.get("签订日期", ''))
    contract_date_num = re.findall(r'\b\d{8}\b', output_dict.get("签订日期", ''))
    if contract_date:
        year = re.findall(r'\d{4}年', contract_date[0])[0].replace("年", "")
        month = re.findall(r'\d{1,2}月', contract_date[0])[0].replace("月", "").zfill(2)
        day = re.findall(r'\d{1,2}[日号]', contract_date[0])[0].replace("日", "").replace("号", "").zfill(2)
        contract_date = f"{year}{month}{day}"
    elif contract_date_num:
        contract_date = contract_date_num[0]
    else:
        contract_date = ""
    ocr_res_dict['contractDate'] = contract_date

    if "货物" in output_dict.get("贸易类型", ''):
        trade_type = "TM01"
    elif "货服" in output_dict.get("贸易类型", ''):
        trade_type = "TM03"
    elif "服务" in output_dict.get("贸易类型", ''):
        trade_type = "TM02"
    else:
        trade_type = ""
    ocr_res_dict['contractTradeType'] = trade_type
    try:
        contract_amt = cn2an.cn2an(output_dict.get("合同总金额", '').replace(" ","").replace("元零","元").replace("角整","角").replace("圆","元").replace("园","元"), "smart")
    except:
        contract_amt_chn = re.findall(hans_num_pattern,
                                output_dict.get("合同总金额", ''))
        contract_amt_num = re.findall(amt_num_pattern,
                                output_dict.get("合同总金额", ''))
        if contract_amt_chn and len(contract_amt_chn)>1:
            try:
                contract_amt = cn2an.cn2an(contract_amt_chn[0].replace("圆","元").replace("园","元"), "smart")
            except:
                contract_amt = ""
        elif contract_amt_num and len(contract_amt_chn)>1:
            try:
                contract_amt = contract_amt_num[0]
            except:
                contract_amt = ""
        else:
            contract_amt = ""
    ocr_res_dict['contractAmt'] = contract_amt

    ocr_res_dict['buyerName'] = output_dict.get("购买方名称", '')
    ocr_res_dict['sellerName'] = output_dict.get("销售方名称", '')
    ocr_res_dict['buyerSocialNo'] = output_dict.get("购买方统一社会信用码", '')
    ocr_res_dict['sellerSocialNo'] = output_dict.get("销售方统一社会信用码", '')
    logging.info("合同数据解析成功")
    return ocr_res_dict




def output_creditLetter(png_list, save_dir_path):
    ocr_res_dict = {}
    message_content = []
    for png in png_list:
        message_content.append(
                        {
                            "type": "image",
                            "image": "file://" + f"{save_dir_path}/{png}"
                        })
    message_content.append({"type":"text",
                            "text":contract_prompt})
    messages = [{"role":"user",
                "content": message_content}]


    ##### qwen api
    file_path = f"{save_dir_path}/{png}"  ###
    biz_type = '2' ### 信用证
    MIME_type = 'image'
    data = bill_recognition(file_path, biz_type, MIME_type)
    output_dict = extract_content(data, biz_type)
    
    ##### 本地qwen 
    # output_dict = qwen2_vl(messages, json_pattern)
    

    ##### 
    # ocr_res_dict['contractNo'] = output_dict.get("合同编号", '')
    # if "订单" in output_dict.get("合同类型", ''):
    #     contract_type = "TIT02"
    # else:
    #     contract_type = "TIT01"
    # ocr_res_dict['contractType'] = contract_type

    # contract_date = re.findall(y_m_d_pattern,
    #                            output_dict.get("签订日期", ''))
    # contract_date_num = re.findall(r'\b\d{8}\b', output_dict.get("签订日期", ''))
    # if contract_date:
    #     year = re.findall(r'\d{4}年', contract_date[0])[0].replace("年", "")
    #     month = re.findall(r'\d{1,2}月', contract_date[0])[0].replace("月", "").zfill(2)
    #     day = re.findall(r'\d{1,2}[日号]', contract_date[0])[0].replace("日", "").replace("号", "").zfill(2)
    #     contract_date = f"{year}{month}{day}"
    # elif contract_date_num:
    #     contract_date = contract_date_num[0]
    # else:
    #     contract_date = ""
    # ocr_res_dict['contractDate'] = contract_date

    # if "货物" in output_dict.get("贸易类型", ''):
    #     trade_type = "TM01"
    # elif "货服" in output_dict.get("贸易类型", ''):
    #     trade_type = "TM03"
    # elif "服务" in output_dict.get("贸易类型", ''):
    #     trade_type = "TM02"
    # else:
    #     trade_type = ""
    # ocr_res_dict['contractTradeType'] = trade_type
    # try:
    #     contract_amt = cn2an.cn2an(output_dict.get("合同总金额", '').replace(" ","").replace("元零","元").replace("角整","角").replace("圆","元").replace("园","元"), "smart")
    # except:
    #     contract_amt_chn = re.findall(hans_num_pattern,
    #                             output_dict.get("合同总金额", ''))
    #     contract_amt_num = re.findall(amt_num_pattern,
    #                             output_dict.get("合同总金额", ''))
    #     if contract_amt_chn and len(contract_amt_chn)>1:
    #         try:
    #             contract_amt = cn2an.cn2an(contract_amt_chn[0].replace("圆","元").replace("园","元"), "smart")
    #         except:
    #             contract_amt = ""
    #     elif contract_amt_num and len(contract_amt_chn)>1:
    #         try:
    #             contract_amt = contract_amt_num[0]
    #         except:
    #             contract_amt = ""
    #     else:
    #         contract_amt = ""
    # ocr_res_dict['contractAmt'] = contract_amt

    # ocr_res_dict['buyerName'] = output_dict.get("购买方名称", '')
    # ocr_res_dict['sellerName'] = output_dict.get("销售方名称", '')
    # ocr_res_dict['buyerSocialNo'] = output_dict.get("购买方统一社会信用码", '')
    # ocr_res_dict['sellerSocialNo'] = output_dict.get("销售方统一社会信用码", '')


    # logging.info("合同数据解析成功")



    #####
    ocr_res_dict['creditLetterNo'] = output_dict.get("信用证编号", '')
    ocr_res_dict['creditLetterDate'] = output_dict.get("开证日期", '')
    ocr_res_dict['creditLetterApplicant'] = output_dict.get("申请人", '')
    ocr_res_dict['creditLetterProfits'] = output_dict.get("受益人", '')
    ocr_res_dict['creditLetterAmount'] = output_dict.get("金额", '')
    ocr_res_dict['advisingBank'] = output_dict.get("通知行", '')
    ocr_res_dict['isNegotiated'] = output_dict.get("是否可议付", '')
    ocr_res_dict['isTransfer'] = output_dict.get("是否可转让", '')
    ocr_res_dict['isBonded'] = output_dict.get("是否可保税", '')


    logging.info("信用证数据解析成功")

    return ocr_res_dict
