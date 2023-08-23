import os

# Basic constants
onager_folder = os.path.dirname(os.environ['VIRTUAL_ENV']) + '/.onager'
default_scripts_folder = os.path.join(onager_folder, 'scripts')
default_logs_folder = os.path.join(onager_folder, 'logs')
job_index = os.path.join(onager_folder, 'job_index.csv') # id,jobname,jobfile_path
history_index = os.path.join(onager_folder, 'history_index.csv')
defaultjobfile = os.path.join(default_scripts_folder, '{jobname}', 'jobs.json')
globalconfigfile = os.path.join(os.path.expanduser('~'), '.onagerconfig')
localconfigfile = os.path.join(onager_folder, 'config')

# Separators
SEP = '_'
WSEP = '__'
FLAG_ON = '+'
FLAG_OFF = '-'
