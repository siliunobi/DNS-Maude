#!/bin/bash

echo "Creates the folder that will contain the results of the experiments"
mkdir -p ./results

echo "Create the Maude Docker container"
docker build -t artifact -f "Dockerfile-maude" .
echo "===> Maude Docker has been set up !"


## Install Go 1.20.5 for the testbed, if another folder exists or the zip, don't un/install go version
echo "Trying to install Go"
if [ -f "go1.20.5.darwin-amd64.tar.gz" -o -d /usr/local/go ]
then
    echo "===> Another Go tar file already exists. No need to download another version."
else
	# Fetch go and untar it [BEWARE this may erase the other Go versions]
  curl -O https://go.dev/dl/go1.20.5.darwin-amd64.tar.gz
  rm -rf /usr/local/go
  tar -C /usr/local -xzf go1.20.5.darwin-amd64.tar.gz
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

echo "===>"
echo "======> The complete setup for Maude and the testbed has been achieved !"
