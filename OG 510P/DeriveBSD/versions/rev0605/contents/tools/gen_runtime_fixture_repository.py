#!/usr/bin/env python3
"""Generate the offline runtime fixture repository snapshot and catalog projection.

This is intentionally small and local.  The real product needs signed FreeBSD
repository metadata and package/base bytes; this generator only keeps the
checked-in fixture repository from becoming a hand-maintained catalog lie.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from cube_digest_lib import canonical_digest, load_json_strict_text, pretty_json_text  # noqa: E402
from derive_runtime import (  # noqa: E402
    CURRENT_CUBE_CUT_VERSION,
    PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
    PACKAGE_PAYLOAD_METADATA_POLICY,
    sha256_bytes,
)

MATERIAL_ROOT = ROOT / "validation" / "runtime-materials" / "current" / "packages"
SNAPSHOT_PATH = ROOT / "validation" / "runtime-package-repository" / "current" / "snapshot.json"
CATALOG_PATH = ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json"
MEDIA_TYPE = "application/vnd.derivebsd.runtime-fixture-pkg"
SOURCE_AUTHORITY = "checked-in-runtime-fixture"
TRUTH_CLAIM = (
    "checked-in fixture payload bytes only; metadata is verified against the admitted repository snapshot "
    "and catalog projection and is not an authoritative FreeBSD pkg archive"
)


def load_payload(path: Path) -> dict[str, Any]:
    value = load_json_strict_text(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: fixture payload must be a JSON object")
    if value.get("kind") != "derive.runtime.package.fixture.bytes":
        raise ValueError(f"{path}: unexpected fixture payload kind {value.get('kind')!r}")
    return value


def package_rows() -> dict[str, dict[str, dict[str, Any]]]:
    platforms: dict[str, dict[str, dict[str, Any]]] = {}
    for path in sorted(MATERIAL_ROOT.glob("*.pkg")):
        if path.name.startswith("."):
            continue
        payload = load_payload(path)
        platform = payload.get("platform")
        pkg_id = payload.get("package_id")
        if not isinstance(platform, str) or not isinstance(pkg_id, str):
            raise ValueError(f"{path}: payload must contain platform and package_id")
        data = path.read_bytes()
        rel = path.relative_to(ROOT).as_posix()
        material = {
            "media_type": MEDIA_TYPE,
            "path": rel,
            "sha256": sha256_bytes(data),
            "size_bytes": len(data),
            "source_authority": SOURCE_AUTHORITY,
            "truth_claim": TRUTH_CLAIM,
        }
        row = {
            "authority": SOURCE_AUTHORITY,
            "fixture_payload_digest": canonical_digest(payload),
            "material": material,
            "origin": payload.get("origin"),
            "package_id": pkg_id,
            "payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
            "platform": platform,
            "runtime_dependencies": payload.get("runtime_dependencies", []),
            "runtime_use": payload.get("runtime_use"),
            "version": payload.get("version"),
        }
        platforms.setdefault(platform, {})[pkg_id] = row
    if not platforms:
        raise ValueError(f"no fixture packages found under {MATERIAL_ROOT}")
    return platforms


def build_snapshot() -> dict[str, Any]:
    packages_by_platform = package_rows()
    platforms: dict[str, Any] = {}
    package_count = 0
    for platform, packages in sorted(packages_by_platform.items()):
        package_count += len(packages)
        platforms[platform] = {
            "packages": {pkg_id: packages[pkg_id] for pkg_id in sorted(packages)},
            "platform_digest_material": (
                f"{platform} bootstrap runtime fixture repository snapshot with material byte bindings, "
                "fixture-payload metadata, and transitive dependency closure inputs"
            ),
        }
    snapshot = {
        "kind": "derive.runtime.package_repository.snapshot.fixture",
        "schema_version": "0.1",
        "snapshot_id": "runtime-fixture-repository-snapshot-20260618-r630",
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
        "network_used": False,
        "authoritative_package_index": False,
        "resolver_identity": "offline-fixture-repository-v5-snapshot-admission-no-network",
        "source_root": "validation/runtime-materials/current/packages",
        "platform_count": len(platforms),
        "package_count": package_count,
        "platforms": platforms,
        "truth_claim": (
            "finite checked-in fixture repository snapshot admitted before catalog resolution; not a signed FreeBSD "
            "repository, pkgbase mirror, ports tree, SAT solver, or real package archive set"
        ),
    }
    snapshot["snapshot_digest"] = canonical_digest(snapshot)
    return snapshot


def build_catalog(snapshot: dict[str, Any], snapshot_bytes: bytes) -> dict[str, Any]:
    catalog_platforms: dict[str, Any] = {}
    for platform, platform_row in sorted(snapshot["platforms"].items()):
        catalog_packages: dict[str, Any] = {}
        for pkg_id, row in sorted(platform_row["packages"].items()):
            catalog_packages[pkg_id] = {
                "authority": row["authority"],
                "dependencies": list(row.get("runtime_dependencies", [])),
                "material": dict(row["material"]),
                "origin": row["origin"],
                "resolved_ref": f"pkgbase-fixture://{platform}/{row['origin']}@{str(row['version']).removesuffix('-fixture')}",
                "runtime_use": row["runtime_use"],
                "version": row["version"],
            }
        catalog_platforms[platform] = {
            "packages": catalog_packages,
            "platform_digest_material": (
                f"{platform} bootstrap runtime fixture catalog projected from admitted repository snapshot "
                "with material byte bindings, fixture-payload metadata checks, and transitive dependency closure"
            ),
        }
    catalog = {
        "kind": "derive.runtime.package_catalog.fixture",
        "schema_version": "0.1",
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "network_used": False,
        "repository_snapshot": {
            "path": SNAPSHOT_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256_bytes(snapshot_bytes),
            "snapshot_digest": snapshot["snapshot_digest"],
            "policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
        },
        "platforms": catalog_platforms,
        "projection_policy": (
            "admitted checked-in fixture repository snapshot is source-of-truth before catalog selection; "
            "package payload metadata must still match catalog package_id/platform/origin/version/runtime_dependencies"
        ),
        "resolver_identity": "offline-fixture-catalog-v5-repository-snapshot-payload-closure-no-network",
        "truth_claim": (
            "finite checked-in bootstrap catalog projected from an admitted checked-in fixture repository snapshot plus "
            "payload metadata and digest/size bindings only; not an authoritative FreeBSD package repository, "
            "pkgbase mirror, ports tree, source resolver, SAT solver, or real pkg archive set"
        ),
    }
    catalog["catalog_digest"] = canonical_digest(catalog)
    return catalog


def write(path: Path, obj: dict[str, Any]) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = pretty_json_text(obj)
    path.write_text(text, encoding="utf-8")
    return text.encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write snapshot and catalog projection")
    args = parser.parse_args()

    snapshot = build_snapshot()
    snapshot_text = pretty_json_text(snapshot)
    snapshot_bytes = snapshot_text.encode("utf-8")
    catalog = build_catalog(snapshot, snapshot_bytes)

    if args.write:
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(snapshot_text, encoding="utf-8")
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_PATH.write_text(pretty_json_text(catalog), encoding="utf-8")
        print(f"wrote {SNAPSHOT_PATH.relative_to(ROOT)}")
        print(f"wrote {CATALOG_PATH.relative_to(ROOT)}")
    else:
        print(pretty_json_text({"snapshot": snapshot, "catalog": catalog}), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
