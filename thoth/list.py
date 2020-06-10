from collections import namedtuple
import subprocess
import sys

from tabulate import tabulate

from .utils import load_jobindex, expand_ids, load_jobfile

JobListing = namedtuple('JobListing', ['job_id', 'task_id', 'jobname', 'command', 'tag'])

def get_job_listings(args):
    def in_joblist(job_id):
        return True if args.jobid is None else job_id == args.jobid
    def in_tasklist(task_id):
        return True if args.tasklist is None else task_id in expand_ids(args.tasklist)

    job_list = []
    try:
        index = load_jobindex()
    except (IOError):
        return job_list
    for jobid in index.keys():
        if not in_joblist(jobid):
            continue
        jobname, jobfile = index[jobid]
        commands, tags = load_jobfile(jobfile)
        for task_id in sorted(commands.keys()):
            if not in_tasklist(task_id):
                continue
            listing = JobListing(
                jobid,
                task_id,
                jobname,
                repr(commands[task_id]),
                tags[task_id]
            )
            job_list.append(listing)
    return job_list

def list_commands(args, quiet=False):
    """Parse the jobs/tasks to cancel and send the appropriate commands to the cluster"""
    job_list = get_job_listings(args)
    if not quiet:
        print(tabulate(job_list, headers=JobListing._fields))
    
