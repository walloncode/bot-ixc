"""Fluxo de consulta de patrimônio (primeira etapa do processo).

Estrutura pronta e ligada às regras puras. Os pontos que dependem da TELA REAL
do IXC (extrair status do DOM) estão isolados em métodos `_ler_*` e dependem
de `selectors.py` — que ainda está como CONFIRMAR. Enquanto não confirmado,
o fluxo PARA e pede intervenção (regra #2 / §16).
"""
from __future__ import annotations

from loguru import logger

from agent import AgentStep
from business_rules import movimentacao as regras_mov
from business_rules import patrimonio as regras_pat
from models import Patrimonio

from .base import Flow
from .parsing import movimentacoes_from_cells
from .selectors import ContratoSel, MovimentacaoSel, PatrimonioSel, linha_patrimonio


class FluxoPatrimonio(Flow):
    def __init__(self, agent, codigo: str) -> None:
        super().__init__(agent)
        self.codigo = codigo

    def handle(self, step: AgentStep) -> AgentStep:
        if step is AgentStep.CONSULTAR_PATRIMONIO:
            return self._consultar()
        if step is AgentStep.VERIFICAR_MOVIMENTACAO:
            return self._verificar_movimentacao()
        if step is AgentStep.ABRIR_CONTRATO:
            return self._abrir_contrato()
        # Próximas etapas (notas/O.S., vendas, NF...) entram aqui.
        logger.warning("Etapa ainda não implementada: {}", step)
        return AgentStep.AGUARDANDO_HUMANO

    # ----- passo: consultar patrimônio ----------------------------------- #
    def _consultar(self) -> AgentStep:
        sel = PatrimonioSel

        # 1. exibir todos os patrimônios, depois buscar por código (Enter).
        #    Logamos cada ação para diagnosticar seletor que não casa com a tela.
        a = self.agent.actuator
        r_todos = a.click(sel.exibir_todos_btn)
        r_digita = a.type_text(sel.busca_input, self.codigo)
        r_enter = a.press(sel.busca_input, sel.busca_tecla)
        r_wait = a.wait(sel.resultado_status)
        logger.info(
            "consultar[{}]: exibir_todos={} | digitar_codigo={} | enter={} | aguardar_status={}",
            self.codigo, r_todos.success, r_digita.success, r_enter.success, r_wait.success,
        )
        if not (r_digita.success and r_enter.success):
            logger.warning(
                "Busca não foi aplicada (digitar/enter falhou) — status lido pode NÃO "
                "ser do patrimônio {}. Verifique os seletores busca_input/exibir_todos.",
                self.codigo,
            )

        # 2. ler status real da tela (depende do IXC -> isolado)
        status = self._ler_status()
        patrimonio = Patrimonio(codigo=self.codigo, status=status)
        self.agent.state.patrimonio = patrimonio

        # 3. aplicar regra pura (sem IA)
        resultado = regras_pat.avaliar_status(patrimonio)
        logger.info("Regra patrimônio: {} ({})", resultado.outcome, resultado.reason)
        if not resultado.ok:
            return AgentStep.ENCERRADO

        # 4. guardar status e flags p/ etapas posteriores (§3, §13, §37).
        #    Comodato NÃO desvia aqui: a devolução ocorre no FIM (passo 37).
        ctx = self.agent.state.context
        ctx["status_origem"] = patrimonio.status
        ctx["status_inicial_comodato"] = regras_pat.em_comodato(patrimonio)
        ctx["precisa_baixa"] = regras_pat.precisa_dar_baixa(patrimonio)
        logger.info("Status {!r} guardado | comodato_inicial={} | precisa_baixa={}",
                    patrimonio.status, ctx["status_inicial_comodato"], ctx["precisa_baixa"])

        # 5. sempre segue para a verificação de movimentação (passo 6).
        return AgentStep.VERIFICAR_MOVIMENTACAO

    # ----- passo: verificar movimentação (passos 6-7) -------------------- #
    def _verificar_movimentacao(self) -> AgentStep:
        sel = MovimentacaoSel

        # 1. abrir o patrimônio (duplo clique na linha) e ir ao histórico.
        self.agent.actuator.double_click(linha_patrimonio(self.codigo))
        self.agent.actuator.click(sel.aba_historico)
        self.agent.actuator.wait(sel.linha_movimentacao)

        # 2. ler movimentações e aplicar a regra pura (§4).
        movimentacoes = self._ler_movimentacoes()
        resultado = regras_mov.avaliar_movimentacoes(movimentacoes)
        logger.info("Regra movimentação: {} ({})", resultado.outcome, resultado.reason)
        if not resultado.ok:
            return AgentStep.ENCERRADO

        self.agent.state.context["movimentacao"] = resultado.data.get("movimentacao")
        return AgentStep.ABRIR_CONTRATO

    # ----- passo 8: abrir contrato -------------------------------------- #
    def _abrir_contrato(self) -> AgentStep:
        """Passo 8: abre o cadastro do contrato pelo botão F3 do campo
        `id_contrato`. Sem regra de negócio (FLUXO_COMPLETO §8 = "—"): só
        navega e segue para a verificação de notas/O.S. (passos 9-10).

        OBS: ainda falta o HTML da tela de contrato aberta para confirmar
        como esperar o carregamento (nova aba? iframe?). Por isso NÃO há
        `wait` inventado aqui — isso entra no passo VERIFICAR_NOTAS_OS.
        """
        self.agent.actuator.click(ContratoSel.abrir_contrato_btn)
        logger.info("Contrato aberto (F3) — seguindo para notas/O.S.")
        return AgentStep.VERIFICAR_NOTAS_OS

    def _ler_movimentacoes(self) -> list[dict]:
        """Lê [{'tipo', 'data'}] do histórico via colunas finalidade + data."""
        finalidades = self.agent.actuator.get_texts(MovimentacaoSel.col_finalidade)
        datas = self.agent.actuator.get_texts(MovimentacaoSel.col_data)
        return movimentacoes_from_cells(finalidades, datas)

    def _ler_status(self) -> str | None:
        """Lê o status do patrimônio na tela (badge `div.vg-badge`).

        Usa o contrato `Actuator.get_text` (DOM ao vivo). None força o
        ENCERRAMENTO pela regra de status desconhecido (§3).
        """
        status = self.agent.actuator.get_text(PatrimonioSel.resultado_status)
        logger.info("Status lido na tela: {!r}", status)
        return status
