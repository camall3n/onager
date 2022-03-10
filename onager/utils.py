import csv
from itertools import count, groupby
import json
import os
import sys

from . import constants

def ensure_onager_folders_exist():
    if not os.path.isdir(constants.onager_folder):
        print("This appears to be your first time running onager in this folder.")
        print()
        print("Allow onager to store files in the directory './.onager/'?")
        response = input("[y/n] > ")
        if response not in ['y', 'Y', 'yes', 'Yes']:
            print('Setup canceled.')
            sys.exit()
        else:
            print("Created folder: './.onager/'")
            print()
    os.makedirs(constants.default_logs_folder, exist_ok=True)
    os.makedirs(constants.default_scripts_folder, exist_ok=True)


def cpu_count():
    # os.cpu_count()
    #     returns number of cores on machine
    # os.sched_getaffinity(pid)
    #     returns set of cores on which process is allowed to run
    #     if pid=0, results are for current process
    #
    # if os.sched_getaffinity doesn't exist, just return cpu_count and hope for the best
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count()

def load_jobfile(jobfile_path):
    with open(jobfile_path, 'r') as file:
        job_records = json.load(file)
    # json stores all keys as strings, so we convert to ints
    jobs = {int(id_): record[0] for id_, record in job_records.items()}
    tags = {int(id_): record[1] for id_, record in job_records.items()}
    return jobs, tags

def save_jobfile(jobs, jobfile_path, tag=None):
    with open(jobfile_path, "w+") as jobfile:
        json.dump(jobs, jobfile)

def compute_subjobs_filename(jobfile_path):
    jobdir = os.path.dirname(jobfile_path)
    return os.path.join(jobdir, 'subjobs.csv')

def load_jobindex():
    with open(constants.default_index, 'r', newline='') as job_index:
        csv_reader = csv.reader(job_index, delimiter=',', quotechar='|')
        index = {job_entry[0]: job_entry[1:] for job_entry in csv_reader}
    return index

def get_next_index_jobid():
    try:
        ids = load_jobindex().keys()
    except IOError:
        ids = []
    try:
        next_jobid = max(map(int,ids)) + 1
    except ValueError:
        next_jobid = 0
    return next_jobid

def update_jobindex(job_entries, append=True):
    mode = 'w+' if not append else 'a+'
    with open(constants.default_index, mode, newline='') as job_index:
        csv_writer = csv.writer(job_index, delimiter=',', quotechar='|')
        csv_writer.writerows(job_entries)

def condense_ids(id_list):
    G = (list(x) for _, x in groupby(id_list, lambda x, c=count(): next(c) - x))
    return ",".join("-".join(map(str, (g[0], g[-1])[:len(g)])) for g in G)

def expand_ids(tasklist):
    return [i for r in _generate_id_ranges(tasklist) for i in r]

def _generate_id_ranges(tasklist):
    task_blocks = tasklist.split(',')
    for task_block in task_blocks:
        if ':' in task_block:
            task_block, step = task_block.split(':')
            step = int(step)
        else:
            step = 1
        if '-' in task_block:
            first, last = map(int, task_block.split('-'))
        else:
            first = int(task_block)
            last = first
        yield range(first, last + 1, step)

def insert_second_to_last(cmd, insert_str, sep=' '):
    cmd = cmd.split(sep)
    return sep.join(cmd[:-1]) + sep + insert_str + sep + cmd[-1]

def split_tasklist_into_subjob_groups(tasklist, tasks_per_node):
    jobids = expand_ids(tasklist)
    list_of_tasklist_strings = [
        condense_ids(jobids[i:i+tasks_per_node]) for i in range(0, len(jobids), tasks_per_node)
    ]
    return list_of_tasklist_strings
