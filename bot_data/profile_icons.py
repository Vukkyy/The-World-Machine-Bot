import interactions
import json

icons = []

awesome = None

def Emojis():
    json_data = {}
    
    with open('bot_data/characters.json', 'r') as f:
        json_data = json.loads(f.read())
        
    characters = json_data['characters']
    
    awesome = []
    
    for character in characters:
        
        name = character['name']
        id_ = character['faces'][0]['id']
        
        awesome.append(
            interactions.SelectOption(
                label = name,
                emoji = interactions.Emoji(name = 'any', id = id_),
                value = name
            )
        )

    return interactions.SelectMenu(
        options=awesome,
        placeholder="Select a character!",
        custom_id="menu_component_char"
    )

async def GetEmoji(idx):
    print(awesome)
    awesome[idx]

async def GenerateModalTWM():
    
    

    return [
        interactions.SelectMenu(
            type = interactions.ComponentType.SELECT,
            options=awesome,
            placeholder="Select a face!",
            custom_id="menu_component",
        ),
        
        awesome
    ]