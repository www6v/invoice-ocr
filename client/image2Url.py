
import base64
import time
import requests
import json


def localFileData():
    #######  合同
    # file = r"D:\mine\work\票据code\合同信息\gxht2.png"
    # file = r"D:\mine\work\票据code\合同信息\gxht10.png"
    # file = r"D:\mine\work\票据code\合同信息\http-1.png"   #  这个比较齐


    #######  信用证
    # file = r"D:\mine\work\票据code\信用证\信用证样本\111.png"

    #######  发票
    file = r"D:\mine\work\票据code\发票信息\04574546.png"

    # with open(r"", "rb") as pdf_file:   
    with open(file, "rb") as pdf_file:    
    # with open("/data/jupyterfile/wwk/invoicefile/invoice-pdf/correction/corretion_0-005.png", "rb") as pdf_file:
        pdf_data = pdf_file.read()    

    return pdf_data


def urlFileData(url):
    try:
        # 发送GET请求获取文件内容
        response = requests.get(url)
        
        # 检查请求是否成功
        response.raise_for_status()
        
        # 获取文件内容
        file_content = response.content
        
        # 将文件内容转换为Base64编码
        # base64_encoded = base64.b64encode(file_content)
        
        # 将bytes转换为字符串并返回
        # return base64_encoded.decode('utf-8')
        
        return file_content
    except requests.RequestException as e:
        print(f"下载文件时发生错误: {e}")
        return None
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        return None

def invoke(billUrl, taskType):
    # pdf_data = localFileData()

    pdf_data = urlFileData(billUrl)

    # 编码为Base64
    base64_encoded = base64.b64encode(pdf_data).decode('utf-8')

    # 目标 URL
    # url = "http://0.0.0.0:9999/api/v1/extract-key-info"
    url = "http://43.128.251.133:9999/api/v1/extract-key-info"

    # 请求数据
    ##### 发票  001,  合同 002,  信用证  004 
    data = {
        "flowId": "172549848941500000001",
        "taskType": taskType,
        "body": {            
            "fileInfo": 
                {
                    "fileType": "png",
                    "fileId": "1234567890",
                    "content": base64_encoded
                }
        }
    }


    # {
    # "flowId": 202408260000101001,
    # "taskType": "001",
    # "body":{
    #     "fileInfo":{
    #         "fileId": "1234567890",
    #         "fileType": "pdf",
    #         "content": 
    # 设置请求头，指定 Content-Type 为 application/json
    headers = {
        "Content-Type": "application/json"
    }

    sss = time.time()
    # 发送 POST 请求
    response = requests.post(url, data=json.dumps(data), headers=headers)
 
    # 打印响应结果
    if response.status_code == 200:
        print("请求成功！")
        print("响应数据：", response.json()['result'])  # 如果返回的是 JSON 数据
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("响应内容：", response.text)
    print(f"消耗时间{time.time()-sss}")

    return response
    # return response.json()['result']


def contractResult(response):
    return {'contractNo' : response.json()['result']['contract']['contractNo'] ,
            'contractType' : response.json()['result']['contract']['contractType'], 
             'contractDate' : response.json()['result']['contract']['contractDate'],
             'contractTradeType': response.json()['result']['contract']['contractTradeType'],
             'contractAmt': response.json()['result']['contract']['contractAmt'],
             'buyerName': response.json()['result']['contract']['buyerName'],
             'sellerName': response.json()['result']['contract']['sellerName'],
             'buyerSocialNo': response.json()['result']['contract']['buyerSocialNo'],
             'sellerSocialNo': response.json()['result']['contract']['sellerSocialNo']}


def invoiceResult(response):
    return {'invoiceType': response.json()['result']['invoiceList'][0]['invoiceType'] ,
            'invoiceNo': response.json()['result']['invoiceList'][0]['invoiceNo'], 
            'invoiceCode': response.json()['result']['invoiceList'][0]['invoiceCode'],
            'invoiceDate': response.json()['result']['invoiceList'][0]['invoiceDate'],
            'buyerSocialNo': response.json()['result']['invoiceList'][0]['buyerSocialNo'],
            'buyerName': response.json()['result']['invoiceList'][0]['buyerName'],
            'invoiceAmt': response.json()['result']['invoiceList'][0]['invoiceAmt'],
            'sellerName': response.json()['result']['invoiceList'][0]['sellerName'],
            'sellerSocialNo': response.json()['result']['invoiceList'][0]['sellerSocialNo'],
            'invoiceAmtNoTax': response.json()['result']['invoiceList'][0]['invoiceAmtNoTax'],
            'invoiceAmtTax': response.json()['result']['invoiceList'][0]['invoiceAmtTax'],
            'remark': response.json()['result']['invoiceList'][0]['remark']
            }


def invokeContract(billUrl, taskType):
    response = invoke(billUrl, taskType)
    return contractResult(response)

def invokeInvoice(billUrl, taskType):
    response = invoke(billUrl, taskType)
    return invoiceResult(response)


if __name__ == "__main__":
    # billUrl = 'https://telegraph-image-92x.pages.dev/file/b274deba01f752f233a88-a70e03baf946353f68.png'    
    # taskType = '004'

    # billUrl = 'https://telegraph-image-92x.pages.dev/file/f756ee357defe5306605d-0d5e0328d8b101ad5f.png' 
    # taskType = '002'
    # invokeContract(billUrl, taskType)

    billUrl = 'https://telegraph-image-92x.pages.dev/file/3a4ba0facd39cab09618a-fe2bfce84a8bc5abe3.png'
    taskType = '001'
    invokeInvoice(billUrl, taskType)

