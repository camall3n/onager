from collections import OrderedDict
import os
from warnings import warn

from .utils import load_jobfile, save_jobfile
from .constants import sep, wsep, flag_on, flag_off

def meta_launch(args):
    base_cmd = args.command

    if args.arg is not None:
        variables = OrderedDict({arglist[0]: arglist[1:] for arglist in args.arg})
    else:
        variables = OrderedDict()

    if args.pos_arg is not None:
        pos_variables = args.pos_arg
    else:
        pos_variables = []

    if args.flag is not None:
        flag_variables = args.flag
    else:
        flag_variables = []

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


    # Positional arguments
    for value_list in pos_variables:
        cmd_prefix_list = [prefix + ' {}' for prefix in cmd_prefix_list]
        cmd_prefix_list = [prefix.format(v) for v in value_list for prefix in cmd_prefix_list]
        if args.tag is not None:
            value_slot = wsep + '{}'
            cmd_suffix_list = [
                suffix + value_slot for suffix in cmd_suffix_list
            ]
            cmd_suffix_list = [
                suffix.format(v) for v in value_list for suffix in cmd_suffix_list
            ]

    # Optional arguments
    for key, value_list in variables.items():
        cmd_prefix_list = [prefix + ' ' + key for prefix in cmd_prefix_list]
        if len(value_list) > 0:
            cmd_prefix_list = [prefix + ' {}' for prefix in cmd_prefix_list]
            cmd_prefix_list = [prefix.format(v) for v in value_list for prefix in cmd_prefix_list]
        if args.tag is not None:
            if key in args.tag_args:
                value_slot = sep + '{}' if len(value_list) > 0 else ''
                keyname = key.replace('_', '').replace('-', '')
                cmd_suffix_list = [
                    suffix + wsep + keyname + value_slot for suffix in cmd_suffix_list
                ]
                if len(value_list) > 0:
                    cmd_suffix_list = [
                        suffix.format(v) for v in value_list for suffix in cmd_suffix_list
                    ]
            else:
                cmd_suffix_list = [suffix for v in value_list for suffix in cmd_suffix_list]

    # Flag/Boolean arguments
    for flag in flag_variables:
        cmd_prefix_list = [prefix + ' {}' for prefix in cmd_prefix_list] + cmd_prefix_list
        cmd_prefix_list = [
            prefix.format(flag) if '{}' in prefix else prefix
            for prefix in cmd_prefix_list
        ]
        if args.tag is not None:
            cmd_suffix_list = [
                suffix + '{}' for suffix in cmd_suffix_list
            ]
            cmd_suffix_list = [
                suffix.format(wsep + s + flag.replace(flag_off, '').replace(flag_on, ''))
                for s in [flag_on, flag_off]
                for suffix in cmd_suffix_list
            ]

    jobfile_path = args.jobfile.format(jobname=args.jobname)
    os.makedirs(os.path.dirname(jobfile_path), exist_ok=True)

    if args.append:
        jobs, tags = load_jobfile(jobfile_path)
        start_jobid = max(jobs.keys()) + 1
    else:
        jobs = dict()
        start_jobid = 1

    if args.tag is not None:
        tag_list = [
            args.jobname + sep + '{}'.format(i) + suffix
            for (i, suffix) in enumerate(cmd_suffix_list, start_jobid)
        ]
        cmd_prefix_list = [
            ' '.join([prefix, args.tag, suffix])
            for (prefix, suffix) in zip(cmd_prefix_list, tag_list)
        ]
    else:
        tag_list = [""]*len(cmd_prefix_list)

    for i, (cmd,tag) in enumerate(zip(cmd_prefix_list,tag_list), start_jobid):
        if not args.quiet:
            print(cmd)
        jobs[i] = (cmd,tag)

    save_jobfile(jobs, jobfile_path, args.tag)
