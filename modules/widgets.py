import tkinter as tk


def btn(parent, text, command, p, style="primary", small=False):
    """
    Botão flat moderno.
    style: 'primary' | 'ghost' | 'danger' | 'muted'
    """
    pad_x = 14 if not small else 10
    pad_y =  7 if not small else 4
    font  = ("Segoe UI", 9, "bold") if small else ("Segoe UI", 10, "bold")

    colors = {
        "primary": (p["accent"],    "#FFFFFF"),
        "amber":   (p["accent2"],   "#FFFFFF"),
        "ghost":   (p["bg_input"],  p["fg"]),
        "danger":  ("#FFE8E8",      p["accent"]),
        "muted":   (p["bg_input"],  p["fg_dim"]),
        "success": (p["accent3"],   "#FFFFFF"),
    }
    bg, fg = colors.get(style, colors["ghost"])

    b = tk.Label(
        parent, text=text, bg=bg, fg=fg,
        font=font, padx=pad_x, pady=pad_y,
        cursor="hand2",
    )
    b.bind("<Button-1>", lambda e: command())

    # hover
    def _enter(e):
        if style == "primary":
            b.config(bg=_darken(p["accent"], 15))
        elif style == "ghost":
            b.config(bg=_darken(p["bg_input"], 8))
        elif style == "danger":
            b.config(bg="#FFCDD2")

    def _leave(e):
        b.config(bg=bg)

    b.bind("<Enter>", _enter)
    b.bind("<Leave>", _leave)
    return b


def icon_btn(parent, text, command, p, fg=None):
    """Botão só com ícone/texto pequeno, sem fundo."""
    b = tk.Label(
        parent, text=text,
        bg=parent["bg"], fg=fg or p["fg_muted"],
        font=("Segoe UI", 11),
        cursor="hand2", padx=4, pady=2,
    )
    b.bind("<Button-1>", lambda e: command())
    b.bind("<Enter>", lambda e: b.config(fg=p["fg"]))
    b.bind("<Leave>", lambda e: b.config(fg=fg or p["fg_muted"]))
    return b


def card(parent, p, pad_x=16, pad_y=12):
    """Frame com estilo card (fundo branco, borda sutil)."""
    f = tk.Frame(
        parent,
        bg=p["bg_card"],
        highlightbackground=p["border"],
        highlightthickness=1,
    )
    return f


def section_label(parent, text, p):
    """Rótulo de secção em maiúsculas pequenas."""
    return tk.Label(
        parent, text=text.upper(),
        bg=parent["bg"], fg=p["fg_muted"],
        font=("Segoe UI", 8, "bold"),
    )


def divider(parent, p):
    return tk.Frame(parent, bg=p["border"], height=1)


def pill_tabs(parent, labels, on_change, p):
    """
    Abas em estilo pill horizontal moderno.
    Retorna (frame, set_active(idx)).
    """
    frame = tk.Frame(parent, bg=p["bg"], pady=4)
    btns  = []
    _cur  = [0]

    def _activate(idx):
        _cur[0] = idx
        for i, b in enumerate(btns):
            if i == idx:
                b.config(bg=p["accent"], fg="#FFFFFF")
            else:
                b.config(bg=p["tab_inactive"], fg=p["tab_fg_off"])
        on_change(idx)

    for i, lbl in enumerate(labels):
        b = tk.Label(
            frame, text=lbl,
            bg=p["tab_inactive"], fg=p["tab_fg_off"],
            font=("Segoe UI", 9, "bold"),
            padx=16, pady=7,
            cursor="hand2",
        )
        b.pack(side=tk.LEFT, padx=2)
        idx = i
        b.bind("<Button-1>", lambda e, i=idx: _activate(i))
        btns.append(b)

    _activate(0)

    def set_active(idx):
        _activate(idx)

    return frame, set_active


def spinbox_modern(parent, from_, to, var, p, width=5):
    """Spinbox sem bordas antiquadas."""
    f = tk.Frame(parent, bg=p["bg_input"],
                 highlightbackground=p["border"], highlightthickness=1)
    sb = tk.Spinbox(
        f, from_=from_, to=to, textvariable=var,
        width=width, format="%02.0f",
        bg=p["bg_input"], fg=p["fg"],
        buttonbackground=p["bg_input"],
        highlightthickness=0, relief=tk.FLAT,
        font=("Consolas", 18, "bold"),
        justify=tk.CENTER,
        bd=0,
    )
    sb.pack(padx=6, pady=4)
    return f, sb


def entry_modern(parent, var, p, width=20, placeholder=""):
    """Entry sem bordas antiquadas."""
    f = tk.Frame(parent, bg=p["bg_input"],
                 highlightbackground=p["border"], highlightthickness=1)
    e = tk.Entry(
        f, textvariable=var, width=width,
        bg=p["bg_input"], fg=p["fg"],
        insertbackground=p["accent"],
        highlightthickness=0, relief=tk.FLAT,
        font=("Segoe UI", 10), bd=0,
    )
    e.pack(padx=10, pady=7, fill=tk.X)

    def _focus_in(ev):
        f.config(highlightbackground=p["accent"])
    def _focus_out(ev):
        f.config(highlightbackground=p["border"])
    e.bind("<FocusIn>",  _focus_in)
    e.bind("<FocusOut>", _focus_out)
    return f, e


def toggle_switch(parent, var, p, command=None):
    """Toggle simples usando Checkbutton restyled."""
    cb = tk.Checkbutton(
        parent, variable=var,
        bg=parent["bg"],
        activebackground=parent["bg"],
        selectcolor=p["accent"],
        fg=p["fg_dim"],
        highlightthickness=0,
        relief=tk.FLAT,
        cursor="hand2",
        command=command,
    )
    return cb


def _darken(hex_color, amount=20):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = max(0, r - amount)
    g = max(0, g - amount)
    b = max(0, b - amount)
    return f"#{r:02x}{g:02x}{b:02x}"