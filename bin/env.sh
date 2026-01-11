
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2026-01-11

cd "$(dirname "${BASH_SOURCE[0]}")/k4SimDelphes/install/"
export PATH=$(pwd)/bin:${PATH}
export LD_LIBRARY_PATH=$(pwd)/lib64:${LD_LIBRARY_PATH}
cd ../../../
