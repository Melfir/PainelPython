// Constantes e referências aos elementos do DOM
const CIRCLE_CIRCUMFERENCE = 301.6; // 2 * PI * 48
let lastMetricsData = null;

function setRadialProgress(circleId, percent) {
  const circle = document.getElementById(circleId);
  if (!circle) return;
  const clamped = Math.min(Math.max(percent, 0), 100);
  const offset = CIRCLE_CIRCUMFERENCE - (clamped / 100) * CIRCLE_CIRCUMFERENCE;
  circle.style.strokeDashoffset = offset;
}

function scrollToCard(id) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    document.querySelectorAll('.dock-item').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
  }
}

// Atualização de elementos na tela
function updateDashboard(data) {
  lastMetricsData = data;

  // Informações Globais do Host
  if (data.hardware) {
    document.getElementById('sys-host').textContent = data.hardware.hostname || 'Localhost';
    document.getElementById('sys-os').textContent = data.hardware.os_name || 'Windows';
    document.getElementById('cpu-name').textContent = data.hardware.cpu_name || 'Processador';
    document.getElementById('ram-specs').textContent = `${data.hardware.ram_total_gb} GB • ${data.hardware.ram_manufacturer}`;
    document.getElementById('gpu-name').textContent = data.hardware.gpu_name || 'Placa de Vídeo';
    document.getElementById('gpu-vram-text').textContent = data.hardware.gpu_vram || 'Dedicada/Compartilhada';
    document.getElementById('cpu-phys-cores').textContent = `${data.hardware.cpu_cores_physical} Cores / ${data.hardware.cpu_cores_logical} Threads`;
  }
  document.getElementById('sys-uptime').textContent = `${data.uptime_hours}h`;

  // CPU
  const cpuPercent = data.cpu.total_percent;
  document.getElementById('cpu-val-center').textContent = Math.round(cpuPercent);
  setRadialProgress('cpu-circle', cpuPercent);
  document.getElementById('cpu-freq-text').textContent = `${data.cpu.clock_ghz.toFixed(2)} GHz`;
  document.getElementById('cpu-temp-avg').textContent = `Avg. temperature: ${Math.round(data.cpu.temp_c)} °C`;
  document.getElementById('cpu-temp-text').textContent = `${Math.round(data.cpu.temp_c)} °C`;
  
  // Dual temperature gradient bars
  const tempRatio = Math.min(Math.max(data.cpu.temp_c / 90, 0.2), 1.0);
  document.getElementById('cpu-temp-blue').style.width = `${Math.round(tempRatio * 60)}%`;
  document.getElementById('cpu-temp-pink').style.width = `${Math.round(tempRatio * 40)}%`;

  // CPU Cores Rows
  const coresContainer = document.getElementById('cpu-cores-list');
  if (coresContainer && data.cpu.cores_percent) {
    let coresHtml = '';
    // Mostrar até 6 cores na visualização rápida para manter harmonia visual
    const countToShow = Math.min(data.cpu.cores_percent.length, 6);
    for (let i = 0; i < countToShow; i++) {
      const val = Math.round(data.cpu.cores_percent[i]);
      coresHtml += `
        <div class="core-row">
          <span class="core-label">Core #${i + 1}</span>
          <div class="core-bar-wrapper">
            <div class="core-bar-fill" style="width: ${val}%"></div>
          </div>
          <span class="core-val">${val}%</span>
        </div>
      `;
    }
    coresContainer.innerHTML = coresHtml;
  }

  // RAM
  const ramPercent = data.memory.percent;
  document.getElementById('ram-val-center').textContent = Math.round(ramPercent);
  setRadialProgress('ram-circle', ramPercent);
  document.getElementById('ram-used').textContent = `${data.memory.used_gb} GB`;
  document.getElementById('ram-free').textContent = `${data.memory.free_gb} GB`;
  document.getElementById('swap-val').textContent = `${Math.round(data.memory.swap_percent)}%`;
  document.getElementById('swap-bar').style.width = `${data.memory.swap_percent}%`;

  // GPU
  const gpuPercent = data.gpu.usage_percent;
  document.getElementById('gpu-val-center').textContent = Math.round(gpuPercent);
  setRadialProgress('gpu-circle', gpuPercent);
  document.getElementById('gpu-3d-bar').style.width = `${Math.min(data.gpu.render_3d * 2.5, 100)}%`;
  document.getElementById('gpu-3d-val').textContent = `${data.gpu.render_3d}%`;
  document.getElementById('gpu-dec-bar').style.width = `${Math.min(data.gpu.video_decode * 3, 100)}%`;
  document.getElementById('gpu-dec-val').textContent = `${data.gpu.video_decode}%`;
  document.getElementById('gpu-copy-bar').style.width = `${Math.min(data.gpu.copy * 3, 100)}%`;
  document.getElementById('gpu-copy-val').textContent = `${data.gpu.copy}%`;

  // Armazenamento
  document.getElementById('disk-read-speed').textContent = `${data.disks.read_mb_s.toFixed(2)} MB/s`;
  document.getElementById('disk-write-speed').textContent = `${data.disks.write_mb_s.toFixed(2)} MB/s`;

  const partContainer = document.getElementById('disk-partitions-list');
  if (partContainer && data.disks.partitions) {
    let partHtml = '';
    data.disks.partitions.forEach(p => {
      partHtml += `
        <div style="background: rgba(255,255,255,0.02); padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
            <span><strong>${p.device}</strong> (${p.mountpoint})</span>
            <span>${p.used_gb} GB / ${p.total_gb} GB (${Math.round(p.percent)}%)</span>
          </div>
          <div class="linear-track">
            <div class="linear-fill disk" style="width: ${p.percent}%"></div>
          </div>
        </div>
      `;
    });
    partContainer.innerHTML = partHtml;
  }

  // Rede
  document.getElementById('net-down-speed').textContent = `${data.network.download_mb_s.toFixed(2)} MB/s`;
  document.getElementById('net-up-speed').textContent = `${data.network.upload_mb_s.toFixed(2)} MB/s`;
  document.getElementById('net-total-recv').textContent = `${data.network.total_recv_gb} GB`;
  document.getElementById('net-total-sent').textContent = `${data.network.total_sent_gb} GB`;

  // Processos Ativos
  const procContainer = document.getElementById('process-list-container');
  if (procContainer && data.top_processes && data.top_processes.length > 0) {
    let procHtml = '';
    data.top_processes.forEach(p => {
      procHtml += `
        <div class="process-item">
          <span class="process-name" title="${p.name} (PID: ${p.pid})">${p.name}</span>
          <span class="process-cpu">CPU: ${(p.cpu_percent || 0).toFixed(1)}%</span>
          <span class="process-mem">RAM: ${(p.memory_percent || 0).toFixed(1)}%</span>
        </div>
      `;
    });
    procContainer.innerHTML = procHtml;
  }

  // Indicador de Conexão
  const connPill = document.getElementById('conn-status');
  if (connPill) {
    connPill.innerHTML = '<span class="status-dot"></span><span>Conectado</span>';
  }
}

// Polling contínuo com fetch HTTP de alta velocidade a cada 1 segundo
async function fetchMetrics() {
  try {
    const res = await fetch('/api/metrics', { cache: 'no-store' });
    if (!res.ok) throw new Error('Falha na resposta HTTP');
    const data = await res.json();
    updateDashboard(data);
  } catch (err) {
    console.warn('Erro ao conectar com servidor Python:', err);
    const connPill = document.getElementById('conn-status');
    if (connPill) {
      connPill.innerHTML = '<span class="status-dot" style="background-color: #ff3366; box-shadow: 0 0 10px #ff3366;"></span><span style="color:#ff3366">Reconectando...</span>';
    }
  }
}

// Exportar métricas em formato JSON
document.getElementById('btn-export')?.addEventListener('click', () => {
  if (!lastMetricsData) return;
  const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(lastMetricsData, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", jsonStr);
  downloadAnchor.setAttribute("download", `hardware_telemetry_${Date.now()}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
});

// Inicialização imediata e loop a cada 1000ms
fetchMetrics();
setInterval(fetchMetrics, 1000);
