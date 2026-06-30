"""
Módulo Cronómetro — RF04, RF05 (voltas), exportação CSV
"""

import tkinter as tk
from tkinter import messagebox
import time as _time
from modules import persistence


class StopwatchTab(tk.Frame):
    def __init__(self, parent, palette):
        super().__init__(parent, bg=palette["bg"])
        self.palette   = palette
        self._running  = False
        self._start_t  = 0.0
        self._elapsed  = 0.0
        self._laps     = []          # [(parcial_str, total_str)]
        self._lap_base = 0.0
        self._build_ui()

    def _build_ui(self):
        p = self.palette

        hdr = tk.Frame(self, bg=p["bg_panel"], pady=8)
        hdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr, text="⏱  CRONÓMETRO",
                 bg=p["bg_panel"], fg=p["accent2"],
                 font=("Helvetica", 13, "bold")).pack(side=tk.LEFT, padx=14)

        # Display principal
        disp = tk.Frame(self, bg=p["bg"], pady=20)
        disp.pack()

        self._time_lbl = tk.Label(disp, text="00:00:00.000",
                                  bg=p["bg"], fg=p["accent2"],
                                  font=("Courier New", 48, "bold"))
        self._time_lbl.pack()

        self._lap_time_lbl = tk.Label(disp, text="Volta actual: 00:00:00.000",
                                      bg=p["bg"], fg=p["fg_dim"],
                                      font=("Courier New", 14))
        self._lap_time_lbl.pack()

        # Botões
        btn_row = tk.Frame(self, bg=p["bg"])
        btn_row.pack(pady=10)

        self._start_btn = tk.Button(btn_row, text="▶  Iniciar",
                                    bg=p["accent"], fg=p["fg"],
                                    font=("Helvetica", 12, "bold"),
                                    relief=tk.FLAT, padx=18, pady=8,
                                    cursor="hand2",
                                    command=self._toggle)
        self._start_btn.pack(side=tk.LEFT, padx=6)

        tk.Button(btn_row, text="⊙  Volta",
                  bg=p["bg_card"], fg=p["fg"],
                  font=("Helvetica", 12), relief=tk.FLAT, padx=14, pady=8,
                  cursor="hand2",
                  command=self._lap).pack(side=tk.LEFT, padx=6)

        tk.Button(btn_row, text="↺  Reiniciar",
                  bg=p["bg_card"], fg=p["fg"],
                  font=("Helvetica", 12), relief=tk.FLAT, padx=14, pady=8,
                  cursor="hand2",
                  command=self._reset).pack(side=tk.LEFT, padx=6)

        tk.Button(btn_row, text="⬇  Exportar CSV",
                  bg=p["bg_card"], fg=p["accent2"],
                  font=("Helvetica", 12), relief=tk.FLAT, padx=14, pady=8,
                  cursor="hand2",
                  command=self._export).pack(side=tk.LEFT, padx=6)

        # Tabela de voltas
        lap_hdr = tk.Frame(self, bg=p["bg_panel"])
        lap_hdr.pack(fill=tk.X, padx=14, pady=(10, 0))
        for txt, w in [("#", 4), ("Parcial", 14), ("Total", 14)]:
            tk.Label(lap_hdr, text=txt, bg=p["bg_panel"], fg=p["fg_dim"],
                     font=("Helvetica", 9, "bold"), width=w, anchor="w").pack(side=tk.LEFT)

        self._lap_frame = tk.Frame(self, bg=p["bg"])
        self._lap_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=4)

    # ── Controlo ──────────────────────────────────────────────────────────────
    def _toggle(self):
        if self._running:
            self._elapsed += _time.time() - self._start_t
            self._running  = False
            self._start_btn.config(text="▶  Retomar", bg=self.palette["accent"])
        else:
            self._start_t = _time.time()
            self._running = True
            self._start_btn.config(text="⏸  Pausar", bg=self.palette["accent3"])
            self._tick()

    def _reset(self):
        self._running  = False
        self._elapsed  = 0.0
        self._lap_base = 0.0
        self._laps     = []
        self._start_btn.config(text="▶  Iniciar", bg=self.palette["accent"])
        self._time_lbl.config(text="00:00:00.000")
        self._lap_time_lbl.config(text="Volta actual: 00:00:00.000")
        for w in self._lap_frame.winfo_children():
            w.destroy()

    def _lap(self):
        if not self._running and self._elapsed == 0:
            return
        total   = self._elapsed + (_time.time() - self._start_t if self._running else 0)
        parcial = total - self._lap_base
        self._lap_base = total
        self._laps.append((self._fmt(parcial), self._fmt(total)))
        self._draw_laps()

    def _export(self):
        if not self._laps:
            messagebox.showinfo("Cronómetro", "Nenhuma volta registada.", parent=self)
            return
        path = persistence.export_laps(self._laps)
        messagebox.showinfo("Exportado", f"Ficheiro guardado em:\n{path}", parent=self)

    # ── Tick ──────────────────────────────────────────────────────────────────
    def _tick(self):
        if not self._running:
            return
        total   = self._elapsed + (_time.time() - self._start_t)
        parcial = total - self._lap_base
        self._time_lbl.config(text=self._fmt(total))
        self._lap_time_lbl.config(text=f"Volta actual: {self._fmt(parcial)}")
        self.after(33, self._tick)   # ~30 fps

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _fmt(s: float) -> str:
        s = max(0.0, s)
        h  = int(s // 3600)
        m  = int((s % 3600) // 60)
        se = s % 60
        ms = int((se - int(se)) * 1000)
        return f"{h:02d}:{m:02d}:{int(se):02d}.{ms:03d}"

    def _draw_laps(self):
        p = self.palette
        for w in self._lap_frame.winfo_children():
            w.destroy()
        for i, (parcial, total) in enumerate(reversed(self._laps), 1):
            n = len(self._laps) - i + 1
            row = tk.Frame(self._lap_frame,
                           bg=p["bg_card"] if i % 2 == 0 else p["bg"])
            row.pack(fill=tk.X, pady=1)
            fg = p["accent2"] if i == 1 else p["fg"]
            for txt, w in [(str(n), 4), (parcial, 14), (total, 14)]:
                tk.Label(row, text=txt, bg=row["bg"], fg=fg,
                         font=("Courier New", 10), width=w, anchor="w").pack(side=tk.LEFT)

    def refresh_theme(self, palette):
        self.palette = palette
        self.configure(bg=palette["bg"])
