#!/usr/bin/env bash
# Lançador do Relógio Zongola
# Coloca este ficheiro na mesma pasta que main.py e executa:
#   chmod +x zongola.sh && ./zongola.sh

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verificar Python 3.9+
if ! command -v python3 &>/dev/null; then
    echo "ERRO: Python 3 não encontrado. Instala com: sudo apt install python3"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PY_VER" -lt 9 ]; then
    echo "AVISO: Python 3.9+ recomendado para suporte total a zoneinfo."
fi

# Verificar tkinter
python3 -c "import tkinter" 2>/dev/null || {
    echo "ERRO: tkinter não instalado."
    echo "Instala com: sudo apt install python3-tk"
    exit 1
}

# Verificar aplay (som)
if ! command -v aplay &>/dev/null && ! command -v paplay &>/dev/null; then
    echo "AVISO: aplay/paplay não encontrados. Sons de alarme podem não funcionar."
    echo "Instala com: sudo apt install alsa-utils   OU   pulseaudio-utils"
fi

cd "$DIR"
exec python3 main.py "$@"
