import os

# Basic constants
onager_folder = '.onager'
default_scripts_folder = os.path.join(onager_folder, 'scripts')
default_logs_folder = os.path.join(onager_folder, 'logs')
default_index = os.path.join(onager_folder, 'job_index.csv') # id,jobname,jobfile_path
defaultjobfile = os.path.join(default_scripts_folder, '{jobname}', 'jobs.json')
globalconfigfile = os.path.join(os.path.expanduser('~'), '.onagerconfig')
localconfigfile = os.path.join(onager_folder, 'config')

# Separators
sep = '_'
wsep = '__'
flag_on = '+'
flag_off = '-'
