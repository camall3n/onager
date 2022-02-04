import argparse
from argparse import Namespace
from contextlib import ExitStack
from datetime import datetime
import json
import os
import subprocess
import sys

from .utils import load_jobfile, compute_subjobs_filename
from .backends.local import LocalBackend
from .backends import __all__ as backend_names
from .subjobsfilemanager import SubjobsFileManager

def run_subjobs_with_local_backend(args):
    subjobsfile = compute_subjobs_filename(args.jobfile)
    sfm = SubjobsFileManager(subjobsfile)
    subjobs = sfm.get_subjobs_dict()
    args.tasklist = subjobs[args.subjob_group_id]

    backend = LocalBackend(logging_name=args.logging_backend)
    jobs = backend.get_job_list(args)
    backend.multilaunch(jobs, args)

def parse_args():
    parser = argparse.ArgumentParser(description='',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--jobfile', type=str, required=True,
        help='The jobfile from which to obtain subjobs')
    parser.add_argument('--logging-jobname', type=str, required=True,
        help='The jobname to use for logging')
    parser.add_argument('--logging-multijobid', type=str, required=True,
        help='')
    parser.add_argument('--logging-backend', choices=backend_names, required=True,
        help='The backend name to use for logging')
    parser.add_argument('--subjob-group-id', type=int, default=1,
        help='Which batch of subjobs to run')
    parser.add_argument('--max-subjobs', type=int, default=-1,
        help='Maximum number of simultaneous subjobs')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    run_subjobs_with_local_backend(args)
