#!/bin/bash

chmod +wx MAUDE_EXP/
# Run the maude experiments, some attacks are triggered by the same files
#export PATH=$PATH:/maude
#export MAUDE_LIB='/Maude-2.7.1-linux'
cd MAUDE_EXP/attacks_vs_model_resolvers || { echo "Failed to enter 'MAUDE_EXP/attacks_vs_model_resolvers' folder !"; exit 1; }
# create_sub_cname_files -> in main: we set qmin to be deactived for the attack Subqueries Unchained CNAME
python3 ./create_sub_cname_files.py
cp -R ./sub-unchained-cname ./results

python3 ./create_sub_ccv_files.py
cp -R ./sub-ccv ./results
# Here we can trigger Cname scrubbing + QMIN, CNAME Scrubbing + Delay, CNAME Scrubbing + QMIN + Delay
python3 ./create_ccv_files.py
cp -R ./ccv-qmin ./results
cp -R ./ccv-qmin-delay ./results
cp -R ./ccv-delay ./results


echo "===> Values for the Maude experiments have been retrieved !"

