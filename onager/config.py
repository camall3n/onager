from argparse import Namespace
import configparser
import os
from warnings import warn

from .constants import defaultconfigfile, globalconfigfile, localconfigfile
from . import backends


def print_config(config):
    for section in config.sections():
        print('[{}]'.format(section))
        for key, value in dict(config[section]).items():
            quote = '"""'  if '\n' in value else ''
            print('{} = {}{}{}'.format(key, quote, value, quote))
        print()

def get_active_config():
    settings = configparser.ConfigParser()
    settings.read(defaultconfigfile)
    settings.read(globalconfigfile)
    settings.read(localconfigfile)
    return settings

def config(args):
    if args.read and args.write:
        raise RuntimeError('Cannot read and write at the same time.')
    if args.read and args.global_ and args.local:
        args.global_ = False
        args.local = False
    if args.write and args.global_ and args.local:
        raise RuntimeError('Cannot write to global and local config files simultaneously.')

    settings = configparser.ConfigParser()
    settings.read(defaultconfigfile)
    if args.global_ or not args.local:
        settings.read(globalconfigfile)
    if args.local or not args.global_:
        settings.read(localconfigfile)

    if args.read:
        print_config(settings)
    elif args.write:
        for (backend, key, value) in args.write:
            if backend not in backends.__all__:
                warn('Unable to set {}.{}={} (invalid backend: {}).'.format(backend, key, value, backend))
                continue
            # if key not in settings[backend].keys():
            #     warn('Unable to set {}.{}={} (invalid key: {}).'.format(backend, key, value, key))
            #     continue
            settings[backend][key] = value

        update_config(settings, global_=args.global_)

def update_config(settings, global_=False):
    if global_:
        with open(globalconfigfile, 'w') as config_file:
            settings.write(config_file)
    else:
        with open(localconfigfile, 'w') as config_file:
            settings.write(config_file)

def maybe_merge_config_into_args(config, args):
    args_dict = vars(args)
    config_dict = dict(config['all'])
    for key, val in args_dict.items():
        if val is None and key in config_dict:
            args_dict[key] = config_dict[key]
    for key, val in config_dict.items():
        if key not in args_dict:
            args_dict[key] = val
    return Namespace(**args_dict)
