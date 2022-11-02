import openai
import os
import random

openai.api_key = os.getenv('OPENAI-KEY')

async def GenerateText(prompt : str, user : str):
    final_prompt = ''
    
    with open('response.txt') as f:
        final_prompt = f'{f.read()}{user}: {prompt}'
    
    return Response(final_prompt)

async def GenerateBattle(gender1, name1, weapon1, personality1, gender2, name2, weapon2, personality2, winner):
    return Response(f'write me a long, epic battle about how {winner} wins. The first figher is a {gender1} individual called {name1}, who wields a weapon called {weapon1}, their personality is: {personality1}.\nthey fight against another individual who is {gender2} called {name2}, who wields a weapon called {weapon2}, their personality is: {personality2}\nthe battle to the death begins in an arena.\n')

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