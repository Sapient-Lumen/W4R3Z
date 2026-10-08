#!/usr/bin/env python3
"""scripts/check_example_ordering_conventions.py

Release-gate drift firewall: enforce a few *ordering conventions* in shipped example packets.

Why:
- Examples serve as templates; stable ordering reduces diff churn and avoids accidental
  ambiguity about how consumers should sort/merge.
- This check is intentionally narrow (examples only) to avoid constraining deployers.

Currently enforced:
1) OfficialChannelDirectory.channels MUST be sorted by channel_id ascending.
2) PublicNoticeFeed.entries MUST honor its declared ordering when ordering != unspecified.
   - issued_at_desc_notice_id_asc
   - issued_at_asc_notice_id_asc

This script is stdlib-only.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"

PKT_OFFICIAL_DIR = EXAMPLES / "evidence_packet_official_channel_directory"
PKT_NOTICE_FEED = EXAMPLES / "evidence_packet_public_notice_feed"


def die(msg: str) -> None:
    print("FAIL", msg, file=sys.stderr)
    raise SystemExit(2)


def _load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"unparseable_json:{p.relative_to(ROOT)}:{e}")


def _find_payload_path(packet_dir: Path) -> Path:
    mf = packet_dir / "manifest.json"
    m = _load_json(mf)
    arts = m.get("artifacts")
    if not isinstance(arts, list):
        die(f"manifest_missing_artifacts:{mf.relative_to(ROOT)}")

    # Convention: shipped packets name their detached payload artifact as "payload".
    for a in arts:
        if not isinstance(a, dict):
            continue
        if str(a.get("name", "")) == "payload":
            url = a.get("url")
            if isinstance(url, str) and url:
                return packet_dir / url

    # Fallback: first artifact under objects/ whose schema looks like a payload schema.
    for a in arts:
        if not isinstance(a, dict):
            continue
        url = a.get("url")
        schema = a.get("schema")
        if isinstance(url, str) and url.startswith("objects/") and isinstance(schema, str) and schema.startswith("schemas/"):
            return packet_dir / url

    die(f"payload_not_found:{mf.relative_to(ROOT)}")
    raise AssertionError


def _parse_dt(s: str) -> datetime:
    # Accept RFC3339-ish timestamps used in examples.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def check_official_channel_directory_ordering() -> None:
    if not PKT_OFFICIAL_DIR.exists():
        return
    payload_path = _find_payload_path(PKT_OFFICIAL_DIR)
    obj = _load_json(payload_path)
    channels = obj.get("channels")
    if not isinstance(channels, list):
        die(f"official_channel_directory_missing_channels:{payload_path.relative_to(ROOT)}")

    ids: list[str] = []
    for i, c in enumerate(channels):
        if not isinstance(c, dict):
            die(f"official_channel_directory_channel_not_object:{payload_path.relative_to(ROOT)}:{i}")
        cid = c.get("channel_id")
        if not isinstance(cid, str) or not cid.strip():
            die(f"official_channel_directory_channel_id_missing:{payload_path.relative_to(ROOT)}:{i}")
        ids.append(cid)

    if len(set(ids)) != len(ids):
        die(f"official_channel_directory_channel_id_duplicate:{payload_path.relative_to(ROOT)}")

    want = sorted(ids)
    if ids != want:
        die(
            "official_channel_directory_channels_not_sorted_by_channel_id:"
            f"{payload_path.relative_to(ROOT)}:got={ids}:want={want}"
        )


def check_public_notice_feed_ordering() -> None:
    if not PKT_NOTICE_FEED.exists():
        return
    payload_path = _find_payload_path(PKT_NOTICE_FEED)
    obj = _load_json(payload_path)

    ordering = str(obj.get("ordering", "unspecified") or "unspecified")
    entries = obj.get("entries")
    if not isinstance(entries, list):
        die(f"public_notice_feed_missing_entries:{payload_path.relative_to(ROOT)}")

    if ordering == "unspecified":
        return

    rows: list[tuple[datetime, str]] = []
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            die(f"public_notice_feed_entry_not_object:{payload_path.relative_to(ROOT)}:{i}")
        issued_at = e.get("issued_at")
        notice_id = e.get("notice_id")
        if not isinstance(notice_id, str) or not notice_id.strip():
            die(f"public_notice_feed_notice_id_missing:{payload_path.relative_to(ROOT)}:{i}")
        if not isinstance(issued_at, str) or not issued_at.strip():
            die(
                f"public_notice_feed_issued_at_required_for_ordering:{payload_path.relative_to(ROOT)}:{i}:{ordering}"
            )
        try:
            dt = _parse_dt(issued_at)
        except Exception:
            die(f"public_notice_feed_issued_at_unparseable:{payload_path.relative_to(ROOT)}:{i}:{issued_at}")
        rows.append((dt, notice_id))

    if ordering == "issued_at_desc_notice_id_asc":
        want = sorted(rows, key=lambda t: (-t[0].timestamp(), t[1]))
    elif ordering == "issued_at_asc_notice_id_asc":
        want = sorted(rows, key=lambda t: (t[0].timestamp(), t[1]))
    else:
        die(f"public_notice_feed_unknown_ordering:{payload_path.relative_to(ROOT)}:{ordering}")

    if rows != want:
        got = [f"{dt.isoformat()}|{nid}" for dt, nid in rows]
        exp = [f"{dt.isoformat()}|{nid}" for dt, nid in want]
        die(
            "public_notice_feed_entries_not_in_declared_order:"
            f"{payload_path.relative_to(ROOT)}:{ordering}:got={got}:want={exp}"
        )


def main() -> int:
    check_official_channel_directory_ordering()
    check_public_notice_feed_ordering()
    print("PASS: example ordering conventions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
