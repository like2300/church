"""
Dhavant Croissance Application Launcher - Version Professionnelle
Lance Django directement avec ouverture automatique du navigateur
Compatible toutes machines Windows
"""
import threading
import time
import tkinter as tk
from tkinter import ttk
import webbrowser
import os
import sys
import socket
import shutil
import tempfile
import traceback
import subprocess
import platform

# CRITICAL: Set Django settings BEFORE any Django import
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

def is_port_in_use(port):
    """Check if port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def open_browser_url(url):
    """Open browser using multiple methods for maximum compatibility"""
    try:
        # Method 1: Windows start command
        if platform.system() == 'Windows':
            subprocess.Popen(['start', url], shell=True, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return True
    except:
        pass
    
    try:
        # Method 2: Default webbrowser module
        webbrowser.open(url, new=2)
        return True
    except:
        pass
    
    try:
        # Method 3: Direct browser execution
        if platform.system() == 'Windows':
            # Try common browsers
            browsers = [
                'chrome', 'firefox', 'msedge', 'explorer', 
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
            ]
            for browser in browsers:
                try:
                    subprocess.Popen([browser, url],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    return True
                except:
                    continue
    except:
        pass
    
    return False

class DjangoServer:
    """Django server runner in thread"""
    def __init__(self):
        self.error = None
        self.started = False

    def run(self):
        try:
            import django
            django.setup()
            
            # CRITICAL FIX: Configure stdout/stderr for console=False mode
            # When console=False, sys.stdout and sys.stderr are None
            # Django needs these to be valid file-like objects
            if sys.stdout is None:
                sys.stdout = open(os.devnull, 'w')
            if sys.stderr is None:
                sys.stderr = open(os.devnull, 'w')
            
            self.started = True

            from django.core.management import execute_from_command_line
            sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload', '--insecure']
            execute_from_command_line(sys.argv)
        except SystemExit:
            pass  # Normal Django exit
        except Exception as e:
            self.error = f"{e}\n{traceback.format_exc()}"

class DjangoAppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Dhavant Croissance")
        self.root.geometry("650x600")
        self.root.resizable(False, False)
        self.center_window()

        self.server_thread = None
        self.server = DjangoServer()
        self.temp_dir = None

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(100, self.start_server)

    def center_window(self):
        self.root.update_idletasks()
        w, h = 650, 600
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2563EB", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header = ttk.Frame(self.root, padding="15")
        header.pack(fill=tk.X)
        header.place(in_=header_frame, relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(header, text="⛪ Dhavant Croissance", font=("Segoe UI", 18, "bold")).pack()
        ttk.Label(header, text="Gestion d'église professionnelle", font=("Segoe UI", 10), foreground="#666666").pack()

        # Status
        self.status_var = tk.StringVar(value="🔄 Initialisation en cours...")
        status_frame = tk.Frame(self.root, bg="#F3F4F6", height=40)
        status_frame.pack(fill=tk.X, pady=5)
        status_frame.pack_propagate(False)
        
        status_lbl = tk.Label(status_frame, textvariable=self.status_var, 
                             font=("Segoe UI", 11, "bold"), bg="#F3F4F6", fg="#1F2937")
        status_lbl.pack(pady=8)

        # Progress
        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=580)
        self.progress.pack(pady=8, padx=20)
        self.progress.start()

        # Logs
        log_frame = ttk.LabelFrame(self.root, text="📋 Journal d'activité", padding="8")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.log_text = tk.Text(log_frame, height=12, font=("Consolas", 9),
                                 state=tk.DISABLED, bg="#F9FAFB", wrap=tk.WORD,
                                 borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#F3F4F6")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        self.btn_open = ttk.Button(btn_frame, text="🌐 Ouvrir le navigateur",
                                    command=self.open_browser, state=tk.DISABLED)
        self.btn_open.pack(pady=5, fill=tk.X)
        
        ttk.Button(btn_frame, text="🔄 Redémarrer", command=self.restart_server).pack(pady=5, fill=tk.X)
        ttk.Button(btn_frame, text="❌ Fermer l'application", command=self.on_closing).pack(pady=5, fill=tk.X)

        # Footer
        footer = tk.Frame(self.root, bg="#F3F4F6")
        footer.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(footer, text="📍 Dhavant Croissance disponible sur: http://127.0.0.1:8000",
                  font=("Segoe UI", 9), foreground="#6B7280", background="#F3F4F6").pack()
        
        ttk.Label(footer, text="💡 Le navigateur s'ouvrira automatiquement",
                  font=("Segoe UI", 8), foreground="#9CA3AF", background="#F3F4F6").pack()

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"> {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def extract_files(self):
        """Extract files from PyInstaller bundle"""
        if not getattr(sys, 'frozen', False):
            return os.path.dirname(os.path.abspath(__file__))

        bundle_dir = sys._MEIPASS
        self.temp_dir = tempfile.mkdtemp(prefix='church_')
        self.log(f"📁 Dossier temporaire créé")

        items = ['manage.py', 'church', 'core', 'templates', 'static', 'staticfiles', 'db.sqlite3']
        for item in items:
            src = os.path.join(bundle_dir, item)
            dst = os.path.join(self.temp_dir, item)
            if os.path.exists(src):
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                self.log(f"  ✓ {item}")
            else:
                self.log(f"  ⚠ {item} non trouvé")

        return self.temp_dir

    def start_server(self):
        try:
            self.log("🚀 Démarrage de l'application...")

            # Get working directory
            if getattr(sys, 'frozen', False):
                app_dir = self.extract_files()
                self.log("📦 Mode: Exécutable")
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
                self.log("📝 Mode: Développement")

            os.chdir(app_dir)
            self.log(f"📂 Dossier: {app_dir}")

            # Add to Python path
            if app_dir not in sys.path:
                sys.path.insert(0, app_dir)
            self.log("📚 Chemins Python mis à jour")

            # Verify files
            if not os.path.exists('manage.py'):
                raise FileNotFoundError("manage.py non trouvé!")
            self.log("✓ manage.py trouvé")

            if not os.path.exists('church'):
                raise FileNotFoundError("Dossier church non trouvé!")
            self.log("✓ Dossier church trouvé")

            # Check port
            if is_port_in_use(8000):
                self.log("⚠️  Port 8000 déjà utilisé, tentative de libération...")
                # Give some time for port to be freed
                time.sleep(2)
            
            # Start Django thread
            self.log("⏳ Chargement de Django...")
            self.server_thread = threading.Thread(target=self.server.run, daemon=True)
            self.server_thread.start()

            # Monitor startup
            self.root.after(1000, self._check_startup)

        except Exception as e:
            self.status_var.set(f"❌ Erreur au démarrage")
            self.progress.stop()
            self.log(f"❌ ERREUR: {e}")
            self.log(traceback.format_exc())

    def _check_startup(self):
        # Check for thread errors
        if self.server.error:
            self.status_var.set("❌ Erreur Django")
            self.progress.stop()
            self.log(f"❌ Erreur Django: {self.server.error}")
            return

        # Check if Django started
        if self.server.started and is_port_in_use(8000):
            self.status_var.set("✅ Serveur prêt ! Ouverture du navigateur...")
            self.progress.stop()
            self.btn_open.config(state=tk.NORMAL)
            self.log("✅ Serveur Django démarré sur port 8000")
            self.log("🌐 Ouverture automatique du navigateur...")
            
            # Auto-open browser after short delay
            self.root.after(1500, self.open_browser)
        else:
            if not hasattr(self, '_tries'):
                self._tries = 0
            self._tries += 1

            if self._tries < 60:  # 30 seconds max
                self.root.after(500, self._check_startup)
            else:
                self.status_var.set("❌ Délai dépassé")
                self.progress.stop()
                self.log("❌ Timeout: serveur non répondant")
                if not self.server.started:
                    self.log("⚠️  Django n'a pas démarré - vérifiez les imports")

    def open_browser(self):
        url = "http://127.0.0.1:8000"
        self.log(f"🌐 Tentative d'ouverture: {url}")
        
        success = open_browser_url(url)
        
        if success:
            self.status_var.set("🌐 Navigateur ouvert avec succès")
            self.log("✅ Navigateur ouvert")
        else:
            self.status_var.set("⚠️  Ouvrez manuellement: http://127.0.0.1:8000")
            self.log("⚠️  Échec ouverture auto - ouvrez manuellement")

    def restart_server(self):
        self.log("🔄 Redémarrage du serveur...")
        self.status_var.set("🔄 Redémarrage...")
        self.progress.start()
        self.btn_open.config(state=tk.DISABLED)
        self._tries = 0
        
        # Restart Django thread
        self.server = DjangoServer()
        self.server_thread = threading.Thread(target=self.server.run, daemon=True)
        self.server_thread.start()
        
        self.root.after(1000, self._check_startup)

    def on_closing(self):
        self.status_var.set("⏹ Arrêt en cours...")
        self.log("🔄 Fermeture de l'application...")

        if self.temp_dir:
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.log("✓ Dossier temporaire nettoyé")
            except:
                pass

        self.log("✓ Application fermée")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon if available
    try:
        root.iconbitmap(default='church.ico')
    except:
        pass
    
    # Set app title
    root.title("Dhavant Croissance - Gestion d'église")
    
    # Launch the app
    DjangoAppLauncher(root)
    root.mainloop()
