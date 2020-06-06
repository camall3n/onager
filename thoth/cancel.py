#!/usr/bin/env python3

"""
gridengine.cancel

This file simplifies the process of canceling jobs on the cluster.
It parses input arguments that describe the job/tasks that should be
canceled, and calls qdel with the appropriate arguments.
"""

import argparse
import subprocess
import sys

def parse_args():
    """Parse input arguments

    Use --help to see a pretty description of the arguments
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-j','--jobid', type=str, default=None, required=True,
                        help='The job ID to delete')
    parser.add_argument('-t','--tasklist', type=str, default=None,
                        help='Comma separated list of task IDs to submit '
                             '(e.g. "18-22:1,26,29,34-49:1")')
    parser.add_argument('-y','--dry_run', action='store_true',
                        help="Don't actually submit jobs to grid engine")
    parser.set_defaults(dry_run=False)
    return parser.parse_args()


def launch_cancel_proc(cmd, args):
    """Print the qdel command and launch a subprocess to execute it"""
    print(cmd)
    if not args.dry_run:
        try:
            subprocess.call(cmd, shell=True)
        except (subprocess.CalledProcessError, ValueError) as err:
            print(err)
            sys.exit()


def cancel(args):
    """Parse the jobs/tasks to cancel and send the appropriate commands to the cluster"""

    cmd = "qdel {} ".format(args.jobid)
    if args.tasklist is not None:
        cmd += "-t {taskblock}"

    if args.tasklist is None:
        yes_or_no = input('Are you sure you want to cancel all tasks for this job? (y/[n])\n> ')
        if yes_or_no in ['y','yes','Y',"YES"]:
            launch_cancel_proc(cmd, args)
        else:
            if yes_or_no not in ['n','no','N',"NO",'']:
                print('Unable to process response "{}"'.format(yes_or_no))
            print('Job cancellation aborted.')
    else:
        taskblocks = args.tasklist.split(',')
        for taskblock in taskblocks:
            launch_cancel_proc(cmd.format(taskblock=taskblock), args)


if __name__ == '__main__':
    args = parse_args()
    cancel(args)
