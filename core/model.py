import configparser
import os
import urllib.request

import openai

from core.logger import create_logger

config = configparser.ConfigParser()
config.read("config.ini")
api_key = config["api"]["key"]

openai.api_key = api_key


class OpenAIModel:
    def __init__(self):
        self.logger = create_logger()
        self.messages = []  # 初始化對話歷史
        self.title = ""  # 初始化標題

    def update_messages(self, initial_system, oneshot_message=None):
        if initial_system and not any(msg['role'] == 'system' for msg in self.messages):
            self.messages.append({"role": "system", "content": initial_system})

        if oneshot_message and initial_system and not any(msg['role'] == 'system' for msg in oneshot_message):
            oneshot_message.append({"role": "system", "content": initial_system})

    def send_request_to_api(self, model_engine, messages):
        """向openai發送request取得response"""
        response = openai.ChatCompletion.create(
            model=model_engine,
            max_tokens=2048,
            temperature=0.5,
            messages=messages
        )
        return response

    def chat_gpt_response(self, prompt, chat_type, initial_system=None):
        """根據指定狀態，取得ChatGPT的回應"""
        oneshot_message = []

        self.update_messages(initial_system, oneshot_message)

        model_engine = "gpt-3.5-turbo"

        if chat_type == "single":
            oneshot_message.append({"role": "user", "content": prompt})
            response = self.send_request_to_api(model_engine, oneshot_message)
        elif chat_type == "continuous":
            if not self.title:  # 如果尚未有任何對話，將第一次提交的文字以指定prompt提取出存檔命名標題
                analysis_prompt = f"請根據以下文字，生成適合的文字標題，盡量減少單字在10個單詞以內用於chatgpt的標題命名: {prompt}"
                oneshot_message.append({"role": "user", "content": analysis_prompt})
                response = self.send_request_to_api(model_engine, oneshot_message)
                self.title = response.choices[0].message.content.replace('\n', '')
                self.title = self.sanitize_filename(self.title)
                self.title = f"{self.title}.md"

            self.messages.append({"role": "user", "content": prompt})
            response = self.send_request_to_api(model_engine, self.messages)
        else:
            return False

        ai_msg = response.choices[0].message.content.replace('\n', '')

        if chat_type == "single":
            oneshot_message.append({"role": "assistant", "content": ai_msg})
            self.logger.info(oneshot_message)
            return ai_msg, oneshot_message
        else:
            self.messages.append({"role": "assistant", "content": ai_msg})
            self.logger.info([{"role": "user", "content": prompt}, {"role": "assistant", "content": ai_msg}])
            print(self.messages)
            return ai_msg, self.messages

    def generate_dalle_image(self, prompt_text, n=1, size="512x512"):
        """提交提示詞給DALL-E，並取得生成圖片的網址"""
        try:
            response = openai.Image.create(
                prompt=prompt_text,
                n=n,
                size=size
            )
            image_url = response['data'][0]['url']
            print(image_url)
            try:
                OpenAIModel.download_image(image_url, f"./img/{prompt_text}.png")  # 下載圖片
                self.logger.info([prompt_text, f"./img/{prompt_text}.png"])
            except:
                # 當prompt因為命名問題無法儲存時，改以created_id作為檔案名稱
                created_id = response["created"]
                OpenAIModel.download_image(image_url, f"./img/{created_id}.png")  # 下載圖片
                self.logger.info([prompt_text, f"./img/{created_id}.png"])
            return image_url, True
        except Exception as e:
            self.logger.info(e)
            error_text = "Your request was rejected as a result of our safety system. " \
                         "Your prompt may contain text that is not allowed by our safety system."
            return error_text, False

    @staticmethod
    def download_image(image_url, local_path):
        """解析並下載圖片"""
        if not os.path.exists("./img"):
            os.makedirs("./img")
        # 檢查文件是否存在，如果存在則為其添加 _流水號
        file_exists = os.path.isfile(local_path)
        count = 1
        new_local_path = local_path

        while file_exists:
            file_name, file_ext = os.path.splitext(local_path)
            new_local_path = f"{file_name}_{count}{file_ext}"
            file_exists = os.path.isfile(new_local_path)
            count += 1

        # 下載並保存圖片
        with urllib.request.urlopen(image_url) as response, open(new_local_path, 'wb') as out_file:
            out_file.write(response.read())

    @staticmethod
    def generate_md_file(messages, filename):
        """此函數將對話歷史生成為Markdown文件"""
        chat_history_folder = "./chat_history"
        if not os.path.exists(chat_history_folder):
            os.makedirs(chat_history_folder)
        file_path = os.path.join(chat_history_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            for message in messages:
                f.write(f"{message['role']}: {message['content']}\n")
                if message['role'] == "assistant":
                    f.write('---\n')  # 在AI回覆後加入分隔線
        return file_path

    def get_message_history(self):
        """取得聊天紀錄的標題，用於命名檔名"""
        if not self.title:
            return self.messages, "chat_history.md"
        return self.messages, self.title

    def clear_message_history(self):
        """清空歷史紀錄"""
        self.messages = []
        self.title = ""

    def sanitize_filename(self, title):
        """替換掉windows無法命名的文字"""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            title = title.replace(char, '-')
        return title
