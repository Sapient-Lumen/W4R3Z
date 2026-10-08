#!/usr/bin/env python3
"""Fail if the archive contains private key material.

Why this exists:
- This repository is often edited by humans and LLMs.
- Accidental inclusion of *secret* key bytes (PEM/PKCS8/OpenSSH) would be catastrophic.

This check is intentionally conservative and does not try to be a full secret scanner.
It targets the highest-risk failure mode: shipping private key blocks or keyfiles.

Scope:
- scans all files under the repo root
- excludes common cache/build directories and operator-local caches
- flags:
  * PEM/OpenSSH private key headers
  * common private-key file extensions (.pem/.key/.p12/.pfx)

Output:
- prints file paths and match type only (does NOT print key material)
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIR_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
}

EXCLUDE_PREFIXES = {
    "evidence/cache/",
}

# High-signal private key headers.
PRIVATE_KEY_HEADER_RE = re.compile(
    rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"
)

# Keyfile extensions we should never ship.
FORBIDDEN_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}

# Common filenames that imply secret key material.
FORBIDDEN_FILENAMES = {
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()

    if any(rel.startswith(pfx) for pfx in EXCLUDE_PREFIXES):
        return True

    parts = set(Path(rel).parts)
    if parts.intersection(EXCLUDE_DIR_PARTS):
        return True

    # Skip VCS dir if present.
    if rel.startswith(".git/"):
        return True

    return False


def scan_file(path: Path) -> list[str]:
    findings: list[str] = []

    # Strong filename heuristics.
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        findings.append(f"forbidden extension '{path.suffix.lower()}'")
    if path.name in FORBIDDEN_FILENAMES:
        findings.append(f"forbidden filename '{path.name}'")

    # Content scan (streamed).
    try:
        with path.open("rb") as f:
            # keep a small sliding window across chunk boundaries
            tail = b""
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                data = tail + chunk
                if PRIVATE_KEY_HEADER_RE.search(data):
                    findings.append("private key header")
                    break
                tail = data[-256:]
    except Exception as e:
        findings.append(f"unreadable ({e})")

    return findings


def main() -> int:
    bad: list[str] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if should_skip(p):
            continue

        findings = scan_file(p)
        if findings:
            rel = p.relative_to(ROOT).as_posix()
            bad.append(f"{rel}: {', '.join(sorted(set(findings)))}")

    if bad:
        print("FAIL: possible private key material detected")
        for line in bad:
            print(" -", line)
        return 2

    print("PASS: no private key material detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
