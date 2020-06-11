import csv
from itertools import count, groupby
import json

from .constants import default_index

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

def load_jobindex():
    with open(default_index, 'r', newline='') as job_index:
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
    with open(default_index, mode, newline='') as job_index:
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
