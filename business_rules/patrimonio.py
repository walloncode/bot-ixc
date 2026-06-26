"""Regras puras de patrimônio (regras.md §3). Sem IA, sem efeitos colaterais."""
from __future__ import annotations

from models import Patrimonio, RuleOutcome, RuleResult

# Status que permitem continuar o fluxo (regras.md §3).
STATUS_CONTINUA = {
    "comodato",
    "disponível técnico", "disponivel tecnico",
    "disponível", "disponivel",
}

# Status que explicitamente NÃO requerem baixa (regras.md §3).
STATUS_SEM_BAIXA = {"disponível", "disponivel"}


def avaliar_status(patrimonio: Patrimonio | None) -> RuleResult:
    """§3: não encontrado / status desconhecido -> ENCERRAR."""
    if patrimonio is None:
        return RuleResult(outcome=RuleOutcome.STOP,
                          reason="Patrimônio não encontrado")

    status = (patrimonio.status or "").strip().lower()
    if not status:
        return RuleResult(outcome=RuleOutcome.STOP,
                          reason="Status do patrimônio desconhecido")

    if status in STATUS_CONTINUA:
        return RuleResult(outcome=RuleOutcome.CONTINUE,
                          reason=f"Status válido: {patrimonio.status}",
                          data={"status": status})

    return RuleResult(outcome=RuleOutcome.STOP,
                      reason=f"Status não previsto: {patrimonio.status}")


def em_comodato(patrimonio: Patrimonio) -> bool:
    """§13: define se a etapa de comodato deve ser executada."""
    return (patrimonio.status or "").strip().lower() == "comodato"


def precisa_dar_baixa(patrimonio: Patrimonio) -> bool | None:
    """§3: decisão de baixa por status.

    - "Disponível"            -> False (não dá baixa).
    - demais status válidos   -> None (regra de baixa ainda não definida).
    """
    if (patrimonio.status or "").strip().lower() in STATUS_SEM_BAIXA:
        return False
    return None
