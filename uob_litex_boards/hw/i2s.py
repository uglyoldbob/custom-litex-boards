from litex.gen import *
from litex.soc.interconnect.stream import SyncFIFO
from litex.soc.interconnect import wishbone

import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = __dir__

def load_i2s_rx_files(platform):
    data_location2 = os.path.join(data_location, "i2srx", "SV_I2S_RX_CORE")
    for f in ["cntr_module.sv", "decoder_module.sv", "full_sync_dff_module.sv", "top_i2s_rx_module.sv"]:
        platform.add_source(os.path.join(data_location2, f))

class QuadPads:
    def __init__(self, pads, cpads, n):
        self.clk = cpads.sclk
        self.ws = pads.ws
        self.sync = Signal()
        self.rx = pads.rx[n]

class I2SQuad(LiteXModule):
    def __init__(self, pads, common_pads, depth=512):
        layout = [("ldata", 24), ("rdata", 24)]
        pads0 = QuadPads(pads, common_pads, 0)
        self.left0 = Signal(24)
        self.right0 = Signal(24)
        i2s0 = Instance("top_i2s_rx_module",
            i_bck_i = common_pads.sclk,
            i_lrck_i = pads.ws,
            i_dat_i = pads.rx,
            o_left_o = self.left0,
            o_right_o = self.right0,
            )
        self.specials += i2s0
        f1 = SyncFIFO(layout, depth)
        f1.sink.ldata.eq(self.left0)
        f1.sink.rdata.eq(self.right0)
        f1.sink.valid.eq(1)
        self.submodules += f1
        
        pads0 = QuadPads(pads, common_pads, 1)
        self.left1 = Signal(24)
        self.right1 = Signal(24)
        i2s1 = Instance("top_i2s_rx_module",
            i_bck_i = common_pads.sclk,
            i_lrck_i = pads.ws,
            i_dat_i = pads.rx,
            o_left_o = self.left1,
            o_right_o = self.right1,
            )
        self.specials += i2s1
        f2 = SyncFIFO(layout, depth)
        f2.sink.ldata.eq(self.left1)
        f2.sink.rdata.eq(self.right1)
        f2.sink.valid.eq(1)
        self.submodules += f2
        
        
        pads2 = QuadPads(pads, common_pads, 2)
        self.left2 = Signal(24)
        self.right2 = Signal(24)
        i2s2 = Instance("top_i2s_rx_module",
            i_bck_i = common_pads.sclk,
            i_lrck_i = pads.ws,
            i_dat_i = pads.rx,
            o_left_o = self.left2,
            o_right_o = self.right2,
            )
        self.specials += i2s2
        f3 = SyncFIFO(layout, depth)
        f3.sink.ldata.eq(self.left2)
        f3.sink.rdata.eq(self.right2)
        f3.sink.valid.eq(1)
        self.submodules += f3
        
        pads3 = QuadPads(pads, common_pads, 3)
        self.left3 = Signal(24)
        self.right3 = Signal(24)
        i2s3 = Instance("top_i2s_rx_module",
            i_bck_i = common_pads.sclk,
            i_lrck_i = pads.ws,
            i_dat_i = pads.rx,
            o_left_o = self.left3,
            o_right_o = self.right3,
            )
        self.specials += i2s3
        f4 = SyncFIFO(layout, depth)
        f4.sink.ldata.eq(self.left3)
        f4.sink.rdata.eq(self.right3)
        f4.sink.valid.eq(1)
        self.submodules += f4
        
        self.wb = wb = wishbone.Interface(data_width=32, address_width=4, addressing="word")
        self.submodules += wb
        self.comb += [
            If(self.wb.cyc & self.wb.stb, Case(wb.adr, {
                0: wb.dat_r.eq(f1.source.ldata),
                1: wb.dat_r.eq(f1.source.rdata), 
                2: wb.dat_r.eq(f2.source.ldata),
                3: wb.dat_r.eq(f2.source.rdata),
                4: wb.dat_r.eq(f3.source.ldata),
                5: wb.dat_r.eq(f3.source.rdata),
                "default": wb.dat_r.eq(0)}))
        ]