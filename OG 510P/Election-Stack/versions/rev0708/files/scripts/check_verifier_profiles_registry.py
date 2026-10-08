#!/usr/bin/env python3
"""scripts/check_verifier_profiles_registry.py

Drift firewall for artifacts/registries/verifier-profiles.csv.

Verifier profiles are a small publishable interoperability surface:
verifiers can claim profile IDs in `hfv.verifier.report` so observers can
compare "what kinds did this verifier actually support?".

This check enforces:
- exact column set
- stable formatting (no leading/trailing spaces)
- valid profile_id format
- required_kinds is a semicolon-separated, sorted, unique list
- every kind exists in artifacts/registries/envelope-kinds.csv
- deterministic order (sorted by profile_id)
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "verifier-profiles.csv"
KIND_REG = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"

PROFILE_ID_RE = re.compile(r"^tes\.verifier\.profile\.[a-z0-9_]+\.v[0-9]+$")
KIND_RE = re.compile(r"^[a-z0-9_.-]+$")


def load_known_kinds() -> set[str]:
    if not KIND_REG.exists():
        raise SystemExit(f"missing envelope kind registry: {KIND_REG}")
    with KIND_REG.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        if "kind" not in (r.fieldnames or []):
            raise SystemExit("envelope-kinds.csv missing 'kind' column")
        return {row["kind"].strip() for row in r if (row.get("kind") or "").strip()}


def main() -> int:
    if not REG.exists():
        print(f"ERROR: missing verifier profiles registry: {REG}", file=sys.stderr)
        return 2

    known_kinds = load_known_kinds()

    errors: list[str] = []
    ids: list[str] = []
    seen: set[str] = set()

    with REG.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        required = {"profile_id", "summary", "required_kinds"}
        if set(r.fieldnames or []) != required:
            print(
                f"ERROR: verifier-profiles.csv columns must be exactly {sorted(required)}; got {r.fieldnames}",
                file=sys.stderr,
            )
            return 2

        for i, row in enumerate(r, start=2):
            raw_id = row.get("profile_id") or ""
            raw_summary = row.get("summary") or ""
            raw_kinds = row.get("required_kinds") or ""

            pid = raw_id.strip()
            summary = raw_summary.strip()
            kinds_raw = raw_kinds.strip()

            if raw_id != pid:
                errors.append(f"line {i}: profile_id has leading/trailing whitespace")
            if raw_summary != summary:
                errors.append(f"line {i}: summary has leading/trailing whitespace")
            if raw_kinds != kinds_raw:
                errors.append(f"line {i}: required_kinds has leading/trailing whitespace")

            if not pid:
                errors.append(f"line {i}: profile_id must be non-empty")
                continue
            if not PROFILE_ID_RE.match(pid):
                errors.append(f"line {i}: invalid profile_id format: {pid!r}")

            if not summary:
                errors.append(f"line {i}: summary must be non-empty for {pid}")

            if pid in seen:
                errors.append(f"line {i}: duplicate profile_id: {pid}")
            seen.add(pid)
            ids.append(pid)

            # required_kinds: semicolon-separated list
            if not kinds_raw:
                errors.append(f"line {i}: required_kinds must be non-empty for {pid}")
                continue

            kinds = [k.strip() for k in kinds_raw.split(";") if k.strip()]
            if not kinds:
                errors.append(f"line {i}: required_kinds must contain at least one kind for {pid}")
                continue

            if any(not KIND_RE.match(k) for k in kinds):
                bad = [k for k in kinds if not KIND_RE.match(k)]
                errors.append(f"line {i}: invalid kind token(s) in {pid}: {bad}")

            if len(set(kinds)) != len(kinds):
                errors.append(f"line {i}: duplicate kinds listed for {pid}")

            if kinds != sorted(kinds):
                errors.append(f"line {i}: kinds must be sorted lexicographically for {pid}")

            unknown = [k for k in kinds if k not in known_kinds]
            if unknown:
                errors.append(f"line {i}: unknown kind(s) in {pid}: {unknown}")

    if ids != sorted(ids):
        errors.append("registry must be sorted by profile_id (lexicographic)")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
