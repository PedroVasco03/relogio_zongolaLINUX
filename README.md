# Relógio Zongola — Desktop Linux

> Aplicação de gestão de tempo com identidade africana (padrão Samakaka)
> para o Sistema Operativo Zongola.
> Universidade Metodista de Angola — Projecto Académico

---

## Requisitos

| Requisito | Versão mínima | Instalar |
|-----------|---------------|---------|
| Python    | 3.9+          | `sudo apt install python3` |
| tkinter   | stdlib        | `sudo apt install python3-tk` |
| aplay     | qualquer      | `sudo apt install alsa-utils` |
| notify-send | qualquer    | `sudo apt install libnotify-bin` |

> **zoneinfo** (suporte de fusos horários) está incluído no Python 3.9+.
> Em Python 3.8, instala: `pip install backports.zoneinfo`

---

## Instalação rápida

```bash
# 1. Clonar / extrair o projecto
unzip relogio_zongola.zip   # ou copiar a pasta

# 2. Entrar na pasta
cd relogio_zongola

# 3. Dar permissão ao lançador
chmod +x zongola.sh

# 4. Executar
./zongola.sh
```

---

## Estrutura do Projecto

```
relogio_zongola/
├── main.py                  ← Janela principal / ponto de entrada
├── zongola.sh               ← Lançador shell
├── relogio-zongola.desktop  ← Integração com menu do desktop
├── modules/
│   ├── theme.py             ← Paletas e configuração Samakaka
│   ├── samakaka.py          ← Motor de desenho do padrão Samakaka
│   ├── analog.py            ← Relógio analógico (Canvas)
│   ├── alarms.py            ← Alarmes (RF02, RF03, RF10)
│   ├── stopwatch.py         ← Cronómetro (RF04, RF05)
│   ├── timers.py            ← Temporizadores (RF06)
│   ├── world_clock.py       ← Relógio mundial (RF07)
│   ├── sound.py             ← Motor de som (aplay/paplay)
│   ├── notifications.py     ← Notificações D-Bus (RF08)
│   ├── settings.py          ← Painel de definições
│   └── persistence.py       ← XDG Base Directory (RF10)
└── README.md
```

---

## Funcionalidades Implementadas

### ✅ Relógio Principal (RF01)
- Display **digital** com formato 12h/24h configurável
- Relógio **analógico** com ponteiros hora/minuto/segundo
- Sincronização com o relógio do sistema operativo

### ✅ Alarmes (RF02, RF03, RF10)
- Criar, editar, activar/desactivar e apagar alarmes
- Configuração de hora, etiqueta e dias da semana (recorrência)
- Função **snooze** configurável (5, 10, 15 ou 20 minutos)
- **Som de alarme** gerado via síntese WAV + aplay
- Notificação nativa via **D-Bus** (notify-send)
- Persistência automática em `~/.config/relogio-zongola/alarms.json`

### ✅ Cronómetro (RF04, RF05)
- Iniciar, pausar, retomar, reiniciar
- Precisão de **milissegundos**
- Registo de **voltas** (laps)
- Exportação para **CSV** em `~/.local/share/relogio-zongola/`

### ✅ Temporizadores (RF06)
- Múltiplos temporizadores independentes
- Perfis pré-definidos: Pomodoro, Pausa curta, Pausa longa
- Guardar perfis personalizados
- **Som e popup** ao terminar
- Barra de progresso visual

### ✅ Relógio Mundial (RF07)
- Adicionar/remover cidades
- Pesquisa de cidade
- Usa **tzdata** do sistema via zoneinfo
- Cidades populares pré-definidas (Luanda, Lisboa, Nairobi, etc.)

### ✅ Padrão Samakaka (identidade africana)
- 4 estilos: Completo, Borda, Cantos, Desligado
- Opacidade e tamanho da célula configuráveis
- 4 paletas de cor: Samakaka Clássico, Noite Azul, Savana Dourada, Kizomba

### ✅ Persistência XDG (RF10, RNF08)
- Configurações: `~/.config/relogio-zongola/config.json`
- Alarmes: `~/.config/relogio-zongola/alarms.json`
- Perfis: `~/.config/relogio-zongola/timers.json`
- Laps CSV: `~/.local/share/relogio-zongola/`

### ✅ Notificações D-Bus (RF08)
- notify-send integrado para alarmes, temporizadores e snooze

---

## Personalizar o Padrão Samakaka

Abre **⚙ Definições** na janela principal e:

1. Escolhe o **tema de cores** (Samakaka Clássico, Noite Azul, Savana, Kizomba)
2. Activa/desactiva o padrão
3. Escolhe o **estilo**: Completo / Borda / Cantos / Desligado
4. Ajusta a **opacidade** (slider 0→1)
5. Ajusta o **tamanho da célula** (16→80 px)
6. Clica **Aplicar e Fechar**

---

## Integrantes do Grupo

| Nome | Nº |
|------|----|
| Ademar Filipe | 55480 |
| Domingos Adriano | 56102 |
| José Longana | 49236 |
| José Julante | 33851 |
| Jonhy Nfilo | 56898 |
| Messias Rosário | 53690 |
| Oliveira Maquinba | 54576 |
| Pedro Vasco | 55404 |
| Tomás Gonçalves | 53577 |

---

## Referências Técnicas

- KERRISK, Michael. *The Linux Programming Interface*. No Starch Press, 2010.
- FREEDESKTOP.ORG. *XDG Base Directory Specification*.
- FREEDESKTOP.ORG. *Desktop Notifications Specification* (D-Bus).
- PYTHON SOFTWARE FOUNDATION. *datetime, wave, struct, zoneinfo* — stdlib docs.
