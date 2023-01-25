import json

def load_config(key : str):
    '''
    Loads Config file.
    '''
   
    with open('config.json', 'r') as f:
        data = f.read()     
        j = json.loads(data)
        
        return j[key]