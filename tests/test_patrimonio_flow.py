"""Fluxo de patrimônio testado SEM browser, via FakeActuator.
Prova que a transição de estados depende só das regras + status lido.
"""
from typing import Optional

from agent import Agent, AgentStep
from flows.patrimonio import FluxoPatrimonio
from flows.parsing import status_from_badge
from models import ActionResult, ScreenState

# HTML real enviado pelo usuário (badge de status).
HTML_BADGE = (
    '<div class="vg-badge" title="Disponível" variant="success-3">'
    '<i class="fa-solid fa-circle-check"></i>'
    '<span class="vg-badge-content">Disponível</span></div>'
)


class FakeActuator:
    """Implementa o contrato Actuator devolvendo um status fixo."""

    def __init__(self, status: Optional[str]):
        self._status = status

    def click(self, target): return ActionResult(success=True)
    def double_click(self, target): return ActionResult(success=True)
    def type_text(self, target, value): return ActionResult(success=True)
    def scroll(self, target, amount=0): return ActionResult(success=True)
    def wait(self, target, timeout_ms=10_000): return ActionResult(success=True)
    def press(self, target, key="Enter"): return ActionResult(success=True)
    def get_text(self, target): return self._status
    def get_texts(self, target): return []
    def capture(self): return ScreenState()


def _run(status):
    agent = Agent(FakeActuator(status))
    flow = FluxoPatrimonio(agent, codigo="PAT123")
    step = flow.handle(AgentStep.CONSULTAR_PATRIMONIO)
    return step, agent.state


# --- parsing offline ---------------------------------------------------- #
def test_parsing_status_do_badge_real():
    assert status_from_badge(HTML_BADGE) == "Disponível"


# --- transições do fluxo ------------------------------------------------ #
def test_comodato_guarda_flag_e_segue_movimentacao():
    # Comodato NÃO desvia no início; guarda flag p/ devolução no fim (passo 37).
    step, state = _run("Comodato")
    assert step is AgentStep.VERIFICAR_MOVIMENTACAO
    assert state.patrimonio.status == "Comodato"
    assert state.context["status_inicial_comodato"] is True


def test_disponivel_tecnico_segue_movimentacao():
    step, _ = _run("Disponível técnico")
    assert step is AgentStep.VERIFICAR_MOVIMENTACAO


def test_disponivel_segue_sem_baixa():
    # "Disponível" -> continua, status guardado, precisa_baixa=False (§3)
    step, state = _run("Disponível")
    assert step is AgentStep.VERIFICAR_MOVIMENTACAO
    assert state.context["precisa_baixa"] is False
    assert state.context["status_origem"] == "Disponível"


def test_status_desconhecido_encerra():
    step, _ = _run("Sucateado")
    assert step is AgentStep.ENCERRADO


def test_status_ausente_encerra():
    step, _ = _run(None)
    assert step is AgentStep.ENCERRADO
