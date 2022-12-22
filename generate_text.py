import openai
import os
import random

openai.api_key = os.getenv('OPENAI-KEY')

async def GenerateText(prompt : str, user : str):
    final_prompt = ''
    
    with open('response.aidata') as f:
        final_prompt = f.read()
        
    final_prompt.replace('%1', user)
    final_prompt.replace('%2', prompt)
    
    return Response(final_prompt)



async def GenerateBattle(gender1, name1, weapon1, personality1, gender2, name2, weapon2, personality2, winner):
    
    weapon_1 = ''
    
    if gender1 == 'Magical':
        weapon_1 = 'A magical weapon.'
    if gender1 == 'Physical':
        weapon_1 = 'A weapon you can swing.'
    if gender1 == 'Tool':
        weapon_1 = 'A tool to use for many different things.'
        
    weapon_2 = ''
    
    if gender2 == 'Magical':
        weapon_2 = 'A magical weapon.'
    if gender1 == 'Physical':
        weapon_2 = 'A weapon you can swing.'
    if gender1 == 'Tool':
        weapon_2 = 'A tool to use for many different things.'
    
    with open('response_battle.aidata') as f:
        final_prompt = f.read()
        
    final_prompt.replace('%1', name1)
    final_prompt.replace('%2', weapon_1)
    final_prompt.replace('%3', weapon1)
    final_prompt.replace('%4', personality1)
    final_prompt.replace('%5', name2)
    final_prompt.replace('%6', weapon_2)
    final_prompt.replace('%7', weapon2)
    final_prompt.replace('%8', personality2)
    final_prompt.replace('%9', winner)
    
    return Response(final_prompt)

def Response(final_prompt : str):  
    # create a completion
    completion = openai.Completion.create(engine="text-davinci-003", prompt=final_prompt, max_tokens = 1024)

    full_text = []

    text = completion.choices[0].text

    if (len(text) > 4095):
        full_text.append(text[0:2048])
        full_text.append(text[2047 : len(text)])
    else:
        full_text.append(text)
    
    # print the completion
    return full_text