# process-manager <!-- omit in toc -->
A modular Python package for launching, monitoring, and logging seperate processes all in one centralized Text-based User Interface (TUI) built with [**textual**](https://textual.textualize.io/). 

## Table of Contents <!-- omit in toc -->
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)

## Introduction
`procecss-manager` launches the processes (nodes) defined in the `config.yaml` file automatically and countinuously monitors their status and logs. The status of a node is determined by whether a *Heart Beat* is detected from that node. All logging and *Heart Beat* communications are sent through [**Cyclone DDS**](https://cyclonedds.io/), a data sharing technology, which is set up by `igmr-robotics-toolkit`. The interactive UI is built with `textual` to visualize the data.

## Installation
To install the package, first clone the repository from GitHub
```bash
git clone git@github.com:Yihan-Ling/process-manager.git
cd process-manager
pip install -e .
```
This should install the package as `process_manager`

## Usage
The file structure in your directory would probably follow something similar to this: 
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




