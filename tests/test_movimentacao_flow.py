"""Passo VERIFICAR_MOVIMENTACAO testado SEM browser, com HTML real do IXC."""
from agent import Agent, AgentStep
from business_rules.movimentacao import avaliar_movimentacoes
from flows.patrimonio import FluxoPatrimonio
from flows.parsing import movimentacoes_from_html
from flows.selectors import MovimentacaoSel
from models import ActionResult, ScreenState

# Tabela real de movimentações (patrimônio 12312) enviada pelo operador.
HTML_MOV = """
<table id="patrimonio_patrimonio_movimentacao"><tbody>
<tr><td abbr="patrimonio_movimentacao.data_movimentacao"><div>13/06/2022</div></td>
    <td abbr="patrimonio_movimentacao.finalidade"><div>Entrada</div></td></tr>
<tr><td abbr="patrimonio_movimentacao.data_movimentacao"><div>01/07/2022</div></td>
    <td abbr="patrimonio_movimentacao.finalidade"><div>Transferido</div></td></tr>
<tr><td abbr="patrimonio_movimentacao.data_movimentacao"><div>12/07/2022</div></td>
    <td abbr="patrimonio_movimentacao.finalidade"><div>Comodato</div></td></tr>
<tr><td abbr="patrimonio_movimentacao.data_movimentacao"><div>29/06/2022</div></td>
    <td abbr="patrimonio_movimentacao.finalidade"><div>&nbsp;</div></td></tr>
</tbody></table>
"""


class FakeMov:
    """FakeActuator que devolve as colunas finalidade/data via get_texts."""

    def __init__(self, finalidades, datas):
        self._fin = finalidades
        self._dat = datas

    def click(self, target): return ActionResult(success=True)
    def double_click(self, target): return ActionResult(success=True)
    def type_text(self, target, value): return ActionResult(success=True)
    def scroll(self, target, amount=0): return ActionResult(success=True)
    def wait(self, target, timeout_ms=10_000): return ActionResult(success=True)
    def press(self, target, key="Enter"): return ActionResult(success=True)
    def get_text(self, target): return None
    def get_texts(self, target):
        if target == MovimentacaoSel.col_finalidade:
            return self._fin
        if target == MovimentacaoSel.col_data:
            return self._dat
        return []
    def capture(self): return ScreenState()


def _run(finalidades, datas):
    agent = Agent(FakeMov(finalidades, datas))
    flow = FluxoPatrimonio(agent, codigo="12312")
    return flow.handle(AgentStep.VERIFICAR_MOVIMENTACAO), agent.state


# --- parsing offline (HTML real) ---------------------------------------- #
def test_parsing_movimentacoes_do_html_real():
    movs = movimentacoes_from_html(HTML_MOV)
    assert len(movs) == 4
    res = avaliar_movimentacoes(movs)
    assert res.ok
    # mais recente entre Comodato/Devolução = Comodato 12/07/2022
    assert res.data["movimentacao"]["tipo"] == "Comodato"
    assert res.data["movimentacao"]["data"].strftime("%d/%m/%Y") == "12/07/2022"


# --- transições do fluxo ------------------------------------------------ #
def test_com_comodato_segue_para_contrato():
    step, state = _run(["Entrada", "Comodato"], ["13/06/2022", "12/07/2022"])
    assert step is AgentStep.ABRIR_CONTRATO
    assert state.context["movimentacao"]["tipo"] == "Comodato"


def test_sem_comodato_nem_devolucao_encerra():
    step, _ = _run(["Entrada", "Transferido"], ["13/06/2022", "01/07/2022"])
    assert step is AgentStep.ENCERRADO
