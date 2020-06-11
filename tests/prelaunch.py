import unittest
from argparse import Namespace

from onager import meta_launcher
from onager.utils import load_jobfile
from onager.constants import defaultjobfile


class TestPrelaunchOptionalArg(unittest.TestCase):

    def setUp(self):
        pass

    def test_single_value_arg(self):
        args = Namespace(**{
            "command": "echo",
            "jobname": "echoy",
            "jobfile": defaultjobfile,
            "arg": [["--test", "hi"]],
            "pos_arg": None,
            "flag": None,
            "tag": "tag",
            "tag_args": None,
            "append": None,
            "quiet": None,
        })
        meta_launcher.meta_launch(args)
        jobs = load_jobfile(args.jobfile.format(jobname=args.jobname))
        self.assertIn("hi", jobs[0][1])

if __name__ == '__main__':
    unittest.main()
