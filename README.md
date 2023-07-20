# Artifact Evaluatiion

## Setup

This setup and docker file were tested on a MacOS system. Currently this is the only OS where both Maude and the testbed work.
The Maude docker has been tested on Windows (10) and Linux (Ubuntu 20.x).

Docker will be used to run and execute the Maude experiments and the actual real implementation tests (located in a framework called 'testbed').

The file 'script.sh' should install Docker and Docker Compose on the session. If you already have Docker installed, please comment lines 7-24.

Alternatively, you can also install Docker manually :
	1. Install [Docker](https://docs.docker.com/get-docker/)
	2. Install [docker-compose](https://docs.docker.com/compose/install/linux/)
	
	
	
## How to run + some explanations
Firstly, we have to download the zipped folder that contains some scripts and the actual code for the Maude project and the testbed.

Within that folder, we simply have to run the following command : 'bash script.sh' or ".\scrip.sh" that, regarding the Maude part, will take care of 
	1. Installing Maude
	2. Building the image
	3. Downloading all project files (from folder 'Maude') to the docker named 'artifact'
	4. Running the docker together with the script 'script-maude-allOSes.sh' which will set the environments, permissions and run the 5 experiments from the paper
	5. Retrieving the results
	
By linking one (newly created) folder to one within the docker, we can simply copy the results of the experiments to the docker folded, and it will automatically "import" its content to the folder outside Docker (in this case, "results").
	
Moreover, the script will carry out the testbed experiments by :
	1. Install Go (If a Go version is already installed, it won't do anything). NOTE: the testbed was run with the version 1.20.5, there is no guarantee the project can run correctly with other versions.
	2. Set up the environment variables and permissions
	3. Downloading and installing the necessary GO packages 
	4. Run the experiments
	5. Retrieve the values
	
Once this is done, one can inspect the resulting values inside the folder 'results' which contains the output of Maude and the testbed projects.

Finally, the script then continues by creating plots using the content of the folder by running the script 'plot.py'.
This will create two figures : 'attacks_af' and 'attacks_delay'.
Those correspond to the ones displayed in the paper 'A Formal Framework for End-to-End DNS Resolution', currently page 10-11.
Minor differences might be observed in the testbed results, this is expected as it is not an entirely deterministic process.


The script will execute the Maude code and the testbed for 5 experiments: 
	1. Subqueries + Unchained
	2. Subqueries + CNAME Scrubbing
	3. CNAME Scrubbing + QMIN
	4. CNAME Scrubbing + Delay
	5. CNAME Scrubbing + QMIN + Delay



## Remarks
More information about the Maude project and the testbed project can be found in the README.md of their respective folder.

### Docker
The -v command links current docker folder with the one within the container.

So we can extract the results of scripts being executed inside the container to a folder that we created. This is useful to easily and quickly inspect the output of our functions.
Here in our case, we first build the Maude image, then, as the script is not executed when building the docker (in Dockerfile), we use this command to run it:
			docker run --mount type=bind,source="${PWD}"/results,target=/results -v /var/run/docker.sock:/var/run/docker.sock -it artifact /bin/bash -c "./maude-allOSes.sh"
			

Otherwise, in case we want to execute directly the script when building the docker, we have to uncomment one of the last line of Dockerfile ("RUN ["/bin/bash", "-c", "./script.sh"]") and
	then executes the following command right after building the image:
	docker run --mount type=bind,source="${PWD}"/results,target=/results -v /var/run/docker.sock:/var/run/docker.sock -it artifact /bin/bash
	
### Maude
The docker seems to work fine with all tested OSes (MacOS, Ubuntu and Windows(10)).

### Testbed
The code used here comes from the testbed GitHub at the state of the 16th July 2023.
The actual code fulfilling steps 1-3 of the testbed part comes from the README of the testbed.

Following the README of the testbed, one can also mount its own attacks using real resolvers software.


### Settings other than the ones from the original project
Modified in utils.py : 
	MAUDE = '/maude/maude.linux64'

Modified in create_ccv_files.py:
	variants = [CCV_QMIN(), CCV_Delay(),CCV_QMIN_Delay()] 
	--- Here we can trigger Cname scrubbing + QMIN, CNAME Scrubbing + Delay, CNAME Scrubbing + QMIN + Delay

Modified in create_sub_cname_files.py:
	In main(): simply remove 'qmin_deactived=False; main()', since we have to disable QMIN

### Strategies

So far only MacOS works with our setup. We tried other strategies such as dind ("docker-in-docker"), a docker that will create dockers for Maude and the testbed,
another strategy was to run both dockers at the same level from within the current OS but compatibility issues and some error messages that were/are complex to solve made this hard to debug.

So the current strategy is to use use MacOS as the base system, at least for the testbed, since the Maude part of the docker seems to be working fine on MacOS, Ubuntu and Windows(10).

Another approach (not yet completely explored) would be to use [Docker-OSX](https://github.com/sickcodes/Docker-OSX) to simulate the MacOS environment in Docker, as this OS works fine with the projects. 
