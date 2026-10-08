from __future__ import annotations

import json
import zipfile
from pathlib import Path

from src.muc5.archive_contract import audit_linked_archive, build_linked_archive, sha256_file
from src.muc5.evidence_tiering import (
    audit_evidence_bundle,
    build_evidence_bundle,
    build_tiering_catalog,
    materialize_evidence_bundle,
    prune_cold_evidence,
    validate_core_tiering,
    write_tiering_catalog,
)


def _archive_cube(tmp_path: Path) -> Path:
    root = tmp_path / "MUCloudtainer-rev0072-2026.06.17.23.36-archiveguard-evidencetiering"
    (root / "data").mkdir(parents=True)
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "revision": "rev0072",
                "timestamp": "2026.06.17.23.36",
                "codename": "archiveguard-evidencetiering",
                "cube_name": root.name,
                "filename": f"{root.name}.zip",
            }
        ),
        encoding="utf-8",
    )
    (root / "data" / "large.csv").write_text("a,b\n" + "1,2\n" * 5000, encoding="utf-8")
    return root


def test_linked_archive_builder_deflates_and_is_deterministic(tmp_path: Path) -> None:
    root = _archive_cube(tmp_path)
    first = tmp_path / f"{root.name}.zip"
    second_dir = tmp_path / "second"
    second_dir.mkdir()
    second = second_dir / f"{root.name}.zip"
    build_linked_archive(root, first, compresslevel=9)
    build_linked_archive(root, second, compresslevel=9)
    report = audit_linked_archive(first, expected_root=root.name, max_archive_bytes=1024 * 1024)
    assert report.passed
    assert report.stored_large_files == []
    assert report.compression_ratio is not None and report.compression_ratio < 0.25
    assert sha256_file(first) == sha256_file(second)


def test_archive_contract_rejects_store_only_large_member(tmp_path: Path) -> None:
    root = _archive_cube(tmp_path)
    archive_path = tmp_path / f"{root.name}.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.write(root / "manifest.json", f"{root.name}/manifest.json")
        archive.write(root / "data" / "large.csv", f"{root.name}/data/large.csv")
    report = audit_linked_archive(
        archive_path,
        expected_root=root.name,
        max_archive_bytes=10 * 1024 * 1024,
        stored_file_threshold_bytes=1024,
    )
    assert not report.passed
    assert report.stored_large_files == [f"{root.name}/data/large.csv"]


def test_evidence_sidecar_round_trip_is_hash_verified(tmp_path: Path) -> None:
    root = tmp_path / "MUCloudtainer-rev0072-2026.06.17.23.36-archiveguard-evidencetiering"
    (root / "data").mkdir(parents=True)
    (root / "scripts").mkdir()
    hot = root / "data" / "rev0998_hot_cpp_transitions.csv"
    cold = root / "data" / "rev0999_cold_cpp_transitions.csv"
    hot.write_text("a,b\n" + "1,2\n" * 20, encoding="utf-8")
    cold.write_text("a,b\n" + "3,4\n" * 30, encoding="utf-8")
    (root / "scripts" / "producer.py").write_text(
        "write_csv(DATA / 'rev0999_cold_cpp_transitions.csv', rows)\n",
        encoding="utf-8",
    )
    bundle_root = "MUCloudtainer-Evidence-rev0072-2026.06.17.23.36-coldstore-bulkraw"
    bundle = tmp_path / f"{bundle_root}.zip"
    catalog = build_tiering_catalog(
        root,
        hot_paths=("data/rev0998_hot_cpp_transitions.csv",),
        min_bytes=10,
        bundle_filename=bundle.name,
        bundle_root=bundle_root,
    )
    build_evidence_bundle(
        root,
        catalog,
        bundle,
        bundle_root=bundle_root,
        timestamp="2026.06.17.23.36",
    )
    bundle_audit = audit_evidence_bundle(bundle, catalog)
    assert bundle_audit["passed"]
    catalog["bundle"]["sha256"] = bundle_audit["bundle_sha256"]
    catalog["bundle"]["bytes"] = bundle_audit["bundle_bytes"]
    write_tiering_catalog(root / "data" / "rev0072_evidence_tiering_catalog.json", catalog)

    prune = prune_cold_evidence(root, catalog)
    assert prune["removed_count"] == 1
    assert hot.exists() and not cold.exists()
    assert validate_core_tiering(root, catalog)["passed"]

    restored = materialize_evidence_bundle(
        root,
        bundle,
        selected_paths=("data/rev0999_cold_cpp_transitions.csv",),
    )
    assert restored["restored_count"] == 1
    assert cold.read_text(encoding="utf-8").count("3,4") == 30
