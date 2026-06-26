"""Testes das regras puras — provam que cada regra é testável isoladamente,
sem browser, sem IA, sem IXC.
"""
from datetime import datetime

from business_rules import patrimonio, vendas, nfe
from models import Patrimonio, Venda, ProdutoVenda, RuleOutcome


def test_patrimonio_nao_encontrado_encerra():
    assert patrimonio.avaliar_status(None).outcome is RuleOutcome.STOP


def test_patrimonio_status_desconhecido_encerra():
    p = Patrimonio(codigo="X", status="Sucateado")
    assert patrimonio.avaliar_status(p).outcome is RuleOutcome.STOP


def test_patrimonio_comodato_continua():
    p = Patrimonio(codigo="X", status="Comodato")
    res = patrimonio.avaliar_status(p)
    assert res.ok and patrimonio.em_comodato(p)


def test_vendas_seleciona_mais_recente_compativel():
    p = "PAT123"
    antiga = Venda(numero="1", documento="638", data=datetime(2024, 1, 1),
                   produtos=[ProdutoVenda(descricao="ONU", preco=100, patrimonio=p)])
    nova = Venda(numero="2", documento="641", data=datetime(2024, 6, 1),
                 produtos=[ProdutoVenda(descricao="ONU", preco=100, patrimonio=p)])
    res = vendas.filtrar_e_selecionar([antiga, nova], p)
    assert res.ok and res.data["venda"].numero == "2"


def test_vendas_sem_compativel_encerra():
    v = Venda(numero="1", documento="999", data=datetime(2024, 1, 1),
              produtos=[ProdutoVenda(descricao="ONU", preco=100, patrimonio="OUTRO")])
    assert vendas.filtrar_e_selecionar([v], "PAT123").outcome is RuleOutcome.STOP


def test_nfe_contrato_com_nf_encerra():
    assert nfe.contrato_ja_tem_nf(True).outcome is RuleOutcome.STOP
