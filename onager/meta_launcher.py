from collections import OrderedDict
import os
from warnings import warn

from .utils import load_jobfile, save_jobfile
from .constants import SEP, WSEP, FLAG_ON, FLAG_OFF
from .history import add_new_history_entry

def filter_cmd_prefix(exclude_variables, cmd_prefix_list, VAR_SEP=' '):
    exclude_arg_keys = []
    for key, variable in exclude_variables.items():
        curr_key_strs = []
        for v in variable:
            curr_key_strs.append(key + VAR_SEP + v)

        exclude_arg_keys.append(curr_key_strs)

    filtered_prefix_list = []
    for cmd_prefix in cmd_prefix_list:
        all_keys_match = True if exclude_arg_keys else False
        for curr_key_strs in exclude_arg_keys:
            all_keys_match &= any(key_str in cmd_prefix for key_str in curr_key_strs)

            if not all_keys_match:
                break

        if not all_keys_match:
            filtered_prefix_list.append(cmd_prefix)

    return filtered_prefix_list

def meta_launch(args):
    base_cmd = args.command

    if args.arg_mode == 'argparse':
        VAR_SEP = ' '
    elif args.arg_mode == 'hydra':
        VAR_SEP = '='
    else:
        raise NotImplementedError(f'Unknown arg mode: {args.arg_mode}')

    variables = OrderedDict()
    exclude_variables = OrderedDict()
    if args.arg is not None:
        variables = OrderedDict({arglist[0]: arglist[1:] for arglist in args.arg})
        if args.exclude is not None:
            exclude_variables = OrderedDict({arglist[0]: arglist[1:] for arglist in args.exclude})


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
            value_slot = WSEP + '{}'
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
            cmd_prefix_list = [prefix + VAR_SEP + '{}' for prefix in cmd_prefix_list]
            cmd_prefix_list = [prefix.format(v) for v in value_list for prefix in cmd_prefix_list]
        if args.tag is not None:
            if key in args.tag_args:
                value_slot = SEP + '{}' if len(value_list) > 0 else ''
                keyname = key.replace('_', '').replace('-', '').replace('=','_').replace('/','.')
                cmd_suffix_list = [
                    suffix + WSEP + keyname + value_slot for suffix in cmd_suffix_list
                ]
                if len(value_list) > 0:
                    cmd_suffix_list = [
                        suffix.format(v) for v in value_list for suffix in cmd_suffix_list
                    ]
            else:
                cmd_suffix_list = [suffix for v in value_list for suffix in cmd_suffix_list]

    cmd_prefix_list = filter_cmd_prefix(exclude_variables, cmd_prefix_list, VAR_SEP=VAR_SEP)

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
                suffix.format(WSEP + s + flag.replace(FLAG_OFF, '').replace(FLAG_ON, ''))
                for s in [FLAG_ON, FLAG_OFF]
                for suffix in cmd_suffix_list
            ]

    jobfile_path = args.jobfile.format(jobname=args.jobname)
    os.makedirs(os.path.dirname(jobfile_path), exist_ok=True)

    if args.append:
        cmds, tags = load_jobfile(jobfile_path)
        start_jobid = max(cmds.keys()) + 1
        jobs = {i: (cmds[i], tags[i]) for i in cmds.keys()}
    else:
        jobs = dict()
        start_jobid = 1

    if args.tag is not None:
        if args.no_tag_number:
            tag_list = [args.jobname + suffix for suffix in cmd_suffix_list]
        else:
            n_digits = len(str(start_jobid + len(cmd_suffix_list) - 1))
            tag_number_format = '{{:0{0}d}}'.format(n_digits)
            tag_list = [
                args.jobname + SEP + tag_number_format.format(i) + suffix
                for (i, suffix) in enumerate(cmd_suffix_list, start_jobid)
            ]

        cmd_prefix_list = [
            (prefix + ' ' + args.tag + VAR_SEP + suffix)
            for (prefix, suffix) in zip(cmd_prefix_list, tag_list)
        ]
    else:
        tag_list = [""]*len(cmd_prefix_list)

    for i, (cmd,tag) in enumerate(zip(cmd_prefix_list,tag_list), start_jobid):
        if not args.quiet:
            print(cmd)
        jobs[i] = (cmd,tag)

    print(f"Prelaunched {len(jobs)} jobs for {args.jobname}.")

    save_jobfile(jobs, jobfile_path, args.tag)
    add_new_history_entry(jobname=args.jobname, dry_run=False)
