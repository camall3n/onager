from contextlib import ExitStack
import json
import subprocess
import sys

from ..utils import load_jobfile

def run_command_by_id(commands, task_id, stdout=None, stderr=None, verbose=False):
    cmd = commands[task_id]
    if verbose:
        print('Launching worker:', cmd)
    with ExitStack() as stack:
        stdout = stack.enter_context(open(stdout, 'wb')) if stdout is not None else None
        stderr = stack.enter_context(open(stderr, 'wb')) if stderr is not None else None
        try:
            subprocess.call(cmd, shell=True, stdout=stdout, stderr=stderr)
        except:
            raise
        else:
            if verbose:
                print('Worker finished:', cmd)

if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Usage: python -m worker path/to/commands.json task_id'
    
    commands_file = sys.argv[1]
    task_id = int(sys.argv[2])

    with open(commands_file, 'r') as file:
        commands = json.load(file)
    # json stores all keys as strings, so we convert to ints
    commands = {int(id): cmd for id,cmd in commands.items()}

    run_command_by_id(commands, task_id)
