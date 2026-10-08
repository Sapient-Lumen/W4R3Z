#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import PurePosixPath
from zipfile import ZipFile, ZipInfo


def strip_root(name: str) -> str:
    parts = PurePosixPath(name).parts
    return PurePosixPath(*parts[1:]).as_posix() if len(parts) > 1 else ""


def category(path: str) -> str:
    p = PurePosixPath(path)
    name = p.name
    parts = set(p.parts)
    if "__pycache__" in parts or ".pytest_cache" in parts or (p.parts and p.parts[0] == "build"):
        return "generated_cache_or_build"
    if path.startswith("data/") and name.endswith(".csv") and (
        name.endswith("_cpp_transitions.csv")
        or name == "rev0026_cpp_shadow_rollout_transitions.csv"
        or name.endswith("_cpp_segment_rows.csv")
        or name == "rev0032_segment_shadow_segments.csv"
    ):
        return "bulk_transition_or_segment_evidence"
    if path.startswith("data/") and name.endswith(".jsonl"):
        return "replay_trace_jsonl"
    if path.startswith("data/"):
        return "other_data"
    if path.startswith("src/"):
        return "source"
    if path.startswith("tests/"):
        return "tests"
    if path.startswith("scripts/"):
        return "scripts"
    if path.startswith("docs/"):
        return "docs"
    if path.startswith("cpp/"):
        return "cpp_source"
    return "top_level_or_other"


def read_member_text(zf: ZipFile, members: dict[str, ZipInfo], relative: str) -> str:
    info = members[relative]
    return zf.read(info).decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the uploaded rev0067 cloudtainer archive.")
    parser.add_argument("archive")
    parser.add_argument("--inventory", default="data/rev0068_uploaded_rev0067_inventory.csv")
    parser.add_argument("--summary", default="data/rev0068_cloudtainer_audit_summary.json")
    args = parser.parse_args()

    with ZipFile(args.archive) as zf:
        infos = [info for info in zf.infolist() if not info.is_dir()]
        members = {strip_root(info.filename): info for info in infos}
        rows = []
        categories = Counter()
        category_bytes = Counter()
        extensions = Counter()
        top_dirs = Counter()
        top_dir_bytes = Counter()
        for info in infos:
            relative = strip_root(info.filename)
            cat = category(relative)
            ext = PurePosixPath(relative).suffix.lower() or "[none]"
            top = PurePosixPath(relative).parts[0] if PurePosixPath(relative).parts else "[root]"
            categories[cat] += 1
            category_bytes[cat] += info.file_size
            extensions[ext] += 1
            top_dirs[top] += 1
            top_dir_bytes[top] += info.file_size
            rows.append(
                {
                    "path": relative,
                    "category": cat,
                    "bytes_uncompressed": info.file_size,
                    "bytes_compressed": info.compress_size,
                    "compression_ratio": round(info.compress_size / info.file_size, 6) if info.file_size else 0.0,
                    "crc32": f"{info.CRC:08x}",
                }
            )

        size_groups: dict[int, list[ZipInfo]] = defaultdict(list)
        for info in infos:
            if info.file_size:
                size_groups[info.file_size].append(info)
        hash_groups: dict[tuple[int, str], list[str]] = defaultdict(list)
        for size, group in size_groups.items():
            if len(group) < 2:
                continue
            for info in group:
                digest = hashlib.sha256(zf.read(info)).hexdigest()
                hash_groups[(size, digest)].append(strip_root(info.filename))
        duplicate_groups = [
            {"bytes_each": size, "sha256": digest, "paths": sorted(paths)}
            for (size, digest), paths in hash_groups.items()
            if len(paths) > 1
        ]
        duplicate_groups.sort(key=lambda item: (-(len(item["paths"]) - 1) * item["bytes_each"], item["paths"]))
        redundant_duplicate_bytes = sum((len(item["paths"]) - 1) * item["bytes_each"] for item in duplicate_groups)

        manifest = json.loads(read_member_text(zf, members, "manifest.json"))
        revision_log = json.loads(read_member_text(zf, members, "data/revision_log.json"))
        revisions = revision_log.get("revisions", [])
        readme_first = next(
            (line.strip() for line in read_member_text(zf, members, "README.md").splitlines() if line.strip()),
            "",
        )

    with open(args.inventory, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: row["path"]))

    total_bytes = sum(info.file_size for info in infos)
    compressed_bytes = sum(info.compress_size for info in infos)
    summary = {
        "audit_revision": "rev0068",
        "source_archive": PurePosixPath(args.archive).name,
        "source_declared_root": PurePosixPath(infos[0].filename).parts[0] if infos else None,
        "total_files": len(infos),
        "total_uncompressed_bytes": total_bytes,
        "total_uncompressed_mib": round(total_bytes / (1024**2), 3),
        "total_member_compressed_bytes": compressed_bytes,
        "total_member_compressed_mib": round(compressed_bytes / (1024**2), 3),
        "categories": {
            key: {"files": categories[key], "bytes": category_bytes[key], "mib": round(category_bytes[key] / (1024**2), 3)}
            for key in sorted(categories)
        },
        "top_directories": {
            key: {"files": top_dirs[key], "bytes": top_dir_bytes[key], "mib": round(top_dir_bytes[key] / (1024**2), 3)}
            for key in sorted(top_dirs)
        },
        "extensions": dict(sorted(extensions.items(), key=lambda item: (-item[1], item[0]))),
        "duplicates": {
            "exact_duplicate_groups": len(duplicate_groups),
            "redundant_bytes": redundant_duplicate_bytes,
            "redundant_mib": round(redundant_duplicate_bytes / (1024**2), 3),
            "largest_groups": duplicate_groups[:20],
        },
        "semantic_identity_findings": {
            "archive_root": PurePosixPath(infos[0].filename).parts[0] if infos else None,
            "readme_heading": readme_first,
            "manifest_revision": manifest.get("revision"),
            "manifest_cube_name": manifest.get("cube_name"),
            "manifest_filename": manifest.get("filename"),
            "revision_log_latest_revision": revisions[-1].get("revision") if revisions else None,
            "revision_log_latest_codename": revisions[-1].get("codename") if revisions else None,
            "revision_log_entries": len(revisions),
        },
        "policy_followthrough": {
            "rev0057_total_uncompressed_mib_documented": 916.742,
            "rev0057_raw_transition_bytes_documented": 718221428,
            "rev0057_cache_build_bytes_documented": 2168796,
            "rev0067_bulk_transition_or_segment_bytes": category_bytes["bulk_transition_or_segment_evidence"],
            "rev0067_cache_build_bytes": category_bytes["generated_cache_or_build"],
            "finding": "The rev0057 tiering policy was documented but not enforced in the linked archive by rev0067.",
        },
        "category_definition_note": (
            "bulk_transition_or_segment_evidence is a conservative filename-based class: full *_cpp_transitions.csv, "
            "the rev0026 shadow-rollout transition file, *_cpp_segment_rows.csv, and rev0032 segment-shadow segments. "
            "Trace-row and compact transition-sample CSVs remain in other_data."
        ),
    }
    with open(args.summary, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
