import json

def load_config():
    '''
    Loads Config file.
    '''
   
    with open('config.json', 'r') as f:
        data = f.read()     
        return json.loads(data)
    
def get_data():
    '''
    Loads Data file.
    '''
    with open('data.json', 'r') as f:
        data = f.read()     
        return json.loads(data)