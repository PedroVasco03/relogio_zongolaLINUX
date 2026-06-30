"""
Painel de Definições — tema, padrão Samakaka, formato de hora.
"""

import tkinter as tk
from tkinter import ttk
from modules import theme as TH


class SettingsPanel(tk.Toplevel):
    def __init__(self, parent, palette, config, on_apply):
        super().__init__(parent)
        self.title("⚙  Definições — Relógio Zongola")
        self.configure(bg=palette["bg"])
        self.geometry("520x600")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self.palette   = palette
        self.config    = config
        self.on_apply  = on_apply   # callback(new_config)

        self._build()

    def _build(self):
        p = self.palette

        # Título
        tk.Label(self, text="⚙  DEFINIÇÕES",
                 bg=p["bg"], fg=p["accent2"],
                 font=("Helvetica", 16, "bold")).pack(pady=(20, 4))
        tk.Frame(self, bg=p["border"], height=1).pack(fill=tk.X, padx=20, pady=8)

        scroll_canvas = tk.Canvas(self, bg=p["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_canvas.pack(fill=tk.BOTH, expand=True, padx=0)

        inner = tk.Frame(scroll_canvas, bg=p["bg"])
        cw = scroll_canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        scroll_canvas.bind("<Configure>",
                           lambda e: scroll_canvas.itemconfig(cw, width=e.width))

        pad = dict(padx=24, pady=4, anchor="w")

        # ── Tema / Paleta ─────────────────────────────────────────────────────
        self._section(inner, "🎨  TEMA DE CORES")
        self._palette_var = tk.StringVar(value=self.config.get("palette", "samakaka_classico"))
        for key, info in TH.PALETTES.items():
            row = tk.Frame(inner, bg=p["bg"])
            row.pack(fill=tk.X, padx=24, pady=2)
            rb = tk.Radiobutton(row, text=info["name"],
                                variable=self._palette_var, value=key,
                                bg=p["bg"], fg=p["fg"],
                                selectcolor=p["accent"],
                                activebackground=p["bg"],
                                font=("Helvetica", 10))
            rb.pack(side=tk.LEFT)
            # Amostra de cor
            swatch = tk.Frame(row, bg=info["accent"], width=18, height=18)
            swatch.pack(side=tk.LEFT, padx=6)
            swatch2 = tk.Frame(row, bg=info["accent2"], width=18, height=18)
            swatch2.pack(side=tk.LEFT, padx=2)

        # ── Formato de hora ───────────────────────────────────────────────────
        self._section(inner, "🕐  FORMATO DE HORA")
        self._fmt_var = tk.StringVar(value=self.config.get("time_format", "24h"))
        row = tk.Frame(inner, bg=p["bg"])
        row.pack(**pad)
        for val, lbl in [("24h", "24 horas"), ("12h", "12 horas (AM/PM)")]:
            tk.Radiobutton(row, text=lbl, variable=self._fmt_var, value=val,
                           bg=p["bg"], fg=p["fg"],
                           selectcolor=p["accent"],
                           activebackground=p["bg"],
                           font=("Helvetica", 10)).pack(side=tk.LEFT, padx=10)

        # Mostrar segundos
        self._sec_var = tk.BooleanVar(value=self.config.get("show_seconds", True))
        tk.Checkbutton(inner, text="Mostrar segundos no display digital",
                       variable=self._sec_var,
                       bg=p["bg"], fg=p["fg"],
                       selectcolor=p["accent"],
                       activebackground=p["bg"],
                       font=("Helvetica", 10)).pack(**pad)

        # ── Padrão Samakaka ───────────────────────────────────────────────────
        self._section(inner, "🪢  PADRÃO SAMAKAKA")

        sak = self.config.get("samakaka", TH.SAMAKAKA_CONFIG.copy())

        self._sak_show = tk.BooleanVar(value=sak.get("show_pattern", True))
        tk.Checkbutton(inner, text="Mostrar padrão Samakaka",
                       variable=self._sak_show,
                       bg=p["bg"], fg=p["fg"],
                       selectcolor=p["accent"],
                       activebackground=p["bg"],
                       font=("Helvetica", 10)).pack(**pad)

        # Estilo do padrão
        tk.Label(inner, text="Estilo do padrão:",
                 bg=p["bg"], fg=p["fg_dim"],
                 font=("Helvetica", 9, "bold")).pack(**pad)
        self._sak_style = tk.StringVar(value=sak.get("pattern_style", "full"))
        style_row = tk.Frame(inner, bg=p["bg"])
        style_row.pack(padx=24, pady=2, anchor="w")
        styles = [("Completo", "full"), ("Borda", "border"),
                  ("Cantos", "corner"), ("Desligado", "off")]
        for lbl, val in styles:
            tk.Radiobutton(style_row, text=lbl,
                           variable=self._sak_style, value=val,
                           bg=p["bg"], fg=p["fg"],
                           selectcolor=p["accent"],
                           activebackground=p["bg"],
                           font=("Helvetica", 10)).pack(side=tk.LEFT, padx=6)

        # Opacidade
        tk.Label(inner, text="Opacidade do padrão:",
                 bg=p["bg"], fg=p["fg_dim"],
                 font=("Helvetica", 9, "bold")).pack(**pad)
        self._sak_opacity = tk.DoubleVar(value=sak.get("pattern_opacity", 0.18))
        op_row = tk.Frame(inner, bg=p["bg"])
        op_row.pack(padx=24, pady=2, anchor="w")
        tk.Scale(op_row, from_=0.0, to=1.0, resolution=0.01,
                 orient=tk.HORIZONTAL, length=240,
                 variable=self._sak_opacity,
                 bg=p["bg"], fg=p["fg"],
                 troughcolor=p["bg_card"],
                 activebackground=p["accent"],
                 highlightthickness=0,
                 showvalue=True).pack(side=tk.LEFT)

        # Escala / tamanho da célula
        tk.Label(inner, text="Tamanho da célula (px):",
                 bg=p["bg"], fg=p["fg_dim"],
                 font=("Helvetica", 9, "bold")).pack(**pad)
        self._sak_scale = tk.IntVar(value=sak.get("pattern_scale", 40))
        sc_row = tk.Frame(inner, bg=p["bg"])
        sc_row.pack(padx=24, pady=2, anchor="w")
        tk.Scale(sc_row, from_=16, to=80, resolution=4,
                 orient=tk.HORIZONTAL, length=240,
                 variable=self._sak_scale,
                 bg=p["bg"], fg=p["fg"],
                 troughcolor=p["bg_card"],
                 activebackground=p["accent"],
                 highlightthickness=0,
                 showvalue=True).pack(side=tk.LEFT)

        # ── Botão Aplicar ─────────────────────────────────────────────────────
        tk.Frame(inner, bg=p["border"], height=1).pack(fill=tk.X, padx=20, pady=16)
        tk.Button(inner, text="✔  Aplicar e Fechar",
                  bg=p["accent"], fg=p["fg"],
                  font=("Helvetica", 12, "bold"),
                  relief=tk.FLAT, pady=10, padx=30,
                  cursor="hand2",
                  command=self._apply).pack(pady=(0, 24))

    def _section(self, parent, title):
        p = self.palette
        tk.Label(parent, text=title,
                 bg=p["bg"], fg=p["accent2"],
                 font=("Helvetica", 11, "bold")).pack(padx=24, pady=(16, 4), anchor="w")
        tk.Frame(parent, bg=p["border"], height=1).pack(fill=tk.X, padx=24, pady=2)

    def _apply(self):
        self.config["palette"]     = self._palette_var.get()
        self.config["time_format"] = self._fmt_var.get()
        self.config["show_seconds"]= self._sec_var.get()
        self.config.setdefault("samakaka", {})
        self.config["samakaka"]["show_pattern"]    = self._sak_show.get()
        self.config["samakaka"]["pattern_style"]   = self._sak_style.get()
        self.config["samakaka"]["pattern_opacity"] = round(self._sak_opacity.get(), 2)
        self.config["samakaka"]["pattern_scale"]   = self._sak_scale.get()
        self.on_apply(self.config)
        self.destroy()
