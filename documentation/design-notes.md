# Design notes

Key decisions and numbers behind the hardware in this repo. Updated 2026-11-03.

## Electronics (hall-effect keyboard)

- **Controller:** Adafruit Metro RP2350, 3.3 V logic. A custom shield plugs on top via the Uno R3 headers.
- **Key sensing:** one linear hall sensor under each MX-style magnetic switch.
  - Hand-solder option: SS49E / 49E in TO-92, laid flat, branded face up, centred under the magnet (pinout 1=VCC 2=GND 3=OUT).
  - SMD option: TI DRV5055 in SOT-23 (pinout 1=VCC 2=OUT 3=GND). DRV5055**A4** (±~170 mT) won't saturate with Gateron KS-20 magnets (~90 mT at bottom-out); A3 has 2× resolution but can clip.
  - Power sensors from **3V3**, not 5 V, so outputs stay inside the RP2350 ADC range. 100 nF decoupling at every sensor.
- **ADC count:** the Metro has only 6 ADC inputs (A0–A5). More than 6 keys needs analog muxes, e.g. CD74HC4067 (16:1) — six of them cover up to 96 keys.
- **Display:** NULLLAB 2.0" ST7789 on SPI0 (D22 = SCK, D23 = MOSI). DC and CS on any free GPIO.
- **Other UI:** EC11 rotary encoder with push switch, Omron B3F-5050 tactile buttons.
- **Power:** MEAN WELL GST60A12 adapter via a CUI PJ-102AH barrel jack (5.5/2.1 mm, centre-positive). Optional — the adapter can plug straight into the Metro.

## Switch lifetime test rig

- **Servo:** TowerPro SG51R (5 g, ~0.6 kg·cm). Servo dimensions in the macro (`SV_*`) are estimates — measure with calipers.
- **Drive:** 20T pinion on a cut-down horn → 40T gear (module 1, 2:1, 30 mm centre distance). Gear + cam are one part on 2× 623ZZ bearings on an M3 axle; slotted axle hole sets the mesh.
- **Cam:** cosine rise of 4.5 mm over 60° of cam rotation, 20° dwell, symmetric fall. Pushes a 623ZZ roller on a guided 10×6 mm plunger with a hard stop at 6 mm. Full press ≈ 130–170° of servo travel. Cam turns CW seen from the front.
- **Height:** saddle slides on a 125 mm column, clamped with M3 bolts in a slot. Plunger tip at rest = saddle bottom − 40 mm. Tick marks every 5 mm.
- **Base:** 170×115×6 mm, two pockets for SYB-170 mini breadboards, DUT bed with M3 clamp slots (nut channels underneath), back stop rail, crosshair at (50, 40).
- **Torque margin:** ~18× with the gearing (~9× without).
- The DUT (a hall-effect switch prototype) is clamped to the bed, not mounted on the breadboards.
