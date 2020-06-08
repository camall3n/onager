import json

def load_jobfile(jobfile_path):
    with open(jobfile_path, 'r') as file:
        commands = json.load(file)
    # json stores all keys as strings, so we convert to ints
    return {int(id): cmd for id, cmd in commands.items()}

