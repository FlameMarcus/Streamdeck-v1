# ---------------------------------------------------------------------------
# main.py – Streamdeck firmware for Raspberry Pi Pico
# ---------------------------------------------------------------------------
# What this does:
#   1. Initialises the ST7735S TFT display.
#   2. Monitors 10 keyboard-switch buttons (2 columns × 5 rows).
#   3. Sends button events to the host PC over USB serial (CDC).
#   4. Receives label/colour updates from the host PC and redraws the display.
#
# USB serial protocol (plain text, newline-terminated):
#   Pico → PC  :  PRESS:<n>          – button n (0-9) pressed
#   Pico → PC  :  RELEASE:<n>        – button n released
#   Pico → PC  :  READY              – sent once on boot
#   PC   → Pico:  LABEL:<n>:<text>   – set label for button n
#   PC   → Pico:  COLOR:<n>:<r>,<g>,<b> – set background colour for button n
#   PC   → Pico:  BRIGHT:<0-100>     – set backlight brightness (PWM)
# ---------------------------------------------------------------------------

import sys
import time
import select
from machine import Pin, SPI, PWM

import config
from st7735s import ST7735S, color565, BLACK, WHITE, DKGRAY, GRAY, BLUE, GREEN

# ---------------------------------------------------------------------------
# Hardware setup
# ---------------------------------------------------------------------------

spi = SPI(config.SPI_ID,
          baudrate=config.SPI_BAUD,
          sck=Pin(config.SPI_SCK),
          mosi=Pin(config.SPI_MOSI))

tft = ST7735S(
    spi=spi,
    cs=Pin(config.TFT_CS,  Pin.OUT),
    dc=Pin(config.TFT_DC,  Pin.OUT),
    rst=Pin(config.TFT_RST, Pin.OUT),
    bl=Pin(config.TFT_BL,  Pin.OUT),
    width=config.TFT_WIDTH,
    height=config.TFT_HEIGHT,
)

# Backlight PWM (for BRIGHT command)
_bl_pwm = PWM(Pin(config.TFT_BL))
_bl_pwm.freq(1000)
_bl_pwm.duty_u16(65535)  # 100% by default

# Buttons – input with internal pull-up; press = LOW
_buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in config.BTN_PINS]

# ---------------------------------------------------------------------------
# Display layout constants
# ---------------------------------------------------------------------------
#
#  Screen is 128 × 160 pixels (portrait).
#
#  ┌──────────────────────────┐  y=0
#  │   Title bar  (128×22)    │
#  ├────────────┬─────────────┤  y=22
#  │  BTN 0     │  BTN 1     │
#  ├────────────┼─────────────┤
#  │  BTN 2     │  BTN 3     │
#  ├────────────┼─────────────┤
#  │  BTN 4     │  BTN 5     │
#  ├────────────┼─────────────┤
#  │  BTN 6     │  BTN 7     │
#  ├────────────┼─────────────┤
#  │  BTN 8     │  BTN 9     │
#  └────────────┴─────────────┘  y=160
#
TITLE_H   = 22            # height of the title bar
BTN_ROWS  = 5
BTN_COLS  = 2
CELL_W    = config.TFT_WIDTH  // BTN_COLS   # 64
CELL_H    = (config.TFT_HEIGHT - TITLE_H) // BTN_ROWS  # 27 (≈27.6)
BORDER    = 1
TEXT_SCALE = 1            # use 1 for normal 8px font, 2 for doubled

# Default per-button labels and background colours
_btn_labels = ["BTN {}".format(i) for i in range(10)]
_btn_colors = [color565(30, 30, 60)] * 10   # dark blue default

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _btn_rect(idx):
    """Return (x, y, w, h) of the button cell at index idx."""
    row = idx // BTN_COLS
    col = idx  % BTN_COLS
    x = col * CELL_W
    y = TITLE_H + row * CELL_H
    return x, y, CELL_W, CELL_H


def draw_title(title="STREAMDECK"):
    tft.fill_rect(0, 0, config.TFT_WIDTH, TITLE_H, color565(0, 0, 128))
    tft.hline(0, TITLE_H - 1, config.TFT_WIDTH, color565(80, 80, 255))
    # Centre the title text (8px chars)
    x = (config.TFT_WIDTH - len(title) * 8) // 2
    tft.text(title, max(x, 0), 7, WHITE)


def draw_button(idx, pressed=False):
    x, y, w, h = _btn_rect(idx)
    bg = _btn_colors[idx]
    if pressed:
        # Lighten slightly to give feedback
        r = ((bg >> 11) & 0x1F) + 6
        g = ((bg >> 5)  & 0x3F) + 12
        b = (bg & 0x1F) + 6
        bg = color565(min(r * 8, 255), min(g * 4, 255), min(b * 8, 255))

    # Background
    tft.fill_rect(x + BORDER, y + BORDER,
                  w - BORDER * 2, h - BORDER * 2, bg)
    # Border
    tft.rect(x, y, w, h, GRAY)

    # Label – truncate to fit (max (CELL_W-4)//8 chars at scale 1)
    label = _btn_labels[idx]
    max_chars = (w - 4) // (8 * TEXT_SCALE)
    if len(label) > max_chars:
        label = label[:max_chars]

    # Centre text in cell
    lx = x + (w - len(label) * 8 * TEXT_SCALE) // 2
    ly = y + (h - 8 * TEXT_SCALE) // 2
    if TEXT_SCALE == 1:
        tft.text(label, lx, ly, WHITE)
    else:
        tft.text_large(label, lx, ly, WHITE, bg=bg, scale=TEXT_SCALE)


def redraw_all():
    tft.fill(BLACK)
    draw_title()
    for i in range(10):
        draw_button(i)
    tft.show()


def redraw_button(idx, pressed=False):
    draw_button(idx, pressed)
    x, y, w, h = _btn_rect(idx)
    # Only flush this cell to save time
    tft._flush_region(x, y, x + w - 1, y + h - 1)


# ---------------------------------------------------------------------------
# Serial (USB CDC) helpers
# ---------------------------------------------------------------------------

_uart = sys.stdin
_out  = sys.stdout

def send(msg):
    _out.write(msg + "\n")


def _parse_command(line):
    """Handle a single command line received from the host."""
    line = line.strip()
    if not line:
        return
    parts = line.split(":", 2)
    cmd = parts[0].upper()

    if cmd == "LABEL" and len(parts) >= 3:
        try:
            idx = int(parts[1])
            if 0 <= idx <= 9:
                _btn_labels[idx] = parts[2]
                redraw_button(idx)
        except ValueError:
            pass

    elif cmd == "COLOR" and len(parts) >= 3:
        try:
            idx = int(parts[1])
            rgb = parts[2].split(",")
            if 0 <= idx <= 9 and len(rgb) == 3:
                r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
                _btn_colors[idx] = color565(r, g, b)
                redraw_button(idx)
        except (ValueError, IndexError):
            pass

    elif cmd == "BRIGHT" and len(parts) >= 2:
        try:
            pct = max(0, min(100, int(parts[1])))
            _bl_pwm.duty_u16(int(pct / 100 * 65535))
        except ValueError:
            pass

    elif cmd == "REDRAW":
        redraw_all()


# ---------------------------------------------------------------------------
# Button state / debounce
# ---------------------------------------------------------------------------

_btn_state      = [1] * 10   # 1 = not pressed (pull-up HIGH)
_btn_last_raw   = [1] * 10
_btn_last_time  = [0] * 10
_btn_pressed    = [False] * 10

def poll_buttons():
    now = time.ticks_ms()
    for i, pin in enumerate(_buttons):
        raw = pin.value()
        if raw != _btn_last_raw[i]:
            _btn_last_raw[i]  = raw
            _btn_last_time[i] = now
        elif time.ticks_diff(now, _btn_last_time[i]) >= config.DEBOUNCE_MS:
            if raw != _btn_state[i]:
                _btn_state[i] = raw
                if raw == 0:  # pressed
                    _btn_pressed[i] = True
                    send("PRESS:{}".format(i))
                    redraw_button(i, pressed=True)
                else:          # released
                    _btn_pressed[i] = False
                    send("RELEASE:{}".format(i))
                    redraw_button(i, pressed=False)


# ---------------------------------------------------------------------------
# Serial input (non-blocking via select/poll)
# ---------------------------------------------------------------------------

_line_buf = ""
_poller   = select.poll()
_poller.register(sys.stdin, select.POLLIN)

def poll_serial():
    global _line_buf
    events = _poller.poll(0)   # non-blocking
    for fd, event in events:
        try:
            ch = sys.stdin.read(1)
        except Exception:
            continue   # skip this character; keep processing other events
        if ch in ("\n", "\r"):
            if _line_buf:
                _parse_command(_line_buf)
                _line_buf = ""
        else:
            _line_buf += ch


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

redraw_all()
send("READY")

while True:
    poll_buttons()
    poll_serial()
    time.sleep_ms(5)
