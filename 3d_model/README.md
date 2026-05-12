# Streamdeck-v1 – 3D Printable Enclosure

Parametric **OpenSCAD** models for the two-piece enclosure.  
Download [OpenSCAD](https://openscad.org/) (free, cross-platform) to open and export these files.

---

## Design highlights (minimalist redesign)

- **Rounded corners** – 4 mm outer radius on both the base and the faceplate for a sleek, modern look.
- **Slimmer profile** – base depth reduced from 22 mm to **18 mm**.
- **Chamfered holes** – switch holes and TFT window have a subtle inner-face bevel for easier component insertion while keeping the visible face pixel-clean.
- **Rotary encoder / volume potentiometer** – a 7.5 mm bushing hole on the **right side wall** of the base, centred at 60 % of the device length and mid-depth, fits a standard **EC11 encoder** (or any potentiometer with a ≤ 7 mm bushing).  The assembly preview shows a round knob protruding from that wall.

---

## Files

| File | Purpose |
|---|---|
| `streamdeck_faceplate.scad` | Top plate – display window + 10 switch holes + snap tabs |
| `streamdeck_base.scad` | Shell – Pico standoffs, TFT ledge, USB cutout, encoder hole, rubber feet |
| `streamdeck_assembly.scad` | Exploded preview of both parts + encoder knob (not for printing) |

---

## Key parameters

### Faceplate (`streamdeck_faceplate.scad`)

| Parameter | Default | Description |
|---|---|---|
| `plate_w` | 90 mm | Overall width |
| `plate_h` | 145 mm | Overall height |
| `plate_thick` | 3 mm | Plate thickness |
| `corner_r` | 4 mm | Outer corner radius |
| `tft_win_w` | 29.5 mm | Display window width (active area + 0.8 mm tolerance) |
| `tft_win_h` | 36.5 mm | Display window height |
| `tft_chamfer` | 0.6 mm | Inner bevel on display window |
| `sw_hole` | 14.0 mm | MX switch hole (use 14.2 for a looser fit) |
| `sw_pitch` | 19.05 mm | Switch centre-to-centre spacing |
| `sw_chamfer` | 0.6 mm | Inner bevel on switch holes for easy insertion |
| `screw_d` | 3.2 mm | M3 corner screw clearance hole |
| `screw_margin` | 4.5 mm | Corner screw distance from edge (increased for rounded corners) |

### Base shell (`streamdeck_base.scad`)

| Parameter | Default | Description |
|---|---|---|
| `shell_w` | 90 mm | Outer width |
| `shell_h` | 145 mm | Outer height |
| `shell_d` | 18 mm | Outer depth (slimmer than original 22 mm) |
| `wall` | 2.0 mm | Shell wall thickness |
| `corner_r` | 4 mm | Outer corner radius |
| `usb_w` | 9 mm | Micro-USB cutout width |
| `usb_h` | 4 mm | Micro-USB cutout height |
| `pico_standoff_h` | 3.0 mm | Pico PCB standoff height above floor |
| `pot_hole_d` | 7.5 mm | Encoder / pot bushing hole diameter |
| `pot_y` | `shell_h × 0.6` | Encoder hole position along device length |
| `pot_z` | `shell_d / 2` | Encoder hole height on the side wall |

---

## Rotary encoder / potentiometer

The base has a **7.5 mm circular hole** on the right side wall (x = 90 face).  
Recommended part: **EC11 rotary encoder** (6 mm shaft, ~12 mm body, M7 thread on bushing).  
The `pot_hole_d = 7.5 mm` is a **clearance hole** sized to pass the encoder's threaded bushing; it is not a pilot hole for tapping.

Steps:
1. Insert the encoder from inside the shell; the bushing pokes through the right wall.
2. Secure with the included nut on the outside.
3. Press on a 18 mm knob cap (D-shaft or knurled).
4. Connect the three pins (CLK, DT, SW) to any three GPIO pins on the Pico.

---

## How to export STL files

1. Open `streamdeck_faceplate.scad` in OpenSCAD.
2. Press **F6** to do a full render.
3. Go to **File → Export → Export as STL…** and save as `faceplate.stl`.
4. Repeat for `streamdeck_base.scad` → save as `base.stl`.

---

## Print settings

| Setting | Recommendation |
|---|---|
| Material | PLA (easy) or PETG (more durable) |
| Layer height | 0.15–0.20 mm |
| Infill | 20–30 % |
| Walls / perimeters | 3 |
| Supports | Not needed for either part |
| Faceplate orientation | Face **down** (best detail on switch holes and display window) |
| Base orientation | Open face **up** |

---

## Assembly

1. Press the 10 MX switches into the faceplate from **above** – they snap at 14.0 mm.
2. Rest the TFT PCB on the two ledges inside the base.
3. Seat the Raspberry Pi Pico on the two standoffs and secure with M2 × 6 mm screws.
4. Mount the rotary encoder in the right-side-wall hole and secure the nut on the outside.
5. Route wires; close the faceplate onto the base – the four snap tabs click into the side slots.
6. Optionally add two M3 × 8 mm screws through the corner holes for extra rigidity.

---

## Customising

All dimensions live at the top of each `.scad` file as named variables.

### Common adjustments

- **Loose switch fit** → change `sw_hole = 14.0` to `sw_hole = 14.2`
- **Sharper corners** → decrease `corner_r` (set to 0 for fully square)
- **More rounded** → increase `corner_r` (max ~8 mm before corners meet)
- **Thicker walls** → increase `wall` in the base file
- **Different depth** → change `shell_d` and update `base_depth` in the assembly file to match
- **Encoder position** → adjust `pot_y` and/or `pot_z` in the base file
- **Display offset** → adjust `tft_x` / `tft_y` in the faceplate file

