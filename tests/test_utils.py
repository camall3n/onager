from onager import meta_launcher
from onager import frontend 
from onager.utils import load_jobfile

def run_meta_launcher(cmd):
    args, _ = frontend.parse_args(cmd.split(' ')) 
    meta_launcher.meta_launch(args)
    return load_jobfile(args.jobfile.format(jobname=args.jobname))
