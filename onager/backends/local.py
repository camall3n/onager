import math
from multiprocessing import Pool
import os
import socket

from ._backend import Backend
from ..worker import run_command_by_id
from ..utils import expand_ids, load_jobfile, update_jobindex, get_next_index_jobid, cpu_count

class LocalBackend(Backend):
    def __init__(self, logging_name=None):
        super().__init__()
        if logging_name is None:
            hostname = socket.gethostname().replace('.local', '')
            self.name = hostname
        else:
            self.name = logging_name

    def get_job_list(self, args):
        return load_jobfile(args.jobfile)[0]

    def get_next_jobid(self):
        return 0

    def get_n_workers(self, task_ids, maxtasks, cpus):
        if maxtasks > 0:
            n_workers = maxtasks
        else:
            max_parallel = math.floor(cpu_count() / cpus)
            workers_available = max(1, max_parallel)
            workers_needed = len(task_ids)
            n_workers = min(workers_needed, workers_available)
        return n_workers

    def send_jobs_to_pool(self, n_workers, task_ids, quiet=False):
        if not quiet:
            print('Starting multiprocessing pool with {} workers'.format(n_workers))
        pool = Pool(n_workers, maxtasksperchild=1)# Each new tasks gets a fresh worker
        pool.map(self.process_one_job, task_ids)
        pool.close()
        pool.join()

    def launch(self, jobs, args, other_args):
        self.commands = jobs
        if len(other_args) != 0:
            raise RuntimeError("{}: Cannot pass in additional args {}".format(
                self.name, ' '.join(other_args)))
        self.quiet = args.quiet
        log_name = '{}_{}'.format(args.jobname, self.get_next_jobid())
        self.log_path = os.path.join(self.get_log_dir(), log_name)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        task_ids = expand_ids(args.tasklist)

        job_entries = [(get_next_index_jobid(), args.jobname, args.jobfile)]
        update_jobindex(job_entries, append=True)

        n_workers = self.get_n_workers(task_ids, args.max_tasks, args.cpus)
        if not args.dry_run:
            self.send_jobs_to_pool(n_workers, task_ids, args.quiet)

    def multilaunch(self, jobs, args):
        self.commands = jobs
        self.quiet = False
        subjob_log_dirname = '{}_{}_subjobs'.format(args.logging_jobname, args.logging_multijobid)
        subjob_log_dir = os.path.join(self.get_log_dir(), subjob_log_dirname)
        log_name = '{}'.format(args.subjob_group_id)
        self.log_path = os.path.join(subjob_log_dir, log_name)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        task_ids = expand_ids(args.tasklist)

        n_workers = self.get_n_workers(task_ids, args.max_subjobs, cpus=1)
        self.send_jobs_to_pool(n_workers, task_ids, quiet=self.quiet)


    def process_one_job(self, task_id):
        run_command_by_id(
            self.commands,
            task_id,
            stdout=self.log_path + '_{}.o'.format(task_id),
            stderr=self.log_path + '_{}.e'.format(task_id),
            quiet=self.quiet,
        )
