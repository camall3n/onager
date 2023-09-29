from argparse import Namespace

from .config import get_active_config, update_config

def ask_user_yes_or_no(question:str = 'Are you sure?'):
    yes_or_no = input(f'{question} (y/[n])\n> ')
    if yes_or_no in ['y','yes','Y',"YES"]:
        return True
    else:
        if yes_or_no not in ['n','no','N',"NO",'']:
            print('Unable to process response "{}". Assuming [n].'.format(yes_or_no))
    return False

command_to_get_slurm_partition_names = 'sinfo -o %R | tail -n +2'
command_to_get_gridengine_partition_names = "qstat -g c | awk 'NR>2 {print $1}' | sed 's/\.q//'"

def get_partition_name(args: Namespace):
    if args.partition is not None:
        return args.partition

    config = get_active_config()
    if config['all']['partition']:
        # TODO: check if it's a valid partition?
        return config['all']['partition']

    partitions = ['super_secret_partition1', 'foo']# TODO: get_partition_names()
    if len(partitions) == 1:
        return partitions[0]

    print(f'No default partition name has been configured. We detected the following partitions (although there may be more):')
    print(partitions)
    partition = input('What partition do you want to use?\n> ')

    if partition in partitions:
        should_save = ask_user_yes_or_no('Would you like to update the default partition for this project?')
        if should_save:
            config['all']['partition'] = partition
            update_config(config)

    return ''
