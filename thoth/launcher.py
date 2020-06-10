import re
import os

from .backends import prepare_backend
from .constants import defaultjobfile
from .utils import load_jobfile, save_jobfile

def launch(args, other_args):
    if not re.match(r'^(\w|\.|-)+$', args.jobname):
        # We want to create a script file, so make sure the filename is legit
        raise ValueError("Invalid job name: {}".format(args.jobname))

    if args.jobfile == defaultjobfile:
        args.jobfile = args.jobfile.format(jobname=args.jobname)
    os.makedirs(os.path.dirname(args.jobfile), exist_ok=True)
    if args.command is not None:
        save_jobfile({1: (args.command, '')}, args.jobfile)
    commands = load_jobfile(args.jobfile)[0]

    backend = prepare_backend(args)

    # Update additional arguments
    if args.tasklist is None:
        args.tasklist = backend.generate_tasklist(commands)

    jobs = backend.get_job_list(args)

    if len(other_args) != 0 and not args.quiet:
        print("Passing these args to backend: {}".format(' '.join(other_args)))

    backend.launch(jobs, args, other_args)
