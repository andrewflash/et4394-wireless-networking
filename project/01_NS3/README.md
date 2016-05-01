# Performance analysis of IEEE 802.11b using NS-3 simulator

This application can be used to simulate WiFi network. The results of simulation can be used to analyze the performance of IEEE 802.11b standard. This application is created and tested under Linux (Ubuntu 14.04) environment with Python and dependencies installed.

## How to use

- Edit parameters (path to NS3, source file, etc) in `run.sh` script file
- Run terminal
- `cd` to this directory
- Run `run.sh` by typing `sh run.sh` in the terminal

## Individual modules

This application consists of several modules that can be run independently. It consists of:

1. Main NS-3 source: `wifi-sim-andri.cc`
2. Shell script: `run.sh`
3. Plotting function in Python:
  - Main plotting modules: `plot.py`
  - Alternative plotting modules (different style): `plot_alt.py`
  - Bar plot: `plot_bar.py`
  - Plot std deviation from simulation results: `plot_var.py`

To run the plotting functions, simple run python followed by the module name:
```
	python plot.py
``` 

## Results

You can see the results in `result` folder.     
