#!/usr/bin/env python3
"""Drift firewall: shipped example object stores must be self-consistent.

Example evidence packets rely on content-addressed objects stored under objects/.
To reduce ambiguity, reviewer confusion, and silent archive bloat, this check enforces
strong conventions for the archive's *shipped* examples:

1) Naming alignment:
   - Any referenced object URI under objects/ MUST be named sha256-<hex>.<ext>
     where <hex> matches the declared sha256 digest.

2) Byte-level integrity:
   - If the referenced object file exists, its sha256 over the bytes MUST match
     the declared digest.

3) No junk / no hidden bloat:
   - The objects/ directory in shipped examples MUST NOT contain non-content-
     addressed files.
   - The objects/ directory MUST NOT contain orphaned content-addressed files
     that are never referenced by any envelope pointer or manifest artifact.

This is not a universal requirement for all deployers, but it is a low-cost,
high-leverage drift firewall for the archive's own examples.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"

RE_SHA256 = re.compile(r"^sha256:([0-9a-fA-F]{64})$")


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def uri_hex_from_name(uri: str) -> str | None:
    """Return hex from 'sha256-<hex>.*' filename, else None."""
    name = Path(uri).name
    if not name.startswith("sha256-"):
        return None
    hexpart = name[len("sha256-") :].split(".", 1)[0]
    if re.fullmatch(r"[0-9a-fA-F]{64}", hexpart):
        return hexpart
    return None


def rel_object_path(ref_uri: str) -> str:
    """Normalize an object reference URI to a path relative to packet/objects/."""
    if ref_uri.startswith("objects/"):
        return ref_uri[len("objects/") :]
    return ref_uri


def check_ref(
    packet: Path,
    kind: str,
    ref_uri: str,
    digest: str,
    ctx: str,
    referenced: set[str],
) -> list[str]:
    problems: list[str] = []

    m = RE_SHA256.match(digest or "")
    if not m:
        problems.append(f"bad_digest:{kind}:{ctx}")
        return problems
    want = m.group(1).lower()

    if not isinstance(ref_uri, str) or not ref_uri:
        problems.append(f"missing_uri:{kind}:{ctx}")
        return problems

    rel = rel_object_path(ref_uri)

    got_hex = uri_hex_from_name(rel)
    if got_hex is None:
        problems.append(f"uri_not_content_addressed:{kind}:{ctx}:{ref_uri}")
        return problems
    if got_hex.lower() != want:
        problems.append(f"uri_digest_mismatch:{kind}:{ctx}:{ref_uri}")

    fp = packet / "objects" / rel
    if not fp.exists():
        problems.append(f"missing_object:{kind}:{ctx}:{ref_uri}")
        return problems

    referenced.add(Path(rel).as_posix())

    got = sha256_file(fp)
    if got.lower() != want:
        problems.append(f"object_hash_mismatch:{kind}:{ctx}:{ref_uri}")

    return problems


def check_packet(packet: Path) -> list[str]:
    problems: list[str] = []
    referenced: set[str] = set()

    objects = packet / "objects"

    env_dir = packet / "envelopes"
    if env_dir.exists():
        for env_path in sorted(env_dir.glob("*.json")):
            try:
                env = json.loads(env_path.read_text(encoding="utf-8"))
            except Exception:
                problems.append(f"envelope_unparseable:{packet.name}:{env_path.name}")
                continue

            # Detached payload pointer.
            ptr = env.get("payload_pointer")
            if isinstance(ptr, dict):
                uri = ptr.get("uri", "")
                dig = ptr.get("digest", "")
                if uri or dig:
                    problems += check_ref(packet, "payload_pointer", uri, dig, f"{env_path.name}", referenced)

            # Attachments.
            atts = env.get("attachments")
            if isinstance(atts, list):
                for i, att in enumerate(atts):
                    if not isinstance(att, dict):
                        continue
                    uri = att.get("uri", "")
                    dig = att.get("digest", "")
                    if uri or dig:
                        problems += check_ref(packet, "attachment", uri, dig, f"{env_path.name}:{i}", referenced)

    # Manifest artifact urls that point into objects/.
    mpath = packet / "manifest.json"
    if mpath.exists():
        try:
            m = json.loads(mpath.read_text(encoding="utf-8"))
            arts = m.get("artifacts", [])
        except Exception:
            arts = []
            problems.append(f"manifest_unparseable:{packet.name}")

        if isinstance(arts, list):
            for i, a in enumerate(arts):
                if not isinstance(a, dict):
                    continue
                url = a.get("url")
                if not isinstance(url, str) or not url.startswith("objects/"):
                    continue
                d = a.get("digest") or (("sha256:" + a["sha256"]) if "sha256" in a else "")
                if isinstance(d, str) and d:
                    problems += check_ref(packet, "manifest", url, d, f"{packet.name}:manifest:{i}", referenced)

    # Object store hygiene.
    if objects.exists():
        all_files = [p for p in objects.rglob("*") if p.is_file()]
        for p in all_files:
            rel = p.relative_to(objects).as_posix()
            if uri_hex_from_name(p.name) is None:
                problems.append(f"objects_dir_non_content_addressed:{packet.name}:{rel}")
                continue
            if rel not in referenced:
                problems.append(f"orphan_object_file:{packet.name}:{rel}")

    return problems


def main() -> int:
    if not EXAMPLES.exists():
        print("PASS: no examples directory")
        return 0

    packets = sorted([p for p in EXAMPLES.iterdir() if p.is_dir() and p.name.startswith("evidence_packet_")])
    problems: list[str] = []
    for pkt in packets:
        problems.extend(check_packet(pkt))

    if problems:
        for p in problems:
            fail(p)
        return 2

    print(f"PASS: object store integrity ({len(packets)} packet(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
