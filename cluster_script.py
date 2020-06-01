#!/usr/bin/env python3

"""
gridengine.run

This file simplifies the process of sending jobs to the cluster.
It parses input arguments that describe how the jobs should be
submitted, writes a bash script to a file, and finally calls qsub
with that bash script as an argument.

When qsub runs the script, the first thing it does is source a
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
    parser.add_argument('--jobtype', choices=['cpu', 'gpu'], default='cpu',
                        help='Which type of job to request')
    parser.add_argument('--mem', type=int, default=1,
                        help='Amount of RAM to request *per node* (in GB)')
    parser.add_argument('--env', type=str, default='./env',
                        help='Path to virtualenv')
    parser.add_argument('--nresources', type=int, default=1,
                        help='Number of CPUs / GPUs to request')
    parser.add_argument('--duration', choices=['test', 'short', 'long', 'vlong'], default='vlong',
                        help='Expected duration of job')
    parser.add_argument('--host', type=str, default=None,
                        help='Wildcard for targeting a specific host or set of hosts')
    parser.add_argument('-t','--taskid', type=int, default=1,
                        help='Task ID of first task')
    parser.add_argument('--tasklist', type=str, default=None,
                        help='Comma separated list of task IDs to submit'
                             ' (e.g. "18-22:1,26,29,34-49:1")')
    parser.add_argument('-n','--ntasks', type=int, default=0,
                        help='Number of tasks')
    parser.add_argument('-max','--maxtasks', type=int, default=-1,
                        help='Maximum number of simultaneous tasks')
    parser.add_argument('-y','--dry_run', action='store_true',
                        help="Don't actually submit jobs to grid engine")
    parser.set_defaults(dry_run=False)
    parser.add_argument('--email', type=str, default=None,
                        help='Email address(es) to notify when job is complete:'
                             ' addr1@brown.edu[, addr2@brown.edu]')
    parser.add_argument('--hold_jid', type=int, default=None,
                        help='Hold job until the specified job ID has finished')
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
    """Print the qsub command and launch a subprocess to execute it"""
    print(cmd)
    if not args.dry_run:
        try:
            byte_str = subprocess.check_output(cmd, shell=True)
            jobid = int(byte_str.decode('utf-8').split('.')[0])
            if args.email is not None:
                notify_cmd = 'qsub '
                notify_cmd += '-o /dev/null ' # don't save stdout file
                notify_cmd += '-e /dev/null ' # don't save stderr file
                notify_cmd += '-m b ' # send email when this new job starts
                notify_cmd += '-M "{}" '.format(args.email) # list of email addresses
                notify_cmd += '-hold_jid {} '.format(jobid)
                notify_cmd += '-N ~{} '.format(args.jobname[1:]) # modify the jobname slightly
                notify_cmd += '-b y sleep 0' # the actual job is a NO-OP
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
    
    # Define the bash script that qsub should run (with values
    # that need to be filled in using the input args).
    venv_path = os.path.join(args.env, 'bin', 'activate')
    script_body='''#!/bin/bash

source {}
{} '''.format(venv_path, args.command)

    # GridEngine doesn't like ranges of tasks that start with zero, so if you
    # submit a job with zero tasks, we ignore the taskid variable and submit a
    # single job with no task id instead of using GridEngine's range feature.
    if args.ntasks > 0 or args.tasklist is not None:
        script_body += r'$SGE_TASK_ID'
    script_body += '\n'

    # Write the script to a file
    os.makedirs("gridengine/scripts/", exist_ok=True)
    jobfile = "gridengine/scripts/{}".format(args.jobname)
    with open(jobfile, 'w') as file:
        file.write(script_body)

    # Call the appropriate qsub command. The default behavior is to use
    # GridEngine's range feature, which starts a batch job with multiple tasks
    # and passes a different taskid to each one. If ntasks is zero, only a
    # single job is submitted with no subtasks.
    cmd = 'qsub '
    cmd += '-cwd ' # run script in current working directory

    # When using the Brown grid:
    #  -l test   (10 min, high priority, limited to one slot per machine)
    #  -l short  (1 hour)
    #  -l long   (1 day)
    #  -l vlong  (infinite duration)
    #  -l gpus=# (infinite duration, on a GPU machine)
    if args.jobtype == 'gpu':
        cmd += '-l gpus={} '.format(args.nresources)# Request a single GPU
    else:
        cmd += '-l {} '.format(args.duration)
        if args.nresources > 1:
            cmd += '-pe smp {} '.format(args.nresources) # Request multiple CPUs

    if args.mem > 1:
        cmd += '-l vf={}G '.format(args.mem)# Reserve extra memory  

    if args.host is not None:
        cmd += '-q {}.q@{}.cs.brown.edu '.format(args.duration, args.host)

    os.makedirs("./gridengine/logs/", exist_ok=True)
    cmd += '-o ./gridengine/logs/ ' # save stdout file to this directory
    cmd += '-e ./gridengine/logs/ ' # save stderr file to this directory

    # The -terse flag causes qsub to print the jobid to stdout. We read the
    # jobid with subprocess.check_output(), and use it to delay the email job
    # until the entire batch job has completed.
    cmd += '-terse '

    if args.ntasks > 0:
        assert args.tasklist is None, 'Arguments ntasks and tasklist not supported simultaneously.'
        cmd += "-t {}-{} ".format(args.taskid, args.taskid+args.ntasks-1) # specify task ID range
        if args.maxtasks > 0:
            cmd += "-tc {} ".format(args.maxtasks) # set maximum number of running tasks
    elif args.tasklist is not None:
        cmd += "-t {taskblock} "

    # Prevent GridEngine from running this new job until the specified job ID is finished.
    if args.hold_jid is not None:
        cmd += "-hold_jid {} ".format(args.hold_jid)
    cmd += "{}".format(jobfile)

    if args.tasklist is None:
        launch(cmd, args)
    else:
        taskblocks = args.tasklist.split(',')
        for taskblock in taskblocks:
            launch(cmd.format(taskblock=taskblock), args)

if __name__ == '__main__':
    run()
