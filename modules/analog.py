"""
Motor de Relógio Analógico — desenhado via tkinter Canvas.
RF01: Exibição digital e analógica com precisão de segundos.
"""

import math


def draw_analog_clock(canvas, cx: int, cy: int, r: int,
                      hour: int, minute: int, second: int,
                      palette: dict):
    """
    Desenha relógio analógico centrado em (cx, cy) com raio r.
    Limpa apenas elementos com tag 'analog'.
    """
    canvas.delete("analog")
    tag = "analog"

    bg      = palette["canvas_bg"]
    accent  = palette["accent"]
    accent2 = palette["accent2"]
    fg      = palette["fg"]
    fg_dim  = palette["fg_dim"]
    border  = palette["border"]

    # ── Face do relógio ───────────────────────────────────────────────────────
    canvas.create_oval(
        cx-r, cy-r, cx+r, cy+r,
        fill=bg, outline=border, width=3, tags=tag
    )

    # Anel decorativo exterior
    canvas.create_oval(
        cx-r+4, cy-r+4, cx+r-4, cy+r-4,
        fill="", outline=accent2, width=1, tags=tag
    )

    # ── Marcadores de horas ───────────────────────────────────────────────────
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        if i % 3 == 0:
            r_outer = r - 8
            r_inner = r - 20
            w = 3
            col = accent2
        else:
            r_outer = r - 12
            r_inner = r - 20
            w = 1
            col = fg_dim
        x1 = cx + r_outer * math.cos(angle)
        y1 = cy + r_outer * math.sin(angle)
        x2 = cx + r_inner * math.cos(angle)
        y2 = cy + r_inner * math.sin(angle)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w, tags=tag)

    # Números nos 4 pontos cardeais
    for i, label in [(0, "12"), (3, "3"), (6, "6"), (9, "9")]:
        angle = math.radians(i * 30 - 90)
        rx = cx + (r - 32) * math.cos(angle)
        ry = cy + (r - 32) * math.sin(angle)
        canvas.create_text(rx, ry, text=label,
                           fill=fg, font=("Courier New", max(9, r//8), "bold"),
                           tags=tag)

    # ── Ponteiros ─────────────────────────────────────────────────────────────
    def _hand(angle_deg, length, width, color, cap="round"):
        angle_rad = math.radians(angle_deg - 90)
        # base traseira pequena
        bx = cx - (length * 0.15) * math.cos(angle_rad)
        by = cy - (length * 0.15) * math.sin(angle_rad)
        tx = cx + length * math.cos(angle_rad)
        ty = cy + length * math.sin(angle_rad)
        canvas.create_line(bx, by, tx, ty,
                           fill=color, width=width,
                           capstyle=cap, tags=tag)

    # Hora
    h_angle = (hour % 12) * 30 + minute * 0.5
    _hand(h_angle, r * 0.55, max(4, r // 12), fg)

    # Minuto
    m_angle = minute * 6 + second * 0.1
    _hand(m_angle, r * 0.78, max(3, r // 18), fg)

    # Segundo
    s_angle = second * 6
    _hand(s_angle, r * 0.85, max(1, r // 30), accent)

    # Centro
    cr = max(5, r // 14)
    canvas.create_oval(
        cx-cr, cy-cr, cx+cr, cy+cr,
        fill=accent, outline=accent2, width=2, tags=tag
    )
    canvas.create_oval(
        cx-2, cy-2, cx+2, cy+2,
        fill=accent2, outline="", tags=tag
    )
