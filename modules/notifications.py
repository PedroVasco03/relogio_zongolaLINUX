"""
Módulo de Notificações — D-Bus via notify-send
RF8: Notificações nativas do ambiente de desktop Linux.
"""

import subprocess
import threading


def _notify(title: str, body: str, urgency: str = "normal", icon: str = "clock"):
    """Envia notificação via notify-send (D-Bus libnotify)."""
    try:
        subprocess.Popen(
            ["notify-send", f"--urgency={urgency}", f"--icon={icon}",
             "--app-name=Relógio Zongola", title, body],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        # notify-send não disponível (ambiente sem D-Bus) — silencioso
        pass


def notify_alarm(label: str):
    t = threading.Thread(
        target=_notify,
        args=(f"⏰ Alarme — {label}", "O teu alarme está a tocar.", "critical", "alarm-clock"),
        daemon=True,
    )
    t.start()


def notify_timer_end(name: str):
    t = threading.Thread(
        target=_notify,
        args=(f"⏱ Temporizador — {name}", "O tempo terminou!", "normal", "appointment-soon"),
        daemon=True,
    )
    t.start()


def notify_snooze(minutes: int):
    t = threading.Thread(
        target=_notify,
        args=("😴 Soneca activada", f"Alarme em {minutes} minuto(s).", "low", "alarm-clock"),
        daemon=True,
    )
    t.start()
