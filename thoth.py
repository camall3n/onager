import argparse
from collections import OrderedDict
import json
import re
import sys

import backends
import meta_launcher
import launcher


def parse_args(args=None):

    parser = argparse.ArgumentParser(description='',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(required=True, dest='subcommand')


    prelaunch_parser = subparsers.add_parser('prelaunch',
        help='Generate commands based on lists of arguments',
        prefix_chars='+')
    prelaunch_parser.add_argument('+arg', type=str, action='append', nargs='+',
        metavar=('--argname', '[value, ...]'),
        help='Add an argument with zero or more mutually exclusive values')
    prelaunch_parser.add_argument('+command', type=str, required=True)
    prelaunch_parser.add_argument('+tag-name', type=str)
    prelaunch_parser.add_argument('+tag-args', type=str, nargs='*')
    prelaunch_parser.add_argument('+tag-id', type=str)


    launch_parser = subparsers.add_parser('launch', help='')
    launch_parser.add_argument('--backend', choices=backends.__all__,
        help='The backend to use for launching jobs', required=True)
    launch_parser.add_argument('--jobname', type=str, required=True,
        help='A name for the job')
    launch_parser.add_argument('--jobfile', type=str, default=launcher.defaultjobfile,
        help='Path to json file containing dictionary mapping run_ids to commands')
    launch_parser.add_argument('--cpus', type=int, default=1,
        help='Number of CPUs to request')
    launch_parser.add_argument('--gpus', type=int, default=0,
        help='Number of GPUs to request')
    launch_parser.add_argument('--mem', type=int, default=2,
        help='Amount of RAM (in GB) to request per node')
    launch_parser.add_argument('--venv', type=str, default='./venv',
        help='Path to python virtualenv')
    launch_parser.add_argument('--duration', type=str, default='0-01:00:00',
        help='Duration of job (d-hh:mm:ss)')
    launch_parser.add_argument('--tasklist', type=str, default=None,
        help='Comma separated list of task ID ranges to submit '
                '(e.g. "18-22:1,26,29,34-49:3,51")')
    launch_parser.add_argument('-max','--maxtasks', type=int, default=-1,
        help='Maximum number of simultaneous tasks')
    launch_parser.add_argument('-y','--dry_run', action='store_true',
        help="Don't actually submit jobs to backend")
    launch_parser.set_defaults(dry_run=False)
    launch_parser.add_argument('--hold_jid', type=str, default=None,
        help='Hold job until the specified jobid or jobid_taskid has finished')


    help_parser = subparsers.add_parser('help',
        help='Show usage information for a subcommand')

    args = parser.parse_args()
    return args

args = parse_args()
print(args)

if args.subcommand == 'prelaunch':
    meta_launcher.meta_launch(args)
elif args.subcommand == 'launch':
    launcher.launch(args)
elif args.subcommand == 'help':
    pass
else:
    raise ValueError("'{}' is not a valid command. See 'thoth --help'.")