# ---------------------------------------------------------------------------
# config.py – Hardware pin definitions for the Streamdeck Pico
# ---------------------------------------------------------------------------
# ┌─────────────────────────────────────────────────────────┐
# │  Raspberry Pi Pico  ←──SPI0──→  ST7735S 1.8" 128×160   │
# │                                                          │
# │  GP18  SCK   →  SCK/CLK                                 │
# │  GP19  MOSI  →  SDA/MOSI                                │
# │  GP17  CS    →  CS/CE                                   │
# │  GP20  DC    →  DC/AO (Data/Command)                    │
# │  GP21  RST   →  RST/RES                                 │
# │  GP22  BL    →  BL/LED (backlight – via 100 Ω resistor) │
# │  3.3 V       →  VCC                                     │
# │  GND         →  GND                                     │
# └─────────────────────────────────────────────────────────┘
#
# Button matrix – 2 columns × 5 rows = 10 keys
# Each button connects between a GP pin and GND.
# Internal pull-ups are enabled; pressing = LOW.
#
#  Physical layout (looking at the device):
#
#   ┌──────────────────────┐
#   │    [ TFT display ]   │
#   ├──────────┬───────────┤
#   │  BTN 0   │  BTN 1   │
#   │  BTN 2   │  BTN 3   │
#   │  BTN 4   │  BTN 5   │
#   │  BTN 6   │  BTN 7   │
#   │  BTN 8   │  BTN 9   │
#   └──────────┴───────────┘

# --- Display (SPI0) --------------------------------------------------------
SPI_ID   = 0
SPI_SCK  = 18   # GP18
SPI_MOSI = 19   # GP19
SPI_BAUD = 20_000_000  # 20 MHz – safe max for ST7735S

TFT_CS   = 17   # GP17  Chip-Select (active LOW)
TFT_DC   = 20   # GP20  Data/Command
TFT_RST  = 21   # GP21  Reset        (active LOW)
TFT_BL   = 22   # GP22  Backlight PWM

# Display physical size
TFT_WIDTH  = 128
TFT_HEIGHT = 160

# --- Buttons ---------------------------------------------------------------
# Indices 0-9 map to BTN_PINS[0]-BTN_PINS[9]
BTN_PINS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # GP0 … GP9

# How many milliseconds a button must be stable before we accept the change
DEBOUNCE_MS = 30
