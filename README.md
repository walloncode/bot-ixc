# Agente IXC

Automação determinística do fluxo de NF-e no IXC.
**Princípio:** 80% regras fixas + 20% IA (só exceções). Previsibilidade > inteligência.

## Arquitetura

```
agent/          decisão e estado (loop perceber→decidir→agir→reavaliar)
  state.py      máquina de estados (AgentStep) + AgentState (Pydantic)
  ai_client.py  IA -> AIDecision (JSON). Só exceções. Gate de confiança.
  brain.py      orquestrador: 1 ação por vez, sempre reavalia
automation/     controle real: Playwright (principal), PyAutoGUI (fallback),
                OpenCV (visão), Tesseract (OCR)
flows/          fluxos de negócio (patrimônio, vendas, NF...) + selectors.py
business_rules/ regras PURAS, sem IA, traduzindo regras.md (fonte da verdade)
skills/         contrato Actuator (ações atômicas: click/type/scroll/wait)
models/         contratos tipados (Pydantic)
persistence/    SQLite (logs/decisões/erros) + Loguru
logs/           screenshots e histórico
main.py         painel FastAPI (start/stop/status)
regras.md       BUSINESS_RULES — fonte da verdade
```

## Setup

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # preencher credenciais e seletores
```

## Rodar

```bash
uvicorn main:app --reload
# POST /start {"patrimonio": "PAT123"}  |  GET /status  |  POST /stop
```

## Testes

```bash
pytest -q
```

## ⚠️ Antes de produção

Os seletores do IXC em `flows/selectors.py` estão como `__CONFIRMAR__`.
Enquanto não forem preenchidos com os seletores reais da tela, o fluxo
**para e pede intervenção humana** (regra #2: nunca inventar a tela do IXC).
```
