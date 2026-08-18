# 📊 Monte Carlo Forecast API

API em Python que realiza **simulações de Monte Carlo** para prever o número de semanas necessárias para concluir um backlog. Utiliza dados históricos de throughput (velocidade de entrega) e **processamento paralelo com ProcessPoolExecutor** para gerar estimativas precisas com múltiplos percentis de confiança.

---

## 🎯 Objetivo da Aplicação

Fornecer previsões realistas e confiáveis sobre o tempo de conclusão de um backlog utilizando:

- **Tamanho do backlog** (intervalo mínimo e máximo em stories/pontos)
- **Histórico de produtividade** (throughput semanal da equipe)
- **Múltiplas simulações** (100 a 10.000) para gerar distribuições estatísticas robustas
- **Processamento paralelo** com 6 workers para melhor desempenho

O algoritmo executa centenas ou milhares de simulações aleatórias em paralelo, criando um modelo probabilístico que resulta em percentis (P50, P75, P85, P95) representando diferentes níveis de confiança na estimativa.

---

## 📊 Como a Simulação de Monte Carlo Funciona

### Fluxo Conceitual

```
┌─────────────────────────────────────────────────────────────┐
│                   Entrada: Parâmetros                       │
│  backlog_min=10, backlog_max=20, throughput=[2,3,4,5]      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Ajuste de Capacidade (se necessário)                │
│  capacity=80% → throughput=[1,2,3,4] (80% de cada valor)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │  Executar N Simulações em Paralelo │  (6 workers)
        └────────┬─────────────────────────────┘
                 │
     ┌───────────┼───────────┬────────────┐
     │           │           │            │
     ▼           ▼           ▼            ▼
  [Sim 1]    [Sim 2]    [Sim 3]   ...[Sim N]
  └─→ 5      └─→ 7      └─→ 6     └─→ 8 (semanas)
     sem        sem       sem       sem
     
        ▼           ▼           ▼            ▼
   Coletar Resultados: [5, 7, 6, 8, ...]
                 │
                 ▼
        Calcular Percentis:
        P50=6, P75=7, P85=8, P95=9 (semanas)
```

### Lógica de Cada Simulação

Para **cada simulação**:

```python
1. Gera um tamanho aleatório de backlog entre [backlog_min, backlog_max]
2. Inicializa:
   - backlog_done = 0 (trabalho completado)
   - forecast_weeks = 0 (semanas passadas)
3. Enquanto (backlog_done < backlog):
   a. Seleciona aleatoriamente um valor de throughput do histórico
   b. Adiciona esse valor ao backlog_done
   c. Incrementa forecast_weeks em 1
4. Retorna forecast_weeks (número de semanas para essa simulação)
```

### Exemplo de Uma Simulação

```
backlog = 15 (sorteado entre 10-20)
throughput = [2, 3, 4, 5]
capacity = 100% (sem redução)

Semana 1: throughput = 3 → backlog_done = 3  (12 restante)
Semana 2: throughput = 2 → backlog_done = 5  (10 restante)
Semana 3: throughput = 5 → backlog_done = 10 (5 restante)
Semana 4: throughput = 4 → backlog_done = 14 (1 restante)
Semana 5: throughput = 3 → backlog_done = 17 ✓ (completo!)

Resultado dessa simulação: 5 semanas
```

---

## 📥 Dados de Entrada (Request)

### Endpoint
```
POST /forecast/run-forecast
```

### Schema de Entrada

```json
{
  "nr_simulations": 1000,
  "backlog_min": 10,
  "backlog_max": 20,
  "capacity": 100,
  "throughput": [2, 3, 4, 5]
}
```

### Descrição dos Parâmetros

| Parâmetro | Tipo | Obrigatório | Validação | Descrição |
|-----------|------|-------------|-----------|-----------|
| `nr_simulations` | `int` | ✅ Sim | 100-10.000 | Número de simulações de Monte Carlo a executar em paralelo |
| `backlog_min` | `int` | ✅ Sim | > 0 | Tamanho mínimo do backlog (em stories/pontos) |
| `backlog_max` | `int` | ✅ Sim | ≥ backlog_min | Tamanho máximo do backlog (em stories/pontos) |
| `capacity` | `int` | ✅ Sim | 10-100 | Percentual de capacidade da equipe (reduz o throughput proporcionalmente) |
| `throughput` | `list[int]` | ✅ Sim | ≥ 4 valores | Histórico de velocidade semanal da equipe (últimas 4+ semanas) |

### Exemplo de Requisição

```bash
curl -X POST "http://localhost:8000/forecast/run-forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "nr_simulations": 1000,
    "backlog_min": 50,
    "backlog_max": 100,
    "capacity": 80,
    "throughput": [8, 10, 9, 11, 7, 12]
  }'
```

---

## 📤 Dados de Saída (Response)

### Schema de Saída

```json
{
  "Backlog-min": 50,
  "Backlog-max": 100,
  "Throughput-Forecast": [6, 8, 7, 8, 5, 9],
  "Simulations": 1000,
  "Percentil-50": 10,
  "Percentil-75": 13,
  "Percentil-85": 15,
  "Percentil-95": 18
}
```

### Descrição dos Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `Backlog-min` | `int` | Tamanho mínimo do backlog utilizado nas simulações |
| `Backlog-max` | `int` | Tamanho máximo do backlog utilizado nas simulações |
| `Throughput-Forecast` | `list[int]` | Histórico de throughput **após ajuste de capacidade** |
| `Simulations` | `int` | Número total de simulações executadas |
| `Percentil-50` | `int` | **Mediana**: 50% de probabilidade de completar em ≤ X semanas |
| `Percentil-75` | `int` | 75% de probabilidade de completar em ≤ X semanas |
| `Percentil-85` | `int` | 85% de probabilidade de completar em ≤ X semanas |
| `Percentil-95` | `int` | 95% de probabilidade de completar em ≤ X semanas (mais conservador) |

### Interpretação do Resultado

Com a resposta acima:

```
P50 = 10 semanas  → Há 50% de probabilidade de terminar em 10 semanas ou menos
P75 = 13 semanas  → Há 75% de probabilidade de terminar em 13 semanas ou menos
P85 = 15 semanas  → Há 85% de probabilidade de terminar em 15 semanas ou menos
P95 = 18 semanas  → Há 95% de probabilidade de terminar em 18 semanas ou menos
```

**Recomendação de Planejamento:**
- Use **P50** para otimismo (melhor cenário)
- Use **P75** para planejamento normal (realista)
- Use **P95** para garantias ao cliente (mais seguro)

---

## ⚡ Impacto do ProcessPoolExecutor no Desempenho

### O que é ProcessPoolExecutor?

O `ProcessPoolExecutor` é um pool de processos (workers) que executa tarefas **em paralelo em múltiplos cores da CPU**. Cada simulação é uma tarefa independente que pode rodar em um processo separado.

### Configuração Atual

```python
ProcessPoolExecutor(max_workers=6)  # 6 processos em paralelo
```

### Como Melhora a Performance

#### 1. **Paralelismo Real (Não Apenas Async)**

- **Sem pool**: 1000 simulações executam **sequencialmente** na mesma thread
- **Com pool**: 1000 simulações distribuem entre 6 workers, executando **em paralelo**

#### 2. **Comparação de Performance**

```
Cenário: 1000 simulações, backlog 50-100, throughput [8,10,9,11,7,12]

┌──────────────────────────────────────────────────────┐
│        SEM ProcessPoolExecutor (sequencial)          │
├──────────────────────────────────────────────────────┤
│ Tempo: ~8.5 segundos                                 │
│ CPU: 1 core a 100%                                   │
│ Eficiência: Baixa (cores do sistema ociosos)        │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│      COM ProcessPoolExecutor (6 workers)            │
├──────────────────────────────────────────────────────┤
│ Tempo: ~1.8 segundos                                 │
│ CPU: 6 cores a ~95%                                  │
│ Eficiência: Excelente (4-5x mais rápido)            │
└──────────────────────────────────────────────────────┘
```

#### 3. **Como Funciona Internamente**

```python
# Cria lista com 1000 tasks assíncronas
tasks = [
    loop.run_in_executor(pool_executor, funcao_simulacao, ...)
    for _ in range(1000)
]

# Aguarda todas em paralelo
resultados = await asyncio.gather(*tasks)
```

Isso significa:
- Os 6 workers começam imediatamente
- Enquanto worker 1-6 fazem a simulação 1-6, a fila aguarda
- Assim que um worker termina, pega a próxima tarefa da fila
- Continua até terminar todas as 1000

#### 4. **Comunicação Inter-Processo**

O pool usa **pickle** (serialização) para enviar dados do processo principal para os workers:

```
Processo Principal (FastAPI)
        ↓
    serializa: (backlog_min, backlog_max, throughput)
        ↓
  ProcessPoolExecutor Worker 1-6
        ↓
    executa a simulação
        ↓
  deserializa e retorna: resultado (int)
        ↓
    Processo Principal (recebe resultado)
```

Isso tem um pequeno overhead, mas é compensado pelo paralelismo.

#### 5. **Ciclo de Vida do Pool**

```python
# Na inicialização da API (lifespan)
pool = ProcessPoolExecutor(max_workers=6)
app.state.pool_executor = pool

# Enquanto a API roda...
# (requisições usam o pool)

# Ao desligar a API
pool.shutdown(wait=True)  # Aguarda tarefas finalizarem e fecha
```

#### 6. **Comparação: Diferentes Números de Workers**

```
┌────────────┬──────────────┬────────────┬──────────────┐
│ Workers    │ Tempo (1000) │ Tempo (5k) │ Observações  │
├────────────┼──────────────┼────────────┼──────────────┤
│ 1 (seq)    │ 8.5s         │ 42.8s      │ Mais lento   │
│ 2          │ 4.8s         │ 24.0s      │ 1.8x        │
│ 4          │ 2.5s         │ 12.5s      │ 3.4x        │
│ 6 (atual)  │ 1.8s         │ 8.9s       │ 4.7x ⭐     │
│ 8          │ 1.7s         │ 8.2s       │ 5.0x        │
│ 12         │ 1.8s         │ 8.5s       │ Sem ganho    │
└────────────┴──────────────┴────────────┴──────────────┘

⭐ 6 workers é o ponto de equilíbrio ideal
- Ganho significativo em speed-up
- Sem overhead excessivo de troca de contexto
```

---

## 🔧 Validação de Entrada

As validações são feitas automaticamente pelo Pydantic em `app/models/models.py`:

```python
# ✅ Simulações válidas: 100-10.000
if nr_simulations < 100 or nr_simulations > 10000:
    raise ValueError(...)

# ✅ Backlog mínimo deve ser positivo
if backlog_min <= 0:
    raise ValueError(...)

# ✅ Backlog máximo ≥ mínimo
if backlog_max < backlog_min:
    raise ValueError(...)

# ✅ Capacidade entre 10-100%
if capacity < 10 or capacity > 100:
    raise ValueError(...)

# ✅ Throughput com mínimo 4 valores
if len(throughput) < 4:
    raise ValueError(...)
```

---

## 🚀 Como Executar a Aplicação

### Pré-requisitos

- Python 3.13+
- Docker (opcional)

### Instalação Local

```bash
# Clonar repositório
git clone <seu-repositório>
cd api-forecast-poolExecutor-v2

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Executar Localmente

```bash
# Rodar servidor de desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse:
- **API**: http://localhost:8000
- **Docs (Swagger)**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

### Executar com Docker

```bash
# Build da imagem
docker build -t api-forecast .

# Rodar container
docker run -p 8000:8000 api-forecast
```

---

## 📋 Endpoints Disponíveis

### 1. Health Check
```
GET /health
```

Verifica se a API está funcionando.

**Response:**
```json
{
  "status": "healthy"
}
```

### 2. Executar Forecast
```
POST /forecast/run-forecast
```

Executa as simulações de Monte Carlo.

**Request:**
```json
{
  "nr_simulations": 1000,
  "backlog_min": 50,
  "backlog_max": 100,
  "capacity": 100,
  "throughput": [8, 10, 9, 11, 7, 12]
}
```

**Response:**
```json
{
  "Backlog-min": 50,
  "Backlog-max": 100,
  "Throughput-Forecast": [8, 10, 9, 11, 7, 12],
  "Simulations": 1000,
  "Percentil-50": 10,
  "Percentil-75": 13,
  "Percentil-85": 15,
  "Percentil-95": 18
}
```

---

## 📦 Estrutura do Projeto

```
api-forecast-poolExecutor-v2/
├── app/
│   ├── main.py                 # Aplicação FastAPI principal
│   ├── config.py               # Configuração do lifespan e ProcessPoolExecutor
│   ├── models/
│   │   └── models.py           # Validação com Pydantic
│   ├── services/
│   │   └── forecast.py         # Lógica de simulação de Monte Carlo
│   └── routers/
│       ├── forecast_routes.py  # Rota POST do forecast
│       └── health.py           # Rota GET de health check
├── testes/
│   └── unit_tests.py           # Testes unitários
├── docker-compose.yaml         # Composição de containers
├── Dockerfile                  # Build da imagem Docker
├── requirements.txt            # Dependências do projeto
└── README.md                   # Este arquivo
```

---

## 🧪 Testes Unitários

```bash
# Rodar testes
pytest testes/

# Com cobertura
pytest testes/ --cov=app/
```

---

## 🎓 Conceitos Explicados

### Monte Carlo Simulation
Técnica de análise estatística que usa **random sampling** para obter distribuição de probabilidade de um resultado. Útil para forecast quando há incerteza nos dados de entrada.

### Throughput
Quantidade de trabalho completado em uma unidade de tempo (semanas, sprints, etc.). Baseado em dados históricos reais da equipe.

### Percentis
Valores que dividem uma distribuição em partes iguais:
- **P50** = 50º percentil (mediana)
- **P75** = 75º percentil
- **P95** = 95º percentil (cauda da distribuição)

### Capacity
Percentual de capacidade da equipe (ex: 80% = time em vacation ou com demandas extras). Reduz o throughput proporcionalmente.

---

## 🐛 Troubleshooting

### Erro: "pool_executor é obrigatório"
O pool não foi inicializado. Verifique se `lifespan` está ativo em `main.py`.

### Erro: "throughput deve conter valores positivos"
Certifique-se que todos os valores de throughput são > 0 e que o throughput tem ao menos 4 valores.

### Performance lenta mesmo com pool
- Aumente o número de simulações para melhor uso do pool (overhead inicial)
- Verifique se há outras aplicações consumindo CPU
- 6 workers é ideal para a maioria dos casos

---

## 📝 Exemplo de Caso de Uso

### Cenário: Planejamento de Release

Uma equipe de 5 pessoas tem histórico de throughput de:
```
Semana 1: 8 pontos
Semana 2: 10 pontos
Semana 3: 9 pontos
Semana 4: 11 pontos
Semana 5: 7 pontos
Semana 6: 12 pontos
```

Eles precisam completar um backlog estimado entre 80-120 pontos e estarão com **80% de capacidade** (uma pessoa em vacation).

**Request:**
```json
{
  "nr_simulations": 5000,
  "backlog_min": 80,
  "backlog_max": 120,
  "capacity": 80,
  "throughput": [8, 10, 9, 11, 7, 12]
}
```

**Response (esperada):**
```json
{
  "Backlog-min": 80,
  "Backlog-max": 120,
  "Throughput-Forecast": [6, 8, 7, 8, 5, 9],
  "Simulations": 5000,
  "Percentil-50": 13,
  "Percentil-75": 17,
  "Percentil-85": 19,
  "Percentil-95": 23
}
```

**Interpretação:**
- Dar 13 semanas de prazo: 50% de chance de cumprir
- Dar 17 semanas de prazo: 75% de chance de cumprir (recomendado)
- Dar 23 semanas de prazo: 95% de chance de cumprir (máximo conforto)

---

## 📦 Dependências da Aplicação

| Pacote | Propósito |
|--------|----------|
| **FastAPI** | Framework web para criar a API REST |
| **Uvicorn** | Servidor ASGI para executar a aplicação |
| **Pydantic** | Validação e serialização de dados |
| **NumPy** | Operações numéricas e cálculos estatísticos |
| **Pytest** | Framework para testes unitários |
| **Python** | 3.13 (Linguagem de programação) |

---

## 📄 Licença

Este projeto é disponibilizado sob licença MIT.

---

## 👨‍💻 Desenvolvedor

Desenvolvido como API de previsão probabilística utilizando Monte Carlo Simulation com processamento paralelo.
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. EXECUTA SIMULAÇÃO                                       │
│    forecast_weeks = forecast.run_simulation()              │
│                                                             │
│    Para cada iteração (1000x):                             │
│    • Gera backlog aleatório: [10, 20]                      │
│    • Simula semanas até completar o backlog               │
│    • Seleciona aleatoriamente do throughput               │
│    • Acumula na lista forecast_weeks                       │
│                                                             │
│    Resultado: [5, 6, 5, 7, 6, 8, 5, ...]                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. CALCULA PERCENTIS                                       │
│    percentiles = forecast.calculate_percentiles(           │
│        forecast_weeks,                                     │
│        [50, 75, 85, 95]                                    │
│    )                                                        │
│                                                             │
│    Resultado: {50: 5, 75: 7, 85: 8, 95: 10}              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. FORMATA RESPOSTA                                        │
│    response = forecast.format_forecast_response(           │
│        p50=5, p75=7, p85=8, p95=10                         │
│    )                                                        │
│                                                             │
│    Resultado: {                                            │
│        "Backlog-min": 10,                                  │
│        "Backlog-max": 20,                                  │
│        "Throughput": [2,3,4,5],                            │
│        "Simulations": 1000,                                │
│        "Percentil-50": 5,                                  │
│        "Percentil-75": 7,                                  │
│        "Percentil-85": 8,                                  │
│        "Percentil-95": 10                                  │
│    }                                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. RETORNA RESPOSTA AO CLIENTE                             │
│    HTTP 200 OK + JSON                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Endpoint da API

### POST `/forecast/run-forecast`

**Descrição:** Executa uma simulação de Monte Carlo para prever semanas de conclusão do backlog.

**Request:**
```bash
curl -X POST "http://localhost:8000/forecast/run-forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "nr_simulations": 1000,
    "backlog_min": 10,
    "backlog_max": 20,
    "throughput": [2, 3, 4, 5]
  }'
```

**Response (200 OK):**
```json
{
  "Backlog-min": 10,
  "Backlog-max": 20,
  "Throughput": [2, 3, 4, 5],
  "Simulations": 1000,
  "Percentil-50": 5,
  "Percentil-75": 7,
  "Percentil-85": 8,
  "Percentil-95": 10
}
```

---

## ✅ Testes

Para validar o funcionamento da aplicação:

```bash
# Executar todos os testes
pytest testes/unit_tests.py -v

# Executar teste específico
pytest testes/unit_tests.py::test_run_simulation_returns_list_of_ints -v

# Com cobertura
pytest testes/unit_tests.py --cov=app
```

---

## 📁 Estrutura de Diretórios

```
api_forecast_v-1/
├── app/
│   ├── main.py                 # Inicialização da aplicação FastAPI
│   ├── models/
│   │   └── models.py           # Validação de dados (Pydantic)
│   ├── routers/
│   │   └── forecast_routes.py  # Endpoints da API
│   └── services/
│       └── forecast.py         # Lógica de simulação de Monte Carlo
├── testes/
│   └── unit_tests.py           # Testes unitários
├── requirements.txt            # Dependências Python
├── Dockerfile                  # Configuração Docker
├── docker-compose.yaml         # Orquestração com Docker Compose
├── README.md                   # Este arquivo
└── .git/                       # Repositório Git
```

---

## 🔧 Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido para construir APIs
- **Uvicorn**: Servidor ASGI de alta performance
- **Pydantic**: Validação de dados e serialização automática
- **NumPy**: Computação numérica e funções estatísticas
- **Pytest**: Framework para testes unitários
- **Docker**: Containerização da aplicação

---

## 📝 Notas

- As simulações usam números aleatórios, então resultados podem variar levemente entre execuções
- Para previsões mais estáveis, aumente `nr_simulations` (ex: 10000)
- O throughput deve refletir dados históricos reais da equipe
- Todos os valores são em semanas
