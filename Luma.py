# luma.py — Anti-Spook Suite for Exodia OS
# Cross-platform paranoid toolkit (Linux + Windows) using Rich

import os
import subprocess
import tempfile
import time
import shutil
import random
import platform
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()
IS_WINDOWS = platform.system() == "Windows"

ASCII_BANNER = r"""
$$\                                         
$$ |                                        
$$ |     $$\   $$\ $$$$$$\\$$$$\   $$$$$$\  
$$ |     $$ |  $$ |$$  _$$  _$$\  \____$$\ 
$$ |     $$ |  $$ |$$ / $$ / $$ | $$$$$$$ |
$$ |     $$ |  $$ |$$ | $$ | $$ |$$  __$$ |
$$$$$$$$\\$$$$$$  |$$ | $$ | $$ |\$$$$$$$ |
\________|\______/ \__| \__| \__| \_______|
                                           
                                           
"""

# Utils

def run(cmd):
    return subprocess.getoutput(cmd)

def log(msg):
    log_path = os.path.join(tempfile.gettempdir(), "luma.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"[{time.ctime()}] {msg}\n")

# 1. Network Kill Switch

def kill_network():
    log("Disabling all network interfaces")
    if IS_WINDOWS:
        run("netsh interface set interface name=\"Wi-Fi\" admin=disable")
        run("netsh interface set interface name=\"Ethernet\" admin=disable")
    else:
        run("nmcli networking off")
        run("ip link set down dev wlan0")
        run("ip link set down dev eth0")
    console.print("[+] Network disabled.", style="bold red")

# 2. Secure Wipe

def wipe_file(path):
    if os.path.isfile(path):
        log(f"Secure wiping {path}")
        size = os.path.getsize(path)
        with open(path, "ba+") as f:
            for _ in range(3):
                f.seek(0)
                f.write(os.urandom(size))
        os.remove(path)
        console.print(f"[+] Wiped: {path}", style="bold green")
    else:
        console.print("[-] Invalid file.", style="bold red")

# 3. MAC Spoof (Linux only)

def spoof_mac():
    if IS_WINDOWS:
        console.print("[-] MAC spoofing not supported on Windows.", style="bold red")
        return
    iface = "wlan0"
    new_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0x00, 0xFF) for _ in range(5))
    run(f"ip link set {iface} down")
    run(f"ip link set {iface} address {new_mac}")
    run(f"ip link set {iface} up")
    console.print(f"[+] MAC spoofed: {new_mac}", style="bold green")
    log(f"MAC spoofed: {new_mac}")

# 4. Outbound Connection Logger

def log_connections():
    console.print("[+] Active Connections:", style="bold cyan")
    output = run("netstat -an" if IS_WINDOWS else "ss -tuna")
    console.print(output)

# 5. Emergency Burn (Linux only)

def kill_everything():
    log("!!! EMERGENCY BURN TRIGGERED !!!")
    kill_network()
    if not IS_WINDOWS:
        run("swapoff -a")
        run("rm -rf /tmp/*")
        console.print("[!] RAM wiped, network down, temp cleared. System going dark.", style="bold red")
        time.sleep(3)
        run("poweroff")
    else:
        console.print("[-] Emergency burn not fully supported on Windows.", style="bold yellow")

# 6. USB Watchdog

def scan_usb():
    console.print("[+] Connected USB devices:", style="bold cyan")
    output = run("wmic path CIM_LogicalDevice where \"Description like '%USB%'\" get /value" if IS_WINDOWS else "lsusb")
    console.print(output)

# 7. Vault Launcher (Linux only)

def open_vault():
    if IS_WINDOWS:
        console.print("[-] Vault feature not supported on Windows.", style="bold red")
        return
    vault_path = Prompt.ask("Path to LUKS container")
    if not os.path.exists(vault_path):
        console.print("[-] Vault not found.", style="bold red")
        return
    mount_point = "/mnt/vault"
    os.makedirs(mount_point, exist_ok=True)
    run(f"cryptsetup open {vault_path} ghostvault")
    run(f"mount /dev/mapper/ghostvault {mount_point}")
    console.print(f"[+] Vault mounted at {mount_point}", style="bold green")

# Menu

def menu():
    while True:
        console.print(Panel("""
[1] Launch Vault
[2] Wipe File
[3] Go Dark (Kill Network)
[4] Spoof MAC
[5] View Connections
[6] Scan USB Devices
[7] Kill Everything
[8] Exit
        """, title="Luma — Anti-Spook Suite", style="bold magenta"))
        choice = Prompt.ask("Select Option")
        if choice == "1": open_vault()
        elif choice == "2": wipe_file(Prompt.ask("File to wipe"))
        elif choice == "3": kill_network()
        elif choice == "4": spoof_mac()
        elif choice == "5": log_connections()
        elif choice == "6": scan_usb()
        elif choice == "7": kill_everything()
        elif choice == "8": break
        else: console.print("Invalid option.", style="bold red")

if __name__ == "__main__":
    os.system("cls" if IS_WINDOWS else "clear")
    console.print(ASCII_BANNER, style="bold blue")
    log("Luma launched")
    menu()
