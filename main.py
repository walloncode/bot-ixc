"""Painel de controle (FastAPI): iniciar/parar/status da automação.

Execução real do fluxo roda em thread separada para não bloquear a API.
Esta camada NÃO contém regra de negócio — só orquestra.
"""
from __future__ import annotations

import threading
from typing import Optional

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

from agent import Agent
from automation import BrowserActuator
from config import settings
from flows.patrimonio import FluxoPatrimonio
from persistence import init_db, setup_logging

app = FastAPI(title="Agente IXC", version="0.1.0")

_runner: Optional[threading.Thread] = None
_status: dict = {"running": False, "step": None, "detail": ""}


class StartReq(BaseModel):
    patrimonio: str


@app.on_event("startup")
def _startup() -> None:
    setup_logging()
    init_db()
    logger.info("Agente IXC pronto.")


def _run_flow(patrimonio: str) -> None:
    actuator = BrowserActuator()
    try:
        actuator.start()
        if settings.ixc_base_url:
            actuator.goto(settings.ixc_base_url)
        agent = Agent(actuator)
        flow = FluxoPatrimonio(agent, codigo=patrimonio)
        final = flow.run()
        _status.update(running=False, step=str(final), detail="fim")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Falha na execução")
        _status.update(running=False, step="ERRO", detail=str(exc))
    finally:
        actuator.stop()


@app.post("/start")
def start(req: StartReq) -> dict:
    global _runner
    if _status["running"]:
        return {"ok": False, "msg": "Já existe execução em andamento"}
    _status.update(running=True, step="iniciando", detail=req.patrimonio)
    _runner = threading.Thread(target=_run_flow, args=(req.patrimonio,), daemon=True)
    _runner.start()
    return {"ok": True, "msg": f"Execução iniciada para {req.patrimonio}"}


@app.get("/status")
def status() -> dict:
    return _status


@app.post("/stop")
def stop() -> dict:
    # Parada cooperativa fica para a próxima iteração (flag no AgentState).
    _status.update(running=False, detail="parada solicitada")
    return {"ok": True}
