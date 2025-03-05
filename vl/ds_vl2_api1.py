import requests 
import base64 
 
# 配置API密钥（从硅基流动控制台获取）
API_KEY = "sk-hioqapoqkyfwjobwoumzbhealcdzrxirbqkhbggcptgxvnnk"
 
def image_analysis(image_path):
    # 读取图片并转换为Base64编码 
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8") 
 
    # 构建API请求参数 
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "deepseek-vl2",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请详细描述这张图片的内容"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ],
        "temperature": 0.5,
        "max_tokens": 1000
    }
 
    # 发送请求 
    try:
        response = requests.post( 
            "https://api.siliconflow.com/v1/chat/completions", 
            headers=headers,
            json=payload 
        )
        response.raise_for_status() 
        return response.json()["choices"][0]["message"]["content"] 
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return None 
 
# 使用示例 
if __name__ == "__main__":
    # result = image_analysis("test.jpg")   
    result = image_analysis(r"D:\mine\work\票据code\合同信息\gxht2.png")    
    if result:
        print("图像识别结果：\n", result)