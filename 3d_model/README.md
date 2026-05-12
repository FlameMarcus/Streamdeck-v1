# Streamdeck-v1 – 3D Printable Enclosure

Parametric **OpenSCAD** models for a sleek two-piece enclosure.  
Download [OpenSCAD](https://openscad.org/) (free, cross-platform) to open and export these files.

---

## Design highlights

- **Single-file parametric design** – all dimensions are variables at the top of `streamdeck_enclosure.scad`.  Changing `tilt_angle`, `wall_t`, or `btn_spacing` cascades through every piece of geometry automatically.
- **Angled / wedge body** – the faceplate tilts 15° toward the user.  The base has a flat bottom; the rear wall is taller than the front wall to achieve the tilt.  Side profile looks like a slim wedge.
- **Spherically-rounded 3-D corners** – the outer shell uses a `hull()` of corner spheres so every external corner (bottom, top, and edges) is smoothly filleted (r = 3.5 mm).
- **Tight internal corners** – all interior corners use r = 1 mm fillets.
- **Micro-USB cutout** – 12 × 7 mm slot on the front face, centred on the Pico's USB port.
- **EC11 encoder hole** – 7 mm bushing hole on the right side wall, vertically centred.
- **4 × M2 Pico standoffs** – PCB raised 2.5 mm above base floor.
- **TFT display ledge** – two inward rails inside the base, positioned at the correct height for the display module.
- **Cable management channel** – 8 mm × 4 mm groove on the outer bottom face, with smooth entry ramps at both ends.  Corner feet raise the base above the desk so the channel clears the surface.
- **FDM-ready** – no overhangs > 45 °; $fn = 64 for smooth curves.

---

## Files

| File | Purpose |
|---|---|
| `streamdeck_enclosure.scad` | **Primary file** – complete single-file parametric design; all modules and parameters live here |
| `streamdeck_faceplate.scad` | Thin wrapper – renders `faceplate()` only for STL export |
| `streamdeck_base.scad` | Thin wrapper – renders `base_shell()` only for STL export |
| `streamdeck_assembly.scad` | Thin wrapper – renders `assembly()` preview (not for printing) |

---

## Key parameters  (`streamdeck_enclosure.scad`)

| Parameter | Default | Description |
|---|---|---|
| `fit_tolerance` | 0.2 mm | Clearance added to each side of every cutout |
| `wall_t` | 2.5 mm | Uniform wall / floor / ceiling thickness |
| `shell_w` | 90 mm | Outer width (X, left–right) |
| `shell_d` | 145 mm | Outer depth (Y, front–back) |
| `tilt_angle` | 15° | Faceplate tilt; cascades to rear_wall_h and plate_l |
| `front_wall_h` | 12 mm | Front wall height above desk |
| `fillet_ext` | 3.5 mm | External corner fillet radius |
| `fillet_int` | 1.0 mm | Internal corner fillet radius |
| `plate_thick` | 3.0 mm | Faceplate thickness |
| `btn_spacing` | 19.0 mm | MX centre-to-centre pitch |
| `btn_hole_size` | 14.0 mm | MX switch hole side (use 14.2 for looser fit) |
| `tft_win_w` | 28.43 mm | Viewing window width (with tolerance) |
| `tft_win_h` | 35.40 mm | Viewing window height (with tolerance) |
| `standoff_h` | 2.5 mm | Pico standoff height above floor |
| `enc_hole_d` | 7.4 mm | EC11 bushing hole (with tolerance) |
| `usb_w` | 12.4 mm | Micro-USB cutout width (with tolerance) |
| `usb_h` | 7.4 mm | Micro-USB cutout height (with tolerance) |
| `cable_ch_w` | 8.0 mm | Cable channel width |
| `cable_ch_d` | 4.0 mm | Cable channel depth |
| `explode` | 0 | Set to 1 in `assembly()` for exploded view |

---

## How to export STL files

### Faceplate
1. Open `streamdeck_faceplate.scad` in OpenSCAD.
2. Press **F6** for a full render.
3. **File → Export → Export as STL…** → save as `faceplate.stl`.

### Base shell
1. Open `streamdeck_base.scad` in OpenSCAD.
2. Press **F6**, then export as `base.stl`.

---

## Print settings

| Setting | Recommendation |
|---|---|
| Material | PLA (easy) or PETG (more durable) |
| Layer height | 0.15–0.20 mm |
| Infill | 25–30 % |
| Walls / perimeters | 3 |
| Top / bottom layers | 4 |
| Supports | **Not needed** for either part |

### Print orientation

| Part | Orientation | Reason |
|---|---|---|
| **Faceplate** | Outer (visible) face **down** on the bed | Best surface finish on switch holes and display window; no supports needed |
| **Base shell** | Open face **up** (flat bottom on bed) | Wedge shape prints cleanly; all walls taper inward above the flat base |

---

## Assembly

1. Press 10 MX switches into the faceplate from above – they snap at 14.0 mm holes.
2. Rest the TFT module in the faceplate pocket (1 mm lip retains it).
3. Seat the Raspberry Pi Pico on the four standoffs; secure with M2 × 6 mm screws.
4. Mount the EC11 encoder in the right-side-wall hole; secure with the M7 nut.
5. Route the USB cable through the front cutout; tuck excess in the bottom channel.
6. Close the faceplate onto the base; secure with 4 × M3 × 16 mm screws through the corner holes into the base bosses.

---

## Customising

All dimensions are variables at the top of `streamdeck_enclosure.scad`.

| Goal | Change |
|---|---|
| Looser switch fit | `btn_hole_size = 14.2` |
| Shallower tilt | `tilt_angle = 10` |
| Thicker walls | `wall_t = 3.0` |
| More FDM tolerance | `fit_tolerance = 0.3` |
| Encoder larger bushing | increase `enc_hole_d` |
| Shorter front edge | decrease `front_wall_h` |
