import re
import os

from .backends import prepare_backend
from .utils import load_jobfile, save_jobfile, get_jobfile_path

def launch(args, other_args):
    if not re.match(r'^(\w|\.|-)+$', args.jobname):
        # We want to create a script file, so make sure the filename is legit
        raise ValueError("Invalid job name: {}".format(args.jobname))

    jobfile = get_jobfile_path(args.jobname)
    os.makedirs(os.path.dirname(jobfile), exist_ok=True)
    if args.command is not None:
        save_jobfile({1: (args.command, '')}, jobfile)
    commands = load_jobfile(jobfile)[0]

    backend = prepare_backend(args)

    # Update additional arguments
    if args.tasklist is None:
        args.tasklist = backend.generate_tasklist(commands)

    jobs = backend.get_job_list(args)

    if len(other_args) != 0:
        print("Passing these args to backend: {}".format(' '.join(other_args)))

    backend.launch(jobs, args, other_args)
