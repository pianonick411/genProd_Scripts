#!/bin/bash
set -euo pipefail
cd HOME
cd CMSSW/src
eval `scramv1 runtime -sh`

# Make untar directory in the rundir #
tar -xvf GRIDPACK_PATH -C PATH_TO_RUN_DIR
# Run the gridpack for 100k events #
cd PATH_TO_RUN_DIR 
./runcmsgrid.sh 10000 1 1 
# Move the output to MELA_PY
cp cmsgrid_final.lhe MELA_PY_PATH/OUTLHENAME
# Run LHE2ROOT #
cd CMSSW/src
cmsenv 
cd MELA_PY_PATH/..
source ./setup.sh 
eval $(./setup.sh env)
cd MELA_PY_PATH
# Delete the output root file if it exists
[ -f "OUTROOT" ] && rm "OUTROOT"
python3 lhe2root_v2.py OUTROOT OUTLHENAME PROCESS
# Make the Plots and move them to the correct directory
cd HOME
python3 PlotFromRoot.py -i PATH_TO_OUT_ROOT -o PATH_TO_PLOTS_DIR -r PATH_TO_RUN_DIR
