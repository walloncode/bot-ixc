"""Regras puras de vendas (regras.md §7)."""
from __future__ import annotations

from models import RuleOutcome, RuleResult, Venda

DOCUMENTOS_VALIDOS = {"638", "641"}


def filtrar_e_selecionar(vendas: list[Venda], patrimonio: str) -> RuleResult:
    """§7: filtra por documento 638/641, casa patrimônio exato, pega a mais recente.

    - nenhuma venda compatível -> ENCERRAR
    - múltiplas -> seleciona a mais recente
    """
    compativeis = [
        v for v in vendas
        if v.documento in DOCUMENTOS_VALIDOS
        and any(p.patrimonio == patrimonio for p in v.produtos)
    ]
    if not compativeis:
        return RuleResult(outcome=RuleOutcome.STOP,
                          reason="Nenhuma venda compatível (doc 638/641 + patrimônio)")

    selecionada = max(compativeis, key=lambda v: v.data)
    return RuleResult(outcome=RuleOutcome.CONTINUE,
                      reason=f"Venda selecionada: {selecionada.numero}",
                      data={"venda": selecionada})
