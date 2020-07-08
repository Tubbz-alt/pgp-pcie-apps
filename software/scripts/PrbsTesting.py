#!/usr/bin/env python3
##############################################################################
## This file is part of 'PGP PCIe APP DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the
## top-level directory of this distribution and at:
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
## No part of 'PGP PCIe APP DEV', including this file,
## may be copied, modified, propagated, or distributed except according to
## the terms contained in the LICENSE.txt file.
##############################################################################

import sys
import rogue
import rogue.hardware.axi
import rogue.interfaces.stream
import pyrogue as pr
import pyrogue.gui
import pyrogue.utilities.prbs
import pyrogue.interfaces.simulation
import argparse
import axipcie as pcie
import surf.protocols.ssi as ssi

#################################################################

# Set the argument parser
parser = argparse.ArgumentParser()

# Convert str to bool
argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

# Add arguments
parser.add_argument(
    "--dev",
    type     = str,
    required = False,
    default  = '/dev/datadev_0',
    help     = "path to device",
)

parser.add_argument(
    "--numLane",
    type     = int,
    required = False,
    default  = 1,
    help     = "# of DMA Lanes",
)

parser.add_argument(
    "--prbsWidth",
    type     = int,
    required = False,
    default  = 256,
    help     = "# of DMA Lanes",
)

parser.add_argument(
    "--numVc",
    type     = int,
    required = False,
    default  = 1,
    help     = "# of VC (virtual channels)",
)

parser.add_argument(
    "--loopback",
    type     = argBool,
    required = False,
    default  = False,
    help     = "Enable read all variables at start",
)

parser.add_argument(
    "--fwRx",
    type     = argBool,
    required = False,
    default  = False,
    help     = "Enable read all variables at start",
)

parser.add_argument(
    "--fwTx",
    type     = argBool,
    required = False,
    default  = True,
    help     = "Enable read all variables at start",
)

parser.add_argument(
    "--swRx",
    type     = argBool,
    required = False,
    default  = True,
    help     = "Enable read all variables at start",
)

parser.add_argument(
    "--swTx",
    type     = argBool,
    required = False,
    default  = False,
    help     = "Enable read all variables at start",
)

parser.add_argument(
    "--pollEn",
    type     = argBool,
    required = False,
    default  = True,
    help     = "Enable auto-polling",
)

parser.add_argument(
    "--initRead",
    type     = argBool,
    required = False,
    default  = True,
    help     = "Enable read all variables at start",
)

# Get the arguments
args = parser.parse_args()

#################################################################

# Set base
base = pr.Root(name='pciServer',description='DMA Loopback Testing')

# Create PCIE memory mapped interface
memMap = rogue.hardware.axi.AxiMemMap(args.dev)

# Add the PCIe core device to base
base.add(pcie.AxiPcieCore(
    memBase     = memMap ,
    offset      = 0x00000000,
    numDmaLanes = args.numLane,
    expand      = False,
))

# Loop through the DMA channels
for lane in range(args.numLane):

    # Loop through the virtual channels
    for vc in range(args.numVc):

        if (args.fwTx):
            # Add the FW PRBS TX Module
            base.add(ssi.SsiPrbsTx(
                name    = ('FwPrbsTx[%d][%d]' % (lane,vc)),
                memBase = memMap,
                offset  = 0x00800000 + (0x10000*lane) + (0x1000*(2*vc+0)),
                expand  = False,
            ))

        if (args.fwRx):
            # Add the FW PRBS RX Module
            base.add(ssi.SsiPrbsRx(
                name    = ('FwPrbsRx[%d][%d]' % (lane,vc)),
                memBase = memMap,
                offset  = 0x00800000 + (0x10000*lane) + (0x1000*(2*vc+1)),
                expand  = False,
            ))


#################################################################

# Create an arrays to be filled
dmaStream = [[None for x in range(args.numVc)] for y in range(args.numLane)]
prbsRx    = [[None for x in range(args.numVc)] for y in range(args.numLane)]
prbTx     = [[None for x in range(args.numVc)] for y in range(args.numLane)]

# Loop through the DMA channels
for lane in range(args.numLane):

    # Loop through the virtual channels
    for vc in range(args.numVc):

        # Set the DMA loopback channel
        dmaStream[lane][vc] = rogue.hardware.axi.AxiStreamDma(args.dev,(0x100*lane)+vc,1)
        dmaStream[lane][vc].setDriverDebug(0)

        if (args.loopback):
            # Loopback the PRBS data
            pyrogue.streamConnect(dmaStream[lane][vc],dmaStream[lane][vc])

        else:
            if (args.swRx):
                # Connect the SW PRBS Receiver module
                prbsRx[lane][vc] = pr.utilities.prbs.PrbsRx(
                    name         = ('SwPrbsRx[%d][%d]'%(lane,vc)),
                    width        = args.prbsWidth,
                    checkPayload = False,
                    expand       = False,
                )
                pyrogue.streamConnect(dmaStream[lane][vc],prbsRx[lane][vc])
                base.add(prbsRx[lane][vc])

            if (args.swTx):
                # Connect the SW PRBS Transmitter module
                prbTx[lane][vc] = pr.utilities.prbs.PrbsTx(
                    name    = ('SwPrbsTx[%d][%d]'%(lane,vc)),
                    width   = args.prbsWidth,
                    expand  = False,
                )
                pyrogue.streamConnect(prbTx[lane][vc], dmaStream[lane][vc])
                base.add(prbTx[lane][vc])

#################################################################

# Start the system
base.start(
    pollEn   = args.pollEn,
    initRead = args.initRead,
)

# Create GUI
appTop = pr.gui.application(sys.argv)
guiTop = pr.gui.GuiTop()
appTop.setStyle('Fusion')
guiTop.addTree(base)
guiTop.resize(600, 800)

print("Starting GUI...\n");

# Run GUI
appTop.exec_()

# Close
base.stop()
exit()
