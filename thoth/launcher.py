import json
import re

from . import backends

defaultjobfile = '.thoth/scripts/{backend}/{jobname}/jobs.json'

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

    backend = prepare_backend(args)

    args.jobfile = 'commands.json' # hardcoded jobfile -- FIXME
    with open(args.jobfile, 'r') as file:
        commands = json.load(file)
    # json stores all keys as strings, so we convert to ints
    commands = {int(id_): cmd for id_,cmd in commands.items()}

    # Update additional arguments
    if args.tasklist is None:
        args.tasklist = backend.generate_tasklist(commands)
    if args.jobfile == defaultjobfile:
        args.jobfile = args.jobfile.format(backend=backend.name, jobname=args.jobname)

    jobs = backend.get_job_list(args)
    backend.launch(jobs, args)
