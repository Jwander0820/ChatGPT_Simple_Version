import configparser

import openai

config = configparser.ConfigParser()
config.read("../config.ini")
api_key = config["api"]["key"]

openai.api_key = api_key


def generate_dalle_image(size="256x256"):
    prompt = input('input your prompt : ')
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=size
    )
    # if n > 1 then change value can see other img
    # response['data'][0]['url'], response['data'][1]['url']
    image_url = response['data'][0]['url']
    print(image_url)


if __name__ == '__main__':
    generate_dalle_image()
