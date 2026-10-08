#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import GENERATED, current_revision, generated_at_utc

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
    "contract": ["procurement", "contract", "supplier", "escrow", "compact", "service-level"],
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
    data = json.loads((GENERATED / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    buckets: dict[str, list[dict]] = {k: [] for k in ARTIFACT_RULES}
    for note in data.get("notes", []):
        file_slug = note.get("file", "").split("/", 1)[-1].rsplit(".", 1)[0].split("-", 1)[-1]
        artifacts = infer_artifacts(file_slug, note.get("title", ""), note.get("thesis", ""), " ".join(note.get("tags", [])))
        for artifact in artifacts:
            buckets[artifact].append({"number": note.get("number"), "file": note.get("file"), "title": note.get("title")})

    payload = {"revision": CURRENT_REV, "generated_at_utc": generated_at_utc(), "artifacts": {}}
    for artifact, notes in buckets.items():
        payload["artifacts"][artifact] = {"count": len(notes), "latest": notes[-1] if notes else None, "notes": notes}

    (GENERATED / "ASSURANCE_ARTIFACTS.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OK: wrote generated/ASSURANCE_ARTIFACTS.json")


if __name__ == "__main__":
    main()
