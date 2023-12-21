# Artifact for "A Formal Framework for End-to-End DNS Resolution"

This repository contains the artifact for reproducing the results shown in the SIGCOMM'23 paper "[A Formal Framework for End-to-End DNS Resolution](https://dl.acm.org/doi/abs/10.1145/3603269.3604870)".

## Setup

This artifact was successfully tested on two macOS systems (Monterey 12.6.5 and Catalina 10.15).
Currently, those are the only known OS versions where **both** the Maude docker and the testbed work.
The Maude docker (`Dockerfile-maude`) has been run successfully as well on Linux (Ubuntu 20.x) and Windows (10).

Docker needs to be preliminarily installed to execute the Maude experiments and the actual real implementation tests (located in a framework called `testbed`). The Docker service or Docker Desktop must be up before running the scripts or experiments.


Go is necessary to run the testbed (tested with `1.18` and `1.20.5`). It can be installed via `script.sh`.

Four main files are required for the setup:
- [script.sh](script.sh) : takes care of the setup, runs the Maude docker, the testbed experiments and plot.py
- [Dockerfile-maude](Dockerfile-maude): environment setup for Maude
- [script-maude-allOSes.sh](script-maude-allOSes.sh): script to run Maude experiments (within Docker or not, see below)
- [plot.py](plot.py): creates plots from the retrieved results

Compatibility matrix of the artifact:

| Part    | macOS Monterey 12.6.5	 | macOS Catalina 10.15 | Ubuntu 20.x | Windows 10 |
|---------|------------------------|----------------------|-------------|------------|
| Maude   | &#9745;                | &#9745;              | &#9745;     | &#9745;    |
| Testbed | &#9745;                | &#9745;              | &#9744;     | &#9744;    |

**NOTE**: For users on macOS machine using the M2 chip or using other macOS versions that the recommended ones, the testbed does **not**/might **not** work.
The Maude docker may run correctly in case of M2 chip if some files are modified:
- Replacing the 1st line of the `Dockerfile-maude` by ```
  FROM --platform=linux/x86_64 ubuntu:jammy```
- Removing the parameter ```-v //var/run/docker.sock://var/run/docker.sock``` from the Docker [command](#run-docker-maude) to run the container (line `60` in `script.sh`).

## How to run
Firstly, we have to download and extract the zipped folder (of the repo) that contains scripts and the actual code for the Maude project and the testbed.

Some Python packages are to be installed for the plotting functions in `script.sh` to work. They can be found in `requirements.txt`.
```bash
python3 -m pip install -r requirements.txt
```

Then, within that (root) folder, we simply have to run the following command to launch the artifact :
```bash
bash script.sh
```
(or `.\script.sh`). It is going to import necessary dependencies, packages and files, and going to run experiments both in Maude (model) and in a testbed (real-implementation).

More precise steps that this script is fulfilling are explained below in the subsections.

## How to run (separately)
Assuming we want to run part of the artifact separately, it is possible by running one of those 4 files:
1. `setup.sh` : create the docker container, install Go and set paths to folders and executables (some commented lines are used). Does **NOT** install Docker
2. `script-maude-allOSes.sh`: run the Maude experiments. Normally called together with Docker, can also be run on its own if [Maude 2.7.1](https://maude.cs.illinois.edu/w/index.php/All_Maude_2_versions), `ENV` variables, paths are defined on the machine and if folder name containing the Maude experiments code is modified
3. `script-testbed.sh`: run the testbed experiments (requires Docker and Go to be installed, and the correct environment variables to be set)
4. `script-plot.py`: plot the results


## Execution of `script.sh` and requirements

### Docker
The main script `script.sh` and the other files require Docker to be installed on the machine for Maude and the testbed.
If this is not the case, you can also install Docker following those lines:
1. Install [Docker](https://docs.docker.com/get-docker/)
2. Install [docker-compose](https://docs.docker.com/compose/install/linux/)

### Maude
To install Maude and environment, see `Requirements` in [Maude/README.md](Maude/README.md). This step is **not** necessary if the Maude docker is used.

Regarding the ***Maude*** part, the script will take care of building a Docker image (`artifact`):
1. Setting up the environment image (ubuntu:jammy)
2. Installing Python3 and dependencies
3. Downloading all project files (from folder `Maude/`) to the container
4. Downloading and setting up [Maude 2.7.1 for Linux](https://maude.cs.illinois.edu/w/images/5/5d/Maude-2.7.1-linux.zip)

Then it will continue by:
1. Running the docker with the script `script-maude-allOSes.sh` which will run the 5 experiments from the paper
2. Retrieving the results from the docker

Modifying lines `13-22` of `script-maude-allOSes.sh` allows to choose which attacks will be run.
Moreover, any modifications to the files `create_sub_cname_files.py`, `create_sub_ccv_files.py` and `create_ccv_files.py`,
located in [Maude/attacks_vs_model_resolvers](Maude/attacks_vs_model_resolvers), can change which resolver models are being attacked and which attack is used.
Furthermore, parameters of the attack can be tuned in those files.

Here a folder `results` has been created and the results of the Maude experiments within the container were transferred to it.

__Note__: If one created the appropriate environment on his/her machine without using Docker, running `script-maude-allOSes.sh`
will execute the Maude experiments and copy the results into `/results`. One can comment all the lines starting with `cp -R`
in the file to avoid duplicating the data (those were necessary when using Docker).

__Note 2__: One can build the Docker image and run it **without** having to run the testbed, by using the two commands in the subsection [Remarks/Run Docker Maude](#run-docker-maude).

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
Regarding the ***attacks***, the script will execute the Maude code and the testbed for 5 of them (described in the paper):
1. Subqueries + Unchained
2. Subqueries + CNAME Scrubbing
3. CNAME Scrubbing + QMIN
4. CNAME Scrubbing + Delay
5. CNAME Scrubbing + QMIN + Delay



## Remarks
More information about the Maude project and the testbed project can be found in the `README.md` of their respective folder.

The below lines contain some general information concerning the code of the two projects and their parameters.

### Run Docker Maude
The Maude docker file works fine with all tested OSes (macOS `10.15`, macOS `12.6.5`, Ubuntu `20.x` and Windows 10).

We can also run the Maude docker file and the corresponding script _independently_ of the main `script.sh` by executing the following commands within the root folder:
```bash
docker build -t artifact -f "Dockerfile-maude" .
docker run --mount type=bind,source="${PWD}"/results,target=/results -v //var/run/docker.sock://var/run/docker.sock -it artifact /bin/bash -c "./script-maude-allOSes.sh"
```

After running the experiments, the results of scripts executed inside the container were extracted into a folder that we created beforehand (`results`).
This is useful to easily and quickly inspect the output of our functions.
Here, we first build the Maude image, then, as the script is not executed when building the docker (in Dockerfile), we use the second above command to run it and link the `results` folder to the docker.

The `-v` command gives access to the Docker daemon.

### Testbed
By running the `script.sh` file, the script will fulfil steps 3-5 of the [Testbed/readme.md](Testbed/readme.md), namely installing Go `1.20.5` and set environment variables,
Go packages. __Note__: steps 1-2 are installing Docker and Docker Compose.

Moreover, one can also mount **its own attacks** using real resolvers software with this testbed.

For more information about the testbed, please check this file [Testbed/readme.md](Testbed/readme.md).


## Strategies to expand portability

The only operating system that can entirely run our setup and the experiments is macOS, version `10.15` and version `12.6.5`.
We tried other strategies to port the projects to other OSes such as `dind` ("docker-in-docker"), a docker that will create dockers for Maude and the testbed, or
run both dockers (one creating the environment for the testbed and Maude) at the same level from within the current OS but compatibility issues and some error messages that were/are complex to solve make this hard to debug.

So the currently working strategy is to use macOS as the base system with those **recommended** versions, at least for the testbed, since the Maude part of the docker seems to be working fine on macOS, Ubuntu and Windows 10.
