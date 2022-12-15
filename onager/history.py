from collections import namedtuple
from datetime import datetime
from shutil import get_terminal_size
import sys
from textwrap import TextWrapper

from tabulate import tabulate

from .constants import history_index
from .utils import load_index, update_index, get_next_index_id

HistoryEntry = namedtuple('HistoryEntry',
                          ['id', 'date', 'time', 'jobname', 'mode', 'dry_run', 'args'])

def make_history_entry(cmd_id, date, time, jobname, mode, dry_run, cmd_args, args):
    assert dry_run in ['y', 'n']
    entry = HistoryEntry(cmd_id, date, time, jobname, mode, (dry_run == 'y'), cmd_args)
    if 'hide' in args and args.hide is not None:
        entry = entry._asdict()
        for field in HistoryEntry._fields:
            if field in args.hide:
                entry[field] = '[hidden]'
        entry = HistoryEntry(**entry)
    return entry

def add_new_history_entry(jobname, dry_run):
    now = datetime.now()
    history_entry = HistoryEntry(
        id=get_next_index_id(history_index),
        date=now.strftime('%Y.%m.%d'),
        time=now.strftime('%H:%M:%S.%f'),
        jobname=jobname,
        mode=sys.argv[1],
        dry_run=dry_run,
        args=' '.join(sys.argv[2:]),
    )
    update_index([get_history_tuple(history_entry)], history_index, append=True)


def get_history_tuple(entry: HistoryEntry) -> str:
    return (
        str(entry.id),
        entry.date,
        entry.time,
        entry.jobname,
        entry.mode,
        ('y' if entry.dry_run else 'n'),
        entry.args,
    )

def get_history(args):
    history_list = []
    try:
        index = load_index(history_index)
    except (IOError):
        return history_list
    for cmd_id, cmd_details in index.items():
        entry = make_history_entry(
            cmd_id,
            *cmd_details,
            args
        )
        history_list.append(entry)
    return history_list

def check_details_match(entry, args):
    if args.details is None:
        return True
    try:
        return (int(entry.id) == int(args.details))
    except ValueError:
        return (entry.jobname == args.details)

def check_mode_valid(entry, args):
    no_mode_specified = not (args.prelaunch or args.launch)
    matches_launch = (entry.mode == 'launch') and args.launch
    matches_prelaunch = (entry.mode == 'prelaunch') and args.prelaunch
    return no_mode_specified or matches_launch or matches_prelaunch

def check_datetime_matches(entry, args):
    if args.since is None:
        return True
    assert len(args.since) <= 2
    date_str, time_str, *_ = args.since + ['00:00:00'] # use midnight if no time specified
    format_str = '%Y.%m.%d %H:%M:%S'
    since_datetime = datetime.strptime(date_str+' '+time_str, format_str)
    entry_datetime = datetime.strptime(entry.date+' '+entry.time, format_str+'.%f')
    return entry_datetime > since_datetime

def should_print(entry, args):
    matches_details = check_details_match(entry, args)
    valid_mode = check_mode_valid(entry, args)
    matches_datetime = check_datetime_matches(entry, args)
    filtered = (entry.dry_run and args.no_dry_run)
    return matches_details and valid_mode and matches_datetime and not filtered

def make_printable(entry, skip_cmd=False, wrap_cmd=False, cmd_width=None):
    result = [str(entry.id), entry.date, entry.time[:-3], entry.jobname, entry.mode]
    if skip_cmd:
        pass # don't print the command
    else:
        if wrap_cmd:
            cmd_str = '\n'.join(TextWrapper(cmd_width).wrap(entry.args))
        else:
            cmd_str = entry.args
            if cmd_width is not None:
                cmd_str = cmd_str[:cmd_width]
                if len(entry.args) > cmd_width:
                    cmd_str = cmd_str[:-5] + '[...]'
        result.append(cmd_str)
    return tuple(result)

def compute_command_width(filtered_history, fields, args):

    full_table_str = tabulate([make_printable(entry) for entry in filtered_history], headers=fields)
    full_width = len(full_table_str.split('\n')[1])
    full_command_width = max([0]+[len(entry.args) for entry in filtered_history])
    base_width = full_width - full_command_width
    min_width = base_width + len('args__')
    terminal_width = args.width or get_terminal_size()[0]
    if len(filtered_history) == 0 or min_width > terminal_width:
        cmd_width = len('args__')
    elif full_width > terminal_width:
        excess_width = full_width - terminal_width
        cmd_width = full_command_width - excess_width
    else:
        cmd_width = full_command_width
    return cmd_width

def print_history(args):
    """Prints onager command history"""
    history_entries = get_history(args)
    if args.details == '-1' and history_entries:
        args.details = history_entries[-1].id

    N = args.n or len(history_entries)
    filtered_history = [entry for entry in history_entries[-N:] if should_print(entry, args)]

    show_details = (args.details is not None)
    if show_details and (len(filtered_history) > 1):
        print('Cannot show details for multiple entries:')
        print()
        show_details = False

    ignored_fields = ['dry_run']
    if show_details:
        ignored_fields.append('args')
    fields = [f for f in HistoryEntry._fields if f not in ignored_fields]
    cmd_width = compute_command_width(filtered_history, fields, args)

    def format_entry(entry):
        return make_printable(entry,
                              skip_cmd=show_details,
                              wrap_cmd=args.full,
                              cmd_width=cmd_width)

    print(tabulate([format_entry(entry) for entry in filtered_history], headers=fields))

    if show_details and len(filtered_history) > 0:
        entry = filtered_history[0]
        print()
        print('onager ' + entry.mode + ' ' + entry.args)
