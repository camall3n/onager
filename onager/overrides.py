from argparse import Namespace

from .config import get_active_config, update_config
from .utils import ask_user_yes_or_no


def get_partition_name(args: Namespace, backend):
    if args.partition is not None:
        return args.partition

    config = get_active_config()
    if config['all']['partition']:
        # TODO: check if it's a valid partition?
        return config['all']['partition']

    partitions = backend.get_partition_names()
    print(partitions)
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

    return partition
