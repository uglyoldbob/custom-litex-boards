# Template from litex-boards crosslink nx vip board
#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2020 David Corrigan <davidcorrigan714@gmail.com>
# Copyright (c) 2020 Alan Green <avg@google.com>
# Copyright (c) 2020 David Shah <dave@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticeNexusPlatform
from litex.build.lattice.programmer import LatticeProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clock", 0, Pins("C14"), IOStandard("LVCMOS33")),
    ("refclock", 0, Pins("M5"), IOStandard("LVCMOS33")),
    ("refclock", 1, Pins("N11"), IOStandard("LVCMOS33")),
    ("refclock", 2, Pins("N14"), IOStandard("LVCMOS33")),
    ("reset", 0, Pins("H16"), IOStandard("LVCMOS33")),
    ("interrupt", 0, Pins("D7"), IOStandard("LVCMOS33")),
    ("interrupt", 1, Pins("D6"), IOStandard("LVCMOS33")),
    ("interrupt", 2, Pins("D4"), IOStandard("LVCMOS33")),
    ("serial", 0,
        Subsignal("rx", Pins("A16"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("B16"), IOStandard("LVCMOS33")),
    ),
    
    ("user_led", 0, Pins("G17"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("H17"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("H15"), IOStandard("LVCMOS33")),
    
    ("hdmi",
        Subsignal("hpd", Pins("E16"), IOStandard("LVCMOS33")),
        Subsignal("scl", Pins("D5"), IOStandard("LVCMOS33")),
        Subsignal("sda", Pins("D17"), IOStandard("LVCMOS33")),
        Subsignal("cec", Pins("E15"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("E7"), IOStandard("LVCMOS33")),
        Subsignal("clk_n", Pins("E6"), IOStandard("LVCMOS33")),
        Subsignal("data0_p", Pins("E5"), IOStandard("LVCMOS33")),
        Subsignal("data1_p", Pins("F7"), IOStandard("LVCMOS33")),
        Subsignal("data2_p", Pins("H3"), IOStandard("LVCMOS33")),
        Subsignal("data0_n", Pins("E4"), IOStandard("LVCMOS33")),
        Subsignal("data1_n", Pins("F6"), IOStandard("LVCMOS33")),
        Subsignal("data2_n", Pins("H4"), IOStandard("LVCMOS33")),
    ),
    
    ("jtag",
        Subsignal("tms", Pins("E13"), IOStandard("LVCMOS33")),
        Subsignal("tdi", Pins("E12"), IOStandard("LVCMOS33")),
        Subsignal("tdo", Pins("E11"), IOStandard("LVCMOS33")),
        Subsignal("tck", Pins("F12"), IOStandard("LVCMOS33")),
    ),
    
    ("pcie", 0,
        Subsignal("rx_p", Pins("A13"), IOStandard("LVCMOS33")),
        Subsignal("rx_n", Pins("A14"), IOStandard("LVCMOS33")),
        Subsignal("tx_p", Pins("A11"), IOStandard("LVCMOS33")),
        Subsignal("tx_n", Pins("A10"), IOStandard("LVCMOS33")),
        Subsignal("refclk_p", Pins("A8"), IOStandard("LVCMOS33")),
        Subsignal("refclk_n", Pins("B8"), IOStandard("LVCMOS33")),
        Subsignal("wake_n", Pins("D12"), IOStandard("LVCMOS33")),
        Subsignal("perst_n", Pins("D16"), IOStandard("LVCMOS33")),
        Subsignal("tck", Pins("F12"), IOStandard("LVCMOS33")),
        Subsignal("tdi", Pins("E12"), IOStandard("LVCMOS33")),
        Subsignal("tdo", Pins("E11"), IOStandard("LVCMOS33")),
        Subsignal("tms", Pins("E13"), IOStandard("LVCMOS33")),
        Subsignal("present_n", Pins("B17"), IOStandard("LVCMOS33")),
        Subsignal("smbus_clk", Pins("C16"), IOStandard("LVCMOS33")),
        Subsignal("smbus_data", Pins("C17"), IOStandard("LVCMOS33")),
        Subsignal("rext", Pins("C12"), IOStandard("LVCMOS33")),
        Subsignal("refret", Pins("B12"), IOStandard("LVCMOS33")),
        Subsignal("aux_power", Pins("C13"), IOStandard("LVCMOS33")),
    ),

    # MIPI camera modules
    # Note that use of MIPI_DPHY standard for + and LVCMOS12H for - is copied from Lattice PDC
    # MIPI pins are unconstrained to work around a Radiant 2.0 bug
    ("camera", 0,
        Subsignal("clkp", Pins("X")),
        Subsignal("clkn", Pins("X")),
        Subsignal("dp", Pins("X X X X")),
        Subsignal("dn", Pins("X X X X")),
    ),
    ("camera", 1,
        Subsignal("clkp", Pins("X")),
        Subsignal("clkn", Pins("X")),
        Subsignal("dp", Pins("X X X X")),
        Subsignal("dn", Pins("X X X X")),
    ),
    ("camera", 2,
        Subsignal("clkp", Pins("D1"), IOStandard("MIPI_DPHY")),
        Subsignal("clkn", Pins("E2"), IOStandard("LVCMOS12H")),
        Subsignal("dp", Pins("E1 C1 F1 B1"), IOStandard("MIPI_DPHY")),
        Subsignal("dn", Pins("F2 D2 G2 C2"), IOStandard("LVCMOS12H")),
    ),
    ("camera", 3,
        Subsignal("clkp", Pins("A4"), IOStandard("MIPI_DPHY")),
        Subsignal("clkn", Pins("B4"), IOStandard("LVCMOS12H")),
        Subsignal("dp", Pins("A3 A5 A2 A6"), IOStandard("MIPI_DPHY")),
        Subsignal("dn", Pins("B3 B5 B2 B6"), IOStandard("LVCMOS12H")),
    ),
    ("camera", 4,
        Subsignal("clkp", Pins("T1"), IOStandard("MIPI_DPHY")),
        Subsignal("clkn", Pins("R1"), IOStandard("LVCMOS12H")),
        Subsignal("dp", Pins("T2 R2 T3 N12"), IOStandard("MIPI_DPHY")),
        Subsignal("dn", Pins("U2 R2 U3 N13"), IOStandard("LVCMOS12H")),
    ),
    
    ("i2s_quad", 0,
        Subsignal("sck", Pins("H13"), IOStandard("LVCMOS33")),
        Subsignal("ws", Pins("H14"), IOStandard("LVCMOS33")),
        Subsignal("data", Pins("H11 H12 J11 J10"), IOStandard("LVCMOS33")),
    ),
    ("i2s_quad", 1,
        Subsignal("sck", Pins("J13"), IOStandard("LVCMOS33")),
        Subsignal("ws", Pins("J12"), IOStandard("LVCMOS33")),
        Subsignal("data", Pins("J15 J14 J17 J16"), IOStandard("LVCMOS33")),
    ),
    ("i2s_quad", 2,
        Subsignal("sck", Pins("K17"), IOStandard("LVCMOS33")),
        Subsignal("ws", Pins("K16"), IOStandard("LVCMOS33")),
        Subsignal("data", Pins("K11 K10 L11 L10"), IOStandard("LVCMOS33")),
    ),
    
    ("i2c", 0,
        Subsignal("scl", Pins("L13"), IOStandard("LVCMOS33")),
        Subsignal("sda", Pins("L12"), IOStandard("LVCMOS33")),
    ),
]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticeNexusPlatform):
    default_clk_name   = "clk12"
    default_clk_period = 1e9/12e6

    def __init__(self, device="LIFCL", toolchain="radiant", **kwargs):
        assert device in ["LIFCL"]
        LatticeNexusPlatform.__init__(self, device + "-40-7MG289C", _io, _connectors, toolchain=toolchain, **kwargs)

    def create_programmer(self, mode = "direct"):
        assert mode in ["direct","flash"]

        xcf_template_direct = """<?xml version='1.0' encoding='utf-8' ?>
<!DOCTYPE       ispXCF  SYSTEM  "IspXCF.dtd" >
<ispXCF version="R1.2.0">
    <Comment></Comment>
    <Chain>
        <Comm>JTAG</Comm>
        <Device>
            <SelectedProg value="TRUE"/>
            <Pos>1</Pos>
            <Vendor>Lattice</Vendor>
            <Family>LIFCL</Family>
            <Name>LIFCL-40</Name>
            <IDCode>0x010f1043</IDCode>
            <Package>All</Package>
            <PON>LIFCL-40</PON>
            <Bypass>
                <InstrLen>8</InstrLen>
                <InstrVal>11111111</InstrVal>
                <BScanLen>1</BScanLen>
                <BScanVal>0</BScanVal>
            </Bypass>
            <File>{bitstream_file}</File>
            <JedecChecksum>N/A</JedecChecksum>
            <MemoryType>Static Random Access Memory (SRAM)</MemoryType>
            <Operation>Fast Configuration</Operation>
            <Option>
                <SVFVendor>JTAG STANDARD</SVFVendor>
                <IOState>HighZ</IOState>
                <PreloadLength>362</PreloadLength>
                <IOVectorData>0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF</IOVectorData>
                <Usercode>0x00000000</Usercode>
                <AccessMode>Direct Programming</AccessMode>
            </Option>
        </Device>
    </Chain>
    <ProjectOptions>
        <Program>SEQUENTIAL</Program>
        <Process>ENTIRED CHAIN</Process>
        <OperationOverride>No Override</OperationOverride>
        <StartTAP>TLR</StartTAP>
        <EndTAP>TLR</EndTAP>
        <VerifyUsercode value="FALSE"/>
        <TCKDelay>3</TCKDelay>
    </ProjectOptions>
    <CableOptions>
        <CableName>USB2</CableName>
        <PortAdd>FTUSB-0</PortAdd>
    </CableOptions>
</ispXCF>
"""

        xcf_template_flash = """<?xml version='1.0' encoding='utf-8' ?>
<!DOCTYPE       ispXCF  SYSTEM  "IspXCF.dtd" >
<ispXCF version="R1.2.0">
    <Comment></Comment>
    <Chain>
        <Comm>JTAG2SPI</Comm>
        <Device>
            <SelectedProg value="TRUE"/>
            <Pos>1</Pos>
            <Vendor>Lattice</Vendor>
            <Family>LIFCL</Family>
            <Name>LIFCL-40</Name>
            <Package>All</Package>
            <Bypass>
                <InstrLen>8</InstrLen>
                <InstrVal>11111111</InstrVal>
                <BScanLen>1</BScanLen>
                <BScanVal>0</BScanVal>
            </Bypass>
            <File>{bitstream_file}</File>
            <MemoryType>External SPI Flash Memory (SPI FLASH)</MemoryType>
            <Operation>Erase,Program,Verify</Operation>
            <Option>
                <SVFVendor>JTAG STANDARD</SVFVendor>
                <Usercode>0x00000000</Usercode>
                <AccessMode>Direct Programming</AccessMode>
            </Option>
            <FPGALoader>
            <CPLDDevice>
                <Device>
                    <Pos>1</Pos>
                    <Vendor>Lattice</Vendor>
                    <Family>LIFCL</Family>
                    <Name>LIFCL-40</Name>
                    <IDCode>0x010f1043</IDCode>
                    <Package>All</Package>
                    <PON>LIFCL-40</PON>
                    <Bypass>
                        <InstrLen>8</InstrLen>
                        <InstrVal>11111111</InstrVal>
                        <BScanLen>1</BScanLen>
                        <BScanVal>0</BScanVal>
                    </Bypass>
                    <MemoryType>Static Random Access Memory (SRAM)</MemoryType>
                    <Operation>Refresh Verify ID</Operation>
                    <Option>
                        <SVFVendor>JTAG STANDARD</SVFVendor>
                        <IOState>HighZ</IOState>
                        <PreloadLength>362</PreloadLength>
                        <IOVectorData>0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF</IOVectorData>
                        <AccessMode>Direct Programming</AccessMode>
                    </Option>
                </Device>
            </CPLDDevice>
            <FlashDevice>
                <Device>
                    <Pos>1</Pos>
                    <Vendor>Macronix</Vendor>
                    <Family>SPI Serial Flash</Family>
                    <Name>MX25L12833F</Name>
                    <IDCode>0x18</IDCode>
                    <Package>8-pin SOP</Package>
                    <Operation>Erase,Program,Verify</Operation>
                    <File>{bitstream_file}</File>
                    <AddressBase>0x00000000</AddressBase>
                    <EndAddress>0x000F0000</EndAddress>
                    <DeviceSize>128</DeviceSize>
                    <DataSize>1016029</DataSize>
                    <NumberOfDevices>1</NumberOfDevices>
                    <ReInitialize value="FALSE"/>
                </Device>
            </FlashDevice>
            <FPGADevice>
                <Device>
                    <Pos>1</Pos>
                    <Name></Name>
                    <File>{bitstream_file}</File>
                    <LocalChainList>
                        <LocalDevice index="-99"
                            name="Unknown"
                            file="{bitstream_file}"/>
                    </LocalChainList>
                    <Option>
                        <SVFVendor>JTAG STANDARD</SVFVendor>
                    </Option>
                </Device>
            </FPGADevice>
            </FPGALoader>
        </Device>
    </Chain>
    <ProjectOptions>
        <Program>SEQUENTIAL</Program>
        <Process>ENTIRED CHAIN</Process>
        <OperationOverride>No Override</OperationOverride>
        <StartTAP>TLR</StartTAP>
        <EndTAP>TLR</EndTAP>
        <DisableCheckBoard value="TRUE"/>
        <VerifyUsercode value="FALSE"/>
        <TCKDelay>3</TCKDelay>
    </ProjectOptions>
    <CableOptions>
        <CableName>USB2</CableName>
        <PortAdd>FTUSB-0</PortAdd>
        <USBID>Lattice ECP5 VIP Processor Board 0000 Serial FT4RXXZ5</USBID>
    </CableOptions>
</ispXCF>
"""

        if mode == "direct":
            xcf_template = xcf_template_direct
        if mode == "flash":
            xcf_template = xcf_template_flash

        return LatticeProgrammer(xcf_template)




