import unittest

from tests.test_utils import run_meta_launcher

class TestPrelaunchMisc(unittest.TestCase):
    def test_custom_jobfile(self):
        cmd = "prelaunch +command echo +jobname testecho \
                +jobfile .onager/scripts/custom/customjobs.json \
                +arg --test hi +arg --test2 hi2 +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual("echo --test hi --test2 hi2 --tag testecho_1__test_hi__test2_hi2",
                jobs[0][1])

    def test_append_jobfile(self):
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi +arg --test2 hi2 +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual("echo --test hi --test2 hi2 --tag testecho_1__test_hi__test2_hi2",
                jobs[0][1])
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi +arg --test2 hi2 +q +a +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 2)
        self.assertEqual("echo --test hi --test2 hi2 --tag testecho_2__test_hi__test2_hi2",
                jobs[0][2])

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
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi +arg --test2 hi2 +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual("echo --test hi --test2 hi2 --tag testecho_1__test_hi__test2_hi2",
                jobs[0][1])

    def test_multiple_value_args(self):
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi bye +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 2)
        self.assertEqual("echo --test hi --tag testecho_1__test_hi", jobs[0][1])
        self.assertEqual("echo --test bye --tag testecho_2__test_bye", jobs[0][2])

    def test_single_value_arg(self):
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual("echo --test hi --tag testecho_1__test_hi", jobs[0][1])

if __name__ == '__main__':
    unittest.main()
