from onager import meta_launcher
from onager import frontend
from onager.utils import load_jobfile, get_jobfile_path

def run_meta_launcher(cmd):
    args, _ = frontend.parse_args(cmd.split(' '))
    meta_launcher.meta_launch(args)
    return load_jobfile(get_jobfile_path(jobname=args.jobname))
