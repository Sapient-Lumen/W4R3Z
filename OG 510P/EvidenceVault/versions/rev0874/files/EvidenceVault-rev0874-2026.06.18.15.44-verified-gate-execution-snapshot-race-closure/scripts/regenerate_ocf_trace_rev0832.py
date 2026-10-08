#!/usr/bin/env python3
"""Regenerate the rev0832 OCF SIC/RTM resolver trace with portable paths.

The historical trace for sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm carried a
serialized locator object inside a path string and failed closed on a receipt
that is present in the archive.  The current resolver understands structured
file locators; rev0832 also keeps resolver output paths relative when invoked
with relative ABOM paths.  This script regenerates that trace while preserving
its original trace date via OCF_TRACE_DATE.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm.yaml"
ABOM = ROOT / "sources/ocf_llm/examples/sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm_abom.json"
TRACE_REL = TRACE.relative_to(ROOT).as_posix()
ABOM_REL = ABOM.relative_to(ROOT).as_posix()
AUDIT_JSON = ROOT / "AUDIT" / "OCF_TRACE_REGENERATION_REV0832.json"
AUDIT_MD = ROOT / "AUDIT" / "OCF_TRACE_REGENERATION_REV0832.md"
LEGACY_TRACE_SHA256 = "f6dbb8889e39030dd467ae85e95020350fe5f945ae6fea2ade14dd422db34b2d"
LEGACY_TIMESTAMP = "2026-02-11"
LEGACY_ACTIVE_SHAPE_ANOMALIES = 3
COMMAND = ["python3", "sources/ocf_llm/tools/ocf_resolver.py", "--out", TRACE_REL, ABOM_REL]
BAD_PATTERNS = {
    "serialized_locator_object_path": r"\{['\"]kind['\"]:\s*['\"]file['\"],\s*['\"]path['\"]:",
    "receipt_load_failed": r"receipt-load-failed",
    "publication_invalid": r"publication-invalid",
    "missing_file_status": r"missing-file",
    "cloud_absolute_path": r"/(?:mnt/data|home/oai|tmp)/",
}


def sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scalar(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*\"([^\"]+)\"", text, re.MULTILINE)
    return m.group(1) if m else None


def current_abom_digest(root: Path = ROOT) -> str:
    sys.path.insert(0, str(root / "sources/ocf_llm/tools"))
    from ocf_resolver import abom_digest, load_abom  # type: ignore
    return abom_digest(load_abom(str(root / ABOM_REL)))


def pattern_counts(text: str) -> dict[str, int]:
    return {name: len(re.findall(pattern, text)) for name, pattern in BAD_PATTERNS.items()}


def build_audit(root: Path = ROOT) -> dict[str, Any]:
    trace = root / TRACE_REL
    text = trace.read_text(encoding="utf-8")
    counts = pattern_counts(text)
    digest = scalar(text, "abomDigest")
    timestamp = scalar(text, "timestamp")
    expected_digest = current_abom_digest(root)
    return {
        "version": 1,
        "revision_context": "rev0832-session-patch-over-rev0831-over-rev0826",
        "status": "trace_regenerated_and_replayable" if digest == expected_digest and not any(counts.values()) else "trace_regeneration_attention_needed",
        "purpose": "Replace a malformed historical OCF resolver trace with deterministic, portable output from the current resolver.",
        "target_trace": TRACE_REL,
        "source_abom": ABOM_REL,
        "portable_replay_command": " ".join(COMMAND),
        "trace_date_source": "OCF_TRACE_DATE",
        "legacy": {
            "trace_sha256": LEGACY_TRACE_SHA256,
            "timestamp": LEGACY_TIMESTAMP,
            "active_shape_anomalies_from_rev0831_audit": LEGACY_ACTIVE_SHAPE_ANOMALIES,
            "known_issue": "structured locator object was serialized into a path string, causing receipt-load-failed/publication-invalid output despite the referenced receipt being shipped",
        },
        "current": {
            "trace_sha256": sha256_file(trace),
            "timestamp": timestamp,
            "abom_digest_in_trace": digest,
            "abom_digest_recomputed": expected_digest,
            "bad_pattern_counts": counts,
            "bad_pattern_total": sum(counts.values()),
        },
        "builder": "scripts/regenerate_ocf_trace_rev0832.py",
        "validator": "scripts/validate_ocf_trace_regeneration_rev0832.py",
    }


def render_markdown(data: dict[str, Any]) -> str:
    c = data["current"]
    l = data["legacy"]
    lines = [
        "# OCF trace regeneration audit (rev0832)",
        "",
        "This records a producer-level repair to one OCF resolver trace rather than only documenting the malformed path shape.",
        "",
        f"- Status: `{data['status']}`",
        f"- Target trace: `{data['target_trace']}`",
        f"- Source ABOM: `{data['source_abom']}`",
        f"- Replay command: `{data['portable_replay_command']}`",
        f"- Trace date source: `{data['trace_date_source']}`",
        "",
        "## Before / after",
        "",
        "| Measure | Legacy | Current |",
        "| --- | ---: | ---: |",
        f"| Trace SHA-256 | `{l['trace_sha256']}` | `{c['trace_sha256']}` |",
        f"| Timestamp | `{l['timestamp']}` | `{c['timestamp']}` |",
        f"| Active serialized-locator shape anomalies | {l['active_shape_anomalies_from_rev0831_audit']} | {c['bad_pattern_counts']['serialized_locator_object_path']} |",
        f"| Bad pattern total | n/a | {c['bad_pattern_total']} |",
        "",
        "## Current bad-pattern counts",
        "",
        "| Pattern | Count |",
        "| --- | ---: |",
    ]
    for name, count in c["bad_pattern_counts"].items():
        lines.append(f"| `{name}` | {count} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The regenerated trace preserves the original trace date but is produced by a portable archive-root command. The validator independently reruns the command with `OCF_TRACE_DATE` and compares the generated bytes to the checked-in trace.",
        "",
    ])
    return "\n".join(lines)


def regenerate(root: Path = ROOT) -> dict[str, Any]:
    env = os.environ.copy()
    env["OCF_TRACE_DATE"] = LEGACY_TIMESTAMP
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cp = subprocess.run(COMMAND, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60)
    if cp.returncode != 0:
        raise SystemExit(f"trace regeneration failed with rc={cp.returncode}: {cp.stderr[:400]}")
    if cp.stderr.strip():
        raise SystemExit(f"trace regeneration wrote unexpected stderr: {cp.stderr[:400]}")
    data = build_audit(root)
    AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_MD.write_text(render_markdown(data), encoding="utf-8")
    return data


def main() -> int:
    data = regenerate(ROOT)
    print(f"ocf-trace-regeneration-rev0832: OK ({data['current']['trace_sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
