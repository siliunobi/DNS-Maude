#!/bin/bash

echo "Creates the folder that will contain the results of the experiments"
mkdir -p ./results

## Install Docker to execute Maude and testbed experiments
apt-get update \
  && apt-get install -y \
	ca-certificates \
	curl \
	gnupg

echo "Installing Docker and Docker Compose ..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --yes --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
 "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
 "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
  
## Install docker compose (BEWARE the version, one is docker-compose, the newest docker-compose-plugin)
apt-get update \
  && apt-get install -y docker-compose docker-compose-plugin

echo "===> Docker and Docker Compose have been installed/updated ..."

echo "Create the Maude Docker container"
docker build -t artifact -f "Dockerfile-maude" .
echo "===> Maude Docker has been set up !"


## Install Go for the testbed, if another folder exists or the zip, don't un/install go version
echo "Trying to install Go"
if [ -f "go1.20.5.linux-amd64.tar.gz" -o -f /usr/local/go/bin ]
then
    echo "===> Another Go tar file already exists. No need to download another version."
else
	# Fetch go and untar it [BEWARE this may erase the other Go versions]
	wget https://go.dev/dl/go1.20.5.linux-amd64.tar.gz
	rm -rf /usr/local/go
	tar -C /usr/local -xzf go1.20.5.linux-amd64.tar.gz
	echo "===> Go has been installed"
fi


## Setting up the environment
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export GOPATH="$(go env GOPATH)"' >> ~/.bashrc
echo 'export PATH="$GOPATH/bin:$PATH"' >> ~/.bashrc
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.profile
echo 'export GOPATH="$(go env GOPATH)"' >> ~/.profile
echo 'export PATH="$GOPATH/bin:$PATH"' >> ~/.profile

## Update env var
source ~/.bashrc

## Sometimes bash is not added to the path
export PATH=$PATH:/bin/bash

# Set the environment var for this terminal as well
export GOPATH=$(go env GOPATH)
export PATH=$GOPATH/bin:$PATH

# Setup the testbed and install the libraries

## Set permission on testbed
chmod +x Testbed
cd Testbed || { echo "Failed to enter 'Testbed' folder !"; exit 1; }
go mod tidy
go install
cd ..
echo "===> The testbed has been set up"

echo "Installing the necessary packages for Python"
apt-get update \
  && apt-get install -y \
	python3-pip
pip3 install matplotlib numpy pandas
echo "===> Python packages have been installed !"

echo "===>"
echo "======> The complete setup for Maude and the testbed has been achieved !"


echo "Now executing the Maude experiments via the container 'artifact'..."
docker run --mount type=bind,source="${PWD}"/results,target=/results -v //var/run/docker.sock://var/run/docker.sock -it artifact /bin/bash -c "./script-maude-allOSes.sh"

echo "===> Maude experiments have been executed !"
echo "The results can be inspected in the folder 'results' : ccv-delay, ccv-qmin, ccv-qmin-delay, sub-ccv, sub-unchained-cname"


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

# Run the plotting script
echo "Plotting the results..."
python3 plot.py
echo "===> The plots have been created in the folder 'results' !"

echo "===>"
echo "======> The script has been entirely executed !"

echo "Exiting..."
