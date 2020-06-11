import configparser
import os
from warnings import warn

from .constants import globalconfigfile, localconfigfile
from . import backends

defaults = {
    'DEFAULT': {
        'header': '',
        'footer': '',
    },
    'slurm': {},
    'gridengine': {},
}

def ensure_initialized():
    settings = configparser.ConfigParser()
    settings.read_dict(defaults)
    if not os.path.exists(localconfigfile):
        with open(localconfigfile, 'w') as config_file:
            settings.write(config_file)

def print_config(config):
    for section in config.sections():
        print('[{}]'.format(section))
        for key, value in dict(config[section]).items():
            quote = '"""'  if '\n' in value else ''
            print('{} = {}{}{}'.format(key, quote, value, quote))
        print()

def get_active_config():
    ensure_initialized()
    settings = configparser.ConfigParser()
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
    ensure_initialized()
    settings.read_dict(defaults)
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
        
        if args.global_:
            with open(globalconfigfile, 'w') as config_file:
                settings.write(config_file)
        else:
            with open(localconfigfile, 'w') as config_file:
                settings.write(config_file)