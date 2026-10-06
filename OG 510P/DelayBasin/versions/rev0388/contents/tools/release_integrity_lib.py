import hashlib
import json
import pathlib
import platform
from typing import Iterable

from release_hygiene_lib import iter_release_paths

INTEGRITY_SURFACES = {"FILE-MANIFEST.json", "CHECKSUMS.sha256", "RELEASE-PROVENANCE.json"}


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def release_file_records(root: pathlib.Path, bundle_name: str | None = None) -> list[dict]:
    records: list[dict] = []
    for path in iter_release_paths(root, bundle_name):
        rel = path.relative_to(root).as_posix()
        if rel in INTEGRITY_SURFACES:
            continue
        records.append({"path": rel, "size": path.stat().st_size, "sha256": sha256_path(path)})
    records.sort(key=lambda row: row["path"])
    return records


def build_file_manifest(root: pathlib.Path, bundle_name: str | None = None) -> dict:
    manifest = json.loads((root / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
    records = release_file_records(root, bundle_name)
    return {
        "project": "DelayBasin",
        "revision": manifest["revision"],
        "bundle": manifest["bundle"],
        "surface": "FILE-MANIFEST.json",
        "scope": "release paths excluding integrity self-reference surfaces and frozen bundles",
        "algorithm": "sha256",
        "path_count": len(records),
        "files": records,
    }


def build_checksums(file_manifest: dict) -> str:
    lines = [f"# DelayBasin {file_manifest['revision']} release file checksums", "# sha256  path"]
    for row in file_manifest["files"]:
        lines.append(f"{row['sha256']}  {row['path']}")
    return "\n".join(lines) + "\n"


def canonical_package_command(manifest: dict) -> str:
    return f"make package-release STAMP={manifest['timestamp']} SLUG={manifest['slug']}"


def build_provenance(root: pathlib.Path, generator: str | None = None, command: str | None = None) -> dict:
    manifest = json.loads((root / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
    generator = generator or "tools/package_release.py"
    command = command or canonical_package_command(manifest)
    return {
        "project": "DelayBasin",
        "revision": manifest["revision"],
        "bundle": manifest["bundle"],
        "surface": "RELEASE-PROVENANCE.json",
        "generator": generator,
        "command": command,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "path_order": "sorted archive-relative paths",
        "zip_timestamps": "1980-01-01T00:00:00 for deterministic package entries",
        "file_manifest": "FILE-MANIFEST.json",
        "checksums": "CHECKSUMS.sha256",
        "self_reference_policy": "FILE-MANIFEST.json excludes FILE-MANIFEST.json, CHECKSUMS.sha256, and RELEASE-PROVENANCE.json to avoid self-hashing loops; the bundle sha256 is emitted as a sidecar after package creation.",
    }


def write_release_integrity(root: pathlib.Path, generator: str | None, command: str | None, bundle_name: str | None = None) -> None:
    file_manifest = build_file_manifest(root, bundle_name)
    (root / "FILE-MANIFEST.json").write_text(json.dumps(file_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "CHECKSUMS.sha256").write_text(build_checksums(file_manifest), encoding="utf-8")
    provenance = build_provenance(root, generator, command)
    (root / "RELEASE-PROVENANCE.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_integrity_canary_tree(root: pathlib.Path) -> None:
    from release_hygiene_lib import build_release_manifest

    (root / "docs").mkdir(parents=True)
    (root / "README.md").write_text("release integrity canary\n", encoding="utf-8")
    (root / "docs" / "note.md").write_text("release integrity canary doc\n", encoding="utf-8")
    manifest = build_release_manifest("rev9999", "2099.01.01.00.00", "integrity-canary")
    (root / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_release_integrity(root, "tools/package_release.py", canonical_package_command(manifest), manifest["bundle"])


def _clone_canary_tree(source: pathlib.Path, destination: pathlib.Path) -> None:
    import shutil

    shutil.copytree(source, destination)


def release_integrity_canary_results() -> list[dict[str, object]]:
    """Run cheap mutation canaries against release integrity validation.

    These canaries avoid full package release. They isolate the file-manifest,
    checksum, and provenance validator so a future refactor cannot leave content
    hash drift, checksum drift, row omissions, or provenance-command drift as
    false greens.
    """
    import tempfile

    from release_integrity_contract_lib import ReleaseIntegrityError, validate_release_integrity

    results: list[dict[str, object]] = []

    def add(row_id: str, expected: object, observed: object, ok: bool) -> None:
        results.append({
            "id": row_id,
            "expected": expected,
            "observed": observed,
            "status": "pass" if ok else "fail",
        })

    with tempfile.TemporaryDirectory(prefix="delaybasin-release-integrity-canaries-") as tmp:
        base = pathlib.Path(tmp)
        pristine = base / "pristine"
        pristine.mkdir()
        _write_integrity_canary_tree(pristine)
        try:
            observed = validate_release_integrity(pristine)
        except ReleaseIntegrityError as exc:
            add("release-integrity-valid-baseline", "valid generated integrity surfaces are accepted", str(exc), False)
        else:
            add(
                "release-integrity-valid-baseline",
                "valid generated integrity surfaces are accepted",
                observed,
                observed.get("path_count", 0) >= 2,
            )

        scenarios = [
            {
                "id": "release-integrity-content-hash-mutation",
                "expected_failure_contains": "FILE-MANIFEST.json hashes drifted",
                "mutate": lambda root: (root / "README.md").write_text("tampered release integrity canary\n", encoding="utf-8"),
            },
            {
                "id": "release-integrity-checksum-drift",
                "expected_failure_contains": "CHECKSUMS.sha256 drifted",
                "mutate": lambda root: (root / "CHECKSUMS.sha256").write_text((root / "CHECKSUMS.sha256").read_text(encoding="utf-8").replace("a", "b", 1), encoding="utf-8"),
            },
            {
                "id": "release-integrity-manifest-row-omission",
                "expected_failure_contains": "FILE-MANIFEST.json hashes drifted",
                "mutate": lambda root: _mutate_file_manifest(root, lambda payload: payload["files"].pop()),
            },
            {
                "id": "release-integrity-path-count-drift",
                "expected_failure_contains": "path_count mismatch",
                "mutate": lambda root: _mutate_file_manifest(root, lambda payload: payload.__setitem__("path_count", payload["path_count"] + 1)),
            },
            {
                "id": "release-integrity-provenance-command-drift",
                "expected_failure_contains": "RELEASE-PROVENANCE.json command mismatch",
                "mutate": lambda root: _mutate_provenance(root, lambda payload: payload.__setitem__("command", "make package-release STAMP=2099.01.01.00.00 SLUG=wrong")),
            },
            {
                "id": "release-integrity-provenance-policy-drift",
                "expected_failure_contains": "self_reference_policy missing",
                "mutate": lambda root: _mutate_provenance(root, lambda payload: payload.__setitem__("self_reference_policy", "FILE-MANIFEST.json excludes CHECKSUMS.sha256 only.")),
            },
        ]
        for index, scenario in enumerate(scenarios, start=1):
            root = base / f"case-{index}"
            _clone_canary_tree(pristine, root)
            scenario["mutate"](root)
            try:
                validate_release_integrity(root)
            except ReleaseIntegrityError as exc:
                message = str(exc)
                token = scenario["expected_failure_contains"]
                add(scenario["id"], {"failure_contains": token}, message, token in message)
            else:
                add(scenario["id"], {"failure_contains": scenario["expected_failure_contains"]}, None, False)
    return results


def _mutate_file_manifest(root: pathlib.Path, mutator) -> None:
    path = root / "FILE-MANIFEST.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _mutate_provenance(root: pathlib.Path, mutator) -> None:
    path = root / "RELEASE-PROVENANCE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
