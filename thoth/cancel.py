import subprocess
import sys

from .backends import prepare_backend
from .list import get_job_listings

def launch_cancel_proc(cmd, args):
    """Print the cancel command and launch a subprocess to execute it"""
    if not args.quiet:
        print(cmd)
    if not args.dry_run:
        try:
            subprocess.call(cmd, shell=True)
        except (subprocess.CalledProcessError, ValueError) as err:
            print(err)
            sys.exit()

def cancel(args):
    """Parse the jobs/tasks to cancel and send the appropriate commands to the cluster"""

    if args.tasklist is None:
        yes_or_no = input('Are you sure you want to cancel all tasks for this job? (y/[n])\n> ')
        if yes_or_no in ['y','yes','Y',"YES"]:
            pass
        else:
            if yes_or_no not in ['n','no','N',"NO",'']:
                print('Unable to process response "{}"'.format(yes_or_no))
            print('Job cancellation aborted.')
            sys.exit()

    job_list = get_job_listings(args)
    unique_job_ids = sorted(list(set([listing.job_id for listing in job_list])))

    tasklists = {job_id: [] for job_id in unique_job_ids}
    for listing in job_list:
        tasklists[listing.job_id].append(listing.task_id)

    cancellations = [(job_id, tasklists[job_id]) for job_id in unique_job_ids]

    backend = prepare_backend(args)
    cmds = backend.get_cancel_cmds(cancellations)
    
    for cmd in cmds:
        launch_cancel_proc(cmd, args)
