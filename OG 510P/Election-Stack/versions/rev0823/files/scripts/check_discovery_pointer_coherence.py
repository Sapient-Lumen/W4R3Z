#!/usr/bin/env python3
"""scripts/check_discovery_pointer_coherence.py

Release-gate drift firewall: keep the Track A comms/discovery spine coherent.

This check is intentionally narrow and bounded. It validates that:
- channel_ids used in shipped example packets are registered in official-channels.csv
- the WellKnown discovery example's payload_sha256 pointers match the shipped example
  payload digests for OfficialChannelDirectory and PublicNoticeFeed
- key discovery URLs are consistent between OfficialChannelDirectory and WellKnown

Rationale:
- Prevent silent typos/renames in channel IDs and discovery URLs.
- Ensure the WellKnown example is a real comparability anchor, not a loose pointer bag.

This check does NOT attempt to validate live URLs or fetch network resources.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"
REG_OFFICIAL_CHANNELS = ROOT / "artifacts" / "registries" / "official-channels.csv"

PKT_OFFICIAL_DIR = EXAMPLES / "evidence_packet_official_channel_directory"
PKT_NOTICE_FEED = EXAMPLES / "evidence_packet_public_notice_feed"
PKT_WELL_KNOWN = EXAMPLES / "evidence_packet_well_known_discovery"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry_channel_ids(path: Path) -> Set[str]:
    ids: Set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            cid = (row.get("channel_id") or "").strip()
            if cid:
                ids.add(cid)
    return ids


def get_payload_sha_and_obj(packet_dir: Path) -> Tuple[str, Dict[str, Any]]:
    manifest = load_json(packet_dir / "manifest.json")
    if not isinstance(manifest, dict):
        raise ValueError("manifest not a dict")
    arts = manifest.get("artifacts")
    if not isinstance(arts, list):
        raise ValueError("manifest.artifacts not a list")
    payload = None
    for a in arts:
        if isinstance(a, dict) and a.get("name") == "payload":
            payload = a
            break
    if not isinstance(payload, dict):
        # fallback: first artifact whose schema is not EvidenceEnvelope
        for a in arts:
            if isinstance(a, dict) and str(a.get("schema") or "") != "schemas/EvidenceEnvelope.json":
                payload = a
                break
    if not isinstance(payload, dict):
        raise ValueError("payload artifact not found")

    sha = (payload.get("sha256") or "").strip()
    digest = (payload.get("digest") or "").strip()
    if not sha and digest.startswith("sha256:"):
        sha = digest.split(":", 1)[1]
    if not sha:
        raise ValueError("payload sha256 missing")

    url = (payload.get("url") or "").strip()
    if not url:
        raise ValueError("payload url missing")

    obj_path = (packet_dir / url).resolve()
    obj_path.relative_to(packet_dir.resolve())

    obj = load_json(obj_path)
    if not isinstance(obj, dict):
        raise ValueError("payload object not a dict")

    return ("sha256:" + sha, obj)


def domain_of(url: str) -> str:
    try:
        p = urlparse(url)
        return (p.hostname or "").lower()
    except Exception:
        return ""


def fail(failures: List[str], msg: str) -> None:
    failures.append(msg)


def main() -> int:
    failures: List[str] = []

    # Preconditions
    if not REG_OFFICIAL_CHANNELS.exists():
        return 0
    for pkt in [PKT_OFFICIAL_DIR, PKT_NOTICE_FEED, PKT_WELL_KNOWN]:
        if not pkt.exists():
            return 0

    reg_ids = load_registry_channel_ids(REG_OFFICIAL_CHANNELS)

    off_digest, off_payload = get_payload_sha_and_obj(PKT_OFFICIAL_DIR)
    feed_digest, feed_payload = get_payload_sha_and_obj(PKT_NOTICE_FEED)
    wk_digest, wk_payload = get_payload_sha_and_obj(PKT_WELL_KNOWN)

    # 1) Channel IDs referenced by example payloads must be registered.
    chs = off_payload.get("channels")
    if not isinstance(chs, list):
        fail(failures, "OfficialChannelDirectory payload: channels missing")
    else:
        for i, c in enumerate(chs):
            if not isinstance(c, dict):
                continue
            cid = str(c.get("channel_id") or "").strip()
            if cid and cid not in reg_ids:
                fail(failures, f"OfficialChannelDirectory payload: channels[{i}].channel_id {cid!r} not in official-channels.csv")

    entries = feed_payload.get("entries")
    if not isinstance(entries, list):
        fail(failures, "PublicNoticeFeed payload: entries missing")
    else:
        for i, e in enumerate(entries):
            if not isinstance(e, dict):
                continue
            chans = e.get("channels")
            if chans is None:
                continue
            if not isinstance(chans, list):
                fail(failures, f"PublicNoticeFeed payload: entries[{i}].channels not a list")
                continue
            for j, cid in enumerate(chans):
                s = str(cid or "").strip()
                if s and s not in reg_ids:
                    fail(failures, f"PublicNoticeFeed payload: entries[{i}].channels[{j}] {s!r} not in official-channels.csv")

    # 2) WellKnown payload digests must match shipped example payload digests.
    ptr = wk_payload.get("pointers")
    if not isinstance(ptr, dict):
        fail(failures, "WellKnownElectionStackDiscovery payload: pointers missing")
    else:
        got_off = str(ptr.get("official_channel_directory_payload_sha256") or "").strip()
        got_feed = str(ptr.get("public_notice_feed_payload_sha256") or "").strip()
        if got_off and got_off != off_digest:
            fail(failures, f"WellKnown pointers: official_channel_directory_payload_sha256 mismatch (got {got_off} want {off_digest})")
        if got_feed and got_feed != feed_digest:
            fail(failures, f"WellKnown pointers: public_notice_feed_payload_sha256 mismatch (got {got_feed} want {feed_digest})")

    # 3) Discovery URLs should be consistent between OfficialChannelDirectory.discovery and WellKnown.pointers.
    disc = off_payload.get("discovery")
    if not isinstance(disc, dict):
        fail(failures, "OfficialChannelDirectory payload: discovery missing")
    elif isinstance(ptr, dict):
        pairs = [
            ("keys_url", "keys_url"),
            ("public_notice_feed_url", "public_notice_feed_url"),
            ("status_board_url", "status_board_url"),
            ("well_known_url", "well_known_url"),
        ]
        for off_k, wk_k in pairs:
            off_v = str(disc.get(off_k) or "").strip()
            wk_v = str(ptr.get(wk_k) or "").strip()
            # For well_known_url, the WellKnown object doesn't include its own URL by definition.
            if off_k == "well_known_url":
                continue
            if off_v and wk_v and off_v != wk_v:
                fail(failures, f"Discovery URL mismatch: OfficialChannelDirectory.discovery.{off_k}={off_v!r} vs WellKnown.pointers.{wk_k}={wk_v!r}")

        # Primary domain should match pointer hostnames when present.
        primary = str(wk_payload.get("primary_domain") or "").strip().lower()
        if primary:
            for k in ["keys_url", "public_notice_feed_url", "official_channel_directory_url", "status_board_url"]:
                u = str(ptr.get(k) or "").strip()
                if not u:
                    continue
                d = domain_of(u)
                if d and d != primary:
                    fail(failures, f"WellKnown primary_domain {primary!r} does not match {k} hostname {d!r}")

    if failures:
        for f in failures:
            print("ERROR:", f)
        return 2

    print("PASS: discovery pointer coherence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
