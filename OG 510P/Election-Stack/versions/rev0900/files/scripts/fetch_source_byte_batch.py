#!/usr/bin/env python3
"""Fetch and receipt a strict source-byte sha256sum batch.

This is the network-capable complement to source_byte_receipts_from_cache_batch.py.
It reads an existing batch handoff file, fetches only those lockfile-pinned
sources, verifies each byte stream against the pinned SHA-256, writes matching
bytes into an operator cache, and optionally emits source-byte receipts.

Release archives must not bundle third-party source bytes.  This helper refuses
release-governed cache paths inside the repository except evidence/cache/, which
is excluded from MANIFEST.sha256 and release ZIP construction.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import tomllib
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import archive_version as _archive_version, release_date as _release_date  # noqa: E402

LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
DEFAULT_RECEIPT_DIR = ROOT / "artifacts" / "source_byte_receipts"
DEFAULT_REPORT = ROOT / "artifacts" / "reports" / f"source-byte-batch-fetch-plan-rev{_archive_version(ROOT).removeprefix('v').zfill(4)}.json"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SHA256SUM_LINE_RE = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9._-]+)$")
FORBIDDEN_PATH_HINT_RE = re.compile(r"(?i)(voter|eligibility|token|session|credential|secret|password|auth|jwt)")
NON_CLAIMS = (
    "not current voter instruction; not legal advice; not source-byte cache "
    "completeness; not public-release authorization; not live-pilot approval"
)
BOUNDARY = (
    "Network-capable source-byte batch fetch verifies externally fetched bytes "
    "against evidence/lock/external-sources.toml before writing cache files or "
    "receipts. It never vendors third-party bytes into the release archive and "
    "does not prove source currentness, legal authority, public-release readiness, "
    "or live-pilot approval."
)


def safe_basename(raw: Any) -> bool:
    s = str(raw or "")
    if not s or s.startswith(".") or "/" in s or "\\" in s or ".." in s:
        return False
    return bool(SAFE_BASENAME_RE.fullmatch(s))


def stable_path_ref(path: Path, root: Path = ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return str(path)


def sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            total += len(chunk)
            h.update(chunk)
    return h.hexdigest(), total


def load_sources(lockfile: Path) -> list[dict[str, Any]]:
    with lockfile.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return [r for r in rows if isinstance(r, dict) and str(r.get("id") or "").strip()]


def pinned_sources(lockfile: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in load_sources(lockfile):
        sha = str(row.get("sha256") or "").strip().lower()
        if sha:
            out.append(row)
    return out


def parse_batch_file(batch_file: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    seen_lines: set[tuple[str, str]] = set()
    seen_filenames: set[str] = set()
    for lineno, raw in enumerate(batch_file.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        m = SHA256SUM_LINE_RE.fullmatch(raw)
        if not m:
            raise ValueError(f"invalid sha256sum line {batch_file}:{lineno}")
        expected_sha, local_filename = m.group(1), m.group(2)
        if not safe_basename(local_filename):
            raise ValueError(f"unsafe local filename {batch_file}:{lineno}")
        key = (expected_sha, local_filename)
        if key in seen_lines:
            raise ValueError(f"duplicate sha256sum line {batch_file}:{lineno}")
        if local_filename in seen_filenames:
            raise ValueError(f"duplicate local filename {batch_file}:{lineno}")
        seen_lines.add(key)
        seen_filenames.add(local_filename)
        entries.append({"expected_sha256": expected_sha, "local_filename": local_filename, "line_number": str(lineno)})
    if not entries:
        raise ValueError(f"empty batch file: {batch_file}")
    return entries


def select_sources_for_batch(sources: list[dict[str, Any]], batch_file: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries = parse_batch_file(batch_file)
    index: dict[tuple[str, str], dict[str, Any]] = {}
    duplicates: list[str] = []
    for row in sources:
        local_filename = str(row.get("local_filename") or "").strip()
        expected_sha = str(row.get("sha256") or "").strip().lower()
        if not local_filename or not expected_sha:
            continue
        key = (expected_sha, local_filename)
        if key in index:
            duplicates.append(local_filename)
        index[key] = row
    if duplicates:
        raise ValueError("batch selection cannot disambiguate duplicate lockfile local filenames: " + ",".join(sorted(duplicates)[:10]))

    selected: list[dict[str, Any]] = []
    unmatched: list[str] = []
    for entry in entries:
        row = index.get((entry["expected_sha256"], entry["local_filename"]))
        if row is None:
            unmatched.append(f"{entry['line_number']}:{entry['local_filename']}")
        else:
            selected.append(row)
    if unmatched:
        raise ValueError("batch file contains entries not pinned in lockfile: " + ",".join(unmatched[:10]))

    return selected, {
        "batch_file": stable_path_ref(batch_file),
        "batch_file_entry_count": len(entries),
        "batch_file_source_count": len(selected),
        "batch_file_sha256sum_sha256": "sha256:" + hashlib.sha256(batch_file.read_bytes()).hexdigest(),
    }


def existing_receipt_source_ids(receipt_dir: Path) -> set[str]:
    out: set[str] = set()
    if not receipt_dir.exists():
        return out
    for path in sorted(receipt_dir.glob("*.receipt.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and str(obj.get("source_id") or "").strip():
            out.add(str(obj.get("source_id") or "").strip())
    return out


def infer_content_type(local_filename: str, headers: Any | None = None) -> str:
    raw = ""
    if headers is not None:
        try:
            raw = str(headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        except Exception:
            raw = ""
    if raw:
        return raw
    low = local_filename.lower()
    if low.endswith(".pdf"):
        return "application/pdf"
    if low.endswith(".txt"):
        return "text/plain"
    if low.endswith(".md"):
        return "text/markdown"
    if low.endswith(".html") or low.endswith(".htm"):
        return "text/html"
    if low.endswith(".json"):
        return "application/json"
    return "application/octet-stream"


def validate_retrieved_at(raw: str) -> str:
    if not raw:
        return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", raw):
        raise ValueError("--retrieved-at-utc must be UTC ISO seconds ending in Z")
    dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return raw


def receipt_id_for(source_id: str, observation_type: str) -> str:
    token = _archive_version(ROOT).upper().replace("V", "REV", 1)
    if observation_type == "operator_cache_file":
        return f"SBR-{token}-CACHE-{source_id}"
    return f"SBR-{token}-{source_id}"


def build_receipt(
    row: dict[str, Any],
    *,
    observed_sha256: str,
    byte_count: int,
    content_type: str,
    retrieved_at_utc: str,
    observation_type: str,
    fetch_status: int | str,
) -> dict[str, Any]:
    source_id = str(row.get("id") or "").strip()
    local_filename = str(row.get("local_filename") or "").strip()
    expected_sha = str(row.get("sha256") or "").strip().lower()
    receipt: dict[str, Any] = {
        "receipt_id": receipt_id_for(source_id, observation_type),
        "source_id": source_id,
        "source_url": str(row.get("url") or "").strip(),
        "retrieved_at_utc": retrieved_at_utc,
        "observation_type": observation_type,
        "fetch_status": fetch_status,
        "content_type": content_type,
        "byte_count": byte_count,
        "observed_sha256": observed_sha256.lower(),
        "lockfile_sha256": expected_sha,
        "local_cache_filename": local_filename,
        "bundled_bytes": False,
        "non_claims": NON_CLAIMS,
    }
    if observation_type == "operator_cache_file":
        receipt["cache_file_sha256_matched"] = True
    return receipt


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def cache_dir_problem(cache_dir: Path) -> str:
    try:
        rel = cache_dir.resolve().relative_to(ROOT.resolve())
    except Exception:
        return ""
    rel_s = rel.as_posix().rstrip("/") + "/"
    if rel_s.startswith("evidence/cache/"):
        return ""
    return (
        "cache-dir is inside the release tree but not under evidence/cache/; "
        "refusing to risk bundling third-party source bytes: " + rel.as_posix()
    )


def fetch_to_cache_temp(
    url: str,
    *,
    local_filename: str,
    cache_dir: Path,
    timeout: int,
    max_bytes: int,
) -> tuple[str, int, str, Path]:
    target = cache_dir / local_filename
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=local_filename + ".", suffix=".part", dir=str(target.parent))
    h = hashlib.sha256()
    total = 0
    content_type = infer_content_type(local_filename)
    req = urllib.request.Request(url, headers={"User-Agent": "The-Election-Stack/source-byte-batch-fetch"})
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as out:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content_type = infer_content_type(local_filename, resp.headers)
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise RuntimeError(f"exceeded --max-bytes ({max_bytes}); aborting at {total}")
                    h.update(chunk)
                    out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
    except Exception:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
    return h.hexdigest(), total, content_type, tmp


def row_url_host(url: str) -> str:
    m = re.match(r"^[a-z][a-z0-9+.-]*://([^/]+)", url, flags=re.I)
    return m.group(1).lower() if m else ""


def parse_source_id_csv(raw: str) -> set[str]:
    ids: set[str] = set()
    for part in str(raw or "").split(","):
        sid = part.strip()
        if not sid:
            continue
        if not re.fullmatch(r"[a-z0-9_]+", sid):
            raise ValueError(f"invalid source id filter {sid!r}; expected [a-z0-9_]+")
        ids.add(sid)
    return ids


def apply_source_id_filters(
    selected: list[dict[str, Any]], *, only_source_ids: set[str], skip_source_ids: set[str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ids_in_batch = {str(r.get("id") or "").strip() for r in selected}
    missing_only = sorted(only_source_ids - ids_in_batch)
    missing_skip = sorted(skip_source_ids - ids_in_batch)
    if missing_only:
        raise ValueError("--only-source-ids not present in selected batch: " + ",".join(missing_only[:10]))
    if missing_skip:
        raise ValueError("--skip-source-ids not present in selected batch: " + ",".join(missing_skip[:10]))
    if only_source_ids:
        selected = [r for r in selected if str(r.get("id") or "").strip() in only_source_ids]
    if skip_source_ids:
        selected = [r for r in selected if str(r.get("id") or "").strip() not in skip_source_ids]
    return selected, {
        "source_id_filter_only_count": len(only_source_ids),
        "source_id_filter_skip_count": len(skip_source_ids),
        "source_id_filter_applied": bool(only_source_ids or skip_source_ids),
    }


def build_report_base(
    *,
    lockfile: Path,
    receipt_dir: Path,
    cache_dir: Path | None,
    batch_meta: dict[str, Any],
    selected: list[dict[str, Any]],
    print_plan: bool,
    cache_only: bool,
    write_receipts: bool,
) -> dict[str, Any]:
    return {
        "archive_version": _archive_version(ROOT),
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": BOUNDARY,
        "network_io": (not print_plan and not cache_only),
        "third_party_bytes_bundled": False,
        "scope": "strict-source-byte-sha256sum-batch",
        "lockfile": stable_path_ref(lockfile),
        "receipt_dir": stable_path_ref(receipt_dir),
        "cache_dir": stable_path_ref(cache_dir) if cache_dir is not None else "",
        "write_receipts_requested": bool(write_receipts),
        **batch_meta,
        "candidate_source_count": len(selected),
        "rows": [],
    }


def process_batch(args: argparse.Namespace) -> dict[str, Any]:
    lockfile = Path(args.lockfile)
    batch_file = Path(args.batch_file)
    receipt_dir = Path(args.receipt_dir)
    cache_dir = Path(args.cache_dir) if args.cache_dir else None

    selected, batch_meta = select_sources_for_batch(pinned_sources(lockfile), batch_file)
    only_source_ids = parse_source_id_csv(args.only_source_ids)
    skip_source_ids = parse_source_id_csv(args.skip_source_ids)
    if only_source_ids and skip_source_ids and (only_source_ids & skip_source_ids):
        raise ValueError("source ids cannot appear in both --only-source-ids and --skip-source-ids")
    selected, filter_meta = apply_source_id_filters(
        selected, only_source_ids=only_source_ids, skip_source_ids=skip_source_ids
    )
    batch_meta.update(filter_meta)
    if args.limit and args.limit > 0:
        selected = selected[: args.limit]

    if not selected:
        raise ValueError("source-id filters/limit selected zero rows")

    if not args.print_plan:
        if cache_dir is None:
            raise ValueError("--cache-dir is required unless --print-plan is used")
        problem = cache_dir_problem(cache_dir)
        if problem:
            raise ValueError(problem)

    report = build_report_base(
        lockfile=lockfile,
        receipt_dir=receipt_dir,
        cache_dir=cache_dir,
        batch_meta=batch_meta,
        selected=selected,
        print_plan=bool(args.print_plan),
        cache_only=bool(args.cache_only),
        write_receipts=bool(args.write_receipts),
    )

    existing = existing_receipt_source_ids(receipt_dir)
    retrieved_at = validate_retrieved_at(args.retrieved_at_utc)
    rows: list[dict[str, Any]] = []
    for row in selected:
        source_id = str(row.get("id") or "").strip()
        url = str(row.get("url") or "").strip()
        local_filename = str(row.get("local_filename") or "").strip()
        expected_sha = str(row.get("sha256") or "").strip().lower()
        out: dict[str, Any] = {
            "source_id": source_id,
            "url_host": row_url_host(url),
            "local_filename": local_filename,
            "expected_sha256": expected_sha,
            "receipt_preexisting": source_id in existing,
            "status": "pending",
            "byte_count": 0,
            "observed_sha256": "",
            "receipt_written": False,
            "cache_file": stable_path_ref((cache_dir / local_filename) if cache_dir is not None else Path(local_filename)),
            "error": "",
        }
        rows.append(out)

        if args.print_plan:
            out["status"] = "plan_only"
            continue
        if not safe_basename(local_filename):
            out["status"] = "unsafe_local_filename"
            out["error"] = "unsafe local_filename in lockfile"
            if args.stop_on_error:
                break
            continue
        if not HEX64_RE.fullmatch(expected_sha):
            out["status"] = "invalid_expected_sha256"
            out["error"] = "invalid lockfile sha256"
            if args.stop_on_error:
                break
            continue
        if source_id in existing and not args.force:
            out["status"] = "skipped_existing_receipt"
            continue
        assert cache_dir is not None
        target = cache_dir / local_filename

        try:
            if target.exists():
                observed, byte_count = sha256_file(target)
                out["observed_sha256"] = observed
                out["byte_count"] = byte_count
                if observed == expected_sha:
                    out["status"] = "cache_hit_match"
                    if args.write_receipts:
                        receipt = build_receipt(
                            row,
                            observed_sha256=observed,
                            byte_count=byte_count,
                            content_type=infer_content_type(local_filename),
                            retrieved_at_utc=retrieved_at,
                            observation_type="operator_cache_file",
                            fetch_status="not_applicable_cache_file",
                        )
                        write_receipt(receipt_dir / f"{source_id}.receipt.json", receipt)
                        out["receipt_written"] = True
                    continue
                out["status"] = "cache_hit_mismatch"
                out["error"] = "existing cache file sha256 does not match lockfile"
                if args.cache_only or not args.force:
                    if args.stop_on_error:
                        break
                    continue

            if args.cache_only:
                out["status"] = "cache_missing"
                continue

            observed, byte_count, content_type, tmp = fetch_to_cache_temp(
                url,
                local_filename=local_filename,
                cache_dir=cache_dir,
                timeout=args.timeout,
                max_bytes=args.max_bytes,
            )
            out["observed_sha256"] = observed
            out["byte_count"] = byte_count
            if observed != expected_sha:
                out["status"] = "fetched_sha256_mismatch"
                out["error"] = "network bytes did not match lockfile sha256; temp file deleted"
                try:
                    tmp.unlink()
                except OSError:
                    pass
                if args.stop_on_error:
                    break
                continue

            os.replace(tmp, target)
            out["status"] = "fetched_match"
            if args.write_receipts:
                receipt = build_receipt(
                    row,
                    observed_sha256=observed,
                    byte_count=byte_count,
                    content_type=content_type,
                    retrieved_at_utc=retrieved_at,
                    observation_type="network_fetch",
                    fetch_status=200,
                )
                write_receipt(receipt_dir / f"{source_id}.receipt.json", receipt)
                out["receipt_written"] = True
        except Exception as exc:
            out["status"] = "error"
            out["error"] = str(exc)
            if args.stop_on_error:
                break

    status_counts = Counter(str(r.get("status") or "") for r in rows)
    report["rows"] = rows
    report["status_counts"] = dict(sorted(status_counts.items()))
    report["error_count"] = sum(1 for r in rows if r.get("status") in {"error", "unsafe_local_filename", "invalid_expected_sha256", "cache_hit_mismatch", "fetched_sha256_mismatch"})
    report["receipt_written_count"] = sum(1 for r in rows if r.get("receipt_written") is True)
    report["matched_byte_count"] = sum(int(r.get("byte_count") or 0) for r in rows if r.get("status") in {"cache_hit_match", "fetched_match"})
    report["completed_source_ids"] = [r["source_id"] for r in rows if r.get("status") in {"cache_hit_match", "fetched_match"}]
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch and/or receipt one source-byte sha256sum batch")
    ap.add_argument("--batch-file", required=True, help="strict sha256sum batch file to process")
    ap.add_argument("--cache-dir", help="external or evidence/cache source-byte cache directory")
    ap.add_argument("--receipt-dir", default=str(DEFAULT_RECEIPT_DIR), help="receipt directory to inspect/write")
    ap.add_argument("--lockfile", default=str(LOCK), help="external-sources.toml path")
    ap.add_argument("--write-receipts", action="store_true", help="write receipt JSON for exact-match bytes")
    ap.add_argument("--force", action="store_true", help="replace existing receipts and mismatched cache files after a successful fetch")
    ap.add_argument("--cache-only", action="store_true", help="inspect cache and write receipts for hits, but perform no network I/O")
    ap.add_argument("--print-plan", action="store_true", help="emit selected batch plan only; no cache inspection, network I/O, or writes")
    ap.add_argument("--stop-on-error", action="store_true", help="stop after the first mismatch/fetch error")
    ap.add_argument("--limit", type=int, default=0, help="optional maximum selected rows to process; 0 means no limit")
    ap.add_argument("--only-source-ids", default="", help="comma-separated source ids from the batch to process; fails closed if any id is not in the selected batch")
    ap.add_argument("--skip-source-ids", default="", help="comma-separated source ids from the batch to skip; fails closed if any id is not in the selected batch")
    ap.add_argument("--retrieved-at-utc", default="", help="UTC timestamp for written receipts; default current UTC")
    ap.add_argument("--timeout", type=int, default=30, help="per-source request timeout seconds")
    ap.add_argument("--max-bytes", type=int, default=200 * 1024 * 1024, help="per-source max download bytes")
    ap.add_argument("--report-path", default=str(DEFAULT_REPORT), help="report path for --write-report")
    ap.add_argument("--write-report", action="store_true", help="write JSON report")
    ap.add_argument("--json", action="store_true", help="print JSON report")
    args = ap.parse_args()

    try:
        report = process_batch(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.write_report:
        out = Path(args.report_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, sort_keys=True, indent=2))
    if report.get("error_count", 0):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
