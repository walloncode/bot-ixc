"""Estado do agente e etapas do fluxo (máquina de estados manual e explícita).

As etapas seguem a ordem das regras de negócio. Transições são decididas pelos
flows + business_rules, nunca pela IA.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from models import Patrimonio


class AgentStep(str, Enum):
    # Ordem real do processo (ver FLUXO_COMPLETO.md). Comodato é tratado no FIM.
    CONSULTAR_PATRIMONIO = "consultar_patrimonio"      # passos 1-5
    VERIFICAR_MOVIMENTACAO = "verificar_movimentacao"  # passos 6-7
    ABRIR_CONTRATO = "abrir_contrato"                  # passo 8
    VERIFICAR_NOTAS_OS = "verificar_notas_os"          # passos 9-10
    COPIAR_CLIENTE = "copiar_cliente"                  # passos 11-13
    ANALISAR_VENDAS = "analisar_vendas"                # passos 14-17
    CRIAR_ENTRADA_ESTOQUE = "criar_entrada_estoque"    # passos 18-22
    INSERIR_PRODUTOS = "inserir_produtos"              # passos 23-25
    EMITIR_NFE = "emitir_nfe"                          # passos 26-28
    FINALIZAR_OS = "finalizar_os"                      # passos 29-36
    DEVOLVER_COMODATO = "devolver_comodato"            # passo 37 (só se comodato)
    # estados terminais / de controle
    CONCLUIDO = "concluido"
    ENCERRADO = "encerrado"          # parada por regra de negócio
    AGUARDANDO_HUMANO = "aguardando_humano"
    ERRO = "erro"


TERMINAIS = {
    AgentStep.CONCLUIDO,
    AgentStep.ENCERRADO,
    AgentStep.AGUARDANDO_HUMANO,
    AgentStep.ERRO,
}


class AgentState(BaseModel):
    """Cérebro simples: tudo que o agente precisa lembrar entre passos."""

    step: AgentStep = AgentStep.CONSULTAR_PATRIMONIO
    patrimonio: Optional[Patrimonio] = None
    context: dict = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)

    @property
    def finished(self) -> bool:
        return self.step in TERMINAIS
