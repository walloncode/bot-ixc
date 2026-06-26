"""Fallback de automação via PyAutoGUI (mouse/teclado).

Usar SOMENTE quando o Playwright não alcança (popups nativos, apps externos).
`target` aqui é interpretado pela camada de visão (template/coordenada),
não por seletor DOM. Frágil por natureza -> preferir sempre o browser.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from loguru import logger

from config import settings
from models import ActionResult, ScreenState


class DesktopActuator:
    """Implementa `Actuator` com mouse/teclado. Resolução de `target` via visão."""

    def __init__(self, locate) -> None:
        # `locate(target) -> (x, y) | None`  (injetado pela camada de visão)
        self._locate = locate

    def _resolve(self, target: str):
        point = self._locate(target)
        if point is None:
            logger.warning("Desktop: target não localizado: {}", target)
        return point

    def click(self, target: str) -> ActionResult:
        import pyautogui

        point = self._resolve(target)
        if point is None:
            return ActionResult(success=False, message=f"click: {target} não encontrado")
        pyautogui.click(*point)
        return ActionResult(success=True, message=f"click {target}")

    def double_click(self, target: str) -> ActionResult:
        import pyautogui

        point = self._resolve(target)
        if point is None:
            return ActionResult(success=False, message=f"dblclick: {target} não encontrado")
        pyautogui.doubleClick(*point)
        return ActionResult(success=True, message=f"dblclick {target}")

    def type_text(self, target: str, value: str) -> ActionResult:
        import pyautogui

        if target:
            res = self.click(target)
            if not res.success:
                return res
        pyautogui.typewrite(value, interval=0.02)
        return ActionResult(success=True, message=f"type {target}")

    def scroll(self, target: str, amount: int = -300) -> ActionResult:
        import pyautogui

        pyautogui.scroll(amount)
        return ActionResult(success=True, message=f"scroll {amount}")

    def wait(self, target: str, timeout_ms: int = 10_000) -> ActionResult:
        # Espera ativa simples baseada em visão; refino fica para a camada de visão.
        import time

        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            if self._resolve(target) is not None:
                return ActionResult(success=True, message=f"wait {target}")
            time.sleep(0.3)
        return ActionResult(success=False, message=f"wait timeout: {target}")

    def press(self, target: str, key: str = "Enter") -> ActionResult:
        import pyautogui

        if target:
            res = self.click(target)
            if not res.success:
                return res
        pyautogui.press(key.lower())
        return ActionResult(success=True, message=f"press {key}")

    def get_text(self, target: str) -> Optional[str]:
        # Fallback desktop: leitura de texto exigiria OCR de região.
        # TODO: integrar automation.ocr.read_text com recorte por visão.
        logger.warning("get_text não suportado no DesktopActuator: {}", target)
        return None

    def get_texts(self, target: str) -> list[str]:
        logger.warning("get_texts não suportado no DesktopActuator: {}", target)
        return []

    def capture(self) -> ScreenState:
        import pyautogui

        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = Path(settings.log_path) / f"desk_{ts}.png"
        pyautogui.screenshot(str(path))
        return ScreenState(screenshot_path=str(path))
