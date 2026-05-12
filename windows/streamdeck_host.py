"""
streamdeck_host.py – Windows host application for the Pico Streamdeck
======================================================================

Requirements (install with pip):
    pip install pyserial pyautogui

Usage:
    python streamdeck_host.py [COM_PORT]

    If COM_PORT is omitted the script tries to auto-detect the Pico.
    Example:  python streamdeck_host.py COM3

The script:
  1. Connects to the Pico over USB serial.
  2. Sends label and colour configuration to the display.
  3. Listens for PRESS events and executes the configured action.
"""

import sys
import os
import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import pyautogui

# Disable pyautogui fail-safe for hotkeys (move mouse to corner won't abort)
pyautogui.FAILSAFE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "buttons_config.json")

_DEFAULT_CONFIG = {
    "title": "STREAMDECK",
    "brightness": 100,
    "buttons": [
        {"id": i, "label": "BTN {}".format(i),
         "color": [30, 30, 60],
         "action": {"type": "hotkey", "keys": ""}}
        for i in range(10)
    ],
    "encoder": {
        "cw":    {"type": "hotkey", "keys": "volumeup"},
        "ccw":   {"type": "hotkey", "keys": "volumedown"},
        "press": {"type": "hotkey", "keys": "volumemute"}
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return json.loads(json.dumps(_DEFAULT_CONFIG))   # deep copy
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(_DEFAULT_CONFIG))

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

# ---------------------------------------------------------------------------
# Serial communication
# ---------------------------------------------------------------------------

def find_pico_port():
    """Try to auto-detect the Raspberry Pi Pico's serial port."""
    for port in serial.tools.list_ports.comports():
        desc = (port.description or "").lower()
        mfr  = (port.manufacturer or "").lower()
        if "pico" in desc or "pico" in mfr or \
           "micropython" in desc or "circuit python" in desc or \
           (port.vid == 0x2E8A):   # Raspberry Pi VID
            return port.device
    return None


class PicoConnection:
    """Manages the serial connection to the Pico."""

    def __init__(self, port, baud=115200):
        self._port   = port
        self._baud   = baud
        self._ser    = None
        self._lock   = threading.Lock()
        self._running = False
        self._callbacks = {}   # event_name → callable(idx)
        self._ready  = False

    def connect(self):
        self._ser = serial.Serial(self._port, self._baud, timeout=0.1)
        self._running = True
        t = threading.Thread(target=self._reader, daemon=True)
        t.start()

    def disconnect(self):
        self._running = False
        if self._ser and self._ser.is_open:
            self._ser.close()

    def send(self, msg):
        if self._ser and self._ser.is_open:
            with self._lock:
                self._ser.write((msg + "\n").encode())

    def on(self, event, callback):
        """Register callback for 'press' or 'release' events."""
        self._callbacks[event] = callback

    def _reader(self):
        buf = ""
        while self._running:
            try:
                raw = self._ser.read(64).decode("utf-8", errors="replace")
            except Exception:
                time.sleep(0.1)
                continue
            buf += raw
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                self._handle_line(line.strip())

    def _handle_line(self, line):
        if not line:
            return
        if line == "READY":
            self._ready = True
            cb = self._callbacks.get("ready")
            if cb:
                cb()
            return
        parts = line.split(":", 1)
        if len(parts) == 2:
            event = parts[0].upper()
            value = parts[1]
            if event == "ENCODER":
                cb = self._callbacks.get("encoder")
                if cb:
                    cb(value)          # value is "CW", "CCW", "PRESS", or "RELEASE"
            else:
                try:
                    idx = int(value)
                except ValueError:
                    return
                cb = self._callbacks.get(event.lower())
                if cb:
                    cb(idx)

    def wait_ready(self, timeout=10):
        deadline = time.time() + timeout
        while not self._ready and time.time() < deadline:
            time.sleep(0.05)
        return self._ready

    def push_config(self, cfg):
        """Send all labels, colours, brightness to the Pico."""
        self.send("BRIGHT:{}".format(cfg.get("brightness", 100)))
        for btn in cfg.get("buttons", []):
            idx   = btn["id"]
            label = btn.get("label", "BTN {}".format(idx))
            color = btn.get("color", [30, 30, 60])
            self.send("LABEL:{}:{}".format(idx, label))
            self.send("COLOR:{}:{},{},{}".format(idx, color[0], color[1], color[2]))


# ---------------------------------------------------------------------------
# Action execution
# ---------------------------------------------------------------------------

def execute_action(action):
    if not action:
        return
    kind = action.get("type", "").lower()

    if kind == "hotkey":
        keys = action.get("keys", "")
        if keys:
            # pyautogui.hotkey expects individual key names separated by +
            parts = [k.strip() for k in keys.split("+")]
            pyautogui.hotkey(*parts)

    elif kind == "launch":
        path = action.get("path", "")
        if path:
            try:
                subprocess.Popen([path])
            except FileNotFoundError:
                # Fallback: try os.startfile (Windows)
                try:
                    os.startfile(path)
                except Exception as e:
                    print("Launch error:", e)

    elif kind == "type":
        text = action.get("text", "")
        if text:
            pyautogui.write(text, interval=0.05)


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class StreamdeckApp(tk.Tk):
    def __init__(self, port=None):
        super().__init__()
        self.title("Pico Streamdeck")
        self.resizable(False, False)
        self._cfg   = load_config()
        self._conn  = None
        self._port  = port
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(200, self._auto_connect)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 6, "pady": 4}

        # --- Connection frame ---
        frm_conn = ttk.LabelFrame(self, text="Connection")
        frm_conn.grid(row=0, column=0, sticky="ew", **pad)

        ttk.Label(frm_conn, text="Port:").grid(row=0, column=0, **pad)
        self._port_var = tk.StringVar(value=self._port or "Auto-detect")
        self._port_entry = ttk.Entry(frm_conn, textvariable=self._port_var, width=12)
        self._port_entry.grid(row=0, column=1, **pad)

        self._connect_btn = ttk.Button(frm_conn, text="Connect",
                                       command=self._on_connect)
        self._connect_btn.grid(row=0, column=2, **pad)

        self._status_var = tk.StringVar(value="Disconnected")
        ttk.Label(frm_conn, textvariable=self._status_var, width=18,
                  foreground="red").grid(row=0, column=3, **pad)

        # --- Button grid ---
        frm_btns = ttk.LabelFrame(self, text="Buttons")
        frm_btns.grid(row=1, column=0, sticky="nsew", **pad)

        self._btn_frames = []
        for idx in range(10):
            row = idx // 2
            col = idx  % 2
            btn_cfg = self._cfg["buttons"][idx]

            frm = ttk.Frame(frm_btns, relief="groove", borderwidth=2)
            frm.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

            ttk.Label(frm, text="BTN {}".format(idx), font=("Arial", 8, "bold"))\
                .grid(row=0, column=0, columnspan=2, sticky="w", padx=2)

            lbl_var = tk.StringVar(value=btn_cfg.get("label", ""))
            ttk.Entry(frm, textvariable=lbl_var, width=10)\
                .grid(row=1, column=0, columnspan=2, padx=2, pady=1)

            act_type_var = tk.StringVar(value=btn_cfg.get("action", {}).get("type", "hotkey"))
            act_val_var  = tk.StringVar(value=self._action_value(btn_cfg.get("action", {})))

            ttk.Combobox(frm, textvariable=act_type_var,
                         values=["hotkey", "launch", "type"],
                         width=7, state="readonly")\
                .grid(row=2, column=0, padx=2, pady=1)

            ttk.Entry(frm, textvariable=act_val_var, width=18)\
                .grid(row=2, column=1, padx=2, pady=1)

            self._btn_frames.append({
                "label":    lbl_var,
                "act_type": act_type_var,
                "act_val":  act_val_var,
            })

        # --- Save / Push buttons ---
        frm_btm = ttk.Frame(self)
        frm_btm.grid(row=2, column=0, sticky="ew", **pad)
        ttk.Button(frm_btm, text="Save config",
                   command=self._save_config).pack(side="left", padx=4)
        ttk.Button(frm_btm, text="Push to Pico",
                   command=self._push_config).pack(side="left", padx=4)

        # --- Rotary encoder config ---
        frm_enc = ttk.LabelFrame(self, text="Rotary Encoder (EC11)")
        frm_enc.grid(row=3, column=0, sticky="ew", **pad)

        enc_cfg = self._cfg.get("encoder", {})
        self._enc_frames = {}
        enc_rows = [
            ("cw",    "CW  (clockwise)   "),
            ("ccw",   "CCW (counter-CW)  "),
            ("press", "Press (click)     "),
        ]
        for r, (key, label) in enumerate(enc_rows):
            ttk.Label(frm_enc, text=label, width=20).grid(
                row=r, column=0, padx=4, pady=2, sticky="w")
            action = enc_cfg.get(key, {})
            type_var = tk.StringVar(value=action.get("type", "hotkey"))
            val_var  = tk.StringVar(value=self._action_value(action))
            ttk.Combobox(frm_enc, textvariable=type_var,
                         values=["hotkey", "launch", "type"],
                         width=7, state="readonly").grid(
                row=r, column=1, padx=2, pady=2)
            ttk.Entry(frm_enc, textvariable=val_var, width=22).grid(
                row=r, column=2, padx=2, pady=2)
            self._enc_frames[key] = {"act_type": type_var, "act_val": val_var}

        # --- Log ---
        frm_log = ttk.LabelFrame(self, text="Log")
        frm_log.grid(row=4, column=0, sticky="nsew", **pad)
        self._log = scrolledtext.ScrolledText(frm_log, height=6, width=60,
                                              state="disabled", font=("Consolas", 9))
        self._log.pack(fill="both", expand=True)

    @staticmethod
    def _action_value(action):
        kind = action.get("type", "hotkey")
        if kind == "hotkey":
            return action.get("keys", "")
        elif kind == "launch":
            return action.get("path", "")
        elif kind == "type":
            return action.get("text", "")
        return ""

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log_msg(self, msg):
        self._log.configure(state="normal")
        self._log.insert("end", msg + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def _auto_connect(self):
        if not self._port:
            detected = find_pico_port()
            if detected:
                self._port_var.set(detected)
                self._on_connect()

    def _on_connect(self):
        port = self._port_var.get().strip()
        if not port or port == "Auto-detect":
            port = find_pico_port()
            if not port:
                messagebox.showerror("Error", "Could not find Pico port.\n"
                                     "Check it is plugged in and try again.")
                return
            self._port_var.set(port)

        if self._conn:
            self._conn.disconnect()

        try:
            self._conn = PicoConnection(port)
            self._conn.on("press",   self._on_press)
            self._conn.on("release", self._on_release)
            self._conn.on("encoder", self._on_encoder)
            self._conn.on("ready",   self._on_pico_ready)
            self._conn.connect()
            self._status_var.set("Connected")
            self._log_msg("Connected to {}".format(port))
        except serial.SerialException as e:
            messagebox.showerror("Serial error", str(e))
            self._status_var.set("Error")

    def _on_pico_ready(self):
        self._log_msg("Pico is ready – pushing config…")
        self._push_config()

    def _on_close(self):
        if self._conn:
            self._conn.disconnect()
        self.destroy()

    # ------------------------------------------------------------------
    # Button events
    # ------------------------------------------------------------------

    def _on_press(self, idx):
        self._log_msg("Button {} pressed".format(idx))
        if idx < len(self._cfg["buttons"]):
            action = self._cfg["buttons"][idx].get("action", {})
            # Run action in background thread so we don't block serial reader
            threading.Thread(target=execute_action, args=(action,), daemon=True).start()

    def _on_release(self, idx):
        self._log_msg("Button {} released".format(idx))

    def _on_encoder(self, direction):
        direction = direction.strip().upper()
        self._log_msg("Encoder: {}".format(direction))
        enc_cfg = self._cfg.get("encoder", {})
        action  = None
        if direction == "CW":
            action = enc_cfg.get("cw")
        elif direction == "CCW":
            action = enc_cfg.get("ccw")
        elif direction == "PRESS":
            action = enc_cfg.get("press")
        if action:
            threading.Thread(target=execute_action,
                             args=(action,), daemon=True).start()

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _collect_config_from_ui(self):
        for idx in range(10):
            ui   = self._btn_frames[idx]
            btn  = self._cfg["buttons"][idx]
            btn["label"] = ui["label"].get()
            kind = ui["act_type"].get()
            val  = ui["act_val"].get()
            if kind == "hotkey":
                btn["action"] = {"type": "hotkey", "keys": val}
            elif kind == "launch":
                btn["action"] = {"type": "launch", "path": val}
            elif kind == "type":
                btn["action"] = {"type": "type", "text": val}

        enc = {}
        for key, ui in self._enc_frames.items():
            kind = ui["act_type"].get()
            val  = ui["act_val"].get()
            if kind == "hotkey":
                enc[key] = {"type": "hotkey", "keys": val}
            elif kind == "launch":
                enc[key] = {"type": "launch", "path": val}
            elif kind == "type":
                enc[key] = {"type": "type", "text": val}
        self._cfg["encoder"] = enc

    def _save_config(self):
        self._collect_config_from_ui()
        save_config(self._cfg)
        self._log_msg("Config saved to {}".format(CONFIG_FILE))

    def _push_config(self):
        self._collect_config_from_ui()
        if not self._conn:
            self._log_msg("Not connected – connect first.")
            return
        self._conn.push_config(self._cfg)
        self._log_msg("Config pushed to Pico.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port_arg = sys.argv[1] if len(sys.argv) > 1 else None
    app = StreamdeckApp(port=port_arg)
    app.mainloop()
