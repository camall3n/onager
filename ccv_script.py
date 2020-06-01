#!/usr/bin/env python3

"""
slurm.run

This file simplifies the process of sending jobs to the cluster.
It parses input arguments that describe how the jobs should be
submitted, writes a bash script to a file, and finally calls sbatch
with that bash script as an argument.

When slurm runs the script, the first thing it does is source a
virtualenv script that configures the python environment properly.
"""

import argparse
import os
import re
import subprocess
import sys


def parse_args(custom_args=None):
    """Parse input arguments

    Use --help to see a pretty description of the arguments
    """
    defaultjob = 'run'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--command', type=str, required=True,
                        help='The command to run (e.g. "python -m module.name --arg=value")')
    parser.add_argument('--jobname', type=str, default=defaultjob,
                        help='A name for the job (max 10 chars)')
    parser.add_argument('--cpus', type=int, default=1,
                        help='Number of CPUs to request')
    parser.add_argument('--gpus', type=int, default=0,
                        help='Number of GPUs to request')
    parser.add_argument('--mem', type=int, default=2,
                        help='Amount of RAM to request *per node* (in GB)')
    parser.add_argument('--env', type=str, default='./env',
                        help='Path to virtualenv')
    parser.add_argument('--duration', choices=['test', 'short', 'medium', 'long', 'slong', 'vlong'], default='long',
                        help='Expected duration of job')
    parser.add_argument('-t','--taskid', type=int, default=1,
                        help='Task ID of first task')
    parser.add_argument('--tasklist', type=str, default=None,
                        help='Comma separated list of task IDs to submit '
                             '(e.g. "18-22:1,26,29,34-49:1")')
    parser.add_argument('-n','--ntasks', type=int, default=0,
                        help='Number of tasks')
    parser.add_argument('-max','--maxtasks', type=int, default=-1,
                        help='Maximum number of simultaneous tasks')
    parser.add_argument('-y','--dry_run', action='store_true',
                        help="Don't actually submit jobs to slurm")
    parser.set_defaults(dry_run=False)
    parser.add_argument('--email', type=str, default=None,
                        help='Email address(es) to notify when job is complete:'
                             ' addr1@brown.edu[, addr2@brown.edu]')
    parser.add_argument('--hold_jid', type=str, default=None,
                        help='Hold job until the specified jobid or jobid_taskid has finished')
    if custom_args:
        args = parser.parse_args(custom_args)
    else:
        args = parser.parse_args()

    if args.jobname == defaultjob:
        args.jobname = "run{}".format(args.taskid)
    elif not re.match(r'^(\w|\.|-)+$', args.jobname):
        # We want to create a script file, so make sure the filename is legit
        print("Invalid job name: {}".format(args.jobname))
        sys.exit()

    return args



def launch(cmd, args):
    """Print the sbatch command and launch a subprocess to execute it"""
    print(cmd)
    if not args.dry_run:
        try:
            byte_str = subprocess.check_output(cmd, shell=True)
            jobid = int(byte_str.decode('utf-8').split('.')[0])
            if args.email is not None:
                notify_cmd = 'sbatch '
                notify_cmd += '-o /dev/null ' # don't save stdout file
                notify_cmd += '-e /dev/null ' # don't save stderr file
                notify_cmd += '--mail-type=BEGIN' # send email when this new job starts
                notify_cmd += '--mail-user="{}" '.format(args.email) # email address
                notify_cmd += '--depend=afterany:{} '.format(jobid)
                notify_cmd += '-J ~{} '.format(args.jobname[1:]) # modify the jobname slightly
                notify_cmd += '--wrap="sleep 0"' # the actual job is a NO-OP
                subprocess.call(notify_cmd, shell=True)
        except (subprocess.CalledProcessError, ValueError) as err:
            print(err)
            sys.exit()


def run(custom_args=None):
    """Build the bash script and send it to the cluster"""
    if custom_args:
        args = parse_args(custom_args)
    else:
        args = parse_args()

    # Define the bash script that sbatch should run (with values
    # that need to be filled in using the input args).
    venv_path = os.path.join(args.env, 'bin', 'activate')
    script_body='''#!/bin/bash

module load python/3.7.4
module load cuda/10.2
module load cudnn/7.6.5
source {}
{} '''.format(venv_path, args.command)

    if args.ntasks > 0 or args.tasklist is not None:
        script_body += r'$SLURM_ARRAY_TASK_ID'
    script_body += '\n'

    # Write the script to a file
    os.makedirs("slurm/scripts/", exist_ok=True)
    jobfile = "slurm/scripts/{}".format(args.jobname)
    with open(jobfile, 'w') as file:
        file.write(script_body)

    # Call the appropriate sbatch command. The default behavior is to use
    # Slurm's job array feature, which starts a batch job with multiple tasks
    # and passes a different taskid to each one. If ntasks is zero, only a
    # single job is submitted with no subtasks.
    cmd = 'sbatch '
    # Slurm runs scripts in current working directory by default

    # Duration
    duration_map = {
        'test': '0:10:00',  # 10 minutes
        'short': '1:00:00',  # 1 hour
        'medium': '15:00:00', # 15 hours
        'long': '1-00:00:00',  # 1 day
        'slong': '2-00:00:00',  # 2 days
        'vlong': '7-00:00:00',  # 1 week
    }
    cmd += '-t {} '.format(duration_map[args.duration])

    # Number of CPU/GPU resources
    cmd += '-n {} '.format(args.cpus)
    if args.gpus > 0:
        partition = 'gpu-debug' if args.duration in ['test','short'] else 'gpu'
        cmd += '-p {} --gres=gpu:{} '.format(partition, args.gpus)
    else:
        partition = 'debug' if args.duration in ['test','short'] else 'batch'
        cmd += '-p {} '.format(partition)

    # Memory requirements
    cmd += '--mem={}G '.format(args.mem)

    # Logging
    os.makedirs("./slurm/logs/", exist_ok=True)
    cmd += '-o ./slurm/logs/{}.o '.format(args.jobname) # save stdout to file
    cmd += '-e ./slurm/logs/{}.e '.format(args.jobname) # save stderr to file

    # The --parsable flag causes sbatch to print the jobid to stdout. We read the
    # jobid with subprocess.check_output(), and use it to delay the email job
    # until the entire batch job has completed.
    cmd += '--parsable '

    if args.ntasks > 0:
        assert args.tasklist is None, 'Arguments ntasks and tasklist not supported simultaneously.'
        cmd += "--array={}-{}".format(args.taskid, args.taskid+args.ntasks-1) # specify task range
        if args.maxtasks > 0:
            cmd += '%{} '.format(args.maxtasks) # set maximum number of running tasks
        else:
            cmd += ' '
    elif args.tasklist is not None:
        cmd += "--array={taskblock} "

    # Prevent Slurm from running this new job until the specified job ID is finished.
    if args.hold_jid is not None:
        cmd += "--depend=afterany:{} ".format(args.hold_jid)
    cmd += "{}".format(jobfile)

    if args.tasklist is None:
        launch(cmd, args)
    else:
        taskblocks = args.tasklist.split(',')
        for taskblock in taskblocks:
            launch(cmd.format(taskblock=taskblock), args)

if __name__ == '__main__':
    run()
