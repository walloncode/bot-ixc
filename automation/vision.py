"""Visão por template matching (OpenCV). Fallback quando o DOM não ajuda.

Função pura e isolada: recebe caminhos de imagem, devolve coordenada/centro.
Não toca em mouse nem em browser.
"""
from __future__ import annotations

from typing import Optional


def locate_template(
    haystack_path: str,
    needle_path: str,
    threshold: float = 0.85,
) -> Optional[tuple[int, int]]:
    """Retorna o centro (x, y) do `needle` dentro do `haystack`, ou None.

    `threshold` em [0,1]: confiança mínima do match.
    """
    import cv2
    import numpy as np

    haystack = cv2.imread(haystack_path, cv2.IMREAD_COLOR)
    needle = cv2.imread(needle_path, cv2.IMREAD_COLOR)
    if haystack is None or needle is None:
        return None

    result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return None

    h, w = needle.shape[:2]
    return (max_loc[0] + w // 2, max_loc[1] + h // 2)
