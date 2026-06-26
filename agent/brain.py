"""Cérebro / orquestrador. Implementa o loop obrigatório:

    1. Captura estado da tela (screenshot)
    2. Interpreta contexto
    3. Decide próximo passo
    4. Executa ação
    5. Reavalia estado

NUNCA executa múltiplas ações sem reavaliar. A IA só é consultada como
exceção (ambiguidade/erro desconhecido) e sempre passa pelo gate de confiança.
"""
from __future__ import annotations

from typing import Callable, Optional

from loguru import logger

from config import settings
from models import ActionResult, AIDecision, ActionType, ScreenState
from skills import Actuator

from .ai_client import AIClient
from .state import AgentState


class HumanConfirmationRequired(Exception):
    """Levantada quando uma decisão precisa de aprovação humana."""

    def __init__(self, decision: AIDecision):
        self.decision = decision
        super().__init__(decision.reason)


class Agent:
    """Coordena percepção -> decisão -> ação, um passo de cada vez."""

    def __init__(
        self,
        actuator: Actuator,
        ai: Optional[AIClient] = None,
        confirm: Optional[Callable[[AIDecision], bool]] = None,
    ) -> None:
        self.actuator = actuator
        self.ai = ai or AIClient()
        self.state = AgentState()
        # `confirm` é injetado (CLI/painel). Por padrão NEGA -> seguro.
        self._confirm = confirm or (lambda _d: False)

    # ----- passos do loop ------------------------------------------------ #
    def perceive(self) -> ScreenState:
        """Passo 1+2: captura a tela."""
        return self.actuator.capture()

    def ask_ai(self, prompt: str) -> AIDecision:
        """Passo 3 (exceção): consulta IA e aplica o gate de confiança."""
        decision = self.ai.decide(prompt)
        logger.info("IA: {} target={} conf={}", decision.action,
                    decision.target, decision.confidence)
        if decision.needs_human(settings.confidence_threshold):
            if not self._confirm(decision):
                raise HumanConfirmationRequired(decision)
        return decision

    def act(self, decision: AIDecision) -> ActionResult:
        """Passo 4: executa UMA ação atômica. A IA não toca no actuator."""
        match decision.action:
            case ActionType.CLICK:
                return self.actuator.click(decision.target)
            case ActionType.TYPE:
                return self.actuator.type_text(decision.target, decision.value or "")
            case ActionType.SCROLL:
                return self.actuator.scroll(decision.target)
            case ActionType.WAIT:
                return self.actuator.wait(decision.target)
            case ActionType.STOP:
                return ActionResult(success=True, message="stop solicitado")
        return ActionResult(success=False, message="ação desconhecida")
