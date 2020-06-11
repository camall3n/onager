import unittest
from argparse import Namespace

from onager import meta_launcher
from onager.utils import load_jobfile
from onager.constants import defaultjobfile

class TestPrelaunchMisc(unittest.TestCase):

    def test_custom_jobfile(self):
        pass

    def test_append_jobfile(self):
        pass

class TestPrelaunchTagging(unittest.TestCase):

    def test_no_tagging(self):
        pass

    def test_default_tagging(self):
        pass

    def test_custom_tagging(self):
        pass

    def test_tagging_positional(self):
        pass

    def test_tagging_optional(self):
        pass

    def test_tagging_flag(self):
        pass

    def test_tagging_combined(self):
        pass

class TestPrelaunchFlagArgs(unittest.TestCase):

    def test_multiple_flag_args(self):
        pass

    def test_single_flag_arg(self):
        pass

class TestPrelaunchPositionalArgs(unittest.TestCase):

    def test_single_positional(self):
        pass

    def test_single_positional_multi_value(self):
        pass

    def test_single_multiple_positional_single_value(self):
        pass

    def test_single_multiple_positional_multi_value(self):
        pass

class TestPrelaunchOptionalArgs(unittest.TestCase):

    def test_multiple_args_single_value(self):
        args = Namespace(**{
            "command": "echo",
            "jobname": "testecho" ,
            "jobfile": defaultjobfile,
            "arg": [["--test", "hi"], ["--test2", "hi2"]],
            "pos_arg": None,
            "flag": None,
            "tag": "--tag",
            "tag_args": None,
            "append": None,
            "quiet": True,
        })
        meta_launcher.meta_launch(args)
        jobs = load_jobfile(args.jobfile.format(jobname=args.jobname)) # pylint: disable=no-member
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual("echo --test hi --test2 hi2 --tag testecho_1__test_hi__test2_hi2", jobs[0][1])

    def test_multiple_value_args(self):
        args = Namespace(**{
            "command": "echo",
            "jobname": "testecho" ,
            "jobfile": defaultjobfile,
            "arg": [["--test", "hi", "bye"]],
            "pos_arg": None,
            "flag": None,
            "tag": "--tag",
            "tag_args": None,
            "append": None,
            "quiet": True,
        })
        meta_launcher.meta_launch(args)
        jobs = load_jobfile(args.jobfile.format(jobname=args.jobname)) # pylint: disable=no-member
        self.assertEqual(len(jobs[0]), 2)
        self.assertEqual("echo --test hi --tag testecho_1__test_hi", jobs[0][1])
        self.assertEqual("echo --test bye --tag testecho_2__test_bye", jobs[0][2])

    def test_single_value_arg(self):
        args = Namespace(**{
            "command": "echo",
            "jobname": "testecho" ,
            "jobfile": defaultjobfile,
            "arg": [["--test", "hi"]],
            "pos_arg": None,
            "flag": None,
            "tag": "--tag",
            "tag_args": None,
            "append": None,
            "quiet": True,
        })
        meta_launcher.meta_launch(args)
        jobs = load_jobfile(args.jobfile.format(jobname=args.jobname)) # pylint: disable=no-member
        self.assertEqual("echo --test hi --tag testecho_1__test_hi", jobs[0][1])

if __name__ == '__main__':
    unittest.main()
