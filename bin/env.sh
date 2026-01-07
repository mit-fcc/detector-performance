
#source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2023-11-23
#source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2025-05-29
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2025-12-12

cd "$(dirname "${BASH_SOURCE[0]}")/k4SimDelphes/install/"
export PATH=$(pwd)/bin:${PATH}
export LD_LIBRARY_PATH=$(pwd)/lib64:${LD_LIBRARY_PATH}
cd ../../../
