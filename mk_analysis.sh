#!/bin/zsh
# fail on first error
set -e 
(cd implementation/pythia && make)
(cd implementation/rivet && rivet-buildplugin RivetDMHigssFiducial.so DMHiggsFiducial.cc)
