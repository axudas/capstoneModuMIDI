# Design notes

Key decisions and numbers behind the hardware in this repo.

## Bank layout

- Each bank: 30 keys in 3 rows (white front, black middle, grey back), 10 columns at a **22.86 mm (0.900 in)** pitch. Switch cut-out 14.00 mm.
- **Stabilizers:** 3u on every key, wire running front to back, so each housing cut-out is **14 mm wide × 7 mm deep**, 19.05 mm (0.750 in) in front of and behind its switch.
- Banks butt together flush with the key pitch running straight across the seam, so a bank repeats every **228.60 mm (9.000 in)**.
- Key positions (inches; x from the plate's left tab tip, y from the bank's front edge): white and grey x = 0.900 + 0.9n, black x = 0.450 + 0.9n. Switch rows at y = **1.125 / 3.050 / 4.975** (48.90 mm apart). White and grey sit 28.58 mm from the bank's front and back edges.
- Neighbouring white-rear / black-front (and black-rear / grey-front) housings are side by side with **3.78 mm** between them front to back.
- A straight seam always cuts a cut-out, so the side edges have **one step** (tab on the left, notch on the right). The seam is at the white-row seam except between y = 2.0875 and 4.0125 in, where it moves 0.450 in left; the steps run through the 3.78 mm gaps between housings. Thinnest webs: 1.89 mm beside the steps, 8.55 mm between a switch and its housings.
- Plate: 1.5 mm, bank + 0.5 in border front and back with 4 × M3 holes in each border, no side border: 240.03 × 180.34 mm.
- Bank board: the bank outline trimmed to the sensors and mounting holes, 239.53 × 104.18 mm, boards 0.5 mm apart.

## Electronics

Decisions from the design notebook (status of 12 November 2026).

- **Architecture:** a head unit plus one to four banks. The head unit is an **Adafruit Metro RP2350** with a 2.0" ST7789 240 × 320 SPI display, a rotary encoder and buttons. It owns the tuning state and sends USB-MIDI (MPE) to the host. Each bank has **its own RP2350A** that scans its 30 keys, so the analog signals never leave the bank board.
- **Inter-bank connector:** 12 pins, 12 V and GND on several pins each, plus a two-wire bus. The bank board uses it as +12V × 5, GND × 5, BUS_A/BUS_B (RS-485, half duplex).
- **Key sensing:** one linear hall sensor under each Gateron magnetic switch.
  - Bank boards: TI **DRV5055** in SOT-23, pick-and-place (pinout 1=VCC 2=OUT 3=GND). A3 and A4 samples are ordered; the bench test with the real magnet and travel decides. A3 at 3.3 V puts bottom-out near 91 % of the span; A4 leaves margin at half the resolution. Same footprint either way.
  - Hand-built prototypes: SS49E / 49E in TO-92, laid flat, branded face up, centred under the magnet (pinout 1=VCC 2=GND 3=OUT).
  - Sensors, muxes and the RP2350 ADC supply (ADC_AVDD) share one analog **3.3 V rail**, so the ADC reference tracks the ratiometric sensors. 100 nF at every sensor.
- **Multiplexing:** the RP2350A has four ADC inputs (GPIO26–29). Four CD74HC4067 16:1 muxes share their select lines: two for the 30 key sensors, two for the 30 key-presence lines. Spare channels carry the 12 V and 5 V rail monitors.
- **Key presence:** the key cap is removable. Two pogo pins in the key base are shorted by the cap, so the bank can tell a key with its cap on from one with it off.
- **Key LEDs:** one WS2812-style LED per key, in the key base (it travels with the key). The bank RP2350 drives the chain through a 74AHCT1G125 buffer at 5 V.
- **Power:** MEAN WELL GST60A12-P1J (12 V 5 A, IEC C14 inlet) into the head unit's 5.5/2.1 mm barrel jack. 12 V is distributed to the banks; each bank makes 5 V with its own buck (LEDs) and 3.3 V with two LDOs (digital and analog). Firmware clamps the LED current. Every rail has a power-good LED.
- **Head-unit controls:** EC11 rotary encoder with push switch, Omron B3F-5050 tactile buttons.

## Switch lifetime test rig

- **Servo:** TowerPro SG51R (5 g, ~0.6 kg·cm). Servo dimensions in the macro (`SV_*`) are estimates — measure with calipers.
- **Drive:** 20T pinion on a cut-down horn → 40T gear (module 1, 2:1, 30 mm centre distance). Gear + cam are one part on 2× 623ZZ bearings on an M3 axle; slotted axle hole sets the mesh.
- **Cam:** cosine rise of 4.5 mm over 60° of cam rotation, 20° dwell, symmetric fall. Pushes a 623ZZ roller on a guided 10×6 mm plunger with a hard stop at 6 mm. Full press ≈ 130–170° of servo travel. Cam turns CW seen from the front.
- **Height:** saddle slides on a 125 mm column, clamped with M3 bolts in a slot. Plunger tip at rest = saddle bottom − 40 mm. Tick marks every 5 mm.
- **Base:** 170×115×6 mm, two pockets for SYB-170 mini breadboards, DUT bed with M3 clamp slots (nut channels underneath), back stop rail, crosshair at (50, 40).
- **Torque margin:** ~18× with the gearing (~9× without).
- The DUT (a hall-effect switch prototype) is clamped to the bed, not mounted on the breadboards.
