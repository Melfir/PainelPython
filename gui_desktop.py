import tkinter as tk
from tkinter import ttk
import threading
import time
import psutil

# Tenta importar CIM ou dados básicos
try:
    import app
    has_app_backend = True
except Exception:
    has_app_backend = False

class HardwareMonitorTkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hardware Monitor - Desktop Widget")
        self.root.geometry("450x600")
        self.root.configure(bg="#13161c")

        # Título
        title_frame = tk.Frame(root, bg="#13161c", pady=12)
        title_frame.pack(fill="x")
        
        lbl_title = tk.Label(title_frame, text="⚡ HARDWARE MONITOR", font=("Helvetica", 14, "bold"), fg="#00d2ff", bg="#13161c")
        lbl_title.pack()

        self.lbl_cpu_name = tk.Label(title_frame, text="Detectando hardware...", font=("Helvetica", 9), fg="#8b949e", bg="#13161c")
        self.lbl_cpu_name.pack()

        # Container Principal
        container = tk.Frame(root, bg="#13161c", padx=20, pady=10)
        container.pack(fill="both", expand=True)

        # CPU Card
        self.create_card(container, "CPU Usage", "lbl_cpu_val", "bar_cpu", "#00d2ff")
        
        # RAM Card
        self.create_card(container, "RAM Usage", "lbl_ram_val", "bar_ram", "#00e5ff")

        # GPU Card
        self.create_card(container, "GPU Estimation", "lbl_gpu_val", "bar_gpu", "#e02478")

        # Rede & Discos Box
        stats_frame = tk.LabelFrame(container, text=" I/O em Tempo Real ", fg="#ffffff", bg="#181b22", font=("Helvetica", 9, "bold"), padx=12, pady=10)
        stats_frame.pack(fill="x", pady=10)

        self.lbl_disk = tk.Label(stats_frame, text="Disco: R: 0.0 MB/s | W: 0.0 MB/s", font=("Consolas", 9), fg="#8b949e", bg="#181b22")
        self.lbl_disk.pack(anchor="w", pady=2)

        self.lbl_net = tk.Label(stats_frame, text="Rede:  ↓ 0.0 MB/s | ↑ 0.0 MB/s", font=("Consolas", 9), fg="#8b949e", bg="#181b22")
        self.lbl_net.pack(anchor="w", pady=2)

        # Botão para abrir o Web Dashboard Completo
        btn_open_web = tk.Button(container, text="🌐 Abrir Painel Web Completo", font=("Helvetica", 10, "bold"),
                                 bg="#0070f3", fg="#ffffff", activebackground="#0051b3", activeforeground="#ffffff",
                                 relief="flat", pady=8, cursor="hand2", command=self.open_web)
        btn_open_web.pack(fill="x", pady=12)

        # Iniciar thread de atualização
        self.running = True
        self.thread = threading.Thread(target=self.update_loop, daemon=True)
        self.thread.start()

    def create_card(self, parent, title, label_attr, bar_attr, color):
        frame = tk.Frame(parent, bg="#181b22", padx=12, pady=10)
        frame.pack(fill="x", pady=6)

        header = tk.Frame(frame, bg="#181b22")
        header.pack(fill="x")

        tk.Label(header, text=title, font=("Helvetica", 10, "bold"), fg="#f0f3f6", bg="#181b22").pack(side="left")
        
        val_label = tk.Label(header, text="0%", font=("Helvetica", 10, "bold"), fg=color, bg="#181b22")
        val_label.pack(side="right")
        setattr(self, label_attr, val_label)

        # Barra
        bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate")
        bar.pack(fill="x", pady=(6, 0))
        setattr(self, bar_attr, bar)

    def open_web(self):
        import webbrowser
        webbrowser.open("http://localhost:5000")

    def update_loop(self):
        while self.running:
            try:
                if has_app_backend:
                    data = app.get_system_metrics()
                    cpu = data["cpu"]["total_percent"]
                    ram = data["memory"]["percent"]
                    gpu = data["gpu"]["usage_percent"]
                    read_s = data["disks"]["read_mb_s"]
                    write_s = data["disks"]["write_mb_s"]
                    down_s = data["network"]["download_mb_s"]
                    up_s = data["network"]["upload_mb_s"]
                    cpu_name = data["hardware"]["cpu_name"]
                else:
                    cpu = psutil.cpu_percent()
                    ram = psutil.virtual_memory().percent
                    gpu = 10.0
                    read_s, write_s = 0.0, 0.0
                    down_s, up_s = 0.0, 0.0
                    cpu_name = "Sistema Operacional"

                def apply():
                    self.lbl_cpu_name.config(text=cpu_name[:45])
                    getattr(self, "lbl_cpu_val").config(text=f"{cpu:.1f}%")
                    getattr(self, "bar_cpu")["value"] = cpu

                    getattr(self, "lbl_ram_val").config(text=f"{ram:.1f}%")
                    getattr(self, "bar_ram")["value"] = ram

                    getattr(self, "lbl_gpu_val").config(text=f"{gpu:.1f}%")
                    getattr(self, "bar_gpu")["value"] = gpu

                    self.lbl_disk.config(text=f"Disco: R: {read_s:.1f} MB/s | W: {write_s:.1f} MB/s")
                    self.lbl_net.config(text=f"Rede:  ↓ {down_s:.1f} MB/s | ↑ {up_s:.1f} MB/s")

                self.root.after(0, apply)
            except Exception:
                pass
            time.sleep(1.0)

def launch_gui():
    root = tk.Tk()
    HardwareMonitorTkApp(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
