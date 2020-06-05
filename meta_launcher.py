import argparse
from collections import OrderedDict
import sys

def usage_msg():
    return '''meta_launcher.py
        [ordered args]
        --argA val1
        --argB
        --argC val1 val2 val3
        --meta-command command
        [--meta-tag-name tagname]
        [--meta-tag-args [argA argC]]'''

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Generate commands based on lists of arguments',
                                 prefix_chars='+')
parser.add_argument('+arg', type=str, action='append', nargs='+',
                    metavar=('argname', '[value, ...]'),
                    help='Add an argument with zero or more mutually exclusive values')
parser.add_argument('+command', type=str, required=True)
parser.add_argument('+tag-name', type=str)
parser.add_argument('+tag-args', type=str, nargs='*')
parser.add_argument('+tag-id', type=str)
args, child_args = parser.parse_known_args()

base_cmd = args.command

variables = OrderedDict({arglist[0]: arglist[1:] for arglist in args.arg})

cmd_prefix_list = [base_cmd]

if args.tag_name is not None:
    cmd_suffix_list = ['']
    if args.tag_args is None:
        args.tag_args = list(variables.keys())

sep = ''
for key, value_list in variables.items():
    cmd_prefix_list = [prefix+' '+key+' {}' for prefix in cmd_prefix_list]
    cmd_prefix_list = [prefix.format(v) for v in value_list for prefix in cmd_prefix_list]
    if args.tag_name is not None:
        if key in args.tag_args:
            value_slot = '-{}' if len(value_list) > 1 or value_list[0]!='' else '{}'
            keyname = key.replace('-','').replace('_','')
            cmd_suffix_list = [suffix+sep+keyname+value_slot for suffix in cmd_suffix_list]
            cmd_suffix_list = [suffix.format(v) for v in value_list for suffix in cmd_suffix_list]
        else:
            cmd_suffix_list = [suffix for v in value_list for suffix in cmd_suffix_list]
        sep = '_'

if args.tag_id is not None:
    cmd_suffix_list = [args.tag_id + '-{}_'.format(i) + suffix for (i, suffix) in enumerate(cmd_suffix_list)]

if args.tag_name is not None:
    cmd_prefix_list = [' '.join([prefix, '--'+args.tag_name, suffix]) for (prefix, suffix) in zip(cmd_prefix_list, cmd_suffix_list)]

for cmd in cmd_prefix_list:
    print(cmd)
