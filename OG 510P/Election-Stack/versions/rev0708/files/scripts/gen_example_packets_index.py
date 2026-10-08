#!/usr/bin/env python3
"""scripts/gen_example_packets_index.py

Generate a small, implementer-facing index of shipped example evidence packets.

Why:
- Example packets are the fastest "runnable" entry point for new implementers.
- This index is intentionally compact (bounded) and derives all technical fields
  from packet envelopes rather than duplicating content in prose.

Output:
- docs/213-example-packets-index.md

Policy:
- stdlib-only
- deterministic ordering
- do not embed payload bodies or large artifacts
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"
OUT = ROOT / "docs" / "213-example-packets-index.md"


def find_packets() -> list[Path]:
    out: list[Path] = []
    if not EXAMPLES.exists():
        return out
    for p in sorted(EXAMPLES.iterdir()):
        if p.is_dir() and p.name.startswith("evidence_packet_"):
            if (p / "manifest.json").exists() and (p / "envelopes").exists() and (p / "objects").exists():
                out.append(p)
    return out


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def envelope_paths(packet: Path) -> list[Path]:
    return sorted((packet / "envelopes").glob("*.json"))


def summarize_packet(packet: Path) -> dict:
    envs = []
    kinds: set[str] = set()
    schemas: set[str] = set()
    rels: set[str] = set()

    for ep in envelope_paths(packet):
        obj = load_json(ep)
        envs.append(obj)
        k = obj.get("kind")
        s = obj.get("payload_schema")
        if isinstance(k, str):
            kinds.add(k)
        if isinstance(s, str):
            schemas.add(s)
        for att in obj.get("attachments", []) or []:
            r = att.get("rel")
            if isinstance(r, str):
                rels.add(r)

    is_bundle = len(envs) != 1

    return {
        "name": packet.name,
        "bundle": is_bundle,
        "kinds": sorted(kinds),
        "schemas": sorted(schemas),
        "attachments": sorted(rels),
        "verify": f"python3 tools/observer_verify_packet.py artifacts/examples/{packet.name}",
    }


def main() -> int:
    packets = [summarize_packet(p) for p in find_packets()]

    lines: list[str] = []
    lines.append("# 213 — Example packets index")
    lines.append("")
    lines.append("**Track:** Shared")
    lines.append("")
    lines.append("> Generated file. Do not hand-edit. Source: scripts/gen_example_packets_index.py")
    lines.append("")
    lines.append("Shipped example evidence packets are small, runnable packets intended to clarify the evidence API surface without embedding large artifacts.")
    lines.append("")
    lines.append("## Index")
    lines.append("")
    lines.append("| Packet directory | Envelope kind(s) | Payload schema(s) | Attachment rel(s) | Verify |")
    lines.append("|---|---|---|---|---|")

    for p in packets:
        name = f"`{p['name']}`"
        kinds = "; ".join(f"`{k}`" for k in p["kinds"]) or "—"
        schemas = "; ".join(f"`{s}`" for s in p["schemas"]) or "—"
        atts = "; ".join(f"`{a}`" for a in p["attachments"]) or "—"
        verify = f"`{p['verify']}`"
        lines.append(f"| {name} | {kinds} | {schemas} | {atts} | {verify} |")

    lines.append("")
    lines.append("Notes:")
    lines.append("- Bundle packets contain multiple envelopes; single-envelope packets are minimal representatives for one envelope kind.")
    lines.append("- Verification checks digests and pointer integrity; signatures in examples are placeholders unless stated otherwise.")
    lines.append("")

    content = "\n".join(lines)
    OUT.write_text(content, encoding="utf-8")
    print(f"WROTE: {OUT.relative_to(ROOT)} ({len(content.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())