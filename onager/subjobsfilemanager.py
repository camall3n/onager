import csv
from pathlib import Path

class SubjobsFileManager:
    def __init__(self, subjobs_filename):
        self._subjobs_filename = subjobs_filename
        self._subjobs = self._get_subjobs_dict()
        self._next_subjob_groupid = 1 if not self._subjobs else max(self._subjobs.keys()) + 1

    def _get_subjobs_dict(self) -> dict:
        subjobs = dict()
        Path(self._subjobs_filename).touch(exist_ok=True)
        with open(self._subjobs_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                subjobs[int(row[0])] = row[1]
        return subjobs

    def get_subjobs_dict(self) -> dict:
        return self._subjobs

    def add_subjobs(self, list_of_tasklist_strings: list) -> None:
        subjob_groupids = []
        with open(self._subjobs_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for tasklist_str in list_of_tasklist_strings:
                subjob_groupid = self._next_subjob_groupid
                writer.writerow([subjob_groupid, tasklist_str])
                self._subjobs[subjob_groupid] = tasklist_str
                subjob_groupids.append(subjob_groupid)
                self._next_subjob_groupid += 1
        return subjob_groupids
