#!/usr/bin/env python3
"""Shared helpers for the synthetic Example County rehearsal.

This module intentionally stays small and stdlib-only except for importing the
existing observer verifier.  It centralizes the packet iteration and in-process
verification path used by the smoke, output-pack, and mission-kernel tools so
those tools do not drift into slightly different definitions of "the Example
County path".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "scenario.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_packet_refs(scenario: dict[str, Any]) -> Iterator[tuple[str, str, str, str]]:
    """Yield unique (phase_id, public_sentence, kind, relative_packet_path)."""

    seen: set[str] = set()
    for phase in scenario.get("phases") or []:
        if not isinstance(phase, dict):
            continue
        phase_id = str(phase.get("phase_id") or "")
        public_sentence = str(phase.get("public_sentence") or "")
        for packet in phase.get("packets") or []:
            if not isinstance(packet, dict):
                continue
            rel = str(packet.get("path") or "").strip()
            if not rel or rel in seen:
                continue
            seen.add(rel)
            yield phase_id, public_sentence, str(packet.get("kind") or "").strip(), rel


def verify_packet(rel: str) -> dict[str, Any]:
    """Verify one scenario packet using observer verifier primitives in-process."""

    tools_dir = str(ROOT / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    from observer_verify_packet import build_report, verify_envelopes, verify_manifest, verify_objects  # type: ignore

    packet_path = ROOT / rel
    problems: list[str] = []
    obj_problems, objects_checked = verify_objects(packet_path / "objects")
    problems += obj_problems
    env_problems, envelopes_checked, kinds_seen = verify_envelopes(packet_path / "envelopes", packet_path)
    problems += env_problems
    problems += verify_manifest(packet_path)
    out = build_report(packet_path, problems, envelopes_checked, objects_checked, kinds_seen, public=True)
    status = str(out.get("status") or "ERROR")
    problems_out = out.get("problems") if isinstance(out.get("problems"), list) else []
    return {
        "packet": rel,
        "returncode": 0 if status == "PASS" else 2,
        "status": status,
        "problems": problems_out,
        "stderr": "",
    }
