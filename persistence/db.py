"""Persistência mínima em SQLite (MVP). Histórico de execuções, decisões e erros.

Trocar por PostgreSQL em produção mantendo as mesmas funções públicas.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from config import settings


def _db_file() -> Path:
    # db_url no formato sqlite:///./logs/agent.db
    raw = settings.db_url.replace("sqlite:///", "")
    return Path(raw)


def _connect() -> sqlite3.Connection:
    path = _db_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def init_db() -> None:
    with _connect() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS execucoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, patrimonio TEXT, etapa TEXT, status TEXT, detalhe TEXT
            );
            CREATE TABLE IF NOT EXISTS decisoes_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, action TEXT, target TEXT, confidence INTEGER, reason TEXT
            );
            CREATE TABLE IF NOT EXISTS erros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, etapa TEXT, mensagem TEXT, screenshot TEXT
            );
            """
        )


def log_execution(patrimonio: str, etapa: str, status: str, detalhe: str = "") -> None:
    with _connect() as con:
        con.execute(
            "INSERT INTO execucoes (ts, patrimonio, etapa, status, detalhe) "
            "VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), patrimonio, etapa, status, detalhe),
        )


def log_decision(action: str, target: str, confidence: int, reason: str) -> None:
    with _connect() as con:
        con.execute(
            "INSERT INTO decisoes_ia (ts, action, target, confidence, reason) "
            "VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), action, target, confidence, reason),
        )


def log_error(etapa: str, mensagem: str, screenshot: str = "") -> None:
    with _connect() as con:
        con.execute(
            "INSERT INTO erros (ts, etapa, mensagem, screenshot) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), etapa, mensagem, screenshot),
        )
