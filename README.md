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
python3 <project root>/metazoo/main.py --remote <repeats>
```
Here, `--remote` tells MetaZoo we want to execute on the remote cluster.
MetaZoo will not re-export files, and neither will it re-compile Zookeeper.
You will be asked a few important questions, and then the cluster will be deployed.

___

Use:
```bash
python3 <project root>/metazoo/main.py -h
```
to see all options.


## Project
Project description and status can be found [here](PROJECT.md)