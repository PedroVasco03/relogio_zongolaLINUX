#!/usr/bin/env python3
"""
Relógio Zongola — Aplicação Desktop Linux
Sistema Operativo Zongola | Universidade Metodista de Angola
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import sys, os

# Garante que os módulos são encontrados independente do directório de execução
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import theme as TH
from modules import persistence as DB
from modules.samakaka  import draw_samakaka
from modules.analog    import draw_analog_clock
from modules.alarms    import AlarmsTab
from modules.stopwatch import StopwatchTab
from modules.timers    import TimersTab
from modules.world_clock import WorldClockTab
from modules.world_cup   import WorldCupTab
from modules.settings  import SettingsPanel
from modules.sound     import play as play_sound, stop_all as stop_sound


# ─────────────────────────────────────────────────────────────────────────────
class RelogioZongola(tk.Tk):
    WIDTH  = 900
    HEIGHT = 640

    def __init__(self):
        super().__init__()

        # Carregar configuração XDG
        self._cfg     = DB.load_config()
        self._alarms  = DB.load_alarms()
        self._profiles= DB.load_timer_profiles()
        TH.set_palette(self._cfg.get("palette", "samakaka_classico"))
        p = TH.get_palette()

        # Janela principal
        self.title("Relógio Zongola")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(820, 560)
        self.configure(bg=p["bg"])

        
        try:
            self.iconbitmap("")
        except Exception:
            pass

        self._build_ui()
        self._apply_theme()
        self._tick()

    # ── Construção da UI ──────────────────────────────────────────────────────
    def _build_ui(self):
        p = TH.get_palette()

        # ── Painel esquerdo: relógio principal ────────────────────────────────
        self._left = tk.Frame(self, bg=p["bg"], width=320)
        self._left.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self._left.pack_propagate(False)

        # Canvas para fundo Samakaka + relógio analógico
        self._bg_canvas = tk.Canvas(self._left, bg=p["canvas_bg"],
                                    highlightthickness=0, width=320)
        self._bg_canvas.pack(fill=tk.BOTH, expand=True)
        self._bg_canvas.bind("<Configure>", self._on_left_resize)

        # Display digital (sobre o canvas via label)
        self._digital_frame = tk.Frame(self._bg_canvas,
                                       bg=p["canvas_bg"])
        self._canvas_digital = self._bg_canvas.create_window(
            160, 20, window=self._digital_frame, anchor="n"
        )

        self._time_var = tk.StringVar(value="00:00:00")
        self._date_var = tk.StringVar(value="")

        self._time_lbl = tk.Label(self._digital_frame,
                                  textvariable=self._time_var,
                                  bg=p["canvas_bg"], fg=p["digit_color"],
                                  font=("Courier New", 32, "bold"))
        self._time_lbl.pack()

        self._date_lbl = tk.Label(self._digital_frame,
                                  textvariable=self._date_var,
                                  bg=p["canvas_bg"], fg=p["fg_dim"],
                                  font=("Helvetica", 9))
        self._date_lbl.pack()

        # Título / logo
        self._logo_id = self._bg_canvas.create_text(
            160, 0, text="RELÓGIO ZONGOLA",
            fill=p["accent2"],
            font=("Helvetica", 10, "bold"),
            anchor="n"
        )

        # Botão de definições no canto inferior
        self._settings_btn = tk.Button(
            self._left, text="⚙  Definições",
            bg=p["bg_panel"], fg=p["fg_dim"],
            font=("Helvetica", 9), relief=tk.FLAT, bd=0, pady=6,
            cursor="hand2",
            command=self._open_settings
        )
        self._settings_btn.pack(fill=tk.X, side=tk.BOTTOM)

        # Separador vertical
        tk.Frame(self, bg=TH.get_palette()["border"], width=2).pack(
            side=tk.LEFT, fill=tk.Y
        )

        # ── Painel direito: abas ──────────────────────────────────────────────
        self._right = tk.Frame(self, bg=p["bg"])
        self._right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_tabs()

    def _build_tabs(self):
        p = TH.get_palette()

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Z.TNotebook",
                        background=p["bg"],
                        borderwidth=0)
        style.configure("Z.TNotebook.Tab",
                        background=p["bg_panel"],
                        foreground=p["fg_dim"],
                        padding=[16, 8],
                        font=("Helvetica", 10, "bold"),
                        borderwidth=0)
        style.map("Z.TNotebook.Tab",
                  background=[("selected", p["bg_card"]),
                               ("active",   p["bg_card"])],
                  foreground=[("selected", p["accent2"]),
                               ("active",   p["fg"])])

        self._nb = ttk.Notebook(self._right, style="Z.TNotebook")
        self._nb.pack(fill=tk.BOTH, expand=True)

        # Alarmes
        self._tab_alarms = AlarmsTab(
            self._nb, p, self._alarms,
            on_save=self._save_alarms,
            root_ref=self
        )
        self._nb.add(self._tab_alarms, text="⏰  Alarme")

        # Cronómetro
        self._tab_sw = StopwatchTab(self._nb, p)
        self._nb.add(self._tab_sw, text="⏱  Cronómetro")

        # Temporizadores
        self._tab_timers = TimersTab(
            self._nb, p, self._profiles,
            on_save=self._save_profiles,
            root_ref=self
        )
        self._nb.add(self._tab_timers, text="⏳  Temporizador")

        # Relógio Mundial
        self._tab_world = WorldClockTab(
            self._nb, p, self._cfg,
            on_save=self._save_config
        )
        self._nb.add(self._tab_world, text="🌍 Relógio Mundial")

        self._tab_wcup = WorldCupTab(
            self._nb, p, self._cfg,
            on_save=self._save_config,
            root_ref=self
        )
        self._nb.add(self._tab_wcup, text="⚽ Mundial — Jogos")
    
    def _tick(self):
        now   = datetime.now()
        fmt   = self._cfg.get("time_format", "24h")
        show_s= self._cfg.get("show_seconds", True)

        if fmt == "12h":
            time_str = now.strftime("%I:%M:%S %p" if show_s else "%I:%M %p")
        else:
            time_str = now.strftime("%H:%M:%S" if show_s else "%H:%M")

        DAYS_PT = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        
        date_str = f"{DAYS_PT[now.weekday()]}, {now.strftime('%d/%m/%Y')}"

        self._time_var.set(time_str)
        self._date_var.set(date_str)

        # Relógio analógico
        self._draw_clock_face(now.hour, now.minute, now.second)

        # ── Vínculo do Motor de Som e Alarmes ─────────────────────────────────
        if hasattr(self, "_tab_alarms") and hasattr(self._tab_alarms, "check_alarms"):
            self._tab_alarms.check_alarms(now)

        self.after(1000, self._tick)

    def _draw_clock_face(self, h, m, s):
        c = self._bg_canvas
        w = c.winfo_width()
        ht = c.winfo_height()
        if w < 10 or ht < 10:
            return

        # Padrão Samakaka (fundo)
        sak_cfg = self._cfg.get("samakaka", TH.SAMAKAKA_CONFIG.copy())
        p = TH.get_palette()
        draw_samakaka(c, w, ht, sak_cfg, p["canvas_bg"])

        # Reposicionar display digital e logo
        c.coords(self._canvas_digital, w // 2, 14)
        c.coords(self._logo_id, w // 2, ht - 14)
        c.itemconfig(self._logo_id, anchor="s")

        # Relógio analógico centrado
        digital_h = 70  
        logo_h    = 24
        avail_h   = ht - digital_h - logo_h
        cx = w // 2
        cy = digital_h + avail_h // 2
        r  = min(w // 2 - 18, avail_h // 2 - 10)
        r  = max(r, 40)

        draw_analog_clock(c, cx, cy, r, h, m, s, p)

    def _on_left_resize(self, event):
        now = datetime.now()
        self._draw_clock_face(now.hour, now.minute, now.second)

    # ── Definições e Tema ─────────────────────────────────────────────────────
    def _open_settings(self):
        SettingsPanel(self, TH.get_palette(), self._cfg,
                      on_apply=self._on_settings_applied)

    def _on_settings_applied(self, new_cfg):
        self._cfg = new_cfg
        TH.set_palette(new_cfg.get("palette", "samakaka_classico"))
        self._save_config()
        self._apply_theme()

    def _apply_theme(self):
        p = TH.get_palette()
        self.configure(bg=p["bg"])

        # Painel esquerdo
        self._left.configure(bg=p["bg"])
        self._bg_canvas.configure(bg=p["canvas_bg"])
        self._digital_frame.configure(bg=p["canvas_bg"])
        self._time_lbl.configure(bg=p["canvas_bg"], fg=p["digit_color"])
        self._date_lbl.configure(bg=p["canvas_bg"], fg=p["fg_dim"])
        self._settings_btn.configure(bg=p["bg_panel"], fg=p["fg_dim"])
        self._bg_canvas.itemconfig(self._logo_id, fill=p["accent2"])

        # Tabs
        style = ttk.Style(self)
        style.configure("Z.TNotebook", background=p["bg"])
        style.configure("Z.TNotebook.Tab",
                        background=p["bg_panel"], foreground=p["fg_dim"])
        style.map("Z.TNotebook.Tab",
                  background=[("selected", p["bg_card"]), ("active", p["bg_card"])],
                  foreground=[("selected", p["accent2"]), ("active", p["fg"])])

        self._right.configure(bg=p["bg"])

        # Propagar para abas
        for tab in [self._tab_alarms, self._tab_sw,
            self._tab_timers, self._tab_world, self._tab_wcup]:
            try:
                tab.refresh_theme(p)
            except Exception:
                pass

    # ── Persistência ──────────────────────────────────────────────────────────
    def _save_config(self):
        DB.save_config(self._cfg)

    def _save_alarms(self):
        DB.save_alarms(self._alarms)

    def _save_profiles(self):
        DB.save_timer_profiles(self._profiles)

    # ── Fechar ────────────────────────────────────────────────────────────────
    def on_close(self):
        stop_sound()
        self._save_config()
        self._save_alarms()
        self._save_profiles()
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
def main():
    app = RelogioZongola()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
