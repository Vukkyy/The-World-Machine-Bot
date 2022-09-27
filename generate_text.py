import openai
import os

openai.api_key = os.environ['OPENAI-KEY']

async def GenerateText(prompt : str):
    final_prompt = ''
    
    with open('response.txt') as f:
        final_prompt = f'{f.read()}{prompt}'
    
    # create a completion
    completion = openai.Completion.create(engine="text-davinci-002", prompt=final_prompt, max_tokens = 1024)

    print('generating')
    
    # print the completion
    return completion.choices[0].text