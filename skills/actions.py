"""Skills = ações atômicas. Uma responsabilidade cada.

`Actuator` é o CONTRATO. Flows e o agente dependem dele, nunca de Playwright
ou PyAutoGUI diretamente. Isso permite trocar a implementação e testar em
isolamento (ex.: um FakeActuator nos testes).
"""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from models import ActionResult, ScreenState


@runtime_checkable
class Actuator(Protocol):
    """Toda automação (browser, desktop) implementa este contrato."""

    def click(self, target: str) -> ActionResult: ...

    def double_click(self, target: str) -> ActionResult: ...

    def type_text(self, target: str, value: str) -> ActionResult: ...

    def scroll(self, target: str, amount: int = 0) -> ActionResult: ...

    def wait(self, target: str, timeout_ms: int = 10_000) -> ActionResult: ...

    def press(self, target: str, key: str = "Enter") -> ActionResult: ...

    def get_text(self, target: str) -> Optional[str]: ...

    def get_texts(self, target: str) -> list[str]: ...

    def capture(self) -> ScreenState: ...
