# Streamdeck-v1

A DIY Stream Deck built with a **Raspberry Pi Pico**, a **1.8-inch 128×160 ST7735S TFT display**, and **10 keyboard switches** arranged in a 2×5 grid.  
Press a button → the Windows host app runs the action you configured (hotkey, app launch, or typed text).

---

## Hardware

| Component | Details |
|---|---|
| Microcontroller | Raspberry Pi Pico (RP2040) |
| Display | 1.8" 128×160 SPI TFT – ST7735S / ST7789 (3.3 V) |
| Buttons | 10 × keyboard switches (MX, Alps, or similar) |
| Power | USB from PC |

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

```bat
pip install pyserial pyautogui
```

### 4 – Configure your buttons

Edit `windows/buttons_config.json`.  
Each button has:

```jsonc
{
  "id": 0,
  "label": "Mute",          // text shown on the TFT
  "color": [60, 0, 0],      // background colour [R, G, B]  0-255
  "action": {
    "type": "hotkey",        // "hotkey" | "launch" | "type"
    "keys": "ctrl+shift+m"  // key combo (hotkey), path (launch), or text (type)
  }
}
```

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
│   ├── streamdeck_faceplate.scad  # Top plate (display window + switch holes)
│   ├── streamdeck_base.scad       # Shell (Pico standoffs, USB cutout, TFT ledge)
│   ├── streamdeck_assembly.scad   # Exploded preview (not for printing)
│   └── README.md                  # Print settings and parameter guide
├── pico/
│   ├── config.py          # All pin numbers live here
│   ├── st7735s.py         # ST7735S display driver (no extra libs needed)
│   └── main.py            # Firmware – runs on the Pico
└── windows/
    ├── streamdeck_host.py # GUI host app for Windows
    └── buttons_config.json # Button labels, colours, actions
```

---

## 3D-printed enclosure

The `3d_model/` folder contains parametric [OpenSCAD](https://openscad.org/) models for a two-piece enclosure:

- **Faceplate** – top plate with a TFT display window and 10 MX switch holes
- **Base shell** – hollow body with Raspberry Pi Pico standoffs, a Micro-USB cutout, and a TFT display ledge

See [`3d_model/README.md`](3d_model/README.md) for export, print settings, and how to adjust dimensions.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Display shows nothing | Check wiring; try swapping `col_offset`/`row_offset` in `st7735s.py` (change `col_offset=2, row_offset=1` to `0,0`) |
| Display colours look wrong | Try changing `0xC8` → `0x00` in the `_MADCTL` line in `st7735s.py` |
| Host app can't find the Pico | Enter the COM port manually (check Device Manager → Ports) |
| Buttons don't respond | Make sure one leg of each switch goes to the listed GP pin and the other to GND |
| `pip install` fails | Make sure Python 3.8+ is installed; try `py -m pip install ...` |

---

## Customising pin assignments

All pin numbers are in `pico/config.py`.  
Change them there and the rest of the code follows automatically.
