import unittest

from tests.test_utils import run_meta_launcher

class TestPrelaunchMisc(unittest.TestCase):
    def test_custom_jobfile(self):
        cmd = "prelaunch +command echo +jobname testecho +jobfile .onager/scripts/custom/customjobs.json +arg --test hi +arg --test2 hi2 +q +tag"  
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
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi +arg --test2 hi2 +q"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[1]), 1)
        self.assertEqual("", jobs[1][1])

    def test_default_tagging(self):
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi +arg --test2 hi2 +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[1]), 1)
        self.assertEqual("echo --test hi --test2 hi2 --tag testecho_1__test_hi__test2_hi2",
                jobs[0][1])
        self.assertEqual("testecho_1__test_hi__test2_hi2", jobs[1][1])

    def test_custom_tagging(self):
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi +arg --test2 hi2 +q +tag --custom_tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual("echo --test hi --test2 hi2 --custom_tag testecho_1__test_hi__test2_hi2",
                jobs[0][1])
        self.assertEqual("testecho_1__test_hi__test2_hi2", jobs[1][1])

    def test_tagging_positional(self):
        cmd = "prelaunch +command echo +jobname testecho +pos-arg hi +pos-arg hi2 +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual("echo hi hi2 --tag testecho_1__hi__hi2", jobs[0][1])
        self.assertEqual("testecho_1__hi__hi2", jobs[1][1])

    def test_tagging_flag(self):
        cmd = "prelaunch +command echo +jobname testecho +flag --hi +flag --hi2 +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 4)
        self.assertEqual("echo --hi --hi2 --tag testecho_1__+hi__+hi2", jobs[0][1])
        self.assertEqual("testecho_1__+hi__+hi2", jobs[1][1])
        self.assertEqual("echo --hi2 --tag testecho_2__-hi__+hi2", jobs[0][2])
        self.assertEqual("testecho_2__-hi__+hi2", jobs[1][2])
        self.assertEqual("echo --hi --tag testecho_3__+hi__-hi2", jobs[0][3])
        self.assertEqual("testecho_3__+hi__-hi2", jobs[1][3])
        self.assertEqual("echo --tag testecho_4__-hi__-hi2", jobs[0][4])
        self.assertEqual("testecho_4__-hi__-hi2", jobs[1][4])

    def test_tagging_combined(self):
        cmd = "prelaunch +command echo +jobname testecho +arg --test hi +pos-arg hi2 +flag --help +q +tag"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 2)
        self.assertEqual("echo hi2 --test hi --help --tag testecho_1__hi2__test_hi__+help",
                jobs[0][1])
        self.assertEqual("testecho_1__hi2__test_hi__+help", jobs[1][1])
        self.assertEqual("echo hi2 --test hi --tag testecho_2__hi2__test_hi__-help",
                jobs[0][2])
        self.assertEqual("testecho_2__hi2__test_hi__-help", jobs[1][2])

class TestPrelaunchFlagArgs(unittest.TestCase):

    def test_multiple_flag_args(self):
        cmd = "prelaunch +command echo +jobname testecho +flag --hi +flag --hi2 +q"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 4)
        self.assertEqual("echo --hi --hi2", jobs[0][1])
        self.assertEqual("echo --hi2", jobs[0][2])
        self.assertEqual("echo --hi", jobs[0][3])
        self.assertEqual("echo", jobs[0][4])

    def test_single_flag_arg(self):
        cmd = "prelaunch +command echo +jobname testecho +flag --hi +q"  
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 2)
        self.assertEqual("echo --hi", jobs[0][1])
        self.assertEqual("echo", jobs[0][2])

class TestPrelaunchPositionalArgs(unittest.TestCase):

    def test_single_positional(self):
        cmd = "prelaunch +command echo +jobname testecho +q +pos-arg 0"
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual("echo 0", jobs[0][1])

    def test_single_positional_multi_value(self):
        cmd = "prelaunch +command echo +jobname testecho +q +pos-arg 0 1 2"
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 3)
        self.assertEqual("echo 0", jobs[0][1])
        self.assertEqual("echo 1", jobs[0][2])
        self.assertEqual("echo 2", jobs[0][3])

    def test_single_multiple_positional_single_value(self):
        cmd = "prelaunch +command echo +jobname testecho +q +pos-arg 0"
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 1)
        self.assertEqual("echo 0", jobs[0][1])

    def test_single_multiple_positional_multi_value(self):
        cmd = "prelaunch +command echo +jobname testecho +q +pos-arg 0 1 2 +pos-arg 3 4"
        jobs = run_meta_launcher(cmd)
        self.assertEqual(len(jobs[0]), 6)
        self.assertEqual("echo 0 3", jobs[0][1])
        self.assertEqual("echo 1 3", jobs[0][2])
        self.assertEqual("echo 2 3", jobs[0][3])
        self.assertEqual("echo 0 4", jobs[0][4])
        self.assertEqual("echo 1 4", jobs[0][5])
        self.assertEqual("echo 2 4", jobs[0][6])

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
