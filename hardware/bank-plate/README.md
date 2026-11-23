# Bank plate

The 1.5 mm switch plate for one 30-key ModuMIDI 2 bank. Banks butt together flush, and the 22.86 mm (0.900 in) key pitch runs straight across the seam.

| File | What |
|---|---|
| `ModuMIDI2_bank_plate.svg` | Laser-cut file, 1:1 in mm, red hairline cut lines |
| `ModuMIDI2_bank_plate_1p5mm.step` | 1.5 mm plate for other CAD tools |
| `ModuMIDI2_bank_plate.FCStd` | FreeCAD model |

## Dimensions

- **Overall:** 240.03 × 180.34 mm, 1.5 mm thick (so MX-style switch clips latch). Square corners.
- **Keys:** 30 switch cut-outs (14.00 mm), 10 columns × 3 rows at a 22.86 mm pitch: white at the front, black in the middle, grey at the back. Rows are 48.90 mm apart; the white switches are 28.58 mm and the grey switches 28.58 mm from the bank's front and back edges.
- **Stabilizers:** a 3u **Gateron low-profile plate-mounted stabilizer** on every key, as in the key prototype (`hardware/key-prototype`). Each key has one opening: two **12.5 mm wide × 6.0 mm deep** housing cut-outs 19.05 mm (0.750 in) in front of and behind the switch, joined by a **1.7 mm slot** for the wire: out from each housing's notch to the bar, then along the bar 9.5 mm to the side of the switch. The wire drops into the slot and the bar pivots there. The bar is on the left of each key, except column 1, whose stabilizer is turned round so its bar is on the right, clear of the seam. Neighbouring white and black housings are side by side, so the white row sits further forward and the grey row further back than the black row.
- **Borders:** a 12.7 mm (0.5 in) border at the front and back, each with 4 × M3 clearance holes (3.4 mm). There is no border on the sides.
- **Side edges (tiling):** a straight seam would always cut a cut-out, so the sides are stepped. The left edge has a tab and the right edge the matching notch (one step each way, through the gaps between the white-rear / black-front and black-rear / grey-front housings), and the next bank's tab drops into this bank's notch. Banks repeat every 228.60 mm (9.000 in).
- **Thinnest webs:** 1.65 mm between each bar slot and its own switch cut-out (as on the prototype), 2.16 mm between the column 1 and column 2 bar slots, 2.4 mm on each side of the seam steps, 4.8 mm between white-rear / black-front (and black-rear / grey-front) housings.

Coordinates in the SVG and FreeCAD model: x from the left tab tip, y from the bank's front edge (the front border is at negative y).

## Before cutting

- Check the laser kerf; the cut-outs are drawn at nominal size.
- Check your stabilizers against the 12.5 × 6.0 mm housing cut-outs and the 1.7 mm wire slot (test-cut one key first; the prototype's checklist lists what is still estimated).
