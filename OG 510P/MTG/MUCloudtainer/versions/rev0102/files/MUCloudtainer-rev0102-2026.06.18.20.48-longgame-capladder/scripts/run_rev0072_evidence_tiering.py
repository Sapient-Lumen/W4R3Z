#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.evidence_tiering import (
    audit_evidence_bundle,
    build_evidence_bundle,
    build_tiering_catalog,
    sha256_file,
    write_tiering_catalog,
)

HOT_PATHS = (
    "data/rev0011_replay_traces.jsonl",
    "data/rev0019_cpp_trace_rows.csv",
    "data/rev0019_public_traces.jsonl",
    "data/rev0020_cpp_trace_rows.csv",
    "data/rev0020_public_traces.jsonl",
    "data/rev0025_outcome_ranker_training_dataset.csv",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Split bulky historical evidence into hot core and immutable cold sidecar tiers.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--bundle-root", default="MUCloudtainer-Evidence-rev0072-2026.06.17.23.36-coldstore-bulkraw")
    parser.add_argument("--timestamp", default="2026.06.17.23.36")
    parser.add_argument("--catalog", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    catalog_path = args.catalog or (root / "data" / "rev0072_evidence_tiering_catalog.json")
    catalog = build_tiering_catalog(
        root,
        hot_paths=HOT_PATHS,
        bundle_filename=args.bundle.name,
        bundle_root=args.bundle_root,
    )
    build_evidence_bundle(
        root,
        catalog,
        args.bundle,
        bundle_root=args.bundle_root,
        timestamp=args.timestamp,
    )
    bundle_audit = audit_evidence_bundle(args.bundle, catalog)
    if not bundle_audit["passed"]:
        print(json.dumps({"bundle_audit": bundle_audit}, indent=2, sort_keys=True))
        raise SystemExit(1)
    catalog["bundle"]["sha256"] = bundle_audit["bundle_sha256"]
    catalog["bundle"]["bytes"] = bundle_audit["bundle_bytes"]
    write_tiering_catalog(catalog_path, catalog)
    audit_path = root / "data" / "rev0072_evidence_bundle_audit.json"
    audit_path.write_text(json.dumps(bundle_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"catalog": str(catalog_path), "summary": catalog["summary"], "bundle_audit": bundle_audit, "bundle_audit_path": str(audit_path)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
