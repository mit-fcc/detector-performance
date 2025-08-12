#!/bin/bash

source /cvmfs/cms.cern.ch/cmsset_default.sh
cmssw-el7 -- 'source /cvmfs/sw.hsf.org/spackages6/key4hep-stack/2022-12-23/x86_64-centos7-gcc11.2.0-opt/ll3gi/setup.sh && export HEPMC3_PATH="/cvmfs/sw.hsf.org/spackages7/hepmc3/3.2.5/x86_64-centos7-gcc11.2.0-opt/rysg6" && export LD_LIBRARY_PATH=$HEPMC3_PATH/lib64:$LD_LIBRARY_PATH && cd '$1' && '$2' '$3' '
