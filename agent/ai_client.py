"""Cliente de IA. A IA NUNCA executa — só devolve `AIDecision` (JSON).

Uso restrito (regra #15): ambiguidades, múltiplas opções, erros desconhecidos.
Se confiança < threshold => o chamador pede confirmação humana.
"""
from __future__ import annotations

import json
from typing import Optional

from loguru import logger

from config import settings
from models import AIDecision

SYSTEM_PROMPT = (
    "Você é o módulo de decisão de um agente de automação do IXC. "
    "Responda SOMENTE com um JSON válido no formato: "
    '{"action":"click|type|scroll|wait|stop","target":"...",'
    '"value":"...|null","confidence":0-100,"reason":"..."}. '
    "Nunca invente dados. Se incerto, use confidence baixo."
)


class AIClient:
    """Provider-agnóstico. Sempre devolve `AIDecision` validado."""

    def __init__(self) -> None:
        self.provider = settings.ai_provider
        self.model = settings.ai_model

    def decide(self, prompt: str) -> AIDecision:
        """Recebe um prompt de contexto e devolve uma decisão estruturada."""
        if self.provider == "none" or not settings.ai_api_key:
            logger.warning("IA desabilitada -> decisão neutra (wait, confidence=0)")
            return AIDecision(action="wait", target="", confidence=0,
                              reason="IA desabilitada")

        raw = self._call_provider(prompt)
        return self._parse(raw)

    # ----- providers ----------------------------------------------------- #
    def _call_provider(self, prompt: str) -> str:
        if self.provider == "anthropic":
            from anthropic import Anthropic

            client = Anthropic(api_key=settings.ai_api_key)
            msg = client.messages.create(
                model=self.model,
                max_tokens=512,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text

        if self.provider == "openai":
            from openai import OpenAI

            client = OpenAI(api_key=settings.ai_api_key)
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            return resp.choices[0].message.content or "{}"

        raise ValueError(f"AI_PROVIDER desconhecido: {self.provider}")

    # ----- parsing defensivo --------------------------------------------- #
    @staticmethod
    def _parse(raw: str) -> AIDecision:
        try:
            data = json.loads(_extract_json(raw))
            return AIDecision.model_validate(data)
        except Exception as exc:  # noqa: BLE001
            logger.error("Falha ao parsear decisão da IA: {} | raw={}", exc, raw)
            return AIDecision(action="stop", target="", confidence=0,
                              reason="resposta da IA inválida")


def _extract_json(raw: str) -> str:
    start, end = raw.find("{"), raw.rfind("}")
    return raw[start : end + 1] if start != -1 and end != -1 else "{}"
