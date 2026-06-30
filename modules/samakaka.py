"""
Motor de Padrão Samakaka — desenhado via tkinter Canvas com Cairo-style logic.
Suporta estilos: full, border, corner, off.
"""

import math


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _blend_alpha(fg_hex: str, bg_hex: str, alpha: float) -> str:
    """Blende fg sobre bg com alpha dado, retorna hex resultante."""
    fr, fg, fb = _hex_to_rgb(fg_hex)
    br, bg_, bb = _hex_to_rgb(bg_hex)
    r = int(fr * alpha + br * (1 - alpha))
    g = int(fg * alpha + bg_ * (1 - alpha))
    b = int(fb * alpha + bb * (1 - alpha))
    return f"#{r:02x}{g:02x}{b:02x}"


def draw_samakaka(canvas, width: int, height: int, cfg: dict, bg_color: str):
    """
    Desenha o padrão Samakaka sobre o canvas tkinter.
    cfg: dicionário de SAMAKAKA_CONFIG
    bg_color: cor de fundo actual do tema
    """
    canvas.delete("samakaka")

    style = cfg.get("pattern_style", "full")
    if style == "off" or not cfg.get("show_pattern", True):
        return

    opacity = float(cfg.get("pattern_opacity", 0.18))
    scale   = int(cfg.get("pattern_scale", 40))
    c_red   = _blend_alpha(cfg.get("color_red",    "#C8202A"), bg_color, opacity)
    c_yel   = _blend_alpha(cfg.get("color_yellow", "#F5A623"), bg_color, opacity)
    c_blk   = _blend_alpha(cfg.get("color_black",  "#0A0A0A"), bg_color, opacity * 0.5)

    tag = "samakaka"

    def _draw_cell(x0, y0):
        """Desenha uma célula 2×2 do padrão Samakaka (losangos + cruz)."""
        s = scale
        h = s // 2
        q = s // 4

        # fundo da célula — quadrado dividido em triângulos
        # Triângulo topo (vermelho)
        canvas.create_polygon(
            x0, y0,  x0+s, y0,  x0+h, y0+h,
            fill=c_red, outline="", tags=tag
        )
        # Triângulo base (vermelho)
        canvas.create_polygon(
            x0, y0+s,  x0+s, y0+s,  x0+h, y0+h,
            fill=c_red, outline="", tags=tag
        )
        # Triângulo esquerdo (preto)
        canvas.create_polygon(
            x0, y0,  x0, y0+s,  x0+h, y0+h,
            fill=c_blk, outline="", tags=tag
        )
        # Triângulo direito (preto)
        canvas.create_polygon(
            x0+s, y0,  x0+s, y0+s,  x0+h, y0+h,
            fill=c_blk, outline="", tags=tag
        )
        # Losango central (amarelo)
        canvas.create_polygon(
            x0+h, y0+q,
            x0+h+q, y0+h,
            x0+h, y0+h+q,
            x0+h-q, y0+h,
            fill=c_yel, outline="", tags=tag
        )

    if style == "full":
        cols = math.ceil(width  / scale) + 1
        rows = math.ceil(height / scale) + 1
        for row in range(rows):
            for col in range(cols):
                _draw_cell(col * scale, row * scale)

    elif style == "border":
        # Apenas faixa à volta (bordas)
        border_w = scale * 2
        # topo
        cols = math.ceil(width / scale) + 1
        for col in range(cols):
            for row in range(math.ceil(border_w / scale) + 1):
                _draw_cell(col * scale, row * scale)
        # base
        y_start = height - border_w
        for col in range(cols):
            for row in range(math.ceil(border_w / scale) + 1):
                _draw_cell(col * scale, y_start + row * scale)
        # lados
        rows = math.ceil(height / scale) + 1
        for row in range(rows):
            for col in range(math.ceil(border_w / scale) + 1):
                _draw_cell(col * scale, row * scale)
            x_start = width - border_w
            for col in range(math.ceil(border_w / scale) + 1):
                _draw_cell(x_start + col * scale, row * scale)

    elif style == "corner":
        # Apenas cantos (quadrantes 4×4 células)
        corner_size = scale * 3
        positions = [
            (0, 0),
            (width - corner_size, 0),
            (0, height - corner_size),
            (width - corner_size, height - corner_size),
        ]
        for cx, cy in positions:
            for row in range(math.ceil(corner_size / scale) + 1):
                for col in range(math.ceil(corner_size / scale) + 1):
                    _draw_cell(cx + col * scale, cy + row * scale)

    # Linha decorativa horizontal no topo e base
    lw = max(2, scale // 10)
    lc = _blend_alpha(cfg.get("color_yellow", "#F5A623"), bg_color, min(opacity * 1.5, 1.0))
    if style != "off":
        canvas.create_line(0, scale*2, width, scale*2, fill=lc, width=lw, tags=tag)
        canvas.create_line(0, height-scale*2, width, height-scale*2, fill=lc, width=lw, tags=tag)
