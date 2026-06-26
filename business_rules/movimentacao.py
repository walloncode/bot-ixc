"""Regras puras de movimentação (regras.md §4)."""
from __future__ import annotations

from models import RuleOutcome, RuleResult

TIPOS_VALIDOS = {"comodato", "devolução", "devolucao"}


def avaliar_movimentacoes(movimentacoes: list[dict]) -> RuleResult:
    """§4: sem movimentação de Comodato/Devolução -> ENCERRAR.

    `movimentacoes`: lista de dicts {"tipo": str, "data": datetime}, já
    extraída pela camada de fluxo. Considera-se a mais recente.
    """
    relevantes = [
        m for m in movimentacoes
        if (m.get("tipo") or "").strip().lower() in TIPOS_VALIDOS
    ]
    if not relevantes:
        return RuleResult(outcome=RuleOutcome.STOP,
                          reason="Sem movimentação de comodato/devolução")

    mais_recente = max(relevantes, key=lambda m: m["data"])
    return RuleResult(outcome=RuleOutcome.CONTINUE,
                      reason=f"Movimentação considerada: {mais_recente['tipo']}",
                      data={"movimentacao": mais_recente})
