"""Diagnóstico de FRAMES do IXC.

Hipótese: a tela de Patrimônio roda dentro de um <iframe>, e por isso o
Playwright (que busca na página principal) não acha os elementos, mesmo com
o seletor correto.

Abre o navegador, espera você logar e abrir a tela alvo, e então lista TODOS
os frames e em qual deles cada seletor é encontrado.

Uso:
    python diag_frames.py
"""
from __future__ import annotations

from automation import BrowserActuator
from config import settings

# Seletores-chave dos passos 1-5 que estão falhando ao vivo.
SELETORES = {
    "exibir_todos": 'button[name="btn_buscar_todas"]',
    "busca (atual)": "input.gridActionsSearchInput[name='q']",
    "busca (ampla name=q)": "input[name='q']",
    "status badge": "div.vg-badge",
}


def main() -> None:
    act = BrowserActuator(headless=False)
    act.start()
    try:
        url = settings.ixc_base_url.strip()
        if url and "seu-ixc" not in url.lower():
            act.goto(url)

        input(
            "\n>>> Logue no IXC e abra Estoque -> Patrimônio (listagem).\n"
            ">>> Com a tela aberta, tecle ENTER para diagnosticar os frames...\n"
        )

        page = act.page
        frames = page.frames
        print(f"\n===== {len(frames)} FRAME(S) NA PÁGINA =====")
        for i, fr in enumerate(frames):
            print(f"\n[{i}] name={fr.name!r}")
            print(f"     url={fr.url!r}")
            for rotulo, sel in SELETORES.items():
                try:
                    n = fr.locator(sel).count()
                except Exception as exc:  # noqa: BLE001
                    n = f"erro({exc})"
                marca = " <-- AQUI" if isinstance(n, int) and n > 0 else ""
                print(f"     {rotulo:24} {sel:42} -> {n}{marca}")
        print("\n=====================================")
        print("Procure as linhas com '<-- AQUI': é o frame onde o conteúdo vive.")

        input("\nENTER para fechar o navegador...")
    finally:
        act.stop()


if __name__ == "__main__":
    main()
