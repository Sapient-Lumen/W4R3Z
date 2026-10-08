#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_RE = re.compile(r'chatgpt-live-surface-contract-rev(\d+)-')


def _contract_rank(path: Path) -> tuple[int, str]:
    match = CONTRACT_RE.search(path.name)
    rev = int(match.group(1)) if match else -1
    return rev, path.name


def active_contract_paths(root: Path = ROOT) -> list[Path]:
    latest = root / 'validation' / 'latest'
    paths = [p for p in latest.glob('chatgpt-live-surface-contract-rev*-*.json') if p.is_file()]
    return sorted(paths, key=_contract_rank, reverse=True)


def active_contract_path(root: Path = ROOT) -> Path:
    paths = active_contract_paths(root)
    if paths:
        return paths[0]
    # Keep a predictable default for fresh trees and clearer error messages.
    return root / 'validation' / 'latest' / 'chatgpt-live-surface-contract-rev0338-2026.06.13.json'


def active_fixture_paths(root: Path = ROOT) -> list[Path]:
    latest = root / 'validation' / 'latest'
    paths = [p for p in latest.glob('chatgpt-live-surface-contract-fixture-rev*.json') if p.is_file()]
    return sorted(paths, key=_contract_rank, reverse=True)


def active_fixture_path(root: Path = ROOT) -> Path | None:
    paths = active_fixture_paths(root)
    return paths[0] if paths else None
