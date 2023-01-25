import json

async def GetDatabase(guild_id : int, database : str, default_data : dict):
    
    db = []
    guild_ids = []
    
    with open(f'databases/{database}.db', 'r') as f:
        data_ = f.read()
        db = data_.split('\n')
        
    for slot in db:
        json_data = json.loads(slot)
        guild_ids.append(json_data['uid'])
    
    if not guild_id in guild_ids:
        str_data = json.dumps(default_data)
        db.append(str_data)
        
        with open(f'databases/{database}.db', 'w') as f:
            full_data = '\n'.join(db)
            f.write(full_data)

        return default_data
    
    index = 0
    for id_ in guild_ids:
        if (guild_id == id_):
            json_data = json.loads(db[index])
            return json_data
        index += 1
        
async def SetDatabase(guild_id : int, database : str, value : str, data,):
    db = []
    guild_ids = []
    
    with open(f'databases/{database}.db', 'r') as f:
        data_ = f.read()
        db = data_.split('\n')
        
    for slot in db:
        json_data = json.loads(slot)
        guild_ids.append(json_data['uid'])
    
    index = 0
    
    json_data = {}
    
    for id_ in guild_ids:
        if (guild_id == id_):
            json_data = json.loads(db[index])
            json_data[value] = data
            db[index] = json.dumps(json_data)
        index += 1
        
    with open(f'databases/{database}.db', 'w') as f:
        full_data = '\n'.join(db)
        f.write(full_data)
        
    return json_data
