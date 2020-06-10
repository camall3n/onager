from . import local, gridengine, slurm

def prepare_backend(args):
    if args.backend == 'local':
        backend = local.LocalBackend()
    elif args.backend == 'gridengine':
        backend = gridengine.GridEngineBackend()
    elif args.backend == 'slurm':
        backend = slurm.SlurmBackend()
    else:
        raise NotImplementedError('Invalid backend')
    return backend