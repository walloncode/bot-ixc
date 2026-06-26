"""Regras puras de estoque/entradas e produtos (regras.md §8 e §9)."""
from __future__ import annotations

from datetime import datetime

from models import EntradaEstoque, ProdutoVenda, Venda


def montar_entrada(venda: Venda, cliente: str, agora: datetime | None = None) -> EntradaEstoque:
    """§8 + §9 + §11: monta a entrada de estoque a partir da venda.

    Campos fixos por regra. Produtos e preços vêm IDÊNTICOS da venda
    (nunca alterar valores). NF da venda salva em observação.
    """
    agora = agora or datetime.now()
    produtos = [
        ProdutoVenda(
            descricao=p.descricao,
            quantidade=1,            # §9 quantidade padrão
            preco=p.preco,           # §9 preço idêntico ao da venda
            patrimonio=p.patrimonio,
        )
        for p in venda.produtos
    ]
    obs = f"Ref. NF venda: {venda.nf_numero or 's/ NF'} | Venda: {venda.numero}"

    return EntradaEstoque(
        tipo_documento="205",        # §8
        fornecedor=cliente,          # §6 cliente copiado do contrato
        condicao_pagamento="1",      # §8
        data_emissao=agora,          # §8
        data_entrada=agora,          # §8
        almoxarifado="85",           # §9
        observacoes=obs,             # §11
        produtos=produtos,
    )
