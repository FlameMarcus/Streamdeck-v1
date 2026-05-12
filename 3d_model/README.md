# Streamdeck-v1 – 3D Printable Enclosure

Parametric **OpenSCAD** models for the two-piece enclosure.  
Download [OpenSCAD](https://openscad.org/) (free, cross-platform) to open and export these files.

---

## Files

| File | Purpose |
|---|---|
| `streamdeck_faceplate.scad` | Top plate – display window + 10 switch holes + snap tabs |
| `streamdeck_base.scad` | Shell – Pico standoffs, TFT ledge, USB cutout, rubber feet |
| `streamdeck_assembly.scad` | Exploded preview of both parts together (not for printing) |

---

## Key parameters (top of each file)

### Faceplate (`streamdeck_faceplate.scad`)

| Parameter | Default | Description |
|---|---|---|
| `plate_w` | 90 mm | Overall width |
| `plate_h` | 145 mm | Overall height |
| `plate_thick` | 3 mm | Plate thickness |
| `tft_win_w` | 29.5 mm | Display window width (active area + 0.8 mm tolerance) |
| `tft_win_h` | 36.5 mm | Display window height |
| `sw_hole` | 14.0 mm | MX switch hole (use 14.2 for a looser fit) |
| `sw_pitch` | 19.05 mm | Switch centre-to-centre spacing |
| `screw_d` | 3.2 mm | M3 corner screw clearance hole |

### Base shell (`streamdeck_base.scad`)

| Parameter | Default | Description |
|---|---|---|
| `shell_w` | 90 mm | Outer width |
| `shell_h` | 145 mm | Outer height |
| `shell_d` | 22 mm | Outer depth |
| `wall` | 2.2 mm | Shell wall thickness |
| `usb_w` | 9 mm | Micro-USB cutout width |
| `usb_h` | 4 mm | Micro-USB cutout height |
| `pico_standoff_h` | 3.5 mm | Pico PCB standoff height above floor |

---

## How to export STL files

1. Open `streamdeck_faceplate.scad` in OpenSCAD.
2. Press **F6** to do a full render (may take a few seconds).
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
4. Route wires; close the faceplate onto the base – the four snap tabs click into the side slots.
5. Optionally add two M3 × 8 mm screws through the corner holes for extra rigidity.

---

## Customising

All dimensions live at the top of each `.scad` file as named variables.  
If your TFT module or switch brand differs from the defaults, edit those values and re-export.

### Common adjustments

- **Loose switch fit** → change `sw_hole = 14.0` to `sw_hole = 14.2`
- **Thicker walls** → increase `wall` in the base file
- **Different depth** → change `shell_d` (and update `base_depth` in the assembly file to match)
- **Display offset** → adjust `tft_x` / `tft_y` in the faceplate file
