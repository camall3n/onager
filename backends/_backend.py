from datetime import datetime, timedelta
import os

class Backend:
    def __init__(self):
        self.name = 'generic_backend'
        self.header = """#!/bin/bash
        """

        self.body = """python -m worker {}
        """

        self.footer = """"""

        self.task_id_var = r'$TASK_ID'

    def wrap_tasks(self, tasks_file, stdout=None, stderr=None):
        body = self.body.format(tasks_file, self.task_id_var)
        wrapper_script = self.header + body + self.footer
        return wrapper_script

    def save_wrapper_script(self, wrapper_script, jobname):
        scripts_dir = ".thoth/scripts/{}/{}/".format(self.name, jobname)
        os.makedirs(scripts_dir, exist_ok=True)
        jobfile = os.path.join(scripts_dir, 'wrapper.sh')
        with open(jobfile, 'w') as file:
            file.write(wrapper_script)
        return jobfile

    def get_job_list(self, args):
        raise NotImplementedError

    def get_time_delta(self, time_str):
        days, hours_minutes_seconds = time_str.split('-')
        t = datetime.strptime(hours_minutes_seconds, "%H:%M:%S")
        partial_days = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        return timedelta(days=int(days)) + partial_days

    def get_log_dir(self):
        log_dir = ".thoth/logs/{}/".format(self.name)
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
