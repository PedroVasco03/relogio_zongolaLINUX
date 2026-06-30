"""
Módulo Temporizadores — RF06, perfis, alertas sonoros e visuais
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import time as _time
import threading
from modules.sound import play as play_sound, stop_all as stop_sound
from modules import notifications


class TimerCard(tk.Frame):
    """Um temporizador independente."""

    def __init__(self, parent, palette, name: str, seconds: int,
                 on_delete, root_ref):
        super().__init__(parent,
                         bg=palette["bg_card"],
                         highlightbackground=palette["border"],
                         highlightthickness=1)
        self.palette    = palette
        self.name       = name
        self._total     = seconds
        self._remaining = seconds
        self._running   = False
        self._on_delete = on_delete
        self._root      = root_ref
        self._build()

    def _build(self):
        p = self.palette

        # Barra lateral
        tk.Frame(self, bg=p["accent"], width=5).pack(side=tk.LEFT, fill=tk.Y)

        body = tk.Frame(self, bg=p["bg_card"])
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)

        row1 = tk.Frame(body, bg=p["bg_card"])
        row1.pack(fill=tk.X)

        self._name_lbl = tk.Label(row1, text=self.name,
                                  bg=p["bg_card"], fg=p["fg"],
                                  font=("Helvetica", 11, "bold"))
        self._name_lbl.pack(side=tk.LEFT)

        tk.Button(row1, text="✕",
                  bg=p["bg_card"], fg=p["fg_dim"],
                  font=("Helvetica", 9), relief=tk.FLAT, bd=0,
                  cursor="hand2",
                  command=self._on_delete).pack(side=tk.RIGHT)

        self._disp = tk.Label(body, text=self._fmt(self._remaining),
                              bg=p["bg_card"], fg=p["accent2"],
                              font=("Courier New", 30, "bold"))
        self._disp.pack(anchor="w")

        # Barra de progresso
        self._prog_bg = tk.Frame(body, bg=p["bg_panel"], height=4)
        self._prog_bg.pack(fill=tk.X, pady=(2, 6))
        self._prog_bar = tk.Frame(self._prog_bg, bg=p["accent"], height=4)
        self._prog_bar.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        btn_row = tk.Frame(body, bg=p["bg_card"])
        btn_row.pack(anchor="w")

        self._toggle_btn = tk.Button(btn_row, text="▶",
                                     bg=p["accent"], fg=p["fg"],
                                     font=("Helvetica", 10, "bold"),
                                     relief=tk.FLAT, padx=10, pady=3,
                                     cursor="hand2",
                                     command=self._toggle)
        self._toggle_btn.pack(side=tk.LEFT, padx=2)

        tk.Button(btn_row, text="↺",
                  bg=p["bg_panel"], fg=p["fg"],
                  font=("Helvetica", 10), relief=tk.FLAT, padx=8, pady=3,
                  cursor="hand2",
                  command=self._reset).pack(side=tk.LEFT, padx=2)

    def _toggle(self):
        if self._remaining <= 0:
            self._reset()
            return
        self._running = not self._running
        if self._running:
            self._toggle_btn.config(text="⏸")
            self._tick()
        else:
            self._toggle_btn.config(text="▶")

    def _reset(self):
        self._running   = False
        self._remaining = self._total
        self._toggle_btn.config(text="▶")
        self._disp.config(text=self._fmt(self._remaining),
                          fg=self.palette["accent2"])
        self._update_progress()

    def _tick(self):
        if not self._running:
            return
        if self._remaining <= 0:
            self._running = False
            self._disp.config(text="00:00:00", fg=self.palette["accent"])
            self._toggle_btn.config(text="▶")
            self._prog_bar.place_configure(relwidth=0)
            
            # 🔥 CORREÇÃO DO MOTOR DE SOM 🔥
            notifications.notify_timer_end(self.name)
            play_sound("alarme_classico", repeat=3) # Utiliza o motor multiplataforma estável
            
            self._show_finished_popup()
            return
        self._remaining -= 1
        self._disp.config(text=self._fmt(self._remaining))
        self._update_progress()
        self.after(1000, self._tick)

    def _update_progress(self):
        ratio = self._remaining / self._total if self._total > 0 else 0
        self._prog_bar.place_configure(relwidth=ratio)

    def _show_finished_popup(self):
        p = self.palette
        popup = tk.Toplevel(self)
        popup.title("Temporizador concluído")
        popup.configure(bg=p["bg"])
        popup.geometry("280x160")
        popup.attributes("-topmost", True)
        popup.lift()

        # Garante que se fechar no "X" da janela, o som também é interrompido
        def _close_popup():
            stop_sound()
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", _close_popup)

        tk.Label(popup, text="⏱  Tempo esgotado!",
                 bg=p["bg"], fg=p["accent2"],
                 font=("Helvetica", 14, "bold")).pack(pady=(24, 6))
        tk.Label(popup, text=self.name,
                 bg=p["bg"], fg=p["fg"],
                 font=("Helvetica", 11)).pack()
        
        tk.Button(popup, text="OK",
                  bg=p["accent"], fg=p["fg"],
                  font=("Helvetica", 10, "bold"),
                  relief=tk.FLAT, padx=20, pady=6,
                  command=_close_popup).pack(pady=16)

    @staticmethod
    def _fmt(s: int) -> str:
        s = max(0, s)
        h = s // 3600
        m = (s % 3600) // 60
        se = s % 60
        return f"{h:02d}:{m:02d}:{se:02d}"

    def refresh_theme(self, palette):
        self.palette = palette


class TimersTab(tk.Frame):
    def __init__(self, parent, palette, profiles: list, on_save, root_ref):
        super().__init__(parent, bg=palette["bg"])
        self.palette   = palette
        self.profiles  = profiles
        self.on_save   = on_save
        self._root     = root_ref
        self._cards    = []
        self._build_ui()

    def _build_ui(self):
        p = self.palette

        hdr = tk.Frame(self, bg=p["bg_panel"], pady=8)
        hdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr, text="⏳  TEMPORIZADORES",
                 bg=p["bg_panel"], fg=p["accent2"],
                 font=("Helvetica", 13, "bold")).pack(side=tk.LEFT, padx=14)

        btn_row = tk.Frame(hdr, bg=p["bg_panel"])
        btn_row.pack(side=tk.RIGHT, padx=14)
        tk.Button(btn_row, text="+ Personalizado",
                  bg=p["accent"], fg=p["fg"],
                  font=("Helvetica", 9, "bold"),
                  relief=tk.FLAT, bd=0, padx=10, pady=4,
                  cursor="hand2",
                  command=self._custom_dialog).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="Guardar Perfil",
                  bg=p["bg_card"], fg=p["fg"],
                  font=("Helvetica", 9),
                  relief=tk.FLAT, bd=0, padx=10, pady=4,
                  cursor="hand2",
                  command=self._save_profile_dialog).pack(side=tk.LEFT, padx=4)

        pf = tk.Frame(self, bg=p["bg"], pady=6)
        pf.pack(fill=tk.X, padx=14)
        tk.Label(pf, text="Perfis rápidos:",
                 bg=p["bg"], fg=p["fg_dim"],
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self._profiles_frame = tk.Frame(pf, bg=p["bg"])
        self._profiles_frame.pack(side=tk.LEFT, padx=8)
        self._draw_profiles()

        outer = tk.Frame(self, bg=p["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=14, pady=4)

        canvas = tk.Canvas(outer, bg=p["bg"], highlightthickness=0)
        sb = tk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._cards_frame = tk.Frame(canvas, bg=p["bg"])
        cw = canvas.create_window((0, 0), window=self._cards_frame, anchor="nw")
        self._cards_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))

    def _draw_profiles(self):
        p = self.palette
        for w in self._profiles_frame.winfo_children():
            w.destroy()
        for prof in self.profiles:
            tk.Button(self._profiles_frame,
                      text=f"{prof['name']} ({self._fmt(prof['seconds'])})",
                      bg=p["bg_card"], fg=p["accent2"],
                      font=("Helvetica", 9), relief=tk.FLAT, bd=0,
                      padx=8, pady=3, cursor="hand2",
                      command=lambda pr=prof: self._add_card(pr["name"], pr["seconds"])
                      ).pack(side=tk.LEFT, padx=3)

    def _add_card(self, name: str, seconds: int):
        p = self.palette
        idx = len(self._cards)

        def _remove():
            card.destroy()
            self._cards.pop(idx)

        card = TimerCard(self._cards_frame, p, name, seconds, _remove, self._root)
        card.pack(fill=tk.X, pady=4)
        self._cards.append(card)

    def _custom_dialog(self):
        p = self.palette
        dlg = tk.Toplevel(self)
        dlg.title("Novo Temporizador")
        dlg.configure(bg=p["bg"])
        dlg.geometry("320x260")
        dlg.resizable(False, False)

        tk.Label(dlg, text="Nome:", bg=p["bg"], fg=p["fg"],
                 font=("Helvetica", 10, "bold")).pack(pady=(16, 2))
        name_var = tk.StringVar(value="Temporizador")
        tk.Entry(dlg, textvariable=name_var,
                 bg=p["bg_card"], fg=p["fg"],
                 font=("Helvetica", 11), relief=tk.FLAT).pack(padx=30, fill=tk.X)

        tk.Label(dlg, text="Duração:", bg=p["bg"], fg=p["fg"],
                 font=("Helvetica", 10, "bold")).pack(pady=(12, 2))
        row = tk.Frame(dlg, bg=p["bg"])
        row.pack()
        h_v = tk.IntVar(value=0)
        m_v = tk.IntVar(value=5)
        s_v = tk.IntVar(value=0)
        for var, lbl, mx in [(h_v, "h", 23), (m_v, "m", 59), (s_v, "s", 59)]:
            tk.Spinbox(row, from_=0, to=mx, textvariable=var, width=4,
                       format="%02.0f",
                       bg=p["bg_card"], fg=p["accent2"], state="readonly",
                       buttonbackground=p["bg_panel"],
                       font=("Courier New", 16, "bold"), relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
            tk.Label(row, text=lbl, bg=p["bg"], fg=p["fg_dim"],
                     font=("Helvetica", 10)).pack(side=tk.LEFT)

        def _ok():
            secs = h_v.get()*3600 + m_v.get()*60 + s_v.get()
            if secs <= 0:
                messagebox.showwarning("Atenção", "Duração deve ser maior que zero.", parent=dlg)
                return
            self._add_card(name_var.get().strip() or "Timer", secs)
            dlg.destroy()

        tk.Button(dlg, text="Adicionar",
                  bg=p["accent"], fg=p["fg"],
                  font=("Helvetica", 10, "bold"),
                  relief=tk.FLAT, pady=6,
                  command=_ok).pack(pady=16, ipadx=20)

    def _save_profile_dialog(self):
        p = self.palette
        name = simpledialog.askstring("Guardar Perfil", "Nome do perfil:",
                                      parent=self)
        if not name:
            return
        secs_str = simpledialog.askstring("Guardar Perfil",
                                           "Duração em segundos (ex: 1500):",
                                           parent=self)
        try:
            secs = int(secs_str)
        except (TypeError, ValueError):
            messagebox.showerror("Erro", "Número inválido.", parent=self)
            return
        self.profiles.append({"name": name, "seconds": secs})
        self.on_save()
        self._draw_profiles()

    @staticmethod
    def _fmt(s: int) -> str:
        h = s // 3600
        m = (s % 3600) // 60
        se = s % 60
        parts = []
        if h: parts.append(f"{h}h")
        if m: parts.append(f"{m}m")
        if se or not parts: parts.append(f"{se}s")
        return "".join(parts)

    def refresh_theme(self, palette):
        self.palette = palette
        self.configure(bg=palette["bg"])