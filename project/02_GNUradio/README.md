# DVB-T Signal Detector using RTL-SDR and GNUradio

This application can be used to detect DVB-T signal for cognitive radio application. Built with Python and GNUradio companion.

## How to use
	
```
Usage:
	python signal_detector_main.py [options]

[options]
	-h : help  
    -o <file_name> : read known frequency from file  
    -l <min_freq> : minimum frequency (Hz)  
	-u <max_freq> : maximum frequency (Hz)  
	-s <freq_step> : frequency_step   
	-i <interval> : interval or waiting time (s)  
	-t <threshold> : threshold value (dB)  
	-p <auto_threshold_diff> : percentage of threshold stdev
	-b <bandwidth> : specify DVB-T bandwidth (Hz)
```
             
## Results

You can see the results in `result` folder. You can change the output folder inside the main source, i.e. `signal_detector_main.py`     