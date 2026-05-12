// =============================================================
//  Streamdeck-v1  –  Assembly Preview  (Minimalist Redesign)
//  NOT for printing – use the individual faceplate / base files.
//
//  Usage: open in OpenSCAD and press F5 (preview) or F6 (render).
// =============================================================

// Import module definitions (top-level geometry is suppressed by use<>)
use <streamdeck_faceplate.scad>
use <streamdeck_base.scad>

// ── Layout constants ───────────────────────────────────────────
// WARNING: these must be kept in sync with streamdeck_base.scad.
// OpenSCAD `use <>` imports only module definitions, not variables,
// so the values are repeated here.
gap        = 15;   // exploded-view separation
base_depth = 18;   // must match shell_d  in streamdeck_base.scad

// ── Encoder preview position ───────────────────────────────────
// Must match pot_y (shell_h * 0.6) and pot_z (shell_d / 2) in
// streamdeck_base.scad.  Update both places if those values change.
enc_y = 145 * 0.6;   // shell_h * 0.6
enc_z = 18  / 2;     // shell_d / 2

// ── Faceplate (raised for exploded view) ──────────────────────
color("SteelBlue", 0.85)
    translate([0, 0, base_depth + gap])
        faceplate();

// ── Base shell ────────────────────────────────────────────────
color("DimGray", 0.85)
    base_shell();

// ── Rotary encoder / knob preview ─────────────────────────────
//   Shows the EC11-style encoder shaft and knob protruding from
//   the right side wall (x = 90 face of the base).
color("Silver", 0.95)
    translate([90, enc_y, enc_z])
        rotate([0, 90, 0]) {
            cylinder(d=6, h=4,  $fn=24);   // shaft stub
            translate([0, 0, 4])
                cylinder(d=18, h=7, $fn=48); // round knob cap
        }
