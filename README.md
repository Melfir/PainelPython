# Hardware Monitor: Visibilidade sobre o Sistema 🚀

Um projeto em **Python** voltado ao monitoramento de hardware em tempo real, explorando a coleta de telemetria do sistema e sua apresentação através de uma interface moderna e responsiva inspirada no **Coresmonitor**.

![Dashboard Preview](index.html)

---

## 🌟 Funcionalidades e Destaques

- **Identificação de Hardware Real**:
  - Detecção automática de modelo do Processador (**CPU**), Cores físicos e Threads.
  - Memória **RAM** instalada, frequência e fabricante.
  - Placa de Vídeo (**GPU**) dedicada e integrada com VRAM via CIM/WMI do Windows.
- **Métricas em Tempo Real (Atualização a cada 1s)**:
  - Consumo global de CPU e uso individual por Core/Thread.
  - Memória RAM em uso, disponível e memória swap/virtual.
  - Taxa de transferência de Disco (Leitura e Escrita em MB/s) e ocupação de partições.
  - Tráfego de Rede (Velocidade de Download e Upload em MB/s e tráfego acumulado).
  - Temperatura média estimada e frequência de clock.
  - Lista em tempo real dos **5 processos mais ativos** do sistema operacional.
- **Design de Alto Nível**:
  - Visual dark futurista fiel à referência do Coresmonitor.
  - Indicadores radiais dinâmicos (SVG Radial Gauges com gradientes neon).
  - Barra de navegação flutuante inferior (*Dock* com blur/glassmorphism).
  - Botão de exportação instantânea de telemetria em formato JSON.

---

## 📂 Estrutura do Projeto

```text
PainelPython/
├── app.py             # Servidor HTTP e coletor de métricas em Python (psutil + CIM)
├── index.html         # Interface web interativa do painel
├── index.css          # Estilização completa com tema escuro e efeitos visuais
├── app.js             # Lógica cliente para polling de 1s e animações dos gauges
├── gui_desktop.py     # Aplicativo desktop alternativo em Tkinter
├── iniciar.bat        # Inicializador rápido com dois cliques para Windows
└── README.md          # Documentação do projeto
```

---

## ⚡ Como Executar e Testar

### 1. Iniciar o Painel Web (Recomendado)
Execute no terminal PowerShell:
```powershell
py app.py
```
O painel abrirá automaticamente no seu navegador padrão em:
👉 **[http://localhost:5000](http://localhost:5000)**

### 2. Pelo arquivo executável rápido
Dê um duplo clique no arquivo [`iniciar.bat`](iniciar.bat).

### 3. Versão Widget Desktop (Opcional)
Se preferir uma janela desktop nativa:
```powershell
py gui_desktop.py
```
