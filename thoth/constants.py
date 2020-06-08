import os

# Basic constants
default_scripts_folder = os.path.join('.thoth', 'scripts')
default_logs_folder = os.path.join('.thoth', 'logs')
default_index = os.path.join('.thoth', 'job_index.csv') # id,jobname,jobfile_path
defaultjobfile = os.path.join(default_scripts_folder, '{jobname}', 'jobs.json')