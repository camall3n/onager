import os
from datetime import datetime

from ._backend import Backend

class SlurmBackend(Backend):
    def __init__(self):
        super().__init__()
        self.name = 'slurm'
        self.header = """#!/bin/bash

        module load python/3.7.4
        module load cuda/10.2
        module load cudnn/7.6.5
        source ./venv/bin/activate

        """
        self.body = """python -m worker {}
        """

        self.footer = """"""

        self.task_id_var = r'$SLURM_ARRAY_TASK_ID'

    def get_job_list(self, args):
        # Call the appropriate sbatch command. The default behavior is to use
        # Slurm's job array feature, which starts a batch job with multiple tasks
        # and passes a different taskid to each one. If ntasks is zero, only a
        # single job is submitted with no subtasks.
        base_cmd = 'sbatch '
        # Slurm runs scripts in current working directory by default

        # Duration
        base_cmd += '-t {} '.format(args.duration)
        duration = datetime.strptime(args.duration, "%d-%H:%M:%S")

        # Number of CPU/GPU resources
        base_cmd += '-n {} '.format(args.cpus)
        if args.gpus > 0:
            short_duration = datetime.strptime("01:00:00", "%H:%M:%S")
            partition = 'gpu-debug' if duration < short_duration else 'gpu'
            base_cmd += '-p {} --gres=gpu:{} '.format(partition, args.gpus)
        else:
            partition = 'debug' if args.duration in ['test','short'] else 'batch'
            base_cmd += '-p {} '.format(partition)

        # Memory requirements
        base_cmd += '--mem={}G '.format(args.mem)

        # Logging
        log_dir = ".thoth/logs/slurm/"
        os.makedirs(log_dir, exist_ok=True)
        base_cmd += '-o {}/{}.o '.format(log_dir, args.jobname) # save stdout to file
        base_cmd += '-e {}/{}.e '.format(log_dir, args.jobname) # save stderr to file

        # The --parsable flag causes sbatch to print the jobid to stdout. We read the
        # jobid with subprocess.check_output(), and use it to delay the email job
        # until the entire batch job has completed.
        base_cmd += '--parsable '

        if args.tasklist is not None:
            base_cmd += "--array={taskblock}"
            if args.maxtasks > 0:
                # set maximum number of running tasks per block
                base_cmd += '%{} '.format(args.maxtasks)
            else:
                base_cmd += ' '

        # Prevent Slurm from running this new job until the specified job ID is finished.
        if args.hold_jid is not None:
            base_cmd += "--depend=afterany:{} ".format(args.hold_jid)
        base_cmd += "{}".format(jobfile)

        if args.tasklist is None:
            return [base_cmd]
        else:
            # TODO: if there are multiple task groups, can they still respect args.maxtasks?
            taskblocks = args.tasklist.split(',')
            return [base_cmd.format(taskblock=taskblock) for taskblock in taskblocks]
