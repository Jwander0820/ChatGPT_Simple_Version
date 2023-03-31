import os
from flask import Flask, render_template, request, jsonify, send_file
from core.model import OpenAIModel

app = Flask(__name__)
openai_model = OpenAIModel()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    input_text = request.form['input_text']
    chat_type = request.form['chat_type']
    initial_system = request.form.get('initial_system')
    response_text, history = openai_model.chat_gpt_response(input_text, chat_type, initial_system)
    if chat_type == "single":
        return jsonify(response=response_text, history=history)
    else:
        return jsonify(response=response_text, history=history)


@app.route('/download_history', methods=['GET'])
def download_history():
    messages, title = openai_model.get_message_history()
    file_path = openai_model.generate_md_file(messages, title)  # 調用函數將對話歷史寫入Markdown文件
    return send_file(file_path)  # 將文件作為附件發送給用戶


@app.route('/clear_history', methods=['POST'])
def clear_history():
    openai_model.clear_message_history()
    return jsonify(success=True)  # 返回操作成功的JSON響應


@app.route('/generate_image', methods=['POST'])
def generate_image_route():
    prompt_text = request.form.get('input_text')
    image_url, success = openai_model.generate_dalle_image(prompt_text)
    return jsonify({"image_url": image_url, "success": success})


if __name__ == '__main__':
    app.run(debug=True)
