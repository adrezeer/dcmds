import os
import string
from colorama import init, Fore, Style, Back
import subprocess
import datetime
import cv2
import time
import msvcrt  # For keyboard input on Windows
import math
import platform
import sys
import psutil  # For detailed system info

init(autoreset=True)  # Colors reset automatically

current_path = None
camera_active = False
video_recording = False
video_writer = None
cap = None

def print_logo():
    """Display DCMDS system logo with colors"""
    logo = f"""
{Fore.CYAN}{Style.BRIGHT}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  {Fore.GREEN}██████╗░{Fore.YELLOW}░█████╗░{Fore.MAGENTA}███╗░░░███╗{Fore.RED}██████╗░{Fore.BLUE}░██████╗{Fore.CYAN}  ║
║  {Fore.GREEN}██╔══██╗{Fore.YELLOW}██╔══██╗{Fore.MAGENTA}████╗░████║{Fore.RED}██╔══██╗{Fore.BLUE}██╔════╝{Fore.CYAN}  ║
║  {Fore.GREEN}██║░░██║{Fore.YELLOW}██║░░╚═╝{Fore.MAGENTA}██╔████╔██║{Fore.RED}██║░░██║{Fore.BLUE}╚█████╗░{Fore.CYAN}  ║
║  {Fore.GREEN}██║░░██║{Fore.YELLOW}██║░░██╗{Fore.MAGENTA}██║╚██╔╝██║{Fore.RED}██║░░██║{Fore.BLUE}░╚═══██╗{Fore.CYAN}  ║
║  {Fore.GREEN}██████╔╝{Fore.YELLOW}╚█████╔╝{Fore.MAGENTA}██║░╚═╝░██║{Fore.RED}██████╔╝{Fore.BLUE}██████╔╝{Fore.CYAN}  ║
║  {Fore.GREEN}╚═════╝░{Fore.YELLOW}░╚════╝░{Fore.MAGENTA}╚═╝░░░░░╚═╝{Fore.RED}╚═════╝░{Fore.BLUE}╚═════╝░{Fore.CYAN}  ║
║                                                               ║
║           {Fore.WHITE}{Style.BRIGHT}D A N R O D E   command   S Y S T E M{Fore.CYAN}               ║
║                                                               ║
║              {Fore.YELLOW}⚡ Advanced Terminal Interface ⚡{Fore.CYAN}               ║
║                  {Fore.RED}Alpha {Fore.GREEN}Version 0.0.1{Fore.CYAN}                          ║
║              {Fore.CYAN}Build: {Fore.YELLOW}January 29, 2026{Fore.CYAN}                        ║
║                    {Fore.YELLOW}[Under Development]{Fore.CYAN}                        ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(logo)
    time.sleep(0.5)

def separator():
    """Enhanced separator with gradient effect"""
    print(Fore.CYAN + "═" * 70)

def animated_separator():
    """Animated loading separator"""
    chars = ["▰", "▱"]
    for i in range(35):
        print(Fore.MAGENTA + chars[i % 2], end="", flush=True)
        time.sleep(0.01)
    print()

def list_drives():
    return [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]

def show_items():
    global current_path
    if not current_path:
        print_error("⚠ No path selected. Use BC or drive letter first.")
        return
    try:
        items = os.listdir(current_path)
        print(Fore.WHITE + Style.BRIGHT + f"\n📂 Contents of {current_path}:")
        separator()
        
        folders = []
        files = []
        
        for item in items:
            full = os.path.join(current_path, item)
            if os.path.isdir(full):
                folders.append(item)
            else:
                files.append(item)
        
        # Display folders first
        for folder in sorted(folders):
            print(Fore.CYAN + Style.BRIGHT + "📁 [DIR]  " + Fore.YELLOW + folder)
        
        # Display files
        for file in sorted(files):
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.py', '.js', '.java', '.cpp', '.c']:
                icon = "💻"
                color = Fore.GREEN
            elif ext in ['.html', '.css', '.jsx']:
                icon = "🌐"
                color = Fore.MAGENTA
            elif ext in ['.txt', '.md', '.doc', '.docx']:
                icon = "📄"
                color = Fore.WHITE
            elif ext in ['.jpg', '.png', '.gif', '.bmp']:
                icon = "🖼️"
                color = Fore.BLUE
            elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
                icon = "🎬"
                color = Fore.RED
            else:
                icon = "📋"
                color = Fore.YELLOW
            
            print(color + f"{icon}        " + file)
        
        separator()
        print(Fore.WHITE + f"Total: {len(folders)} folders, {len(files)} files")
        print(Fore.CYAN + f"\n💡 Tip: Type " + Fore.GREEN + "'browse'" + Fore.CYAN + " to navigate with arrow keys!")
        
    except Exception as e:
        print_error(f"❌ Cannot access this folder: {e}")

def browse_files():
    """Interactive file browser with arrow key navigation"""
    global current_path
    if not current_path:
        print_error("⚠ No path selected. Use BC or drive letter first.")
        return None
    
    try:
        items = os.listdir(current_path)
        all_items = []
        
        # Collect all items with icons
        for item in sorted(items):
            full = os.path.join(current_path, item)
            if os.path.isdir(full):
                all_items.append(("📁 [DIR]  " + item, item, "folder"))
            else:
                ext = os.path.splitext(item)[1].lower()
                if ext in ['.py', '.js', '.java', '.cpp', '.c']:
                    icon = "💻"
                elif ext in ['.html', '.css', '.jsx']:
                    icon = "🌐"
                elif ext in ['.txt', '.md', '.doc', '.docx']:
                    icon = "📄"
                elif ext in ['.jpg', '.png', '.gif', '.bmp']:
                    icon = "🖼️"
                elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
                    icon = "🎬"
                else:
                    icon = "📋"
                all_items.append((f"{icon}        {item}", item, "file"))
        
        if not all_items:
            print_error("No files or folders found")
            return None
        
        selected = 0
        
        while True:
            # Clear and redraw
            os.system('cls' if os.name == 'nt' else 'clear')
            print_logo()
            print(Fore.CYAN + Style.BRIGHT + f"\n📂 Browsing: {current_path}")
            print(Fore.WHITE + "Use ↑↓ arrows, Enter to select, ESC to cancel\n")
            separator()
            
            # Display items with selection
            display_start = max(0, selected - 15)
            display_end = min(len(all_items), display_start + 30)
            
            for i in range(display_start, display_end):
                display, name, item_type = all_items[i]
                if i == selected:
                    print(Back.WHITE + Fore.BLACK + "► " + display + " " * (60 - len(display)))
                else:
                    if item_type == "folder":
                        print(Fore.CYAN + "  " + display)
                    else:
                        print(Fore.YELLOW + "  " + display)
            
            separator()
            print(Fore.GREEN + f"\nSelected: " + Fore.YELLOW + all_items[selected][1])
            print(Fore.CYAN + f"Item {selected + 1} of {len(all_items)}")
            
            # Get key input - blocking wait (no infinite loop!)
            key = msvcrt.getch()
            
            # Arrow keys return two bytes
            if key == b'\xe0':  # Arrow key prefix
                key = msvcrt.getch()
                if key == b'H':  # Up arrow
                    selected = (selected - 1) % len(all_items)
                elif key == b'P':  # Down arrow
                    selected = (selected + 1) % len(all_items)
            
            # Enter key
            elif key == b'\r':
                return all_items[selected][1]
            
            # ESC key
            elif key == b'\x1b':
                print_info("\nBrowse cancelled")
                return None
            
            # 'c' or 'C' key for copy
            elif key.lower() == b'c':
                return all_items[selected][1]
    
    except Exception as e:
        print_error(f"Error browsing: {e}")
        return None

def print_command(text):
    print(Fore.GREEN + Style.BRIGHT + "✓ " + text)

def print_output(text):
    print(Fore.MAGENTA + Style.BRIGHT + "➤ " + text)

def print_error(text):
    print(Fore.RED + Style.BRIGHT + "✗ " + text)

def print_success(text):
    print(Fore.GREEN + Back.BLACK + Style.BRIGHT + "✓ " + text)

def print_info(text):
    print(Fore.CYAN + Style.BRIGHT + "ℹ " + text)

# System Startup Animation
os.system('cls' if os.name == 'nt' else 'clear')
print_logo()
print(Fore.CYAN + "Initializing DCMDS..." + Style.RESET_ALL)
animated_separator()
print_success("System Ready!")
separator()

print(Fore.YELLOW + Style.BRIGHT + "\n🎯 DCMDS - Danrode CMD System")
print(Fore.WHITE + "Advanced Python Terminal with Enhanced Features")
print(Fore.CYAN + "\nType " + Fore.GREEN + "'help'" + Fore.CYAN + " to see all available commands")
separator()

while True:
    # Custom prompt with current path
    if current_path:
        prompt = f"{Fore.YELLOW}[{Fore.GREEN}{current_path}{Fore.YELLOW}]{Fore.WHITE} DCMDS{Fore.CYAN}>{Fore.WHITE} "
    else:
        prompt = f"{Fore.WHITE}DCMDS{Fore.CYAN}>{Fore.WHITE} "
    
    cmd = input(prompt).strip()
    if not cmd:
        continue

    separator()

    # ---- EXIT ----
    if cmd.lower() == "exit" or cmd.lower() == "bsx":
        print(Fore.YELLOW + "Shutting down DCMDS...")
        animated_separator()
        print_success("Goodbye! 👋")
        break

    # ---- HELP ----
    elif cmd.lower() == "help":
        print(Fore.CYAN + Style.BRIGHT + "\n📚 DCMDS COMMAND REFERENCE\n")
        commands = [
            ("BC", "Show all available drives (interactive)", "💾"),
            ("C / D / E", "Switch to specified drive", "🔄"),
            ("CD <folder>", "Enter specified folder", "📂"),
            (">> <folder>", "Quick enter folder (shortcut for CD)", "⚡"),
            ("..", "Go back to parent folder", "⬆️"),
            ("..", "Exit from drive (when at root)", "🚪"),
            ("CDT", "Display current path", "📍"),
            ("ls", "List files and folders", "📋"),
            ("browse", "Interactive file browser (arrow keys)", "🎯"),
            ("<filename>", "Auto-detect and run file directly", "🎯"),
            ("open <file>", "Open file with default program", "🚀"),
            ("create <file>", "Create new file in current folder", "✨"),
            ("delete <file>", "Delete file in current folder", "🗑️"),
            ("run <file>", "Run file (HTML→Chrome, Code→VS Code)", "⚡"),
            ("code <file>", "Open file in VS Code", "💻"),
            ("acode", "Enter Python interactive mode", "🐍"),
            ("calc", "Open advanced calculator", "🧮"),
            ("server port <num>", "Start local HTTP server", "🌐"),
            ("camera", "Open camera preview", "📷"),
            ("take", "Take a photo", "📸"),
            ("vid", "Start video recording", "🎥"),
            ("endvid", "Stop video recording", "⏹️"),
            ("clear", "Clear screen", "🧹"),
            ("version", "Show version information", "ℹ️"),
            ("debug", "System diagnostics and information", "🔧"),
            ("shutdown", "Shutdown computer", "🔴"),
            ("sleep", "Put computer to sleep", "😴"),
            ("restart", "Restart computer", "🔄"),
            ("exit / bsx", "Exit terminal (quick exit)", "🚪")
        ]
        
        for cmd_name, description, icon in commands:
            print(f"{Fore.GREEN}{icon} {Fore.YELLOW}{cmd_name:<20} {Fore.WHITE}→ {Fore.CYAN}{description}")
        
        separator()

    # ---- CLEAR ----
    elif cmd.lower() == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')
        print_logo()
        print_success("Screen cleared!")

    # ---- VERSION ----
    elif cmd.lower() == "version":
        print(Fore.CYAN + Style.BRIGHT + "\n📊 DCMDS VERSION INFORMATION\n")
        separator()
        print(Fore.WHITE + "System Name:     " + Fore.YELLOW + "DCMDS (Danrode CMD System)")
        print(Fore.WHITE + "Version:         " + Fore.GREEN + "0.0.1")
        print(Fore.WHITE + "Stage:           " + Fore.RED + "Alpha (Under Development)")
        print(Fore.WHITE + "Build:           " + Fore.CYAN + "January 29, 2026")
        print(Fore.WHITE + "Creator:         " + Fore.MAGENTA + "Danrode")
        separator()
        print(Fore.YELLOW + "\n📝 Version Format: Alpha.Beta.Version")
        print(Fore.WHITE + "• " + Fore.RED + "0" + Fore.WHITE + ".x.x = Alpha (Under Development)")
        print(Fore.WHITE + "• x." + Fore.YELLOW + "0" + Fore.WHITE + ".x = Beta Testing")
        print(Fore.WHITE + "• x.x." + Fore.GREEN + "1" + Fore.WHITE + " = Version Number (Official Release)")

    # ---- DEBUG ----
    elif cmd.lower() == "debug":
        print(Fore.RED + Style.BRIGHT + "\n🔧 DCMDS SYSTEM DIAGNOSTICS\n")
        separator()
        
        # DCMDS Info
        print(Fore.CYAN + Style.BRIGHT + "📦 DCMDS INFORMATION:")
        print(Fore.WHITE + "  System Name:    " + Fore.YELLOW + "DCMDS (Danrode CMD System)")
        print(Fore.WHITE + "  Version:        " + Fore.GREEN + "0.0.1 (Alpha)")
        print(Fore.WHITE + "  Build Date:     " + Fore.CYAN + "January 29, 2026")
        print(Fore.WHITE + "  Current Path:   " + Fore.YELLOW + (current_path if current_path else "None"))
        
        separator()
        
        # Python Info
        print(Fore.CYAN + Style.BRIGHT + "🐍 PYTHON INFORMATION:")
        print(Fore.WHITE + "  Python Version: " + Fore.GREEN + sys.version.split()[0])
        print(Fore.WHITE + "  Full Version:   " + Fore.YELLOW + sys.version.replace('\n', ' '))
        print(Fore.WHITE + "  Executable:     " + Fore.CYAN + sys.executable)
        print(Fore.WHITE + "  Platform:       " + Fore.MAGENTA + sys.platform)
        
        separator()
        
        # Windows Info
        print(Fore.CYAN + Style.BRIGHT + "🪟 WINDOWS INFORMATION:")
        print(Fore.WHITE + "  OS:             " + Fore.YELLOW + platform.system() + " " + platform.release())
        print(Fore.WHITE + "  Version:        " + Fore.GREEN + platform.version())
        print(Fore.WHITE + "  Edition:        " + Fore.CYAN + platform.win32_edition())
        print(Fore.WHITE + "  Architecture:   " + Fore.MAGENTA + platform.machine())
        print(Fore.WHITE + "  Computer Name:  " + Fore.YELLOW + platform.node())
        
        separator()
        
        # Processor Info
        print(Fore.CYAN + Style.BRIGHT + "💻 PROCESSOR INFORMATION:")
        print(Fore.WHITE + "  Processor:      " + Fore.YELLOW + platform.processor())
        print(Fore.WHITE + "  Architecture:   " + Fore.GREEN + platform.architecture()[0])
        print(Fore.WHITE + "  CPU Cores:      " + Fore.CYAN + f"{psutil.cpu_count(logical=False)} Physical, {psutil.cpu_count(logical=True)} Logical")
        print(Fore.WHITE + "  CPU Usage:      " + Fore.MAGENTA + f"{psutil.cpu_percent(interval=1)}%")
        
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                print(Fore.WHITE + "  CPU Frequency:  " + Fore.YELLOW + f"{cpu_freq.current:.2f} MHz (Max: {cpu_freq.max:.2f} MHz)")
        except:
            pass
        
        separator()
        
        # Memory Info
        print(Fore.CYAN + Style.BRIGHT + "🧠 MEMORY INFORMATION:")
        memory = psutil.virtual_memory()
        print(Fore.WHITE + "  Total RAM:      " + Fore.GREEN + f"{memory.total / (1024**3):.2f} GB")
        print(Fore.WHITE + "  Available:      " + Fore.YELLOW + f"{memory.available / (1024**3):.2f} GB")
        print(Fore.WHITE + "  Used:           " + Fore.RED + f"{memory.used / (1024**3):.2f} GB ({memory.percent}%)")
        print(Fore.WHITE + "  Free:           " + Fore.CYAN + f"{memory.free / (1024**3):.2f} GB")
        
        separator()
        
        # Disk Info
        print(Fore.CYAN + Style.BRIGHT + "💾 DISK INFORMATION:")
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                print(Fore.WHITE + f"  Drive {partition.device}")
                print(Fore.WHITE + f"    Total:        " + Fore.GREEN + f"{usage.total / (1024**3):.2f} GB")
                print(Fore.WHITE + f"    Used:         " + Fore.RED + f"{usage.used / (1024**3):.2f} GB ({usage.percent}%)")
                print(Fore.WHITE + f"    Free:         " + Fore.CYAN + f"{usage.free / (1024**3):.2f} GB")
                print(Fore.WHITE + f"    File System:  " + Fore.YELLOW + partition.fstype)
            except:
                pass
        
        separator()
        
        # Network Info
        print(Fore.CYAN + Style.BRIGHT + "🌐 NETWORK INFORMATION:")
        net_if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in net_if_addrs.items():
            print(Fore.WHITE + f"  Interface: " + Fore.YELLOW + interface_name)
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    print(Fore.WHITE + f"    IP Address:   " + Fore.GREEN + address.address)
                elif str(address.family) == 'AddressFamily.AF_LINK':
                    print(Fore.WHITE + f"    MAC Address:  " + Fore.CYAN + address.address)
        
        separator()
        
        # Loaded Modules
        print(Fore.CYAN + Style.BRIGHT + "📚 LOADED MODULES:")
        modules = ['colorama', 'cv2', 'psutil', 'datetime', 'subprocess']
        for module in modules:
            if module in sys.modules:
                print(Fore.WHITE + f"  ✓ {module:<15} " + Fore.GREEN + "Loaded")
            else:
                print(Fore.WHITE + f"  ✗ {module:<15} " + Fore.RED + "Not Loaded")
        
        separator()
        
        # Access Options
        print(Fore.YELLOW + Style.BRIGHT + "\n⚙️  ACCESS OPTIONS:")
        print(Fore.WHITE + "  1. " + Fore.GREEN + "Export Debug Log to File")
        print(Fore.WHITE + "  2. " + Fore.GREEN + "Show Environment Variables")
        print(Fore.WHITE + "  3. " + Fore.GREEN + "Show Running Processes")
        print(Fore.WHITE + "  4. " + Fore.GREEN + "Network Statistics")
        print(Fore.WHITE + "  5. " + Fore.GREEN + "Battery Information")
        print(Fore.WHITE + "  0. " + Fore.CYAN + "Exit Debug Mode")
        
        while True:
            choice = input(Fore.YELLOW + "\nSelect option (0-5): " + Fore.WHITE).strip()
            
            if choice == "0":
                print_info("Exited debug mode")
                break
            
            elif choice == "1":
                try:
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"dcmds_debug_{timestamp}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write("DCMDS DEBUG LOG\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(f"Generated: {datetime.datetime.now()}\n\n")
                        f.write(f"DCMDS Version: 0.0.1 (Alpha)\n")
                        f.write(f"Build Date: January 29, 2026\n")
                        f.write(f"Python Version: {sys.version}\n")
                        f.write(f"OS: {platform.system()} {platform.release()}\n")
                        f.write(f"Processor: {platform.processor()}\n")
                        f.write(f"RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB\n")
                    print_success(f"Debug log saved: {Fore.YELLOW}{filename}")
                except Exception as e:
                    print_error(f"Failed to save log: {e}")
            
            elif choice == "2":
                print(Fore.CYAN + "\n📝 ENVIRONMENT VARIABLES:")
                separator()
                for key, value in sorted(os.environ.items())[:10]:  # Show first 10
                    print(Fore.WHITE + f"  {key:<20} " + Fore.YELLOW + f"{value[:50]}...")
                print(Fore.CYAN + f"\n  ... and {len(os.environ) - 10} more")
            
            elif choice == "3":
                print(Fore.CYAN + "\n⚙️  TOP 10 PROCESSES:")
                separator()
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except:
                        pass
                processes = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
                for proc in processes:
                    print(Fore.WHITE + f"  {proc['name']:<25} " + 
                          Fore.CYAN + f"PID: {proc['pid']:<8} " + 
                          Fore.YELLOW + f"CPU: {proc['cpu_percent']:.1f}% " + 
                          Fore.GREEN + f"RAM: {proc['memory_percent']:.1f}%")
            
            elif choice == "4":
                print(Fore.CYAN + "\n🌐 NETWORK STATISTICS:")
                separator()
                net_io = psutil.net_io_counters()
                print(Fore.WHITE + f"  Bytes Sent:     " + Fore.GREEN + f"{net_io.bytes_sent / (1024**2):.2f} MB")
                print(Fore.WHITE + f"  Bytes Received: " + Fore.YELLOW + f"{net_io.bytes_recv / (1024**2):.2f} MB")
                print(Fore.WHITE + f"  Packets Sent:   " + Fore.CYAN + f"{net_io.packets_sent}")
                print(Fore.WHITE + f"  Packets Recv:   " + Fore.MAGENTA + f"{net_io.packets_recv}")
            
            elif choice == "5":
                try:
                    battery = psutil.sensors_battery()
                    if battery:
                        print(Fore.CYAN + "\n🔋 BATTERY INFORMATION:")
                        separator()
                        print(Fore.WHITE + f"  Charge:         " + Fore.GREEN + f"{battery.percent}%")
                        print(Fore.WHITE + f"  Plugged In:     " + (Fore.GREEN + "Yes" if battery.power_plugged else Fore.RED + "No"))
                        if battery.secsleft != -1:
                            hours = battery.secsleft // 3600
                            minutes = (battery.secsleft % 3600) // 60
                            print(Fore.WHITE + f"  Time Left:      " + Fore.YELLOW + f"{hours}h {minutes}m")
                    else:
                        print_info("No battery detected (Desktop PC)")
                except:
                    print_error("Battery information not available")
            
            else:
                print_error("Invalid option")

    # ---- BC (List Drives) ----
    elif cmd.lower() == "bc":
        drives = list_drives()
        if not drives:
            print_error("No drives found!")
        else:
            selected = 0
            browsing = True
            
            while browsing:
                # Clear and redraw
                os.system('cls' if os.name == 'nt' else 'clear')
                print_logo()
                print(Fore.CYAN + Style.BRIGHT + "\n💾 AVAILABLE DRIVES")
                print(Fore.WHITE + "Use ↑↓ arrows, Enter to select, ESC to cancel\n")
                separator()
                
                # Display drives with selection
                for i, drive in enumerate(drives):
                    if i == selected:
                        print(Back.GREEN + Fore.BLACK + "► " + drive + " " * 20)
                    else:
                        print(Fore.YELLOW + "  " + drive)
                
                separator()
                print(Fore.GREEN + f"\nSelected: " + Fore.YELLOW + drives[selected])
                print(Fore.CYAN + "\n↑↓ Navigate | Enter Select | ESC Cancel")
                
                # Get key input - blocking wait
                key = msvcrt.getch()
                
                # Arrow keys
                if key == b'\xe0':
                    key = msvcrt.getch()
                    if key == b'H':  # Up arrow
                        selected = (selected - 1) % len(drives)
                    elif key == b'P':  # Down arrow
                        selected = (selected + 1) % len(drives)
                
                # Enter key
                elif key == b'\r':
                    current_path = drives[selected]
                    print_success(f"\nCurrent path set to: {Fore.YELLOW}{current_path}")
                    browsing = False
                
                # ESC key
                elif key == b'\x1b':
                    print_info("\nSelection cancelled")
                    browsing = False
                
                # C key
                elif key.lower() == b'c':
                    current_path = drives[selected]
                    print_success(f"\nCurrent path set to: {Fore.YELLOW}{current_path}")
                    browsing = False

    # ---- Drive Shortcut (C / D / E) ----
    elif len(cmd) == 1 and cmd.upper() + ":\\" in list_drives():
        current_path = cmd.upper() + ":\\"
        print_success(f"Current path set to: {Fore.YELLOW}{current_path}")

    # ---- Quick CD with >> ----
    elif cmd.startswith(">> "):
        target = cmd[3:].strip()
        if not current_path:
            print_error("No current path. Choose drive first.")
        else:
            new_path = os.path.join(current_path, target)
            if os.path.isdir(new_path):
                current_path = new_path
                print_success(f"Entered folder: {Fore.YELLOW}{current_path}")
            else:
                print_error("Folder not found")

    # ---- Go Back (..) ----
    elif cmd == "..":
        if not current_path:
            print_error("No current path selected")
        else:
            # Check if at drive root (e.g., C:\)
            if len(current_path) <= 3:  # At root like "C:\"
                print_info(f"Exiting from {Fore.YELLOW}{current_path}")
                current_path = None
                print_success("Returned to drive selection. Use " + Fore.GREEN + "'bc'" + Fore.CYAN + " to choose a drive")
            else:
                parent = os.path.dirname(current_path.rstrip("\\"))
                if parent and len(parent) > 2:
                    current_path = parent
                    print_success(f"Moved to: {Fore.YELLOW}{current_path}")
                else:
                    current_path = parent + "\\"
                    print_success(f"Moved to root: {Fore.YELLOW}{current_path}")

    # ---- CD ----
    elif cmd.lower().startswith("cd "):
        target = cmd[3:].strip()
        if not current_path:
            print_error("No current path. Choose drive first.")
        else:
            new_path = os.path.join(current_path, target)
            if os.path.isdir(new_path):
                current_path = new_path
                print_success(f"Entered folder: {Fore.YELLOW}{current_path}")
            else:
                print_error("Folder not found")

    # ---- CDT ----
    elif cmd.lower() == "cdt":
        if current_path:
            print_info(f"Current path: {Fore.YELLOW}{current_path}")
        else:
            print_error("No path selected")

    # ---- LS ----
    elif cmd.lower() == "ls":
        show_items()

    # ---- BROWSE ----
    elif cmd.lower() == "browse":
        selected_file = browse_files()
        if selected_file:
            separator()
            print_success(f"Selected: {Fore.YELLOW}{selected_file}")
            print(Fore.CYAN + "What do you want to do?")
            print(Fore.WHITE + "1. " + Fore.GREEN + "Open file")
            print(Fore.WHITE + "2. " + Fore.GREEN + "Enter folder")
            print(Fore.WHITE + "3. " + Fore.GREEN + "Copy name to clipboard")
            print(Fore.WHITE + "4. " + Fore.GREEN + "Use in command (type command)")
            
            action = input(Fore.YELLOW + "\nChoice (1-4): ").strip()
            
            if action == "1":
                full_path = os.path.join(current_path, selected_file)
                if os.path.isfile(full_path):
                    print_output(f"Opening {Fore.YELLOW}{selected_file}")
                    os.startfile(full_path)
                else:
                    print_error("Cannot open folder, use option 2")
            
            elif action == "2":
                full_path = os.path.join(current_path, selected_file)
                if os.path.isdir(full_path):
                    current_path = full_path
                    print_success(f"Entered: {Fore.YELLOW}{current_path}")
                else:
                    print_error("Not a folder!")
            
            elif action == "3":
                try:
                    os.system(f'echo {selected_file}| clip')
                    print_success(f"Copied to clipboard: {Fore.YELLOW}{selected_file}")
                except:
                    print_error("Failed to copy to clipboard")
            
            elif action == "4":
                user_cmd = input(Fore.GREEN + f"Command for '{selected_file}': " + Fore.WHITE).strip()
                if user_cmd:
                    full_cmd = f"{user_cmd} {selected_file}"
                    print_info(f"Executing: {Fore.YELLOW}{full_cmd}")

    # ---- OPEN ----
    elif cmd.lower().startswith("open "):
        if not current_path:
            print_error("No path selected")
        else:
            name = cmd[5:].strip()
            path = os.path.join(current_path, name)
            if os.path.exists(path):
                print_success(f"Opening file: {Fore.YELLOW}{path}")
                os.startfile(path)
            else:
                print_error("File not found")

    # ---- CREATE ----
    elif cmd.lower().startswith("create "):
        if not current_path:
            print_error("No path selected")
        else:
            name = cmd[7:].strip()
            path = os.path.join(current_path, name)
            if not os.path.exists(path):
                open(path, "w").close()
                print_success(f"File created: {Fore.YELLOW}{path}")
            else:
                print_error("File already exists")

    # ---- DELETE ----
    elif cmd.lower().startswith("delete "):
        if not current_path:
            print_error("No path selected")
        else:
            name = cmd[7:].strip()
            path = os.path.join(current_path, name)
            if os.path.isfile(path):
                confirm = input(Fore.RED + f"⚠ Delete {name}? (y/n): ")
                if confirm.lower() == 'y':
                    os.remove(path)
                    print_success(f"File deleted: {Fore.YELLOW}{path}")
                else:
                    print_info("Deletion cancelled")
            else:
                print_error("File not found")

    # ---- RUN ----
    elif cmd.lower().startswith("run "):
        if not current_path:
            print_error("No path selected")
        else:
            name = cmd[4:].strip()
            path = os.path.join(current_path, name)
            if not os.path.exists(path):
                print_error("File not found")
            else:
                ext = os.path.splitext(path)[1].lower()
                if ext == ".html":
                    print_output(f"Opening {Fore.YELLOW}{path}{Fore.MAGENTA} in Google Chrome...")
                    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                    if os.path.exists(chrome_path):
                        subprocess.run([chrome_path, path])
                        print_success("Launched successfully!")
                    else:
                        print_error("Chrome not found! Edit path if needed.")
                elif ext in [".py", ".js", ".java", ".cpp", ".c", ".cs"]:
                    print_output(f"Opening {Fore.YELLOW}{path}{Fore.MAGENTA} in VS Code...")
                    os.system(f'code "{path}"')
                    print_success("Launched successfully!")
                else:
                    print_error("Cannot run this file type")

    # ---- CODE ----
    elif cmd.lower().startswith("code "):
        if not current_path:
            print_error("No path selected")
        else:
            name = cmd[5:].strip()
            path = os.path.join(current_path, name)
            if os.path.exists(path):
                print_output(f"Opening {Fore.YELLOW}{path}{Fore.MAGENTA} in VS Code...")
                os.system(f'code "{path}"')
                print_success("Launched successfully!")
            else:
                print_error("File not found")

    # ---- ACODE ----
    elif cmd.lower() == "acode":
        if not current_path:
            print_error("No path selected")
        else:
            print(Fore.CYAN + Style.BRIGHT + "\n🐍 Python Interactive Mode")
            print(Fore.WHITE + "Type 'xcode' to exit\n")
            separator()
            while True:
                py_line = input(Fore.GREEN + "PY>> " + Fore.WHITE).strip()
                if py_line.lower() == "xcode":
                    print_success("Exited acode mode")
                    break
                try:
                    result = eval(py_line)
                    if result is not None:
                        print(Fore.MAGENTA + "➤ " + str(result))
                except SyntaxError:
                    try:
                        exec(py_line)
                    except Exception as e:
                        print_error(f"Error: {e}")
                except Exception as e:
                    print_error(f"Error: {e}")

    # ---- CALCULATOR ----
    elif cmd.lower() == "calc":
        print(Fore.CYAN + Style.BRIGHT + "\n🧮 DCMDS ADVANCED CALCULATOR")
        print(Fore.WHITE + "Type 'exit' to quit calculator\n")
        separator()
        print(Fore.YELLOW + "Supported operations:")
        print(Fore.WHITE + "• Basic: " + Fore.GREEN + "+ - * / % **")
        print(Fore.WHITE + "• Functions: " + Fore.GREEN + "sqrt(), sin(), cos(), tan(), log(), abs()")
        print(Fore.WHITE + "• Constants: " + Fore.GREEN + "pi, e")
        print(Fore.WHITE + "• Examples: " + Fore.CYAN + "2+2, sqrt(16), sin(pi/2), 2**8")
        separator()
        
        calc_history = []
        
        while True:
            calc_input = input(Fore.GREEN + "CALC>> " + Fore.WHITE).strip()
            
            if calc_input.lower() == "exit":
                print_success("Exited calculator")
                break
            
            if calc_input.lower() == "history":
                if calc_history:
                    print(Fore.CYAN + "\n📝 Calculation History:")
                    for i, (expr, res) in enumerate(calc_history, 1):
                        print(Fore.WHITE + f"{i}. " + Fore.YELLOW + f"{expr}" + Fore.WHITE + " = " + Fore.GREEN + f"{res}")
                else:
                    print_info("No history yet")
                continue
            
            if calc_input.lower() == "clear":
                calc_history.clear()
                print_success("History cleared")
                continue
            
            if not calc_input:
                continue
            
            try:
                # Replace common math functions
                calc_input_eval = calc_input.replace("^", "**")
                
                # Safe evaluation with math functions
                safe_dict = {
                    "sqrt": math.sqrt,
                    "sin": math.sin,
                    "cos": math.cos,
                    "tan": math.tan,
                    "log": math.log,
                    "log10": math.log10,
                    "abs": abs,
                    "pi": math.pi,
                    "e": math.e,
                    "pow": pow,
                    "round": round,
                    "floor": math.floor,
                    "ceil": math.ceil,
                }
                
                result = eval(calc_input_eval, {"__builtins__": {}}, safe_dict)
                print(Fore.MAGENTA + Style.BRIGHT + "➤ " + Fore.GREEN + str(result))
                calc_history.append((calc_input, result))
                
            except Exception as e:
                print_error(f"Error: {e}")

    # ---- SERVER ----
    elif cmd.lower().startswith("server port "):
        port_str = cmd[12:].strip()
        if not port_str.isdigit():
            print_error("Invalid port number")
        else:
            port = int(port_str)
            if not current_path:
                print_error("No path selected. Choose a folder first.")
            else:
                print_output(f"Starting HTTP server at {Fore.YELLOW}http://localhost:{port}/{Fore.MAGENTA}")
                print_output(f"Serving: {Fore.YELLOW}{current_path}")
                print(Fore.RED + "\n⚠ Press Ctrl+C to stop the server\n")
                try:
                    import http.server
                    import socketserver

                    os.chdir(current_path)
                    handler = http.server.SimpleHTTPRequestHandler
                    with socketserver.TCPServer(("", port), handler) as httpd:
                        print_success(f"Server running on port {port}")
                        httpd.serve_forever()
                except KeyboardInterrupt:
                    print_output("\nServer stopped")
                except OSError as e:
                    print_error(f"Failed to start server: {e}")

    # ---- CAMERA ----
    elif cmd.lower() == "camera":
        if camera_active:
            print_error("Camera already active!")
        else:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print_error("Cannot open camera")
            else:
                camera_active = True
                print_success("Camera active. Press 'q' to close preview")
                while camera_active and not video_recording:
                    ret, frame = cap.read()
                    if not ret:
                        print_error("Failed to grab frame")
                        break
                    cv2.imshow("DCMDS Camera", frame)
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        camera_active = False
                        break
                cap.release()
                cv2.destroyAllWindows()
                print_success("Camera closed")

    # ---- TAKE PHOTO ----
    elif cmd.lower() == "take":
        if camera_active and cap is not None:
            ret, frame = cap.read()
            if ret:
                filename = f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                cv2.imwrite(filename, frame)
                print_success(f"Photo saved: {Fore.YELLOW}{filename}")
            else:
                print_error("Failed to capture photo")
        else:
            print_error("Camera not active. Use 'camera' command first")

    # ---- START VIDEO ----
    elif cmd.lower() == "vid":
        if camera_active and cap is not None:
            if video_recording:
                print_error("Video already recording!")
            else:
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                filename = f"video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
                frame_width = int(cap.get(3))
                frame_height = int(cap.get(4))
                video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))
                video_recording = True
                print_success(f"Recording video... Use 'endvid' to stop")
                print_info(f"Output: {Fore.YELLOW}{filename}")
        else:
            print_error("Camera not active. Use 'camera' command first")

    # ---- END VIDEO ----
    elif cmd.lower() == "endvid":
        if video_recording:
            video_recording = False
            if video_writer is not None:
                video_writer.release()
            cv2.destroyAllWindows()
            print_success("Video recording stopped and saved")
        else:
            print_error("No video is being recorded")

    # ---- SHUTDOWN ----
    elif cmd.lower() == "shutdown":
        print(Fore.RED + Style.BRIGHT + "⚠️  WARNING: This will shutdown your computer!")
        confirm = input(Fore.YELLOW + "Are you sure? (yes/no): ").strip().lower()
        if confirm in ["yes", "y"]:
            print_output("Shutting down computer in 10 seconds...")
            print(Fore.RED + "Press Ctrl+C to cancel")
            try:
                time.sleep(2)
                os.system("shutdown /s /t 10")
                print_success("Shutdown initiated!")
            except KeyboardInterrupt:
                print_info("Shutdown cancelled")
        else:
            print_info("Shutdown cancelled")

    # ---- SLEEP ----
    elif cmd.lower() == "sleep":
        print(Fore.YELLOW + Style.BRIGHT + "💤 Putting computer to sleep...")
        confirm = input(Fore.YELLOW + "Continue? (yes/no): ").strip().lower()
        if confirm in ["yes", "y"]:
            print_success("Going to sleep mode...")
            time.sleep(1)
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            print_info("Sleep cancelled")

    # ---- RESTART ----
    elif cmd.lower() == "restart":
        print(Fore.RED + Style.BRIGHT + "⚠️  WARNING: This will restart your computer!")
        confirm = input(Fore.YELLOW + "Are you sure? (yes/no): ").strip().lower()
        if confirm in ["yes", "y"]:
            print_output("Restarting computer in 10 seconds...")
            print(Fore.RED + "Press Ctrl+C to cancel")
            try:
                time.sleep(2)
                os.system("shutdown /r /t 10")
                print_success("Restart initiated!")
            except KeyboardInterrupt:
                print_info("Restart cancelled")
        else:
            print_info("Restart cancelled")

    else:
        # ---- AUTO-DETECT: Try to find and run the file ----
        if current_path and not cmd.startswith(" "):
            # Check if it's a file in current directory
            potential_file = os.path.join(current_path, cmd)
            
            # First check if file exists
            if os.path.exists(potential_file):
                # It's a file
                if os.path.isfile(potential_file):
                    ext = os.path.splitext(potential_file)[1].lower()
                    
                    # Auto-run HTML files in Chrome
                    if ext == ".html":
                        print_output(f"🌐 Detected HTML file. Opening in Chrome...")
                        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                        if os.path.exists(chrome_path):
                            subprocess.run([chrome_path, potential_file])
                            print_success("Launched successfully!")
                        else:
                            print_error("Chrome not found!")
                    
                    # Auto-open code files in VS Code
                    elif ext in [".py", ".js", ".java", ".cpp", ".c", ".cs", ".css", ".jsx"]:
                        print_output(f"💻 Detected code file. Opening in VS Code...")
                        os.system(f'code "{potential_file}"')
                        print_success("Launched successfully!")
                    
                    # Auto-open with default program
                    else:
                        print_output(f"📂 Opening with default program...")
                        os.startfile(potential_file)
                        print_success("Launched successfully!")
                
                # It's a folder
                elif os.path.isdir(potential_file):
                    current_path = potential_file
                    print_success(f"Entered folder: {Fore.YELLOW}{current_path}")
            
            # File/folder doesn't exist
            else:
                print_error(f"❌ File or folder '{cmd}' not found!")
                print_info(f"💡 Tip: Type 'ls' to see available files and folders")
        else:
            print_error(f"Unknown command: '{cmd}'. Type 'help' for available commands")

    separator()
