#!/usr/bin/env python3

# Template from litex-boards crosslink nx vip board
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Corrigan <davidcorrigan714@gmail.com>
# Copyright (c) 2020 Alan Green <avg@google.com>
# Copyright (c) 2020 David Shah <dave@ds0.me>
#
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from uob_litex_boards.platforms import uob_pcie1
from uob_litex_boards.i2s import I2SMaster
from uob_litex_boards.mipi import MipiCsiMaster

from litex.soc.cores.hyperbus import HyperRAM
from litex.soc.cores.i2c import I2CMaster

from litex.soc.cores.ram import NXLRAM
from litex.soc.cores.video import VideoHDMIPHY
from litex.build.io import CRG
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_por = ClockDomain()
        self.cd_hdmi = ClockDomain()
        self.cd_hdmi5x = ClockDomain()

        # TODO: replace with PLL
        # Clocking
        self.sys_clk = sys_osc = NXOSCA(platform)
        sys_osc.create_hf_clk(self.cd_sys, sys_clk_freq)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)
        rst_n = platform.request("reset")

        # Power On Reset
        por_cycles  = 4096
        por_counter = Signal(log2_int(por_cycles), reset=por_cycles-1)
        self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        self.sync.por += If(por_counter != 0, por_counter.eq(por_counter - 1))
        self.specials += AsyncResetSynchronizer(self.cd_por, ~rst_n)
        self.specials += AsyncResetSynchronizer(self.cd_sys, (por_counter != 0) | self.rst)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
        "rom":  0x00000000,
        "sram": 0x40000000,
        "csr":  0xf0000000,
    }
    def __init__(self, sys_clk_freq=75e6, toolchain="radiant",
        hyperram        = "none",
        with_led_chaser = True,
        with_video_terminal = True,
        with_video_colorbars = False,
        **kwargs):
        platform = uob_pcie1.Platform(toolchain=toolchain)
        platform.add_platform_command("ldc_set_sysconfig {{MASTER_SPI_PORT=SERIAL}}")

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)
        
        self.i2cm0 = I2CMaster(platform.request("i2c"))

        # SoCCore -----------------------------------------_----------------------------------------
        # Disable Integrated SRAM since we want to instantiate LRAM specifically for it
        kwargs["integrated_sram_size"] = 0
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on UOB PCIE1 Board", **kwargs)

        # SRAM/HyperRAM ----------------------------------------------------------------------------
        if hyperram == "none":
            # 128KB LRAM (used as SRAM) ------------------------------------------------------------
            size = 128 * KILOBYTE
            self.spram = NXLRAM(32, size)
            self.bus.add_slave("sram", slave=self.spram.bus, region=SoCRegion(origin=self.mem_map["sram"],
                size=size))
        else:
            # Use HyperRAM generic PHY as SRAM -----------------------------------------------------
            size = 8 * MEGABYTE
            hr_pads = platform.request("hyperram", int(hyperram))
            self.hyperram = HyperRAM(hr_pads, sys_clk_freq=sys_clk_freq)
            self.bus.add_slave("sram", slave=self.hyperram.bus, region=SoCRegion(origin=self.mem_map["sram"], size=size, mode="rwx"))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = Cat(*[platform.request("user_led", i) for i in range(3)]),
                sys_clk_freq = sys_clk_freq)
        
        self.videophy = VideoHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
        if with_video_terminal:
            self.add_video_terminal(phy=self.videophy, timings="1280x720@60Hz", clock_domain="hdmi")
        if with_video_colorbars:
            self.add_video_colorbars(phy=self.videophy, timings="1280x720@60Hz", clock_domain="hdmi")
        
        self.mipi0 = MipiCsiMaster(platform.request("camera", number=2))
        self.mipi1 = MipiCsiMaster(platform.request("camera", number=3))
        self.mipi2 = MipiCsiMaster(platform.request("camera", number=4))
        self.i2s_quad_0 = I2SMaster(platform.request("i2s_quad", number=0))
        self.i2s_quad_1 = I2SMaster(platform.request("i2s_quad", number=1))
        self.i2s_quad_2 = I2SMaster(platform.request("i2s_quad", number=2))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=uob_pcie1.Platform, description="LiteX SoC on UOB PCIE1 Board.")
    parser.add_target_argument("--sys-clk-freq",  default=75e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-hyperram", default="none",           help="Enable use of HyperRAM chip (none, 0 or 1).")
    parser.add_target_argument("--prog-target",   default="direct",         help="Programming Target (direct or flash).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
        hyperram     = args.with_hyperram,
        toolchain    = args.toolchain,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer(args.prog_target)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()

