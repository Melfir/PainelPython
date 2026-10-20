# Hardware Monitor: Visibilidade sobre o Sistema 🚀

Um projeto em Python para monitorar o hardware e o desempenho do sistema em tempo real, com coleta de telemetria e apresentação em uma interface moderna e responsiva inspirada no visual do Coresmonitor.

O objetivo é facilitar a leitura de informações críticas como CPU, memória, disco, rede, GPU e processos em execução, tudo em uma experiência visual clara e dinâmica.

---

## ✨ Funcionalidades

- Identificação automática de hardware:
  - Modelo do processador (CPU)
  - Núcleos físicos e threads
  - Memória RAM instalada, frequência e fabricante
  - GPU dedicada e integrada com VRAM via CIM/WMI no Windows

- Métricas em tempo real (atualização a cada 1 segundo):
  - Uso global da CPU
  - Uso individual por core/thread
  - Memória RAM em uso, disponível e virtual
  - Leitura e escrita de disco em MB/s
  - Ocupação de partições
  - Tráfego de rede em MB/s e total acumulado
  - Temperatura estimada e frequência do clock
  - Top 5 processos mais ativos do sistema

- Interface visual:
  - Tema escuro futurista
  - Indicadores radiais dinâmicos em SVG
  - Dock inferior com visual glassmorphism
  - Exportação instantânea dos dados em formato JSON

---

## 🧩 Requisitos

- Python 3.9+
- Windows 10/11 (recomendado para suporte completo de WMI/CIM)
- Navegador moderno
- Permissões adequadas para leitura de algumas informações do sistema

### Dependências

O projeto utiliza bibliotecas como:

- `psutil`
- `wmi` (quando necessário para coleta avançada de hardware no Windows)
- `flask` (para o servidor web da aplicação)

Instale as dependências com:

```powershell
pip install psutil wmi flask
```

---

## 📁 Estrutura do Projeto

```text
PainelPython/
├── app.py             # Servidor HTTP e coleta de métricas em Python
├── index.html         # Interface web do painel
├── index.css          # Estilos do tema escuro e efeitos visuais
├── app.js             # Lógica cliente para polling e animações
├── gui_desktop.py     # Versão desktop em Tkinter
├── iniciar.bat        # Inicializador rápido para Windows
├── README.md          # Documentação do projeto
└── LICENSE            # Caso exista no projeto
```

---

## ⚙️ Como Executar

### 1) Painel Web (recomendado)

No terminal PowerShell:

```powershell
py app.py
```

A aplicação abrirá automaticamente no navegador padrão em:

```text
http://localhost:5000
```

### 2) Executável rápido

Dê um duplo clique em:

```text
iniciar.bat
```

### 3) Versão desktop (opcional)

```powershell
py gui_desktop.py
```

---

## 🛠️ Como Funciona

A aplicação coleta dados do sistema em intervalos curtos usando `psutil` e, no Windows, integrações específicas como CIM/WMI para obter informações mais detalhadas sobre hardware e componentes.

Esses dados são enviados ao navegador por meio de um servidor HTTP e atualizados em tempo real na interface, permitindo uma leitura visual e dinâmica dos indicadores.

---

## 📊 Observações Importantes

- A atualização a cada segundo pode aumentar o consumo de CPU em máquinas mais antigas.
- Algumas métricas podem variar conforme:
  - Sistema operacional
  - Drivers instalados
  - Hardware específico
  - Permissões do usuário
- Informações de temperatura e detalhes de GPU dependem do suporte do sistema e do fabricante.

---

## 🧪 Troubleshooting

### O painel não abre

- Verifique se o Python está instalado corretamente.
- Confirme se todas as dependências foram instaladas.
- Tente rodar:

```powershell
python --version
pip install psutil wmi flask
```

### Erro ao importar bibliotecas

Instale manualmente:

```powershell
pip install psutil
pip install wmi
pip install flask
```

### Problemas com temperatura ou GPU

Algumas informações podem não estar disponíveis em máquinas específicas, em sistemas com suporte limitado ou em configurações de hardware diferentes.

---

## 🚀 Melhorias Futuras

- Adicionar gráficos históricos
- Exportação em CSV
- Suporte para Linux/macOS
- Alertas de uso crítico
- Melhor gerenciamento de desempenho da interface
- Modo de monitoramento em segundo plano

---

## 🤝 Contribuição

Contribuições são bem-vindas. Se quiser melhorar o projeto:

1. Faça um fork
2. Crie uma branch para sua feature
3. Faça suas alterações
4. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob uma licença apropriada. Consulte o arquivo `LICENSE` para mais detalhes, caso exista no repositório.

---

## 📝 Resumo

O Hardware Monitor é uma ferramenta visual para acompanhar o comportamento do sistema em tempo real, ideal para monitoramento local, análise de desempenho e visualização gráfica de recursos do computador.
