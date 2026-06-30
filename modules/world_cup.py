"""
Módulo Mundial — Jogos do Campeonato Mundial FIFA via TheSportsDB
Permite ver jogos do dia/dias seguintes e activar/desactivar alarme
automático (10 min antes do início) para cada jogo.
"""

import threading
import tkinter as tk
from datetime import date, datetime, timedelta

from modules.widgets import btn, icon_btn, card, section_label, divider
from modules import notifications
from modules.sound import play as play_sound

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

SPORTSDB_KEY      = "123"   # chave pública de teste TheSportsDB
SPORTSDB_URL      = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}/eventsday.php"
MUNDIAL_LEAGUE_ID = "4429"  # FIFA World Cup


def _fetch_games(target_date: date) -> list:
    """Consulta a TheSportsDB e devolve lista de jogos para um dia."""
    if not REQUESTS_OK:
        return []
    try:
        resp = requests.get(
            SPORTSDB_URL,
            params={"d": target_date.strftime("%Y-%m-%d"), "l": MUNDIAL_LEAGUE_ID},
            timeout=6,
        )
        resp.raise_for_status()
        events = resp.json().get("events") or []
        jogos = []
        for ev in events:
            try:
                h, m = ev["strTime"].split(":")[:2]
            except Exception:
                continue
            jogos.append({
                "id":     ev.get("idEvent"),
                "time":   f"{int(h):02d}:{int(m):02d}",
                "home":   ev.get("strHomeTeam", "?"),
                "away":   ev.get("strAwayTeam", "?"),
                "venue":  ev.get("strVenue", ""),
                "round":  ev.get("intRound", ""),
            })
        return jogos
    except Exception:
        return []


def _is_past(game: dict) -> bool:
    """Verifica se o horário de início do jogo já passou."""
    try:
        h, m = map(int, game["time"].split(":"))
        kickoff = datetime.combine(game["date"], datetime.min.time()).replace(hour=h, minute=m)
        return datetime.now() >= kickoff
    except Exception:
        return False


class WorldCupEngine(threading.Thread):
    """Thread background: verifica jogos com alarme activo e dispara aviso."""

    def __init__(self, get_games, on_trigger, minutes_before=10):
        super().__init__(daemon=True)
        self._get_games = get_games          # callback -> dict {id: game}
        self._cb         = on_trigger        # callback(game)
        self._before      = minutes_before
        self._alive       = True
        self._fired       = set()

    def run(self):
        while self._alive:
            now = datetime.now()
            for gid, g in self._get_games().items():
                if not g.get("alarm_on"):
                    continue
                if gid in self._fired:
                    continue
                try:
                    h, m = map(int, g["time"].split(":"))
                except ValueError:
                    continue
                kickoff = datetime.combine(g["date"], datetime.min.time()).replace(hour=h, minute=m)
                aviso   = kickoff - timedelta(minutes=self._before)
                if now >= aviso and now < kickoff:
                    self._fired.add(gid)
                    self._cb(g)
            import time as _t
            _t.sleep(15)

    def stop(self):
        self._alive = False


class WorldCupTab(tk.Frame):
    """Aba 'Mundial — Jogos' com lista de jogos e toggle de alarme por jogo."""

    def __init__(self, parent, palette, config, on_save, root_ref):
        super().__init__(parent, bg=palette["bg"])
        self.p        = palette
        self.config   = config
        self.on_save  = on_save
        self.root     = root_ref

        # games: dict id -> {id,time,home,away,venue,round,date,alarm_on}
        self.config.setdefault("world_cup_games", {})
        self._games = self.config["world_cup_games"]
        self._offset = 0   # 0 = hoje, 1 = amanhã, etc.

        self._engine = WorldCupEngine(lambda: self._games, self._on_alarm_fire)
        self._engine.start()

        self._build()
        self._render_list()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build(self):
        p = self.p

        hdr = tk.Frame(self, bg=p["bg"])
        hdr.pack(fill=tk.X, padx=20, pady=(16, 10))
        tk.Label(hdr, text="Mundial — Jogos", bg=p["bg"], fg=p["fg"],
                 font=("Segoe UI", 15, "bold")).pack(side=tk.LEFT)

        if not REQUESTS_OK:
            tk.Label(self, text="Biblioteca 'requests' não encontrada — função desactivada.",
                     bg=p["bg"], fg=p["accent"],
                     font=("Segoe UI", 9)).pack(padx=20, pady=10, anchor="w")
            return

        # Selector de dia (pills)
        day_row = tk.Frame(self, bg=p["bg"])
        day_row.pack(fill=tk.X, padx=20, pady=(0, 10))
        self._day_btns = []
        labels = ["Hoje", "+1 dia", "+2 dias", "+3 dias"]
        for i, lbl in enumerate(labels):
            b = tk.Label(day_row, text=lbl,
                        bg=p["accent"] if i == 0 else p["bg_input"],
                        fg="#FFFFFF" if i == 0 else p["fg_dim"],
                        font=("Segoe UI", 9, "bold"),
                        padx=14, pady=6, cursor="hand2")
            b.pack(side=tk.LEFT, padx=3)
            b.bind("<Button-1>", lambda e, i=i: self._select_day(i))
            self._day_btns.append(b)

        icon_btn(day_row, "↻  Actualizar", self._fetch_current, p).pack(side=tk.RIGHT)

        self._status_lbl = tk.Label(self, text="", bg=p["bg"], fg=p["fg_muted"],
                                    font=("Segoe UI", 8))
        self._status_lbl.pack(padx=20, anchor="w")

        divider(self, p).pack(fill=tk.X, padx=20, pady=(8, 10))

        # Lista de jogos (scroll)
        outer = tk.Frame(self, bg=p["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=20)
        self._canvas = tk.Canvas(outer, bg=p["bg"], highlightthickness=0)
        sb = tk.Scrollbar(outer, orient=tk.VERTICAL, command=self._canvas.yview,
                          width=6, troughcolor=p["bg"], bg=p["border"])
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self._lf = tk.Frame(self._canvas, bg=p["bg"])
        cw = self._canvas.create_window((0, 0), window=self._lf, anchor="nw")
        self._lf.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(cw, width=e.width))

        # Busca inicial em background
        self._fetch_current()

    def _select_day(self, idx):
        p = self.p
        self._offset = idx
        for i, b in enumerate(self._day_btns):
            b.config(bg=p["accent"] if i == idx else p["bg_input"],
                     fg="#FFFFFF" if i == idx else p["fg_dim"])
        self._fetch_current()

    # ── Busca de dados ───────────────────────────────────────────────────────
    def _fetch_current(self):
        if not REQUESTS_OK:
            return
        target = date.today() + timedelta(days=self._offset)
        self._status_lbl.config(text="A carregar jogos...")

        def _run():
            jogos = _fetch_games(target)
            self.root.after(0, lambda: self._on_fetched(jogos, target))

        threading.Thread(target=_run, daemon=True).start()

    def _on_fetched(self, jogos, target_date):
        if not jogos:
            self._status_lbl.config(
                text=f"Sem jogos encontrados para {target_date.strftime('%d/%m/%Y')}."
            )
        else:
            self._status_lbl.config(
                text=f"{len(jogos)} jogo(s) em {target_date.strftime('%d/%m/%Y')}."
            )
        # Mescla com jogos já guardados (preserva estado do alarme)
        for j in jogos:
            gid = j["id"]
            if gid in self._games:
                self._games[gid].update(j, date=target_date)
            else:
                self._games[gid] = dict(j, date=target_date, alarm_on=False)
        self.on_save()
        self._render_list(filter_date=target_date)

    # ── Renderização ──────────────────────────────────────────────────────────
    def _render_list(self, filter_date=None):
        for w in self._lf.winfo_children():
            w.destroy()
        p = self.p

        filter_date = filter_date or (date.today() + timedelta(days=self._offset))
        shown = [g for g in self._games.values() if g.get("date") == filter_date]
        shown.sort(key=lambda g: g["time"])

        if not shown:
            tk.Label(self._lf, text="Nenhum jogo para este dia.",
                     bg=p["bg"], fg=p["fg_muted"],
                     font=("Segoe UI", 10)).pack(pady=40)
            return

        for g in shown:
            if _is_past(g) and g.get("alarm_on"):
                g["alarm_on"] = False
                self.on_save()
            self._game_card(g).pack(fill=tk.X, pady=4)

    def _game_card(self, g):
        p = self.p
        c = card(self._lf, p)

        on   = g.get("alarm_on", False)
        past = _is_past(g)

        tk.Frame(c, bg=p["accent"] if on else p["border"], width=3).place(
            relx=0, rely=0, relheight=1
        )

        body = tk.Frame(c, bg=p["bg_card"])
        body.pack(fill=tk.X, padx=(14, 12), pady=10)

        row1 = tk.Frame(body, bg=p["bg_card"])
        row1.pack(fill=tk.X)

        time_fg = p["fg_muted"] if past else p["fg"]
        tk.Label(row1, text=g["time"], bg=p["bg_card"], fg=time_fg,
                 font=("Consolas", 16, "bold")).pack(side=tk.LEFT)

        teams = f"{g['home']}  vs  {g['away']}"
        tk.Label(row1, text=teams, bg=p["bg_card"], fg=time_fg,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=12)

        # Toggle alarme
        right = tk.Frame(row1, bg=p["bg_card"])
        right.pack(side=tk.RIGHT)

        if past:
            # Jogo já começou/terminou — alarme bloqueado
            state_lbl = tk.Label(
                right,
                text="⛔ Jogo já decorreu",
                bg=p["bg_input"], fg=p["fg_muted"],
                font=("Segoe UI", 8, "bold"),
                padx=10, pady=5,
            )
            state_lbl.pack()
            # sem bind — não clicável
        else:
            state_lbl = tk.Label(
                right,
                text="🔔 Alarme ON" if on else "🔕 Alarme OFF",
                bg=p["accent"] if on else p["bg_input"],
                fg="#FFFFFF" if on else p["fg_dim"],
                font=("Segoe UI", 8, "bold"),
                padx=10, pady=5, cursor="hand2",
            )
            state_lbl.pack()

            def _toggle(e=None, g=g, lbl=state_lbl):
                g["alarm_on"] = not g.get("alarm_on", False)
                self.on_save()
                on2 = g["alarm_on"]
                lbl.config(text="🔔 Alarme ON" if on2 else "🔕 Alarme OFF",
                           bg=p["accent"] if on2 else p["bg_input"],
                           fg="#FFFFFF" if on2 else p["fg_dim"])
                c.winfo_children()[0].config(bg=p["accent"] if on2 else p["border"])

            state_lbl.bind("<Button-1>", _toggle)

        # Detalhes (local/ronda)
        venue = g.get("venue", "")
        rnd   = g.get("round", "")
        if venue or rnd:
            details = "  ·  ".join(filter(None, [venue, f"Ronda {rnd}" if rnd else ""]))
            tk.Label(body, text=details, bg=p["bg_card"], fg=p["fg_muted"],
                     font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

        footer_txt = "Jogo já decorreu — alarme indisponível" if past \
            else "Alarme dispara 10 min antes do início"
        tk.Label(body, text=footer_txt,
                 bg=p["bg_card"], fg=p["fg_muted"],
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))

        return c

    # ── Disparo de alarme ────────────────────────────────────────────────────
    def _on_alarm_fire(self, game):
        self.root.after(0, lambda: self._popup(game))

    def _popup(self, game):
        p = self.p
        label = f"{game['home']} x {game['away']}"
        notifications.notify_alarm(f"⚽ {label} em 10 min")
        play_sound("alarme_urgente", repeat=1)

        pop = tk.Toplevel(self)
        pop.title("Jogo do Mundial!")
        pop.configure(bg=p["bg"])
        pop.geometry("320x220")
        pop.attributes("-topmost", True)
        pop.resizable(False, False)

        tk.Label(pop, text="⚽", bg=p["bg"], fg=p["accent"],
                 font=("Segoe UI", 32)).pack(pady=(20, 4))
        tk.Label(pop, text=label, bg=p["bg"], fg=p["fg"],
                 font=("Segoe UI", 12, "bold")).pack()
        tk.Label(pop, text=f"Início às {game['time']}", bg=p["bg"], fg=p["fg_dim"],
                 font=("Segoe UI", 10)).pack(pady=(2, 16))

        btn(pop, "OK", pop.destroy, p, "primary", small=True).pack()

    def refresh_theme(self, palette):
        self.p = palette
        self.configure(bg=palette["bg"])
        self._render_list()

    def destroy(self):
        self._engine.stop()
        super().destroy()