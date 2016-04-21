#!/bin/bash
path="/home/xflash/Downloads/ns-allinone-3.24.1/ns-3.24.1/"
program="wifi-sim-ref.cc"
parameter=""

cp $program ${path}/scratch
cd $path
#./waf --run $program $parameter
