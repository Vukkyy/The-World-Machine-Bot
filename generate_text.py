import openai
import os

openai.api_key = os.environ['OPENAI-KEY']

async def GenerateText(prompt : str):
    final_prompt = ''
    
    with open('response.txt') as f:
        final_prompt = f'{f.read()}{prompt}'
    
    return Response(final_prompt)

async def GenerateBattle(name1, weapon1, name2, weapon2):
    return Response(f'Generate a long story of a battle between {name1} who wields a {weapon1}, fighting against {name2}, who wields a {weapon2}')

def Response(final_prompt : str):
    # create a completion
    completion = openai.Completion.create(engine="text-davinci-002", prompt=final_prompt, max_tokens = 1024)

    full_text = []

    text = completion.choices[0].text

    if (len(text) > 4095):
        full_text.append(text[0:2048])
        full_text.append(text[2047 : len(text)])
    else:
        full_text.append(text)
    
    # print the completion
    return full_text