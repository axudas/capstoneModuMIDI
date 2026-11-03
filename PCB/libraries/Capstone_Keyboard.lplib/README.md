# Capstone Keyboard – LibrePCB library

Format: LibrePCB **2.x** (file format "2", same as the current official libraries).
Depends on: **LibrePCB Base** (for categories and the GND/VCC supply symbols you'll use in schematics).

## Install
1. Unzip so you have a folder named `Capstone_Keyboard.lplib`.
2. LibrePCB → Control Panel → **Library Manager → Add Library → Local Library** and point it at that folder
   (or copy it into `<workspace>/data/libraries/local/`).
3. Make sure "LibrePCB Base" is installed too.

## What's inside (8 devices)

| Device | Footprint | Notes |
|---|---|---|
| Adafruit Metro RP2350 (Shield Headers) | Arduino Uno R3 shield headers + 4× M3 holes | For a shield that plugs on top of the Metro. 3.3 V logic. |
| NULLLAB 2.0in ST7789 Display (1x06 Header) | 1×6 2.54 mm header | Mates with the supplied GH1.25→Dupont cable. Pins: G, V, SCL, SDA, DC, CS. |
| EC11 Rotary Encoder With Switch (WWZMDiB) | Alps EC11E vertical | A/C/B + S1/S2, lugs on 2.6 mm holes. |
| Omron B3F-5050 | B3F 12×12, 12.5×5.0 mm grid + 2× Ø1.8 boss holes | B32-1260 cap is mechanical only. |
| CUI PJ-102AH (for MEAN WELL GST60A12) | PJ-102AH THT | 5.5/2.1 mm, centre-positive. Optional – the adapter can plug straight into the Metro. |
| Hall Effect Sensor SS49E / 49E (TO-92, Through-Hole) | TO-92: **Lying Flat (under key switch)**, Upright Wide 2.54 mm, Upright 1.27 mm | **Hand-solderable hall sensor.** Pinout 1=VCC 2=GND 3=OUT (branded face). Lay it flat, branded face up, centred under the magnet. |
| Hall Effect Sensor DRV5055 (SOT-23, SMD) | SOT-23-3 | Surface-mount alternative. Pinout 1=VCC 2=OUT 3=GND. |
| MX-Style Magnetic Key Switch | Peg holes ±5.08 mm; variants "Center Post" / "No Center Post" | Mechanical only, pair with a hall sensor. |

## Check before you order boards
- **Metro D22/D23** are drawn where an Uno has D12/D13. Check this against the Metro silkscreen.
- **Display cable colours:** check them against the module's G/V/SCL/SDA/DC/CS silkscreen.
- **Hall sensor position:** the origin of the TO-92 "Lying Flat" footprint (and of the SOT-23) is the sensor centre. Put it under your switch's magnet, as given in your switch's datasheet.
  If the sensor sits at the switch centre, use the "No Center Post" footprint.
- Print the footprints 1:1 on paper and push the real parts through it.

## Design notes
- The Metro has only **6 ADC inputs (A0–A5)**. For more than 6 hall keys, use analog multiplexers
  (e.g. CD74HC4067, 16:1). Six of them cover up to 96 keys.
- Power the hall sensors from **3V3**, not 5 V, so their outputs never exceed the RP2350 ADC range.
  Put a 100 nF capacitor at each sensor.
- DRV5055A4: about ±170 mT range, so it won't saturate with Gateron KS-20 magnets (~90 mT at bottom-out).
  A3 gives twice the resolution but can clip near bottom-out. Both are bipolar, so either magnet pole works.
- Display SPI: D22 = SPI0 SCK and D23 = SPI0 MOSI on the Metro. Any free GPIO works for DC and CS.
