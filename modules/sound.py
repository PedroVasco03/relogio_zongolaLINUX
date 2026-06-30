"""
Motor de Som — gera tons de alarme sem dependências externas.
Compatível com Windows, Linux e macOS.
"""

import os
import wave
import struct
import math
import tempfile
import threading
import subprocess
import sys
import time

# Se for Windows, importamos o winsound de forma segura
if sys.platform == "win32":
    import winsound
else:
    winsound = None


def _generate_wav(path: str, freq: float = 880.0, duration: float = 0.4,
                 volume: float = 0.8, sample_rate: int = 44100):
    """Gera ficheiro WAV com tom sinusoidal."""
    n_samples = int(sample_rate * duration)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)   # 16-bit
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            # envelope ADSR simples
            t = i / sample_rate
            env = min(t / 0.01, 1.0) * max(1.0 - (t - duration + 0.05) / 0.05, 0.0)
            val = int(32767 * volume * env * math.sin(2 * math.pi * freq * t))
            frames += struct.pack("<h", max(-32768, min(32767, val)))
        wf.writeframes(bytes(frames))


def _play_wav(path: str):
    """Toca WAV detetando o Sistema Operacional atual."""
    # 1. Suporte nativo para WINDOWS
    if sys.platform == "win32" and winsound:
        try:
            # SND_FILENAME toca o arquivo, SND_NODEFAULT evita som de erro se falhar
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
            return
        except Exception:
            pass

    # 2. Suporte nativo para macOS
    elif sys.platform == "darwin":
        try:
            subprocess.run(["afplay", path], timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass

    # 3. Fallback para LINUX (Seu código original adaptado)
    else:
        for player in ["aplay", "paplay", "ffplay"]:
            try:
                result = subprocess.run(
                    [player, "-q", path] if player != "ffplay" else
                    [player, "-nodisp", "-autoexit", "-loglevel", "quiet", path],
                    timeout=5,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    return
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue


# Tons pré-definidos (frequência Hz, duração s)
SOUNDS = {
    "alarme_classico": [(880, 0.4), (0, 0.1), (880, 0.4), (0, 0.1), (880, 0.4)],
    "alarme_urgente":  [(1046, 0.15)] * 8,
    "alarme_suave":    [(523, 0.6), (0, 0.2), (659, 0.6)],
    "temporizador":    [(880, 0.3), (0, 0.1), (1100, 0.3), (0, 0.1), (1320, 0.5)],
    "notificacao":     [(880, 0.2), (0, 0.05), (1100, 0.2)],
}


def _play_sequence(sequence: list):
    """Toca sequência de (freq, dur) salvando na pasta local para testes."""
    for freq, dur in sequence:
        if freq == 0:
            time.sleep(dur)
            continue
        
        # Salvando diretamente na pasta atual do script para evitar travas do Windows Temp
        path = f"temp_tone_{freq}.wav"
        
        _generate_wav(path, freq=freq, duration=dur)
        _play_wav(path)
        
        try:
            os.unlink(path)
        except Exception:
            pass


def play(sound_name: str = "alarme_classico", repeat: int = 1):
    """Toca som em thread separada para não bloquear UI."""
    seq = SOUNDS.get(sound_name, SOUNDS["alarme_classico"])

    def _run():
        for _ in range(repeat):
            _play_sequence(seq)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t


def stop_all():
    """Mata todos os players de áudio ativos de forma multiplataforma."""
    if sys.platform == "win32":
        # No Windows, se o winsound estiver rodando de forma assíncrona, isso para ele:
        if winsound:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
    else:
        # No Linux e macOS, encerra os subprocessos comuns
        for player in ["aplay", "paplay", "afplay", "ffplay"]:
            try:
                subprocess.run(["pkill", "-f", player],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            except Exception:
                pass