import argparse
from collections import OrderedDict
import sys

def meta_launch(args):
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
