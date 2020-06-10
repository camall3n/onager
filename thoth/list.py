import argparse
from collections import namedtuple
import subprocess
import sys

from tabulate import tabulate

from .utils import load_jobindex, expand_ids, load_jobfile

JobListing = namedtuple('JobListing', ['job_id', 'task_id', 'jobname', 'command', 'tag'])

def launch_cancel_proc(cmd, args):
    """Print the qdel command and launch a subprocess to execute it"""
    print(cmd)
    if not args.dry_run:
        try:
            subprocess.call(cmd, shell=True)
        except (subprocess.CalledProcessError, ValueError) as err:
            print(err)
            sys.exit()

def get_job_list(args):

    def in_joblist(job_id):
        return True if args.job_id is None else job_id == args.job_id
    def in_tasklist(task_id):
        return True if args.tasklist is None else task_id in expand_ids(args.tasklist)

    job_list = []
    try:
        index = load_jobindex()
        jobname, jobfile = index[args.jobid]
        commands, tags = load_jobfile(jobfile)
    except (KeyError, IOError):
        return job_list

    for task_id in sorted(commands.keys()):
        if in_joblist(job_id) and in_tasklist(task_id):
            listing = JobListing(
                args.job_id,
                task_id,
                args.jobname,
                repr(commands[task_id]),
                tags[task_id]
            )
            job_list.append(listing)
    return job_list

def list_commands(args, quiet=False):
    """Parse the jobs/tasks to cancel and send the appropriate commands to the cluster"""
    job_list = get_job_list(args)
    if not quiet:
        print(tabulate(job_list, headers=JobListing._fields))
    