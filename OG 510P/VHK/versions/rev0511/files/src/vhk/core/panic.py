from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PanicConfig:
    panic_file: str = "/tmp/vhk_panic"


class PanicStop(RuntimeError):
    """Raised when the panic file exists."""


def panic_path(cfg: PanicConfig) -> Path:
    return Path(cfg.panic_file).expanduser().resolve()


def is_panicking(cfg: PanicConfig) -> bool:
    return panic_path(cfg).exists()


def set_panic(cfg: PanicConfig) -> Path:
    p = panic_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("panic\n")
    return p


def clear_panic(cfg: PanicConfig) -> None:
    p = panic_path(cfg)
    if p.exists():
        p.unlink()
