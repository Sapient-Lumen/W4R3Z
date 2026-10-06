import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import warnings
import zipfile

from release_hygiene_lib import iter_release_paths, should_skip_release_path


class PackagePreflightError(RuntimeError):
    pass



FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)
FIXED_FILE_MODE = 0o644
FIXED_EXTERNAL_ATTR = (FIXED_FILE_MODE & 0xFFFF) << 16


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sidecar_line(digest: str, bundle_name: str) -> str:
    return f"{digest}  {bundle_name}\n"


def verify_sha256_sidecar(bundle_path: pathlib.Path, sidecar_path: pathlib.Path, bundle_name: str) -> str:
    """Validate the external sidecar format and digest against the emitted zip."""
    if sidecar_path.name != f"{bundle_name}.sha256":
        raise PackagePreflightError(f"sha256 sidecar filename mismatch: {sidecar_path.name}")
    if bundle_path.name != bundle_name:
        raise PackagePreflightError(f"bundle path filename mismatch: {bundle_path.name}")
    text = sidecar_path.read_text(encoding="utf-8")
    digest = sha256_path(bundle_path)
    expected = _sidecar_line(digest, bundle_name)
    if text != expected:
        raise PackagePreflightError("sha256 sidecar content mismatch")
    return digest


def write_verified_sha256_sidecar(bundle_path: pathlib.Path, sidecar_path: pathlib.Path, bundle_name: str) -> str:
    digest = sha256_path(bundle_path)
    sidecar_path.write_text(_sidecar_line(digest, bundle_name), encoding="utf-8")
    return verify_sha256_sidecar(bundle_path, sidecar_path, bundle_name)


def package_sidecar_canary_results() -> list[dict[str, object]]:
    """Run cheap sidecar format/digest canaries without full package release."""
    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="delaybasin-sidecar-canaries-") as tmp:
        base = pathlib.Path(tmp)
        bundle_name = "DelayBasin-rev9999-2099.01.01.00.00-sidecar-canary.zip"
        bundle_path = base / bundle_name
        sidecar_path = base / f"{bundle_name}.sha256"
        bundle_path.write_bytes(b"sidecar canary bundle bytes\n")
        digest = write_verified_sha256_sidecar(bundle_path, sidecar_path, bundle_name)
        rows.append({
            "id": "sidecar-valid-format-and-digest",
            "expected": "write_verified_sha256_sidecar emits exact sha256sum-compatible line and verifies it",
            "observed": {"digest": digest, "sidecar": sidecar_path.read_text(encoding="utf-8")},
            "status": "pass" if sidecar_path.read_text(encoding="utf-8") == _sidecar_line(digest, bundle_name) else "fail",
        })
        scenarios = [
            ("sidecar-wrong-digest", _sidecar_line("0" * 64, bundle_name), sidecar_path, "content mismatch"),
            ("sidecar-single-space", f"{digest} {bundle_name}\n", sidecar_path, "content mismatch"),
            ("sidecar-wrong-bundle-name", _sidecar_line(digest, "DelayBasin-rev9999-2099.01.01.00.00-other.zip"), sidecar_path, "content mismatch"),
            ("sidecar-wrong-sidecar-filename", _sidecar_line(digest, bundle_name), base / "wrong.sha256", "filename mismatch"),
        ]
        for row_id, content, path, token in scenarios:
            path.write_text(content, encoding="utf-8")
            try:
                verify_sha256_sidecar(bundle_path, path, bundle_name)
            except PackagePreflightError as exc:
                message = str(exc)
                rows.append({
                    "id": row_id,
                    "expected_failure_contains": token,
                    "observed_failure": message,
                    "status": "pass" if token in message else "fail",
                })
            else:
                rows.append({
                    "id": row_id,
                    "expected_failure_contains": token,
                    "observed_failure": None,
                    "status": "fail",
                })
    return rows


def write_deterministic_zip(root: pathlib.Path, bundle_path: pathlib.Path, bundle_name: str) -> None:
    """Write release-hygiene paths with stable ordering and fixed zip metadata."""
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in iter_release_paths(root, bundle_name):
            arcname = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(arcname, FIXED_ZIP_DT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = FIXED_EXTERNAL_ATTR
            zf.writestr(info, path.read_bytes())

def lint_preflight_command() -> list[str]:
    return [sys.executable, "-S", "tools/run_lint_suite.py"]


def lint_preflight_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_lint_preflight(root: pathlib.Path) -> None:
    """Fail closed unless the target release tree passes non-mutating lint."""
    subprocess.run(
        lint_preflight_command(),
        cwd=root,
        env=lint_preflight_env(),
        text=True,
        check=True,
    )


def expected_zip_members(root: pathlib.Path, bundle_name: str) -> list[str]:
    return [path.relative_to(root).as_posix() for path in iter_release_paths(root, bundle_name)]


def actual_zip_members(bundle_path: pathlib.Path) -> list[str]:
    with zipfile.ZipFile(bundle_path, "r") as zf:
        bad_member = zf.testzip()
        if bad_member:
            raise PackagePreflightError(f"zip member failed CRC/integrity check: {bad_member}")
        names = [info.filename for info in zf.infolist()]
    return names


def _reject_unsafe_zip_member_path(name: str) -> None:
    rel_path = pathlib.PurePosixPath(name)
    normalized = rel_path.as_posix()
    if (
        not name
        or name.startswith("/")
        or name.endswith("/")
        or "//" in name
        or "\\" in name
        or normalized != name
        or "" in rel_path.parts
        or "." in rel_path.parts
        or ".." in rel_path.parts
    ):
        raise PackagePreflightError(f"unsafe zip member path: {name}")


def safe_zip_member_target(destination: pathlib.Path, name: str) -> pathlib.Path:
    _reject_unsafe_zip_member_path(name)
    root = destination.resolve()
    target = (destination / pathlib.PurePosixPath(name).as_posix()).resolve()
    if target == root or root not in target.parents:
        raise PackagePreflightError(f"unsafe zip member path: {name}")
    return target


def validate_zip_member_set(root: pathlib.Path, bundle_path: pathlib.Path, bundle_name: str) -> list[str]:
    """Check that the emitted zip contains exactly the release-hygiene file set."""
    names = actual_zip_members(bundle_path)
    if len(names) != len(set(names)):
        raise PackagePreflightError("duplicate zip member detected")
    for name in names:
        _reject_unsafe_zip_member_path(name)
        if should_skip_release_path(pathlib.PurePosixPath(name), bundle_name):
            raise PackagePreflightError(f"release-hygiene-excluded path present in zip: {name}")
    expected = expected_zip_members(root, bundle_name)
    if names != expected:
        missing = sorted(set(expected) - set(names))[:10]
        extra = sorted(set(names) - set(expected))[:10]
        if not missing and not extra:
            raise PackagePreflightError("zip member order drifted from release paths")
        raise PackagePreflightError(f"zip member set drifted from release paths; missing={missing} extra={extra}")
    return names


def extract_zip_safely(bundle_path: pathlib.Path, destination: pathlib.Path) -> None:
    with zipfile.ZipFile(bundle_path, "r") as zf:
        for info in zf.infolist():
            target = safe_zip_member_target(destination, info.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)


def run_artifact_smoke(root: pathlib.Path, bundle_path: pathlib.Path, bundle_name: str) -> None:
    """Prove the just-emitted release zip, not merely the workspace, passes lint.

    The pre-zip lint preflight proves the regenerated working tree is admissible.
    This post-zip smoke check proves packaging did not omit, add, corrupt, or
    path-slip files and that a clean extraction can run the same lint suite.
    """
    validate_zip_member_set(root, bundle_path, bundle_name)
    with tempfile.TemporaryDirectory(prefix="delaybasin-artifact-smoke-") as tmp:
        extract_root = pathlib.Path(tmp) / "extract"
        extract_root.mkdir()
        extract_zip_safely(bundle_path, extract_root)
        run_lint_preflight(extract_root)



def _write_determinism_canary_tree(root: pathlib.Path) -> None:
    (root / "docs").mkdir(parents=True)
    (root / "zeta.txt").write_text("zeta\n", encoding="utf-8")
    (root / "README.md").write_text("deterministic writer canary\n", encoding="utf-8")
    (root / "docs" / "note.md").write_text("nested note\n", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "ghost.pyc").write_bytes(b"cached")
    frozen = root / "DelayBasin-rev0001-2000.01.01.00.00-old.zip"
    frozen.write_text("frozen bundle sediment\n", encoding="utf-8")


def package_determinism_canary_results() -> list[dict[str, object]]:
    """Run cheap writer canaries for deterministic zip bytes and metadata.

    These canaries deliberately avoid full release packaging. They isolate the
    deterministic writer so lint can catch member-order, fixed-metadata, or
    hygiene-omission drift without turning every check into a double release.
    """
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="delaybasin-zip-determinism-") as tmp:
        base = pathlib.Path(tmp)
        root = base / "tree"
        root.mkdir()
        _write_determinism_canary_tree(root)
        bundle_name = "DelayBasin-rev9999-2099.01.01.00.00-determinism-canary.zip"
        bundle_a = base / "a.zip"
        bundle_b = base / "b.zip"
        write_deterministic_zip(root, bundle_a, bundle_name)
        write_deterministic_zip(root, bundle_b, bundle_name)
        bytes_a = bundle_a.read_bytes()
        bytes_b = bundle_b.read_bytes()
        names = actual_zip_members(bundle_a)
        expected = expected_zip_members(root, bundle_name)
        infos = []
        with zipfile.ZipFile(bundle_a, "r") as zf:
            infos = zf.infolist()
        def add(row_id: str, expected_text: str, observed: object, ok: bool) -> None:
            results.append({
                "id": row_id,
                "expected": expected_text,
                "observed": observed,
                "status": "pass" if ok else "fail",
            })
        add(
            "deterministic-writer-identical-bytes",
            "two writes from the same canary tree produce identical zip bytes",
            {"sha256_a": sha256_path(bundle_a), "sha256_b": sha256_path(bundle_b), "size_a": len(bytes_a), "size_b": len(bytes_b)},
            bytes_a == bytes_b,
        )
        add(
            "deterministic-writer-member-order",
            "zip members exactly follow release-hygiene sorted paths",
            {"members": names, "expected": expected},
            names == expected,
        )
        add(
            "deterministic-writer-fixed-metadata",
            "every zip member uses fixed timestamp, file mode, compression, and no directory entries",
            [
                {
                    "filename": info.filename,
                    "date_time": list(info.date_time),
                    "external_attr": info.external_attr,
                    "compress_type": info.compress_type,
                    "is_dir": info.is_dir(),
                }
                for info in infos
            ],
            all(
                info.date_time == FIXED_ZIP_DT
                and info.external_attr == FIXED_EXTERNAL_ATTR
                and info.compress_type == zipfile.ZIP_DEFLATED
                and not info.is_dir()
                for info in infos
            ),
        )
        add(
            "deterministic-writer-hygiene-exclusions",
            "sediment excluded by release hygiene never appears in writer output",
            names,
            "__pycache__/ghost.pyc" not in names and all("DelayBasin-rev0001" not in name for name in names),
        )
        try:
            validate_zip_member_set(root, bundle_a, bundle_name)
        except PackagePreflightError as exc:
            add(
                "deterministic-writer-smoke-compatible",
                "deterministic writer output is accepted by artifact-smoke member validation",
                str(exc),
                False,
            )
        else:
            add(
                "deterministic-writer-smoke-compatible",
                "deterministic writer output is accepted by artifact-smoke member validation",
                "accepted",
                True,
            )
    return results


def _write_zip(bundle_path: pathlib.Path, members: list[tuple[str, bytes]]) -> None:
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, payload in members:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                zf.writestr(name, payload)


def _make_canary_root(root: pathlib.Path) -> tuple[pathlib.Path, str, list[tuple[str, bytes]]]:
    canary_root = root / "tree"
    (canary_root / "docs").mkdir(parents=True)
    (canary_root / "README.md").write_text("release smoke canary\n", encoding="utf-8")
    (canary_root / "docs" / "note.md").write_text("release smoke canary doc\n", encoding="utf-8")
    bundle_name = "DelayBasin-rev9999-2099.01.01.00.00-smoke-canary.zip"
    expected_members = [("README.md", b"release smoke canary\n"), ("docs/note.md", b"release smoke canary doc\n")]
    return canary_root, bundle_name, expected_members


def package_artifact_negative_canary_results() -> list[dict[str, object]]:
    """Run cheap synthetic zip mutations against artifact-smoke member/extract guards."""
    scenarios = [
        {
            "id": "zip-missing-expected-member",
            "expected_failure_contains": ["zip member set drifted", "docs/note.md"],
            "members": lambda expected: expected[:1],
            "call": "validate",
        },
        {
            "id": "zip-extra-excluded-member",
            "expected_failure_contains": ["release-hygiene-excluded path present", "__pycache__/ghost.pyc"],
            "members": lambda expected: [*expected, ("__pycache__/ghost.pyc", b"cached")],
            "call": "validate",
        },
        {
            "id": "zip-unsafe-traversal-member",
            "expected_failure_contains": ["unsafe zip member path", "../escape.txt"],
            "members": lambda expected: [*expected, ("../escape.txt", b"escape")],
            "call": "validate",
        },
        {
            "id": "zip-duplicate-member",
            "expected_failure_contains": ["duplicate zip member detected"],
            "members": lambda expected: [*expected, expected[0]],
            "call": "validate",
        },
        {
            "id": "zip-member-order-drift",
            "expected_failure_contains": ["zip member order drifted from release paths"],
            "members": lambda expected: list(reversed(expected)),
            "call": "validate",
        },
        {
            "id": "safe-extract-direct-traversal",
            "expected_failure_contains": ["unsafe zip member path", "../escape.txt"],
            "members": lambda _expected: [("../escape.txt", b"escape")],
            "call": "extract",
        },
    ]
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="delaybasin-artifact-canaries-") as tmp:
        base = pathlib.Path(tmp)
        root, bundle_name, expected_members = _make_canary_root(base)
        for scenario in scenarios:
            bundle_path = base / f"{scenario['id']}.zip"
            _write_zip(bundle_path, scenario["members"](expected_members))
            try:
                if scenario["call"] == "extract":
                    extract_dest = base / f"extract-{scenario['id']}"
                    extract_dest.mkdir()
                    extract_zip_safely(bundle_path, extract_dest)
                else:
                    validate_zip_member_set(root, bundle_path, bundle_name)
            except PackagePreflightError as exc:
                message = str(exc)
                expected = scenario["expected_failure_contains"]
                passed = all(token in message for token in expected)
                results.append({
                    "id": scenario["id"],
                    "expected_failure_contains": expected,
                    "observed_failure": message,
                    "status": "pass" if passed else "fail",
                })
                continue
            results.append({
                "id": scenario["id"],
                "expected_failure_contains": scenario["expected_failure_contains"],
                "observed_failure": None,
                "status": "fail",
            })
    return results
