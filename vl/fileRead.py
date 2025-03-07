import requests
import json

# kofe

def upload_file(file_path, user, MIME_type):   
    upload_url = "https://www.kofe.ai/v1/files/upload"
    headers = {
        # "Authorization": "Bearer app-xxxxxxxx",
        "Authorization": "Bearer app-mm40LkPE0iRewxyO1Ls7t6ra",        
    }
    
    try:
        print("上传文件中...")
        with open(file_path, 'rb') as file:
            if MIME_type == 'image':
                files = {
                    # 'file': (file_path, file, 'text/plain')  # 确保文件以适当的MIME类型上传 
                    'file': (file_path, file, 'image/png')  # 修改MIME类型为图片类型              
                }
                data = {
                    "user": user,
                    # "type": "TXT"  # 设置文件类型为TXT
                    "type": "IMAGE"  # 修改文件类型为IMAGE                
                }           
            elif MIME_type == 'application/pdf':
                files = {
                    # 'file': (file_path, file, 'text/plain')  # 确保文件以适当的MIME类型上传
                    # 'file': (file_path, file, 'image')  # 修改MIME类型为图片类型  
                    'file': (file_path, file, 'application/pdf')  # 修改MIME类型为图片类型              
                }
                data = {
                    "user": user,
                    # "type": "TXT"  # 设置文件类型为TXT
                    "type": "application/pdf"  # 修改文件类型为IMAGE                
                }                   
                          
            response = requests.post(upload_url, headers=headers, files=files, data=data)
            if response.status_code == 201:  # 201 表示创建成功
                print("文件上传成功")
                return response.json().get("id")  # 获取上传的文件 ID
            else:
                print(f"文件上传失败，状态码: {response.status_code}")
                return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None

def run_workflow(file_id, user, bizType, MIME_type, response_mode="blocking") -> str:
    workflow_url = "https://www.kofe.ai/v1/workflows/run"    
    headers = {
        "Authorization": "Bearer app-mm40LkPE0iRewxyO1Ls7t6ra",
        "Content-Type": "application/json"
    }

    if MIME_type == 'image':
        typeFile = "image"
    elif MIME_type == 'application/pdf':        
        typeFile = "document"

    data = {
        "inputs": {
            # "orig_mail": {
            #     # "transfer_method": "local_file",
            #     "transfer_method": "remote_url",
            #     "upload_file_id": file_id,
            #     # "type": "document"
            #     "type": "image"  # 修改类型为image
            # }
            "uploadFile": {
                # "transfer_method": "local_file",
                "transfer_method": "local_file",
                "upload_file_id": file_id,
                # "type": "document"
                "type": typeFile  # 修改类型为image
            },   

            "bizType" : bizType
        },
        "response_mode": response_mode,
        "user": user
    }

    try:
        print("运行工作流...")
        response = requests.post(workflow_url, headers=headers, json=data)
        if response.status_code == 200:
            print("工作流执行成功")
            return response.json()
        else:
            print(f"工作流执行失败，状态码: {response.status_code}")            
            return {"status": "error", "message": f"Failed to execute workflow, status code: {response.status_code}, response.content {response.content}"}
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"status": "error", "message": str(e)}


def bill_recognition(file_path, bizType, MIME_type):
    user = "abc-123"
    
    # 上传文件
    file_id = upload_file(file_path, user, MIME_type)
    if file_id:
        # 文件上传成功，继续运行工作流
        result = run_workflow(file_id, user, bizType, MIME_type)
        print(result)

        return result
    else:
        print("文件上传失败，无法执行工作流")



def extract_content(data, biz_type):
    if biz_type == '1':
        # 获取text1的内容
        text_content = data['data']['outputs']['text1']
        print(text_content)
        print('-----')

    if biz_type == '2':
        # 获取text2的内容
        text_content = data['data']['outputs']['text2']
        print(text_content)
        print('-----')        

    # 由于text1中的内容是一个json字符串,需要去掉```json和```标记
    text_json_str = text_content.replace('```json\n', '').replace('\n```', '')
    print(text_json_str)
    print('-----')

    # 将json字符串解析为Python对象
    text_data = json.loads(text_json_str)
    # print(text_data)
    # print(type(text_data))
    print('-----')

    return text_data


if __name__ == "__main__":
    # file_path = r"D:\mine\work\票据code\合同信息\gxht2.png"
    # biz_type = '1'
    # MIME_type = 'image'   
   
    # file_path = r"D:\mine\work\票据code\信用证\信用证样本\bohaiyinghangzheng.pdf"
    file_path = r"D:\mine\work\票据code\信用证\信用证样本\111.png"
    biz_type = '2'
    MIME_type = 'image'
    # MIME_type = 'application/pdf'    

    data = bill_recognition(file_path, biz_type, MIME_type)

    text_data = extract_content(data, biz_type)
    print(type(text_data))
