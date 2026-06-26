"""Configuração central do agente. Fonte única de parâmetros de ambiente."""
from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # IXC
    ixc_base_url: str = ""
    ixc_user: str = ""
    ixc_password: str = ""

    # Navegador
    headless: bool = False

    # IA — só para exceções/ambiguidades
    ai_provider: str = "none"          # anthropic | openai | none
    ai_api_key: str = ""
    ai_model: str = "claude-opus-4-8"
    confidence_threshold: int = 85     # < threshold => confirmação humana

    # OCR
    tesseract_cmd: str = ""

    # Persistência / logs
    db_url: str = "sqlite:///./logs/agent.db"
    rules_file: str = "regras.md"
    log_dir: str = "logs"

    @property
    def rules_path(self) -> Path:
        return ROOT / self.rules_file

    @property
    def log_path(self) -> Path:
        p = ROOT / self.log_dir
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
