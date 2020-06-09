import argparse
import subprocess
import sys

from tabulate import tabulate

from .utils import load_jobindex, expand_ids, load_jobfile

def launch_cancel_proc(cmd, args):
    """Print the qdel command and launch a subprocess to execute it"""
    print(cmd)
    if not args.dry_run:
        try:
            subprocess.call(cmd, shell=True)
        except (subprocess.CalledProcessError, ValueError) as err:
            print(err)
            sys.exit()

def print_table(table, header):
    row_format ="{:>15}" * (len(header) + 1)
    print(row_format.format("", *header))
    for col, row in zip(header, table):
        print(row_format.format(col, *row))


def list_commands(args):
    """Parse the jobs/tasks to cancel and send the appropriate commands to the cluster"""
    job_id = args.jobid
    tasklist = args.tasklist
    def in_tasklist(task_id):
        return True if tasklist is None else task_id in expand_ids(tasklist)

    index = load_jobindex()
    jobname, jobfile = index[args.jobid]
    commands, tags = load_jobfile(jobfile)
    table = []
    for task_id in sorted(commands.keys()):
        if in_tasklist(task_id):
            table.append((job_id, task_id, jobname, repr(commands[task_id]), tags[task_id]))
    print(tabulate(table, headers=['job_id', 'task_id', 'jobname', 'command', 'tag']))
    sys.exit()


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
