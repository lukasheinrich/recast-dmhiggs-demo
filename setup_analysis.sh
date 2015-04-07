#!/bin/zsh

#we need to work from this subdir for now. so cd into it
cd implementation

#this is needed for pythia
export PYTHIA8DATA=$(pythia8-config --xmldoc)

#done
