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

parser = argparse.ArgumentParser(description='Generate commands based on lists of arguments', usage=usage_msg())
parser.add_argument('--meta-command', type=str, required=True)
parser.add_argument('--meta-tag-name', type=str)
parser.add_argument('--meta-tag-args', type=str, nargs='*')
parser.add_argument('--meta-tag-id', type=str)
args, child_args = parser.parse_known_args()

base_cmd = args.meta_command

variables = OrderedDict({None: []})
current_var = None
for arg in child_args:
    if '--' == arg[:2]:
        # variable
        if current_var is not None and not variables[current_var]:
            variables[current_var] = ['']
        current_var = arg[2:]
        variables[current_var] = []
    else:
        variables[current_var].append(arg)
if current_var is not None and not variables[current_var]:
    variables[current_var] = ['']
if variables[None]:
    base_cmd = base_cmd + ' ' + ' '.join(variables[None])
del variables[None]

cmd_prefix_list = [base_cmd]

if args.meta_tag_name is not None:
    cmd_suffix_list = ['']
    if args.meta_tag_args is None:
        args.meta_tag_args = list(variables.keys())

sep = ''
for key, value_list in variables.items():
    cmd_prefix_list = [prefix+' --'+key+' {}' for prefix in cmd_prefix_list]
    cmd_prefix_list = [prefix.format(v) for v in value_list for prefix in cmd_prefix_list]
    if args.meta_tag_name is not None:
        if key in args.meta_tag_args:
            value_slot = '-{}' if len(value_list) > 1 or value_list[0]!='' else '{}'
            keyname = key.replace('-','').replace('_','')
            cmd_suffix_list = [suffix+sep+keyname+value_slot for suffix in cmd_suffix_list]
            cmd_suffix_list = [suffix.format(v) for v in value_list for suffix in cmd_suffix_list]
        else:
            cmd_suffix_list = [suffix for v in value_list for suffix in cmd_suffix_list]
        sep = '_'

if args.meta_tag_id is not None:
    cmd_suffix_list = [args.meta_tag_id + '-{}_'.format(i) + suffix for (i, suffix) in enumerate(cmd_suffix_list)]

if args.meta_tag_name is not None:
    cmd_prefix_list = [' '.join([prefix, '--'+args.meta_tag_name, suffix]) for (prefix, suffix) in zip(cmd_prefix_list, cmd_suffix_list)]

for cmd in cmd_prefix_list:
    print(cmd)
