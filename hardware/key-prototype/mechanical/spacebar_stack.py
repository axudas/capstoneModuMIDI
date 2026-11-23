#!/usr/bin/env python3
"""
Parametric layer stack for the ModuMIDI 3u hall-effect key prototype: one stack per key type.

  grey   wide head (20.32 mm) at the back, narrow tail (6.35 mm) running forward between the black keys, 76.2 mm long;
         the switch sits 28.575 mm from the back end of the head (bank plate, rows 48.90 mm apart)
  black  11.43 x 57.15 mm, centred on its switch
  white  the grey key turned around (head at the front): built as the grey stack rotated 180 degrees, PCB included

The keys run front to back. Every key has an MX-style magnetic switch at its centre and a Gateron low-profile
plate-mounted stabilizer (6.25u, wire cut and bent to 3u) with its housings 19.05 mm in front of and behind the switch.
The low-profile stab sits much lower than the full-height switch, so the key reaches down to it with two posts.

Layers (bottom -> top):
  1. PCB      30 x 113 x 1.6 mm, shared by all three keys (pcb/spacebarHall): TO-92 hall sensor lying flat under the
              switch, axial C1/R1/R3, a 5-pin key header (J2, behind the switch: DI, DET, GND, DO, 5V wires up to the
              key), and a 7-way screw terminal (J1) on a 13 mm tab at the back (at the front for the white key)
  2. FOAM     3.5 mm, fills the gap between PCB top and plate bottom
  3. ACRYLIC  1.5 mm plate: switch cut-out, 2 low-profile stabilizer cut-outs (Gateron drawing) joined by the wire slot, J2 wire slot
  4. KEY      12 mm tall, steep walls: centre MX stem socket, 2 stabilizer posts reaching down to the low-profile stab,
              a pocket for one WS2812B-2020 pixel cut from a 5 mm strip, a 2-pin pogo connector (top detect) and
              2 magnet pockets
  5. TOPPER   5 mm hollow diffuser on the key, with a lip all round that hugs the top of the key, 2 magnets, and a
              brass shim that shorts the pogo pins when it is on

Run:  pip install manifold3d trimesh numpy   then   python3 spacebar_stack.py
Outputs: ./<white|black|grey>/ with stl/ (one STL per part), cut-files/ (DXF for the plate and foam),
stack_exploded / stack_assembled / key_assembled / key_exploded .stl + .glb
Coordinates: X across the key (right +), Y front(-) / back(+) along the key, Z up. Origin = switch centre on the
PCB bottom.
"""
import math, os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, JoinType, OpType

HERE = os.path.dirname(os.path.abspath(__file__))
SEG = 48                       # circle resolution
IN = 25.4

# ---------------- parameters (mm) ----------------
# stack outline (foam + plate); the PCB adds PCB_TAB at the back for the terminal
BOARD_W, BOARD_D = 30.0, 100.0           # X, Y, centred on the switch
PCB_T = 1.6
PLATE_T = 1.5                            # acrylic, standard MX plate thickness
PLATE_TOP_ABOVE_PCB_TOP = 5.0            # MX spec: plate top to PCB top
FOAM_T = PLATE_TOP_ABOVE_PCB_TOP - PLATE_T   # 3.5
SCREW_D = 2.2                            # M2 clearance
SCREWS = [(sx * 12.0, sy * 47.0) for sx in (-1, 1) for sy in (-1, 1)]
PCB_TAB = 13.0                           # PCB extension at +Y for J1 (outside the foam + plate)
TB_PIN_Y = 58.0                          # J1 pins at x = 10.5 ... -10.5 (7-way)
TB_PINS = 7
TB_BODY = (54.9, 62.5, 3.5 * TB_PINS)    # y0, y1, length along X
TB_H = 8.5                               # terminal body height above the PCB -- ESTIMATE, check your part
SWITCH_CUT = 0.551 * IN                  # 14.00 mm, as the bank plate SVG
STAB_Y = 0.75 * IN                       # 3u stabilizer: housings 19.05 mm in front of / behind the switch
# Gateron low-profile plate-mounted stabilizer (KS-WXZ-Z10F01-D08-97), bought as 6.25u, wire cut + bent to 3u.
# Plate cut-out per housing from Gateron's drawing: 6.00 (along the key) x 12.50 (across), plus a 1.70 mm notch.
STAB_CUT_W, STAB_CUT_D = 12.5, 6.0
STAB_CUT_X0, STAB_CUT_X1 = -STAB_CUT_W / 2, STAB_CUT_W / 2
STAB_NOTCH_W = 1.7                       # notch on the wire side (-X), where the wire arm goes into the housing
# The wire drops into a 1.7 mm slot cut in the acrylic: from each housing notch out to the bar, then along the bar.
# The bar pivots in that slot and its two arms run through the notches into the sliders.
WIRE_D = 1.4                             # stabilizer wire diameter: ESTIMATE, measure it
WIRE_SLOT = STAB_NOTCH_W                 # slot width for the bar and arms (same as Gateron's notch)
STAB_WIRE_X = -9.5                       # the bar's straight run (1.2 mm web left to the switch cut-out)
# heights are NOT on Gateron's drawing -- ESTIMATES for a low-profile stab, measure the real one and update:
LP_STEM_TOP = 6.5                        # stab stem top above the plate top, at rest
LP_TRAVEL = 3.5                          # stab stroke (shorter than the MX switch's 4 mm, so it sets the key travel)
LP_SOCKET_DEPTH = 2.5                    # how far the stab stem goes into the key post
LP_HOUSING_ABOVE = 0.3                   # housing top above the plate top
PCB_PEG_D, PCB_PEG_X = 1.75, 5.08
# J2 key header: 1x5 2.54 mm pin header between the switch and the back stabilizer (y = LED_Y on the board)
J2_X = (-5.08, -2.54, 0.0, 2.54, 5.08)   # DI, DET, GND, DO, 5V
J2_BODY_H = 2.5                          # header plastic, sits in the foam cut-out
J2_PIN_ABOVE_PLATE = 1.0                 # trim the pins to about 1 mm above the plate (full-length pins hit the black key)
# key caps (bottom outlines, from the bank drawing, switch-centred). Each is a union of rectangles (x0, y0, x1, y1);
# the tail rectangle runs on into the head so its tapered end is buried inside it.
CAPS = {
    'grey':  [(-0.4 * IN, -0.7 * IN, 0.4 * IN, 1.125 * IN), (-0.125 * IN, -1.875 * IN, 0.125 * IN, 0.0)],
    'black': [(-0.225 * IN, -1.125 * IN, 0.225 * IN, 1.125 * IN)],
}
CAP_H, CAP_WALL, CAP_ROOF = 12.0, 1.5, 3.0
TAPER = 0.6                              # steep walls: the top is 0.6 mm in from the bottom edge all round
CAP_R = 1.0
CAP_REST_ABOVE_PLATE = 7.5               # skirt bottom above plate top, at rest (4 mm travel + margin)
STEM_D, CROSS_L, CROSS_W, CROSS_DEPTH = 5.5, 4.15, 1.31, 3.8
FIT = 0.15                               # clearance per side for every mating feature
# hollow light-box topper with a lip that hugs the top of the key
TOPPER_H, TOPPER_WALL, DIFFUSER_T = 5.0, 2.0, 1.0
LIP_T, LIP_H = 1.0, 2.0                  # lip wall thickness, how far it reaches down the key
# per key: LED wire hole (over J2 on the PCB), pogo connector (its 2 wires run inside the key to the LED end), magnets
FEATURES = {
    'grey':  {'led_hole_y': 11.35, 'pogo_y': -11.35, 'mags': ((0.0, 24.0), (5.5, -11.35))},
    'black': {'led_hole_y': 11.35, 'pogo_y': -11.35, 'mags': ((0.0, -24.0), (0.0, 24.0))},
}
# magnets: one 6 x 2 disc in each end of the topper + one under it in the key (opposite poles facing)
MAG_D, MAG_T = 6.0, 2.0
MAG_POCKET_D, MAG_POCKET_DEPTH = MAG_D + 0.2, MAG_T + 0.2
# RGB LED: one WS2812B-2020 pixel cut from a 5 mm wide strip (144 LED/m), wires soldered to its DIN-end pads
LED_SEG = (5.0, 6.9, 0.3)                # strip piece: width (x), length cut line to cut line (y), FPC thickness
LED_BODY = (2.0, 2.0, 0.84)              # the 2020 LED on it
LED_POCKET_DEPTH = 2.2                   # strip piece + LED sit about 1 mm below the key top
WIRE_BAY = 3.25                          # pocket length behind the DIN end, over the wire hole
LED_WIRE_HOLE = 3.5
# top-detect: 2-pin pogo connector (Top-Link 10101022778, 5.80 mm pitch, 5.20 mm working height), pins up, its row
# along the key. Only pitch + working height are published -- the body numbers are ESTIMATES: measure yours.
POGO_PITCH = 5.8
POGO_BODY = (3.2, 9.6, 3.0)              # x (across), y (along the pins' row), z
POGO_KEY = (2.6, 3.6, 4.0)               # T-shaped centre block, sticks out toward -x, 1 mm deeper than the body
POGO_COLLAR = (2.0, 0.6)
POGO_PLUNGER = (1.0, 1.6)
POGO_TAIL = (0.8, 2.0)
POGO_PRESS = 1.0                         # plungers stick out 1 mm above the key top; the topper presses them flush
SHORT_PLATE = (4.0, 9.0, 0.3)            # brass shim / copper tape in the topper underside (x, y, thickness)
# plate + foam wire slots (x0, y0, x1, y1), around the PCB pads
def led_slot(y):  return (-6.35, y - 1.3, 6.35, y + 1.3)    # over J2: its 5 pins + the wires up to the key
# exploded views: extra Z per layer, and for the key's own parts
EXPLODE = {'pcb': 0, 'foam': 12, 'plate': 24, 'key': 44, 'topper': 64}
KEY_EXPLODE = {'4_key': 0, '4a_rgb_led_strip_piece': 12, '4c_pogo_connector': 12, '4b_magnets_key': 12,
               '5b_short_plate': 26, '5a_magnets_topper': 26, '5_topper': 38}

def part_explode(name, layer):
    if name in KEY_EXPLODE:
        return EXPLODE['key'] + KEY_EXPLODE[name]
    return EXPLODE[layer]

# derived Z levels (assembled)
Z_PCB_TOP = PCB_T
Z_PLATE_BOT = Z_PCB_TOP + FOAM_T
Z_PLATE_TOP = Z_PLATE_BOT + PLATE_T
Z_STEM_TOP = Z_PLATE_TOP + 11.6          # MX stem top at rest
Z_CAP_BOT = Z_PLATE_TOP + CAP_REST_ABOVE_PLATE
Z_CAP_TOP = Z_CAP_BOT + CAP_H

# ---------------- helpers ----------------
def box(w, d, h, x=0.0, y=0.0, z=0.0):
    """box centred on (x, y) in XY, from z to z+h"""
    return Manifold.cube((w, d, h), center=False).translate((x - w / 2, y - d / 2, z))

def rbox_xy(x0, y0, x1, y1, h, r, z=0.0):
    return rbox(x1 - x0, y1 - y0, h, r, (x0 + x1) / 2, (y0 + y1) / 2, z)

def cyl(dia, h, x=0.0, y=0.0, z=0.0):
    return Manifold.cylinder(h, dia / 2, dia / 2, SEG).translate((x, y, z))

def rrect(w, d, r):
    r = min(r, w / 2 - 0.01, d / 2 - 0.01)
    return CrossSection.square((w - 2 * r, d - 2 * r), True).offset(r, JoinType.Round, 2.0, SEG)

def rbox(w, d, h, r, x=0.0, y=0.0, z=0.0):
    return rrect(w, d, r).extrude(h).translate((x, y, z))

def tapered_rect(x0, y0, x1, y1, inset, h, r, z=0.0):
    """hull of a bottom rounded rectangle and a top one inset by `inset` all round"""
    a = rrect(x1 - x0, y1 - y0, r).extrude(0.01).translate(((x0 + x1) / 2, (y0 + y1) / 2, 0))
    b = rrect(x1 - x0 - 2 * inset, y1 - y0 - 2 * inset, r).extrude(0.01).translate(((x0 + x1) / 2, (y0 + y1) / 2, h - 0.01))
    return Manifold.batch_hull([a, b]).translate((0, 0, z))

def union(parts):
    parts = [p for p in parts if p is not None]
    out = parts[0]
    for p in parts[1:]:
        out = out + p
    return out

def mx_cross(h, z, grow=0.0):
    return box(CROSS_L + grow, CROSS_W + grow, h, z=z) + box(CROSS_W + grow, CROSS_L + grow, h, z=z)

def stab_cutout_2d(y):
    """rectangles (x0, y0, x1, y1) of one stabilizer cut-out centred on y"""
    # housing cut-out + the notch, which carries on out to the bar as the arm slot
    return [(STAB_CUT_X0, y - STAB_CUT_D / 2, STAB_CUT_X1, y + STAB_CUT_D / 2),
            (STAB_WIRE_X - WIRE_SLOT / 2, y - STAB_NOTCH_W / 2, STAB_CUT_X0 + 0.01, y + STAB_NOTCH_W / 2)]

def wire_slot_2d():
    """the bar's slot, joining the two arm slots"""
    h = WIRE_SLOT / 2
    return (STAB_WIRE_X - h, -STAB_Y - h, STAB_WIRE_X + h, STAB_Y + h)

def plate_like(t, z, cutouts_rect, holes, tab=0.0):
    """flat layer of the stack outline (+ tab mm at +Y) with rectangular cut-outs and round holes (x, y, d)"""
    m = rbox(BOARD_W, BOARD_D + tab, t, 1.0, y=tab / 2, z=z)
    for x0, y0, x1, y1 in cutouts_rect:
        m = m - box(x1 - x0, y1 - y0, t + 2, x=(x0 + x1) / 2, y=(y0 + y1) / 2, z=z - 1)
    for x, y, d in holes:
        m = m - cyl(d, t + 2, x, y, z - 1)
    return m

def axial(x0, y0, x1, y1, d=1.6):
    """axial resistor / capacitor body lying flat between two pads"""
    L = math.dist((x0, y0), (x1, y1)) - 3.9
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    c = Manifold.cylinder(L, d / 2, d / 2, 24).rotate((0, 90, 0)).translate((-L / 2, 0, 0))
    return c.rotate((0, 0, ang)).translate(((x0 + x1) / 2, (y0 + y1) / 2, PCB_T + d / 2))

# ---------------- key geometry per type ----------------
def cap_pieces(v):
    return CAPS[v]

def top_pieces(v):
    """key top outline as rectangles (the bottom pieces inset by TAPER)"""
    return [(x0 + TAPER, y0 + TAPER, x1 - TAPER, y1 - TAPER) for x0, y0, x1, y1 in cap_pieces(v)]

def width_at(v, y, top=True):
    """half-width of the key (top or bottom outline) at y"""
    hw = 0.0
    for x0, y0, x1, y1 in (top_pieces(v) if top else cap_pieces(v)):
        if y0 <= y <= y1:
            hw = max(hw, x1)
    return hw

def led_span(v):
    """y range of the LED pocket: wire bay over the hole, then the strip piece (DIN end toward the hole)"""
    hy = FEATURES[v]['led_hole_y']
    return hy - LED_WIRE_HOLE / 2 - 0.25, hy - LED_WIRE_HOLE / 2 + WIRE_BAY + LED_SEG[1] + 0.25

def led_centre(v):
    y0, y1 = led_span(v)
    return y1 - 0.25 - LED_SEG[1] / 2

def keepouts(v):
    """(x0, y0, x1, y1) areas on the key top the notches must stay clear of"""
    f = FEATURES[v]
    y0, y1 = led_span(v)
    ko = [(-LED_SEG[0] / 2 - 0.25, y0, LED_SEG[0] / 2 + 0.25, y1)]
    py = f['pogo_y']
    ko.append((-POGO_BODY[0] / 2 - POGO_KEY[0] - FIT, py - POGO_BODY[1] / 2 - FIT,
               POGO_BODY[0] / 2 + FIT, py + POGO_BODY[1] / 2 + FIT))
    for mx, my in f['mags']:
        ko.append((mx - MAG_POCKET_D / 2, my - MAG_POCKET_D / 2, mx + MAG_POCKET_D / 2, my + MAG_POCKET_D / 2))
    return ko

# ---------------- layer 1: PCB (shared) ----------------
def make_terminal():
    """J1 screw terminal: body, 7 screw heads, 7 wire openings on the +Y face, pins through the PCB"""
    y0, y1, L = TB_BODY
    tb = box(L, y1 - y0, TB_H, y=(y0 + y1) / 2, z=PCB_T)
    for i in range(TB_PINS):
        x = 3.5 * (TB_PINS - 1) / 2 - 3.5 * i
        tb = tb - cyl(2.6, 1.0, x, TB_PIN_Y, PCB_T + TB_H - 0.8)
        tb = tb + (cyl(2.4, 0.6, x, TB_PIN_Y, PCB_T + TB_H - 0.8) - box(0.5, 2.6, 1.0, x=x, y=TB_PIN_Y, z=PCB_T + TB_H - 0.5))
        tb = tb - box(2.4, 4.0, 2.6, x=x, y=y1 - 1.9, z=PCB_T + 1.6)
        tb = tb + box(0.8, 0.8, 3.5, x=x, y=TB_PIN_Y, z=-3.5 + PCB_T)
    return tb

def make_pcb():
    holes = [(x, y, SCREW_D) for x, y in SCREWS] + [(sx * PCB_PEG_X, 0, PCB_PEG_D) for sx in (-1, 1)]
    pcb = plate_like(PCB_T, 0.0, [], holes, tab=PCB_TAB)
    parts = [box(3.0, 4.0, 1.55, z=PCB_T)]                       # U1 TO-92 lying flat, branded face up
    for y in (-2.54, 0.0, 2.54):
        parts.append(box(1.6, 0.45, 0.45, x=-2.3, y=y, z=PCB_T))
    parts.append(axial(9.5, 3.75, 9.5, -3.75, 1.9))              # C1 100 nF
    parts.append(axial(-13.0, 24.5, -13.0, 32.12))               # R1 330R
    parts.append(axial(-3.81, 36.0, 3.81, 36.0))                 # R3 10k
    parts.append(make_terminal())
    return pcb + union(parts)

def pcb_wire_stubs(v):
    """J2: the 5-pin key header (pins trimmed) that the key's 5 wires are soldered to"""
    y = FEATURES[v]['led_hole_y']
    parts = [box(2.54 * 5, 2.54, J2_BODY_H, 0, y, PCB_T)]
    top = Z_PLATE_TOP + J2_PIN_ABOVE_PLATE
    parts += [box(0.64, 0.64, top - (PCB_T - 2.5), x, y, PCB_T - 2.5) for x in J2_X]
    return union(parts)

# ---------------- layer 2: foam ----------------
def foam_cuts(v):
    f = FEATURES[v]
    cut = [(-7.75, -7.75, 7.75, 7.75),                           # switch bottom housing + sensor
           (7.9, -4.9, 11.1, 4.9),                               # C1
           (-14.3, 22.9, -11.7, 33.7),                           # R1
           (-5.4, 34.7, 5.4, 37.3)]                              # R3
    for sy in (-1, 1):
        cut.append((STAB_WIRE_X - 1.5, sy * STAB_Y - 4.0, STAB_CUT_X1 + 1.0, sy * STAB_Y + 4.0))   # stabilizer housing + arm swing
    cut.append((STAB_WIRE_X - 1.5, -STAB_Y - 4.9, STAB_WIRE_X + 1.5, STAB_Y + 4.9))              # stabilizer bar
    x0, y0, x1, y1 = led_slot(f['led_hole_y']); cut.append((x0 - 1.0, y0 - 0.4, x1 + 1.0, y1 + 0.4))   # J2 header
    return cut

def make_foam(v):
    return plate_like(FOAM_T, Z_PCB_TOP, foam_cuts(v), [(x, y, SCREW_D + 1.0) for x, y in SCREWS])

# ---------------- layer 3: acrylic plate + switch + stabilizer ----------------
def plate_cuts(v):
    f = FEATURES[v]
    cut = [(-SWITCH_CUT / 2, -SWITCH_CUT / 2, SWITCH_CUT / 2, SWITCH_CUT / 2),
           led_slot(f['led_hole_y'])]
    for sy in (-1, 1):
        cut += stab_cutout_2d(sy * STAB_Y)
    cut.append(wire_slot_2d())
    return cut

def make_plate(v):
    return plate_like(PLATE_T, Z_PLATE_BOT, plate_cuts(v), [(x, y, SCREW_D) for x, y in SCREWS])

TRAVEL = min(4.0, LP_TRAVEL)            # key travel: the MX switch has 4 mm, the low-profile stab less

def switch_top_housing(grow=0.0):
    """the MX top housing above the plate (15.6 square tapering to 11 over 3.6 mm), optionally grown all round"""
    return Manifold.batch_hull([rrect(15.6 + 2 * grow, 15.6 + 2 * grow, 1).extrude(0.01),
                                rrect(11 + 2 * grow, 11 + 2 * grow, 1).extrude(0.01).translate((0, 0, 3.59 + grow))]).translate((0, 0, Z_PLATE_TOP))

def make_switch():
    """simplified MX-style magnetic switch, sitting in the plate cut-out"""
    bottom = box(13.9, 13.9, Z_PLATE_TOP - Z_PCB_TOP, z=Z_PCB_TOP)
    pegs = cyl(1.6, 2.0, -PCB_PEG_X, 0, Z_PCB_TOP - 2.0) + cyl(1.6, 2.0, PCB_PEG_X, 0, Z_PCB_TOP - 2.0)
    top = switch_top_housing()
    slider = rbox(7.0, 5.5, 4.4, 0.8, z=Z_PLATE_TOP + 3.6)
    stem = mx_cross(Z_STEM_TOP - (Z_PLATE_TOP + 8.0), Z_PLATE_TOP + 8.0, grow=-0.1)
    return bottom + pegs + top + slider + stem

WIRE_Z = Z_PLATE_BOT + PLATE_T / 2              # the bar sits in the plate slot, mid-thickness

def stab_wire(press=0.0):
    """bar along the key in the plate slot; at each housing an arm runs across to the slider.
    Pressing the key by `press` turns the bar so each arm's slider end drops by `press`."""
    L = 2 * STAB_Y
    r = WIRE_D / 2
    ang = math.degrees(math.atan2(press, -STAB_WIRE_X))
    parts = [Manifold.cylinder(L, r, r, 24).rotate((-90, 0, 0)).translate((STAB_WIRE_X, -L / 2, WIRE_Z))]
    for sy in (-1, 1):
        arm = Manifold.cylinder(-STAB_WIRE_X, r, r, 24).rotate((0, 90, 0))            # along +x from the bar
        arm = arm + Manifold.sphere(r, 24)                                            # the bend
        arm = arm.rotate((0, ang, 0))                                                 # tilt about the bar axis
        parts.append(arm.translate((STAB_WIRE_X, sy * STAB_Y, WIRE_Z)))
    return union(parts)

def make_stabilizer():
    """low-profile plate-mount stabilizer (placeholder shapes, heights estimated): 2 housings clipped in the plate,
    2 short sliders with MX-style crosses, wire bent to 3u running along the key on the -X side"""
    parts = []
    z_top = Z_PLATE_TOP + LP_STEM_TOP
    for sy in (-1, 1):
        y = sy * STAB_Y
        housing = box(STAB_CUT_W - 0.3, STAB_CUT_D - 0.2, 2.6 + PLATE_T + LP_HOUSING_ABOVE, 0, y, Z_PLATE_BOT - 2.6)
        housing = housing - box(4.4, 4.4, 10, 0, y, Z_PLATE_BOT - 3)
        housing = housing - box(STAB_CUT_W, STAB_NOTCH_W, 10, -STAB_CUT_W / 2, y, WIRE_Z - LP_TRAVEL - 1.2)  # arm channel
        slider_bot = Z_PLATE_BOT + 0.3             # the arm tip goes into the slider; pressed, 0.3 mm above the PCB
        slider = box(4.2, 4.2, z_top - LP_SOCKET_DEPTH - slider_bot, 0, y, slider_bot)
        stem = mx_cross(LP_SOCKET_DEPTH, z_top - LP_SOCKET_DEPTH, grow=-0.1).translate((0, y, 0))
        parts += [housing, slider, stem]
    parts.append(stab_wire())
    return union(parts)

# ---------------- layer 4: key ----------------
def key_outer(v):
    return union([tapered_rect(*p, TAPER, CAP_H, CAP_R, z=Z_CAP_BOT) for p in cap_pieces(v)])

def key_inner(v):
    pieces = []
    for x0, y0, x1, y1 in cap_pieces(v):
        if x1 - x0 - 2 * CAP_WALL < 1.0:
            continue
        pieces.append(tapered_rect(x0 + CAP_WALL, y0 + CAP_WALL, x1 - CAP_WALL, y1 - CAP_WALL,
                                   TAPER * (CAP_H - CAP_ROOF) / CAP_H, CAP_H - CAP_ROOF + 0.01, 0.5, z=Z_CAP_BOT - 0.01))
    return union(pieces)

def pogo_body_bottom():
    """z of the pogo body underside when the topper is on (plungers pressed flush with the key top)"""
    return Z_CAP_TOP - POGO_PLUNGER[1] - POGO_COLLAR[1] + POGO_PRESS - POGO_BODY[2]

def make_key(v):
    f = FEATURES[v]
    z0, top = Z_CAP_BOT, Z_CAP_TOP
    outer = key_outer(v)
    cap = outer - key_inner(v)
    ceiling = top - CAP_ROOF
    stem_bot = z0 + 0.5
    adds, cuts = [], []
    adds.append(cyl(STEM_D, ceiling - stem_bot + 0.1, 0, 0, stem_bot))       # centre MX stem socket
    cuts.append(mx_cross(CROSS_DEPTH, stem_bot - 0.01))
    post_bot = Z_PLATE_TOP + LP_STEM_TOP - LP_SOCKET_DEPTH                     # low-profile stab: posts reach down
    posts = []
    for sy in (-1, 1):
        y = sy * STAB_Y
        posts.append(cyl(STEM_D, ceiling - post_bot + 0.1, 0, y, post_bot))
        cuts.append(mx_cross(LP_SOCKET_DEPTH + 0.2, post_bot - 0.01).translate((0, y, 0)))
    # relief over the switch's top housing so a key narrower than the switch (black) clears it at full travel
    cuts.append(switch_top_housing(0.3).translate((0, 0, TRAVEL + 0.3)))
    # LED: rib under the pocket, pocket (wire bay + strip piece), wire hole down into the key
    y0, y1 = led_span(v)
    pw = LED_SEG[0] + 0.5
    adds.append(box(pw + 3.0, y1 - y0 + 2.0, 1.01, 0, (y0 + y1) / 2, ceiling - 1.0))
    cuts.append(rbox_xy(-pw / 2, y0, pw / 2, y1, LED_POCKET_DEPTH + 1, 0.5, top - LED_POCKET_DEPTH))
    cuts.append(cyl(LED_WIRE_HOLE, CAP_H + 2, 0, f['led_hole_y'], z0 - 1))
    # pogo connector: boss under the roof, stepped pocket for body + T block, tail holes
    py, zb = f['pogo_y'], pogo_body_bottom()
    kx = -POGO_BODY[0] / 2 - POGO_KEY[0] / 2 + FIT
    adds.append(box(POGO_BODY[0] + POGO_KEY[0] + 3.0, POGO_BODY[1] + 3.0, ceiling - (zb - 2.0) + 0.1,
                    -POGO_KEY[0] / 2, py, zb - 2.0))
    cuts.append(box(POGO_BODY[0] + 2 * FIT, POGO_BODY[1] + 2 * FIT, top - zb + 1, 0, py, zb))
    cuts.append(box(POGO_KEY[0] + 2 * FIT, POGO_KEY[1] + 2 * FIT, top - zb + 2, kx, py, zb - 1.0))
    for dy in (-POGO_PITCH / 2, POGO_PITCH / 2):
        cuts.append(cyl(1.6, 10, 0, py + dy, zb - 9))
    for mx, my in f['mags']:                          # magnet pockets in the top
        cuts.append(cyl(MAG_POCKET_D, MAG_POCKET_DEPTH + 1, mx, my, top - MAG_POCKET_DEPTH))
    cap = cap + (union(adds) ^ outer)                 # additions never stick out of the key
    cap = cap + union(posts)                          # the stab posts hang below the key (white/grey tail: wider than it)
    return cap - union(cuts)

def make_pogo(v):
    """2-pin pogo connector in its pocket, shown pressed (topper on); 2 wire stubs off the tails"""
    py, zb = FEATURES[v]['pogo_y'], pogo_body_bottom()
    m = box(POGO_BODY[0], POGO_BODY[1], POGO_BODY[2], 0, py, zb)
    m = m + box(POGO_KEY[0], POGO_KEY[1], POGO_KEY[2], -POGO_BODY[0] / 2 - POGO_KEY[0] / 2 + 0.01, py, zb - 1.0)
    for dy in (-POGO_PITCH / 2, POGO_PITCH / 2):
        zt = zb + POGO_BODY[2]
        m = m + cyl(POGO_COLLAR[0], POGO_COLLAR[1], 0, py + dy, zt - 0.01)
        m = m + cyl(POGO_PLUNGER[0], Z_CAP_TOP - (zt + POGO_COLLAR[1]) + 0.01, 0, py + dy, zt + POGO_COLLAR[1] - 0.01)
        m = m + cyl(POGO_TAIL[0], POGO_TAIL[1] + 0.01, 0, py + dy, zb - POGO_TAIL[1])
        m = m + cyl(0.8, 6.0, 0, py + dy, zb - POGO_TAIL[1] - 6.0)
    return m

def make_short_plate(v):
    return box(SHORT_PLATE[0], SHORT_PLATE[1], SHORT_PLATE[2], 0, FEATURES[v]['pogo_y'], Z_CAP_TOP)

def make_led(v):
    """one WS2812B-2020 pixel lying in its pocket, LED up; 3 wires from the DIN end down the wire hole"""
    zb = Z_CAP_TOP - LED_POCKET_DEPTH
    yc, hy = led_centre(v), FEATURES[v]['led_hole_y']
    m = box(LED_SEG[0], LED_SEG[1], LED_SEG[2], 0, yc, zb) + box(*LED_BODY, x=0, y=yc, z=zb + LED_SEG[2])
    ye = yc - LED_SEG[1] / 2 + 0.6                    # solder pads at the DIN end
    for dx in (-1.6, 0.0, 1.6):
        m = m + Manifold.cylinder(ye - hy, 0.35, 0.35, 16).rotate((-90, 0, 0)).translate((dx * 0.5, hy, zb + LED_SEG[2] + 0.35))
        m = m + cyl(0.7, 7.0, dx * 0.5, hy, zb + LED_SEG[2] + 0.35 - 7.0)
    return m

# ---------------- layer 5: topper ----------------
def make_topper(v):
    """hollow diffuser on the key top, with a lip all round that hugs the top LIP_H of the key"""
    f = FEATURES[v]
    top = Z_CAP_TOP
    grow = FIT + TAPER * LIP_H / CAP_H                # the key is a little wider LIP_H below its top
    outer = union([rbox_xy(x0 - grow - LIP_T, y0 - grow - LIP_T, x1 + grow + LIP_T, y1 + grow + LIP_T,
                           TOPPER_H + LIP_H, CAP_R + LIP_T, top - LIP_H) for x0, y0, x1, y1 in top_pieces(v)])
    seat = union([rbox_xy(x0 - grow, y0 - grow, x1 + grow, y1 + grow, LIP_H + 1, CAP_R, top - LIP_H - 1)
                  for x0, y0, x1, y1 in top_pieces(v)])
    shell = outer - seat
    # hollow where the key is wide enough, except solid blocks around the magnets and the pogo shim
    cav = []
    for x0, y0, x1, y1 in top_pieces(v):
        if x1 - x0 - 2 * TOPPER_WALL < 4.0:
            continue
        cav.append(rbox_xy(x0 + TOPPER_WALL, y0 + TOPPER_WALL, x1 - TOPPER_WALL, y1 - TOPPER_WALL,
                           TOPPER_H - DIFFUSER_T + 1, 1.0, top - 1))
    blocks = [box(40, MAG_POCKET_D + 2.4, 20, y=my, z=top - 5) for mx, my in f['mags']]
    blocks.append(box(40, SHORT_PLATE[1] + 2.5, 20, y=f['pogo_y'], z=top - 5))
    shell = shell - (union(cav) - union(blocks))
    shell = shell - box(SHORT_PLATE[0] + 2 * FIT, SHORT_PLATE[1] + 2 * FIT, SHORT_PLATE[2] + 1, 0, f['pogo_y'], top - 1)
    for mx, my in f['mags']:
        shell = shell - cyl(MAG_POCKET_D, MAG_POCKET_DEPTH + 1, mx, my, top - 1)
    return shell

def make_magnets(v, which):
    zs = {'key': Z_CAP_TOP - MAG_T, 'topper': Z_CAP_TOP}[which]
    return union([cyl(MAG_D, MAG_T, mx, my, zs) for mx, my in FEATURES[v]['mags']])

# ---------------- parts list ----------------
def layers(v):
    """(file name, layer key, builder, RGBA) for key type v ('grey' / 'black'; white is built from grey)"""
    key_col = {'grey': (150, 150, 155, 255), 'black': (45, 45, 50, 255)}[v]
    return [
        ('1_pcb',             'pcb',    lambda: make_pcb() + pcb_wire_stubs(v), (30, 110, 50, 255)),
        ('2_foam',            'foam',   lambda: make_foam(v),         (235, 225, 200, 255)),
        ('3_acrylic_plate',   'plate',  lambda: make_plate(v),        (150, 200, 235, 150)),
        ('3a_switch',         'plate',  make_switch,                  (60, 60, 60, 255)),
        ('3b_stabilizer',     'plate',  make_stabilizer,              (200, 200, 205, 255)),
        ('4_key',             'key',    lambda: make_key(v),          key_col),
        ('4a_rgb_led_strip_piece', 'key', lambda: make_led(v),        (255, 40, 200, 255)),
        ('4c_pogo_connector', 'key',    lambda: make_pogo(v),         (30, 30, 30, 255)),
        ('4b_magnets_key',    'key',    lambda: make_magnets(v, 'key'), (120, 120, 130, 255)),
        ('5_topper',          'topper', lambda: make_topper(v),       (255, 214, 150, 165)),
        ('5b_short_plate',    'topper', lambda: make_short_plate(v),  (205, 160, 60, 255)),
        ('5a_magnets_topper', 'topper', lambda: make_magnets(v, 'topper'), (120, 120, 130, 255)),
    ]

KEYS = ('white', 'black', 'grey')
def source(k):
    return 'grey' if k == 'white' else k

def turn(m, k):
    """white = grey turned 180 degrees about the switch centre (the whole stack, PCB included)"""
    return m.rotate((0, 0, 180)) if k == 'white' else m

def build(k):
    """[(name, layer key, manifold, colour)] for key type k"""
    out = []
    for name, lay, fn, col in layers(source(k)):
        m = turn(fn(), k)
        if k == 'white' and name == '4_key':
            col = (240, 240, 240, 255)
        out.append((name, lay, m, col))
    return out

# ---------------- output ----------------
def to_trimesh(m, color=None):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=False)
    if color is not None:
        mat = trimesh.visual.material.PBRMaterial(baseColorFactor=[c / 255 for c in color], metallicFactor=0.0,
                                                  roughnessFactor=0.7, alphaMode='BLEND' if color[3] < 255 else 'OPAQUE')
        t.visual = trimesh.visual.TextureVisuals(material=mat)
    return t

def dxf(path, items):
    """minimal R12 DXF, layer CUT: ('rect', x0, y0, x1, y1) | ('circle', x, y, d) | ('rrect', x0, y0, x1, y1, r)
    | ('poly', [(x, y), ...])"""
    L = ['0', 'SECTION', '2', 'ENTITIES']
    def line(a, b):
        L.extend(['0', 'LINE', '8', 'CUT', '10', f'{a[0]:.4f}', '20', f'{a[1]:.4f}', '11', f'{b[0]:.4f}', '21', f'{b[1]:.4f}'])
    for it in items:
        if it[0] == 'rect':
            x0, y0, x1, y1 = it[1:]
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
            for a, b in zip(pts, pts[1:]):
                line(a, b)
        elif it[0] == 'poly':
            pts = list(it[1]) + [it[1][0]]
            for a, b in zip(pts, pts[1:]):
                line(a, b)
        elif it[0] == 'circle':
            L.extend(['0', 'CIRCLE', '8', 'CUT', '10', f'{it[1]:.4f}', '20', f'{it[2]:.4f}', '40', f'{it[3] / 2:.4f}'])
        elif it[0] == 'rrect':
            x0, y0, x1, y1, r = it[1:]
            for a, b in [((x0 + r, y0), (x1 - r, y0)), ((x1, y0 + r), (x1, y1 - r)),
                         ((x1 - r, y1), (x0 + r, y1)), ((x0, y1 - r), (x0, y0 + r))]:
                line(a, b)
            for cx, cy, a0 in [(x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]:
                L.extend(['0', 'ARC', '8', 'CUT', '10', f'{cx:.4f}', '20', f'{cy:.4f}', '40', f'{r:.4f}',
                          '50', f'{a0:.1f}', '51', f'{a0 + 90:.1f}'])
    L.extend(['0', 'ENDSEC', '0', 'EOF'])
    open(path, 'w').write('\n'.join(L) + '\n')

def turn_items(items, k):
    if k != 'white':
        return items
    out = []
    for it in items:
        if it[0] in ('rect', 'rrect'):
            x0, y0, x1, y1 = it[1:5]
            out.append((it[0], -x1, -y1, -x0, -y0) + tuple(it[5:]))
        elif it[0] == 'poly':
            out.append(('poly', [(-x, -y) for x, y in it[1]]))
        else:
            out.append(('circle', -it[1], -it[2], it[3]))
    return out

def merged_cuts(rects):
    """overlapping rectangles merged into closed outlines, so the laser cuts each opening once"""
    cs = CrossSection.batch_boolean([CrossSection.square((x1 - x0, y1 - y0)).translate((x0, y0))
                                     for x0, y0, x1, y1 in rects], OpType.Add)
    return [('poly', [(round(x, 4), round(y, 4)) for x, y in loop]) for loop in cs.to_polygons()]

def cut_items(k, which):
    v = source(k)
    outline = ('rrect', -BOARD_W / 2, -BOARD_D / 2, BOARD_W / 2, BOARD_D / 2, 1.0)
    if which == 'plate':
        items = [outline] + merged_cuts(plate_cuts(v)) + [('circle', x, y, SCREW_D) for x, y in SCREWS]
    else:
        items = [outline] + merged_cuts(foam_cuts(v)) + [('circle', x, y, SCREW_D + 1.0) for x, y in SCREWS]
    return turn_items(items, k)

def write_key(k):
    d = os.path.join(HERE, k)
    stl_dir, cut_dir = os.path.join(d, 'stl'), os.path.join(d, 'cut-files')
    os.makedirs(stl_dir, exist_ok=True); os.makedirs(cut_dir, exist_ok=True)
    parts = build(k)
    exploded, assembled, ex_scene, as_scene = [], [], trimesh.Scene(), trimesh.Scene()
    key, key_scene, kx, kx_scene = [], trimesh.Scene(), [], trimesh.Scene()
    for name, lay, m, col in parts:
        assert m.status().name == 'NoError', (k, name)
        to_trimesh(m).export(os.path.join(stl_dir, f'{name}.stl'))
        e = m.translate((0, 0, part_explode(name, lay)))
        exploded.append(e); assembled.append(m)
        ex_scene.add_geometry(to_trimesh(e, col), node_name=name, geom_name=name)
        as_scene.add_geometry(to_trimesh(m, col), node_name=name, geom_name=name)
        if lay in ('key', 'topper'):
            key.append(m); key_scene.add_geometry(to_trimesh(m, col), node_name=name, geom_name=name)
            ke = m.translate((0, 0, KEY_EXPLODE[name]))
            kx.append(ke); kx_scene.add_geometry(to_trimesh(ke, col), node_name=name, geom_name=name)
        print(f'{k:6s} {name:24s} {m.volume():9.1f} mm^3')
    to_trimesh(union(exploded)).export(os.path.join(d, 'stack_exploded.stl'))
    to_trimesh(union(assembled)).export(os.path.join(d, 'stack_assembled.stl'))
    ex_scene.export(os.path.join(d, 'stack_exploded.glb')); as_scene.export(os.path.join(d, 'stack_assembled.glb'))
    to_trimesh(union(key)).export(os.path.join(d, 'key_assembled.stl')); key_scene.export(os.path.join(d, 'key_assembled.glb'))
    to_trimesh(union(kx)).export(os.path.join(d, 'key_exploded.stl')); kx_scene.export(os.path.join(d, 'key_exploded.glb'))
    dxf(os.path.join(cut_dir, 'acrylic_plate_1.5mm.dxf'), cut_items(k, 'plate'))
    dxf(os.path.join(cut_dir, 'foam_3.5mm.dxf'), cut_items(k, 'foam'))

def check():
    """a few fit checks that are easy to break when editing the numbers"""
    for v in ('grey', 'black'):
        f = FEATURES[v]
        y0, y1 = led_span(v)
        assert width_at(v, (y0 + y1) / 2) > LED_SEG[0] / 2 + 1.0, (v, 'LED pocket too wide for the key')
        for c in plate_cuts(v)[1:2]:   # the J2 wire slot must leave a web to the switch, stabilizer and wire cut-outs
            for o in [plate_cuts(v)[0]] + plate_cuts(v)[2:]:
                gap = max(o[1] - c[3], c[1] - o[3], o[0] - c[2], c[0] - o[2])
                assert gap >= 1.2, (v, 'thin plate web', c, o, gap)
        sw, ws = plate_cuts(v)[0], wire_slot_2d()
        assert sw[0] - ws[2] >= 1.2, (v, 'thin web between the wire slot and the switch cut-out', sw[0] - ws[2])
        for mx, my in f['mags']:
            assert width_at(v, my) > abs(mx) + MAG_POCKET_D / 2 + 0.8, (v, 'magnet too close to the edge', mx, my)
        print(f'{v}: LED pocket y {y0:.2f}..{y1:.2f}, pogo y {f["pogo_y"]}, magnets {f["mags"]}')

def main():
    check()
    for k in KEYS:
        write_key(k)
    print('wrote white/, black/, grey/ (stl/, cut-files/, stack_* and key_* .stl/.glb)')

if __name__ == '__main__':
    main()
