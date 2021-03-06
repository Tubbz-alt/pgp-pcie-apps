##############################################################################
## This file is part of 'PGP PCIe APP DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'PGP PCIe APP DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

# Setup environment
source /afs/slac.stanford.edu/g/reseng/rogue/anaconda/rogue_pre-release.sh

# Python Package directories
export SURF_DIR=${PWD}/../firmware/submodules/surf/python
export PCIE_DIR=${PWD}/../firmware/submodules/axi-pcie-core/python

# Setup python path
export PYTHONPATH=${SURF_DIR}:${PCIE_DIR}:${PYTHONPATH}
