import configparser
import os
import urllib.request

import openai

config = configparser.ConfigParser()
config.read("config.ini")
api_key = config["api"]["key"]

openai.api_key = api_key


class OpenAIModel:
    def __init__(self):
        # 初始化對話歷史
        self.messages = []

    def chat_gpt_response(self, prompt, chat_type, initial_system=None):
        # 此函數負責向GPT-3 API發送請求並返回AI的回應
        oneshot_message = []  # 將 oneshot_message 改為局部變量
        if initial_system and not any(msg['role'] == 'system' for msg in self.messages):
            self.messages.append({"role": "system", "content": initial_system})

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
            return ai_msg, oneshot_message

        # 如果對話類型為"continuous"，即連續對話
        elif chat_type == "continuous":
            # 將用戶的提問添加到對話歷史中
            self.messages.append({"role": "user", "content": prompt})

            response = openai.ChatCompletion.create(
                model=model_engine,
                max_tokens=2048,
                temperature=0.5,
                messages=self.messages
            )

            ai_msg = response.choices[0].message.content.replace('\n', '')
            # 將AI回應添加到對話歷史中
            self.messages.append({"role": "assistant", "content": ai_msg})
            print(self.messages)
            return ai_msg, self.messages

    @staticmethod
    def generate_dalle_image(prompt_text, n=1, size="512x512"):
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
            except:
                # 當prompt因為命名問題無法儲存時，改以created_id作為檔案名稱
                created_id = response["created"]
                OpenAIModel.download_image(image_url, f"./img/{created_id}.png")  # 下載圖片
            return image_url, True
        except Exception as e:
            print(e)
            error_text = "Your request was rejected as a result of our safety system. " \
                         "Your prompt may contain text that is not allowed by our safety system."
            return error_text, False

    @staticmethod
    def download_image(image_url, local_path):
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
        # 此函數將對話歷史生成為Markdown文件
        with open(filename, 'w', encoding='utf-8') as f:
            for message in messages:
                f.write(f"{message['role']}: {message['content']}\n")
                if message['role'] == "assistant":
                    f.write('---\n')  # 在AI回覆後加入分隔線

    def get_message_history(self):
        return self.messages

    def clear_message_history(self):
        self.messages = []
