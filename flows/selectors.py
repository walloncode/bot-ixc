"""Seletores do IXC — confirmados a partir do HTML real da tela.

⚠️ REGRA #2: nada aqui é inventado. Tudo veio do HTML enviado.
"""
from __future__ import annotations

CONFIRMAR = "__CONFIRMAR__"


class PatrimonioSel:
    # 1) Botão que lista todos os patrimônios antes da busca.
    exibir_todos_btn: str = 'button[name="btn_buscar_todas"]'

    # 2) Campo de busca (já por CÓDIGO: placeholder "Consultar por Código").
    busca_input: str = "input.gridActionsSearchInput[name='q']"
    busca_tecla: str = "Enter"

    # 3) Badge de status. Busca por código retorna 1 resultado (confirmado).
    resultado_status: str = "div.vg-badge"


class MovimentacaoSel:
    # Aba do histórico — por texto (mais robusto que rel="2").
    aba_historico: str = 'a.tabTitle:has-text("Histórico de movimentações")'

    # Tabela e colunas do histórico de movimentações (confirmadas no HTML).
    tabela: str = "#patrimonio_patrimonio_movimentacao"
    linha_movimentacao: str = f"{tabela} tr.tableRow"
    col_finalidade: str = f'{tabela} td[abbr="patrimonio_movimentacao.finalidade"]'
    col_data: str = f'{tabela} td[abbr="patrimonio_movimentacao.data_movimentacao"]'


def linha_patrimonio(codigo: str) -> str:
    """Linha do resultado da busca cujo patrimonio.id == codigo.

    Aberta com DUPLO CLIQUE. Escopo pela célula de id evita casar com a
    tabela de movimentação (que usa abbr 'patrimonio_movimentacao.*').
    """
    return f'tr.tableRow:has(td[abbr="patrimonio.id"] div:text-is("{codigo}"))'


def pendentes(*seletores: str) -> list[str]:
    """Retorna os seletores ainda não confirmados (== CONFIRMAR)."""
    return [s for s in seletores if s == CONFIRMAR]
