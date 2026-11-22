# Capstone Keyboard – KiCad library

- **Symbols:** `Capstone_Keyboard.kicad_sym`
- **Footprints:** `Capstone_Keyboard.pretty/`
- **Format:** KiCad 7. It opens in KiCad 7, 8 and 9, and newer versions upgrade it when you save.
- **Origin:** converted on 2026-11-17 from the earlier LibrePCB library (`Capstone_Keyboard.lplib`). Pad numbers, pinouts and footprint origins are unchanged.

The two KiCad projects in this repo (`PCB/moduMidi` and `spacebar-prototype/pcb/spacebarHall`) already list this library in their own `sym-lib-table` / `fp-lib-table`, so it works as soon as you open them. To use it in another project:

1. Go to **Preferences → Manage Symbol Libraries → Project Specific Libraries**, then **+**.
2. Set the nickname to `Capstone_Keyboard` and the path to this folder's `Capstone_Keyboard.kicad_sym`.
3. Do the same under **Manage Footprint Libraries**, with `Capstone_Keyboard.pretty`.

The nickname must be exactly `Capstone_Keyboard`, because the symbols refer to their footprints as `Capstone_Keyboard:<name>`.

## Symbols (8)

| Symbol | Default footprint | Notes |
|---|---|---|
| `Hall_SS49E_TO-92` | `Hall_TO-92_LyingFlat` | **Hand-solderable hall sensor** (SS49E / 49E / DRV5055 LPG). Pinout 1=VCC 2=GND 3=OUT, branded face. Lay it flat, branded face up, centred under the magnet. Other footprints: `Hall_TO-92_Upright_P2.54mm`, `Hall_TO-92_Upright_P1.27mm`. |
| `Hall_DRV5055_SOT-23` | `Hall_SOT-23-3` | Surface-mount alternative. Pinout 1=VCC 2=OUT 3=GND. |
| `MX_Magnetic_Switch` | `MX_Magnetic_NoCenterPost` | Mechanical only (two peg holes at ±5.08 mm). Pair it with a hall sensor. `MX_Magnetic_CenterPost` adds the Ø4 mm centre hole. |
| `CUI_PJ-102AH` | `CUI_PJ-102AH` | 5.5/2.1 mm barrel jack, centre-positive (for the MEAN WELL GST60A12). |
| `EC11_Encoder_Switch` | `EC11_Encoder_Switch_Vertical` | A/C/B + S1/S2. The mounting lugs MP1/MP2 are footprint-only pads. |
| `Omron_B3F-5050` | `Omron_B3F-5050_12x12mm` | 12 × 12 mm tactile switch. The B32-1260 cap is mechanical only. |
| `ST7789_Display_1x06` | `PinHeader_1x06_P2.54mm_ST7789` | **Superseded** by the 4-pin I2C OLED (2026-11-04). Kept for reference. |
| `Adafruit_Metro_RP2350` | `Adafruit_Metro_RP2350_ShieldHeaders` | **Superseded** by the ESP32 dev board (2026-11-04). Kept for reference. |

## Extra footprint

| Footprint | Use |
|---|---|
| `Stabilizer_Cherry_PCB_Holes` | The 3.05 mm and 4.0 mm NPTH holes for one Cherry stabilizer. Place one on each side of the switch, at ±50 mm for a 6.25u spacebar. It fits PCB-mount stabs and clears plate-mount ones. |

## Check before you order boards

- **Hall sensor position:** the footprint origin is the sensor centre. Put it under your switch's magnet, as given in your switch's datasheet. If it sits at the switch centre, use `MX_Magnetic_NoCenterPost`.
- **Fit check:** print the footprints 1:1 on paper and push the real parts through.

## Design notes

- **Sensor supply:** power the hall sensors from **3V3**, so their outputs stay inside the ADC range. Put a 100 nF capacitor at each sensor.
- **DRV5055 grade:** the DRV5055A4 covers about ±170 mT, so it won't saturate with Gateron KS-20 magnets (about 90 mT at bottom-out). The A3 gives twice the resolution but can clip near bottom-out. Both are bipolar, so either magnet pole works.
- **ESP32 inputs:** put the sensors / mux outputs on **ADC1 (GPIO32–39)**, because ADC2 doesn't work while Wi-Fi is on. For more keys than that, use CD74HC4067 16:1 multiplexers. See `documentation/design-notes.md`.
