from litex.gen import *
from litex.soc.interconnect.stream import SyncFIFO
from litex.soc.interconnect import wishbone

import os
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = __dir__

def load_mipi_csi_rx_files(platform):
    data_location2 = os.path.join(data_location, "USB_C_Industrial_Camera_FPGA_USB3", "FPGA_Firmware", "Source", "src")
    for source in os.listdir(data_location2):
        if source.endswith(".v"):
            platform.add_source(os.path.join(data_location2, source))
    data_location2 = os.path.join(data_location2, "Lattice_specfic")
    for source in os.listdir(data_location2):
        if source.endswith(".v"):
            platform.add_source(os.path.join(data_location2, source))

class MipiCsiMaster(LiteXModule):
    def __init__(self, pads):
        self.specials += Instance("mipi_csi_16_nx", 
            p_MIPI_LANES = len(pads.dp),
            p_MAX_PIXEL_WIDTH = 10,
            i_mipi_clk_p_in = pads.clkp,
            i_mipi_clk_n_in = pads.clkn,
            i_mipi_data_p_in = pads.dp,
            i_mipi_data_n_in = pads.dn,
        )