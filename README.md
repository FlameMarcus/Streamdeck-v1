# Streamdeck-v1

A DIY Stream Deck built with a **Raspberry Pi Pico**, a **1.8-inch 128×160 ST7735S TFT display**, and **10 keyboard switches** arranged in a 5×2 grid (5 rows, 2 columns).  
Press a button → the Windows host app runs the action you configured (hotkey, app launch, or typed text).

---

## Hardware

| Component | Details | AliExpress |
|---|---|---|
| Microcontroller | Raspberry Pi Pico (RP2040) | [Buy on AliExpress](https://www.aliexpress.com/wholesale?SearchText=raspberry+pi+pico+rp2040) |
| Display | 1.8" 128×160 SPI TFT – ST7735S / ST7789 (3.3 V) | [Buy on AliExpress](https://www.aliexpress.com/wholesale?SearchText=1.8+inch+ST7735S+TFT+SPI+display+128x160) |
| Buttons | 10 × keyboard switches (MX, Alps, or similar) | [Buy on AliExpress](https://www.aliexpress.com/wholesale?SearchText=cherry+mx+mechanical+keyboard+switches) |
| Rotary encoder | EC11 rotary encoder with push-button (5-pin, 6 mm shaft) | [Buy on AliExpress](https://www.aliexpress.com/wholesale?SearchText=EC11+rotary+encoder+switch+5pin+6mm) |
| Power | USB from PC | — |

### Physical layout

```
┌──────────────────────┐
│    [ TFT Display ]   │   ← display on top
├──────────┬───────────┤
│  BTN 0   │  BTN 1   │
│  BTN 2   │  BTN 3   │
│  BTN 4   │  BTN 5   │
│  BTN 6   │  BTN 7   │
│  BTN 8   │  BTN 9   │
└──────────┴───────────┘
                        ← [KNOB] on right side wall
```

---

## Wiring

### TFT display → Pico (SPI0)

| TFT pin | Pico pin | Pico GP |
|---------|----------|---------|
| VCC     | 3.3V     | Pin 36  |
| GND     | GND      | Pin 38  |
| SCK / CLK | SPI0 SCK | GP18  |
| SDA / MOSI | SPI0 MOSI | GP19 |
| CS / CE | GP17     | GP17    |
| DC / AO | GP20     | GP20    |
| RST / RES | GP21   | GP21    |
| BL / LED | GP22 (via 100 Ω resistor) | GP22 |

> **Note:** Connect BL through a 100 Ω resistor to protect the LED, or directly to 3.3 V if your module has a built-in resistor.

### Buttons → Pico

Each button connects between a GPIO pin and **GND**.  
Internal pull-ups are enabled so you don't need external resistors.

| Button | Pico GP |
|--------|---------|
| BTN 0  | GP0     |
| BTN 1  | GP1     |
| BTN 2  | GP2     |
| BTN 3  | GP3     |
| BTN 4  | GP4     |
| BTN 5  | GP5     |
| BTN 6  | GP6     |
| BTN 7  | GP7     |
| BTN 8  | GP8     |
| BTN 9  | GP9     |

### Rotary encoder (EC11) → Pico

The EC11 has 5 pins.  Connect them as follows (internal pull-ups enabled; no external resistors needed):

| EC11 pin | Pico pin | Pico GP |
|----------|----------|---------|
| CLK (A)  | Pin 14   | GP10    |
| DT  (B)  | Pin 15   | GP11    |
| SW (button) | Pin 16 | GP12  |
| +        | 3.3 V    | Pin 36  |
| GND      | GND      | Pin 38  |

> **Note:** Both the TFT display and the rotary encoder draw 3.3 V from the Pico. Pin 36 is the Pico's 3.3V output — you can share it between both components using a small breadboard or by daisy-chaining the wires. Total current draw is well within the Pico's 300 mA limit.

**How the encoder works in the firmware:**
- Turning CW → fires `ENCODER:CW` → host executes the `cw` action (default: volume up)  
- Turning CCW → fires `ENCODER:CCW` → host executes the `ccw` action (default: volume down)  
- Pressing the knob → fires `ENCODER:PRESS` / `ENCODER:RELEASE` → host executes the `press` action (default: mute)  

You can change these actions in `windows/buttons_config.json` under the `"encoder"` key, or live in the host app's **Rotary Encoder** panel.

---

## Software setup

### 1 – Flash MicroPython onto the Pico

1. Hold the **BOOTSEL** button on the Pico while plugging in the USB cable.  
2. It will appear as a USB drive called `RPI-RP2`.  
3. Download the latest MicroPython `.uf2` from <https://micropython.org/download/rp2-pico/> and drag it onto the drive.  
4. The Pico reboots automatically.

### 2 – Copy the firmware files

Use [Thonny](https://thonny.org/) (free, easy to use) or `mpremote`:

Copy these three files from the `pico/` folder **to the root of the Pico**:

| File | Purpose |
|---|---|
| `pico/config.py` | Pin definitions |
| `pico/st7735s.py` | TFT display driver |
| `pico/main.py` | Main firmware |

In Thonny:
1. Open each file.  
2. Go to **File → Save copy… → MicroPython device** and save as the same filename.

The Pico will run `main.py` automatically every time it boots.

### 3 – Install Windows requirements

Open a Command Prompt or PowerShell and run:

> **Requires Python 3.8 or newer.** Check your version with `python --version`.

```bat
pip install -r windows/requirements.txt
```

### 4 – Configure your buttons

Edit `windows/buttons_config.json`.  
Each button has:

```json
{
  "id": 0,
  "label": "Mute",
  "color": [60, 0, 0],
  "action": {
    "type": "hotkey",
    "keys": "ctrl+shift+m"
  }
}
```

| Field | Description |
|---|---|
| `id` | Zero-based button index (0–9) |
| `label` | Text displayed on the TFT screen |
| `color` | Background color as `[R, G, B]`, each value 0–255 |
| `action.type` | Action type: `"hotkey"`, `"launch"`, or `"type"` |
| `action.keys` | Key combo (hotkey), file path (launch), or text string (type) |

The `encoder` section in the same file controls the rotary knob:

```json
"encoder": {
  "cw":    {"type": "hotkey", "keys": "volumeup"},
  "ccw":   {"type": "hotkey", "keys": "volumedown"},
  "press": {"type": "hotkey", "keys": "volumemute"}
}
```

| Field | Description |
|---|---|
| `cw` | Action fired when turning the encoder clockwise |
| `ccw` | Action fired when turning the encoder counter-clockwise |
| `press` | Action fired when pressing the encoder knob |

**Action types:**

| Type | What it does | Value field |
|---|---|---|
| `hotkey` | Press a keyboard shortcut | e.g. `ctrl+shift+m`, `ctrl+F1`, `volumeup` |
| `launch` | Open a program or file | Full path, e.g. `C:\Program Files\...` |
| `type` | Type text as if from keyboard | Any string |

### 5 – Run the host app

```bat
cd windows
python streamdeck_host.py
```

Or specify the COM port directly (useful if auto-detect fails):

```bat
python streamdeck_host.py COM3
```

A small window opens showing the button grid.  
You can change labels and actions there too – click **Save config** then **Push to Pico**.

---

## Project structure

```
Streamdeck-v1/
├── 3d_model/
│   ├── streamdeck_enclosure.scad  # PRIMARY FILE – complete single-file parametric design
│   ├── streamdeck_faceplate.scad  # Thin wrapper: renders faceplate() only (for STL export)
│   ├── streamdeck_base.scad       # Thin wrapper: renders base_shell() only (for STL export)
│   ├── streamdeck_assembly.scad   # Thin wrapper: renders assembly() preview (not for printing)
│   └── README.md                  # Print settings and full parameter guide
├── pico/
│   ├── config.py          # All pin numbers live here (including encoder GP10/11/12)
│   ├── st7735s.py         # ST7735S display driver (no extra libs needed)
│   └── main.py            # Firmware – runs on the Pico
└── windows/
    ├── streamdeck_host.py  # GUI host app for Windows
    └── buttons_config.json # Button labels, colors, actions + encoder actions
```

---

## 3D-printed enclosure

The `3d_model/` folder contains a single parametric [OpenSCAD](https://openscad.org/) file that generates a sleek, angled two-piece enclosure:

- **Faceplate** – 15° tilted plate with a recessed TFT display window (1 mm retaining lip) and 10 × MX switch holes with chamfered inner edges
- **Base shell** – flat-bottomed wedge body with Raspberry Pi Pico standoffs, a 12 × 7 mm Micro-USB cutout on the front face, a TFT display ledge, a **7 mm EC11 encoder hole** on the right side wall, and a cable management channel on the underside

All parameters (tilt angle, wall thickness, button spacing, tolerances, etc.) are variables at the top of [`3d_model/streamdeck_enclosure.scad`](3d_model/streamdeck_enclosure.scad).

See [`3d_model/README.md`](3d_model/README.md) for export instructions, print settings, and a full parameter reference.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Display shows nothing | Check wiring; try swapping `col_offset`/`row_offset` in `st7735s.py` (change `col_offset=2, row_offset=1` to `0,0`) |
| Display colors look wrong | Try changing `0xC8` → `0x00` in the `_MADCTL` line in `st7735s.py` |
| Host app can't find the Pico | Enter the COM port manually (check Device Manager → Ports) |
| Buttons don't respond | Make sure one leg of each switch goes to the listed GP pin and the other to GND |
| Encoder doesn't respond | Check CLK→GP10, DT→GP11, SW→GP12, + →3.3 V, GND→GND; verify `ENC_CLK/DT/SW` in `config.py` |
| Encoder turns the wrong direction | Swap the CLK and DT wires (or swap `ENC_CLK` and `ENC_DT` values in `config.py`) |
| `pip install` fails | Make sure Python 3.8+ is installed; try `py -m pip install ...` |

---

## Customising pin assignments

All pin numbers are in `pico/config.py`.  
Change them there and the rest of the code follows automatically.
