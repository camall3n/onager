# onager
Lightweight python library for launching experiments and tuning hyperparameters, either locally or on a cluster.

By Cameron Allen & Neev Parikh

# Installation

Currently requires Python 3

```
pip install onager
```

# Usage

## Prelaunch
Prelaunch generates commands and adds them to a jobfile. The default behavior also prints the list of generated commands.

```
onager prelaunch +jobname experiment1 +command myscript +arg --learningrate 0.1 0.01 0.001 +arg --batchsize 32 64 128 +tag --mytag
```

Output:
```
myscript --learningrate 0.1 --batchsize 32 --mytag experiment1_1__learningrate_0.1__batchsize_32
myscript --learningrate 0.01 --batchsize 32 --mytag experiment1_2__learningrate_0.01__batchsize_32
myscript --learningrate 0.001 --batchsize 32 --mytag experiment1_3__learningrate_0.001__batchsize_32
myscript --learningrate 0.1 --batchsize 64 --mytag experiment1_4__learningrate_0.1__batchsize_64
myscript --learningrate 0.01 --batchsize 64 --mytag experiment1_5__learningrate_0.01__batchsize_64
myscript --learningrate 0.001 --batchsize 64 --mytag experiment1_6__learningrate_0.001__batchsize_64
myscript --learningrate 0.1 --batchsize 128 --mytag experiment1_7__learningrate_0.1__batchsize_128
myscript --learningrate 0.01 --batchsize 128 --mytag experiment1_8__learningrate_0.01__batchsize_128
myscript --learningrate 0.001 --batchsize 128 --mytag experiment1_9__learningrate_0.001__batchsize_128
```

## Launch
Launch reads a jobfile (or accepts a single user-specified command), and launches the associated job(s) on the specified backend. Currently onager supports 'slurm' and 'gridengine' as cluster backends, and 'local' for running on a single host.

```
onager launch --backend slurm --jobname experiment1
```

Output:
```
sbatch -J experiment1 -t 0-01:00:00 -n 1 -p batch --mem=2G -o .onager/logs/slurm/%x_%A_%a.o -e .onager/logs/slurm/%x_%A_%a.e --parsable --array=1,2,3,4,5,6,7,8,9 .onager/scripts/experiment1/wrapper.sh
```

## Config
By default, onager will simply launch commands for you. If you need to do additional initialization or cleanup, you can configure it using the `config` subcommand and writing to the `header` or `footer` fields of the appropriate backend.

```
onager config --write slurm header "module load python/3.7.4
module load cuda/10.2
module load cudnn/7.6.5
source ./venv/bin/activate"
```

## List
List is useful for displaying information about launched jobs and tasks, since the backend will typically assign the same jobname to all subtasks.

```
onager list
```

Output:
```
  job_id    task_id  jobname      command                                                                                                   tag
--------  ---------  -----------  --------------------------------------------------------------------------------------------------------  ------------------------------------------------
13438569          1  experiment1  'myscript --learningrate 0.1 --batchsize 32 --mytag experiment1_1__learningrate_0.1__batchsize_32'        experiment1_1__learningrate_0.1__batchsize_32
13438569          2  experiment1  'myscript --learningrate 0.01 --batchsize 32 --mytag experiment1_2__learningrate_0.01__batchsize_32'      experiment1_2__learningrate_0.01__batchsize_32
13438569          3  experiment1  'myscript --learningrate 0.001 --batchsize 32 --mytag experiment1_3__learningrate_0.001__batchsize_32'    experiment1_3__learningrate_0.001__batchsize_32
13438569          4  experiment1  'myscript --learningrate 0.1 --batchsize 64 --mytag experiment1_4__learningrate_0.1__batchsize_64'        experiment1_4__learningrate_0.1__batchsize_64
13438569          5  experiment1  'myscript --learningrate 0.01 --batchsize 64 --mytag experiment1_5__learningrate_0.01__batchsize_64'      experiment1_5__learningrate_0.01__batchsize_64
13438569          6  experiment1  'myscript --learningrate 0.001 --batchsize 64 --mytag experiment1_6__learningrate_0.001__batchsize_64'    experiment1_6__learningrate_0.001__batchsize_64
13438569          7  experiment1  'myscript --learningrate 0.1 --batchsize 128 --mytag experiment1_7__learningrate_0.1__batchsize_128'      experiment1_7__learningrate_0.1__batchsize_128
13438569          8  experiment1  'myscript --learningrate 0.01 --batchsize 128 --mytag experiment1_8__learningrate_0.01__batchsize_128'    experiment1_8__learningrate_0.01__batchsize_128
13438569          9  experiment1  'myscript --learningrate 0.001 --batchsize 128 --mytag experiment1_9__learningrate_0.001__batchsize_128'  experiment1_9__learningrate_0.001__batchsize_128
```

## Cancel
Quickly cancel the specified jobs (and subtasks) on the backend

```
onager cancel --backend slurm --jobid 13438569 --tasklist 1-3:1,5,8-9
```

Output:
```
scancel 13438569_1 13438569_2 13438569_3 13438569_5 13438569_8 13438569_9
```

## Re-launch
Launch also supports re-running selected subtasks from a previously launched job

```
onager launch --backend slurm --jobname experiment1 --tasklist 1-3:1,5,8-9
```

Output:
```
sbatch -J experiment1 -t 0-01:00:00 -n 1 -p batch --mem=2G -o .onager/logs/slurm/%x_%A_%a.o -e .onager/logs/slurm/%x_%A_%a.e --parsable --array=1-3:1,5,8-9 .onager/scripts/experiment1/wrapper.sh
```

## Help
For a list of the available subcommands and their respective arguments, use the `help` subcommand:

```
onager help
onager help launch
```
