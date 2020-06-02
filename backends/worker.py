import json
import subprocess
import sys

def run(commands_file, run_id):
    with open(commands_file, 'r') as file:
        commands = json.load(file)
    # json stores all keys as strings, so we convert to ints
    commands = {int(id): cmd for id,cmd in commands.items()}
    cmd = commands[run_id]
    print('Launching worker:', cmd)
    subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    run(sys.argv[1], int(sys.argv[2]))
