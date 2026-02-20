#!/bin/bash

cd bin

source /cvmfs/cms.cern.ch/cmsset_default.sh

echo "Install particle gun with HepMC3"
cmssw-cc7 -- 'source /cvmfs/sw.hsf.org/spackages6/key4hep-stack/2022-12-23/x86_64-centos7-gcc11.2.0-opt/ll3gi/setup.sh && HEPMC3_PATH="/cvmfs/sw.hsf.org/spackages7/hepmc3/3.2.5/x86_64-centos7-gcc11.2.0-opt/rysg6" && export LD_LIBRARY_PATH=$HEPMC3_PATH/lib64:$LD_LIBRARY_PATH && g++ --std=c++11 -I${HEPMC3_PATH}/include -L${HEPMC3_PATH}/lib64 -lHepMC3 -o gunHEPMC3 ../bin/gunHEPMC3.cpp'
cmssw-cc7 -- 'source /cvmfs/sw.hsf.org/spackages6/key4hep-stack/2022-12-23/x86_64-centos7-gcc11.2.0-opt/ll3gi/setup.sh && HEPMC3_PATH="/cvmfs/sw.hsf.org/spackages7/hepmc3/3.2.5/x86_64-centos7-gcc11.2.0-opt/rysg6" && export LD_LIBRARY_PATH=$HEPMC3_PATH/lib64:$LD_LIBRARY_PATH && g++ --std=c++11 -I${HEPMC3_PATH}/include -L${HEPMC3_PATH}/lib64 -lHepMC3 -o jpsi_mumu_HEPMC3 ../bin/jpsi_mumu_HEPMC3.cpp'
echo "Done!"



echo "Install DelphesHEPMC3"
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2026-02-09 # 2026-01-11

git clone https://github.com/jeyserma/k4SimDelphes.git

cd k4SimDelphes
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j ${nproc}

cd ../install
export PATH=$(pwd)/bin:${PATH}
export LD_LIBRARY_PATH=$(pwd)/lib64:${LD_LIBRARY_PATH}
echo "Done!"

