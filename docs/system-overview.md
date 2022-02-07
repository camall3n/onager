# Onager - System Overview

Onager is designed for conveniently managing and launching multiple related computing jobs.

The core workflow is as follows:

1. Main executable - `bin/onager`

1. Prelaunch - `onager.meta_launcher.meta_launch()`

    - Inputs:
        - jobname
        - command
        - argument lists
        - etc.

    - Outputs:
        - jobfile - `jobs.json`
            - contains a JSON dictionary mapping from jobids to 2-item lists, each containing a command and a (possibly empty) tag identifier.

1. Launch - `onager.launcher.launch()`

   - Inputs:
      - jobname
         - (must have previously been used to generate a prelaunch jobfile, or otherwise a single `--command "..."` must be passed in on the command line.)
      - backend name (slurm, gridengine, local)
      - requested resources (cpus, gpus, memory, duration, etc.)
         - Note that resource requests are always node-specific, so if `onager launch` is called with `--cpus 8` and `--tasks-per-node 4`, each node will have 8 cpus that will be shared between the 4 subjobs on that node.
      - virtual environment (if any)
      - other args (forwarded to backend)

   - Outputs:
      - "Single" mode:
         - Shell script - `wrapper.sh`
            - Wraps `onager.worker` executable with the appropriate environment setup/teardown steps (`--venv`, `onager config`, etc.)
      - "Multi" mode:
         - Shell script - `multiwrapper.sh`
            - Wraps `onager.multiworker` executable with the appropriate environment setup/teardown steps (`--venv`, `onager config`, etc.)
         - Subjobs file - `subjobs.csv`
            - CSV file mapping from subjob_groupids to node-specific tasklists
      - "Local" mode":
         - None, simply spawns a multiprocess pool and calls `worker.run_cmd_by_id()`

1. Worker
    - "Single" mode - `onager.worker`
        - Loads the jobfile specified in `wrapper.sh` and invokes `worker.run_cmd_by_id()` using the jobid specified in the relevant environment variable (backen specific)

    - "Multi" mode - `onager.multiworker`
        - Parses the arguments specified in `multiwrapper.sh` and invokes `multiworker.run_subjobs_with_local_backend()`
        - Reads `subjobs.csv` to determine the appropriate tasklist
        - Uses the computed tasklist to prepare to run jobs from `jobs.json` as subjobs
        - Requests a LocalBackend and invokes `backend.multilaunch()` to run the jobs
