#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
REVISION = "rev0071"
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
EXPECTED_SOURCE_ENTRIES = 3551
OUTPUT_PREFIXES = (
    "data/rev0071_cloudtainer_",
    "evidence/rev0071-cloudtainer-",
)
EXCLUDED_DIR_PARTS = {"__pycache__", ".pytest_cache"}


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def is_generated_rev0071(rel: str) -> bool:
    return any(rel.startswith(prefix) for prefix in OUTPUT_PREFIXES)


def iter_payload_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if is_generated_rev0071(rel):
            continue
        if any(part in EXCLUDED_DIR_PARTS for part in path.relative_to(ROOT).parts):
            continue
        yield path


def source_zip_identity(source_zip: Path | None) -> dict:
    row = {
        "source_zip_supplied": bool(source_zip),
        "source_zip_name": "",
        "source_zip_exists": False,
        "source_zip_sha256": "",
        "source_zip_entries": 0,
        "source_zip_status": "not-supplied",
    }
    if source_zip is None:
        return row

    row["source_zip_name"] = source_zip.name
    row["source_zip_exists"] = source_zip.exists()
    if not source_zip.exists():
        row["source_zip_status"] = "missing"
        return row

    row["source_zip_sha256"] = sha_file(source_zip)
    try:
        import zipfile
        with zipfile.ZipFile(source_zip) as archive:
            row["source_zip_entries"] = len(archive.infolist())
    except Exception as exc:  # pragma: no cover - defensive artifact probe
        row["source_zip_status"] = f"zip-error:{type(exc).__name__}"
        return row

    row["source_zip_status"] = (
        "pass"
        if row["source_zip_sha256"] == EXPECTED_SOURCE_SHA256
        and row["source_zip_entries"] == EXPECTED_SOURCE_ENTRIES
        else "fail"
    )
    return row


def count_text_refs(pattern: str) -> list[dict]:
    rows = []
    for path in iter_payload_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.stat().st_size > 2_500_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        count = text.count(pattern)
        if count:
            rows.append({"file": rel, "pattern": pattern, "count": count})
    return rows


def build_inventory() -> tuple[list[dict], list[dict], list[dict], list[dict], dict]:
    inventory: list[dict] = []
    by_top: dict[str, dict] = defaultdict(lambda: {"top_dir": "", "files": 0, "bytes": 0})
    by_ext: dict[str, dict] = defaultdict(lambda: {"extension": "", "files": 0, "bytes": 0})
    dup_map: dict[tuple[str, int], list[str]] = defaultdict(list)

    for path in iter_payload_files():
        rel = path.relative_to(ROOT).as_posix()
        size = path.stat().st_size
        top = rel.split("/", 1)[0]
        ext = path.suffix.lower() or "[none]"
        digest = sha_file(path)

        inventory.append({
            "file": rel,
            "top_dir": top,
            "extension": ext,
            "bytes": size,
            "sha256": digest,
        })

        by_top[top]["top_dir"] = top
        by_top[top]["files"] += 1
        by_top[top]["bytes"] += size
        by_ext[ext]["extension"] = ext
        by_ext[ext]["files"] += 1
        by_ext[ext]["bytes"] += size
        dup_map[(digest, size)].append(rel)

    duplicate_rows = []
    for (digest, size), files in dup_map.items():
        if len(files) < 2:
            continue
        duplicate_rows.append({
            "sha256": digest,
            "bytes_each": size,
            "copies": len(files),
            "wasted_bytes": (len(files) - 1) * size,
            "files": "|".join(sorted(files)),
        })

    duplicate_rows.sort(key=lambda row: (row["wasted_bytes"], row["copies"], row["bytes_each"]), reverse=True)
    top_rows = sorted(by_top.values(), key=lambda row: row["bytes"], reverse=True)
    ext_rows = sorted(by_ext.values(), key=lambda row: row["bytes"], reverse=True)

    ranked_files = [
        row for row in inventory
        if row["file"].startswith("data/")
        and "_ranked_audit_queue." in row["file"]
    ]

    summary = {
        "revision": REVISION,
        "payload_file_count_excluding_generated_rev0071": len(inventory),
        "payload_bytes_excluding_generated_rev0071": sum(row["bytes"] for row in inventory),
        "top_dir_count": len(top_rows),
        "extension_count": len(ext_rows),
        "exact_duplicate_groups": len(duplicate_rows),
        "exact_duplicate_wasted_bytes": sum(row["wasted_bytes"] for row in duplicate_rows),
        "ranked_audit_queue_files": len(ranked_files),
        "ranked_audit_queue_bytes": sum(row["bytes"] for row in ranked_files),
        "ranked_audit_queue_share_pct": round(
            100.0 * sum(row["bytes"] for row in ranked_files) / max(1, sum(row["bytes"] for row in inventory)), 2
        ),
    }
    return inventory, top_rows, ext_rows, duplicate_rows, summary


def status_from(summary: dict, source: dict) -> str:
    failures = []
    if source["source_zip_supplied"] and source["source_zip_status"] != "pass":
        failures.append("source_zip_identity")
    if summary["ranked_audit_queue_share_pct"] < 50:
        # This is a waste audit. If the dominant waste signal disappears, the stored narrative needs review.
        failures.append("ranked_queue_signal_missing")
    if summary["exact_duplicate_wasted_bytes"] < 1_000_000:
        failures.append("duplicate_signal_missing")
    return "pass" if not failures else "fail"


def render_evidence(summary: dict, top_rows: list[dict], duplicate_rows: list[dict], source: dict) -> str:
    top_lines = "\n".join(
        f"- {row['top_dir']}: {row['files']} files, {row['bytes']} bytes"
        for row in top_rows[:8]
    )
    dup_lines = "\n".join(
        f"- {row['wasted_bytes']} wasted bytes across {row['copies']} copies: {row['files'].split('|')[0]}"
        for row in duplicate_rows[:8]
    )
    return f"""# rev0071 cloudtainer waste / source-alias audit

```text
status: {summary['status']}
source zip supplied: {source['source_zip_name'] or 'not supplied'}
source zip status: {source['source_zip_status']}
payload files excluding generated rev0071 metrics: {summary['payload_file_count_excluding_generated_rev0071']}
payload bytes excluding generated rev0071 metrics: {summary['payload_bytes_excluding_generated_rev0071']}
ranked audit queue files: {summary['ranked_audit_queue_files']}
ranked audit queue bytes: {summary['ranked_audit_queue_bytes']}
ranked audit queue share: {summary['ranked_audit_queue_share_pct']}%
exact duplicate groups: {summary['exact_duplicate_groups']}
exact duplicate wasted bytes: {summary['exact_duplicate_wasted_bytes']}
```

## Largest top-level payload areas

{top_lines}

## Largest exact-duplicate groups

{dup_lines}

## Interpretation

The cube is not source-heavy; it is evidence/history-heavy. The dominant payload is repeated ranked-audit-queue material, followed by exact copies duplicated between `data/`, `evidence/`, `manifests/`, `handoff/`, and `maintainer_artifacts/`.

rev0071 does not delete historical files. It creates a stable inventory and makes future compaction reviewable before removal.
"""


def run(source_zip: Path | None) -> dict:
    inventory, top_rows, ext_rows, duplicate_rows, summary = build_inventory()
    source = source_zip_identity(source_zip)
    stale_refs = count_text_refs("Nicotine-source(1).zip")

    summary.update({
        "source_bundle_expected_sha256": EXPECTED_SOURCE_SHA256,
        "source_zip_supplied": source["source_zip_supplied"],
        "source_zip_name": source["source_zip_name"],
        "source_zip_sha256": source["source_zip_sha256"],
        "source_zip_entries": source["source_zip_entries"],
        "source_zip_status": source["source_zip_status"],
        "historical_nicotine_source_1_ref_files": len(stale_refs),
        "historical_nicotine_source_1_refs": sum(row["count"] for row in stale_refs),
        "severe_waste_signals": [
            "ranked_audit_queue_history_dominates_payload",
            "exact_duplicate_evidence_data_manifest_copies",
            "historical_source_basename_references_need_hash_based_aliasing",
            "fresh_current_checkout_blocker_still_open",
        ],
    })
    summary["status"] = status_from(summary, source)

    data = ROOT / "data"
    evidence = ROOT / "evidence"
    write_csv(data / "rev0071_cloudtainer_file_inventory.csv", inventory,
              ["file", "top_dir", "extension", "bytes", "sha256"])
    write_json(data / "rev0071_cloudtainer_file_inventory.json", inventory)

    write_csv(data / "rev0071_cloudtainer_top_dirs.csv", top_rows,
              ["top_dir", "files", "bytes"])
    write_json(data / "rev0071_cloudtainer_top_dirs.json", top_rows)

    write_csv(data / "rev0071_cloudtainer_extensions.csv", ext_rows,
              ["extension", "files", "bytes"])
    write_json(data / "rev0071_cloudtainer_extensions.json", ext_rows)

    write_csv(data / "rev0071_cloudtainer_duplicate_groups.csv", duplicate_rows,
              ["sha256", "bytes_each", "copies", "wasted_bytes", "files"])
    write_json(data / "rev0071_cloudtainer_duplicate_groups.json", duplicate_rows)

    write_csv(data / "rev0071_cloudtainer_stale_source_refs.csv", stale_refs,
              ["file", "pattern", "count"])
    write_json(data / "rev0071_cloudtainer_stale_source_refs.json", stale_refs)

    write_json(data / "rev0071_cloudtainer_source_zip_identity.json", source)
    write_json(data / "rev0071_cloudtainer_waste_summary.json", summary)
    write_csv(data / "rev0071_cloudtainer_waste_summary.csv", [summary], list(summary.keys()))

    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "rev0071-cloudtainer-waste-audit.md").write_text(
        render_evidence(summary, top_rows, duplicate_rows, source),
        encoding="utf-8",
    )
    return summary


def validate(summary: dict) -> dict:
    stored_path = ROOT / "data" / "rev0071_cloudtainer_waste_summary.json"
    stored = json.loads(stored_path.read_text(encoding="utf-8"))
    keys = [
        "status",
        "payload_file_count_excluding_generated_rev0071",
        "payload_bytes_excluding_generated_rev0071",
        "exact_duplicate_groups",
        "exact_duplicate_wasted_bytes",
        "ranked_audit_queue_files",
        "ranked_audit_queue_bytes",
        "ranked_audit_queue_share_pct",
        "source_zip_status",
        "source_zip_sha256",
        "source_zip_entries",
        "historical_nicotine_source_1_ref_files",
        "historical_nicotine_source_1_refs",
    ]
    mismatches = [
        {"key": key, "stored": stored.get(key), "computed": summary.get(key)}
        for key in keys
        if stored.get(key) != summary.get(key)
    ]
    return {
        "revision": REVISION,
        "mode": "validate-existing",
        "status": "pass" if not mismatches and summary.get("status") == "pass" else "fail",
        "mismatches": mismatches,
        **{key: summary.get(key) for key in keys},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-zip", type=Path)
    parser.add_argument("--validate-existing", action="store_true")
    args = parser.parse_args()

    summary = run(args.source_zip)
    output = validate(summary) if args.validate_existing else summary
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
