from collections import OrderedDict
import json
import os

from .utils import load_jobfile

def meta_launch(args):
    base_cmd = args.command

    variables = OrderedDict({arglist[0]: arglist[1:] for arglist in args.arg})

    cmd_prefix_list = [base_cmd]

    if args.tag is not None:
        cmd_suffix_list = ['']
        if args.tag_args is None:
            args.tag_args = list(variables.keys())

    sep = ''
    for key, value_list in variables.items():
        cmd_prefix_list = [prefix + ' ' + key + ' {}' for prefix in cmd_prefix_list]
        cmd_prefix_list = [prefix.format(v) for v in value_list for prefix in cmd_prefix_list]
        if args.tag is not None:
            if key in args.tag_args:
                value_slot = '-{}' if len(value_list) > 1 or value_list[0] != '' else '{}'
                keyname = key.replace('-', '').replace('_', '')
                cmd_suffix_list = [
                    suffix + sep + keyname + value_slot for suffix in cmd_suffix_list
                ]
                cmd_suffix_list = [
                    suffix.format(v) for v in value_list for suffix in cmd_suffix_list
                ]
            else:
                cmd_suffix_list = [suffix for v in value_list for suffix in cmd_suffix_list]
            sep = '_'

    cmd_suffix_list = [
        args.jobname + '-{}_'.format(i) + suffix
        for (i, suffix) in enumerate(cmd_suffix_list, args.jobname_start)
    ]

    if args.tag is not None:
        cmd_prefix_list = [
            ' '.join([prefix, '--' + args.tag, suffix])
            for (prefix, suffix) in zip(cmd_prefix_list, cmd_suffix_list)
        ]

    jobfile_path = args.jobfile.format(jobname=args.jobname)
    os.makedirs(os.path.dirname(jobfile_path), exist_ok=True)
    if args.append:
        jobs = load_jobfile(jobfile_path)
    else:
        jobs = dict()
    with open(jobfile_path, "w+") as jobfile:
        for i, cmd in enumerate(cmd_prefix_list, args.jobname_start):
            if args.verbose:
                print(cmd)
            jobs[i] = cmd
        json.dump(jobs, jobfile)
