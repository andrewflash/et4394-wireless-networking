from datetime import datetime
import os, sys, getopt
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

use_list = 0
default_database = "dvbt_freq_delft.txt"
f_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
result_dir = 'results_' + f_timestamp + '/'
x_lim = 0.3
y_lim = 0.3
y_lim_min = 0.5
threshold = -70
use_threshold = 0

def main(argv):

    global x_lim, y_lim, y_lim_min, use_list, threshold, use_threshold

    input_file_result = ""
    input_file_no_detection = ""

    help_string = \
        "DVB-T Signal Detector - ROC Analyzer - by A. Rahmadhani\n" + \
        "--------------------------------------\n\n" + \
        "Usage: signal_detector_main.py [options]\n\n" + \
        "[options]:\n" + \
        "  -h : help\n" + \
        "  -q : use known DVB-T frequency list\n" + \
        "  -d <file_name> : signal detection results\n" + \
        "  -n <file_name> : signal not-detected results\n" + \
        "  -x <x_limit> : limit x axis for ROC\n" + \
        "  -l <y_min> : minimum y axis for ROC\n" + \
        "  -y <y_limit> : limit y axis for PDF curves\n" + \
        "  -t <threshold> : obtain result at specific threshold\n"

    # Read command line arguments
    try:
        opts, args = getopt.getopt(argv,"hqx:y:d:n:l:t:")
    except getopt.GetoptError:
        print help_string
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print help_string
            sys.exit()
        elif opt == "-q":
            use_list = 1
        elif opt == "-d":
            input_file_result = str(arg)
        elif opt == "-n":
            input_file_no_detection = str(arg)
        elif opt == "-x":
            x_lim = float(arg)
        elif opt == "-y":
            y_lim = float(arg)
        elif opt == "-l":
            y_lim_min = float(arg)
        elif opt == "-t":
            threshold = float(arg)
            use_threshold = 1

    analyze_ROC(input_file_result,input_file_no_detection)

def analyze_ROC(input_file_result,input_file_no_detection):
    global use_list, default_database, result_dir, x_lim, y_lim, y_lim_min, threshold, use_threshold

    freq_true_list = []

    if use_list:
        # Read from list
        with open(default_database,'r') as f:
            for l in f:
                s = l.strip()
                if s[0].isdigit():
                    freq_true_list.append(float(s))

    level = []
    level_no = []

    # Read results
    with open(input_file_result,'r') as f:
        for l in f:
            s = l.strip().split("\t")
            if s[0][0].isdigit():
                if use_list:
                    if float(s[0]) in freq_true_list:
                        level.append(float(s[1]))
                    else:
                        # Add to no-detection though is detected (false alarm)
                        level_no.append(float(s[1]))
                else:
                    level.append(float(s[1]))
                if use_threshold == 0:
                    threshold = float(s[2])

    # Create result dir if not exists
    try:
        os.makedirs(result_dir)
    except OSError:
        pass

    # Read no detection results
    with open(input_file_no_detection,'r') as f:
        for l in f:
            s = l.strip().split("\t")
            if s[0][0].isdigit():
                if use_list:
                    if float(s[0]) not in freq_true_list:
                        level_no.append(float(s[1]))
                    else:
                        # Add to level detection though is not detected (misdetection)
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
    plt.ylim(ymax=y_lim)
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
    plt.xlim(xmax=x_lim)
    plt.ylim(ymin=y_lim_min)
    plt.title('RTL-SDR ROC curves')
    plt.savefig(fNamePlt + ".png")
    plt.savefig(fNamePlt + ".pdf")
    plt.close()

# Find nearest value for ROC analysis
def getnearpos(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx

if __name__ == '__main__':
    main(sys.argv[1:])