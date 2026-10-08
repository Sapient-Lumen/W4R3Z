#!/usr/bin/env python3
"""Check required receipt/gossip attachments for core envelope kinds.

Authoritative registry:
- artifacts/registries/envelope-attachment-requirements.csv

Applies to example packets and example envelopes under artifacts/examples/.

This is a drift firewall against selective disclosure: if a kind promises
receipted + gossiped publication, examples must show how to do it and
verifiers can test it.
"""

from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "artifacts" / "examples"
REQS = ROOT / "artifacts" / "registries" / "envelope-attachment-requirements.csv"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def is_envelope(obj: object) -> bool:
    return (
        isinstance(obj, dict)
        and "envelope_version" in obj
        and "kind" in obj
        and "payload_schema" in obj
        and "payload_digest" in obj
    )


def find_packet_root(p: Path) -> Path | None:
    cur = p.resolve()
    for parent in [cur] + list(cur.parents):
        if (parent / "manifest.json").exists() and (parent / "objects").exists():
            return parent
    return None


def resolve_pointer(ptr: dict, packet_root: Path) -> Path | None:
    # uri is preferred if present
    uri = (ptr.get("uri") or "").strip()
    candidates: list[Path] = []
    if uri:
        candidates += [
            packet_root / "objects" / uri,
            packet_root / "envelopes" / uri,
            packet_root / uri,
        ]
    # digest filename fallback
    d = ptr.get("digest", "")
    if d.startswith("sha256:"):
        hx = d.split(":", 1)[1]
        for base in [packet_root / "objects", packet_root / "envelopes", packet_root]:
            for ext in [".json", ".bin", ".txt", ".md", ".csv", ".toml", ""]:
                candidates.append(base / f"sha256-{hx}{ext}")

    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


def load_requirements() -> dict[str, list[dict[str, str]]]:
    if not REQS.exists():
        raise SystemExit(f"Missing requirements registry: {REQS}")
    out: dict[str, list[dict[str, str]]] = {}
    with REQS.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        needed = {"kind", "rel", "required", "media_type", "attachment_schema", "description"}
        if set(reader.fieldnames or []) != needed:
            raise SystemExit(f"Attachment requirements columns must be exactly {sorted(needed)}; got {reader.fieldnames}")
        for row in reader:
            out.setdefault(row["kind"].strip(), []).append({k: row[k].strip() for k in needed})
    return out


def main() -> int:
    reqs = load_requirements()
    errors: list[str] = []

    for p in EXAMPLES_DIR.rglob("*.json"):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not is_envelope(obj):
            continue

        kind = str(obj.get("kind", "")).strip()
        needed = reqs.get(kind)
        if not needed:
            continue

        packet_root = find_packet_root(p)
        if not packet_root:
            errors.append(f"Envelope with attachment requirements not inside a packet (needs objects/ + manifest.json): {p.relative_to(ROOT)}")
            continue

        atts = obj.get("attachments") or []
        if not isinstance(atts, list):
            errors.append(f"attachments must be an array: {p.relative_to(ROOT)}")
            continue

        # index by rel
        byrel: dict[str, list[dict]] = {}
        for a in atts:
            if not isinstance(a, dict):
                continue
            r = str(a.get("rel", "")).strip()
            if r:
                byrel.setdefault(r, []).append(a)

        for r in needed:
            if r["required"].lower() != "yes":
                continue
            rel = r["rel"]
            if rel not in byrel:
                errors.append(f"Missing required attachment rel={rel} for {kind} in {p.relative_to(ROOT)}")
                continue

            # verify each pointer at least resolves and hashes
            for ptr in byrel[rel]:
                target = resolve_pointer(ptr, packet_root)
                if not target:
                    errors.append(f"Attachment missing for rel={rel} digest={ptr.get('digest')} in {p.relative_to(ROOT)}")
                    continue
                got = sha256_bytes(target.read_bytes())
                want = str(ptr.get("digest", "")).split(":")[-1]
                if got.lower() != want.lower():
                    errors.append(f"Attachment digest mismatch rel={rel} file={target.relative_to(packet_root)} in {p.relative_to(ROOT)}")

                mt = (ptr.get("media_type") or ptr.get("content_type") or "").strip()
                if mt and mt != r["media_type"]:
                    errors.append(f"Attachment media_type mismatch rel={rel} got={mt} expected={r['media_type']} in {p.relative_to(ROOT)}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
