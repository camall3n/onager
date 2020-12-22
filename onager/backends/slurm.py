from datetime import timedelta
import os
import math

from ._backend import Backend
from ..utils import expand_ids

class SlurmBackend(Backend):
    def __init__(self):
        super().__init__()
        self.name = 'slurm'
        self.task_id_var = r'$SLURM_ARRAY_TASK_ID'


    def _get_body(self, tasks_file, args):
        """
        A bit complicated. It may have a bunch of concurrent processes.
        """
        tasklist_elems = args.tasklist.split(',')
        tasklist_elems.extend(["__filler__"]*args.tasks_per_job) # Makes sure that it doesn't go over on last job.
        bash_task_array_defn = "task_array=({})\n".format(' '.join(tasklist_elems))
        task_id_var = self.task_id_var

        all_tasks = []
        pids = []
        for i in range(1, args.tasks_per_job + 1):
            task_num_str_defn = "task_array_num=$(( {}*{} - {} + {} - 1))".format(str(args.tasks_per_job), task_id_var, str(args.tasks_per_job), i)
            # task_num_str_defn = "\ntask_array_num=$(( {}*{} + {} - {} - 1))".format(str(args.tasks_per_job), task_id_var, i, str(args.tasks_per_job))
            real_task_id_str = "task_num=${task_array[$task_array_num]}"
            task = self.body.strip().format(tasks_file, "$task_num")
            # task = self.body.strip().format(tasks_file, real_task_id_str)
            get_pid_str = "pid{}=$!\n".format(str(i))
            single_task_str = " \n".join([task_num_str_defn, real_task_id_str, task])
            single_task_str = single_task_str + " & \n" + get_pid_str
            # single_task_str = "( " + single_task_str + " ) & \n" + get_pid_str
            pids.append("$pid{}".format(str(i)))
            # single_task_str = " \n".join([task_num_str_defn, real_task_id_str, task])
            all_tasks.append(single_task_str)

        wait_str = "wait " + " ".join(pids)
        full_task_str = " \n".join(all_tasks)
        full_task_str = "\n{} \n{} \n{} \n".format(bash_task_array_defn, full_task_str, wait_str)
        return full_task_str

    def get_cancel_cmds(self, cancellations):
        cmds = []
        for cancellation in cancellations:
            jobid, tasklist = cancellation
            cmd = "scancel"
            if tasklist is None:
                cmd += " {}".format(jobid)
            else:
                for task_id in tasklist:
                    cmd += " {}_{}".format(jobid, task_id)
            cmds.append(cmd)
        return cmds

    def get_job_list(self, args):
        # Call the appropriate sbatch command. The default behavior is to use
        # Slurm's job array feature, which starts a batch job with multiple tasks
        # and passes a different taskid to each one. If ntasks is zero, only a
        # single job is submitted with no subtasks.
        base_cmd = 'sbatch '
        base_cmd += '-J {} '.format(args.jobname)  # set name of job
        # Slurm runs scripts in current working directory by default

        # Duration
        base_cmd += '-t {} '.format(args.duration)
        duration = self.get_time_delta(args.duration)

        # Number of CPU/GPU resources
        base_cmd += '-n {} '.format(args.cpus)
        if args.debug and duration > timedelta(hours=2):
            raise RuntimeError('{}: Duration cannot exceed 2 hours while in debug/test mode.'.format(self.name))
        if args.gpus > 0:
            partition = 'gpu-debug' if args.debug else 'gpu'
            base_cmd += '-p {} --gres=gpu:{} '.format(partition, args.gpus)
        else:
            partition = 'debug' if args.debug else 'batch'
            base_cmd += '-p {} '.format(partition)

        # Memory requirements
        base_cmd += '--mem={}G '.format(args.mem)

        # Logging
        log_dir = self.get_log_dir()
        # Format is jobname_jobid_taskid.*
        base_cmd += '-o {} '.format(os.path.join(log_dir, '%x_%A_%a.o'))  # save stdout to file
        base_cmd += '-e {} '.format(os.path.join(log_dir, '%x_%A_%a.e'))  # save stderr to file

        # The --parsable flag causes sbatch to print the jobid to stdout. We read the
        # jobid with subprocess.check_output()
        base_cmd += '--parsable '

        num_jobs = len(args.tasklist.split(",")) / args.tasks_per_job
        num_jobs = math.ceil(num_jobs)
        array = ",".join(map(str, range(1, num_jobs+1)))

        # base_cmd += "--array={}".format(args.tasklist)
        base_cmd += "--array={}".format(array)
        if args.maxtasks > 0:
            # set maximum number of running tasks
            base_cmd += '%{} '.format(args.maxtasks)
        else:
            base_cmd += ' '

        # Prevent Slurm from running this new job until the specified job ID is finished.
        if args.hold_jid is not None:
            base_cmd += "--depend=afterany:{} ".format(args.hold_jid)

        wrapper_script = self.wrap_tasks(args.jobfile, args)
        wrapper_file = self.save_wrapper_script(wrapper_script, args.jobname)
        base_cmd += "{}".format(wrapper_file)
        return [base_cmd]

    def launch(self, jobs, args, other_args):
        task_ids = expand_ids(args.tasklist)
        task_id_strs = ','.join(map(str, task_ids))
        args.tasklist = task_id_strs # Hope that's okay.
        # print('whats this look like')
        # __import__('pdb').set_trace()
        super().launch(jobs, args, other_args)

