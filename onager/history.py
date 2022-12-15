from collections import namedtuple
from datetime import datetime
import sys

from tabulate import tabulate

from .constants import history_index
from .utils import load_index, update_index, get_next_index_id

HistoryEntry = namedtuple('HistoryEntry', ['id', 'date', 'time', 'mode', 'dry_run', 'command'])

def make_history_entry(cmd_id, date, time, mode, dry_run, command, args):
    assert dry_run in ['y', 'n']
    entry = HistoryEntry(cmd_id, date, time, mode, (dry_run == 'y'), command)
    if 'hide' in args and args.hide is not None:
        entry = entry._asdict()
        for field in HistoryEntry._fields:
            if field in args.hide:
                entry[field] = '[hidden]'
        entry = HistoryEntry(**entry)
    return entry

def add_new_history_entry(dry_run):
    now = datetime.now()
    history_entry = HistoryEntry(
        id=get_next_index_id(history_index),
        date=now.strftime('%Y.%m.%d'),
        time=now.strftime('%H:%M:%S.%f'),
        mode=sys.argv[1],
        dry_run=dry_run,
        command=' '.join(sys.argv[1:]),
    )
    update_index([get_history_tuple(history_entry)], history_index, append=True)


def get_history_tuple(entry: HistoryEntry) -> str:
    return str(entry.id), entry.date, entry.time, entry.mode, ('y' if entry.dry_run else 'n'), entry.command

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

def print_history(args):
    """Prints onager command history"""
    history_entries = get_history(args)
    def make_printable(entry):
        return str(entry.id), entry.date, entry.time, entry.command

    def should_print(entry):
        no_mode_specified = not (args.prelaunch or args.launch)
        matches_launch = (entry.mode == 'launch') and args.launch
        matches_prelaunch = (entry.mode == 'prelaunch') and args.prelaunch

        if args.since is not None:
            assert len(args.since) <= 2
            date_str, time_str, *_ = args.since + ['00:00:00'] # use midnight if no time specified
            format_str = '%Y.%m.%d %H:%M:%S'
            since_datetime = datetime.strptime(date_str+' '+time_str, format_str)
            entry_datetime = datetime.strptime(entry.date+' '+entry.time, format_str+'.%f')
            matches_datetime = entry_datetime > since_datetime
        else:
            matches_datetime = True

        valid_mode = no_mode_specified or matches_launch or matches_prelaunch
        filtered = (entry.dry_run and args.no_dry_run)
        return valid_mode and matches_datetime and not filtered

    N = args.n or len(history_entries)
    printable_history = [
        make_printable(entry) for entry in history_entries[-N:] if should_print(entry)
    ]

    fields = [field for field in HistoryEntry._fields if field not in ['mode', 'dry_run']]
    print(tabulate(printable_history, headers=fields))
