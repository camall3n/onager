import os

# Basic constants
default_scripts_folder = os.path.join('.onager', 'scripts')
default_logs_folder = os.path.join('.onager', 'logs')
default_index = os.path.join('.onager', 'job_index.csv') # id,jobname,jobfile_path
defaultjobfile = os.path.join(default_scripts_folder, '{jobname}', 'jobs.json')
globalconfigfile = os.path.join(os.path.expanduser('~'), '.onagerconfig')
localconfigfile = os.path.join('.onager', 'config')

# Separators
sep = '_'
wsep = '__'
flag_on = '+'
flag_off = '-'
