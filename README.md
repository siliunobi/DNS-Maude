# Artifact for "A Formal Framework for End-to-End DNS Resolution"

This repository contains the artifact for reproducing the results shown in the submission "[A Formal Framework for End-to-End DNS Resolution](https://github.com/siliunobi/DNS-Maude/blob/main/sigcomm23-paper683-submission.pdf)".

## Setup

This artifact was successfully tested on a macOS system (10.15 Catalina). Currently, this is the only OS where both the Maude docker and the testbed work.
The Maude docker (`Dockerfile-maude`) has been tested successfully as well on Windows (10) and Linux (Ubuntu 20.x).

Docker needs to be preliminarily installed to execute the Maude experiments and the actual real implementation tests (located in a framework called `testbed`).

Four main files are required for the setup:
- [script.sh](script.sh) : takes care of the setup, runs also the Maude docker, testbed and plot.py
- [Dockerfile-maude](Dockerfile-maude): environment setup for Maude
- [script-maude-allOSes.sh](script-maude-allOSes.sh): script to run Maude experiment (within Docker or not, see below)
- [plot.py](plot.py): creates plots from the retrieved results


## How to run
Firstly, we have to download and extract the zipped folder (of the repo) that contains scripts and the actual code for the Maude project and the testbed.

Some Python packages are to be installed for the plotting functions in `script.sh` to work. They can be found in `requirements.txt`.
```bash
python3 -m pip install -r requirements.txt
```

Within that (root) folder, we simply have to run the following command :
```bash
bash script.sh
```
(or `.\script.sh`) that is going to import necessary dependencies, packages and files, and going to run experiments both in Maude (model) and in a testbed (real-implementation).

More precise steps that this script is fulfilling are explained below in the subsections.

## How to run (separately)
Assuming we want to run part of the artifact separately, it is possible by running one of those 4 files:
1. `setup.sh` : create the docker container, install Go and set paths to folders and executables (some commented lines are used). Does **NOT** install Docker
2. `script-maude-allOSes.sh`: run the Maude experiments. Normally called together with Docker, can also be run on its own if [Maude 2.7.1](https://maude.cs.illinois.edu/w/index.php/All_Maude_2_versions), `ENV` variables, paths are defined and if folder name containing the Maude experiments code is modified
3. `script-testbed.sh`: run the testbed experiments (requires Docker installed on the machine and the correct environment variable to be set)
4. `script-plot.py`: plot the results


## Execution of `script.sh` and requirements

### Docker
The file `script.sh` and the other ones require Docker to be installed on the machine for Maude and the testbed.
If this is not the case, you can also install Docker following those lines:
1. Install [Docker](https://docs.docker.com/get-docker/)
2. Install [docker-compose](https://docs.docker.com/compose/install/linux/)


### Maude
To install Maude and environment, see [Maude/README.md](Maude/README.md). This step is **not** necessary if the Maude docker is used.

Regarding the ***Maude*** part, the script will take care of 
1. Installing Maude
2. Building the image
3. Downloading all project files (from folder `Maude/`) to the docker named `artifact`
4. Running the docker together with the script `script-maude-allOSes.sh` which will set the environments, permissions and run the 5 experiments from the paper
5. Retrieving the results
	
By linking one (newly created) folder to one within the docker, we can simply copy the results of the experiments to the docker folder, and it will automatically "import" its content to the folder outside Docker (in this case, `results`).

__Note__: if one created the appropriate environment on his/her machine without using Docker, running `script-maude-allOSes.sh`
will execute the Maude experiments and copy the results into `/results`. One can also comment all the lines starting with `cp -R`
in the file to avoid duplicating the data (those were necessary when using Docker).

### Testbed and Go
Moreover, the script will carry out the ***testbed*** experiments written in the [Go](https://go.dev/doc/install) language by :
1. Installing Go version `1.20.5` (If a Go version is already installed in `/usr/local/go`, it won't do anything).
2. Setting up the environment variables and permissions
3. Downloading and installing the necessary GO packages 
4. Running the experiments
5. Retrieving the values
	
Once the experiments have been completed, one can inspect the resulting values inside the folder `results` which contains the output of Maude and the testbed projects.

NOTE: the Go versions the testbed was run with are `1.18` and `1.20.5`, there is no guarantee the project can run correctly with other versions. We recommend using `1.20.5`.

### Plot the results
Finally, after having run the Maude and the testbed experiments, the script then continues by creating plots using the content of the folder by running the script `plot.py`.
This will create two figures : `attacks_af` and `attacks_delay`.
Those correspond to the ones displayed in the paper "[A Formal Framework for End-to-End DNS Resolution](https://github.com/siliunobi/DNS-Maude/blob/main/sigcomm23-paper683-submission.pdf)" currently page 10-11.
Minor differences might be observed in the testbed results, this is expected as it is not an entirely deterministic process.

#### Python packages

A `requirements.txt` is present in the root folder, in case anyone wants to run the experiments and the plotting file `plot.py` separately but directly in the folder using a virtual environment.
A similar file is located within `Maude` folder.
The necessary packages are `matplotlib` (`3.8.2`), `numpy`(`1.26.2`) and `pandas`(`2.1.3`). Most current versions of those should work fine as well.

### Chosen attacks
Regarding the tested ***attacks***, the script will execute the Maude code and the testbed for 5 of them (described in the paper): 
1. Subqueries + Unchained
2. Subqueries + CNAME Scrubbing
3. CNAME Scrubbing + QMIN
4. CNAME Scrubbing + Delay
5. CNAME Scrubbing + QMIN + Delay



## Remarks
More information about the Maude project and the testbed project can be found in the `README.md` of their respective folder.

The below lines contain some general information concerning the code of the two projects and their parameters.

### Docker
The Maude docker file works fine with all tested OSes (macOS 10.15, Ubuntu 20.x and Windows 10).

We can also run the Maude docker file and the corresponding script _independently_ of the main `script.sh` by executing the following commands within the root folder:
```bash
docker build -t artifact -f "Dockerfile-maude" .
docker run --mount type=bind,source="${PWD}"/results,target=/results -v //var/run/docker.sock://var/run/docker.sock -it artifact /bin/bash -c "./script-maude-allOSes.sh"
```

After running the experiments, we can extract the results of scripts being executed inside the container into a folder that we created. This is useful to easily and quickly inspect the output of our functions.
Here in our case, we first build the Maude image, then, as the script is not executed when building the docker (in Dockerfile), we use the second above command to run it.

The `-v` command links current docker folder with the one within the container.

### Testbed
The code used in this artifact for the testbed comes from this [GitHub repo](https://github.com/jaymoneyjay/dns-testbed) by Jodok Vieli at the state of the 16th July 2023.
Inside the `script.sh` file, the actual code fulfilling steps 1-3 (installing Go `1.20.5`, set environment variables, Go packages) of the testbed part comes from the README of the repo.

Following the README of the `testbed` folder, one can also mount **its own attacks** using real resolvers software.


## Strategies to expand portability

So far the only operating system that can entirely run our setup and the experiments is macOS version `10.15`.
We tried other strategies to port the projects to other OSes such as `dind` ("docker-in-docker"), a docker that will create dockers for Maude and the testbed, or
run both dockers (one creating the environment for the testbed and Maude) at the same level from within the current OS but compatibility issues and some error messages that were/are complex to solve make this hard to debug.

So the current (working) strategy is to use macOS as the base system, at least for the testbed, since the Maude part of the docker seems to be working fine on macOS, Ubuntu and Windows 10.

Another approach (not yet completely explored) to increase portability would be to use [Docker-OSX](https://github.com/sickcodes/Docker-OSX) to simulate the macOS environment in Docker, then hopefully run the docker file within this.