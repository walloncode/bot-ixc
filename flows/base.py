"""Base de fluxo. Cada fluxo é uma máquina de estados que avança UM passo
por vez, sempre reavaliando (regra §7 do prompt mestre).

Subclasses implementam `handle(step)` retornando o próximo `AgentStep`.
A base cuida de: log, parada em estados terminais e segurança.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from loguru import logger

from agent import Agent, AgentStep
from agent.brain import HumanConfirmationRequired


class Flow(ABC):
    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    @abstractmethod
    def handle(self, step: AgentStep) -> AgentStep:
        """Executa o passo atual e devolve o próximo. Uma ação -> reavalia."""

    def run(self, max_steps: int = 100) -> AgentStep:
        """Loop principal: avança passo a passo até um estado terminal."""
        state = self.agent.state
        for _ in range(max_steps):
            if state.finished:
                break
            logger.info("Passo: {}", state.step)
            try:
                state.step = self.handle(state.step)
            except HumanConfirmationRequired as exc:
                logger.warning("Aguardando humano: {}", exc.decision.reason)
                state.step = AgentStep.AGUARDANDO_HUMANO
            except Exception as exc:  # noqa: BLE001 - erro crítico para
                logger.exception("Erro crítico no fluxo")
                state.errors.append(str(exc))
                state.step = AgentStep.ERRO
        logger.info("Fluxo finalizado em: {}", state.step)
        return state.step
