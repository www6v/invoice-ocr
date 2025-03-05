

import requests
import json

# 硅基流动API的URL
api_url = "https://api.siliconflow.com/v1/images/generate"  # wrong

# 你的API密钥
api_key = "sk-hioqapoqkyfwjobwoumzbhealcdzrxirbqkhbggcptgxvnnk"

# 请求头，包含API密钥
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 请求体，包含模型名称和文本描述
data = {
    "model": "deepseek-ai/Janus-Pro-7B",
    "prompt": "a futuristic cityscape at sunset",
    "num_images": 1,
    "image_size": "1024x1024"
}

# 发送POST请求
response = requests.post(api_url, headers=headers, data=json.dumps(data))

# 检查响应状态
if response.status_code == 200:
    # 解析响应数据
    result = response.json()
    image_url = result['data'][0]['url']
    print("Generated Image URL:", image_url)
else:
    print("Failed to generate image:", response.text)