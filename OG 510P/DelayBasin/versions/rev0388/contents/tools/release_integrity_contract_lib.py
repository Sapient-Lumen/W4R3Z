import json
import pathlib
from typing import Any

from release_integrity_lib import build_checksums, canonical_package_command, release_file_records


REQUIRED_INTEGRITY_SURFACES = (
    "RELEASE-MANIFEST.json",
    "FILE-MANIFEST.json",
    "CHECKSUMS.sha256",
    "RELEASE-PROVENANCE.json",
)


class ReleaseIntegrityError(RuntimeError):
    pass


def _load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    path = root / rel
    if not path.exists():
        raise ReleaseIntegrityError(f"missing release integrity surface: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReleaseIntegrityError(f"release integrity surface is not valid JSON: {rel}") from exc
    if not isinstance(data, dict):
        raise ReleaseIntegrityError(f"release integrity surface must be a JSON object: {rel}")
    return data


def _require_equal(label: str, observed: Any, expected: Any) -> None:
    if observed != expected:
        raise ReleaseIntegrityError(f"{label} mismatch: observed={observed!r} expected={expected!r}")


def validate_checksums_text(text: str, file_manifest: dict[str, Any]) -> None:
    expected = build_checksums(file_manifest)
    if text != expected:
        raise ReleaseIntegrityError("CHECKSUMS.sha256 drifted from FILE-MANIFEST.json")
    lines = text.splitlines()
    if len(lines) < 2 or lines[0] != f"# DelayBasin {file_manifest.get('revision')} release file checksums" or lines[1] != "# sha256  path":
        raise ReleaseIntegrityError("CHECKSUMS.sha256 header drifted from release checksum format")
    seen: set[str] = set()
    checksum_paths: list[str] = []
    manifest_paths = [row.get("path") for row in file_manifest.get("files", [])]
    for line in lines[2:]:
        digest, sep, rel = line.partition("  ")
        if sep != "  " or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ReleaseIntegrityError(f"CHECKSUMS.sha256 malformed checksum row: {line}")
        if not rel or rel in seen:
            raise ReleaseIntegrityError(f"CHECKSUMS.sha256 duplicate or empty path row: {rel}")
        seen.add(rel)
        checksum_paths.append(rel)
    if checksum_paths != manifest_paths:
        raise ReleaseIntegrityError("CHECKSUMS.sha256 path order drifted from FILE-MANIFEST.json")


def validate_release_provenance(provenance: dict[str, Any], manifest: dict[str, Any]) -> None:
    stable_expected = {
        "project": "DelayBasin",
        "revision": manifest.get("revision"),
        "bundle": manifest.get("bundle"),
        "surface": "RELEASE-PROVENANCE.json",
        "command": canonical_package_command(manifest),
        "path_order": "sorted archive-relative paths",
        "zip_timestamps": "1980-01-01T00:00:00 for deterministic package entries",
        "file_manifest": "FILE-MANIFEST.json",
        "checksums": "CHECKSUMS.sha256",
    }
    for key, expected in stable_expected.items():
        _require_equal(f"RELEASE-PROVENANCE.json {key}", provenance.get(key), expected)
    generator = provenance.get("generator")
    if generator not in {"tools/package_release.py", "tools/gen_release_integrity.py"}:
        raise ReleaseIntegrityError(f"RELEASE-PROVENANCE.json generator is not an admitted integrity writer: {generator}")
    policy = provenance.get("self_reference_policy", "")
    for token in ["FILE-MANIFEST.json", "CHECKSUMS.sha256", "RELEASE-PROVENANCE.json", "sidecar"]:
        if token not in policy:
            raise ReleaseIntegrityError(f"RELEASE-PROVENANCE.json self_reference_policy missing {token}")


def validate_file_manifest(root: pathlib.Path, manifest: dict[str, Any], file_manifest: dict[str, Any]) -> None:
    for key in ("project", "revision", "bundle", "surface", "scope", "algorithm", "path_count", "files"):
        if key not in file_manifest:
            raise ReleaseIntegrityError(f"FILE-MANIFEST.json missing {key}")
    _require_equal("FILE-MANIFEST.json project", file_manifest.get("project"), "DelayBasin")
    _require_equal("FILE-MANIFEST.json revision", file_manifest.get("revision"), manifest.get("revision"))
    _require_equal("FILE-MANIFEST.json bundle", file_manifest.get("bundle"), manifest.get("bundle"))
    _require_equal("FILE-MANIFEST.json surface", file_manifest.get("surface"), "FILE-MANIFEST.json")
    _require_equal("FILE-MANIFEST.json algorithm", file_manifest.get("algorithm"), "sha256")
    expected = release_file_records(root, manifest.get("bundle"))
    if file_manifest.get("files") != expected:
        raise ReleaseIntegrityError("FILE-MANIFEST.json hashes drifted from current release paths; run tools/gen_release_integrity.py")
    if file_manifest.get("path_count") != len(expected):
        raise ReleaseIntegrityError("FILE-MANIFEST.json path_count mismatch")
    paths = [row.get("path") for row in file_manifest.get("files", [])]
    if paths != sorted(paths):
        raise ReleaseIntegrityError("FILE-MANIFEST.json files are not sorted by archive-relative path")
    if len(paths) != len(set(paths)):
        raise ReleaseIntegrityError("FILE-MANIFEST.json contains duplicate path rows")
    forbidden_self_rows = {"FILE-MANIFEST.json", "CHECKSUMS.sha256", "RELEASE-PROVENANCE.json"}.intersection(paths)
    if forbidden_self_rows:
        raise ReleaseIntegrityError(f"FILE-MANIFEST.json contains self-reference rows: {sorted(forbidden_self_rows)}")


def validate_release_integrity(root: pathlib.Path) -> dict[str, Any]:
    root = pathlib.Path(root)
    for rel in REQUIRED_INTEGRITY_SURFACES:
        if not (root / rel).exists():
            raise ReleaseIntegrityError(f"missing release integrity surface: {rel}")
    manifest = _load_json(root, "RELEASE-MANIFEST.json")
    file_manifest = _load_json(root, "FILE-MANIFEST.json")
    provenance = _load_json(root, "RELEASE-PROVENANCE.json")
    validate_file_manifest(root, manifest, file_manifest)
    validate_checksums_text((root / "CHECKSUMS.sha256").read_text(encoding="utf-8"), file_manifest)
    validate_release_provenance(provenance, manifest)
    return {
        "revision": manifest.get("revision"),
        "bundle": manifest.get("bundle"),
        "path_count": file_manifest.get("path_count"),
        "checksum_rows": len(file_manifest.get("files", [])),
    }
