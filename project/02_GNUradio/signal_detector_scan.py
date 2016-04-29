from gnuradio.eng_option import eng_option
from signal_detector import signal_detector
from datetime import datetime
import numpy as np
import os, sys, getopt, time, wx, thread
import matplotlib.pyplot as plt

# Global variable
freq_min = 478000000
freq_max = 862000000
freq_step = 1e6
freq_scan_interval = 5
threshold = 99999
threshold_noise = 0.7
read_database_file = ""

# Timestamp for file name
f_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
result_dir = 'results_' + f_timestamp + '/'

# Automatically scan frequency
# -- interval in second
def scan_freq(tb,start_freq,end_freq,step,interval):
    # Load global variables
    global read_database_file,threshold,threshold_noise,result_dir, \
        nTrueTrue, totalTrueTrue, f_timestamp

    # Noise and threshold info string
    sNoise = ""
    
    # Sweep frequency
    freq = start_freq

    # Output filename
    f_write_scan = result_dir + 'dvbt_scan_results_' + f_timestamp + '.txt'

    # Calculate threshold if not specified in parameters
    if int(threshold) == 99999:
        # Get Noise level for calculating threshold
        noise_level, mean_level, std_level = get_noise_level(tb,start_freq,end_freq,8e6,0.1)
        default_threshold = noise_level + threshold_noise*std_level
        tb.set_threshold(default_threshold)
        sNoise = "Noise level = %f dB\nMean level = %f dB\n" \
            "Stdev level = %f\nPercentage threshold from stdev = %f\n" \
            "Calculated threshold = %d\n" \
            % (noise_level,mean_level,std_level,threshold_noise,default_threshold)
        print "\n" + sNoise
    else:
        tb.set_threshold(threshold)

    # Open frequency list from file
    if read_database_file != "":
        fdata = open(read_database_file,'r')
        f = open(f_write_scan,'w')
        print "Scanning frequency list from file"
        print "Freq\t\tLevel\t\tThreshold\tDetection"        
        if sNoise != "":
            f.write(sNoise)
        f.write("Freq\tLevel\tThreshold\tDetection\n")
        f.flush()
        for val in fdata.readlines():
            tb.set_freq(float(val))
            time.sleep(interval)
            s = "%d\t%f\t%f\t%d" % (tb.get_freq(),tb.get_probe_level(),tb.get_threshold(),tb.get_probe_detection())
            print s
            f.write(s+"\n")
            f.flush()
        fdata.close()
        f.close()
    else:
        # Sweep frequencies
        fout = open(f_write_scan,'w')
        print "Scanning frequency (automatic)"
        print "Freq\t\tLevel\t\tThreshold\tDetection"
        if sNoise != "":
            fout.write(sNoise)
        fout.write("Freq\tLevel\tThreshold\tDetection\n") 
        fout.flush()
        while freq <= end_freq:
            tb.set_freq(freq)
            time.sleep(interval)
            s = "%d\t%f\t%f\t%d" % (tb.get_freq(),tb.get_probe_level(),tb.get_threshold(),tb.get_probe_detection())
            print s
            fout.write(s+"\n")
            fout.flush()
            freq = freq + step
        fout.close()

# Get noise level for calculating default threshold
def get_noise_level(tb,start_freq,end_freq,step,interval):
    level_arr = []
    freq = start_freq
    print "Calculating noise level"
    while freq <= end_freq:
        tb.set_freq(freq)
        time.sleep(interval)
        print "%d\t%d" % (tb.get_freq(),tb.get_probe_level())
        level_arr.append(tb.get_probe_level())
        freq = freq + step
    n, bins, patches = plt.hist(level_arr,bins=len(level_arr),normed=1,stacked=1)
    bin_max = np.argmax(n)
    # return average noise level and all signal mean
    return (bins[bin_max],np.mean(level_arr),np.std(level_arr))

def main(argv):
    import ctypes
    import os

    global freq_min, freq_max, \
       freq_step,freq_scan_interval, \
       threshold,threshold_noise, \
       result_dir, \
       read_database_file

    help_string = \
        "DVB-T Signal Detector - Scanner - by A. Rahmadhani\n" + \
        "--------------------------------------\n\n" + \
        "Usage: signal_detector_main.py [options]\n\n" + \
        "[options]:\n" + \
        "  -h : help\n" + \
        "  -o <file_name> : read known frequency from file\n" + \
        "  -l <min_freq> : minimum frequency (Hz)\n" + \
        "  -u <max_freq> : maximum frequency (Hz)\n" + \
        "  -s <freq_step> : frequency_step \n" + \
        "  -i <interval> : interval or waiting time (s)\n" + \
        "  -t <threshold> : threshold value (dB)\n" + \
        "  -p <auto_threshold_diff> : percentage of threshold stdev\n"

    # Read command line arguments
    try:
        opts, args = getopt.getopt(argv,"hrql:u:s:i:t:p:o:b:",
            ["help","auto","lfreq=","ufreq=","step=","interval=", 
            "threshold=","threshold_diff=","open_data=",
            "bandwidth="])

    except getopt.GetoptError:
        print help_string
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print help_string
            sys.exit()
        elif opt in ("-r", "--auto"):
            auto_recog = 1
        elif opt in ("-q", "--uselist"):
            use_list = 1
        elif opt in ("-l", "--lfreq"):
            freq_min = float(arg)
        elif opt in ("-u", "--hfreq"):
            freq_max = float(arg)
        elif opt in ("-s", "--step"):
            freq_step = float(arg)
        elif opt in ("-i", "--interval"):
            freq_scan_interval = float(arg)
        elif opt in ("-t", "--threshold"):
            threshold = float(arg)
        elif opt in ("-p", "--threshold_diff"):
            threshold_noise = float(arg)
        elif opt in ("-o", "--open_data"):
            read_database_file = str(arg)
        elif opt in ("-b", "--bandwidth"):
            bandwidth = float(arg)
 
    # GUI from GNUradio companion
    if os.name == 'posix':
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

    # Create result dir if not exists
    try:
        os.makedirs(result_dir)
    except OSError:
        pass

    app = signal_detector()
    app.Start(True)
    # Start new thread to scan frequency
    thread.start_new_thread(scan_freq, (app,freq_min,freq_max,freq_step,freq_scan_interval))

    # Wait for GUI thread
    app.Wait()
    # Exit properly when GUI closed
    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])