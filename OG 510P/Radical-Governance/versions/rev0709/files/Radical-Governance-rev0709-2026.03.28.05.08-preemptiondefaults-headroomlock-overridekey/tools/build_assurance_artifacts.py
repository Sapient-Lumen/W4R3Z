#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from archive_meta import current_revision

CURRENT_REV = current_revision()

ARTIFACT_RULES = {
    "assessment": ["assessment", "impact assessment", "peer review", "fria"],
    "register": ["register", "registry", "inventory", "list", "ledger", "head register", "allowlist", "allowlists"],
    "notice": ["notice", "explanation", "warning label", "system card"],
    "packet": ["packet", "dossier", "case log"],
    "log": ["log", "logs", "audit", "monitoring", "lease identifier"],
    "schedule": ["schedule", "retention", "deletion", "disposition", "lifecycle"],
    "waiver": ["waiver", "determination", "exception"],
    "runbook": ["runbook", "runbooks", "drill", "drills", "training"],
    "contract": ["procurement", "contract", "supplier", "escrow"],
    "test-or-rehearsal": ["test", "testing", "rehearsal", "sandbox", "beta", "pilot", "conformance"],
}


def infer_artifacts(*parts: str) -> list[str]:
    haystack = " ".join(parts).lower()
    matched = []
    for artifact, keywords in ARTIFACT_RULES.items():
        if any(keyword in haystack for keyword in keywords):
            matched.append(artifact)
    return sorted(matched)


def main() -> None:
    data = json.loads((ROOT / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    buckets: dict[str, list[dict]] = {k: [] for k in ARTIFACT_RULES}
    for note in data.get("notes", []):
        artifacts = infer_artifacts(note.get("slug", ""), note.get("title", ""), note.get("thesis", ""))
        for artifact in artifacts:
            buckets[artifact].append(
                {
                    "number": note.get("number"),
                    "file": note.get("file"),
                    "title": note.get("title"),
                }
            )

    payload = {
        "revision": CURRENT_REV,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "artifacts": {},
    }
    for artifact, notes in buckets.items():
        latest = notes[-1] if notes else None
        payload["artifacts"][artifact] = {
            "count": len(notes),
            "latest": latest,
            "notes": notes,
        }

    (ROOT / "ASSURANCE_ARTIFACTS.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("OK: wrote ASSURANCE_ARTIFACTS.json")


if __name__ == "__main__":
    main()
