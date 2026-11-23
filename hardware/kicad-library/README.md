# Capstone Keyboard – KiCad library

- **Symbols:** `Capstone_Keyboard.kicad_sym`
- **Footprints:** `Capstone_Keyboard.pretty/`
- **Format:** KiCad 7 or newer (KiCad 10 opens it and upgrades it when you save).

The two KiCad projects in this repo (`hardware/bank-board` and `hardware/key-prototype/pcb`) already list this library in their own `sym-lib-table` / `fp-lib-table`, so it works as soon as you open them. To use it in another project:

1. Go to **Preferences → Manage Symbol Libraries → Project Specific Libraries**, then **+**.
2. Set the nickname to `Capstone_Keyboard` and the path to this folder's `Capstone_Keyboard.kicad_sym`.
3. Do the same under **Manage Footprint Libraries**, with `Capstone_Keyboard.pretty`.

The nickname must be exactly `Capstone_Keyboard`, because the symbols refer to their footprints as `Capstone_Keyboard:<name>`.

## Symbols (9)

| Symbol | Default footprint | Notes |
|---|---|---|
| `Hall_SS49E_TO-92` | `Hall_TO-92_LyingFlat` | Through-hole hall sensor (SS49E / 49E / DRV5055 LPG), used on the hand-built key prototype. Pinout 1=VCC 2=GND 3=OUT, branded face. Lay it flat, branded face up, centred under the magnet. Other footprints: `Hall_TO-92_Upright_P2.54mm`, `Hall_TO-92_Upright_P1.27mm`. |
| `Hall_DRV5055_SOT-23` | `Hall_SOT-23-3` | **Used on the bank board: pick-and-place DRV5055A4QDBZR.** Pinout 1=VCC 2=OUT 3=GND. |
| `MX_Magnetic_Switch` | `MX_Magnetic_NoCenterPost` | Mechanical only (two peg holes at ±5.08 mm). Pair it with a hall sensor. `MX_Magnetic_CenterPost` adds the Ø4 mm centre hole. |
| `CUI_PJ-102AH` | `CUI_PJ-102AH` | 5.5/2.1 mm barrel jack, centre-positive (for the MEAN WELL GST60A12). |
| `EC11_Encoder_Switch` | `EC11_Encoder_Switch_Vertical` | A/C/B + S1/S2. The mounting lugs MP1/MP2 are footprint-only pads. |
| `Omron_B3F-5050` | `Omron_B3F-5050_12x12mm` | 12 × 12 mm tactile switch. The B32-1260 cap is mechanical only. |
| `ST7789_Display_1x06` | `PinHeader_1x06_P2.54mm_ST7789` | 2.0" ST7789 SPI display module on the head unit (G, V, SCL, SDA, DC, CS; RES and BLK are tied high on the module). |
| `Adafruit_Metro_RP2350` | `Adafruit_Metro_RP2350_ShieldHeaders` | The head-unit controller (Uno-shaped shield headers + 4 × M3). |
| `RP2350A_QFN-60` | `RP2350-QFN-60-1EP_7x7_P0.4mm_EP3.4x3.4mm_ThermalVias` | **The per-bank microcontroller.** Symbol, footprint and 3D model (`Capstone_Keyboard.3dshapes/RP2350_QFN60.step`) from Raspberry Pi's RP2350A minimal design (RP-006440). Needs the QSPI flash, 12 MHz crystal and core-regulator inductor from that design; see `hardware/bank-board`. |

## Extra footprints

| Footprint | Use |
|---|---|
| `L_pol_2016` | 2016 polarised inductor for the RP2350 core regulator (Abracon AOTA-B201610 series, 3.3 µH). The dot orientation matters. From Raspberry Pi's minimal design. |
| `Stabilizer_Cherry_PCB_Holes` | The 3.05 mm and 4.0 mm NPTH holes for one Cherry stabilizer. Place one on each side of the switch: ±19.05 mm for a 3u key (turned 90° when the key runs front to back), ±50 mm for a 6.25u spacebar. It fits PCB-mount stabs and clears plate-mount ones. |

## Check before you order boards

- **Hall sensor position:** the footprint origin is the sensor centre. Put it under your switch's magnet, as given in your switch's datasheet. If it sits at the switch centre, use `MX_Magnetic_NoCenterPost`.
- **Fit check:** print the footprints 1:1 on paper and push the real parts through.

## Design notes

- **Sensor supply:** power the hall sensors from **3V3**, so their outputs stay inside the ADC range. Put a 100 nF capacitor at each sensor.
- **DRV5055 grade:** the DRV5055A4 covers about ±170 mT, so it won't saturate with Gateron KS-20 magnets (about 90 mT at bottom-out). The A3 gives twice the resolution but can clip near bottom-out. Both are bipolar, so either magnet pole works.
- **Bank ADC:** the RP2350A has four ADC inputs (GPIO26–29). The bank board puts the 30 sensors and 30 key-presence lines through four CD74HC4067 16:1 multiplexers, one per ADC pin. See `hardware/bank-board/README.md`.
