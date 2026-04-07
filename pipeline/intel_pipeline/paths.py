from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """pipeline/ 의 부모 = 저장소 루트."""
    return Path(__file__).resolve().parent.parent.parent


def vault_dir() -> Path:
    return repo_root() / "market-intel"


def config_dir() -> Path:
    return repo_root() / "config"


def state_dir() -> Path:
    p = repo_root() / "pipeline" / "state"
    p.mkdir(parents=True, exist_ok=True)
    return p


def state_db_path() -> Path:
    return state_dir() / "intel.sqlite"


def kpi_log_path() -> Path:
    p = repo_root() / "pipeline" / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p / "kpi.jsonl"
