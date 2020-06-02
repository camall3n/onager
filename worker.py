import json
import subprocess
import sys

def run_command_by_id(commands_file, run_id):
    with open(commands_file, 'r') as file:
        commands = json.load(file)
    # json stores all keys as strings, so we convert to ints
    commands = {int(id): cmd for id,cmd in commands.items()}
    cmd = commands[run_id]
    print('Launching worker:', cmd)
    subprocess.call(cmd, shell=True)

def run_single_command(command_file):
    with open(command_file, 'r') as file:
        cmd = file.read()
    print('Launching worker:', cmd)
    subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        run_command_by_id(sys.argv[1], int(sys.argv[2]))
    else:
        run_single_command(sys.argv[1])
