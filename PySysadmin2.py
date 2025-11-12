#!/usr/bin/env python3
'''
#####################################################################################
 Title 		PySysadmin.py
 Written by	Jean Paul BERES

 v1.0			2025-10-12
                Transcription of Bash script in Python
				Prerequisits: expac ; yay ; ranger ; dysk

 v1.1			2025-10-14
				Only using pure python code, no usage of AWK or grep²

 v2.0           2025-10-14
                Optimized for performance, readability, and maintainability
                Uses pure Python, minimizes shell calls, and improves error handling

 v2.1           2025-10-19
                All Messages and ErrorMsgs Defined as constants
                Optimizing Code

 v3.0           2025-11-11
                Full System Audit through Lynis Auditing Tool with Report creation
                Prerequisits: Chaotic-Aur ; expac ; yay ; ranger ; dysk ; lynis
                New Layout
                Using Python lists iso separate variables (Menuoptions, ErrMSg, Msg)

#####################################################################################
'''
import os
import platform
import subprocess
import shutil
import re
from pathlib import Path
from typing import Tuple, Optional

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    WHITE = "\033[37m"
    MAGENTA = "\033[35m"
    YELLOW = "\033[33m"

class Gr:
    L_TOP = "┌"
    R_TOP = "┐"
    L_BOTTOM = "└"
    R_BOTTOM = "┘"
    H_LINE = "─"
    V_LINE = "│"

# --- Constants ---
N_LINE = "\n"
LINE_WIDTH = 70
BOX_WIDTH = 32
FIRST_HBOX_LINE = 28
FIRST_V_POS = 70
TEXT_POS = FIRST_V_POS + 3
NBRLINES = 8
PROMPTLINE = FIRST_HBOX_LINE + 28

Msg = [
"*** PRESS Enter to continue ***" ,
"*** Checkupdates ***" ,
"*** Install Updates ***" ,
"*** Last Installed/Updated Packages ***" ,
"*** Remove Cache ***" ,
"*** Full System Audit Running [Please Wait...] ***" ,
"### Full System Audit Report Available in ~/Audit directory ###"
]

ErrMsg = [
"No Error" ,
"*** No Updates or Error: " ,
"*** Update process failed with exit code "
]

MenuOptions = [
"(A)uditFullSystem" ,
"(C)heckUpdates" ,
"(D)ir" ,
"(F)reemem" ,
"(I)nstallHistory" ,
"(R)emoveAllCache" ,
"(U)pdate" ,
"(Q)uit"
]

class SystemInfo:
    @staticmethod
    def run_cmd(cmd: str):
        try:
            return subprocess.check_output(cmd, shell=True, text=True).strip()
        except subprocess.CalledProcessError:
            return "unknown"

    @staticmethod
    def get_os():
        os_release = Path("/etc/os-release")
        if os_release.exists():
            with open(os_release) as f:
                for line in f:
                    if line.startswith("NAME="):
                        return line.split("=")[1].strip().strip('"')
        return "unknown"

    @staticmethod
    def get_shell():
        try:
            version = SystemInfo.run_cmd("bash --version").split()[3].split('(')[0]
            return f"bash {version}"
        except IndexError:
            return "unknown"

    @staticmethod
    def get_de():
        de = SystemInfo.run_cmd("plasmashell --version 2> /dev/null")
        if de:
            return f"KDE {de.split()[0]} {de.split()[1]}"
        return "unknown"

    @staticmethod
    def get_kde_theme() -> Tuple[str, str, str, str]:
        if shutil.which("kreadconfig5"):
            icons = SystemInfo.run_cmd("kreadconfig5 --file kdeglobals --group Icons --key Theme 2>/dev/null || echo unknown")
            cursor = SystemInfo.run_cmd("kreadconfig5 --file kcminputrc --group Mouse --key cursorTheme 2>/dev/null || echo unknown")
            color = SystemInfo.run_cmd("kreadconfig5 --file kdeglobals --group General --key ColorScheme 2>/dev/null || echo unknown")
            qt_style = SystemInfo.run_cmd("kreadconfig5 --file kdeglobals --group KDE --key widgetStyle 2>/dev/null || echo unknown")
            return icons, cursor, color, qt_style
        return "unknown", "unknown", "unknown", "unknown"

    @staticmethod
    def get_fonts():
        try:
            font = SystemInfo.run_cmd("fc-match -v")
            match = re.search(r'fullname:\s*"([^"]+)"', font)
            if match:
                return match.group(1).split('(')[0].strip()
        except Exception:
            pass
        return "unknown"

    @staticmethod
    def get_gpu() -> Tuple[str, str]:
        gpu = gpu2 = ""
        try:
            lspci = SystemInfo.run_cmd("lspci")
            for line in lspci.splitlines():
                if any(x in line.lower() for x in ["vga", "3d", "display"]):
                    gpu = line.split(': ')[-1]
                    break
            glxinfo = SystemInfo.run_cmd("glxinfo")
            for line in glxinfo.splitlines():
                if "OpenGL renderer" in line:
                    gpu2 = line.split(': ')[1]
                    break
        except Exception:
            pass
        return gpu, gpu2

    @staticmethod
    def get_mem() -> Tuple[str, str]:
        try:
            free_h = SystemInfo.run_cmd("free -h").splitlines()[1].split()
            free_m = SystemInfo.run_cmd("free -m").splitlines()[1].split()
            total = free_h[1]
            used = int(free_m[1]) - int(free_m[3]) - int(free_m[5])
            return f"{used}M", total
        except (IndexError, ValueError):
            return "unknown", "unknown"

    @staticmethod
    def get_root_disk():
        try:
            df = SystemInfo.run_cmd("df -h /").splitlines()[1].split()
            return f"{df[2]}/{df[1]} ({df[4]})"
        except IndexError:
            return "unknown"

    @staticmethod
    def get_packages():
        try:
            pkg_count = len(SystemInfo.run_cmd("pacman -Qq").splitlines())
            return f"{pkg_count} (pacman)"
        except Exception:
            return "unknown"

    @staticmethod
    def get_cpu():
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(': ')[1].strip()
        except IOError:
            pass
        return "unknown"

class UI:
    @staticmethod
    def fmt_out(key: str, val: str):
        print(f"{Colors.BOLD}{Colors.CYAN}{key :<20}{Colors.RESET}{Colors.GREEN}: {Colors.WHITE}{val}")

    @staticmethod
    def sep_line():
        print(f"{Colors.MAGENTA}{Gr.H_LINE * LINE_WIDTH}{Colors.RESET}")

    @staticmethod
    def draw_box():
        print(f"\033[{FIRST_HBOX_LINE};{FIRST_V_POS}H{Colors.BOLD}{Colors.GREEN}{Gr.L_TOP}{Gr.H_LINE * BOX_WIDTH}{Gr.R_TOP}")
        for i in range(NBRLINES):
            print(f"\033[{FIRST_HBOX_LINE + 1 + i};{FIRST_V_POS}H{Gr.V_LINE}")
            print(f"\033[{FIRST_HBOX_LINE + 1 + i};{FIRST_V_POS + BOX_WIDTH + 1}H{Gr.V_LINE}")
        print(f"\033[{FIRST_HBOX_LINE + NBRLINES + 1};{FIRST_V_POS}H{Gr.L_BOTTOM}{Gr.H_LINE * BOX_WIDTH}{Gr.R_BOTTOM}")

    @staticmethod
    def display_info():
        TEXTLINE= FIRST_HBOX_LINE + 1
        for Item in MenuOptions:
            print(f"\033[{TEXTLINE};{TEXT_POS}H{Colors.BOLD}{Colors.YELLOW}{Item}")
            TEXTLINE = TEXTLINE + 1

    @staticmethod
    def press_enter():
        print(f"{Colors.BOLD}{Colors.GREEN}{Msg[0]}")
        input()

    @staticmethod
    def clear_screen():
        os.system("clear")

class Actions:
    @staticmethod
    def freemem():
        UI.clear_screen()
        print(f"{Colors.YELLOW}{Colors.BOLD}")
        subprocess.run("sudo free -h", shell=True, check=True)
        # Clear caches
        subprocess.run("sudo sysctl -w vm.drop_caches=3", shell=True, check=True)
        subprocess.run(["sync"])
        subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"])
        # Display memory status after clearing caches
        print(f"{Colors.RESET}{Colors.BOLD}")
        subprocess.run("sudo free -h", shell=True, check=True)
        UI.press_enter()

    @staticmethod
    def open_ranger():
        UI.clear_screen()
        subprocess.run("ranger", check=True)

    @staticmethod
    def check_updates():
        UI.clear_screen()
        print(f"{Colors.BOLD}{Colors.YELLOW}{Msg[1]}{Colors.RESET}")
        try:
            subprocess.run(["checkupdates"], check=True)
        except subprocess.CalledProcessError as e:
            # Exit code 2 just means there are updates (or no updates or an error)
            if e.returncode != 2:
                print(f"{Colors.BOLD}{Colors.MAGENTA}{ErrMsg[1]}{e}{Colors.RESET}")
        UI.press_enter()

    @staticmethod
    def install_updates():
        UI.clear_screen()
        print(f"{Colors.BOLD}{Colors.YELLOW}{Msg[2]}{Colors.RESET}")
        try:
            subprocess.run("sudo pacman -Syyu", shell=True, check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"{Colors.BOLD}{Colors.MAGENTA}{ErrMsg[2]}{e.returncode}{Colors.RESET}")
        UI.press_enter()

    @staticmethod
    def list_inst_updates():
        UI.clear_screen()
        print(f"{Colors.BOLD}{Colors.YELLOW}{Msg[3]}{Colors.RESET}")
        subprocess.run("expac --timefmt='%Y-%m-%d %T' '%l\t%n' | sort | tail -n 50", shell=True, check=True, text=True)
        UI.press_enter()

    @staticmethod
    def remove_all_cache():
        UI.clear_screen()
        print(f"{Colors.BOLD}{Colors.YELLOW}{Msg[4]}{Colors.RESET}")
        subprocess.run("rm -Rvf ~/.cache/", shell=True, check=True)
        os.makedirs(os.path.expanduser("~/.cache"), exist_ok=True)
        subprocess.run("rm -Rvf ~/.local/share/recently-used.xbel*", shell=True, check=True)
        UI.press_enter()

    @staticmethod
    def full_sys_audit():
        UI.clear_screen()
        print(f"{Colors.BOLD}{Colors.YELLOW}{Msg[5]}{Colors.RESET}")
        subprocess.run("sudo lynis audit system --forensics --pentest --verbose --no-log > ~/Audit/FullSysAudit.txt", shell=True, check=True, text=True)
        print(f"{N_LINE}{Colors.BOLD}{Colors.WHITE}{Msg[6]}{Colors.RESET}{N_LINE}")
        UI.press_enter()

def my_fetch():
    # Get the info out of SystemInfo Class
    UI.sep_line()
    UI.fmt_out("OS", f"{SystemInfo.get_os()} {platform.machine()}")
    UI.fmt_out("Kernel", SystemInfo.run_cmd("uname -sr"))
    UI.fmt_out("Shell", SystemInfo.get_shell())
    UI.fmt_out("Root Disk", SystemInfo.get_root_disk())
    UI.fmt_out("Packages", SystemInfo.get_packages())
    UI.sep_line()
    UI.fmt_out("DE", f"{SystemInfo.get_de()} - {os.getenv('XDG_SESSION_TYPE', 'unknown')}")
    icons, cursor, color, qt_style = SystemInfo.get_kde_theme()
    UI.fmt_out("Qt Style", qt_style)
    UI.fmt_out("Icons", icons)
    UI.fmt_out("Color Scheme", color)
    UI.fmt_out("Font", SystemInfo.get_fonts())
    UI.fmt_out("Plasma Cursor", cursor)
    UI.sep_line()
    UI.fmt_out("CPU", f"{SystemInfo.get_cpu()} ({os.cpu_count()} cores)")
    gpu, gpu2 = SystemInfo.get_gpu()
    UI.fmt_out("GPU", gpu)
    UI.fmt_out("Second GPU", gpu2)
    used, total = SystemInfo.get_mem()
    UI.fmt_out("Mem.(Used/Total)", f"{used}/{total}")
    UI.sep_line()

def selection():
    print(f"\033[{PROMPTLINE}H{Colors.RESET}")
    choice = input()
    match choice:
        case "r" | "R":
            Actions.remove_all_cache()
        case "f" | "F":
            Actions.freemem()
        case "d" | "D":
            Actions.open_ranger()
        case "c" | "C":
            Actions.check_updates()
        case "u" | "U":
            Actions.install_updates()
        case "i" | "I":
            Actions.list_inst_updates()
        case "a" | "A":
            Actions.full_sys_audit()
        case _ : exit(1)

def main():
    while True:
        # Display SystemInfo
        UI.clear_screen()
        my_fetch()

        # Display Install Info and Disk Info
        subprocess.run(["yay", "-P", "--stats"], check=True)
        subprocess.run(["dysk", "-c", "label+default", "--filter", "disk <> HDD", "--sort", "filesystem", "-u", "binary"], check=True)
        subprocess.run(["dysk", "-c", "label+default", "--filter", "disk <> SSD", "--sort", "filesystem", "-u", "binary"], check=True)

        # Display Box with Menu Options
        UI.draw_box()
        UI.display_info()

        # Select actions
        selection()

main()
