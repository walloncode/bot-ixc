"""Contratos de dados do agente. Tudo tipado (Pydantic) e sem lógica.

Estes modelos são a fronteira entre as camadas:
- IA devolve `AIDecision`
- Automação devolve `ActionResult`
- Captura de tela devolve `ScreenState`
- Regras puras devolvem `RuleResult`
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Ações atômicas
# --------------------------------------------------------------------------- #
class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    WAIT = "wait"
    STOP = "stop"


class AIDecision(BaseModel):
    """Única forma como a IA pode "falar". A IA nunca executa — só sugere."""

    action: ActionType
    target: str
    value: Optional[str] = None
    confidence: int = Field(ge=0, le=100)
    reason: str = ""

    def needs_human(self, threshold: int) -> bool:
        return self.confidence < threshold


# --------------------------------------------------------------------------- #
# Estado da tela e resultado de ação
# --------------------------------------------------------------------------- #
class ScreenState(BaseModel):
    """Snapshot do que está visível. Produzido pela camada de automação."""

    screenshot_path: Optional[str] = None
    url: Optional[str] = None
    ocr_text: Optional[str] = None
    captured_at: datetime = Field(default_factory=datetime.now)


class ActionResult(BaseModel):
    """Resultado de executar uma skill atômica."""

    success: bool
    message: str = ""
    screenshot_path: Optional[str] = None


# --------------------------------------------------------------------------- #
# Resultado de regra de negócio pura (SEM IA)
# --------------------------------------------------------------------------- #
class RuleOutcome(str, Enum):
    CONTINUE = "continue"        # segue o fluxo
    STOP = "stop"                # ENCERRAR PROCESSO (regra de negócio)
    NEEDS_HUMAN = "needs_human"  # regra não cobre -> intervenção humana


class RuleResult(BaseModel):
    outcome: RuleOutcome
    reason: str
    data: dict = Field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.outcome is RuleOutcome.CONTINUE


# --------------------------------------------------------------------------- #
# Entidades de domínio do IXC
# --------------------------------------------------------------------------- #
class Patrimonio(BaseModel):
    codigo: str
    status: Optional[str] = None          # ex: "Comodato", "Disponível técnico"
    cliente: Optional[str] = None
    roteador_id: Optional[str] = None


class ProdutoVenda(BaseModel):
    descricao: str
    quantidade: int = 1
    preco: float
    patrimonio: Optional[str] = None


class Venda(BaseModel):
    numero: str
    documento: str                        # 638 | 641 (regra de negócio)
    data: datetime
    nf_numero: Optional[str] = None
    produtos: list[ProdutoVenda] = Field(default_factory=list)


class EntradaEstoque(BaseModel):
    tipo_documento: str = "205"
    fornecedor: str = ""                  # = cliente copiado do contrato
    condicao_pagamento: str = "1"
    data_emissao: Optional[datetime] = None
    data_entrada: Optional[datetime] = None
    almoxarifado: str = "85"
    observacoes: str = ""
    produtos: list[ProdutoVenda] = Field(default_factory=list)
