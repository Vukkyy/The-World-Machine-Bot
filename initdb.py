from replit import db
import json

#db['loveletters'] = ''

#db['sun'] = '50'

db['achievements'] = json.dumps({
   'user_id' : 0,
    'times_messaged' : 0,
    'suns_shattered' : 0,
    'times_asked' : 0,
    'letters_sent' : 0
}) + '\n'

db['achievementblacklist'] = '3458734059834'

with open('loveletter.txt', 'w') as f:
    f.write(db['achievements'])