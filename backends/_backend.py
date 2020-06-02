
class Backend:
    def __init__(self):
        self.name = 'generic_backend'
        self.header = """#!/bin/bash
        """

        self.body = """python -m worker {}
        """

        self.footer = """"""

        self.task_id_var = r'$TASK_ID'

    def wrap_tasks(self, tasks_file, single_task=False, stdout=None, stderr=None):
        body = self.body.format(tasks_file)
        if not single_task:
            body += body.task_id_var
        wrapper_script = self.header + body + self.footer
        return wrapper_script

    def save_wrapper_script(self, wrapper_script, jobname):
        scripts_dir = "scripts/{}".format(self.name)
        os.makedirs(scripts_dir, exist_ok=True)
        jobfile = os.join(scripts_dir, jobname)
        with open(jobfile, 'w') as file:
            file.write(wrapper_script)

    def get_job_list(self, args):
        raise NotImplementedError
