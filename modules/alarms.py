"""
Módulo de Alarmes — RF02, RF03, RF10
Alarmes múltiplos, recorrentes, snooze configurável, persistência.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import time as _time

from modules import notifications
from modules.sound import play as play_sound, stop_all as stop_sound

DAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
SNOOZE_OPTIONS = [5, 10, 15, 20]


class AlarmEngine(threading.Thread):
    """Thread em background que verifica alarmes a cada segundo."""

    def __init__(self, get_alarms, on_trigger):
        super().__init__(daemon=True)
        self._get_alarms  = get_alarms
        self._on_trigger  = on_trigger   # callback(alarm_dict) no thread principal
        self._active      = True
        self._snoozed     = {}           # alarm_id -> datetime de disparo pós-snooze

    def run(self):
        while self._active:
            now = datetime.now()
            for alarm in self._get_alarms():
                if not alarm.get("active", True):
                    continue
                aid = alarm["id"]

                # Verificar snooze
                if aid in self._snoozed:
                    if now >= self._snoozed[aid]:
                        del self._snoozed[aid]
                        self._on_trigger(alarm)
                    continue

                # Verificar hora
                h, m = alarm["hour"], alarm["minute"]
                if now.hour == h and now.minute == m and now.second == 0:
                    # Verificar dia da semana (0=Seg … 6=Dom)
                    days = alarm.get("days", list(range(7)))
                    wd = now.weekday()  # 0=Monday
                    if wd in days:
                        self._on_trigger(alarm)

            _time.sleep(1)

    def snooze(self, alarm_id: int, minutes: int):
        self._snoozed[alarm_id] = datetime.now() + timedelta(minutes=minutes)

    def stop(self):
        self._active = False


class AlarmsTab(tk.Frame):
    def __init__(self, parent, palette: dict, alarms: list, on_save, root_ref):
        super().__init__(parent, bg=palette["bg"])
        self.palette   = palette
        self.alarms    = alarms
        self.on_save   = on_save
        self.root      = root_ref
        self._next_id  = max((a.get("id", 0) for a in alarms), default=0) + 1

        self._engine = AlarmEngine(
            get_alarms=lambda: self.alarms,
            on_trigger=self._alarm_triggered,
        )
        self._engine.start()

        self._build_ui()
        self._refresh_list()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        p = self.palette

        hdr = tk.Frame(self, bg=p["bg_panel"], pady=8)
        hdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr, text="⏰  ALARMES",
                 bg=p["bg_panel"], fg=p["accent2"],
                 font=("Helvetica", 13, "bold")).pack(side=tk.LEFT, padx=14)
        tk.Button(hdr, text="+ Novo Alarme",
                  bg=p["accent"], fg=p["fg"],
                  font=("Helvetica", 9, "bold"),
                  relief=tk.FLAT, bd=0, padx=10, pady=4,
                  cursor="hand2",
                  command=self._new_alarm_dialog).pack(side=tk.RIGHT, padx=14)

        # Lista de alarmes com scroll
        outer = tk.Frame(self, bg=p["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=14)

        self._canvas = tk.Canvas(outer, bg=p["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient=tk.VERTICAL,
                           command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._list_frame = tk.Frame(self._canvas, bg=p["bg"])
        cw = self._canvas.create_window((0, 0), window=self._list_frame, anchor="nw")
        self._list_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(cw, width=e.width))

    def _refresh_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        p = self.palette
        if not self.alarms:
            tk.Label(self._list_frame,
                     text="Nenhum alarme configurado.\nClica em '+ Novo Alarme' para começar.",
                     bg=p["bg"], fg=p["fg_dim"],
                     font=("Helvetica", 11), justify=tk.CENTER
                     ).pack(pady=40)
            return

        for alarm in sorted(self.alarms, key=lambda a: (a["hour"], a["minute"])):
            self._alarm_card(alarm).pack(fill=tk.X, pady=4)

    def _alarm_card(self, alarm: dict) -> tk.Frame:
        p  = self.palette
        card = tk.Frame(self._list_frame, bg=p["bg_card"],
                        highlightbackground=p["border"], highlightthickness=1)

        accent_bar = p["accent"] if alarm.get("active", True) else p["fg_dim"]
        tk.Frame(card, bg=accent_bar, width=5).pack(side=tk.LEFT, fill=tk.Y)

        body = tk.Frame(card, bg=p["bg_card"])
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=10)

        row1 = tk.Frame(body, bg=p["bg_card"])
        row1.pack(fill=tk.X)

        time_str = f"{alarm['hour']:02d}:{alarm['minute']:02d}"
        tk.Label(row1, text=time_str,
                 bg=p["bg_card"], fg=p["accent2"],
                 font=("Courier New", 26, "bold")).pack(side=tk.LEFT)

        lbl = alarm.get("label", "")
        if lbl:
            tk.Label(row1, text=lbl,
                     bg=p["bg_card"], fg=p["fg"],
                     font=("Helvetica", 11)).pack(side=tk.LEFT, padx=12)

        # Toggle activo
        var = tk.BooleanVar(value=alarm.get("active", True))
        def _toggle(a=alarm, v=var):
            a["active"] = v.get()
            self.on_save()
            self._refresh_list()

        tk.Checkbutton(row1, text="Activo", variable=var,
                       bg=p["bg_card"], fg=p["fg"],
                       selectcolor=p["bg_card"],
                       activebackground=p["bg_card"],
                       font=("Helvetica", 9),
                       command=_toggle).pack(side=tk.RIGHT, padx=4)

        # Dias
        days = alarm.get("days", list(range(7)))
        days_str = "  ".join(DAYS_PT[d] for d in days) if days else "—"
        tk.Label(body, text=f"📅 {days_str}",
                 bg=p["bg_card"], fg=p["fg_dim"],
                 font=("Helvetica", 9)).pack(anchor="w")

        # Botões editar/apagar
        btn_row = tk.Frame(body, bg=p["bg_card"])
        btn_row.pack(anchor="e")
        tk.Button(btn_row, text="✎ Editar",
                  bg=p["bg_panel"], fg=p["fg"],
                  font=("Helvetica", 8), relief=tk.FLAT, bd=0, padx=6, pady=2,
                  command=lambda a=alarm: self._edit_alarm_dialog(a)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_row, text="✕ Apagar",
                  bg=p["bg_panel"], fg=p["accent"],
                  font=("Helvetica", 8), relief=tk.FLAT, bd=0, padx=6, pady=2,
                  command=lambda a=alarm: self._delete_alarm(a)).pack(side=tk.LEFT, padx=2)

        return card

   
    def _new_alarm_dialog(self, alarm=None):
        p = self.palette
        editing = alarm is not None
        dlg = tk.Toplevel(self)
        dlg.title("Editar Alarme" if editing else "Novo Alarme")
        dlg.configure(bg=p["bg"])
        dlg.geometry("380x420")
        dlg.resizable(False, False)

        # Hora / Minuto
        tk.Label(dlg, text="Hora:", bg=p["bg"], fg=p["fg"],
                 font=("Helvetica", 10, "bold")).pack(pady=(16, 2))
        time_row = tk.Frame(dlg, bg=p["bg"])
        time_row.pack()

        
        now_time = datetime.now()
        h_var = tk.IntVar(value=alarm["hour"] if editing else now_time.hour)
        m_var = tk.IntVar(value=alarm["minute"] if editing else now_time.minute)

        tk.Spinbox(time_row, from_=0, to=23, textvariable=h_var, width=4,
                   format="%02.0f", bg=p["bg_card"], fg=p["accent2"], state="readonly",
                   buttonbackground=p["bg_panel"],
                   font=("Courier New", 18, "bold"), relief=tk.FLAT).pack(side=tk.LEFT)
        tk.Label(time_row, text=":", bg=p["bg"], fg=p["fg"],
                 font=("Courier New", 18, "bold")).pack(side=tk.LEFT)
        tk.Spinbox(time_row, from_=0, to=59, textvariable=m_var, width=4,
                   format="%02.0f", bg=p["bg_card"], fg=p["accent2"], state="readonly",
                   buttonbackground=p["bg_panel"],
                   font=("Courier New", 18, "bold"), relief=tk.FLAT).pack(side=tk.LEFT)

        # Etiqueta
        tk.Label(dlg, text="Etiqueta:", bg=p["bg"], fg=p["fg"],
                 font=("Helvetica", 10, "bold")).pack(pady=(12, 2))
        lbl_var = tk.StringVar(value=alarm.get("label", "") if editing else "")
        tk.Entry(dlg, textvariable=lbl_var,
                 bg=p["bg_card"], fg=p["fg"],
                 font=("Helvetica", 11), relief=tk.FLAT).pack(padx=30, fill=tk.X)

        # Dias da semana
        tk.Label(dlg, text="Repetir:", bg=p["bg"], fg=p["fg"],
                 font=("Helvetica", 10, "bold")).pack(pady=(12, 2))
        days_row = tk.Frame(dlg, bg=p["bg"])
        days_row.pack()
        day_vars = []
        sel_days = set(alarm.get("days", list(range(7))) if editing else range(7))
        for i, d in enumerate(DAYS_PT):
            v = tk.BooleanVar(value=(i in sel_days))
            day_vars.append(v)
            tk.Checkbutton(days_row, text=d, variable=v,
                           bg=p["bg"], fg=p["fg"],
                           selectcolor=p["accent"],
                           activebackground=p["bg"],
                           font=("Helvetica", 9)
                           ).pack(side=tk.LEFT)

        # Snooze
        tk.Label(dlg, text="Snooze (min):", bg=p["bg"], fg=p["fg"],
                 font=("Helvetica", 10, "bold")).pack(pady=(12, 2))
        snooze_var = tk.IntVar(value=alarm.get("snooze", 10) if editing else 10)
        snooze_row = tk.Frame(dlg, bg=p["bg"])
        snooze_row.pack()
        for opt in SNOOZE_OPTIONS:
            tk.Radiobutton(snooze_row, text=str(opt), variable=snooze_var, value=opt,
                           bg=p["bg"], fg=p["fg"],
                           selectcolor=p["accent"],
                           activebackground=p["bg"],
                           font=("Helvetica", 10)).pack(side=tk.LEFT, padx=6)

        def _save():
            days = [i for i, v in enumerate(day_vars) if v.get()]
            if not days:
                messagebox.showwarning("Atenção", "Selecciona pelo menos um dia.", parent=dlg)
                return
            if editing:
                alarm["hour"]   = h_var.get()
                alarm["minute"] = m_var.get()
                alarm["label"]  = lbl_var.get().strip()
                alarm["days"]   = days
                alarm["snooze"] = snooze_var.get()
            else:
                self.alarms.append({
                    "id":     self._next_id,
                    "hour":   h_var.get(),
                    "minute": m_var.get(),
                    "label":  lbl_var.get().strip(),
                    "days":   days,
                    "snooze": snooze_var.get(),
                    "active": True,
                })
                self._next_id += 1
            self.on_save()
            self._refresh_list()
            dlg.destroy()

        tk.Button(dlg, text="Guardar",
                  bg=p["accent"], fg=p["fg"],
                  font=("Helvetica", 10, "bold"),
                  relief=tk.FLAT, pady=6,
                  command=_save).pack(pady=16, ipadx=20)
        
    def _edit_alarm_dialog(self, alarm: dict):
        self._new_alarm_dialog(alarm=alarm)

    def _delete_alarm(self, alarm: dict):
        if messagebox.askyesno("Confirmar", f"Apagar alarme {alarm['hour']:02d}:{alarm['minute']:02d}?",
                               parent=self):
            self.alarms.remove(alarm)
            self.on_save()
            self._refresh_list()

    # ── Disparo ───────────────────────────────────────────────────────────────
    def _alarm_triggered(self, alarm: dict):
        """Chamado pelo engine (thread daemon) — agenda na thread principal."""
        self.root.after(0, lambda: self._show_alarm_popup(alarm))

    def _show_alarm_popup(self, alarm: dict):
        p = self.palette
        notifications.notify_alarm(alarm.get("label", "Alarme"))
        
       
        play_sound("alarme_classico", repeat=4)

        popup = tk.Toplevel(self)
        popup.title("⏰ Alarme!")
        popup.configure(bg=p["bg"])
        popup.geometry("300x200")
        popup.resizable(False, False)
        popup.lift()
        popup.attributes("-topmost", True)

        time_str = f"{alarm['hour']:02d}:{alarm['minute']:02d}"
        tk.Label(popup, text="⏰", bg=p["bg"], fg=p["accent"],
                 font=("Helvetica", 32)).pack(pady=(20, 4))
        tk.Label(popup, text=time_str,
                 bg=p["bg"], fg=p["accent2"],
                 font=("Courier New", 28, "bold")).pack()
        lbl = alarm.get("label", "")
        if lbl:
            tk.Label(popup, text=lbl,
                     bg=p["bg"], fg=p["fg"],
                     font=("Helvetica", 12)).pack()

        btn_row = tk.Frame(popup, bg=p["bg"])
        btn_row.pack(pady=16)

        snooze_min = alarm.get("snooze", 10)

        
        def _dismiss():
            stop_sound()  
            popup.destroy()

        def _snooze():
            stop_sound()  
            self._engine.snooze(alarm["id"], snooze_min)
            notifications.notify_snooze(snooze_min)
            popup.destroy()

        
        popup.protocol("WM_DELETE_WINDOW", _dismiss)

        tk.Button(btn_row, text="Soneca",
                 bg=p["bg_panel"], fg=p["fg"],
                 font=("Helvetica", 10), relief=tk.FLAT, padx=12, pady=6,
                 command=_snooze).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_row, text="Dispensar",
                 bg=p["accent"], fg=p["fg"],
                 font=("Helvetica", 10, "bold"), relief=tk.FLAT, padx=12, pady=6,
                 command=_dismiss).pack(side=tk.LEFT, padx=8)

    def refresh_theme(self, palette: dict):
        self.palette = palette
        self.configure(bg=palette["bg"])
        self._refresh_list()

    def destroy(self):
        self._engine.stop()
        super().destroy()
