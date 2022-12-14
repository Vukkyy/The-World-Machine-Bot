import openai
import os
import random

openai.api_key = os.getenv('OPENAI-KEY')

async def GenerateText(prompt : str, user : str):
    final_prompt = ''
    
    with open('response.txt') as f:
        final_prompt = eval(f.read())
    
    return Response(final_prompt)



async def GenerateBattle(gender1, name1, weapon1, personality1, gender2, name2, weapon2, personality2, winner):
    
    weapon_1 = ''
    
    if gender1 == 'Magical':
        weapon_1 = 'Prepares a spell from their weapon'
    if gender1 == 'Physical':
        weapon_1 = 'Holds their weapon'
    if gender1 == 'Tool':
        weapon_1 = 'Prepares their tool'
        
    weapon_2 = ''
    
    if gender2 == 'Magical':
        weapon_2 = 'Prepares a spell from their weapon'
    if gender2 == 'Physical':
        weapon_2 = 'Holds their weapon'
    if gender2 == 'Tool':
        weapon_2 = 'Prepares their tool'
    
    final_prompt = f"write me a long battle to the death. The first fighter is named {name1}, {name1} {weapon_1} called {weapon1}, {personality1} VS {name2}, {name2} {weapon_2} called {weapon2}, {personality2}. Let's think step by step. Everyone should be refered to with they/them pronouns, the winner of this battle should be {winner} due to their skills and the battle to the death begins in an arena.\n"
    
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