#!/bin/bash

# Run the 5 experiments of the testbed
echo "Running the testbed experiments..."
cd Testbed || { echo "Failed to enter 'Testbed' folder !"; exit 1; }
testbed run validation/framework/01_Subqueries+Unchained/experiment.yaml
testbed run validation/framework/02_Subqueries+CNAME_Scrubbing/experiment.yaml
testbed run validation/framework/03_CNAME_Scrubbing+QMIN/experiment.yaml
testbed run validation/framework/04_CNAME_Scrubbing+Delay/experiment.yaml
testbed run validation/framework/05_CNAME_Scrubbing+QMIN+Delay/experiment.yaml
# Copy the results of the testbed experiments to the folder 'results'
cp -R validation/framework/01_Subqueries+Unchained ../results
cp -R validation/framework/02_Subqueries+CNAME_Scrubbing ../results
cp -R validation/framework/03_CNAME_Scrubbing+QMIN ../results
cp -R validation/framework/04_CNAME_Scrubbing+Delay ../results
cp -R validation/framework/05_CNAME_Scrubbing+QMIN+Delay ../results
cd ..
# Values have been retrieved
echo "===> Testbed experiments have been executed !"
echo "Results can be inspected in the folder 'results' : 01_Subqueries+Unchained, 02_Subqueries+CNAME_Scrubbing, 03_CNAME_Scrubbing+QMIN, 04_CNAME_Scrubbing+Delay, 05_CNAME_Scrubbing+QMIN+Delay"
