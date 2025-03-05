import requests
import json
import base64
import gradio as gr


history = []


def main(filepath):
    # 读取PDF文件
    with open(filepath, "rb") as file:
        file_data = file.read()

    # 编码为Base64
    base64_encoded = base64.b64encode(file_data).decode('utf-8')

    # 目标 URL
    url = "http://0.0.0.0:9999/api/v1/extract-key-info"
    if "pdf" in filepath:
        file_type = "pdf"
    else:
        file_type = "png"

    # 请求数据
    data = {
        "flowId": "agent-contract",
        "taskType": "002",
        "body": {
            "fileId": "ttt",
            "fileInfos": [
                {
                    "fileType": file_type,
                    "fileName": "mmm",
                    "content": base64_encoded
                }
            ]
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    # 发送 POST 请求
    response = requests.post(url, data=json.dumps(data), headers=headers)

    # 打印响应结果
    if response.status_code == 200:
        print("请求成功！")
        print("响应数据：", response.json()['result'])  # 如果返回的是 JSON 数据
        res_data = []
        res_data.append("\n".join([f"{k}:{v}" for k,v in response.json()['result']['contract'].items()]))
        return [("合同解析结果", "\n\n".join(res_data))]
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("响应内容：", response.text)
        return [("合同解析结果", "解析失败")]

def clear_history():
    global history
    history = []
    return history

with gr.Blocks(css="styles.css") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown('## 发票关键信息提取')
            gr.Markdown("""
                1.**上传合同文档-pdf/图片**  
                2.**输出关键信息**：合同类型，合同编号，购买方名称，销售方名称，合同总金额，签订日期，贸易类型 
            """)
            clear_button = gr.Button("清空历史", elem_id="clear_button")
        with gr.Column(scale=3):
            chatbot_output = gr.Chatbot(label="智能体生成内容", elem_id="chatbot_output",
                                        elem_classes="output-box")
            with gr.Row():
                file_input = gr.File(type="filepath",
                                    label="上传文件（PDF/DOCX）",
                                    elem_id="file_input",
                                    elem_classes="input-box")
                generate_button = gr.Button("一键生成", elem_id="generate_button", elem_classes="lar-button")


    # 一键生成按钮触发文件上传和生成
    generate_button.click(main, inputs=file_input, outputs=[chatbot_output])
    clear_button.click(clear_history, inputs=None, outputs=[chatbot_output])

if __name__ == "__main__":
    demo.launch(server_port=9200, server_name="0.0.0.0")