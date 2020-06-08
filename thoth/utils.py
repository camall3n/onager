import json

def load_jobfile(jobfile_path):
    with open(jobfile_path, 'r') as file:
        job_record = json.load(file)
    tag = job_record['tag'] if job_record['tag'] != '' else None
    # json stores all keys as strings, so we convert to ints
    jobs = {int(id): cmd for id, cmd in job_record['jobs'].items()}
    return jobs, tag

def save_jobfile(jobs, jobfile_path, tag=None):
    job_record = dict()
    job_record['tag'] = tag if tag is not None else ''
    job_record['jobs'] = jobs
    with open(jobfile_path, "w+") as jobfile:
        json.dump(job_record, jobfile)

