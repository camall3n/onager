from collections import OrderedDict
import json
import os
from warnings import warn

from .utils import load_jobfile

def meta_launch(args):
    base_cmd = args.command

    variables = OrderedDict({arglist[0]: arglist[1:] for arglist in args.arg})
    base_cmd_args = list(variables.keys())

    cmd_prefix_list = [base_cmd]

    if args.tag == '':
        raise ValueError("+tag cannot be an empty string")

    if args.tag is not None:
        cmd_suffix_list = ['']
        if args.tag_args is None:
            args.tag_args = base_cmd_args
        else:
            for tag_arg in args.tag_args:
                if tag_arg not in base_cmd_args:
                    warn(RuntimeWarning("{} is not a command arg: {}".format(tag_arg,
                        base_cmd_args)))
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

    jobfile_path = args.jobfile.format(jobname=args.jobname)
    os.makedirs(os.path.dirname(jobfile_path), exist_ok=True)

    if args.append:
        jobs = load_jobfile(jobfile_path)
        jobname_start = max(jobs.keys()) + 1
    else:
        jobs = dict()
        jobname_start = 0

    if args.tag is not None:
        cmd_suffix_list = [
            args.jobname + '-{}_'.format(i) + suffix
            for (i, suffix) in enumerate(cmd_suffix_list, jobname_start)
        ]
        cmd_prefix_list = [
            ' '.join([prefix, '--' + args.tag, suffix])
            for (prefix, suffix) in zip(cmd_prefix_list, cmd_suffix_list)
        ]

    with open(jobfile_path, "w+") as jobfile:
        for i, cmd in enumerate(cmd_prefix_list, jobname_start):
            if args.verbose:
                print(cmd)
            jobs[i] = cmd
        json.dump(jobs, jobfile)
