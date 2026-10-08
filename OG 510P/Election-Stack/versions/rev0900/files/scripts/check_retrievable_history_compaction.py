#!/usr/bin/env python3
"""Validate all in-carrier retrievable-history compaction bridges.

Historical releases keep superseded paths as fail-closed JSON stubs.  Their
original bytes must remain recoverable from deterministic tar+gzip bundles in
this same release carrier.  This checker is intentionally multi-revision: a
current release may retain older compaction reports and add a new compaction
slice without invalidating the older one.
"""
from __future__ import annotations

import hashlib
import json
import re
import stat
import sys
import tarfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPORT_GLOB = "rev*-retrievable-history-compaction.json"
REV_RE = re.compile(r"^v(\d+)$")


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def version_number(raw: str) -> int | None:
    m = REV_RE.match(str(raw))
    return int(m.group(1)) if m else None


def safe_rel(raw: object) -> str | None:
    if not isinstance(raw, str) or not raw or raw.startswith("/") or "\\" in raw or "\x00" in raw:
        return None
    parts = raw.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return raw


def validate_report(report_path: Path, current_rev: int, errors: list[str]) -> dict[str, int]:
    label = report_path.relative_to(ROOT).as_posix()
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(errors, f"{label}: unreadable compaction report: {exc}")
        return {"targets": 0, "members": 0, "bundle_bytes": 0, "net": 0}

    report_rev = version_number(report.get("archive_version"))
    if report_rev is None:
        fail(errors, f"{label}: invalid archive_version")
    elif report_rev > current_rev:
        fail(errors, f"{label}: future archive_version {report.get('archive_version')!r} for current {VERSION!r}")

    compaction_id = report.get("compaction_id")
    if not isinstance(compaction_id, str) or not compaction_id:
        fail(errors, f"{label}: missing compaction_id")

    bundle_meta = report.get("bundle") if isinstance(report.get("bundle"), dict) else {}
    bundle_rel = safe_rel(bundle_meta.get("path"))
    if bundle_rel is None:
        fail(errors, f"{label}: missing or unsafe bundle.path")
        bundle = ROOT / "missing"
    else:
        bundle = ROOT / bundle_rel

    try:
        bst = bundle.lstat()
        if stat.S_ISLNK(bst.st_mode) or not stat.S_ISREG(bst.st_mode):
            fail(errors, f"{label}: history bundle is not a concrete regular file")
        bundle_bytes = bundle.read_bytes()
    except OSError as exc:
        fail(errors, f"{label}: unreadable history bundle: {exc}")
        bundle_bytes = b""

    if bundle_bytes:
        if len(bundle_bytes) != bundle_meta.get("size_bytes"):
            fail(errors, f"{label}: history bundle size does not match report")
        if sha256(bundle_bytes) != bundle_meta.get("sha256"):
            fail(errors, f"{label}: history bundle SHA-256 does not match report")
        if len(bundle_bytes) < 10 or bundle_bytes[:3] != b"\x1f\x8b\x08":
            fail(errors, f"{label}: history bundle is not a gzip stream")
        elif int.from_bytes(bundle_bytes[4:8], "little") != 0:
            fail(errors, f"{label}: history bundle gzip mtime is not deterministic zero")

    targets = report.get("targets") if isinstance(report.get("targets"), list) else []
    if len(targets) != report.get("scope", {}).get("compacted_target_count"):
        fail(errors, f"{label}: compacted target count mismatch")
    by_path: dict[str, dict] = {}
    expected_members: set[str] = set()
    original_total = 0
    stub_total = 0
    for idx, row in enumerate(targets):
        if not isinstance(row, dict):
            fail(errors, f"{label}: targets[{idx}] is not an object")
            continue
        rel = safe_rel(row.get("path"))
        if rel is None:
            fail(errors, f"{label}: targets[{idx}] has unsafe path")
            continue
        if rel in by_path:
            fail(errors, f"{label}: duplicate target path: {rel}")
            continue
        by_path[rel] = row
        expected_members.add(rel)
        path = ROOT / rel
        try:
            pst = path.lstat()
            if stat.S_ISLNK(pst.st_mode) or not stat.S_ISREG(pst.st_mode):
                fail(errors, f"{label}: target stub is not a concrete regular file: {rel}")
                continue
            raw = path.read_bytes()
            stub = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            fail(errors, f"{label}: unreadable target stub {rel}: {exc}")
            continue
        if len(raw) != row.get("stub_bytes"):
            fail(errors, f"{label}: stub byte count mismatch: {rel}")
        if stub.get("compacted_historical_artifact") is not True:
            fail(errors, f"{label}: missing compacted_historical_artifact marker: {rel}")
        if stub.get("compaction_id") != compaction_id:
            fail(errors, f"{label}: compaction_id mismatch: {rel}")
        if stub.get("path") != rel:
            fail(errors, f"{label}: stub path binding mismatch: {rel}")
        if stub.get("original_sha256") != row.get("sha256"):
            fail(errors, f"{label}: stub original SHA mismatch: {rel}")
        if stub.get("original_size_bytes") != row.get("bytes"):
            fail(errors, f"{label}: stub original size mismatch: {rel}")
        retrieval = stub.get("retrieval") if isinstance(stub.get("retrieval"), dict) else {}
        if retrieval.get("format") != "tar+gzip" or retrieval.get("bundle_path") != bundle_rel or retrieval.get("member_path") != rel:
            fail(errors, f"{label}: stub retrieval binding mismatch: {rel}")
        if not isinstance(row.get("bytes"), int) or row["bytes"] < 1:
            fail(errors, f"{label}: invalid original byte count: {rel}")
        else:
            original_total += row["bytes"]
        stub_total += len(raw)

    sidecars = report.get("policy_sidecars_rebound_to_stub_bytes")
    if not isinstance(sidecars, list):
        sidecars = []
        fail(errors, f"{label}: policy sidecar ledger missing")
    for idx, row in enumerate(sidecars):
        if not isinstance(row, dict):
            fail(errors, f"{label}: policy sidecars[{idx}] is not an object")
            continue
        side_rel = safe_rel(row.get("path"))
        payload_rel = safe_rel(row.get("now_binds_stub_path"))
        if side_rel is None or payload_rel is None:
            fail(errors, f"{label}: policy sidecars[{idx}] path binding missing")
            continue
        expected_members.add(side_rel)
        try:
            payload = (ROOT / payload_rel).read_bytes()
            side_text = (ROOT / side_rel).read_text(encoding="utf-8")
        except OSError as exc:
            fail(errors, f"{label}: policy sidecar binding unreadable: {side_rel}: {exc}")
            continue
        digest = hashlib.sha256(payload).hexdigest()
        expected_line = f"{digest}  {Path(payload_rel).name}\n"
        legacy_expected_line = f"sha256:{digest}  {Path(payload_rel).name}\n"
        if side_text not in {expected_line, legacy_expected_line} or row.get("stub_sha256") != "sha256:" + digest:
            fail(errors, f"{label}: policy sidecar does not bind shipped stub bytes: {side_rel}")

    member_data: dict[str, bytes] = {}
    if bundle_bytes:
        try:
            with tarfile.open(bundle, mode="r:gz") as tf:
                members = tf.getmembers()
                names = [m.name for m in members]
                if names != sorted(names) or len(names) != len(set(names)):
                    fail(errors, f"{label}: history bundle members are not unique lexicographic entries")
                if set(names) != expected_members:
                    missing = sorted(expected_members - set(names))[:10]
                    extra = sorted(set(names) - expected_members)[:10]
                    fail(errors, f"{label}: history bundle member set differs from target plus preserved-sidecar ledger; missing={missing} extra={extra}")
                for m in members:
                    if not m.isfile() or m.issym() or m.islnk():
                        fail(errors, f"{label}: unsafe history bundle member type: {m.name}")
                        continue
                    if m.mtime != 0 or m.uid != 0 or m.gid != 0 or stat.S_IMODE(m.mode) != 0o644:
                        fail(errors, f"{label}: non-deterministic history bundle metadata: {m.name}")
                    fh = tf.extractfile(m)
                    if fh is None:
                        fail(errors, f"{label}: unreadable history bundle member: {m.name}")
                    else:
                        member_data[m.name] = fh.read()
        except (OSError, tarfile.TarError) as exc:
            fail(errors, f"{label}: could not parse history bundle: {exc}")

    for rel, row in by_path.items():
        data = member_data.get(rel)
        if data is None:
            continue
        if len(data) != row.get("bytes") or sha256(data) != row.get("sha256"):
            fail(errors, f"{label}: recovered member does not match original size/SHA: {rel}")

    metrics = report.get("metrics") if isinstance(report.get("metrics"), dict) else {}
    bundle_size = len(bundle_bytes)
    expected_metrics = {
        "original_target_total_bytes": original_total,
        "stub_total_bytes": stub_total,
        "gross_target_bytes_recovered": original_total - stub_total,
        "bundle_size_bytes": bundle_size,
        "net_bytes_recovered_before_this_report_and_retrieval_tool": original_total - stub_total - bundle_size,
    }
    for key, value in expected_metrics.items():
        if metrics.get(key) != value:
            fail(errors, f"{label}: compaction metric mismatch for {key}: {metrics.get(key)!r} != {value!r}")
    if len(member_data) != report.get("scope", {}).get("exact_payload_member_count"):
        fail(errors, f"{label}: exact payload member count mismatch")
    verification = report.get("verification") if isinstance(report.get("verification"), dict) else {}
    if verification.get("original_bytes_deleted_without_retrievable_copy") is not False:
        fail(errors, f"{label}: report does not assert retrievable-copy preservation")
    if not (ROOT / "tools/retrieve_compacted_history.py").is_file():
        fail(errors, f"{label}: retrieval tool missing")
    return {"targets": len(targets), "members": len(member_data), "bundle_bytes": bundle_size, "net": expected_metrics["net_bytes_recovered_before_this_report_and_retrieval_tool"]}


def main() -> int:
    errors: list[str] = []
    current_rev = version_number(VERSION)
    if current_rev is None:
        print(f"ERROR: invalid VERSION {VERSION!r}", file=sys.stderr)
        return 2
    reports = sorted((ROOT / "artifacts" / "reports").glob(REPORT_GLOB))
    if not reports:
        print("ERROR: no retrievable-history compaction reports found", file=sys.stderr)
        return 2
    totals = {"targets": 0, "members": 0, "bundle_bytes": 0, "net": 0}
    for report_path in reports:
        metrics = validate_report(report_path, current_rev, errors)
        for key in totals:
            totals[key] += metrics[key]
    if errors:
        for message in errors[:120]:
            print("ERROR:", message, file=sys.stderr)
        return 2
    print(
        "PASS: retrievable history compaction "
        f"(reports={len(reports)}, targets={totals['targets']}, members={totals['members']}, bundle_bytes={totals['bundle_bytes']}, net_recovered={totals['net']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
