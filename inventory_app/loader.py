import shutil
import sys
import time

CYAN = "\033[38;2;79;212;232m"
PURPLE = "\033[38;2;185;140;255m"
GREEN = "\033[38;2;94;233;160m"
DIM = "\033[38;2;154;168;194m"
BOLD = "\033[1m"
RESET = "\033[0m"
HIDE = "\033[?25l"
SHOW = "\033[?25h"
CLEAR = "\033[2J\033[H"


def _width():
    return max(48, min(shutil.get_terminal_size((80, 24)).columns, 88))


def _bar(percent, width=36):
    filled = int(width * max(0, min(100, percent)) / 100)
    return f"{GREEN}{'█' * filled}{DIM}{'░' * (width - filled)}{RESET}"


def start():
    sys.stdout.write(HIDE + CLEAR)
    sys.stdout.flush()
    w = _width()
    line = "═" * (w - 8)
    print(f"{CYAN}{BOLD}")
    print(f"  ╔{line}╗")
    print(f"  ║{'ONESHOT INVENTORY':^{w - 8}}║")
    print(f"  ║{'high-end vision boot':^{w - 8}}║")
    print(f"  ╚{line}╝")
    print(RESET)
    print(f"  {DIM}Petronas neon core  ·  YOLOv8  ·  live capture{RESET}\n")


def set_progress(percent, stage):
    sys.stdout.write("\r\033[K")
    sys.stdout.write(
        f"  {_bar(percent)}  {CYAN}{int(percent):3d}%{RESET}  {stage:<40}"
    )
    sys.stdout.flush()


def finish(dashboard_url):
    set_progress(100, "systems online")
    print("\n")
    print(f"  {GREEN}●{RESET}  model locked")
    print(f"  {GREEN}●{RESET}  camera live")
    print(f"  {GREEN}●{RESET}  capture pipeline on backend")
    print()
    print(f"  {PURPLE}{BOLD}Dashboard{RESET}  {CYAN}{dashboard_url}{RESET}")
    print(f"  {DIM}Live feed never freezes. Detections stay server-side.{RESET}")
    print()
    sys.stdout.write(SHOW)
    sys.stdout.flush()


def fail(message):
    print(f"\n  {RESET}boot warning: {message}")
    sys.stdout.write(SHOW)
    sys.stdout.flush()


def pulse(seconds=0.18):
    time.sleep(seconds)
