from datetime import datetime, timedelta
import os
import subprocess
import sys

from ..config import get_active_config
from ..constants import default_logs_folder
from ..utils import update_jobindex, insert_second_to_last
from ..history import add_new_history_entry

class Backend:
    def __init__(self):
        self.name = 'generic_backend'
        self.header = '#!/bin/bash'
        self.body = '\npython -m onager.worker {} {} \n'
        self.multiworker_body = '\npython -m onager.multiworker {} \n'
        self.footer = ''

        self.task_id_var = r'$TASK_ID'
        self.job_id_var = r'$JOB_ID'

    def get_body(self, tasks_file, args):
        if args.tasks_per_node == 1:
            return self.body.format(tasks_file, self.task_id_var)
        else:
            body = self.multiworker_body
            args_str_list = []
            args_str_list.append('--jobfile {}'.format(args.jobfile))
            args_str_list.append('--logging-jobname {}'.format(args.jobname))
            args_str_list.append('--logging-multijobid {}'.format(self.job_id_var))
            args_str_list.append('--logging-backend {}'.format(args.backend))
            args_str_list.append('--subjob-group-id {}'.format(self.task_id_var))
            args_str_list.append('--max-subjobs {}'.format(args.max_tasks_per_node))
            return body.format(' '.join(args_str_list))

    def wrap_tasks(self, tasks_file, args):
        config = get_active_config()
        header = '\n'.join((self.header, config[self.name]['header']))
        if args.venv is not None:
            venv_activate_path = os.path.join(os.path.normpath(args.venv), 'bin', 'activate')
            header = '\n'.join((header, 'source {}'.format(venv_activate_path)))
        body = self.get_body(tasks_file, args)
        footer = '\n'.join((config[self.name]['footer'], self.footer))
        wrapper_script = header + body + footer
        return wrapper_script

    def save_wrapper_script(self, wrapper_script, jobname, filename='wrapper.sh'):
        scripts_dir = os.path.join('.onager', 'scripts', jobname)
        os.makedirs(scripts_dir, exist_ok=True)
        jobfile = os.path.join(scripts_dir, filename)
        with open(jobfile, 'w') as file:
            file.write(wrapper_script)
        return jobfile

    def get_job_list(self, args):
        raise NotImplementedError

    def get_cancel_cmds(self, cancellations):
        raise NotImplementedError

    def get_time_delta(self, time_str):
        if '-' in time_str:
            days, hours_minutes_seconds = time_str.split('-')
        else:
            days, hours_minutes_seconds = 0, time_str
        t = datetime.strptime(hours_minutes_seconds, "%H:%M:%S")
        partial_days = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        return timedelta(days=int(days)) + partial_days

    def get_log_dir(self):
        log_dir = os.path.join(default_logs_folder, self.name)
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def generate_tasklist(self, commands):
        ids = sorted(commands.keys())
        tasklist = ','.join(map(str, ids))
        return tasklist

    def launch(self, jobs, args, other_args):
        jobids = []

        if len(other_args) != 0:
            additional_args = ' '.join(other_args)
            jobs = [insert_second_to_last(job, additional_args) for job in jobs]

        for job in jobs:
            print(job)
            if not args.dry_run:
                try:
                    byte_str = subprocess.check_output(job, shell=True)
                    jobid = byte_str.decode('utf-8').replace('\n','').split('.')[0]
                    jobids.append(jobid)
                except (subprocess.CalledProcessError, ValueError) as err:
                    print(err)
                    sys.exit()
        job_entries = [(jobid, args.jobname, args.jobfile) for jobid in jobids]
        update_jobindex(job_entries, append=True)
        add_new_history_entry(args.jobname, args.dry_run)
