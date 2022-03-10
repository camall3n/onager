# Multiworker - design doc

An upgrade for the `launch` subcommand that allows submitting jobs to a cluster in such a way that multiple jobs can run on the same node.

## Purpose

- It allows a single GPU reservation to be used for two jobs at the same time.
- It allows for pipelining of many short-duration jobs without requiring additional reservations, which take time
- It allows for I/O-constrained jobs to be run in parallel on much less hardware

## Description

Introduces two new arguments: `--tasks-per-node` and `--max-tasks-per-node`.

The default value, `--tasks-per-node=1`, behaves the same way as before. But when `--tasks-per-node > 1`, it switches into "multiworker" mode. Each node that gets scheduled on the backend (slurm/gridengine) will subsequently run the local backend with the desired number of subjobs.

The `--max-tasks-per-node` has a default value of `-1`, which will automatically compute the number of cores on the system, and give you that many workers for processing your subjobs. You can override it to less than that, for example if you wanted 4 jobs to run with 2 cpus each on a node with 4 cpus. You can also override it to more, for example if you knew the jobs would mostly be sleeping or waiting on I/O or something.

## Implementation

When activated, the `launch` subcommand switches into the "multi" mode. Now, instead of producing a `wrapper.sh` file (which wraps `onager.worker`), onager produces a `multiwrapper.sh` file (which wraps `onager.multiworker`) as well as a `subjobs.csv` file that specifies which nodes should execute which jobs.

The differentiation of `.sh` scripts allows both modes to be used simultaneously without conflicting: if a job is launched in "multi" mode, it will continue to execute `multiwrapper.sh`, even if another job is simultaneously launched in "single" mode (e.g. with a different tasklist).

Both modes still use `jobs.json` to track which jobs are associated with which IDs, but the "multi" mode must perform an additional translation step. The multiworker reads the `subjobs.csv` file and converts from what we call the `--subjob-group-id` to a tasklist that uses the original `jobs.json` ID numbering.

Once the multiworker has recovered the relevant tasklist, it launches them using the local backend. Typically, the local backend stores log files in a directory based on the hostname of the current node. But we don't want that here, because each node will have a different hostname, and therefore the log files will be split among many folders. So we instead provide the multiworker with a `--logging-backend` that matches the original backend name that we selected when we ran `onager launch`. This allows all logs to end up in the same place they normally would.

To keep things organized, we put node logs (i.e. logs from running the local backend) in the logs directory, and we put subjob-specific logs in a subdirectory:

```text
.onager/logs/slurm/
 ├── jobname_SLURMJOBID_TASKID.e
 ├── jobname_SLURMJOBID_TASKID.o
 └── jobname_SLURMJOBID_subjobs/
     ├──TASKID_SUBTASKID.e
     └──TASKID_SUBTASKID.o
```
