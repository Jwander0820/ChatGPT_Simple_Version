import configparser

import openai

config = configparser.ConfigParser()
config.read("../config.ini")
api_key = config["api"]["key"]

openai.api_key = api_key


def single_shot():
    prompt = input('me > ')
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    text = response["choices"][0]["text"]
    print(text)


if __name__ == '__main__':
    single_shot()
