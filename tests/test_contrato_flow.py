"""Passo ABRIR_CONTRATO testado SEM browser, com seletor do HTML real do IXC."""
from agent import Agent, AgentStep
from flows.patrimonio import FluxoPatrimonio
from flows.selectors import ContratoSel
from models import ActionResult, ScreenState


class FakeClick:
    """FakeActuator que registra o alvo de cada click."""

    def __init__(self):
        self.clicks = []

    def click(self, target):
        self.clicks.append(target)
        return ActionResult(success=True)
    def double_click(self, target): return ActionResult(success=True)
    def type_text(self, target, value): return ActionResult(success=True)
    def scroll(self, target, amount=0): return ActionResult(success=True)
    def wait(self, target, timeout_ms=10_000): return ActionResult(success=True)
    def press(self, target, key="Enter"): return ActionResult(success=True)
    def get_text(self, target): return None
    def get_texts(self, target): return []
    def capture(self): return ScreenState()


def test_abrir_contrato_clica_botao_f3_e_segue_para_notas():
    agent = Agent(FakeClick())
    flow = FluxoPatrimonio(agent, codigo="12312")

    step = flow.handle(AgentStep.ABRIR_CONTRATO)

    # clicou no botão F3 real do campo de contrato
    assert ContratoSel.abrir_contrato_btn in agent.actuator.clicks
    # e transita para a verificação de notas/O.S. (passos 9-10)
    assert step is AgentStep.VERIFICAR_NOTAS_OS
