#!/usr/bin/env python
##################################################
# Main Function - Gnuradio Python Flow Graph
# Title: DVB-T Signal Detector using RTL-SDR
# Author: Andri Rahmadhani
# Description: Detect DVB-T signal for cognitive radio application
# Generated: Thu Apr 21 13:52:Main Function - 41 2016
##################################################

from gnuradio.eng_option import eng_option
from signal_detector import signal_detector
from datetime import datetime
import os, sys, getopt, time, wx, thread
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# Global variable
freq_min = 478000000
freq_max = 862000000
freq_step = 1e6
freq_scan_interval = 5
threshold = 99999
threshold_noise = 0.7
read_database_file = ""
result_dir = "result/"
default_database = "dvbt_freq_delft.txt"
bandwidth = 8000000
auto_recog = 0
use_list = 0
compare_bw = 0

# Timestamp for file name
f_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

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

    # Identify Signal
    fNameDetection,fNameNoDetection = identify_signal_bw(f_write_scan)

    # Analyze ROC
    analyze_ROC(fNameDetection,fNameNoDetection)

    # Exit the program
    sys.exit(0)

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

# Identify signal from bandwidth
def identify_signal_bw(input_file):
    global bandwidth, f_timestamp, freq_min, \
        freq_max, auto_recog, compare_bw

    freq = []
    level = []
    detection = []
    threshold = 0

    with open(input_file, 'r') as fin:
        for l in fin:
            s = l.strip().split("\t")
            if s[0][0].isdigit():
                freq.append(s[0])
                level.append(s[1])
                threshold = s[2]
                detection.append(s[3])

    # Plot signal level
    fNamePlt = result_dir + "dvbt_freq_results_" + f_timestamp
    plt.clf()
    plt.plot(freq, level)
    plt.xlabel('frequency (Hz)')
    plt.ylabel('level (dB)')
    plt.title('Frequency spectrum of detector')
    plt.grid(True)
    plt.axhline(y=threshold,color='r')
    plt.savefig(fNamePlt + ".png")
    plt.savefig(fNamePlt + ".pdf")
    plt.close()

    # Plot signal detection
    fNamePlt = result_dir + "dvbt_detect_results_" + f_timestamp
    plt.plot(freq, detection)
    plt.xlabel('frequency (Hz)')
    plt.ylabel('detection')
    plt.ylim(ymax=1.5)
    plt.title('Detection of detector in the given range')
    plt.grid(True)
    plt.savefig(fNamePlt + ".png")
    plt.savefig(fNamePlt + ".pdf")
    plt.close()

    detection_res = []
    detection_res_center = []
    detection_no_res = []
    level_res = []
    level_res_center = []
    level_no_res = []

    if auto_recog:
        # Compare with bandwidth
        step_size = int(round(bandwidth/(float(freq[1]) - float(freq[0]))))

        start_counting = 0
        dTemp = []
        for j in range(0,len(detection)-1):
            if start_counting:
                dTemp.append(j)
            else:
                detection_no_res.append(freq[j])
                level_no_res.append(level[j])

            # Rising edge
            if detection[j+1] > detection[j]:
                if start_counting != 1:
                    start_counting = 1     
            # Falling edge       
            elif detection[j+1] < detection[j]:
                if start_counting != 0:
                    start_counting = 0
                    # If compare bandwidth is on
                    if compare_bw:
                        if(len(dTemp) >= step_size - 1 and len(dTemp) <= step_size + 1):
                            detection_res_center.append(freq[int(np.median(dTemp))])
                            level_res_center.append(level[int(np.median(dTemp))])
                            for idx in dTemp:
                                detection_res.append(freq[idx])
                                level_res.append(level[idx])
                        else:
                            for idx in dTemp:
                                detection_no_res.append(freq[idx])
                                level_no_res.append(level[idx])
                    else:
                        detection_res.append(freq[int(np.median(dTemp))])
                        level_res.append(level[int(np.median(dTemp))])
                    dTemp = []
    else:
        for i in range(0,len(detection)):
            if float(detection[i]) >= 1:
                detection_res.append(freq[i])
                level_res.append(level[i])
            else:
                detection_no_res.append(freq[i])
                level_no_res.append(level[i])

    # Save to file
    s = "Detection Results (Hz):"
    fNameDetection = result_dir + "dvbt_final_results_" + f_timestamp + ".txt" 
    f = open(fNameDetection,'w')
    print "\n"+s
    f.write(s+"\n")
    for i in range(0,len(detection_res)):
        print "%s" % (detection_res[i])
        f.write(detection_res[i]+"\t"+level_res[i]+"\t"+threshold+"\n")
    f.close()

    sNo = "No Detection Results (Hz):"
    fNameNoDetection = result_dir + "dvbt_final_no_results_" + f_timestamp + ".txt"
    fNo = open(fNameNoDetection,'w')
    fNo.write(sNo+"\n")
    for i in range(0,len(detection_no_res)):
        fNo.write(detection_no_res[i]+"\t"+level_no_res[i]+"\t"+threshold+"\n")
    fNo.close()

    # Plot detected center frequency
    fNamePlt = result_dir + "dvbt_center_results_" + f_timestamp
    plt.plot(detection_res,[1]*len(detection_res),'ro',linewidth=2.0)
    for i in detection_res:
        plt.axvline(x=i)
    plt.xlabel('frequency (Hz)')
    plt.ylabel('detection')
    plt.ylim(ymax=1.05)
    plt.title('Center frequency of detected signal in the given range')
    plt.grid(True)
    plt.savefig(fNamePlt + ".png")
    plt.savefig(fNamePlt + ".pdf")
    plt.close()

    # return fileName results
    return (fNameDetection,fNameNoDetection)

# Analyze ROC
def analyze_ROC(input_file_result,input_file_no_detection):
    global threshold, use_list, default_database

    freq_true_list = []

    if use_list:
        # Read from list
        with open(default_database,'r') as f:
            for l in f:
                s = l.strip()
                if s[0].isdigit():
                    freq_true_list.append(float(s))

    # Read results
    level = []
    with open(input_file_result,'r') as f:
        for l in f:
            s = l.strip().split("\t")
            if s[0][0].isdigit():
                level.append(float(s[1]))
                threshold = float(s[2])

    # Read no detection results
    level_no = []
    with open(input_file_no_detection,'r') as f:
        for l in f:
            s = l.strip().split("\t")
            if s[0][0].isdigit():
                if use_list:
                    if float(s[0]) not in freq_true_list:
                        level_no.append(float(s[1]))
                    else:
                        # Add to level detection though is not detected
                        level.append(float(s[1]))
                else:
                    level_no.append(float(s[1]))

    level_mean = np.mean(level)
    level_std = np.std(level)
    level_no_mean = np.mean(level_no)
    level_no_std = np.std(level_no)

    # Probability of detected signal
    N = 10000
    Ptarget = np.random.normal(level_mean,level_std,N)
    # Probability of empty channel
    Pnotarget = np.random.normal(level_no_mean,level_no_std,N)

    Ptarget_sorted = np.sort(Ptarget)
    pt = stats.norm.cdf(Ptarget_sorted,np.mean(Ptarget_sorted),np.std(Ptarget_sorted))
    Pnotarget_sorted = np.sort(Pnotarget)
    pnt = stats.norm.cdf(Pnotarget_sorted,np.mean(Pnotarget_sorted),np.std(Pnotarget_sorted))
    Pd = 1 - pt[getnearpos(Ptarget_sorted,threshold)]   # Prob. of detection
    Pfa = 1 - pt[getnearpos(Pnotarget_sorted,threshold)]     # Prob. of false alarm
    print "Pd = %f" % (Pd)
    print "Pfa = %f" % (Pfa)
    
    # Save probability results to file
    fNameProb = result_dir + "dvbt_prob_results_" + f_timestamp + ".txt"
    f = open(fNameProb,'w')
    f.write("Probability of Detection = " + str(Pd) + "\n")
    f.write("Mean = " + str(level_mean) + "\n")
    f.write("Stdev = " + str(level_std) + "\n")
    f.write("Probability of False Alarm = " + str(Pfa) + "\n")
    f.write("Mean = " + str(level_no_mean) + "\n")
    f.write("Stdev = " + str(level_no_std) + "\n")
    f.close()

    # Create Ptarget pdf
    fNamePlt = result_dir + 'dvbt_pdf_results_' + f_timestamp
    PtargetPdf = stats.norm.pdf(Ptarget_sorted,np.mean(Ptarget_sorted),np.std(Ptarget_sorted))
    plt.plot(Ptarget_sorted,PtargetPdf,label='target present')
    PnotargetPdf = stats.norm.pdf(Pnotarget_sorted,np.mean(Pnotarget_sorted),np.std(Pnotarget_sorted))
    plt.plot(Pnotarget_sorted,PnotargetPdf,hold=1,label='no target present')
    plt.axvline(x=threshold,color='k',linestyle='dashed',hold=1,label='threshold')
    plt.xlabel('level (dB)')
    plt.title('RTL-SDR detection probability')
    plt.legend(loc='upper right')
    plt.savefig(fNamePlt + ".png")
    plt.savefig(fNamePlt + ".pdf")
    plt.close()
    
    # Create ROC plot and save to file
    level_all = np.arange(Ptarget_sorted[0],Ptarget_sorted[len(Ptarget_sorted)-1])
    pt_ROC = []
    pnt_ROC = []
    for i in level_all:
        pt_ROC.append(pt[getnearpos(Ptarget_sorted,i)])
        pnt_ROC.append(pnt[getnearpos(Pnotarget_sorted,i)])
    pt_ROC = np.array(pt_ROC)
    pnt_ROC = np.array(pnt_ROC)

    fNamePlt = result_dir + 'dvbt_roc_results_' + f_timestamp
    plt.plot(1-pnt_ROC,1-pt_ROC)
    plt.xlabel('Probability of False Alarm')
    plt.ylabel('Probability of Detection')
    plt.title('RTL-SDR ROC curves')
    plt.savefig(fNamePlt + ".png")
    plt.savefig(fNamePlt + ".pdf")
    plt.close()

# Find nearest value for ROC analysis
def getnearpos(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx

def main(argv):
    import ctypes
    import os

    global freq_min, freq_max, \
       freq_step,freq_scan_interval, \
       threshold,threshold_noise, \
       result_dir, use_list, bandwidth, \
       auto_recog, read_database_file, \
       compare_bw

    help_string = \
        "DVB-T Signal Detector by A. Rahmadhani\n" + \
        "--------------------------------------\n\n" + \
        "Usage: signal_detector_main.py [options]\n\n" + \
        "[options]:\n" + \
        "  -h : help\n" + \
        "  -r : try to recognize signal automatically\n" + \
        "  -q : use known DVB-T frequency list\n" + \
        "  -c : compare bandwidth to identify signal\n" + \
        "  -o <file_name> : read known frequency from file\n" + \
        "  -l <min_freq> : minimum frequency (Hz)\n" + \
        "  -u <max_freq> : maximum frequency (Hz)\n" + \
        "  -s <freq_step> : frequency_step \n" + \
        "  -i <interval> : interval or waiting time (s)\n" + \
        "  -t <threshold> : threshold value (dB)\n" + \
        "  -p <auto_threshold_diff> : percentage of threshold stdev\n" + \
        "  -b <bandwidth> : specify DVB-T bandwidth (Hz)h\n"

    # Read command line arguments
    try:
        opts, args = getopt.getopt(argv,"hrqcl:u:s:i:t:p:o:b:",
            ["help","auto","lfreq=","ufreq=","step=","interval=", 
            "threshold=","threshold_diff=","open_data=",
            "bandwidth=","compare"])

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
        elif opt in ("-c", "--compare"):
            compare_bw = 1 

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