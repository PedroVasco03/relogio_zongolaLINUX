"""
Módulo de Tema — Relógio Zongola
Paleta africana com suporte a padrão Samakaka parametrizável.
"""

# ── Paletas disponíveis ────────────────────────────────────────────────────────
PALETTES = {
    "samakaka_classico": {
        "name": "Samakaka Clássico",
        "bg":           "#0D0D0D",
        "bg_panel":     "#1A1A1A",
        "bg_card":      "#222222",
        "accent":       "#C8202A",   # vermelho Samakaka
        "accent2":      "#F5A623",   # amarelo/dourado
        "accent3":      "#1B5E20",   # verde (terceira cor do pano)
        "fg":           "#F0E6D3",   # areia clara
        "fg_dim":       "#9E9E9E",
        "border":       "#C8202A",
        "digit_color":  "#F5A623",
        "second_color": "#C8202A",
        "canvas_bg":    "#111111",
    },
    "samakaka_noite": {
        "name": "Samakaka Noite Azul",
        "bg":           "#050A1A",
        "bg_panel":     "#0D1B2A",
        "bg_card":      "#112240",
        "accent":       "#C8202A",
        "accent2":      "#E8C547",
        "accent3":      "#2E7D32",
        "fg":           "#CDD6F4",
        "fg_dim":       "#6C7086",
        "border":       "#C8202A",
        "digit_color":  "#E8C547",
        "second_color": "#C8202A",
        "canvas_bg":    "#070E1C",
    },
    "savana": {
        "name": "Savana Dourada",
        "bg":           "#1C1208",
        "bg_panel":     "#2A1E0F",
        "bg_card":      "#3A2A14",
        "accent":       "#D4892A",
        "accent2":      "#E8C547",
        "accent3":      "#6B8E23",
        "fg":           "#F5DEB3",
        "fg_dim":       "#A0856A",
        "border":       "#D4892A",
        "digit_color":  "#E8C547",
        "second_color": "#D4892A",
        "canvas_bg":    "#150E05",
    },
    "kizomba": {
        "name": "Kizomba Violeta",
        "bg":           "#0D0520",
        "bg_panel":     "#1A0A3A",
        "bg_card":      "#25124A",
        "accent":       "#C8202A",
        "accent2":      "#9C27B0",
        "accent3":      "#F5A623",
        "fg":           "#E8D5F5",
        "fg_dim":       "#8E7AAA",
        "border":       "#9C27B0",
        "digit_color":  "#F5A623",
        "second_color": "#C8202A",
        "canvas_bg":    "#080315",
    },
}

# ── Configuração do padrão Samakaka ───────────────────────────────────────────
SAMAKAKA_CONFIG = {
    "show_pattern":    True,
    "pattern_opacity": 0.18,    # 0.0 – 1.0
    "pattern_scale":  40,       # tamanho da célula base em px
    "pattern_style":  "full",   # "full" | "border" | "corner" | "off"
    # cores do padrão (independentes do tema)
    "color_red":   "#C8202A",
    "color_yellow":"#F5A623",
    "color_black": "#0A0A0A",
    "color_white": "#F0E6D3",
}

# ── Fontes ────────────────────────────────────────────────────────────────────
FONTS = {
    "display":   ("Courier New", 72, "bold"),
    "display_sm":("Courier New", 48, "bold"),
    "digit_med": ("Courier New", 36, "bold"),
    "heading":   ("Helvetica",   16, "bold"),
    "label":     ("Helvetica",   11, "normal"),
    "label_sm":  ("Helvetica",    9, "normal"),
    "btn":       ("Helvetica",   10, "bold"),
    "mono":      ("Courier New", 13, "normal"),
    "mono_sm":   ("Courier New", 10, "normal"),
}

# Tema activo (alterado em runtime)
_active_palette = "samakaka_classico"

def get_palette():
    return PALETTES[_active_palette]

def set_palette(name: str):
    global _active_palette
    if name in PALETTES:
        _active_palette = name

def get_samakaka():
    return SAMAKAKA_CONFIG

def update_samakaka(key, value):
    SAMAKAKA_CONFIG[key] = value
