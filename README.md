# MetaZoo

When working with
an ancient version of Zookeeper,  
server instances with 6-year old Java, 4-year old Python and no useful build tools,
there is only one who can save the project: MetaZoo

## Usage
Here, we describe how to use and interact with this project.

### Installation
We require a few things:
 1. Is `JAVA_HOME` set in the `~/.bashrc` of the remote? (DAS5 does not provide this)
 2. Is `JAVA_HOME` pointed such that there is a `JAVA_HOME/bin/java`, `JAVA_HOME/bin/javac`, both version 8?

If you have that setup, proceed to the next stage.
In case you have only just cloned this repository, you will want to use:
```bash
python3 <project root>/metazoo/main.py --init
```
The init flag will do the following things:
 1. Copy this project efficiently to the remote cluster
 2. Install dependencies (no `sudo` needed) on the cluster
 3. Compile the ZooKeeper project on the cluster

You only have to call `--init` once (although calling it multiple times causes no problems).

### Running
After initializattion, we run 
```bash
python3 <project root>/metazoo/main.py --remote <optional repeats>
```
Here, `--remote` tells MetaZoo we want to execute on the remote cluster.
MetaZoo will not re-export files, and neither will it re-compile Zookeeper.
Use the `-e` flag to force-export from your local machine, and the `-c` flag to force-(re)compile on the remote.
You will be asked a few important questions, and then the cluster will be deployed.


#### Running for a long time
When experiments have to run for many hours, you of course do not want to control the remote cluster from your local device, because you would need to leave your local device on for the entire duration of the experiment.
Use:
```bash
ssh <ssh_key for remote>
tmux
python3 </path/to/metazoo/main.py> --exec <repeats>
```
This way, MetaZoo commands from the remote in a tmux instance.
You can safely press `ctrl+B` `D` to exit tmux.
Now you can logout and shutdown your local machine without interrupting your experiment.
___

Use:
```bash
python3 <project root>/metazoo/main.py -h
```
to see all options.


## Project
Project description and status can be found [here](PROJECT.md)