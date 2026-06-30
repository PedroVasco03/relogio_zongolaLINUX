"""
Módulo de Persistência — XDG Base Directory Specification
Guarda configurações em ~/.config/relogio-zongola/
"""

import json
import os
from pathlib import Path

APP_NAME = "relogio-zongola"

def _config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME", "")
    base = Path(xdg) if xdg else Path.home() / ".config"
    d = base / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d

def _data_dir() -> Path:
    xdg = os.environ.get("XDG_DATA_HOME", "")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    d = base / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d

# ── config.json ──────────────────────────────────────────────────────────────
_CONFIG_DEFAULTS = {
    "time_format": "24h",
    "palette":     "samakaka_classico",
    "show_seconds": True,
    "samakaka": {
        "show_pattern":    True,
        "pattern_opacity": 0.18,
        "pattern_scale":   40,
        "pattern_style":   "full",
    },
    "world_clocks": [
        {"city": "Luanda",       "tz": "Africa/Luanda"},
        {"city": "Lisboa",       "tz": "Europe/Lisbon"},
        {"city": "São Paulo",    "tz": "America/Sao_Paulo"},
        {"city": "Paris",        "tz": "Europe/Paris"},
    ],
}

def load_config() -> dict:
    p = _config_dir() / "config.json"
    if p.exists():
        try:
            data = json.loads(p.read_text())
            # merge with defaults for missing keys
            for k, v in _CONFIG_DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(_CONFIG_DEFAULTS)

def save_config(cfg: dict):
    p = _config_dir() / "config.json"
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))

# ── alarms.json ──────────────────────────────────────────────────────────────
def load_alarms() -> list:
    p = _config_dir() / "alarms.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return []

def save_alarms(alarms: list):
    p = _config_dir() / "alarms.json"
    p.write_text(json.dumps(alarms, ensure_ascii=False, indent=2))

# ── timers.json ───────────────────────────────────────────────────────────────
def load_timer_profiles() -> list:
    p = _config_dir() / "timers.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return [
        {"name": "Pomodoro",   "seconds": 1500},
        {"name": "Pausa curta","seconds": 300},
        {"name": "Pausa longa","seconds": 900},
    ]

def save_timer_profiles(profiles: list):
    p = _config_dir() / "timers.json"
    p.write_text(json.dumps(profiles, ensure_ascii=False, indent=2))

# ── laps CSV (cronómetro) ────────────────────────────────────────────────────
def export_laps(laps: list) -> str:
    """Exporta voltas para CSV em XDG_DATA_HOME. Retorna caminho do ficheiro."""
    from datetime import datetime
    fname = f"laps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    p = _data_dir() / fname
    lines = ["volta,tempo_parcial,tempo_total"]
    for i, (parcial, total) in enumerate(laps, 1):
        lines.append(f"{i},{parcial},{total}")
    p.write_text("\n".join(lines))
    return str(p)
