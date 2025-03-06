import requests
import json

# kofe

def upload_file(file_path, user):
    # upload_url = "https://api.kofe.ai/v1/files/upload"    
    upload_url = "https://www.kofe.ai/v1/files/upload"
    headers = {
        # "Authorization": "Bearer app-xxxxxxxx",
        "Authorization": "Bearer app-mm40LkPE0iRewxyO1Ls7t6ra",        
    }
    
    try:
        print("上传文件中...")
        with open(file_path, 'rb') as file:
            files = {
                # 'file': (file_path, file, 'text/plain')  # 确保文件以适当的MIME类型上传
                # 'file': (file_path, file, 'image')  # 修改MIME类型为图片类型  
                'file': (file_path, file, 'image/png')  # 修改MIME类型为图片类型              
            }
            data = {
                "user": user,
                # "type": "TXT"  # 设置文件类型为TXT
                "type": "IMAGE"  # 修改文件类型为IMAGE                
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

def run_workflow(file_id, user, response_mode="blocking"):
    # workflow_url = "https://api.kofe.ai/v1/workflows/run"
    workflow_url = "https://www.kofe.ai/v1/workflows/run"    
    headers = {
        "Authorization": "Bearer app-mm40LkPE0iRewxyO1Ls7t6ra",
        "Content-Type": "application/json"
    }

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
                "type": "image"  # 修改类型为image
            }            
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
            return {"status": "error", "message": f"Failed to execute workflow, status code: {response.status_code}"}
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # 使用示例
    # file_path = "{your_file_path}"
    file_path = r"D:\mine\work\票据code\合同信息\gxht2.png"
    # user = "difyuser"
    user = "abc-123"
    
    # 上传文件
    file_id = upload_file(file_path, user)
    if file_id:
        # 文件上传成功，继续运行工作流
        result = run_workflow(file_id, user)
        print(result)
    else:
        print("文件上传失败，无法执行工作流")
