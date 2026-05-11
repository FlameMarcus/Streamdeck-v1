# ---------------------------------------------------------------------------
# st7735s.py – MicroPython driver for the ST7735S 1.8" 128×160 TFT display
# ---------------------------------------------------------------------------
# Works on Raspberry Pi Pico (RP2040) using the hardware SPI peripheral.
# Colour format: RGB565 (2 bytes per pixel, big-endian).
# ---------------------------------------------------------------------------

import time
import struct
from machine import Pin, SPI
import framebuf

# ST7735S command codes
_SWRESET = 0x01
_SLPOUT  = 0x11
_NORON   = 0x13
_INVOFF  = 0x20
_DISPON  = 0x29
_CASET   = 0x2A
_RASET   = 0x2B
_RAMWR   = 0x2C
_MADCTL  = 0x36
_COLMOD  = 0x3A

# Colour helpers (RGB565 big-endian)
def color565(r, g, b):
    """Pack 8-bit R,G,B into a 16-bit RGB565 integer."""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

# Ready-made colour constants
BLACK   = color565(0,   0,   0)
WHITE   = color565(255, 255, 255)
RED     = color565(255, 0,   0)
GREEN   = color565(0,   255, 0)
BLUE    = color565(0,   0,   255)
YELLOW  = color565(255, 255, 0)
CYAN    = color565(0,   255, 255)
MAGENTA = color565(255, 0,   255)
ORANGE  = color565(255, 128, 0)
GRAY    = color565(128, 128, 128)
DKGRAY  = color565(40,  40,  40)

class ST7735S:
    """Driver for the ST7735S 1.8-inch 128×160 SPI TFT display."""

    def __init__(self, spi, cs, dc, rst, bl=None,
                 width=128, height=160,
                 col_offset=2, row_offset=1):
        """
        Parameters
        ----------
        spi        : machine.SPI instance (already configured)
        cs         : machine.Pin – Chip Select (active LOW)
        dc         : machine.Pin – Data/Command
        rst        : machine.Pin – Reset (active LOW)
        bl         : machine.Pin or None – Backlight (optional)
        width/height : display resolution
        col_offset/row_offset : address offsets that vary between modules.
            Common values for 128×160 ST7735S: col=2, row=1
        """
        self._spi = spi
        self._cs  = cs
        self._dc  = dc
        self._rst = rst
        self._bl  = bl
        self.width  = width
        self.height = height
        self._col_offset = col_offset
        self._row_offset = row_offset

        # Framebuffer (RGB565) – kept in RAM for fast partial updates
        self._buf = bytearray(width * height * 2)
        self._fb  = framebuf.FrameBuffer(self._buf, width, height, framebuf.RGB565)

        self._reset()
        self._init_display()
        if bl:
            bl.value(1)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset(self):
        self._rst.value(1)
        time.sleep_ms(50)
        self._rst.value(0)
        time.sleep_ms(50)
        self._rst.value(1)
        time.sleep_ms(150)

    def _write_cmd(self, cmd):
        self._dc.value(0)
        self._cs.value(0)
        self._spi.write(bytes([cmd]))
        self._cs.value(1)

    def _write_data(self, data):
        self._dc.value(1)
        self._cs.value(0)
        self._spi.write(data if isinstance(data, (bytes, bytearray)) else bytes([data]))
        self._cs.value(1)

    def _write_cmd_data(self, cmd, *args):
        self._write_cmd(cmd)
        if args:
            self._write_data(bytes(args))

    # ------------------------------------------------------------------
    # Initialisation sequence for ST7735S 128×160
    # ------------------------------------------------------------------

    def _init_display(self):
        cmds = [
            (_SWRESET, None,           150),  # software reset
            (_SLPOUT,  None,           500),  # exit sleep
            # Frame rate control
            (0xB1, bytes([0x01, 0x2C, 0x2D]),   0),
            (0xB2, bytes([0x01, 0x2C, 0x2D]),   0),
            (0xB3, bytes([0x01, 0x2C, 0x2D,
                          0x01, 0x2C, 0x2D]),    0),
            (0xB4, bytes([0x07]),               0),  # dot inversion
            # Power control
            (0xC0, bytes([0xA2, 0x02, 0x84]),   0),
            (0xC1, bytes([0xC5]),               0),
            (0xC2, bytes([0x0A, 0x00]),         0),
            (0xC3, bytes([0x8A, 0x2A]),         0),
            (0xC4, bytes([0x8A, 0xEE]),         0),
            (0xC5, bytes([0x0E]),               0),  # VCOM
            (_INVOFF, None,                     0),
            # Memory access direction: MX+MY+BGR → portrait, correct colours
            (_MADCTL, bytes([0xC8]),            0),
            # 16-bit colour
            (_COLMOD, bytes([0x05]),            0),
            # Gamma
            (0xE0, bytes([0x02, 0x1c, 0x07, 0x12,
                          0x37, 0x32, 0x29, 0x2D,
                          0x29, 0x25, 0x2B, 0x39,
                          0x00, 0x01, 0x03, 0x10]), 0),
            (0xE1, bytes([0x03, 0x1d, 0x07, 0x06,
                          0x2E, 0x2C, 0x29, 0x2D,
                          0x2E, 0x2E, 0x37, 0x3F,
                          0x00, 0x00, 0x02, 0x10]), 0),
            (_NORON,  None,  10),
            (_DISPON, None, 100),
        ]
        for cmd, data, delay in cmds:
            self._write_cmd(cmd)
            if data:
                self._write_data(data)
            if delay:
                time.sleep_ms(delay)

    # ------------------------------------------------------------------
    # Window / pixel helpers
    # ------------------------------------------------------------------

    def _set_window(self, x0, y0, x1, y1):
        x0 += self._col_offset
        x1 += self._col_offset
        y0 += self._row_offset
        y1 += self._row_offset
        self._write_cmd(_CASET)
        self._write_data(struct.pack('>HH', x0, x1))
        self._write_cmd(_RASET)
        self._write_data(struct.pack('>HH', y0, y1))
        self._write_cmd(_RAMWR)

    def _flush_region(self, x0, y0, x1, y1):
        """Push a rectangular region of the framebuffer to the display."""
        self._set_window(x0, y0, x1, y1)
        self._dc.value(1)
        self._cs.value(0)
        w = x1 - x0 + 1
        for row in range(y0, y1 + 1):
            start = (row * self.width + x0) * 2
            self._spi.write(self._buf[start: start + w * 2])
        self._cs.value(1)

    # ------------------------------------------------------------------
    # Public drawing API (all changes go to the framebuffer first)
    # ------------------------------------------------------------------

    def fill(self, colour):
        """Fill the entire screen with a single colour and flush."""
        self._fb.fill(colour)
        self.show()

    def show(self):
        """Push the entire framebuffer to the display."""
        self._set_window(0, 0, self.width - 1, self.height - 1)
        self._dc.value(1)
        self._cs.value(0)
        self._spi.write(self._buf)
        self._cs.value(1)

    def pixel(self, x, y, colour):
        self._fb.pixel(x, y, colour)

    def hline(self, x, y, w, colour):
        self._fb.hline(x, y, w, colour)

    def vline(self, x, y, h, colour):
        self._fb.vline(x, y, h, colour)

    def rect(self, x, y, w, h, colour):
        self._fb.rect(x, y, w, h, colour)

    def fill_rect(self, x, y, w, h, colour):
        self._fb.fill_rect(x, y, w, h, colour)

    def text(self, s, x, y, colour):
        """Draw 8×8 pixel text using the built-in MicroPython font."""
        self._fb.text(s, x, y, colour)

    def text_large(self, s, x, y, colour, bg=None, scale=2):
        """
        Draw text scaled up by 'scale' (integer ≥ 1).
        Slow but useful for labels – uses pixel-by-pixel scaling.
        """
        char_w = 8 * scale
        char_h = 8 * scale
        for ci, ch in enumerate(s):
            # Render single character into a tiny 8×8 framebuf
            tmp_buf = bytearray(8 * 8 * 2)
            tmp_fb  = framebuf.FrameBuffer(tmp_buf, 8, 8, framebuf.RGB565)
            tmp_fb.fill(0)
            tmp_fb.text(ch, 0, 0, colour)
            cx = x + ci * char_w
            for py in range(8):
                for px in range(8):
                    c = tmp_fb.pixel(px, py)
                    if c or bg is not None:
                        draw_c = c if c else (bg if bg is not None else 0)
                        self._fb.fill_rect(cx + px * scale,
                                           y  + py * scale,
                                           scale, scale, draw_c)
