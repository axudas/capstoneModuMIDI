# moduMidi: bank board (KiCad)

The **bank board** of the ModuMIDI 2 hall-effect keyboard: one board per bank, 30 keys, with its own RP2350. Open `moduMidi.kicad_pro` in KiCad 10. Parts come from `../kicad-library/Capstone_Keyboard` (already set up in this project's library tables) and the standard KiCad libraries.

## Schematic

Six sheets. They connect through global labels and power symbols, so a net has the same name on every sheet.

| Sheet | File | What's on it |
|---|---|---|
| Root | `moduMidi.kicad_sch` | 30 DRV5055 hall sensors with one 100 nF each |
| MCU | `bank_mcu.kicad_sch` | RP2350A with its flash, crystal, core regulator, boot/run buttons, SWD and USB service connectors |
| Power | `bank_power.kicad_sch` | Inter-bank connectors, 12 V → 5 V buck, two 3.3 V LDOs, power-good LEDs, rail monitors |
| Muxes | `bank_mux.kicad_sch` | Four CD74HC4067 analog multiplexers |
| Key links | `bank_keys.kicad_sch` | LED data buffer and one connector per key (LED chain + key presence) |
| Bus | `bank_bus.kicad_sch` | RS-485 transceiver, termination jumper, bank address jumpers |

**Numbering:** sensor n is Un, its capacitor C1nn, its presence pull-up R1nn and its key connector J1nn (for example key 7: U7, C107, R107, J107).

### Power rails

| Rail | From | Feeds |
|---|---|---|
| +12V | Inter-bank connector J3, passed on through J4 | Buck, rail monitor |
| +5V | U33 buck (3 A) | Key LEDs, LED buffer, both LDOs |
| +3V3 | U34 LDO | RP2350 IO, flash, RS-485 |
| +3.3VA | U35 LDO behind ferrite bead FB1 | 30 sensors, 4 muxes, RP2350 ADC (ADC_AVDD) |
| +1V1 | RP2350's own core regulator (L1) | RP2350 core (DVDD) |

### RP2350A pins used

| GPIO | Net | Use |
|---|---|---|
| 0 / 1 / 2 | BUS_TX / BUS_RX / BUS_DE | UART0 to the RS-485 transceiver |
| 3 / 4 | BANK_ID0 / BANK_ID1 | Bank address jumpers (internal pull-ups) |
| 6–9 | MUX_S0–S3 | Select lines, shared by all four muxes |
| 10 | LED_DATA | Key LED chain (through the 5 V buffer) |
| 25 | STATUS_LED | Status LED D1 |
| 26 / 27 | ADC_KEY_A / ADC_KEY_B | Key sensors 1–15 / 16–30 |
| 28 / 29 | ADC_DET_A / ADC_DET_B | Key presence 1–15 / 16–30 |

GPIO5 and GPIO11–24 are unused (no-connect flags).

## Parts list

### Root: sensors
| Ref | Part | Why |
|---|---|---|
| U1–U30 | DRV5055A4QDBZR, SOT-23 | One linear hall sensor under each switch. The A3 fits the same footprint if the bench test picks it. |
| C101–C130 | 100 nF 0402 | Decoupling right at each sensor. |

### MCU (from Raspberry Pi's RP2350A minimal design)
| Ref | Part | Why |
|---|---|---|
| U31 | RP2350A, QFN-60 | The bank's own controller (notebook p. 28). Scans the 30 keys through the muxes and reports to the head unit. |
| U32 | W25Q128JVS QSPI flash, SOIC-8 | Program storage; the RP2350 has no internal flash. A smaller W25Q16/W25Q32 works too. |
| Y1, C2, C3, R1 | 12 MHz ABM8-272-T3, 2 × 15 pF, 1 kΩ | Clock crystal with load caps; R1 limits drive, as in the reference design. |
| L1 | 3.3 µH, 2016, polarised | Core-regulator inductor (VREG_LX → +1V1). Keep the footprint's dot orientation. |
| R2, C4 | 33 Ω, 4.7 µF | Filter for VREG_AVDD. |
| C5–C9 | 4.7 µF × 4, 100 nF × 2 | VREG_VIN and +1V1 (DVDD) decoupling. |
| C10–C17, C18 | 100 nF × 8, 10 µF | One per IOVDD / QSPI_IOVDD / USB_OTP_VDD pin, plus bulk. |
| C19 | 100 nF | ADC_AVDD (on +3.3VA). |
| C1 | 100 nF | Flash decoupling. |
| SW1, R3 | Push button, 1 kΩ | BOOTSEL: hold while resetting to get the USB bootloader. |
| SW2, R4 | Push button, 1 kΩ | RUN (reset). |
| J1 | JST SH 3-pin | Raspberry Pi debug connector (SWD) for the Debug Probe. |
| J2, R5, R6 | JST SH 4-pin, 2 × 27 Ω | USB service port for bench bring-up and UF2 flashing. Pin 1 (VBUS) isn't used. |
| D1, R7 | LED, 1 kΩ | Status LED on GPIO25. |

### Power
| Ref | Part | Why |
|---|---|---|
| J3 / J4 | 2 × 6, 2.54 mm SMD socket / header | Inter-bank connector in and out (notebook p. 28: 12 pins, 12 V and return on several pins each, bus pair). SMD on the bottom side so no pins come up into the switches; placeholder footprints until the blind-mate header is chosen. |
| D2 | SMAJ15A TVS | Clamps 12 V spikes when a bank is plugged in live. |
| C20 | 47 µF 25 V electrolytic | Damps the ringing of the cable inductance on hot-plug. |
| C21–C23 | 2 × 10 µF 25 V, 100 nF | Buck input capacitors. |
| U33 | TPS54302, SOT-23-6 | 12 V → 5 V buck, 3 A. Local regulation per bank (notebook p. 22): a worn connector loses volts, not LED brightness. |
| R8, R9 | 100 kΩ, 20 kΩ | Enable divider: the buck starts above about 7 V and EN stays at 2 V. |
| C24 | 100 nF | Bootstrap capacitor. |
| L2 | 10 µH, Bourns SRN6045TA | Buck inductor. |
| R10, R11 | 100 kΩ, 13.3 kΩ | Feedback divider: 0.596 V × (1 + 100/13.3) = 5.08 V. |
| C25–C27 | 2 × 22 µF 10 V, 100 µF 10 V electrolytic | Buck output and LED-rail reservoir. |
| U34, C28, C29 | AP2112K-3.3, 1 µF, 10 µF | +3V3 digital LDO. |
| FB1 | Ferrite bead, 600 Ω at 100 MHz, 0805 | Keeps buck ripple and LED current off the analog LDO. |
| U35, C30–C32 | AP7361C-33E (SOT-223), 2 × 10 µF, 100 nF | +3.3VA analog LDO: sensors, muxes, ADC (about 0.2–0.3 A). |
| D3–D6, R12–R15 | Green 0603 LEDs, 10 k / 2.2 k / 1 k / 1 kΩ | Power-good LED on every rail (notebook p. 42). |
| R16, R17, C33 | 100 kΩ, 27 kΩ, 100 nF | V12_SENSE: 12 V monitor, reads up to 15.5 V (notebook p. 23). |
| R18, R19, C34 | 100 kΩ, 100 kΩ, 100 nF | V5_SENSE: 5 V monitor. |

### Muxes
| Ref | Part | Why |
|---|---|---|
| U36, U37 | CD74HC4067M | Keys 1–15 and 16–30 into ADC0/ADC1. Channel 15 carries V12_SENSE / V5_SENSE. |
| U38, U39 | CD74HC4067M | Presence 1–15 and 16–30 into ADC2/ADC3. Channel 15 is tied to GND as a zero check. |
| C35–C38 | 100 nF | Mux decoupling. |

All four share MUX_S0–S3, so one select step reads key n, key n+15 and both presence lines.

### Key links
| Ref | Part | Why |
|---|---|---|
| U40 | 74AHCT1G125, SOT-23-5 | Re-drives the 3.3 V LED data at 5 V for the WS2812 chain (notebook p. 23). |
| C39, R20, R21 | 100 nF, 10 kΩ pull-down, 330 Ω | Decoupling; keeps LED data low while the RP2350 boots; series resistor at the chain input. |
| J101–J130 | 5-pin connector per key | Key-base link: 1 +5V, 2 GND, 3 LED DIN, 4 LED DOUT, 5 DET. The LED sits in the key base (Tier 1) and two pogo pins report whether the cap is on (notebook p. 29). JST SH footprint is a placeholder until the key-base wiring is chosen. |
| R101–R130 | 10 kΩ | Pull DET up to +3.3VA: high = cap off, low = cap on. |
| TP1 | Test pad | End of the LED chain (LED_CH31). |

### Bus
| Ref | Part | Why |
|---|---|---|
| U41 | MAX3485, SOIC-8 | 3.3 V half-duplex RS-485 on the connector's bus pair; robust over the bank chain. |
| C40 | 100 nF | Decoupling. |
| R22 | 10 kΩ | Holds DE low (receive) while the RP2350 boots. |
| JP1, R23 | Solder jumper, 120 Ω | Bus termination: close on the last bank only. |
| JP2, JP3 | Solder jumpers | Bank address 0–3, like the 2023 boards' solder bridges. |

### Removed
- **J1 DC jack:** the 12 V supply plugs into the head unit and reaches the banks over the inter-bank connector (notebook p. 28), so banks don't need their own jack.

### Not added, and why
- **Op-amp buffer and separate analog ground return** (notebook p. 23): these were for sending analog signals to the head unit. With an RP2350 on every bank the analog path stays on the board.
- **Reverse-polarity FET and fuse** (notebook p. 21): they belong at the head unit's 12 V input, where the supply plugs in.

## Board

- **Outline:** the bank outline (one step each way: tab on the left, notch on the right; side edges and steps inset 0.25 mm) trimmed front and back to the smallest band that holds the 30 sensors and 6 mounting holes (+1 mm). **239.53 × 104.18 mm**, outer corners R3, step corners R1.
  - Boards tile with a 0.5 mm gap, and each board stays inside its own bank's footprint (black column 1's sensor sits in the tab).
  - The full plate outline and its dimensions are on the **Bank.Outline** layer (User.1), for reference.
- **U1–U30** sit at the switch centres (footprint origin = sensor centre, under the magnet) and are linked to the schematic symbols. Key pitch 22.86 mm, rows 48.90 mm apart.
- **H1–H6:** M2 holes (`MountingHole_2.2mm_M2`, NPTH, board-only) in the white and grey rows, between the switches at black columns 2, 6 and 10. Each is 2.2 mm clear of the neighbouring switch cut-outs.
- **F.SilkS:** the key-cap layout, clipped to the board and kept off the holes. **F.Fab:** 14 mm switch outlines and 14 × 7 mm stabilizer-housing outlines.
- Dimensions are on User.Drawings, notes on User.Comments.
- **All 214 parts are placed; nothing is routed yet.** DRC: 0 errors (only the unrouted connections).
- **Top side** (faces the plate, about 3.5 mm of foam): only the low parts that belong to each key, kept clear of every switch and stabilizer cut-out.
  - U1–U30 at the switch centres, C1nn 3.3 mm beside its sensor (on the VCC side; column 10 on the other side, clear of the designator).
  - J101–J130, one key connector per key, in the gap between the switch and its stabilizer, inside the key's own footprint: white keys behind the switch, black and grey keys in front of it.
- **Bottom side:** everything else, in blocks.
  - **J3** (bank in) under the left tab and **J4** (bank out) by the right notch, so neighbouring banks' connectors face each other.
  - **Power** next to J3: D2, C20–C23, the buck (U33, L2, C24–C27), both LDOs (U34, FB1, U35), the power-good LEDs D3–D6.
  - **Muxes** U36/U37 left of the MCU and U38/U39 right of it, with the rail-monitor dividers R16–R19 under U36/U37.
  - **MCU** in the middle: U31 with its decoupling ring, L1/R2/C4, flash U32 behind it, crystal Y1 beside it, the LED buffer U40 next to it.
  - **Debug row** along the back edge: SW1 BOOTSEL, SW2 RUN, J1 SWD, J2 USB, status LED D1.
  - **Bus** next to J4: U41, termination JP1/R23, address jumpers JP2/JP3.
  - R1nn (key-presence pull-ups) directly under their key connectors.
- Designators of the new parts are on the fab layers, because the key-cap layout fills F.SilkS.

## Open questions

- The inner stabilizer housings sit over the board. They need cut-outs in the board or enough height between plate and board.
- **Stabilizer bar:** the plate now has the low-profile stabilizer's wire slot (bar 9.5 mm to the left of each key's switch, to the right on column 1), and the bar and arms swing down into the foam gap when a key is pressed. H1–H6 sit on bar lines and need to move; no other top-side part is in a bar or arm zone. F.Fab still shows the old 14 × 7 mm housings.
- Key-base wiring (flex or wires) and the blind-mate inter-bank header: both have placeholder footprints.
- RS-485 is this schematic's reading of the notebook's "bus pair"; the head unit needs the matching transceiver and fail-safe bias resistors.
- DRV5055 A3 or A4: decided by the magnet and travel bench test.
- Run ERC in KiCad 10 (the schematic's connections were checked against a netlist export).
