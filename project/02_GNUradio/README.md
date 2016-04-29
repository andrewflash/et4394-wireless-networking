# DVB-T Signal Detector using RTL-SDR and GNUradio

This application can be used to detect DVB-T signal for cognitive radio application. Built with Python and GNUradio companion.

## How to use

```
Usage:
	python signal_detector_main.py [options]

[options]
	-h : help  
    -r : try to recognize signal automatically
    -q : use known DVB-T frequency list
    -c : compare bandwidth to identify signal
    -o <file_name> : read known frequency from file  
    -l <min_freq> : minimum frequency (Hz)  
	-u <max_freq> : maximum frequency (Hz)  
	-s <freq_step> : frequency_step   
	-i <interval> : interval or waiting time (s)  
	-t <threshold> : threshold value (dB)  
	-p <auto_threshold_diff> : percentage of threshold stdev
	-b <bandwidth> : specify DVB-T bandwidth (Hz)
```

### Example

1. Use automatic frequency scan, find threshold value, and try to recognize DVB-T signal. Compare the result with known list to verify the signal. Use default 8 MHz bandwidth and compare the result. Use default value for other parameters. 

```
	python signal_detector_main.py -r -q -c
```

2. Same as previous example but no need to search threshold value. We specify threshold manually.

```
	python signal_detector_main.py -r -q -c -t -60
```

## Individual module

This application has several modules that can be run independently. It consists of:

1. Frequency scanner: `signal_detector_scan.py`
2. Signal identifier: `signal_detector_identifier.py`
3. ROC analyzer: `signal_detector_roc.py`

For more information about the modules, please refer to the help information by passing `-h` as parameter when running the modules.

## Results

You can see the results in `result` folder. You can change the output folder inside the main source, i.e. `signal_detector_main.py`     