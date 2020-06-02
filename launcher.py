import argparse
from datetime import datetime, timedelta
import json
import os
import re
import subprocess
import sys

import backends

def parse_args(args=None):
    """Parse input arguments

    Use --help to see a pretty description of the arguments
    """
    defaultjobfile = '.thoth/scripts/{backend}/{jobname}/jobs.json'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--backend', choices=backends.__all__, default='local',
                        help='The backend to use for launching jobs')
    parser.add_argument('--jobname', type=str, required=True,
                        help='A name for the job')
    parser.add_argument('--jobfile', type=str, default=defaultjobfile,
                        help='Path to json file containing dictionary mapping run_ids to commands')
    parser.add_argument('--cpus', type=int, default=1,
                        help='Number of CPUs to request')
    parser.add_argument('--gpus', type=int, default=0,
                        help='Number of GPUs to request')
    parser.add_argument('--mem', type=int, default=2,
                        help='Amount of RAM (in GB) to request per node')
    parser.add_argument('--venv', type=str, default='./venv',
                        help='Path to python virtualenv')
    parser.add_argument('--duration', type=str, default='0-01:00:00',
                        help='Duration of job (d-hh:mm:ss)')
    parser.add_argument('--tasklist', type=str, default=None,
                        help='Comma separated list of task ID ranges to submit '
                             '(e.g. "18-22:1,26,29,34-49:3,51")')
    parser.add_argument('-max','--maxtasks', type=int, default=-1,
                        help='Maximum number of simultaneous tasks')
    parser.add_argument('-y','--dry_run', action='store_true',
                        help="Don't actually submit jobs to backend")
    parser.set_defaults(dry_run=False)
    parser.add_argument('--hold_jid', type=str, default=None,
                        help='Hold job until the specified jobid or jobid_taskid has finished')

    if args is not None:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    if args.backend == 'local':
        backend = backends.local.LocalBackend()
    elif args.backend == 'gridengine':
        backend = backends.gridengine.GridEngineBackend()
    elif args.backend == 'slurm':
        backend = backends.slurm.SlurmBackend()
    else:
        raise NotImplementedError('Invalid backend')

    if not re.match(r'^(\w|\.|-)+$', args.jobname):
        # We want to create a script file, so make sure the filename is legit
        print("Invalid job name: {}".format(args.jobname))
        sys.exit()

    if args.jobfile == defaultjobfile:
        args.jobfile = args.jobfile.format(backend=backend.name, jobname=args.jobname)

    return args, backend

def launch(commands):
    args, backend = parse_args()
    args.tasklist = backend.generate_tasklist(commands, args.tasklist)
    jobs = backend.get_job_list(args)
    for job in jobs:
        print(job)
        if not args.dry_run:
            try:
                byte_str = subprocess.check_output(cmd, shell=True)
                jobid = int(byte_str.decode('utf-8').split('.')[0])
            except (subprocess.CalledProcessError, ValueError) as err:
                print(err)
                sys.exit()

if __name__ == '__main__':
    with open('commands.json', 'r') as file:
        commands = json.load(file)
    # json stores all keys as strings, so we convert to ints
    commands = {int(id): cmd for id,cmd in commands.items()}
    launch(commands)
