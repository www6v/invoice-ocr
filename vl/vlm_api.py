
import os
from openai import OpenAI


##### 千问 api

client = OpenAI(
    # api_key=os.getenv("DASHSCOPE_API_KEY"),

    api_key="",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# completion = client.chat.completions.create(
#     model="qwen-vl-plus",  # qwen-vl-max-latest 
#     messages=[
#         {
#             "role": "system",
#             "content": [{"type": "text", "text": "You are a helpful assistant."}],
#         },
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"
#                     },
#                 },
#                 {"type": "text", "text": "图中描绘的是什么景象?"},
#             ],
#         },
#     ],
# )


completion = client.chat.completions.create(
    model="qwen-vl-plus",  # qwen-vl-max-latest 
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": r"D:\mine\work\票据code\合同信息\gxht2.png"
                    },
                },
                {"type": "text", "text": "图中描绘的是什么景象?"},
            ],
        },
    ],
)

if __name__ == "__main__":
  print(completion.choices[0].message.content)
