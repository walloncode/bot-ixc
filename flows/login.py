"""Login automático no IXC (email + senha) usando credenciais do .env.

Mantém o estilo do projeto: só usa ações atômicas do Actuator e seletores
confirmados em selectors.py. Enquanto os seletores estiverem como CONFIRMAR,
recusa-se a agir (regra §16: não inventar).
"""
from __future__ import annotations

from loguru import logger

from flows.selectors import LoginSel, pendentes
from models import ActionResult


def fazer_login(actuator, user: str, password: str) -> ActionResult:
    """Login do IXC em duas etapas: 1) email + Continuar  2) senha + entrar.

    A etapa 1 já está confirmada. Se a etapa 2 (senha) ainda não tiver
    seletores, fazemos só a etapa 1 — assim você cai na tela de senha e pode
    capturar o HTML dela (e digitar a senha manualmente nessa primeira vez).
    """
    if not user or not password:
        return ActionResult(success=False, message="IXC_USER/IXC_PASSWORD vazios no .env")

    # --- Etapa 1: email + Continuar -------------------------------------- #
    actuator.wait(LoginSel.email_input)
    r_email = actuator.type_text(LoginSel.email_input, user)
    r_cont = actuator.click(LoginSel.continuar_btn)
    logger.info("login etapa 1: email={} | continuar={}", r_email.success, r_cont.success)
    if not (r_email.success and r_cont.success):
        return ActionResult(success=False, message="falha na etapa 1 (email/continuar)")

    # --- Etapa 2: senha + entrar ----------------------------------------- #
    if pendentes(LoginSel.senha_input, LoginSel.entrar_btn):
        return ActionResult(
            success=False,
            message="Etapa 1 OK (email enviado). Etapa 2 (senha) pendente: "
            "envie o HTML da tela de senha. Por ora, digite a senha manualmente.",
        )

    actuator.wait(LoginSel.senha_input)
    r_senha = actuator.type_text(LoginSel.senha_input, password)
    r_btn = actuator.click(LoginSel.entrar_btn)
    ok = r_senha.success and r_btn.success
    logger.info("login etapa 2: senha={} | entrar={}", r_senha.success, r_btn.success)
    return ActionResult(success=ok, message="login enviado" if ok else "falha na etapa 2 (senha)")
