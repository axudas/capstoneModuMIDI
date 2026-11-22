# ModuMIDI 2 — Hall-Effect MIDI Keyboard (Capstone)

A modular MIDI keyboard that uses **magnetic (hall-effect) key switches** for analog, velocity-sensitive key sensing. It is driven by an **Adafruit Metro RP2350** and has an ST7789 display, a rotary encoder and buttons. This project builds on the original ModuMIDI (see `reference material/oldProject`).

> **Last updated:** 2026-11-17

---

## Repository layout

```
capstone/
├── README.md                     ← you are here
├── PCB/
│   ├── moduMidi/                 KiCad project (schematic + board)
│   └── libraries/
│       ├── Capstone_Keyboard.kicad_sym   custom KiCad symbols (8)
│       ├── Capstone_Keyboard.pretty/     custom KiCad footprints (12)
│       └── README.md
├── mechanical/
│   └── switch-test-rig/          FreeCAD switch-lifetime test rig (macro, FCStd, STEP, STLs)
├── spacebar-prototype/           single hall-effect key test: KiCad board + RGB-lit 6.25u spacebar layer stack (STL)
├── documentation/
│   └── design-notes.md           key design decisions and numbers
├── src/                          firmware (not started yet)
└── reference material/
    └── oldProject/               original ModuMIDI: Altium PCB, 3D-printed parts, photos
```

## Status

| Area | Status |
|---|---|
| Parts library (KiCad) | ✅ Done — 8 symbols, 12 footprints, needs a 1:1 paper-print fit check |
| Schematic | 🟡 In progress — 33 hall sensors + barrel jack placed |
| PCB layout | 🟡 Started — 175 × 125 mm board outline set |
| Spacebar prototype (1 key, 6.25u, RGB) | 🟡 Started — all-THT KiCad PCB routed (DRC clean), layer stack STLs + cut files + renders, not built yet |
| Switch test rig (CAD) | ✅ Designed — ready to print, servo dims need measuring |
| Firmware | ⬜ Not started |
| Enclosure / keys | ⬜ Not started (old ModuMIDI parts available for reference) |

## What's been done

### 1. Custom KiCad parts library — `PCB/libraries/Capstone_Keyboard`
KiCad symbol library (`.kicad_sym`) and footprint library (`.pretty`), converted from the original LibrePCB library on 2026-11-17. Both KiCad projects already point to it. It has symbols and footprints for:

| Device | Footprint |
|---|---|
| Adafruit Metro RP2350 (shield headers) | Arduino Uno R3 headers + 4× M3 holes |
| NULLLAB 2.0" ST7789 display | 1×6 2.54 mm header (G, V, SCL, SDA, DC, CS) |
| EC11 rotary encoder with switch | Alps EC11E vertical |
| Omron B3F-5050 tactile switch | B3F 12×12 + 2× boss holes |
| CUI PJ-102AH barrel jack (for MEAN WELL GST60A12) | PJ-102AH THT |
| Hall sensor SS49E / 49E (TO-92) | Lying flat under the key switch, upright wide, upright 1.27 mm |
| Hall sensor TI DRV5055 (SOT-23) | SOT-23-3 |
| MX-style magnetic key switch | "Center Post" / "No Center Post" variants |
| Cherry stabilizer (PCB holes) | 3.05 + 4.0 mm NPTH pair, one per side |

See the library's own [README](PCB/libraries/README.md) for pinouts and how to add it to other projects.

### 2. Schematic started — `PCB/moduMidi`
The KiCad project `moduMidi.kicad_pro` has the main schematic with 33 linear hall-effect sensors (U1–U33) and the DC barrel jack (J1) placed, plus the 175 × 125 mm board outline.

### 3. Switch lifetime test rig — `mechanical/switch-test-rig`
A 3D-printable rig for cycling a hall-effect switch prototype to measure its lifetime:
- SG51R micro servo → 2:1 gear train → cosine cam → roller → guided plunger, so the switch is pressed straight down with no side load.
- Adjustable height column with a scale, breadboard pockets for the electronics, and a clamp bed for the device under test.
- Parametric FreeCAD macro, assembled `.FCStd`, `.step` and print-ready STLs. The full print list, hardware and assembly steps are in its [README](mechanical/switch-test-rig/README.md).

![Switch test rig](mechanical/switch-test-rig/img/iso.png)

### 4. Design decisions
Sensor choice, ADC/mux plan, power and display wiring are written up in [documentation/design-notes.md](documentation/design-notes.md).

## Future work

**Electronics**
- [ ] Check the library footprints: print 1:1 and push the real parts through. Also check Metro D22/D23 against its silkscreen and the display cable colours.
- [ ] Finish the schematic: add the Metro, CD74HC4067 analog muxes (the Metro has only 6 ADC pins), the display, encoder and buttons. Add a 100 nF capacitor on every sensor, and power the sensors from 3V3.
- [ ] Pick the final hall sensor (SS49E TO-92 for hand assembly vs DRV5055A4 SOT-23).
- [ ] Lay out the PCB (KiCad: Update PCB from Schematic), put each sensor under its switch's magnet, run ERC/DRC and order boards.

**Firmware (`src/`)**
- [ ] Read the ADC through the muxes and calibrate each key (rest / bottom-out).
- [ ] Turn key travel into MIDI note on/off with velocity (and optionally aftertouch).
- [ ] USB-MIDI device, display UI, encoder menu.

**Testing**
- [ ] Measure the SG51R and update the `SV_*` parameters in the rig macro, then print and build the rig.
- [ ] Write test-rig firmware (servo cycling + press counter + sensor logging) and run lifetime tests on the switch prototype.

**Mechanical**
- [ ] Design the enclosure, key plates and keycaps (old ModuMIDI parts can be a starting point).

## Tools

- [KiCad](https://www.kicad.org) 7 or newer — schematic, PCB and parts library (the files are KiCad 7 format; KiCad 8/9 open them and upgrade on save)
- [FreeCAD](https://www.freecad.org) — test rig (run `SwitchLifeRig.FCMacro` to regenerate)

### Working on the PCB from this repo
1. In KiCad, open `PCB/moduMidi/moduMidi.kicad_pro` (or `spacebar-prototype/pcb/spacebarHall/spacebarHall.kicad_pro`).
2. That's it. Each project's `sym-lib-table` / `fp-lib-table` already points to `PCB/libraries/Capstone_Keyboard`, and the other parts come from the standard KiCad libraries that ship with KiCad.

The projects moved from LibrePCB to KiCad on 2026-11-17. The LibrePCB files are still in the git history if you ever need them.

---

## Changelog

| Date | Change |
|---|---|
| 2026-11-17 | Spacebar board v0.5: off-board connections moved to a 6-way 3.5 mm screw terminal (J1) on a 13 mm tab at the left end (board now 153 × 30 mm), R1 moved next to J2, all signals routed on top. J1 pinout changed: TOP_DET / 3V3 / HALL_OUT / GND / 5V / LED_DIN |
| 2026-11-17 | **Switched from LibrePCB to KiCad**: `Capstone_Keyboard` library (8 symbols, 12 footprints), `moduMidi` project and the spacebar board (DRC clean, schematic and board match). LibrePCB files removed. |
| 2026-11-17 | Spacebar prototype: whole-design exploded model now also breaks the key apart (LED, pogo, magnets, shim, topper) |
| 2026-11-17 | Spacebar prototype: whole-key exploded model (`key_exploded.stl/.glb`) + renders |
| 2026-11-17 | Spacebar prototype: whole-key assembled model (`key_assembled.stl/.glb`), assembled-stack GLB, assembled + section renders |
| 2026-11-17 | Spacebar prototype v4: top-detect 2-pin pogo connector in the spacebar, shorted by a brass shim in the topper (J3 + 10k pull-up, TOP_DET on J1 pin 6) |
| 2026-11-17 | Spacebar prototype v3: all-THT PCB (axial C1/R1, GND on bottom plane), LED = one WS2812B strip pixel, magnets in topper ends, thinner topper without ribs, key 0.75 in deep, proper 3D renders |
| 2026-11-17 | Spacebar prototype v2: taller/steeper key, toothed key pattern along both edges, hollow diffuser topper, RGB LED in the key (J2 + 5V/DIN on J1), through-hole TO-92 hall sensor |
| 2026-11-17 | Added `spacebar-prototype/`: one-key DRV5055 board (LibrePCB) and an exploded PCB / foam / acrylic / spacebar / keyed-topper stack (STL, GLB, DXF) |
| 2026-11-03 | Portfolio page: [aidancarr.tech/modumidi.html](https://aidancarr.tech/modumidi.html) |
| 2026-11-03 | Organized repo: added LibrePCB project + libraries, switch test rig, design notes and this README |
| 2026-10-22 | Imported the original ModuMIDI project as reference material |
