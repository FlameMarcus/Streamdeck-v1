// =============================================================
//  Streamdeck-v1  –  Complete Parametric Enclosure
//  Single-file, production-quality FDM design.
//
//  Open in OpenSCAD: F5 for preview, F6 for full render.
//  All dimensions in millimetres.
//
//  Two printable parts:
//    faceplate()   – angled top plate (print face-down)
//    base_shell()  – wedge body      (print open-face-up)
//
//  assembly()  – positioned preview (NOT for printing)
// =============================================================

$fn = 64;   // Global arc resolution; 64 gives smooth FDM curves

// ═══════════════════════════════════════════════════════════════
//  1.  PARAMETERS BLOCK
//      Change any value here – geometry updates automatically.
// ═══════════════════════════════════════════════════════════════

// ── General tolerances & overlap ───────────────────────────────
fit_tolerance  = 0.2;   // Clearance added to each side of every cutout (mm)
wall_t         = 2.5;   // Uniform wall / floor / ceiling thickness (mm)
eps            = 0.01;  // Tiny overlap used in boolean operations

// ── Outer footprint ────────────────────────────────────────────
shell_w        = 90;    // Device width  (X, left–right) in mm
shell_d        = 145;   // Device depth  (Y, front–back, desk footprint) in mm

// ── Tilt / wedge geometry ──────────────────────────────────────
tilt_angle     = 15;    // Faceplate tilt in degrees; rear wall is taller
front_wall_h   = 12;    // Height of the front wall above desk (mm)
rear_wall_h    = front_wall_h + shell_d * tan(tilt_angle); // derived

// ── Corner fillet radii ────────────────────────────────────────
fillet_ext     = 3.5;   // External corner radius – large, premium look
fillet_int     = 1.0;   // Internal corner radius – tight

// ── Faceplate ─────────────────────────────────────────────────
plate_thick    = 3.0;   // Faceplate thickness, measured perpendicular to face
plate_w        = shell_w;
plate_l        = shell_d / cos(tilt_angle); // faceplate length along its own plane

// ── Button grid (5 rows × 2 cols, MX-compatible) ───────────────
btn_rows       = 5;
btn_cols       = 2;
btn_spacing    = 19.0;  // MX centre-to-centre pitch (mm)
btn_hole_size  = 14.0;  // MX switch hole side length (mm)
btn_chamfer    = 0.6;   // Inner bevel on switch holes (easier insertion)
btn_grid_span  = (btn_cols - 1) * btn_spacing;  // X span of column centres
btn_x0         = (plate_w - btn_grid_span - btn_hole_size) / 2; // left hole X
btn_y0         = 7.0;   // Y offset from faceplate bottom edge to row-0 hole

// ── TFT display (1.8" ST7735S, portrait orientation) ───────────
tft_win_w      = 28.03 + 2 * fit_tolerance;  // Viewing window width  (X)
tft_win_h      = 35.00 + 2 * fit_tolerance;  // Viewing window height (Y)
tft_mod_w      = 36.00 + 2 * fit_tolerance;  // Module PCB width  (retaining)
tft_mod_h      = 47.00 + 2 * fit_tolerance;  // Module PCB height (retaining)
tft_lip_depth  = 1.0;                         // Recessed pocket depth on inner face
tft_top_margin = 8.0;                         // Gap from faceplate top to window
tft_x0         = (plate_w - tft_win_w) / 2;
tft_y0         = plate_l - tft_top_margin - tft_win_h;
tft_mod_x0     = (plate_w - tft_mod_w) / 2;
tft_mod_y0     = tft_y0 - (tft_mod_h - tft_win_h) / 2;

// ── Raspberry Pi Pico standoffs ────────────────────────────────
pico_w         = 51.0;  // PCB long dimension  (along X in shell)
pico_d         = 21.0;  // PCB short dimension (along Y; USB port at Y-min end)
standoff_h     = 2.5;   // PCB raised height above base floor
standoff_od    = 5.0;   // Standoff outer diameter
standoff_id    = 2.2 + 2 * fit_tolerance;  // M2 clearance hole
pico_x0        = (shell_w - pico_w) / 2;  // Pico centred on X
pico_y0        = wall_t;                   // Pico flush against front inner wall
// Four standoffs at PCB corners, 3 mm inset from PCB edge
pico_mounts    = [[3, 3], [pico_w-3, 3], [3, pico_d-3], [pico_w-3, pico_d-3]];

// ── Rotary encoder EC11 (right side wall) ──────────────────────
enc_hole_d     = 7.0 + 2 * fit_tolerance;           // Bushing clearance hole
enc_y          = shell_d / 2;                        // Centred along device depth
enc_z          = (front_wall_h + enc_y * tan(tilt_angle)) / 2; // mid-wall height

// ── Micro-USB cutout (front face, aligned with Pico port) ───────
usb_w          = 12.0 + 2 * fit_tolerance;  // Cutout width
usb_h          =  7.0 + 2 * fit_tolerance;  // Cutout height
usb_x          = (shell_w - usb_w) / 2;    // Centred on front face
usb_z          = wall_t + standoff_h;       // Above standoff level

// ── Cable management channel (bottom outer face) ───────────────
cable_ch_w     = 8.0;   // Channel width (X direction)
cable_ch_d     = 4.0;   // Channel depth (Z, below outer bottom face)
cable_ch_r     = 2.0;   // Entry fillet radius at front / rear ends
cable_ch_x0    = (shell_w - cable_ch_w) / 2;  // Centred on X

// ── TFT display ledge (two rails inside base) ──────────────────
tft_ledge_proj = 2.5;   // Ledge protrusion inward from side wall
tft_ledge_h    = 2.0;   // Ledge shelf thickness
// World Z of TFT module lower face (computed from tilt geometry)
tft_ledge_z    = front_wall_h
               + tft_y0 * sin(tilt_angle)
               + (plate_thick - tft_lip_depth) * cos(tilt_angle)
               - 4;     // subtract TFT module thickness (4 mm)
// World Y start of ledge span (projected from faceplate coords)
tft_ledge_y0   = tft_mod_y0 * cos(tilt_angle) - wall_t;
tft_ledge_len  = tft_mod_h * cos(tilt_angle) + 4; // slight overrun for clearance

// ── Corner screw bosses (4 × M3, faceplate attachment) ─────────
boss_od        = 7.0;   // Boss outer diameter
boss_id        = 2.5;   // M3 self-tap pilot hole diameter
screw_margin   = 6.0;   // Boss centre offset from outer shell edge
screw_d        = 3.2 + 2 * fit_tolerance;  // M3 clearance hole in faceplate
// Boss height at a given world-Y: reaches just under the faceplate inner face
function boss_h(y) = max(8,
    front_wall_h
    + y * tan(tilt_angle)
    + plate_thick * cos(tilt_angle)
    - wall_t - 0.4);    // 0.4 mm clearance so boss doesn't lift faceplate

// ── Corner feet (raise base so cable channel clears the desk) ──
foot_h         = cable_ch_d + 1.5;  // Must exceed channel depth
foot_sz        = 8.0;               // Foot pad square side
foot_margin    = 7.0;               // Foot inset from shell edges

// ── Assembly view ──────────────────────────────────────────────
explode        = 0;     // 0 = assembled,  1 = exploded (20 mm gap)
explode_gap    = 20;    // Separation in exploded view (mm)


// ═══════════════════════════════════════════════════════════════
//  2.  HELPER MODULES
// ═══════════════════════════════════════════════════════════════

// rounded_box – axis-aligned box with vertically-filleted edges
module rounded_box(w, d, h, r) {
    hull()
        for (cx = [r, w - r])
            for (cy = [r, d - r])
                translate([cx, cy, 0])
                    cylinder(r = r, h = h);
}

// wedge_hull – flat-bottomed wedge with spherically-rounded 3-D corners
// h_front = wall height at y=0,  h_rear = wall height at y=d
module wedge_hull(w, d, h_front, h_rear, r) {
    hull()
        for (cx = [r, w - r]) {
            translate([cx, r,     r])          sphere(r = r);  // bottom front
            translate([cx, d - r, r])          sphere(r = r);  // bottom rear
            translate([cx, r,     h_front - r]) sphere(r = r); // top front
            translate([cx, d - r, h_rear  - r]) sphere(r = r); // top rear
        }
}

// mx_hole – single MX-compatible 14 × 14 mm switch cutout with inner chamfer
module mx_hole() {
    hull() {
        // Exact opening on the outer (visible) face
        cube([btn_hole_size, btn_hole_size, plate_thick - btn_chamfer + eps]);
        // Chamfered outward on inner face for easy switch insertion
        translate([-btn_chamfer, -btn_chamfer, plate_thick - btn_chamfer])
            cube([btn_hole_size + 2*btn_chamfer,
                  btn_hole_size + 2*btn_chamfer,
                  btn_chamfer + eps]);
    }
}

// standoff – hollow M2 standoff post (boss with central pilot hole)
module standoff(h, od, id) {
    difference() {
        cylinder(d = od, h = h);
        translate([0, 0, -eps])
            cylinder(d = id, h = h + 2*eps);
    }
}


// ═══════════════════════════════════════════════════════════════
//  3.  FACEPLATE MODULE
// ═══════════════════════════════════════════════════════════════

// faceplate – angled top plate: display window, MX holes, M3 corner screws
module faceplate() {
    difference() {
        // ── Solid plate body with large rounded corners ───────────
        rounded_box(plate_w, plate_l, plate_thick, fillet_ext);

        // ── TFT viewing window (full-depth cutout, outer face exact) ──
        translate([tft_x0, tft_y0, -eps])
            cube([tft_win_w, tft_win_h, plate_thick + 2*eps]);

        // ── TFT module retaining pocket (1 mm lip on inner face) ──
        //    The module PCB rests in this pocket; the lip holds it flush.
        translate([tft_mod_x0, tft_mod_y0, plate_thick - tft_lip_depth])
            cube([tft_mod_w, tft_mod_h, tft_lip_depth + 2*eps]);

        // ── 5 × 2 MX switch holes ─────────────────────────────────
        for (col = [0 : btn_cols - 1])
            for (row = [0 : btn_rows - 1])
                translate([
                    btn_x0 + col * btn_spacing,
                    btn_y0 + row * btn_spacing,
                    -eps
                ])
                    mx_hole();

        // ── 4 × M3 corner screw clearance holes ───────────────────
        for (cx = [screw_margin, plate_w - screw_margin])
            for (cy = [screw_margin, plate_l - screw_margin])
                translate([cx, cy, -eps])
                    cylinder(d = screw_d, h = plate_thick + 2*eps);
    }
}


// ═══════════════════════════════════════════════════════════════
//  4.  BASE SHELL MODULE
// ═══════════════════════════════════════════════════════════════

// base_shell – wedge body: Pico standoffs, USB cutout, encoder hole,
//              TFT ledge, cable channel, M3 bosses, corner feet
module base_shell() {

    difference() {
        // ── Outer wedge body (spherically-rounded corners throughout) ──
        wedge_hull(shell_w, shell_d, front_wall_h, rear_wall_h, fillet_ext);

        // ── Hollow interior (open at angled top face) ──────────────
        //    Shifted in by wall_t on all sides.  Extra height ensures the
        //    void pierces the angled top completely, leaving it fully open.
        translate([wall_t, wall_t, wall_t])
            wedge_hull(
                shell_w - 2*wall_t,
                shell_d - 2*wall_t,
                front_wall_h - wall_t + 30,   // exceeds outer at front → open
                rear_wall_h  - wall_t + 30,   // exceeds outer at rear  → open
                fillet_int
            );

        // ── Micro-USB cutout on front face (Y = 0 wall) ────────────
        translate([usb_x, -eps, usb_z])
            cube([usb_w, wall_t + 2*eps, usb_h]);

        // ── EC11 encoder bushing hole on right side wall (X = shell_w) ─
        translate([shell_w - wall_t - eps, enc_y, enc_z])
            rotate([0, 90, 0])
                cylinder(d = enc_hole_d, h = wall_t + 2*eps);

        // ── Cable management channel (outer bottom face, centred on X) ─
        //    8 mm wide × 4 mm deep groove, full Y length.
        translate([cable_ch_x0, 0, -cable_ch_d])
            cube([cable_ch_w, shell_d, cable_ch_d + eps]);

        // Front entry fillet – ramps channel open at Y = 0 face
        hull() {
            translate([cable_ch_x0, eps,        -eps])
                cube([cable_ch_w, eps, eps]);
            translate([cable_ch_x0, cable_ch_r, -cable_ch_d])
                cube([cable_ch_w, eps, cable_ch_d]);
        }
        // Rear entry fillet – mirrors above at Y = shell_d face
        hull() {
            translate([cable_ch_x0, shell_d - eps,        -eps])
                cube([cable_ch_w, eps, eps]);
            translate([cable_ch_x0, shell_d - cable_ch_r, -cable_ch_d])
                cube([cable_ch_w, eps, cable_ch_d]);
        }
    }

    // ── Raspberry Pi Pico standoffs (4 corners of PCB footprint) ──
    translate([pico_x0, pico_y0, wall_t])
        for (m = pico_mounts)
            translate([m[0] - standoff_od/2, m[1] - standoff_od/2, 0])
                standoff(standoff_h, standoff_od, standoff_id);

    // ── TFT display ledge (two inward rails on inner side walls) ──
    //    Height and Y position derived from tilt geometry so that the
    //    module aligns with the faceplate pocket when assembled.
    translate([wall_t, tft_ledge_y0, tft_ledge_z])
        cube([tft_ledge_proj, tft_ledge_len, tft_ledge_h]);
    translate([shell_w - wall_t - tft_ledge_proj, tft_ledge_y0, tft_ledge_z])
        cube([tft_ledge_proj, tft_ledge_len, tft_ledge_h]);

    // ── M3 screw bosses (4 inner corners, height reaches faceplate) ──
    for (cx = [screw_margin, shell_w - screw_margin])
        for (cy = [screw_margin, shell_d - screw_margin]) {
            bh = boss_h(cy);
            translate([cx, cy, wall_t])
                difference() {
                    cylinder(d = boss_od, h = bh);
                    translate([0, 0, -eps])
                        cylinder(d = boss_id, h = bh + 2*eps);
                }
        }

    // ── Corner feet (raise base above desk for cable channel clearance) ─
    for (fx = [foot_margin, shell_w - foot_margin - foot_sz])
        for (fy = [foot_margin, shell_d - foot_margin - foot_sz])
            translate([fx, fy, -foot_h])
                cube([foot_sz, foot_sz, foot_h]);
}


// ═══════════════════════════════════════════════════════════════
//  5.  ASSEMBLY PREVIEW MODULE
// ═══════════════════════════════════════════════════════════════

// assembly – positions faceplate and base; explode = 1 adds 20 mm gap
module assembly() {

    // Base shell: flat bottom at Z = 0 (feet go negative)
    color("DimGray", 0.92)
        base_shell();

    // Faceplate: outer face tangent to base angled top edge.
    // translate → front-bottom of angled top, rotate → tilt angle.
    // explode offset lifts it cleanly away for the exploded view.
    color("SteelBlue", 0.92)
        translate([0, 0, front_wall_h + (explode ? explode_gap : 0)])
            rotate([tilt_angle, 0, 0])
                faceplate();

    // Encoder / knob preview stub (not a printable part)
    color("Silver", 0.95)
        translate([shell_w, enc_y, enc_z])
            rotate([0, 90, 0]) {
                cylinder(d = 6,  h = 4);          // shaft stub
                translate([0, 0, 4])
                    cylinder(d = 18, h = 7);       // round knob cap
            }
}


// ═══════════════════════════════════════════════════════════════
//  6.  RENDER
// ═══════════════════════════════════════════════════════════════

assembly();
