"""Runner LOCAL para teste AO VIVO dos passos já implementados (1-8).

Abre o navegador, ESPERA você logar no IXC e abrir Estoque -> Patrimônio
(a listagem), e então roda o fluxo para o patrimônio informado. O bot ainda
NÃO faz login sozinho — por isso a pausa manual.

Uso:
    python run_local.py 12312
    python run_local.py          # pergunta o código no terminal
"""
from __future__ import annotations

import sys

from loguru import logger

from agent import Agent
from automation import BrowserActuator
from config import settings
from flows.login import fazer_login
from flows.patrimonio import FluxoPatrimonio
from persistence import setup_logging


def main() -> None:
    setup_logging()

    codigo = sys.argv[1] if len(sys.argv) > 1 else input("Código do patrimônio: ").strip()
    if not codigo:
        print("Informe o código do patrimônio.")
        return

    url = settings.ixc_base_url.strip()
    url_valida = url and "seu-ixc" not in url.lower()  # ignora o placeholder do .env

    actuator = BrowserActuator(headless=False)  # sempre visível para acompanhar
    actuator.start()
    try:
        if url_valida:
            res = actuator.goto(url)
            if res.success:
                logger.info("Abri {}", url)
            else:
                logger.warning("Não consegui abrir {} ({}). Navegue manualmente.", url, res.message)
        else:
            logger.warning(
                "IXC_BASE_URL não configurado (ainda é o exemplo). "
                "Digite o endereço do IXC no próprio navegador."
            )

        # Login automático (email + senha do .env). Se ainda não configurado,
        # apenas avisa e segue — você loga manualmente.
        res_login = fazer_login(actuator, settings.ixc_user, settings.ixc_password)
        if res_login.success:
            logger.info("Login automático enviado. Aguarde carregar o IXC.")
        else:
            logger.warning("Login automático não feito: {}", res_login.message)

        input(
            "\n>>> Faça LOGIN no IXC e abra Estoque -> Patrimônio (a LISTAGEM).\n"
            ">>> Com a tela de patrimônios aberta, tecle ENTER aqui para o bot rodar...\n"
        )

        agent = Agent(actuator)
        flow = FluxoPatrimonio(agent, codigo=codigo)
        final = flow.run()

        print("\n===== RESULTADO =====")
        print("Passo final  :", final)
        print("Patrimônio   :", agent.state.patrimonio)
        print("Contexto     :", agent.state.context)
        if agent.state.errors:
            print("Erros        :", agent.state.errors)
        print("=====================")
        print(
            "\nDica: 'aguardando_humano' no passo 8+ é ESPERADO — VERIFICAR_NOTAS_OS\n"
            "ainda não foi implementado. Se ENCERRAR já no início com status None,\n"
            "é sinal de que algum seletor não casou com a tela real.\n"
        )

        input("ENTER para fechar o navegador...")
    finally:
        actuator.stop()


if __name__ == "__main__":
    main()
