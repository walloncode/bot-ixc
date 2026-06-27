"""Automação principal via Playwright. Implementa o contrato `Actuator`.

Estável e previsível: usa seletores e espera explícita de elementos.
`target` é sempre um seletor Playwright (CSS/text/xpath) — definido em
`flows/selectors.py`, nunca inventado aqui.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from config import settings
from models import ActionResult, ScreenState


class BrowserActuator:
    """Wrapper fino sobre Playwright. Cada método = uma ação atômica."""

    def __init__(self, headless: Optional[bool] = None) -> None:
        self._headless = settings.headless if headless is None else headless
        self._pw = None
        self._browser = None
        self.page = None

    # ----- ciclo de vida ------------------------------------------------- #
    def start(self) -> None:
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self._headless)
        self.page = self._browser.new_page()
        logger.info("Browser iniciado (headless={})", self._headless)

    def goto(self, url: str) -> ActionResult:
        try:
            self.page.goto(url)
            return ActionResult(success=True, message=f"goto {url}")
        except Exception as exc:  # noqa: BLE001 - reportado, não derruba o fluxo
            return ActionResult(success=False, message=f"goto falhou: {exc}")

    def stop(self) -> None:
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()
        logger.info("Browser encerrado")

    # ----- skills atômicas ----------------------------------------------- #
    def click(self, target: str) -> ActionResult:
        try:
            self.page.click(target)
            return ActionResult(success=True, message=f"click {target}")
        except Exception as exc:  # noqa: BLE001 - reportado, não engolido
            return ActionResult(success=False, message=f"click falhou: {exc}")

    def double_click(self, target: str) -> ActionResult:
        try:
            self.page.dblclick(target)
            return ActionResult(success=True, message=f"dblclick {target}")
        except Exception as exc:  # noqa: BLE001
            return ActionResult(success=False, message=f"dblclick falhou: {exc}")

    def type_text(self, target: str, value: str) -> ActionResult:
        try:
            self.page.fill(target, value)
            return ActionResult(success=True, message=f"type {target}")
        except Exception as exc:  # noqa: BLE001
            return ActionResult(success=False, message=f"type falhou: {exc}")

    def scroll(self, target: str, amount: int = 0) -> ActionResult:
        try:
            self.page.locator(target).scroll_into_view_if_needed()
            return ActionResult(success=True, message=f"scroll {target}")
        except Exception as exc:  # noqa: BLE001
            return ActionResult(success=False, message=f"scroll falhou: {exc}")

    def wait(self, target: str, timeout_ms: int = 10_000) -> ActionResult:
        try:
            self.page.wait_for_selector(target, timeout=timeout_ms)
            return ActionResult(success=True, message=f"wait {target}")
        except Exception as exc:  # noqa: BLE001
            return ActionResult(success=False, message=f"wait falhou: {exc}")

    def press(self, target: str, key: str = "Enter") -> ActionResult:
        try:
            self.page.press(target, key)
            return ActionResult(success=True, message=f"press {key} em {target}")
        except Exception as exc:  # noqa: BLE001
            return ActionResult(success=False, message=f"press falhou: {exc}")

    def get_text(self, target: str) -> Optional[str]:
        try:
            text = self.page.locator(target).first.inner_text()
            return text.strip() or None
        except Exception as exc:  # noqa: BLE001
            logger.warning("get_text falhou em {}: {}", target, exc)
            return None

    def get_texts(self, target: str) -> list[str]:
        try:
            return [t.strip() for t in self.page.locator(target).all_inner_texts()]
        except Exception as exc:  # noqa: BLE001
            logger.warning("get_texts falhou em {}: {}", target, exc)
            return []

    def capture(self) -> ScreenState:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = Path(settings.log_path) / f"shot_{ts}.png"
        self.page.screenshot(path=str(path))
        return ScreenState(screenshot_path=str(path), url=self.page.url)
