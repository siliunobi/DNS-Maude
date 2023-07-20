# Installation and Usage
* Install and use the testbed according to `dnstestbed/readme.md`.
* The testbed was used and tested on `macos Monterey version 12.6.5`. Other operating systems are not guaranteed to be supported.

# Reproduction of Data
* The data used in _Figure 7 (a-c)_ and _8 (a-b)_ is created by running the experiments contained in `validation/framework`.
* To reproduce the specific data run the following commands

```
testbed run validation/framework/01_Subqueries+Unchained/experiment.yaml        // figure 7a
testbed run validation/framework/02_Subqueries+CNAME_Scrubbing/experiment.yaml  // figure 7b
testbed run validation/framework/03_CNAME_Scrubbing+QMIN/experiment.yaml        // figure 7c
testbed run validation/framework/04_CNAME_Scrubbing+Delay/experiment.yaml       // figure 8a
testbed run validation/framework/05_CNAME_Scrubbing+QMIN+Delay/experiment.yaml  // figure 8b
```
* The data will be alocated in the results directory within the respective experiment directory, e.g. `validation/framework/01_Subqueries+Unchained/results`. One might need to delete that directory before running the experiment again.