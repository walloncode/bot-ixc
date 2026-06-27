"""Diagnóstico INTERATIVO dos passos 2-4 (no frame principal).

Os elementos existem (diag_frames confirmou count=1), mas click/fill falham.
Este script TENTA clicar e digitar de verdade, reportando visibilidade,
se está habilitado e o erro real do Playwright — para achar a causa.

Uso:
    python diag_acoes.py [codigo_patrimonio]
"""
from __future__ import annotations

import sys

from automation import BrowserActuator
from config import settings

BTN = 'button[name="btn_buscar_todas"]'
BUSCA = "input.gridActionsSearchInput[name='q']"


def estado(page, sel: str, nome: str) -> None:
    loc = page.locator(sel)
    try:
        n = loc.count()
    except Exception as exc:  # noqa: BLE001
        print(f"  {nome}: count erro -> {exc}")
        return
    if n == 0:
        print(f"  {nome}: NÃO encontrado (count=0)")
        return
    first = loc.first
    try:
        vis = first.is_visible()
    except Exception as exc:  # noqa: BLE001
        vis = f"erro({exc})"
    try:
        en = first.is_enabled()
    except Exception as exc:  # noqa: BLE001
        en = f"erro({exc})"
    print(f"  {nome}: count={n} | visivel={vis} | habilitado={en}")


def tenta(fn, descricao: str) -> None:
    try:
        fn()
        print(f"  {descricao}: OK")
    except Exception as exc:  # noqa: BLE001
        print(f"  {descricao}: FALHOU -> {exc}")


def main() -> None:
    codigo = sys.argv[1] if len(sys.argv) > 1 else "12312"
    act = BrowserActuator(headless=False)
    act.start()
    page = act.page
    try:
        url = settings.ixc_base_url.strip()
        if url and "seu-ixc" not in url.lower():
            act.goto(url)

        input(
            "\n>>> Logue e abra Estoque -> Patrimônio (listagem).\n"
            ">>> ENTER para diagnosticar as ações...\n"
        )

        print("\n== ANTES de clicar 'Exibir todos' ==")
        estado(page, BTN, "exibir_todos")
        estado(page, BUSCA, "busca")

        print("\n== Clicando 'Exibir todos' (timeout 8s) ==")
        tenta(lambda: page.click(BTN, timeout=8000), "click exibir_todos")
        page.wait_for_timeout(2000)

        print("\n== DEPOIS de clicar ==")
        estado(page, BUSCA, "busca")

        print(f"\n== Digitando o código {codigo!r} na busca (timeout 8s) ==")
        tenta(lambda: page.fill(BUSCA, codigo, timeout=8000), "fill busca")
        page.wait_for_timeout(500)
        tenta(lambda: page.press(BUSCA, "Enter"), "press Enter")
        page.wait_for_timeout(2000)

        print("\n== Resultado da busca (badges de status na tela) ==")
        try:
            badges = page.locator("div.vg-badge").all_inner_texts()
            print(f"  div.vg-badge encontrados: {len(badges)} -> {badges[:5]}")
        except Exception as exc:  # noqa: BLE001
            print(f"  erro lendo badges: {exc}")

        input("\nENTER para fechar o navegador...")
    finally:
        act.stop()


if __name__ == "__main__":
    main()
