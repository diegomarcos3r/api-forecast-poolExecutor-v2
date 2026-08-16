# Monte Carlo Forecast API

API que realiza **simulações de Monte Carlo** para prever o número de semanas necessárias para concluir um backlog. Utiliza dados históricos de throughput (velocidade de entrega) para gerar estimativas precisas com múltiplos percentis de confiança.

---

## 🎯 Objetivo da Aplicação

Fornecer previsões realistas sobre o tempo de conclusão de um backlog baseadas em:
- **Tamanho do backlog** (intervalo mínimo e máximo)
- **Histórico de produtividade** (throughput semanal)
- **Múltiplas simulações** para gerar distribuições estatísticas

O algoritmo executa centenas ou milhares de simulações aleatórias para criar um modelo probabilístico, resultando em percentis (P50, P75, P85, P95) que representam diferentes níveis de confiança na estimativa.

---

## 📥 Dados de Entrada

O endpoint aceita um JSON com os seguintes parâmetros:

```json
{
  "nr_simulations": 1000,
  "backlog_min": 10,
  "backlog_max": 20,
  "throughput": [2, 3, 4, 5]
}
```

| Parâmetro | Tipo | Descrição | Validação |
|-----------|------|-----------|-----------|
| `nr_simulations` | `int` | Número de simulações de Monte Carlo a executar | Deve ser > 0 |
| `backlog_min` | `int` | Tamanho mínimo do backlog (em stories/pontos) | Deve ser > 0 |
| `backlog_max` | `int` | Tamanho máximo do backlog (em stories/pontos) | Deve ser ≥ backlog_min |
| `throughput` | `list[int]` | Histórico de velocidade semanal da equipe | Mínimo 4 valores |

---

## ⚙️ Como Ocorre o Processamento

### 1. **Validação de Entrada**
O Pydantic valida automaticamente:
- Simulações > 0
- Backlog mínimo > 0
- Backlog máximo ≥ mínimo
- Throughput com pelo menos 4 semanas de histórico

### 2. **Simulação de Monte Carlo**
Para cada uma das `nr_simulations`:

```
Para cada simulação:
  1. Gera um tamanho aleatório de backlog entre [backlog_min, backlog_max]
  2. Inicializa contador de semanas e trabalho completado
  3. Enquanto (trabalho completado < backlog):
     - Seleciona aleatoriamente um valor de throughput
     - Adiciona esse valor ao trabalho completado
     - Incrementa o contador de semanas
  4. Armazena o número de semanas necessárias
```

### 3. **Cálculo de Percentis**
Após todas as simulações, calcula os percentis:
- **P50** (Mediana): 50% de chance de concluir em menos semanas
- **P75**: 75% de chance de concluir em menos semanas
- **P85**: 85% de chance de concluir em menos semanas
- **P95**: 95% de chance de concluir em menos semanas

### 4. **Formatação da Resposta**
Retorna um JSON estruturado com os parâmetros de entrada e os percentis calculados.

---

## 📤 Dados de Saída

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

| Campo | Descrição |
|-------|-----------|
| `Backlog-min` | Tamanho mínimo do backlog utilizado |
| `Backlog-max` | Tamanho máximo do backlog utilizado |
| `Throughput` | Histórico de throughput fornecido |
| `Simulations` | Número de simulações executadas |
| `Percentil-50` | Mediana (50% de confiança) em semanas |
| `Percentil-75` | 75% de confiança em semanas |
| `Percentil-85` | 85% de confiança em semanas |
| `Percentil-95` | 95% de confiança em semanas |

**Interpretação:** Com os dados acima, há 50% de probabilidade de completar em 5 semanas, e 95% de probabilidade em 10 semanas.

---

## 📦 Dependências da Aplicação

| Pacote | Versão | Propósito |
|--------|--------|----------|
| **FastAPI** | Latest | Framework web para criar a API REST |
| **Uvicorn** | Latest | Servidor ASGI para executar a aplicação |
| **Pydantic** | Latest | Validação e serialização de dados |
| **NumPy** | Latest | Operações numéricas e cálculos estatísticos |
| **Pytest** | Latest | Framework para testes unitários |
| **Python** | 3.13 | Linguagem de programação |

Todas as dependências estão definidas em `requirements.txt`.

---

## 🚀 Como a Aplicação Roda

### Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                │
├─────────────────────────────────────────────────────┤
│  main.py                                            │
│  └─ Inicializa a aplicação FastAPI                 │
├─────────────────────────────────────────────────────┤
│  app/routers/forecast_routes.py                    │
│  └─ Endpoint POST /forecast/run-forecast           │
├─────────────────────────────────────────────────────┤
│  app/models/models.py                              │
│  └─ Validação de dados (CreateSimulation)          │
├─────────────────────────────────────────────────────┤
│  app/services/forecast.py                          │
│  └─ Lógica da simulação de Monte Carlo             │
└─────────────────────────────────────────────────────┘
```

### Execução Local

1. **Instale as dependências**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Execute a aplicação**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Acesse a API**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Execução com Docker

1. **Construa e suba o container**
   ```bash
   docker-compose up --build
   ```

2. **Acesse a API**
   - [http://localhost:8000/docs](http://localhost:8000/docs)

A aplicação será servida em `http://localhost:8000`.

---

## 🔄 Fluxo da Aplicação

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLIENTE ENVIA REQUISIÇÃO                                │
│    POST /forecast/run-forecast                             │
│    Body: {nr_simulations, backlog_min, backlog_max, ...}  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. VALIDAÇÃO (Pydantic)                                    │
│    ✓ nr_simulations > 0?                                   │
│    ✓ backlog_min > 0?                                      │
│    ✓ backlog_max >= backlog_min?                           │
│    ✓ throughput tem 4+ valores?                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. INSTANCIA CLASSE Forecast                               │
│    forecast = Forecast(                                    │
│        nr_simulations=1000,                                │
│        backlog_min=10,                                     │
│        backlog_max=20,                                     │
│        throughput=[2,3,4,5]                                │
│    )                                                        │
└────────────────┬────────────────────────────────────────────┘
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
