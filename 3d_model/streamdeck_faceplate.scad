// =============================================================
//  Streamdeck-v1  –  Faceplate / Top Plate  (Minimalist Redesign)
//  Print face-down for best hole accuracy.
//  All dimensions in millimetres.
// =============================================================

// ── Global parameters ─────────────────────────────────────────
plate_w        = 90;      // overall width
plate_h        = 145;     // overall height
plate_thick    = 3;       // plate thickness
corner_r       = 4.0;     // rounded corners – matches base shell

wall           = 5;       // side margin

// ── TFT display window ────────────────────────────────────────
tft_win_w      = 29.5;    // active area 28.7 + 0.8 mm tolerance
tft_win_h      = 36.5;    // active area 35.7 + 0.8 mm tolerance
tft_x          = (plate_w - tft_win_w) / 2;
tft_y          = plate_h - wall - tft_win_h;
tft_chamfer    = 0.6;     // inner-face bevel on TFT window

// ── MX switch holes (2×5 grid, 19.05 mm pitch) ────────────────
sw_hole        = 14.0;    // MX snap-fit = 14.0; looser = 14.2
sw_pitch       = 19.05;   // standard MX centre-to-centre
sw_cols        = 2;
sw_rows        = 5;
sw_grid_w      = (sw_cols - 1) * sw_pitch;
sw_grid_x0     = (plate_w - sw_grid_w) / 2 - sw_hole / 2;
sw_grid_y0     = wall;
sw_chamfer     = 0.6;     // inner-face bevel for easy switch insertion

// ── Corner screw holes (M3) ────────────────────────────────────
screw_d        = 3.2;     // M3 clearance
screw_margin   = 4.5;     // increased clearance for rounded corners

// ── Snap-fit tabs ─────────────────────────────────────────────
//   Four tabs on the underside edge that click into the base slots.
tab_w          = 8;
tab_h          = 1.5;     // protrusion below plate
tab_thick      = 1.5;

eps = 0.01;               // small overlap to avoid z-fighting

// ── Helper: rounded-corner box ────────────────────────────────
module rounded_box(w, h, d, r) {
    hull()
        for (x = [r, w - r])
            for (y = [r, h - r])
                translate([x, y, 0])
                    cylinder(r=r, h=d, $fn=48);
}

// ── Helper: rectangular hole with chamfer on inner face (z = thick)
//   The visible face (z = 0, printed face-down) stays clean and exact;
//   the inner face gets a subtle bevel for easier component insertion.
module chamfered_rect_hole(w, h, thick, ch) {
    hull() {
        // Exact opening from z = 0 up to the chamfer start
        cube([w, h, thick - ch + eps]);
        // Chamfered outward on the inner face
        translate([-ch, -ch, thick - ch])
            cube([w + 2*ch, h + 2*ch, ch + eps]);
    }
}

// =============================================================
module faceplate() {
    difference() {
        // ── Solid rounded plate ───────────────────────────────
        rounded_box(plate_w, plate_h, plate_thick, corner_r);

        // ── TFT display window (chamfered inner face) ─────────
        translate([tft_x, tft_y, -eps])
            chamfered_rect_hole(tft_win_w, tft_win_h,
                                plate_thick + 2*eps, tft_chamfer);

        // ── 2×5 switch holes (chamfered inner face) ───────────
        for (col = [0 : sw_cols - 1])
            for (row = [0 : sw_rows - 1])
                translate([
                    sw_grid_x0 + col * sw_pitch,
                    sw_grid_y0 + row * sw_pitch,
                    -eps
                ])
                    chamfered_rect_hole(sw_hole, sw_hole,
                                        plate_thick + 2*eps, sw_chamfer);

        // ── Corner M3 screw holes ─────────────────────────────
        for (cx = [screw_margin, plate_w - screw_margin - screw_d])
            for (cy = [screw_margin, plate_h - screw_margin - screw_d])
                translate([cx, cy, -eps])
                    cylinder(d=screw_d, h=plate_thick + 2*eps, $fn=20);
    }

    // ── Snap tabs (underside edge, pointing down) ─────────────
    //   Left / right pairs at roughly 1/3 and 2/3 of the height.
    for (ty = [plate_h * 0.33, plate_h * 0.66]) {
        // left tab
        translate([0, ty - tab_w/2, -tab_h])
            cube([tab_thick, tab_w, tab_h]);
        // right tab
        translate([plate_w - tab_thick, ty - tab_w/2, -tab_h])
            cube([tab_thick, tab_w, tab_h]);
    }
}

faceplate();
