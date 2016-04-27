from datetime import datetime
import sys, getopt
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
result_dir = ""
bandwidth = 8000000
auto_recog = 0

f_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def main(argv):

    global freq_min, freq_max, \
       freq_step,freq_scan_interval, \
       threshold,threshold_noise, \
       result_dir, use_list, bandwidth, \
       auto_recog

    input_file=""

    help_string = \
        "DVB-T Signal Detector - Identifier - by A. Rahmadhani\n" + \
        "--------------------------------------\n\n" + \
        "Usage: signal_detector_main.py [options]\n\n" + \
        "[options]:\n" + \
        "  -h : help\n" + \
        "  -r : try to recognize signal automatically\n" + \
        "  -q : use known DVB-T frequency list\n" + \
        "  -o <file_name> : input scanner results file\n" + \
        "  -l <min_freq> : minimum frequency (Hz)\n" + \
        "  -u <max_freq> : maximum frequency (Hz)\n" + \
        "  -s <freq_step> : frequency_step \n" + \
        "  -i <interval> : interval or waiting time (s)\n" + \
        "  -t <threshold> : threshold value (dB)\n" + \
        "  -p <auto_threshold_diff> : percentage of threshold stdev\n" + \
        "  -b <bandwidth> : specify DVB-T bandwidth (Hz)h\n"

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
            input_file = str(arg)
        elif opt in ("-b", "--bandwidth"):
            bandwidth = float(arg)

    identify_signal_bw(input_file)

# Identify signal from bandwidth
def identify_signal_bw(input_file):
    global bandwidth, f_timestamp, freq_min, freq_max, auto_recog

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
    plt.plot(freq, level)
    plt.xlabel('frequency (Hz)')
    plt.ylabel('level (dB)')
    plt.title('Frequency spectrum of detector')
    plt.grid(True)
    plt.axhline(y=threshold,color='r')
    plt.savefig(fNamePlt + ".png")
    plt.savefig(fNamePlt + ".svg")
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
    plt.savefig(fNamePlt + ".svg")
    plt.close()

    detection_res = []
    detection_no_res = []
    level_res = []
    level_no_res = []

    if auto_recog:
        # Compare with bandwidth
        step_size = int(round(bandwidth/(float(freq[1]) - float(freq[0]))))

        detection_window = []
        detection_mean = []
        detection_std = []
    
        for j in range(0,len(detection)-step_size):
            for k in range(0,step_size):
                detection_window.append(float(detection[j+k]))
            detection_mean.append(np.mean(detection_window))
            detection_std.append(np.std(detection_window))
            detection_window = []

        i = 0
        start_counting = 0
        dTemp = []
        for j in range(0,len(detection_std)-1):
            # Rising edge
            if detection_std[j] >= 0.5 and detection_mean[j+1] > detection_mean[j]:
                if start_counting != 1:
                    start_counting = 1
            # Falling edge
            elif detection_std[j] >= 0.5 and detection_mean[j+1] < detection_mean[j]:
                if start_counting != 0:
                    start_counting = 0
                    i = 0
                    # Compare with bandwidth
                    if(len(dTemp) >= step_size - 1 and len(dTemp) <= step_size + 1):
                        detection_res.append(freq[int(np.median(dTemp))])
                        level_res.append(level[int(np.median(dTemp))])
                    dTemp = []

            if start_counting:
                dTemp.append(j+i)
                i = i + 1
            else:
                detection_no_res.append(freq[j])
                level_no_res.append(level[j])
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

    # return fileName results
    return (fNameDetection,fNameNoDetection)

if __name__ == '__main__':
    main(sys.argv[1:])