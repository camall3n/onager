# onager
Lightweight python library for launching experiments and tuning hyperparameters, either locally or on a cluster.

By Cameron Allen & Neev Parikh

-----

## Installation

Currently requires Python 3.7+

```
pip install onager
```

-----

## Developer Documentation

- [System Overview](docs/system-overview.md)
  - [Multiworker design doc](docs/multiworker.md)

-----

## Usage

### Prelaunch
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

Argument types:
```
+arg --argname [value ...]
```
- Add an argument with zero or more mutually exclusive values

```
+pos-arg value [value ...]
```

- Add a positional argument with one or more mutually exclusive values

```
+flag --flagname
```

- Add a boolean argument that will be toggled in the resulting commands


Options:
```
+tag [TAG]
```

- Passes a unique tag string for each run to the specified arg in the command, i.e. `--tag <tag-contents>`.

```
+tag-args --argname [--argname ...]
```

- Specifies which args go into the unique `<tag-contents>`. Default is all provided args.

```
+no-tag-number
```

- Disable auto-numbering when generating tags


### Launch
Launch reads a jobfile (or accepts a single user-specified command), and launches the associated job(s) on the specified backend. Currently onager supports 'slurm' and 'gridengine' as cluster backends, and 'local' for running on a single host.

```
onager launch --backend slurm --jobname experiment1
```

Output:
```
sbatch -J experiment1 -t 0-01:00:00 -n 1 -p batch --mem=2G -o .onager/logs/slurm/%x_%A_%a.o -e .onager/logs/slurm/%x_%A_%a.e --parsable --array=1,2,3,4,5,6,7,8,9 .onager/scripts/experiment1/wrapper.sh
```

Options:
```
--max-tasks MAX_TASKS
```

- Maximum number of simultaneous tasks on backend. This argument can be used to limit the number of jobs to avoid flooding the cluster or to override the default parallelism of the local backend. When `--tasks-per-node` is greater than 1, `--max-tasks` governs the number of nodes, and `--max-tasks-per-node` governs the number of tasks per node.

```
--tasks-per-node TASKS_PER_NODE
```

- Enables running multiple tasks in parallel on the backend by spawning another "local" backend on each node.

```
--max-tasks-per-node MAX_TASKS_PER_NODE
```

- Maximum number of simultaneous tasks to process with each node.

### Config
By default, onager will simply launch commands for you. If you need to do additional initialization or cleanup, you can configure it using the `config` subcommand and writing to the `header` or `footer` fields of the appropriate backend.

```
onager config --write slurm header "module load python/3.7.4
module load cuda/10.2
module load cudnn/7.6.5
source ./venv/bin/activate"
```

### List
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

### Cancel
Quickly cancel the specified jobs (and subtasks) on the backend

```
onager cancel --backend slurm --jobid 13438569 --tasklist 1-3:1,5,8-9
```

Output:
```
scancel 13438569_1 13438569_2 13438569_3 13438569_5 13438569_8 13438569_9
```

### Re-launch
Launch also supports re-running selected subtasks from a previously launched job

```
onager launch --backend slurm --jobname experiment1 --tasklist 1-3:1,5,8-9
```

Output:
```
sbatch -J experiment1 -t 0-01:00:00 -n 1 -p batch --mem=2G -o .onager/logs/slurm/%x_%A_%a.o -e .onager/logs/slurm/%x_%A_%a.e --parsable --array=1-3:1,5,8-9 .onager/scripts/experiment1/wrapper.sh
```

### Help
For a list of the available subcommands and their respective arguments, use the `help` subcommand:

```
onager help
onager help launch
```

-----

## Example: MNIST
Let's consider a toy MNIST example to concretely see how this would be used in a more realistic setting.

### Setup
If you have the repository cloned, install the `examples/mnist/requirements.txt` in some virtualenv.
You now have a pretty standard setup for an existing project. To use onager, all you have to do is
`pip install onager`.

```
cd examples/mnist
source venv/bin/activate
pip install onager
```

### Prelaunch
Say we need to tune the hyperparameters on our very important MNIST example. We say we want to tune
the learning rate between these values `0.3, 1.0, 3.0` and the batch-size between `32, 64`. We need
to run this for at least 3 seeds each, giving us a total of 18 runs in this experiment. We can use
the prelaunch to generate these commands using the following command:

```
onager prelaunch +command "python mnist.py --epochs 1 --gamma 0.7 --no-cuda" +jobname mnist_lr_bs +arg --lr 0.3 1.0 3.0 +arg --batch-size 32 64 +arg --seed {0..2} +tag --run-tag
```

Output:
```
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 0.3 --batch-size 32 --seed 0 --run-tag mnist_lr_bs_01__lr_0.3__batchsize_32__seed_0
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 1.0 --batch-size 32 --seed 0 --run-tag mnist_lr_bs_02__lr_1.0__batchsize_32__seed_0
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 3.0 --batch-size 32 --seed 0 --run-tag mnist_lr_bs_03__lr_3.0__batchsize_32__seed_0
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 0.3 --batch-size 64 --seed 0 --run-tag mnist_lr_bs_04__lr_0.3__batchsize_64__seed_0
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 1.0 --batch-size 64 --seed 0 --run-tag mnist_lr_bs_05__lr_1.0__batchsize_64__seed_0
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 3.0 --batch-size 64 --seed 0 --run-tag mnist_lr_bs_06__lr_3.0__batchsize_64__seed_0
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 0.3 --batch-size 32 --seed 1 --run-tag mnist_lr_bs_07__lr_0.3__batchsize_32__seed_1
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 1.0 --batch-size 32 --seed 1 --run-tag mnist_lr_bs_08__lr_1.0__batchsize_32__seed_1
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 3.0 --batch-size 32 --seed 1 --run-tag mnist_lr_bs_09__lr_3.0__batchsize_32__seed_1
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 0.3 --batch-size 64 --seed 1 --run-tag mnist_lr_bs_10__lr_0.3__batchsize_64__seed_1
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 1.0 --batch-size 64 --seed 1 --run-tag mnist_lr_bs_11__lr_1.0__batchsize_64__seed_1
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 3.0 --batch-size 64 --seed 1 --run-tag mnist_lr_bs_12__lr_3.0__batchsize_64__seed_1
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 0.3 --batch-size 32 --seed 2 --run-tag mnist_lr_bs_13__lr_0.3__batchsize_32__seed_2
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 1.0 --batch-size 32 --seed 2 --run-tag mnist_lr_bs_14__lr_1.0__batchsize_32__seed_2
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 3.0 --batch-size 32 --seed 2 --run-tag mnist_lr_bs_15__lr_3.0__batchsize_32__seed_2
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 0.3 --batch-size 64 --seed 2 --run-tag mnist_lr_bs_16__lr_0.3__batchsize_64__seed_2
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 1.0 --batch-size 64 --seed 2 --run-tag mnist_lr_bs_17__lr_1.0__batchsize_64__seed_2
python mnist.py --epochs 1 --gamma 0.7 --no-cuda --lr 3.0 --batch-size 64 --seed 2 --run-tag mnist_lr_bs_18__lr_3.0__batchsize_64__seed_2
```

Note that the `--run-tag` is a simple identifier the program accepts that uniquely tags each
run of the script. This could to be used to create a unique directory to store loss/reward etc.

Now this command will generate a `jobs.json` in the default location for the *jobfile*. It is
located here: `.onager/scripts/mnist_lr_bs/jobs.json`. You can customize this by specifying a custom
`+jobfile` argument. See `onager help prelaunch` for more details.

### Launch

Say we want to run this on a Slurm backend somewhere. We need to run prelaunch as described above
and then you simply specify what kind of hardware you need. More details can be found via
`onager help launch`. For this example, we used:

```
onager launch --backend slurm --jobname mnist_lr_bs --cpus 2 --mem 5 --venv ./venv/ --duration 00:30:00 -max 5
```

We specified the same jobname as we did during prelaunch. This lets onager find the right jobfile
automatically. If you'd like, you can provide a custom jobfile too.

And that's it! We now can check `.onager/logs/slurm/` for our logs. To keep track of which jobs are
scheduled, we can use `onager list`. Say you want to cancel some jobs; an easy way to cancel is via
`onager cancel`

-----

## Example: Managing GridEngine 'Eqw' errors
Sometimes GridEngine inexplicably fails to launch certain jobs, causing them to permanently remain in 'Eqw' state. The only known fix for this is to re-run the jobs, but that requires manually parsing the `qstat` output and resubmitting only the affected jobs.

We can use onager to automatically handle this problem for us.

```
cd ..
onager prelaunch +command ./myscript +pos-arg {0001..1000} +tag +jobname test-eqw
onager launch --backend gridengine --duration 00:02:00 --jobname test-eqw --venv mnist/venv/
```

Suppose `qstat` gives the following output:
```
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID
-----------------------------------------------------------------------------------------------------------------
[...]
2323537 0.50500 test-eqw   csal         r     06/12/2020 00:31:27 short.q@mblade1309.cs.brown.ed     1 327
2323537 0.50500 test-eqw   csal         r     06/12/2020 00:31:27 short.q@mblade1309.cs.brown.ed     1 328
2323537 0.50500 test-eqw   csal         r     06/12/2020 00:31:27 short.q@mblade1309.cs.brown.ed     1 329
2323537 0.50500 test-eqw   csal         r     06/12/2020 00:31:34 short.q@dblade41.cs.brown.edu      1 330
2323537 0.50500 test-eqw   csal         Eqw   06/12/2020 00:31:09                                    1 35-40:1,57,138-201:1
```

We can cancel the 'Eqw' jobs and re-launch them with:
```
onager cancel --backend gridengine --jobid 2323537 --tasklist 35-40:1,57,138-201:1
onager launch --backend gridengine --duration 00:02:00 --jobname test-eqw --venv mnist/venv/ --tasklist 35-40:1,57,138-201:1
```

If there are multiple ranges (as in this example), onager will automatically handle splitting those ranges up into separate `qdel` and `qsub` commands.

-----

## Example: Launching Jobs Locally
Sometimes a cluster is overkill, and you just want to launch jobs locally. Onager supports this as well.

```
onager prelaunch +jobname experiment1 +command ./myscript +pos-arg {1..10} +tag
onager launch --backend local --jobname experiment1 --maxtasks 4
```
