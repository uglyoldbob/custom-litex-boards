#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.fhdl.specials import Tristate
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *

from litex.build.io import DDROutput
from litex.build.generic_platform import *

from litex.soc.cores.clock.gowin_gw2a import GW2APLL, GW2ADIV
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.interconnect import wishbone
from litex.soc.interconnect.csr import CSRStorage
from litex.soc.interconnect.csr_eventmanager import EventManager, EventSourcePulse
from litex.soc.interconnect.stream import Endpoint, SyncFIFO
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.led import LedChaser, WS2812
from litex.soc.cores.prbs import PRBS31Generator
from litex.soc.cores.video import VideoGowinHDMIPHY, video_timing_layout, video_data_layout;

from litedram.frontend.wishbone import LiteDRAMWishbone2Native
from litedram.modules import M12L64322A  # FIXME: use the real model number
from litedram.phy import GENSDRPHY

from litex_boards.platforms import sipeed_tang_nano_20k

from uob_litex_boards.software.constants import SoftwareWbsdcard, SoftwareNes

from nes import Nes
from opencores_sdcard import SdCard

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, reset=None):
        self.inclock = Signal()
        self.rst      = Signal()
        clki = Signal()
        clko = Signal()
        self.cd_sys   = ClockDomain()
        self.cd_por   = ClockDomain()
        self.cd_hdmi  = ClockDomain()
        self.cd_hdmi5x  = ClockDomain()

        # Clk
        clk27 = platform.request("clk27")
        
        self.specials += Instance("IBUF",
                i_I = clk27,
                o_O = self.inclock)

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        self.por_done  = por_done = Signal()
        self.comb += self.cd_por.clk.eq(self.inclock)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW2APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done)
        pll.register_clkin(self.inclock, 27e6)
        pll.create_clkout(self.cd_hdmi5x, 371.25e6)
        self.div5 = GW2ADIV(self.cd_hdmi5x.clk, "5")
        self.comb += self.cd_hdmi.clk.eq(self.div5.clkout)
        self.comb += self.cd_hdmi.rst.eq(self.rst)
        
        if sys_clk_freq == 37125000:
            self.div2 = GW2ADIV(self.div5.clkout, "2")
            self.comb += self.cd_sys.clk.eq(self.div2.clkout)
        else:
            self.pll2 = pll2 = GW2APLL(devicename=platform.devicename, device=platform.device)
            if reset is not None:
                self.comb += pll2.reset.eq(~por_done | reset)
            else:
                self.comb += pll2.reset.eq(~por_done)
            pll2.register_clkin(self.inclock, 27e6)
            pll2.create_clkout(self.cd_sys, sys_clk_freq)

class WbSdcard(LiteXModule):
    def __init__(self, core, platform, sys_clk_freq):
        self.submodules.ev = EventManager()
        self.ev.int_data = EventSourcePulse()
        self.ev.int_cmd = EventSourcePulse()
        self.ev.finalize()
        sdthing = SdCard(platform)
        pads = platform.request("sdcard")
        wb = wishbone.Interface(data_width=32, address_width=11, addressing="word")
        wbm = wishbone.Interface(data_width=32, address_width=29, addressing="word")
        sd_cmd_o = Signal()
        sd_cmd_i = Signal()
        sd_cmd_oe = Signal()
        self.specials += Tristate(pads.cmd, sd_cmd_o, sd_cmd_oe, i=sd_cmd_i)
        sd_dat_o = Signal(4)
        sd_dat_i = Signal(4)
        sd_dat_oe = Signal()
        sys_clk = ClockSignal("sys")
        idata = Signal()
        icmd = Signal()
        self.specials += Tristate(pads.data, sd_dat_o, sd_dat_oe, i=sd_dat_i)
        sd_wb_slave = Instance("sdc_controller",
            i_wb_clk_i = sys_clk,
            i_wb_rst_i = ResetSignal("sys"),
            i_wb_dat_i = wb.dat_w,
            o_wb_dat_o = wb.dat_r,
            i_wb_adr_i = wb.adr[0:8],
            i_wb_sel_i = wb.sel,
            i_wb_we_i = wb.we,
            i_wb_cyc_i = wb.cyc,
            i_wb_stb_i = wb.stb,
            o_wb_ack_o = wb.ack,
            o_m_wb_adr_o = wbm.adr,
            o_m_wb_sel_o = wbm.sel,
            o_m_wb_we_o = wbm.we,
            o_m_wb_dat_o = wbm.dat_w,
            i_m_wb_dat_i = wbm.dat_r,
            o_m_wb_cyc_o = wbm.cyc,
            o_m_wb_stb_o = wbm.stb,
            i_m_wb_ack_i = wbm.ack,
            o_m_wb_cti_o = wbm.cti,
            o_m_wb_bte_o = wbm.bte,
            i_sd_cmd_dat_i = sd_cmd_i,
            o_sd_cmd_out_o = sd_cmd_o,
            o_sd_cmd_oe_o = sd_cmd_oe,
            i_sd_dat_dat_i = sd_dat_i,
            o_sd_dat_out_o = sd_dat_o,
            o_sd_dat_oe_o = sd_dat_oe,
            o_sd_clk_o_pad = pads.clk,
            i_sd_clk_i_pad = sys_clk,
            o_int_cmd = icmd,
            o_int_data = idata,
            )
        self.comb += [
            self.ev.int_data.trigger.eq(idata),
            self.ev.int_cmd.trigger.eq(icmd),
        ]
        self.specials += sd_wb_slave
        core.bus.add_slave(name="sdcard", slave=wb, region=SoCRegion(
            origin = 0x3000_0000,
            size   = 1024,
        ))
        core.bus.add_master(master=wbm, region=SoCRegion(origin=0x40000000, size=0x00800000))

class NesInst(LiteXModule):
    def __init__(self, core, platform, sys_clk_freq):
        nes = Nes(platform)
        self.vin = Endpoint(video_timing_layout)
        self.vout = Endpoint(video_data_layout)
        self.testo = Signal(2)
        nes_clk = ClockSignal("hdmi")
        nes_box_valid1 = Signal()
        nes_box_valid2 = Signal()
        nes_picture_box_valid = Signal()
        video_fifo_read = Signal()
        self.comb += [
            If((self.vin.hcount > 255) & (self.vin.hcount < 1024), nes_box_valid1.eq(1)),
            If(self.vin.vcount < self.vin.vres, nes_box_valid2.eq(1)),
            nes_picture_box_valid.eq(nes_box_valid1 & nes_box_valid2),
            video_fifo_read.eq(self.vout.ready & nes_picture_box_valid),
        ]
        self.vid_select = CSRStorage(8)
        
        hdmi_data = Signal(24)
        hdmi_row = Signal(11)
        hdmi_column = Signal(12)
        hdmi_data_valid = Signal()
        hdmi_line_done = Signal()
        hdmi_line_ready = Signal()
        self.comb += [
                If(self.vin.vcount < 720, hdmi_line_ready.eq(self.vin.hsync)),
        ]
        cpu_oe = Signal(2)
        self.wb_rom = wb_rom = wishbone.Interface(data_width=16, address_width=21, addressing="word")
        nes_reset = ResetSignal("hdmi")
        self.specials += Instance("Nes",
            p_clockbuf = "none",
            p_FREQ = 74250000,
            p_sim = 0,
            p_softcpu = 0,
            p_ramtype = "wishbone",
            p_rambits = 3,
            p_random_noise = 1,
            i_clock = nes_clk,
            i_reset = nes_reset,
            o_testo = self.testo,
            o_hdmi_pixel_out = hdmi_data,
            i_hdmi_vsync = self.vin.vsync,
            o_hdmi_valid_out = hdmi_data_valid,
            i_hdmi_pvalid = 1,
            o_hdmi_line_done = hdmi_line_done,
            i_hdmi_line_ready = hdmi_line_ready,
            i_rom_wb_ack = wb_rom.ack,
            i_rom_wb_d_miso = wb_rom.dat_r,
            o_rom_wb_d_mosi = wb_rom.dat_w,
            i_rom_wb_err = wb_rom.err,
            o_rom_wb_addr = wb_rom.adr,
            o_rom_wb_bte = wb_rom.bte,
            o_rom_wb_cti = wb_rom.cti,
            o_rom_wb_cyc = wb_rom.cyc,
            o_rom_wb_sel = wb_rom.sel,
            o_rom_wb_stb = wb_rom.stb,
            o_rom_wb_we = wb_rom.we,
            o_cpu_oe = cpu_oe,
        )
        #core.bus.add_master(master=self.wb_rom, region=SoCRegion(origin=0x40000000, size=0x00800000))
        #TODO
        rgb_layout = [
                ("r", 8),
                ("g", 8),
                ("b", 8)
        ]
        fifo = SyncFIFO(rgb_layout, 2048)
        vidtest = PRBS31Generator(24)
        vidtest = ClockDomainsRenamer( {"sys" : "hdmi"} )(vidtest)
        self.fifo = ClockDomainsRenamer( {"sys": "hdmi"} )(fifo)
        self.submodules += [vidtest, self.vid_select, self.fifo]
        self.comb += Case(self.vid_select.storage, {
                0: [self.vin.ready.eq(self.vout.ready),
                    self.vout.hsync.eq(self.vin.hsync),
                    self.vout.vsync.eq(self.vin.vsync),
                    self.vout.de.eq(self.vin.de),
                    self.fifo.sink.r.eq(hdmi_data[0:8]),
                    self.fifo.sink.g.eq(hdmi_data[8:16]),
                    self.fifo.sink.b.eq(hdmi_data[16:24]),
                    self.fifo.source.ready.eq(video_fifo_read),
                    self.fifo.sink.valid.eq(hdmi_data_valid),
                    self.vout.valid.eq(self.fifo.source.valid),
                    If(nes_picture_box_valid, [self.vout.r.eq(self.fifo.source.r), 
                        self.vout.g.eq(self.fifo.source.g), 
                        self.vout.b.eq(self.fifo.source.b)]),],
                1: [self.vin.ready.eq(self.vout.ready),
                    self.vout.hsync.eq(self.vin.hsync),
                    self.vout.vsync.eq(self.vin.vsync),
                    self.vout.de.eq(self.vin.de),
                    self.fifo.sink.r.eq(hdmi_data[0:8]),
                    self.fifo.sink.g.eq(hdmi_data[8:16]),
                    self.fifo.sink.b.eq(hdmi_data[16:24]),
                    self.fifo.source.ready.eq(self.vout.ready),
                    self.fifo.sink.valid.eq(hdmi_data_valid),
                    self.vout.valid.eq(self.fifo.source.valid),
                    self.vout.r.eq(self.fifo.source.r), 
                    self.vout.g.eq(self.fifo.source.g), 
                    self.vout.b.eq(self.fifo.source.b)],
                2: [self.vin.ready.eq(self.vout.ready),
                    self.vout.hsync.eq(self.vin.hsync),
                    self.vout.vsync.eq(self.vin.vsync),
                    self.vout.de.eq(self.vin.de),
                    self.vout.r.eq(vidtest.o[0:8]), 
                    self.vout.g.eq(vidtest.o[8:16]), 
                    self.vout.b.eq(vidtest.o[16:24])],
                3: [self.vin.ready.eq(self.vout.ready),
                    self.vout.valid.eq(self.vin.valid),
                    self.vout.hsync.eq(self.vin.hsync),
                    self.vout.vsync.eq(self.vin.vsync),
                    self.vout.de.eq(self.vin.de),   
                    self.vout.r.eq(hdmi_data[0:8]), 
                    self.vout.g.eq(hdmi_data[8:16]), 
                    self.vout.b.eq(hdmi_data[16:24])],
                4: [self.vin.ready.eq(self.vout.ready),
                    self.vout.hsync.eq(self.vin.hsync),
                    self.vout.vsync.eq(self.vin.vsync),
                    self.vout.de.eq(self.vin.de),
                    self.vout.r.eq(255), 
                    self.vout.g.eq(0), 
                    self.vout.b.eq(255)],
                "default": [self.vin.ready.eq(self.vout.ready),
                    self.vout.hsync.eq(self.vin.hsync),
                    self.vout.vsync.eq(self.vin.vsync),
                    self.vout.de.eq(self.vin.de),
                    self.vout.r.eq(255), 
                    self.vout.g.eq(255), 
                    self.vout.b.eq(255)],
        })

# BaseSoC ------------------------------------------------------------------------------------------
class BaseSoC(SoCCore):
    interrupt_map = {
        "wbsdcard" : 4,
    }
    interrupt_map.update(SoCCore.interrupt_map)

    def __init__(self, toolchain="gowin", sys_clk_freq=48e6,
        with_led_chaser = False,
        with_rgb_led    = False,
        with_buttons    = True,
        with_video_terminal = False,
        with_framebuffer = False,
        with_wb_sdcard = False,
        **kwargs):

        platform = sipeed_tang_nano_20k.Platform(toolchain=toolchain)
        platform.toolchain.options["vhdl_std"] = "vhd2008"
        platform.toolchain.options["top_module"] = "sipeed_tang_nano_20k"
        
        test_io = [
            ("test_io", 0, Pins("J5:3"), IOStandard("LVCMOS33")),
            ("test_io", 1, Pins("J5:5"), IOStandard("LVCMOS33")),
        ]
        
        platform.add_extension(test_io)
        
        extra_reset = Signal()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq, reset=extra_reset)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Nano 20K", **kwargs)

        # TODO: XTX SPI Flash

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            class SDRAMPads:
                def __init__(self):
                    self.clk   = platform.request("O_sdram_clk")
                    self.cke   = platform.request("O_sdram_cke")
                    self.cs_n  = platform.request("O_sdram_cs_n")
                    self.cas_n = platform.request("O_sdram_cas_n")
                    self.ras_n = platform.request("O_sdram_ras_n")
                    self.we_n  = platform.request("O_sdram_wen_n")
                    self.dm    = platform.request("O_sdram_dqm")
                    self.a     = platform.request("O_sdram_addr")
                    self.ba    = platform.request("O_sdram_ba")
                    self.dq    = platform.request("IO_sdram_dq")
            sdram_pads = SDRAMPads()

            self.specials += DDROutput(0, 1, sdram_pads.clk, ClockSignal("sys"))

            self.sdrphy = GENSDRPHY(sdram_pads, sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = M12L64322A(sys_clk_freq, "1:1"), # FIXME.
                l2_cache_size = 128,
            )

        self.nes = NesInst(self, platform, sys_clk_freq)
        self.bus.add_master(master=self.nes.wb_rom, region=SoCRegion(origin=0x40000000, size=0x00800000))
        tp = platform.request_all("test_io")
        self.comb += [tp.eq(self.nes.testo),
        ]


        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("led_n"),
                sys_clk_freq = sys_clk_freq
            )
            
        if with_video_terminal:
            print("Adding hdmi output")
            self.videophy = VideoGowinHDMIPHY(platform.request("hdmi"), clock_domain="hdmi")
            self.add_nes_video_terminal(self.nes, phy=self.videophy, timings="1280x720@60Hz", clock_domain="hdmi")

        # RGB Led ----------------------------------------------------------------------------------
        if with_rgb_led:
            self.rgb_led = WS2812(
                pad          = platform.request("rgb_led"),
                nleds        = 2,
                sys_clk_freq = sys_clk_freq
            )
            self.bus.add_slave(name="rgb_led", slave=self.rgb_led.bus, region=SoCRegion(
                origin = 0x2000_0000,
                size   = 4,
            ))

        if with_wb_sdcard:
            self.sdcard = WbSdcard(self, platform, sys_clk_freq)

        # Buttons ----------------------------------------------------------------------------------
        if with_buttons:
            btn_pads = platform.request_all("btn")
            self.buttons = GPIOIn(pads=~btn_pads)
            self.comb += [
                extra_reset.eq(btn_pads[0]),
                self.crg.rst.eq(btn_pads[0])
            ]
            if not with_led_chaser:
                leds = platform.request_all("led_n")
                self.comb += leds[1].eq(btn_pads[0])

    def add_nes_video_terminal(self, nes, name="video_terminal", phy=None, timings="800x600@60Hz", clock_domain="sys"):
        from litex.soc.cores.video import VideoTimingGenerator, VideoTerminal
        from litex.soc.interconnect                  import stream
        # Video Timing Generator.
        self.check_if_exists(f"{name}_vtg")
        vtg = VideoTimingGenerator(default_video_timings=timings if isinstance(timings, str) else timings[1])
        vtg = ClockDomainsRenamer(clock_domain)(vtg)
        self.add_module(name=f"{name}_vtg", module=vtg)

        # Connect Video Terminal to Video PHY.
        #self.comb += vt.source.connect(phy if isinstance(phy, stream.Endpoint) else phy.sink)
        self.comb += vtg.source.connect(nes.vin)
        self.comb += nes.vout.connect(phy if isinstance(phy, stream.Endpoint) else phy.sink)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_20k.Platform, description="LiteX SoC on Tang Nano 20K.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=37.125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-video-terminal", action="store_true",    help="Enable Video Terminal (HDMI).")
    parser.add_target_argument("--with-rgb-led", action="store_true",    help="Enable RGB led.")
    parser.add_target_argument("--with-wb-sdcard", action="store_true", help="Enable SDCard support with a wishbone slave.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",            action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",                action="store_true", help="Enable SDCard support.")
    args = parser.parse_args()

    soc = BaseSoC(
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        with_video_terminal = args.with_video_terminal,
        with_rgb_led = args.with_rgb_led,
        with_wb_sdcard = args.with_wb_sdcard,
        **parser.soc_argdict
    )
    
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    builder.add_external_software_package("libwbsdcard", SoftwareWbsdcard, cmd_srcs=["groot.o"])
    builder.add_software_library("libwbsdcard")
    builder.add_external_software_package("libnes", SoftwareNes)
    builder.add_software_library("libnes")
    builder.add_json(os.path.join(SoftwareNes, "whatever.json"))
    
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()
