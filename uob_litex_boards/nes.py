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