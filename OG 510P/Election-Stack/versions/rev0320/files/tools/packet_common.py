#!/usr/bin/env python3
"""tools/packet_common.py

Small helpers for reading canonical packet layouts.

Rationale:
Operator-facing tools (cards, verifiers) frequently need to:
  - locate an envelope under packet/envelopes/
  - locate a detached payload under packet/objects/
  - recompute payload_digest per docs/176

Centralizing the path+digest rules reduces silent drift across tools.

Normative reference: docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from jcs import dump_bytes as jcs_bytes

from envelope_common import canonicalize_payload_bytes_for_digest, sha256_hex
from path_safety import safe_join


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def find_envelope_by_kind(packet_dir: Path, kind: str) -> Optional[Path]:
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        return None
    for p in sorted(env_dir.glob("*.json")):
        try:
            env = load_json(p)
        except Exception:
            continue
        if env.get("kind") == kind:
            return p
    return None


def _normalize_object_uri(uri: str) -> str:
    # Some packets use object URIs like "objects/sha256-...". Normalize to objects/ relative.
    if uri.startswith("objects/"):
        return uri[len("objects/") :]
    return uri


def _objects_dir_for_base(base_dir: Path) -> Path:
    """Best-effort objects/ resolver.

    Callers typically pass:
      - packet_dir / "objects" (when starting from a packet)
      - envelope_path.parent   (when starting from an envelope file)

    We resolve to the nearest objects/ directory without allowing path traversal
    via payload_pointer.uri.
    """

    if base_dir.name == "objects":
        return base_dir
    if (base_dir / "objects").exists():
        return base_dir / "objects"
    if (base_dir.parent / "objects").exists():
        return base_dir.parent / "objects"
    return base_dir


def _load_detached_payload(env: Dict[str, Any], base_dir: Path) -> Tuple[bytes, str, str]:
    """Return (payload_bytes, where, media_type).

    base_dir is typically:
      - packet_dir / "objects"  (when starting from a packet)
      - envelope_path.parent     (best-effort when starting from an envelope file)
    """

    pp = env.get("payload_pointer")
    if not isinstance(pp, dict):
        raise SystemExit("Envelope has neither payload_inline nor payload_pointer")
    uri = pp.get("uri")
    if not isinstance(uri, str) or not uri:
        raise SystemExit("payload_pointer.uri missing")

    objects_dir = _objects_dir_for_base(base_dir)
    rel = _normalize_object_uri(uri)

    # Anchor detached payload lookups to the packet root (guards against objects/ symlink escapes).
    if objects_dir.name == "objects":
        anchor = objects_dir.parent
        rel2 = f"objects/{rel}"
    else:
        anchor = objects_dir
        rel2 = rel

    payload_path = safe_join(anchor, rel2)
    if not payload_path:
        raise SystemExit(f"Unsafe payload_pointer.uri: {uri!r}")
    if not payload_path.exists():
        raise SystemExit(f"Detached payload not found for uri={uri!r} (looked under {objects_dir})")
    hardened = safe_join(anchor, rel2, must_exist=True)
    if not hardened:
        raise SystemExit(f"Unsafe payload_pointer.uri (symlink escape): {uri!r}")

    media_type = str(pp.get("media_type") or pp.get("content_type") or "").strip()
    return hardened.read_bytes(), str(hardened), media_type


def load_payload_object(env: Dict[str, Any], base_dir: Path) -> Any:
    """Load payload as a JSON value (best-effort)."""

    if "payload_inline" in env:
        return env.get("payload_inline")

    try:
        payload_bytes, _, _ = _load_detached_payload(env, base_dir)
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None


def recompute_payload_digest(env: Dict[str, Any], base_dir: Path) -> Tuple[str, str]:
    """Recompute payload_digest per docs/176 (best-effort).

    Returns (payload_digest, note).
    """

    if "payload_inline" in env:
        payload_obj = env["payload_inline"]
        payload_bytes = jcs_bytes(payload_obj)
        return f"sha256:{sha256_hex(payload_bytes)}", "inline"

    payload_bytes, where, media_type = _load_detached_payload(env, base_dir)
    canon = str(env.get("canonicalization") or "").strip()
    bytes_to_hash, note = canonicalize_payload_bytes_for_digest(payload_bytes, media_type, canon)
    return f"sha256:{sha256_hex(bytes_to_hash)}", f"{where} ({note})"
