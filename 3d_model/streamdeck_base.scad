// =============================================================
//  Streamdeck-v1  –  Base Shell  (Minimalist Redesign)
//  Print with the open face up (no supports needed inside).
//  All dimensions in millimetres.
// =============================================================

// ── Outer shell dimensions ────────────────────────────────────
shell_w        = 90;
shell_h        = 145;
shell_d        = 18;      // reduced depth for a slimmer profile
wall           = 2.0;     // shell wall thickness
corner_r       = 4.0;     // outer corner radius (rounded minimalist look)

// ── Faceplate snap-tab slots ──────────────────────────────────
tab_slot_w     = 9;       // slightly wider than the tab
tab_slot_h     = 1.6;     // slightly taller than the tab protrusion
tab_slot_thick = 1.6;

// ── Raspberry Pi Pico standoffs ───────────────────────────────
//   Pico board: 51 × 21 mm, mounting holes ~4.8 mm from each end,
//   centred on the 21 mm axis.  Hole dia = 2.1 mm (M2 clearance).
pico_w          = 51;
pico_h          = 21;
pico_hole_d     = 2.2;    // M2 clearance
pico_standoff_d = 5;      // standoff outer diameter
pico_standoff_h = 3.0;    // height above floor (keeps PCB clear of wires)
// Pico centred horizontally, near the bottom of the shell
pico_x0         = (shell_w - pico_w) / 2;
pico_y0         = wall + 4;
// Mounting holes: 2 mm from each short edge, centred on long axis
pico_hole_offsets = [
    [2,          pico_h / 2],
    [pico_w - 2, pico_h / 2]
];

// ── TFT display ledge ─────────────────────────────────────────
//   Two thin rails near the top hold the TFT PCB (36 × 47 mm).
tft_pcb_w      = 36;
tft_pcb_h      = 47;
tft_shelf_h    = 2;       // shelf thickness
tft_shelf_d    = 2.5;     // how far the shelf protrudes inward
tft_x0         = (shell_w - tft_pcb_w) / 2;
tft_y0         = shell_h - wall - tft_pcb_h - tft_shelf_h;

// ── Micro-USB cutout (bottom short side, y = 0 face) ──────────
usb_w          = 9;       // plug width + tolerance
usb_h          = 4;       // plug height + tolerance
usb_x          = (shell_w - usb_w) / 2;
usb_z          = wall + 1;

// ── Rotary encoder / potentiometer (right side wall) ──────────
//   EC11-style encoder: 7.5 mm bushing hole; body sits inside.
//   Positioned 60 % up the device length, mid-depth – naturally
//   reachable while pressing buttons.
pot_hole_d     = 7.5;
pot_y          = shell_h * 0.6;   // 60 % along the length
pot_z          = shell_d / 2;     // vertically centred on the wall

// ── Corner screw bosses (match faceplate M3 holes) ────────────
boss_d         = 7;
boss_h         = shell_d - wall;  // nearly full depth
boss_hole_d    = 2.5;             // M3 self-tap pilot hole
screw_margin   = 4.5;             // increased from 3.5 mm for rounded corner clearance

eps = 0.01;

// ── Helper: rounded-corner box via hull of four corner cylinders
module rounded_box(w, h, d, r) {
    hull()
        for (x = [r, w - r])
            for (y = [r, h - r])
                translate([x, y, 0])
                    cylinder(r=r, h=d, $fn=48);
}

// =============================================================
module base_shell() {
    difference() {
        // ── Outer rounded solid ───────────────────────────────
        rounded_box(shell_w, shell_h, shell_d, corner_r);

        // ── Hollow interior (open top) ────────────────────────
        translate([wall, wall, wall])
            rounded_box(
                shell_w - 2*wall,
                shell_h - 2*wall,
                shell_d,                    // cut all the way to open top
                max(corner_r - wall, 0.5)   // inner corner radius
            );

        // ── Micro-USB cutout on bottom face (y = 0 side) ──────
        translate([usb_x, -eps, usb_z])
            cube([usb_w, wall + 2*eps, usb_h]);

        // ── Rotary encoder hole on right side wall ────────────
        translate([shell_w - wall - eps, pot_y, pot_z])
            rotate([0, 90, 0])
                cylinder(d=pot_hole_d, h=wall + 2*eps, $fn=32);

        // ── Faceplate snap-tab slots (inside top rim) ─────────
        for (ty = [shell_h * 0.33, shell_h * 0.66]) {
            // left slot
            translate([-eps, ty - tab_slot_w/2,
                       shell_d - tab_slot_h - wall])
                cube([tab_slot_thick + eps, tab_slot_w,
                      tab_slot_h + eps]);
            // right slot
            translate([shell_w - tab_slot_thick, ty - tab_slot_w/2,
                       shell_d - tab_slot_h - wall])
                cube([tab_slot_thick + eps, tab_slot_w,
                      tab_slot_h + eps]);
        }

        // ── M3 screw holes through corner bosses ──────────────
        for (cx = [screw_margin, shell_w - screw_margin - boss_d/2])
            for (cy = [screw_margin, shell_h - screw_margin - boss_d/2])
                translate([cx + boss_d/2 - boss_hole_d/2,
                           cy + boss_d/2 - boss_hole_d/2,
                           -eps])
                    cylinder(d=boss_hole_d, h=boss_h + 2*eps, $fn=20);
    }

    // ── Corner screw bosses (inside the shell) ────────────────
    for (cx = [wall, shell_w - wall - boss_d])
        for (cy = [wall, shell_h - wall - boss_d])
            translate([cx, cy, wall])
                cylinder(d=boss_d, h=boss_h, $fn=20);

    // ── Pico standoffs ────────────────────────────────────────
    for (ho = pico_hole_offsets)
        translate([pico_x0 + ho[0] - pico_standoff_d/2,
                   pico_y0 + ho[1] - pico_standoff_d/2,
                   wall]) {
            difference() {
                cylinder(d=pico_standoff_d, h=pico_standoff_h, $fn=20);
                translate([0, 0, -eps])
                    cylinder(d=pico_hole_d, h=pico_standoff_h + 2*eps,
                             $fn=20);
            }
        }

    // ── TFT display shelf (left and right rails) ──────────────
    translate([tft_x0 - tft_shelf_d, tft_y0, wall])
        cube([tft_shelf_d, tft_pcb_h, tft_shelf_h]);
    translate([tft_x0 + tft_pcb_w, tft_y0, wall])
        cube([tft_shelf_d, tft_pcb_h, tft_shelf_h]);

    // ── Rubber-foot bumps (4 × pads on outer bottom face) ─────
    foot_size   = 8;
    foot_h      = 1.8;
    foot_margin = 6;
    for (fx = [foot_margin, shell_w - foot_margin - foot_size])
        for (fy = [foot_margin, shell_h - foot_margin - foot_size])
            translate([fx, fy, 0])
                cube([foot_size, foot_size, foot_h]);
}

base_shell();
