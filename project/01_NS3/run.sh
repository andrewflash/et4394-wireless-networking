#!/bin/bash

curDir=$(pwd)
resultDir="$curDir/results"
resultFile="$resultDir/ns3_results_$(date +%m%d%Y_%H%M%S)"

mkdir $resultDir

# Change this path to your NS3 path
path="/home/xflash/Downloads/ns-allinone-3.24.1/ns-3.24.1/"

# Change with your application file
program="wifi-sim-andri.cc"
program_name="wifi-sim-andri"

# Insert user parameters here
echo -n "--------------------------------------------\n"
echo -n "WiFi simulator using NS3 by Andri Rahmadhani\n"
echo -n "--------------------------------------------\n"
echo -n "Available scenario:\n"
echo -n "  0 ==> Mobility: Static circular nodes location\n"
echo -n "  1 ==> Mobility: Static random nodes location\n"
echo -n "  2 ==> Mobility: Dynamic random walk 2D\n"
echo -n "  3 ==> DSSS data rate variation\n"
echo -n "  4 ==> Palyoad variation\n"
echo -n "  5 ==> RTS/CTS variation\n"
echo -n "Enter scenario number: "
read scenarioNumber

if [ $scenarioNumber -gt 5 ]; then
	echo "Invalid scenario"
	exit
fi

# Default parameter value
seqn=2
rad=10
payload=1024
rts=150
datarate="5Mbps"
dsssdatarate="DsssRate11Mbps"

echo -n "Enter min number of nodes: "
read nMin
echo -n "Enter max number of nodes: "
read nMax
if [ $scenarioNumber -eq 0 ]; then
	echo -n "Enter radius: "
	read rad
elif [ $scenarioNumber -eq 1 ]; then
	echo -n "Enter radius: "
	read rad
elif [ $scenarioNumber -eq 2 ]; then
	echo ""
elif [ $scenarioNumber -eq 3 ]; then
	echo -n "1 ==> DsssRate11Mbps\n"
	echo -n "2 ==> DsssRate5_5Mbps\n"
	echo -n "3 ==> DsssRate2Mbps\n"
	echo -n "4 ==> DsssRate1Mbps\n"
	echo -n "Enter number: "
	read nDSSS
	if [ $nDSSS -eq 1 ]; then
		dsssdatarate="DsssRate11Mbps"
	elif [ $nDSSS -eq 2 ]; then	
		dsssdatarate="DsssRate5_5Mbps"
	elif [ $nDSSS -eq 3 ]; then
		dsssdatarate="DsssRate2Mbps"
	elif [ $nDSSS -eq 4 ]; then
		dsssdatarate="DsssRate1Mbps"
	else
		echo -n "Invalid option\n"
		exit
	fi
elif [ $scenarioNumber -eq 4 ]; then
	echo -n "Enter payload size: "
	read payload
elif [ $scenarioNumber -eq 5 ]; then
	echo -n "0 => Do not use RTS/CTS\n"
	echo -n "1 => Use RTS/CTS\n"
	echo -n "Enter number: "
	read useRTS
	if [ $useRTS -eq 0 ]; then
		rts=2000
	elif [ $useRTS -eq 1 ]; then	
		rts=150	
	fi
fi

parameter="--scenario=$scenarioNumber --r=$rad --datarate=$datarate --rtsCts=$rts --payload=$payload --dsssdatarate=$dsssdatarate"

# Remove previous results
#rm -f results.txt

# Copy program to NS-3 scratch folder
cp -f $program ${path}/scratch
cd $path

# Iteration
for node in `seq $nMin $nMax`;
do
	for iteration in `seq $seqn`;
	do
		# Compile and run program
		./waf --run "$program_name $parameter --n=$node --output=$resultFile-N-$node.txt"  
  	done
done

# Plot results
cd $curDir
python plot.py