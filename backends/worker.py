import json
import subprocess
import sys

def run_command_by_id(commands, task_id, stdout=None, stderr=None):
    cmd = commands[task_id]
    print('Launching worker:', cmd)
    if stdout is not None:
        stdout = open(stdout, 'wb')
    if stderr is not None:
        stderr = open(stderr, 'wb')
    try:
        subprocess.call(cmd, shell=True, stdout=stdout, stderr=stderr)
    finally:
        if stdout is not None:
            stdout.close()
        if stderr is not None:
            stderr.close()

if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Usage: python -m worker path/to/commands.json task_id'
    
    commands_file = sys.argv[1]
    task_id = int(sys.argv[2])

    with open(commands_file, 'r') as file:
        commands = json.load(file)
    # json stores all keys as strings, so we convert to ints
    commands = {int(id): cmd for id,cmd in commands.items()}

    run_command_by_id(commands, task_id)
