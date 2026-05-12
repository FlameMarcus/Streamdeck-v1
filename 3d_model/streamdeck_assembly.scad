// =============================================================
//  Streamdeck-v1  –  Assembly Preview
//  Opens both parts side-by-side so you can inspect the fit.
//  This file is NOT meant for printing – use the individual
//  faceplate / base files instead.
//
//  Usage: open this file in OpenSCAD and press F5 (preview)
//         or F6 (render) to see the exploded assembly.
// =============================================================

// Import module definitions (does NOT execute their top-level calls)
use <streamdeck_faceplate.scad>
use <streamdeck_base.scad>

// Gap between the two halves in the exploded view
gap = 15;
base_depth = 22;  // must match shell_d in streamdeck_base.scad

// ── Faceplate (top half) ──────────────────────────────────────
color("SteelBlue", 0.85)
    translate([0, 0, base_depth + gap])
        faceplate();

// ── Base shell (bottom half) ──────────────────────────────────
color("DimGray", 0.85)
    base_shell();
