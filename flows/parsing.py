"""Parsing puro de elementos do IXC (sem browser). Testável offline.

Serve como (a) validação do que entendemos do DOM e (b) fallback quando se
tem apenas um snapshot de HTML salvo, sem sessão ao vivo.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional


def status_from_badge(html: str) -> Optional[str]:
    """Extrai o status do badge `div.vg-badge`.

    Prioriza o atributo `title`; cai para o texto de `.vg-badge-content`.
    """
    m = re.search(r'class="vg-badge"[^>]*\btitle="([^"]+)"', html)
    if m:
        return m.group(1).strip()
    m = re.search(r'vg-badge-content"\s*>([^<]+)<', html)
    return m.group(1).strip() if m else None


# --------------------------------------------------------------------------- #
# Movimentações (histórico do patrimônio)
# --------------------------------------------------------------------------- #
def movimentacoes_from_cells(finalidades: list[str], datas: list[str]) -> list[dict]:
    """Pareia colunas `finalidade` (= tipo) e `data` em [{'tipo','data'}].

    `data` em dd/mm/aaaa -> datetime. Linhas sem data válida são ignoradas.
    """
    out: list[dict] = []
    for tipo, d in zip(finalidades, datas):
        try:
            data = datetime.strptime((d or "").strip(), "%d/%m/%Y")
        except ValueError:
            continue
        out.append({"tipo": (tipo or "").strip(), "data": data})
    return out


def _cells_by_abbr(html: str, abbr: str) -> list[str]:
    pat = rf'abbr="{re.escape(abbr)}">\s*<div[^>]*>(.*?)</div>'
    vals = re.findall(pat, html, flags=re.DOTALL)
    return [re.sub(r"&nbsp;", " ", v).strip() for v in vals]


def movimentacoes_from_html(html: str) -> list[dict]:
    """Extrai as movimentações da tabela `patrimonio_patrimonio_movimentacao`."""
    finalidades = _cells_by_abbr(html, "patrimonio_movimentacao.finalidade")
    datas = _cells_by_abbr(html, "patrimonio_movimentacao.data_movimentacao")
    return movimentacoes_from_cells(finalidades, datas)
