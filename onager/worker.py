from contextlib import ExitStack
from datetime import datetime
import subprocess
import sys

from .utils import load_jobfile

def run_command_by_id(commands, task_id, stdout=None, stderr=None, quiet=False):
    cmd = commands[task_id]
    if not quiet:
        print('Launching worker: {}'.format(cmd), flush=True)
        start_time = datetime.now()
    with ExitStack() as stack:
        stdout = stack.enter_context(open(stdout, 'wb')) if stdout is not None else None
        stderr = stack.enter_context(open(stderr, 'wb')) if stderr is not None else None
        try:
            subprocess.call(cmd, shell=True, stdout=stdout, stderr=stderr)
        except:
            raise
        else:
            if not quiet:
                elapsed = datetime.now() - start_time
                print('Worker finished: {}\nElapsed time:  {}'.format(cmd, elapsed), flush=True)

if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Usage: python -m worker path/to/commands.json task_id'

    commands_file = sys.argv[1]
    task_id = int(sys.argv[2])

    commands = load_jobfile(commands_file)[0]

    run_command_by_id(commands, task_id)
