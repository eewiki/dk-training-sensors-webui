import datetime
import threading
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI

print("Python ready", flush=True)

web = WebUI()

_lock = threading.Lock()
_state = {
    "tempC": None,
    "tempF": None,
    "hum": None,
    "x": None,
    "y": None,
    "z": None,
    "roll": None,
    "pitch": None,
    "yaw": None,
    "last_presence_utc": None,   # ISO UTC string
    "last_presence_mm": None,
}

def now_utc_iso():
    # ISO 8601 UTC, ex: 2026-03-01T08:22:29Z
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def update_sensors(tempC, tempF, hum):
    with _lock:
        _state["tempC"] = float(tempC)
        _state["tempF"] = float(tempF)
        _state["hum"] = float(hum)

def update_movement_sensors(x, y, z, roll, pitch, yaw):
    with _lock:
        _state["x"] = float(x)
        _state["y"] = float(y)
        _state["z"] = float(z)
        _state["roll"] = float(roll)
        _state["pitch"] = float(pitch)
        _state["yaw"] = float(yaw)

def presence_mm(mm):
    with _lock:
        _state["last_presence_utc"] = now_utc_iso()
        _state["last_presence_mm"] = int(mm)
    return True

Bridge.provide("update_sensors", update_sensors)
Bridge.provide("update_movement_sensors", update_movement_sensors)
Bridge.provide("presence_mm", presence_mm)

def api_state(_req=None):
    with _lock:
        payload = {
            "now_utc": now_utc_iso(),
            "tempC": _state["tempC"],
            "tempF": _state["tempF"],
            "hum": _state["hum"],
            "x": _state["x"],
            "y": _state["y"],
            "z": _state["z"],
            "roll": _state["roll"],
            "pitch": _state["pitch"],
            "yaw": _state["yaw"],
            "last_presence_utc": _state["last_presence_utc"],
            "last_presence_mm": _state["last_presence_mm"],
        }
    return payload

web.expose_api("GET", "/api/state", api_state)

App.run()