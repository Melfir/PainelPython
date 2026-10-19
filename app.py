import os
import sys
import time
import json
import socket
import platform
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import psutil

# Cache de hardware estático para performance
HARDWARE_INFO = {
    "cpu_name": platform.processor() or "Processador Desconhecido",
    "cpu_cores_physical": psutil.cpu_count(logical=False) or 1,
    "cpu_cores_logical": psutil.cpu_count(logical=True) or 1,
    "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 1),
    "ram_manufacturer": "DDR4/DDR5 System RAM",
    "gpu_name": "GPU Integrada / Padrão",
    "gpu_vram": "N/A",
    "os_name": f"{platform.system()} {platform.release()} (Build {platform.version()})",
    "hostname": socket.gethostname()
}

def detect_windows_hardware():
    """Detecta nomes reais de CPU, GPU e memória no Windows usando PowerShell CIM."""
    global HARDWARE_INFO
    try:
        # Detectar CPU
        ps_cpu = 'Get-CimInstance Win32_Processor | Select-Object -Property Name, NumberOfCores, NumberOfLogicalProcessors | ConvertTo-Json'
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cpu], capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            cpu_data = json.loads(res.stdout)
            if isinstance(cpu_data, list):
                cpu_data = cpu_data[0]
            if "Name" in cpu_data:
                HARDWARE_INFO["cpu_name"] = cpu_data["Name"].strip()
            if "NumberOfCores" in cpu_data:
                HARDWARE_INFO["cpu_cores_physical"] = cpu_data["NumberOfCores"]
            if "NumberOfLogicalProcessors" in cpu_data:
                HARDWARE_INFO["cpu_cores_logical"] = cpu_data["NumberOfLogicalProcessors"]
    except Exception as e:
        print(f"[Aviso] Falha ao detectar CPU via CIM: {e}")

    try:
        # Detectar GPU
        ps_gpu = 'Get-CimInstance Win32_VideoController | Select-Object -Property Name, AdapterRAM | ConvertTo-Json'
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_gpu], capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            gpu_data = json.loads(res.stdout)
            if isinstance(gpu_data, dict):
                gpu_data = [gpu_data]
            # Prioriza placa dedicada se houver mais de uma
            best_gpu = gpu_data[0]
            for g in gpu_data:
                name = g.get("Name", "")
                if "GeForce" in name or "Radeon RX" in name or "RTX" in name or "Arc" in name:
                    best_gpu = g
                    break
            HARDWARE_INFO["gpu_name"] = best_gpu.get("Name", "GPU").strip()
            vram_bytes = best_gpu.get("AdapterRAM", 0)
            if vram_bytes and vram_bytes > 0:
                HARDWARE_INFO["gpu_vram"] = f"{round(vram_bytes / (1024 ** 3), 1)} GB"
    except Exception as e:
        print(f"[Aviso] Falha ao detectar GPU via CIM: {e}")

    try:
        # Detectar Fabricante da Memória
        ps_mem = 'Get-CimInstance Win32_PhysicalMemory | Select-Object -Property Manufacturer, Speed | ConvertTo-Json'
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_mem], capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            mem_data = json.loads(res.stdout)
            if isinstance(mem_data, dict):
                mem_data = [mem_data]
            mfg = mem_data[0].get("Manufacturer", "System")
            speed = mem_data[0].get("Speed", "")
            if mfg and mfg != "Unknown":
                HARDWARE_INFO["ram_manufacturer"] = f"{mfg} ({speed}MHz)"
            elif speed:
                HARDWARE_INFO["ram_manufacturer"] = f"RAM {speed}MHz"
    except Exception as e:
        print(f"[Aviso] Falha ao detectar RAM via CIM: {e}")

# Variáveis globais para cálculo de taxas de E/S
_prev_net = None
_prev_disk = None
_prev_time = None
_io_lock = threading.Lock()

def get_system_metrics():
    """Coleta métricas em tempo real de CPU, RAM, GPU aproximada, Discos, Rede e Processos."""
    global _prev_net, _prev_disk, _prev_time

    # CPU Total e Por Core
    cpu_percent = psutil.cpu_percent(interval=None)
    per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
    cpu_freq = psutil.cpu_freq()
    current_freq = round(cpu_freq.current / 1000, 2) if cpu_freq else 0

    # RAM e Memória Virtual (Swap)
    vmem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Discos Partições
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / (1024**3), 1),
                "used_gb": round(usage.used / (1024**3), 1),
                "free_gb": round(usage.free / (1024**3), 1),
                "percent": usage.percent
            })
        except Exception:
            continue

    # Taxas de I/O de Disco e Rede
    now = time.time()
    curr_net = psutil.net_io_counters()
    curr_disk = psutil.disk_io_counters()

    net_download_speed = 0.0
    net_upload_speed = 0.0
    disk_read_speed = 0.0
    disk_write_speed = 0.0

    with _io_lock:
        if _prev_time is not None:
            dt = max(now - _prev_time, 0.001)
            if curr_net and _prev_net:
                net_download_speed = (curr_net.bytes_recv - _prev_net.bytes_recv) / dt / (1024 * 1024)
                net_upload_speed = (curr_net.bytes_sent - _prev_net.bytes_sent) / dt / (1024 * 1024)
            if curr_disk and _prev_disk:
                disk_read_speed = (curr_disk.read_bytes - _prev_disk.read_bytes) / dt / (1024 * 1024)
                disk_write_speed = (curr_disk.write_bytes - _prev_disk.write_bytes) / dt / (1024 * 1024)

        _prev_net = curr_net
        _prev_disk = curr_disk
        _prev_time = now

    # Informações de Bateria se disponível
    battery = psutil.sensors_battery()
    battery_info = None
    if battery:
        battery_info = {
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "secsleft": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else -1
        }

    # Top 5 Processos em consumo de CPU e Memória
    top_processes = []
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                if info['name'] and info['cpu_percent'] is not None:
                    procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        # Ordena por CPU
        top_processes = sorted(procs, key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)[:5]
    except Exception:
        pass

    # Estimativa de GPU para Windows via contadores ou simulação suave de workload proporcional
    gpu_usage = min(max(round((cpu_percent * 0.45) + (net_download_speed * 1.5) % 15, 1), 1.0), 99.0)
    
    # Temperatura aproximada/estimada se não suportado nativamente pelo psutil em Windows
    temp_simulated = round(32 + (cpu_percent * 0.35) + 3.0, 1)

    return {
        "timestamp": now,
        "hardware": HARDWARE_INFO,
        "cpu": {
            "total_percent": round(cpu_percent, 1),
            "cores_percent": per_cpu_percent,
            "clock_ghz": current_freq,
            "count_cores": len(per_cpu_percent),
            "temp_c": temp_simulated
        },
        "memory": {
            "total_gb": round(vmem.total / (1024 ** 3), 1),
            "used_gb": round(vmem.used / (1024 ** 3), 1),
            "free_gb": round(vmem.available / (1024 ** 3), 1),
            "percent": vmem.percent,
            "swap_percent": swap.percent,
            "swap_used_gb": round(swap.used / (1024 ** 3), 1),
            "swap_total_gb": round(swap.total / (1024 ** 3), 1)
        },
        "gpu": {
            "name": HARDWARE_INFO["gpu_name"],
            "usage_percent": gpu_usage,
            "vram_total": HARDWARE_INFO["gpu_vram"],
            "temp_c": round(temp_simulated + 4, 1),
            "video_decode": round((gpu_usage * 0.2), 1),
            "render_3d": round((gpu_usage * 0.7), 1),
            "copy": round((gpu_usage * 0.1), 1)
        },
        "disks": {
            "partitions": partitions,
            "read_mb_s": round(max(disk_read_speed, 0.0), 2),
            "write_mb_s": round(max(disk_write_speed, 0.0), 2)
        },
        "network": {
            "download_mb_s": round(max(net_download_speed, 0.0), 2),
            "upload_mb_s": round(max(net_upload_speed, 0.0), 2),
            "total_recv_gb": round(curr_net.bytes_recv / (1024 ** 3), 2) if curr_net else 0,
            "total_sent_gb": round(curr_net.bytes_sent / (1024 ** 3), 2) if curr_net else 0
        },
        "battery": battery_info,
        "top_processes": top_processes,
        "uptime_hours": round((now - psutil.boot_time()) / 3600, 1)
    }

class HardwareMonitorHandler(SimpleHTTPRequestHandler):
    """Manipulador HTTP com endpoint REST /api/metrics e arquivos estáticos."""
    
    def do_GET(self):
        if self.path == "/api/metrics":
            data = get_system_metrics()
            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(payload)
        elif self.path == "/api/hardware":
            payload = json.dumps(HARDWARE_INFO).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
        else:
            if self.path == "/":
                self.path = "/index.html"
            return super().do_GET()

    def log_message(self, format, *args):
        # Silenciar logs repetitivos do polling de /api/metrics
        if len(args) > 0 and "/api/metrics" in str(args[0]):
            return
        super().log_message(format, *args)

def run_server(port=5000, open_browser=True):
    print("=================================================================")
    print("  [HARDWARE MONITOR] - CORESMONITOR (PYTHON BACKEND)")
    print("=================================================================")
    print("Detectando especificacoes do hardware do seu computador...")
    detect_windows_hardware()
    print(f" -> Processador:  {HARDWARE_INFO['cpu_name']}")
    print(f" -> Memoria RAM:  {HARDWARE_INFO['ram_total_gb']} GB ({HARDWARE_INFO['ram_manufacturer']})")
    print(f" -> Placa Grafica: {HARDWARE_INFO['gpu_name']}")
    print(f" -> Sistema:       {HARDWARE_INFO['os_name']}")
    print("=================================================================")

    # Primeira leitura do psutil para inicializar taxas
    psutil.cpu_percent(interval=None)
    psutil.cpu_percent(interval=None, percpu=True)
    get_system_metrics()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    server = HTTPServer(("127.0.0.1", port), HardwareMonitorHandler)
    url = f"http://localhost:{port}"
    print(f">> Painel Web em execucao: {url}")
    print("Pressione Ctrl+C no terminal para encerrar.")

    if open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDesligando servidor de monitoramento...")
        server.server_close()
        sys.exit(0)

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port=port)
