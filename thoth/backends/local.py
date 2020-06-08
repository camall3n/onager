import math
from multiprocessing import Pool, cpu_count
import os
import socket

from ._backend import Backend
from .worker import run_command_by_id
from ..utils import load_jobfile


class LocalBackend(Backend):
    def __init__(self):
        super().__init__()
        hostname = socket.gethostname().replace('.local', '')
        self.name = hostname

    def get_job_list(self, args):
        return None

    def get_next_jobid(self):
        return 0

    def launch(self, jobs, args):
        self.commands = load_jobfile(args.jobfile)[0]
        self.verbose = args.verbose
        log_name = '{}_{}'.format(args.jobname, self.get_next_jobid())
        self.log_path = os.path.join(self.get_log_dir(), log_name)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        task_ids = self.expand_ids(args.tasklist)

        n_workers = max(1, math.floor(cpu_count() /
                                      args.cpus)) if args.maxtasks <= 0 else args.maxtasks
        if self.verbose:
            print('Starting multiprocessing pool with {} workers'.format(n_workers))
        pool = Pool(n_workers, maxtasksperchild=1)
        pool.map(self.process_one_job, task_ids)
        pool.close()
        pool.join()

    def process_one_job(self, task_id):
        run_command_by_id(
            self.commands,
            task_id,
            stdout=self.log_path + '_{}.o'.format(task_id),
            stderr=self.log_path + '_{}.e'.format(task_id),
            verbose=self.verbose,
        )
