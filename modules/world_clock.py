"""
Módulo Relógio Mundial — RF07
Monitorização de fusos horários usando zoneinfo (stdlib Python 3.9+) ou pytz.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
    _USE_ZONEINFO = True
except ImportError:
    try:
        import pytz
        _USE_ZONEINFO = False
    except ImportError:
        _USE_ZONEINFO = None

# Cidades populares pré-definidas
POPULAR_CITIES = [
    ("Luanda",        "Africa/Luanda"),
    ("Lisboa",        "Europe/Lisbon"),
    ("Londres",       "Europe/London"),
    ("Paris",         "Europe/Paris"),
    ("Berlim",        "Europe/Berlin"),
    ("Madrid",        "Europe/Madrid"),
    ("São Paulo",     "America/Sao_Paulo"),
    ("Nova Iorque",   "America/New_York"),
    ("Los Angeles",   "America/Los_Angeles"),
    ("Dubai",         "Asia/Dubai"),
    ("Tóquio",        "Asia/Tokyo"),
    ("Pequim",        "Asia/Shanghai"),
    ("Nairobi",       "Africa/Nairobi"),
    ("Cairo",         "Africa/Cairo"),
    ("Lagos",         "Africa/Lagos"),
    ("Joanesburgo",   "Africa/Johannesburg"),
    ("Kinshasa",      "Africa/Kinshasa"),
    ("Maputo",        "Africa/Maputo"),
    ("Moscovo",       "Europe/Moscow"),
    ("Sydney",        "Australia/Sydney"),
]


def _get_tz_object(tz_name: str):
    if _USE_ZONEINFO:
        return ZoneInfo(tz_name)
    elif _USE_ZONEINFO is False:
        import pytz
        return pytz.timezone(tz_name)
    return None


def _get_time_in_tz(tz_name: str) -> str:
    try:
        tz = _get_tz_object(tz_name)
        if tz:
            now = datetime.now(tz)
            return now.strftime("%H:%M:%S")
        return datetime.utcnow().strftime("%H:%M:%S UTC")
    except Exception:
        return "--:--:--"


def _get_date_in_tz(tz_name: str) -> str:
    try:
        tz = _get_tz_object(tz_name)
        if tz:
            now = datetime.now(tz)
            return now.strftime("%a, %d %b %Y")
        return ""
    except Exception:
        return ""


def _get_offset_str(tz_name: str) -> str:
    try:
        tz = _get_tz_object(tz_name)
        if tz:
            now = datetime.now(tz)
            offset = now.utcoffset()
            total = int(offset.total_seconds())
            sign = "+" if total >= 0 else "-"
            h, m = divmod(abs(total) // 60, 60)
            return f"UTC{sign}{h:02d}:{m:02d}"
        return ""
    except Exception:
        return ""


class WorldClockTab(tk.Frame):
    def __init__(self, parent, palette: dict, config: dict, on_save):
        super().__init__(parent, bg=palette["bg"])
        self.palette   = palette
        self.config    = config          # referência ao dict de config global
        self.on_save   = on_save         # callback para persistir
        self._cards    = []
        self._running  = True

        self._build_ui()
        self._build_cards()
        self._tick()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        p = self.palette

        # Cabeçalho + botão adicionar
        hdr = tk.Frame(self, bg=p["bg_panel"], pady=8)
        hdr.pack(fill=tk.X, pady=(0, 8))

        tk.Label(hdr, text="🌍  RELÓGIO MUNDIAL",
                 bg=p["bg_panel"], fg=p["accent2"],
                 font=("Helvetica", 13, "bold")).pack(side=tk.LEFT, padx=14)

        tk.Button(hdr, text="+ Adicionar cidade",
                  bg=p["accent"], fg=p["fg"],
                  font=("Helvetica", 9, "bold"),
                  relief=tk.FLAT, bd=0, padx=10, pady=4,
                  cursor="hand2",
                  command=self._add_city_dialog).pack(side=tk.RIGHT, padx=14)

        # Pesquisa
        sf = tk.Frame(self, bg=p["bg"])
        sf.pack(fill=tk.X, padx=14, pady=(0, 10))
        tk.Label(sf, text="Pesquisar:", bg=p["bg"], fg=p["fg_dim"],
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())
        
        self.search_entry = tk.Entry(sf, textvariable=self._search_var,
                  bg=p["bg_card"], fg=p["fg"],
                  insertbackground=p["fg"],
                  font=("Helvetica", 10), relief=tk.FLAT,
                  bd=0)
        self.search_entry.pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

        # Área de cards (scroll)
        outer = tk.Frame(self, bg=p["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=14)

        self._canvas = tk.Canvas(outer, bg=p["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient=tk.VERTICAL,
                           command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)

        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._card_frame = tk.Frame(self._canvas, bg=p["bg"])
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._card_frame, anchor="nw"
        )
        self._card_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            )
        )
        self._canvas.bind("<Configure>", self._on_canvas_resize)

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    # ── Cards ─────────────────────────────────────────────────────────────────
    def _build_cards(self):
        for w in self._card_frame.winfo_children():
            w.destroy()
        self._cards.clear()

        clocks = self.config.get("world_clocks", [])
        query  = self._search_var.get().lower() if hasattr(self, "_search_var") else ""

        for entry in clocks:
            city = entry["city"]
            tz   = entry["tz"]
            if query and query not in city.lower() and query not in tz.lower():
                continue
            card = self._make_card(entry, city, tz)
            card.pack(fill=tk.X, pady=4)
            self._cards.append((card, tz))

    def _make_card(self, entry_dict: dict, city: str, tz: str) -> tk.Frame:
        p = self.palette
        card = tk.Frame(self._card_frame, bg=p["bg_card"],
                        relief=tk.FLAT, bd=0,
                        highlightbackground=p["border"],
                        highlightthickness=1)

        # Linha esquerda colorida
        tk.Frame(card, bg=p["accent"], width=4).pack(side=tk.LEFT, fill=tk.Y)

        body = tk.Frame(card, bg=p["bg_card"])
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=10)

        row1 = tk.Frame(body, bg=p["bg_card"])
        row1.pack(fill=tk.X)

        city_lbl = tk.Label(row1, text=f"🏙 {city}",
                            bg=p["bg_card"], fg=p["fg"],
                            font=("Helvetica", 12, "bold"))
        city_lbl.pack(side=tk.LEFT)

        offset_lbl = tk.Label(row1, text=_get_offset_str(tz),
                              bg=p["bg_card"], fg=p["fg_dim"],
                              font=("Helvetica", 9))
        offset_lbl.pack(side=tk.LEFT, padx=8)

        # Botão remover baseado na referência direta do objeto do dicionário
        tk.Button(row1, text="✕",
                  bg=p["bg_card"], fg=p["fg_dim"],
                  font=("Helvetica", 9), relief=tk.FLAT, bd=0,
                  cursor="hand2",
                  command=lambda e=entry_dict: self._remove_city(e)
                 ).pack(side=tk.RIGHT)

        time_lbl = tk.Label(body, text=_get_time_in_tz(tz),
                            bg=p["bg_card"], fg=p["accent2"],
                            font=("Courier New", 28, "bold"))
        time_lbl.pack(anchor="w")

        date_lbl = tk.Label(body, text=_get_date_in_tz(tz),
                            bg=p["bg_card"], fg=p["fg_dim"],
                            font=("Helvetica", 9))
        date_lbl.pack(anchor="w")

        card._time_lbl = time_lbl
        card._date_lbl = date_lbl
        return card

    def _filter(self):
        self._build_cards()

    # ── Tick ──────────────────────────────────────────────────────────────────
    def _tick(self):
        if not self._running:
            return
        for (card, tz) in self._cards:
            try:
                if hasattr(card, "_time_lbl") and card.winfo_exists():
                    card._time_lbl.config(text=_get_time_in_tz(tz))
                    card._date_lbl.config(text=_get_date_in_tz(tz))
            except Exception:
                pass
        self.after(1000, self._tick)

    # ── Adicionar / Remover ───────────────────────────────────────────────────
    def _add_city_dialog(self):
        p = self.palette
        dlg = tk.Toplevel(self)
        dlg.title("Adicionar Cidade")
        dlg.configure(bg=p["bg"])
        dlg.geometry("400x350")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="Cidade popular:",
                 bg=p["bg"], fg=p["fg"],
                 font=("Helvetica", 10, "bold")).pack(pady=(16, 4))

        lb = tk.Listbox(dlg, bg=p["bg_card"], fg=p["fg"],
                        selectbackground=p["accent"],
                        font=("Helvetica", 10),
                        height=6, relief=tk.FLAT, bd=0)
        lb.pack(fill=tk.X, padx=20)
        for city, tz in POPULAR_CITIES:
            lb.insert(tk.END, f"{city}  ({tz})")

        sep = tk.Frame(dlg, bg=p["border"], height=1)
        sep.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(dlg, text="Ou fuso personalizado (ex: Africa/Luanda):",
                 bg=p["bg"], fg=p["fg_dim"],
                 font=("Helvetica", 9)).pack()

        row1 = tk.Frame(dlg, bg=p["bg"])
        row1.pack(fill=tk.X, padx=20, pady=2)
        
        city_var = tk.StringVar()
        tz_var   = tk.StringVar()

        tk.Label(row1, text="Nome:", bg=p["bg"], fg=p["fg"], font=("Helvetica", 9)).pack(side=tk.LEFT)
        tk.Entry(row1, textvariable=city_var, bg=p["bg_card"], fg=p["fg"],
                 font=("Helvetica", 10), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        row2 = tk.Frame(dlg, bg=p["bg"])
        row2.pack(fill=tk.X, padx=20, pady=2)
        tk.Label(row2, text="Fuso:", bg=p["bg"], fg=p["fg"], font=("Helvetica", 9)).pack(side=tk.LEFT)
        tk.Entry(row2, textvariable=tz_var, bg=p["bg_card"], fg=p["fg"],
                 font=("Helvetica", 10), relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        def _confirm():
            sel = lb.curselection()
            if sel:
                city, tz = POPULAR_CITIES[sel[0]]
            else:
                city = city_var.get().strip()
                tz   = tz_var.get().strip()
                if not city or not tz:
                    messagebox.showwarning("Atenção", "Preenche o nome e o fuso.", parent=dlg)
                    return

            # Validação do Timezone (zoneinfo ou pytz)
            if _USE_ZONEINFO is not None:
                try:
                    _get_tz_object(tz)
                except Exception:
                    messagebox.showerror("Erro", f"Fuso '{tz}' não reconhecido.", parent=dlg)
                    return
            else:
                messagebox.showwarning("Aviso", "Sem bibliotecas de fuso horário. Usando UTC padrão.")

            clocks = self.config.setdefault("world_clocks", [])
            clocks.append({"city": city, "tz": tz})
            self.on_save()
            self._build_cards()
            dlg.destroy()

        tk.Button(dlg, text="Adicionar",
                  bg=p["accent"], fg=p["fg"],
                  font=("Helvetica", 10, "bold"),
                  relief=tk.FLAT, pady=6,
                  command=_confirm).pack(pady=10, ipadx=20)

    def _remove_city(self, entry_dict: dict):
        clocks = self.config.get("world_clocks", [])
        if entry_dict in clocks:
            clocks.remove(entry_dict)
            self.on_save()
            self._build_cards()

    def refresh_theme(self, palette: dict):
        self.palette = palette
        self.configure(bg=palette["bg"])
        self.search_entry.configure(bg=palette["bg_card"], fg=palette["fg"], insertbackground=palette["fg"])
        self._build_cards()

    def destroy(self):
        self._running = False
        super().destroy()