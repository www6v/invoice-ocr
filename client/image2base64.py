import base64


# 读取PDF文件
# with open("/data/jupyterfile/wwk/invoicefile/invoice-pdf/03100160031132504296.pdf", "rb") as pdf_file:
with open(r"D:\mine\work\票据 OCR-代码\发票信息\fapiao-14.pdf", "rb") as pdf_file:
    pdf_data = pdf_file.read()

# 编码为Base64
base64_encoded = base64.b64encode(pdf_data).decode('utf-8')

# 输出Base64字符串
print(base64_encoded)



