# process-manager <!-- omit in toc -->
A modular Python package for launching, monitoring, and logging multiple processes in a centralized Text-based User Interface (TUI) built with [**textual**](https://textual.textualize.io/). 

![Process Manager View](assets\process_manager.png "Process Manager")

## Table of Contents <!-- omit in toc -->
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
  - [config.yaml](#configyaml)
  - [Heartbeat](#heartbeat)
  - [Log](#log)
  - [Start Program](#start-program)

## Introduction
`process-manager` automatically launches the processes (nodes) defined in the `config.yaml` file automatically and countinuously monitors their status and logs. The status of a node is determined by whether a *Heartbeat* is detected from that node. All logging and *Heartbeat* communications are sent through [**Cyclone DDS**](https://cyclonedds.io/), a data sharing technology, which is set up by `igmr-robotics-toolkit`. This allows communication across diferent programs and devices with proper setup. The interactive UI is built with `textual` to visualize the data.

## Installation
To install the package, first clone the repository from GitHub
```bash
git clone git@github.com:Yihan-Ling/process-manager.git
cd process-manager
pip install -e .
```
This installs the package as `process_manager`

## Usage
Assume your directory structure looks like this: 
```
root_directory/
├── process-manager
├── programs/
│   ├── __init__.py
│   ├── program_1.py
│   └── program_2.py
├── __init__.py
└── program_3.py
```
> note as of version 0.1.0, the program only supports running processes as python modules, not stand-alone files

### config.yaml
To identify which nodes should be started and kept track of by the process manager, edit the `process-manager/src/process_manager/config.yaml`:

```yaml
processes:
# <full.module.path>: <Display Name>
  test_programs.dummy_processes.d_one: Process One
  test_programs.dummy_processes.d_two: Process Two
  test_programs.dummy_processes.d_three: Process Three
```
Edit the yaml file to include all module you want to run as the first part of the enrty, and give it a readable name (should be distinct across all nodes) to be displayed in the UI. 

For example, to include program_1-3 in the example structure:
```yaml
processes:
  programs.program_1: Program 1
  programs.program_2: Program 2
  program_3: Program 3
```
### Heartbeat
Next, in each process, add a piece of code to report a *heartbeat* periodically, that is, in a loop that the program runs continuously (see `dummy_processes` for examples). 

```python
import igmr_robotics_toolkit.comms.auto_init    # Has to import before CycloneDDS
from process_manager.util import write_heartbeat, create_writer

state_writer = create_writer(_log) # Creates a Cyclone DDS DataWriter

while True:
    write_heartbeat(writer=state_writer, module=__spec__.name) # Sends a heartbeat through the DataWriter
```
### Log
To log through process manager, use the `logger` provided by `process_manager.log`.

```python
from process_manager.log import logger
from process_manager.util import auto_default_logging 


_log = logger(__file__)
_log.info("process started")
_log.critical("process ended")
```
### Start Program
To start the process manager, first run 
```bash
python -m igmr_robotics_toolkit.comms.params --config process-manager/src/process_manager/config.yaml
```
to start the Cyclone DDS communication.

In a seperate terminal, run
```bash
process_manager
```
to start the process manager
