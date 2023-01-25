import os
import interactions

# Get a list of all files in the 'commands' directory that aren't in the '__pycache__' folder
files = [f for f in os.listdir('commands') if f != '__pycache__']

# Strip the '.py' extension from each file name
commands = [f.replace('.py', '') for f in files]

def load_commands(client):
    print("Loading Commands...")

    # Load each command using the client.load method
    [client.load(f"commands.{command}") for command in commands]

    print(f"Loaded {len(commands)} commands.")