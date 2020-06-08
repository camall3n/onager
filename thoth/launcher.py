import json
import re
import os

from . import backends
from .constants import defaultjobfile
from .utils import load_jobfile


def prepare_backend(args):
    if args.backend == 'local':
        backend = backends.local.LocalBackend()
    elif args.backend == 'gridengine':
        backend = backends.gridengine.GridEngineBackend()
    elif args.backend == 'slurm':
        backend = backends.slurm.SlurmBackend()
    else:
        raise NotImplementedError('Invalid backend')

    return backend


def launch(args):
    if not re.match(r'^(\w|\.|-)+$', args.jobname):
        # We want to create a script file, so make sure the filename is legit
        raise ValueError("Invalid job name: {}".format(args.jobname))

    if args.jobfile == defaultjobfile:
        args.jobfile = args.jobfile.format(jobname=args.jobname)
    os.makedirs(os.path.dirname(args.jobfile), exist_ok=True)
    commands = load_jobfile(args.jobfile)

    backend = prepare_backend(args)

    # Update additional arguments
    if args.tasklist is None:
        args.tasklist = backend.generate_tasklist(commands)

    jobs = backend.get_job_list(args)
    backend.launch(jobs, args)
