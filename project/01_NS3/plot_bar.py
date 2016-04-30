#!/usr/bin/env python

from os import listdir
from os.path import isfile, join
from datetime import datetime
import os, sys, getopt
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import glob

def main(argv):
	dirFold = "results_combine"
	files = [dirFold + "/results1.txt", dirFold + "/results2.txt", //
		dirFold + "/results3.txt","/results4.txt"

	throughput1 = []
	throughput2 = []
	throughput3 = []
	throughput4 = []
	n = []
	temp = []

	# File 1
	f = open(file1,'r')
	for l in f:
		s = l.strip().split("\t")
		if s[0][0].isdigit():
			temp.append(float(s[0]))
			cur_n = float(s[0])
	f.close()

	throughput.append(np.mean(temp))
	n.append(cur_n)
	temp = []

	plt.plot(n,throughput1,'gv-',label="Average throughput");
	plt.plot(n,throughput);
	plt.xlabel('Number of nodes')
	plt.ylabel('Throughput (Mbps)')
	plt.legend(loc='center right')

	# Save to file
	f_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	
	fout = open(dirFile + "/results_"+f_timestamp+".txt",'w')
	fout.write("N\tAvg.Throughput\tTotalThroughput\n")
	for i,j,k in zip(n,throughput,throughputTot):
		fout.write(str(i)+"\t"+str(j)+"\t"+str(k)+"\n")
	fout.close()

	plt.savefig(dirFile + "/results_"+f_timestamp+".png")
	plt.savefig(dirFile + "/results_"+f_timestamp+".pdf")

if __name__ == '__main__':
    main(sys.argv[1:])