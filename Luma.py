# luma.py — Anti-Spook Suite for Exodia OS
# Cross-platform paranoid toolkit (Linux + Windows) using Rich

import os
import subprocess
import tempfile
import time
import shutil
import random
import platform
import requests
import json
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
Made By PDX
"""

# Globals
WEBHOOK_URL = None

# Utils

def run(cmd):
    return subprocess.getoutput(cmd)

def log(msg):
    log_path = os.path.join(tempfile.gettempdir(), "luma.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"[{time.ctime()}] {msg}\n")
    send_discord_message(f"**Luma Log:** {msg}")

def send_discord_message(content, embeds=None):
    global WEBHOOK_URL
    if not WEBHOOK_URL:
        return
    headers = {"Content-Type": "application/json"}
    data = {"content": content}
    if embeds:
        data["embeds"] = embeds
    try:
        requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(data))
    except Exception as e:
        console.print(f"[-] Failed to send webhook message: {e}", style="bold red")

def confirm_action(msg):
    return Prompt.ask(f"[bold red]{msg} (yes/no)")[0].lower() == "y"

# 1. Network Kill Switch

def kill_network():
    if not confirm_action("Kill network now? This will disable all interfaces."):
        console.print("[*] Network kill aborted.", style="bold yellow")
        return
    log("Disabling all network interfaces")
    if IS_WINDOWS:
        # Disable all interfaces found via netsh
        interfaces = run('netsh interface show interface | findstr "Enabled"').splitlines()
        for line in interfaces:
            parts = line.strip().split()
            if len(parts) >= 4:
                name = " ".join(parts[3:])
                run(f'netsh interface set interface name="{name}" admin=disable')
        console.print("[+] Network disabled.", style="bold red")
        log("Network disabled on Windows")
    else:
        # Disable all interfaces except lo
        interfaces = run("ip -o link show | awk -F': ' '{print $2}'").splitlines()
        for iface in interfaces:
            if iface == "lo":
                continue
            run(f"ip link set {iface} down")
        console.print("[+] Network disabled.", style="bold red")
        log("Network disabled on Linux")

# 2. Secure Wipe

def wipe_file(path):
    if not os.path.isfile(path):
        console.print("[-] Invalid file.", style="bold red")
        return
    if not confirm_action(f"Securely wipe {path}? This is irreversible!"):
        console.print("[*] Wipe aborted.", style="bold yellow")
        return
    log(f"Secure wiping {path}")
    size = os.path.getsize(path)
    try:
        with open(path, "r+b") as f:
            for _ in range(3):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        os.remove(path)
        console.print(f"[+] Wiped: {path}", style="bold green")
        log(f"Wiped file: {path}")
    except Exception as e:
        console.print(f"[-] Failed to wipe file: {e}", style="bold red")
        log(f"Failed to wipe file {path}: {e}")

# 3. MAC Spoof (Linux only)

def spoof_mac():
    if IS_WINDOWS:
        console.print("[-] MAC spoofing not supported on Windows.", style="bold red")
        return
    iface = Prompt.ask("Enter interface to spoof MAC (default wlan0)", default="wlan0")
    new_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0x00, 0xFF) for _ in range(5))
    try:
        run(f"ip link set {iface} down")
        run(f"ip link set {iface} address {new_mac}")
        run(f"ip link set {iface} up")
        console.print(f"[+] MAC spoofed: {new_mac}", style="bold green")
        log(f"MAC spoofed on {iface}: {new_mac}")
    except Exception as e:
        console.print(f"[-] Failed to spoof MAC: {e}", style="bold red")
        log(f"MAC spoof failed: {e}")

# 4. Outbound Connection Logger

def log_connections():
    console.print("[+] Active Connections:", style="bold cyan")
    output = run("netstat -an" if IS_WINDOWS else "ss -tuna")
    console.print(output)
    log("Displayed active connections")

# 5. Emergency Burn (Linux only)

def kill_everything():
    if not confirm_action("EMERGENCY BURN! This will kill network, wipe temp, disable swap, and power off! Proceed?"):
        console.print("[*] Emergency burn aborted.", style="bold yellow")
        return
    log("!!! EMERGENCY BURN TRIGGERED !!!")
    kill_network()
    if not IS_WINDOWS:
        run("swapoff -a")
        run("rm -rf /tmp/*")
        console.print("[!] RAM wiped, network down, temp cleared. System going dark.", style="bold red")
        log("Swap off, /tmp wiped")
        time.sleep(3)
        run("poweroff")
    else:
        console.print("[-] Emergency burn not fully supported on Windows.", style="bold yellow")

# 6. USB Watchdog

def scan_usb():
    console.print("[+] Connected USB devices:", style="bold cyan")
    output = run("wmic path CIM_LogicalDevice where \"Description like '%USB%'\" get /value" if IS_WINDOWS else "lsusb")
    console.print(output)
    log("Scanned USB devices")

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
    log(f"Vault mounted: {vault_path} at {mount_point}")

# 8. Clipboard Wipe

def wipe_clipboard():
    if IS_WINDOWS:
        run('echo off | clip')
    else:
        # Try xclip first
        if shutil.which("xclip"):
            run('printf "" | xclip -selection clipboard')
        # Fallback to wl-clipboard for Wayland
        elif shutil.which("wl-copy"):
            run('printf "" | wl-copy')
        else:
            console.print("[-] Clipboard wipe not supported: no xclip or wl-copy found.", style="bold red")
            return
    console.print("[+] Clipboard wiped.", style="bold green")
    log("Clipboard wiped")

# 9. Firewall Toggle

def toggle_firewall():
    if IS_WINDOWS:
        status = run('netsh advfirewall show allprofiles state')
        if "ON" in status:
            run('netsh advfirewall set allprofiles state off')
            console.print("[*] Firewall disabled.", style="bold yellow")
            log("Firewall disabled")
        else:
            run('netsh advfirewall set allprofiles state on')
            console.print("[+] Firewall enabled.", style="bold green")
            log("Firewall enabled")
    else:
        if not shutil.which("ufw"):
            console.print("[-] Firewall toggle not supported: ufw not found.", style="bold red")
            return
        status = run("ufw status")
        if "Status: active" in status:
            run("ufw disable")
            console.print("[*] Firewall disabled.", style="bold yellow")
            log("Firewall disabled")
        else:
            run("ufw enable")
            console.print("[+] Firewall enabled.", style="bold green")
            log("Firewall enabled")

# 10. Process Killer

def kill_process():
    proc = Prompt.ask("Enter suspicious process name to kill (e.g. tcpdump)")
    if not proc.strip():
        console.print("[-] Process name cannot be empty.", style="bold red")
        return
    if not confirm_action(f"Are you sure to kill all processes named '{proc}'?"):
        console.print("[*] Process kill aborted.", style="bold yellow")
        return
    try:
        if IS_WINDOWS:
            run(f"taskkill /F /IM {proc}.exe")
        else:
            run(f"pkill {proc}")
        console.print(f"[+] Killed processes named {proc}.", style="bold green")
        log(f"Killed processes: {proc}")
    except Exception as e:
        console.print(f"[-] Failed to kill process: {e}", style="bold red")
        log(f"Process kill failed: {e}")

# 11. Discord Webhook Configuration

def configure_discord_webhook():
    global WEBHOOK_URL
    url = Prompt.ask("Enter Discord webhook URL (leave blank to disable)")
    if url.strip() == "":
        WEBHOOK_URL = None
        console.print("[*] Discord webhook disabled.", style="bold yellow")
        log("Discord webhook disabled")
    else:
        WEBHOOK_URL = url.strip()
        console.print("[+] Discord webhook configured.", style="bold green")
        log("Discord webhook configured")

# Menus

def menu_page_1():
    while True:
        console.print(Panel("""
[1] Launch Vault
[2] Wipe File
[3] Go Dark (Kill Network)
[4] Spoof MAC
[5] View Connections
[6] More Options >>
[7] Exit
        """, title="Luma — Anti-Spook Suite [Page 1]", style="bold magenta"))
        choice = Prompt.ask("Select Option")
        if choice == "1": open_vault()
        elif choice == "2": wipe_file(Prompt.ask("File to wipe"))
        elif choice == "3": kill_network()
        elif choice == "4": spoof_mac()
        elif choice == "5": log_connections()
        elif choice == "6": menu_page_2()
        elif choice == "7": break
        else: console.print("Invalid option.", style="bold red")

def menu_page_2():
    while True:
        console.print(Panel("""
[1] Scan USB Devices
[2] Kill Everything
[3] Clipboard Wipe
[4] Toggle Firewall
[5] Kill Suspicious Process
[6] Configure Discord Webhook
[7] Back to Main Menu
        """, title="Luma — Anti-Spook Suite [Page 2]", style="bold magenta"))
        choice = Prompt.ask("Select Option")
        if choice == "1": scan_usb()
        elif choice == "2": kill_everything()
        elif choice == "3": wipe_clipboard()
        elif choice == "4": toggle_firewall()
        elif choice == "5": kill_process()
        elif choice == "6": configure_discord_webhook()
        elif choice == "7": return
        else: console.print("Invalid option.", style="bold red")

def menu():
    menu_page_1()

if __name__ == "__main__":
    os.system("cls" if IS_WINDOWS else "clear")
    console.print(ASCII_BANNER, style="bold blue")
    log("Luma launched")
    menu()
