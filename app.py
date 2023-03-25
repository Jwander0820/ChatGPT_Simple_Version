from flask import Flask, render_template, request, jsonify, make_response, send_file
import openai
import json
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
api_key = config["api"]["key"]

openai.api_key = api_key

app = Flask(__name__)

# 初始化對話歷史
messages = []
oneshot_message = []


# 此函數負責向GPT-3 API發送請求並返回AI的回應
def chat_gpt_response(prompt, chat_type, initial_system=None):
    global messages
    oneshot_message = []  # 將 oneshot_message 改為局部變量
    if initial_system and not any(msg['role'] == 'system' for msg in messages):
        messages.append({"role": "system", "content": initial_system})

    if initial_system and not any(msg['role'] == 'system' for msg in oneshot_message):
        oneshot_message.append({"role": "system", "content": initial_system})
    model_engine = "gpt-3.5-turbo"  # 使用gpt-3.5-turbo模型
    # 如果對話類型為"single"，即一次性對話
    if chat_type == "single":
        oneshot_message.append({"role": "user", "content": prompt})
        # 向API發送請求
        response = openai.ChatCompletion.create(
            model=model_engine,
            max_tokens=1024,
            temperature=0.5,
            messages=oneshot_message
        )
        # 從API返回的回應中提取AI回應的文本
        ai_msg = response.choices[0].message.content.replace('\n', '')
        # 將AI回應添加到對話歷史中
        oneshot_message.append({"role": "assistant", "content": ai_msg})
        print(oneshot_message)
        return ai_msg

    # 如果對話類型為"continuous"，即連續對話
    elif chat_type == "continuous":
        # 將用戶的提問添加到對話歷史中
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=model_engine,
            max_tokens=2048,
            temperature=0.5,
            messages=messages
        )

        ai_msg = response.choices[0].message.content.replace('\n', '')
        # 將AI回應添加到對話歷史中
        messages.append({"role": "assistant", "content": ai_msg})
        print(messages)
        return ai_msg


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    input_text = request.form['input_text']
    chat_type = request.form['chat_type']
    initial_system = request.form.get('initial_system')
    response_text = chat_gpt_response(input_text, chat_type, initial_system)
    if chat_type == "single":
        return jsonify(response=response_text, history=oneshot_message)
    else:
        return jsonify(response=response_text, history=messages)


# 此函數將對話歷史生成為Markdown文件
def generate_md_file(messages, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for message in messages:
            f.write(f"{message['role']}: {message['content']}\n")
            if message['role'] == "assistant":
                f.write('---\n')  # 在AI回覆後加入分隔線


@app.route('/download_history', methods=['GET'])
def download_history():
    global messages
    filename = 'chat_history.md'
    generate_md_file(messages, filename)  # 調用函數將對話歷史寫入Markdown文件
    return send_file(filename, as_attachment=True)  # 將文件作為附件發送給用戶


@app.route('/clear_history', methods=['POST'])
def clear_history():
    global messages
    messages = []  # 清空對話歷史
    return jsonify(success=True)  # 返回操作成功的JSON響應


if __name__ == '__main__':
    app.run()