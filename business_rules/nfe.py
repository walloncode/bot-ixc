"""Regras puras de NF-e (regras.md §5, §10). Validação completa antes de emitir."""
from __future__ import annotations

from models import EntradaEstoque, RuleOutcome, RuleResult, Venda


def contrato_ja_tem_nf(nf_existente: bool) -> RuleResult:
    """§5: se já existe NF para o mesmo patrimônio -> ENCERRAR."""
    if nf_existente:
        return RuleResult(outcome=RuleOutcome.STOP,
                          reason="Já existe NF para este patrimônio")
    return RuleResult(outcome=RuleOutcome.CONTINUE, reason="Sem NF prévia")


def validar_pre_danfe(entrada: EntradaEstoque, venda: Venda) -> RuleResult:
    """§10: valida Produto, Quantidade, Valor e Referência da venda.

    Qualquer divergência -> NÃO EMITIR.
    """
    divergencias: list[str] = []

    vendidos = {p.descricao: p for p in venda.produtos}
    for prod in entrada.produtos:
        ref = vendidos.get(prod.descricao)
        if ref is None:
            divergencias.append(f"Produto fora da venda: {prod.descricao}")
            continue
        if prod.quantidade != 1:
            divergencias.append(f"Quantidade != 1: {prod.descricao}")
        if prod.preco != ref.preco:
            divergencias.append(
                f"Preço divergente em {prod.descricao}: {prod.preco} != {ref.preco}"
            )

    if venda.numero not in entrada.observacoes:
        divergencias.append("Referência da venda ausente na observação")

    if divergencias:
        return RuleResult(outcome=RuleOutcome.STOP,
                          reason="Divergências na Pré-DANFE",
                          data={"divergencias": divergencias})

    return RuleResult(outcome=RuleOutcome.CONTINUE,
                      reason="Pré-DANFE validada: pode emitir")
