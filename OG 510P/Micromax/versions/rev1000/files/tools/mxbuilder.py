#!/usr/bin/env python3
"""Acquire, verify, and run inside Micromax's byte-locked release builder.

The network-facing bootstrap is deliberately tiny: the ambient interpreter may
only *download* the exact wheel rows in ``release/requirements-builder.txt``.
Micromax verifies every wheel itself, creates a pip-less virtual environment,
extracts the verified pip wheel with strict ZIP/path/resource checks, and then
installs the remaining verified wheels with package-index resolution disabled.
The child
release process receives a self-digested receipt that binds its claims to the
source lock and the exact wheel bytes observed before and after installation.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import stat
import subprocess
import sys
import tempfile
import venv
import zipfile
from email.parser import Parser
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import mxrelease  # noqa: E402

SCHEMA = "micromax.release-builder.v1"
DEFAULT_LOCK = Path(mxrelease.BUILDER_LOCK_PATH)
DEFAULT_RECEIPT = "micromax-builder-receipt.json"
PYPI_SIMPLE_INDEX = "https://pypi.org/simple"

# These are safety ceilings, not expected working-set sizes.  Current locked
# wheels are all far below them, while the bounds stop a substituted or corrupt
# archive from turning verification/bootstrap into an unbounded memory/disk job.
MAX_WHEEL_BYTES = 64 * 1024 * 1024
MAX_WHEEL_MEMBERS = 25_000
MAX_WHEEL_MEMBER_BYTES = 64 * 1024 * 1024
MAX_WHEEL_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_METADATA_BYTES = 512 * 1024
_ALLOWED_WHEEL_COMPRESSION = {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}


class BuilderError(RuntimeError):
    """A release builder could not be proved safe enough to execute."""


def canonical_json(value: Mapping[str, object]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")



def seal_receipt(payload: Mapping[str, object]) -> dict[str, object]:
    if "receipt_digest" in payload:
        raise BuilderError("builder receipt payload already contains receipt_digest")
    sealed = dict(payload)
    sealed["receipt_digest"] = hashlib.sha256(canonical_json(payload)).hexdigest()
    return sealed


def validate_receipt_digest(value: Mapping[str, object]) -> None:
    claimed = value.get("receipt_digest")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise BuilderError("builder receipt has no valid self digest")
    body = dict(value)
    body.pop("receipt_digest", None)
    actual = hashlib.sha256(canonical_json(body)).hexdigest()
    if claimed != actual:
        raise BuilderError("builder receipt self digest mismatch")


def _safe_wheel_member(name: str) -> PurePosixPath:
    """Reject raw ZIP aliases before ``PurePosixPath`` can normalize them."""

    if not name or "\\" in name or "\x00" in name or name.startswith("/"):
        raise BuilderError(f"unsafe wheel member name: {name!r}")
    raw = name[:-1] if name.endswith("/") else name
    if not raw:
        raise BuilderError(f"unsafe wheel member path: {name!r}")
    parts = raw.split("/")
    if any(part in {"", ".", ".."} or ":" in part for part in parts):
        raise BuilderError(f"unsafe wheel member path: {name!r}")
    member = PurePosixPath(*parts)
    if member.is_absolute():
        raise BuilderError(f"unsafe wheel member path: {name!r}")
    return member


def _regular_zip_member(info: zipfile.ZipInfo) -> bool:
    if info.is_dir():
        return False
    mode = (int(info.external_attr) >> 16) & 0o170000
    return mode in {0, stat.S_IFREG}


def _stat_signature(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        int(value.st_dev),
        int(value.st_ino),
        int(value.st_size),
        int(value.st_mtime_ns),
        int(value.st_ctime_ns),
    )


def _read_regular_wheel(path: Path) -> bytes:
    """Read one bounded wheel from a stable regular inode."""

    try:
        if path.is_symlink():
            raise BuilderError(f"builder wheel may not be a symlink: {path.name}")
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise BuilderError(f"builder wheel is not a regular file: {path.name}")
            if before.st_size <= 0 or before.st_size > MAX_WHEEL_BYTES:
                raise BuilderError(
                    f"builder wheel size is outside the {MAX_WHEEL_BYTES}-byte budget: "
                    f"{path.name}"
                )
            raw = handle.read(MAX_WHEEL_BYTES + 1)
            after = os.fstat(handle.fileno())
        current = path.stat(follow_symlinks=False)
    except BuilderError:
        raise
    except OSError as exc:
        raise BuilderError(f"could not read builder wheel {path.name}: {exc}") from exc
    if len(raw) != before.st_size or len(raw) > MAX_WHEEL_BYTES:
        raise BuilderError(f"builder wheel changed or exceeded its byte budget: {path.name}")
    if _stat_signature(before) != _stat_signature(after):
        raise BuilderError(f"builder wheel changed while being read: {path.name}")
    if _stat_signature(before) != _stat_signature(current):
        raise BuilderError(f"builder wheel path changed while being read: {path.name}")
    return raw


def _validated_wheel_infos(
    archive: zipfile.ZipFile,
    *,
    label: str,
) -> list[tuple[zipfile.ZipInfo, PurePosixPath]]:
    infos = archive.infolist()
    if not infos or len(infos) > MAX_WHEEL_MEMBERS:
        raise BuilderError(
            f"wheel member count is outside the {MAX_WHEEL_MEMBERS}-member budget: {label}"
        )
    total = 0
    seen: set[str] = set()
    validated: list[tuple[zipfile.ZipInfo, PurePosixPath]] = []
    for info in infos:
        member = _safe_wheel_member(info.filename)
        key = member.as_posix().casefold()
        if key in seen:
            raise BuilderError(f"duplicate wheel member alias in {label}: {info.filename}")
        seen.add(key)
        if info.flag_bits & 0x1:
            raise BuilderError(f"encrypted wheel member is not allowed in {label}: {info.filename}")
        if info.compress_type not in _ALLOWED_WHEEL_COMPRESSION:
            raise BuilderError(
                f"unsupported wheel compression in {label}: {info.filename}"
            )
        if info.file_size < 0 or info.file_size > MAX_WHEEL_MEMBER_BYTES:
            raise BuilderError(
                f"wheel member exceeds the {MAX_WHEEL_MEMBER_BYTES}-byte budget in "
                f"{label}: {info.filename}"
            )
        total += int(info.file_size)
        if total > MAX_WHEEL_UNCOMPRESSED_BYTES:
            raise BuilderError(
                f"wheel exceeds the {MAX_WHEEL_UNCOMPRESSED_BYTES}-byte expanded budget: "
                f"{label}"
            )
        if not info.is_dir() and not _regular_zip_member(info):
            raise BuilderError(f"non-regular wheel member in {label}: {info.filename}")
        validated.append((info, member))
    return validated


def _wheel_identity_from_bytes(raw: bytes, *, label: str) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = _validated_wheel_infos(archive, label=label)
            metadata_infos = [
                (info, member)
                for info, member in infos
                if len(member.parts) == 2
                and member.parts[0].endswith(".dist-info")
                and member.parts[1] == "METADATA"
            ]
            if len(metadata_infos) != 1:
                raise BuilderError(
                    f"wheel must contain exactly one top-level METADATA: {label}"
                )
            info, _member = metadata_infos[0]
            if info.file_size > MAX_METADATA_BYTES:
                raise BuilderError(f"wheel METADATA exceeds its byte budget: {label}")
            metadata_bytes = archive.read(info)
    except BuilderError:
        raise
    except (OSError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise BuilderError(f"unreadable builder wheel {label}: {exc}") from exc
    if len(metadata_bytes) > MAX_METADATA_BYTES:
        raise BuilderError(f"wheel METADATA exceeds its byte budget: {label}")
    try:
        metadata = Parser().parsestr(metadata_bytes.decode("utf-8"))
    except UnicodeError as exc:
        raise BuilderError(f"wheel METADATA is not UTF-8: {label}") from exc
    names = metadata.get_all("Name", [])
    versions = metadata.get_all("Version", [])
    if len(names) != 1 or len(versions) != 1:
        raise BuilderError(f"wheel METADATA must declare one Name and Version: {label}")
    name = mxrelease.canonical_project_name(str(names[0]))
    version = str(versions[0]).strip()
    if not name or not version or any(ord(char) < 0x20 for char in version):
        raise BuilderError(f"wheel metadata has invalid Name or Version: {label}")
    return name, version


def wheel_identity(path: Path) -> tuple[str, str]:
    """Read normalized project/version authority from one bounded wheel."""

    path = Path(path)
    return _wheel_identity_from_bytes(_read_regular_wheel(path), label=path.name)


def verify_wheelhouse(
    wheelhouse: Path,
    lock_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Return exact wheel descriptors, rejecting extras, gaps, and bad bytes."""

    expected = {
        str(row["name"]): {
            "version": str(row["version"]),
            "hashes": {str(value) for value in row.get("hashes", [])},
        }
        for row in lock_rows
    }
    if not wheelhouse.is_dir() or wheelhouse.is_symlink():
        raise BuilderError(f"builder wheelhouse is not a private directory: {wheelhouse}")
    paths = sorted(wheelhouse.iterdir(), key=lambda item: item.name.casefold())
    if any(path.suffix.lower() != ".whl" for path in paths):
        raise BuilderError("builder wheelhouse may contain only .whl files")
    found: dict[str, dict[str, object]] = {}
    for path in paths:
        raw = _read_regular_wheel(path)
        name, version = _wheel_identity_from_bytes(raw, label=path.name)
        if name not in expected:
            raise BuilderError(f"unexpected project in builder wheelhouse: {name}")
        if name in found:
            raise BuilderError(f"duplicate project in builder wheelhouse: {name}")
        digest = hashlib.sha256(raw).hexdigest()
        authority = expected[name]
        if version != authority["version"]:
            raise BuilderError(
                f"builder wheel version mismatch for {name}: "
                f"{version} != {authority['version']}"
            )
        if digest not in authority["hashes"]:
            raise BuilderError(f"builder wheel digest is not authorized for {name}")
        found[name] = {
            "project": name,
            "version": version,
            "filename": path.name,
            "bytes": len(raw),
            "sha256": digest,
        }
    missing = sorted(set(expected) - set(found))
    if missing:
        raise BuilderError("builder wheelhouse is incomplete: " + ", ".join(missing))
    return [found[name] for name in sorted(found)]


def _extract_verified_pip(
    wheel: Path,
    purelib: Path,
    *,
    expected_sha256: str | None = None,
) -> None:
    """Bootstrap the verified pip wheel without using an older installer."""

    raw = _read_regular_wheel(wheel)
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha256 != expected_sha256:
        raise BuilderError("verified pip wheel changed before bootstrap extraction")
    purelib.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = _validated_wheel_infos(archive, label=wheel.name)
            for info, member in infos:
                destination = purelib.joinpath(*member.parts)
                if info.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                written = 0
                with archive.open(info) as source, destination.open("xb") as target:
                    while True:
                        chunk = source.read(min(1024 * 1024, MAX_WHEEL_MEMBER_BYTES + 1 - written))
                        if not chunk:
                            break
                        written += len(chunk)
                        if written > info.file_size or written > MAX_WHEEL_MEMBER_BYTES:
                            raise BuilderError(
                                f"pip wheel member expanded beyond its declared budget: "
                                f"{info.filename}"
                            )
                        target.write(chunk)
                if written != info.file_size:
                    raise BuilderError(
                        f"pip wheel member length mismatch: {info.filename}"
                    )
    except BuilderError:
        raise
    except (OSError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise BuilderError(f"could not extract verified pip wheel: {exc}") from exc


def _venv_python(environment: Path) -> Path:
    return environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _venv_bin(environment: Path) -> Path:
    return environment / ("Scripts" if os.name == "nt" else "bin")


def _base_builder_env(*, offline: bool) -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    for key in list(env):
        if key.startswith("PIP_"):
            env.pop(key, None)
    env.update(
        {
            "PIP_CONFIG_FILE": os.devnull,
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_CACHE_DIR": "1",
            "PYTHONNOUSERSITE": "1",
        }
    )
    if offline:
        env["PIP_NO_INDEX"] = "1"
    return env


def _purelib_for(python: Path) -> Path:
    proc = subprocess.run(
        [str(python), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
        check=False,
        capture_output=True,
        text=True,
        env=_base_builder_env(offline=True),
    )
    if proc.returncode != 0:
        raise BuilderError("could not locate virtual-environment purelib")
    path = Path(proc.stdout.strip())
    if not path.is_absolute():
        raise BuilderError("virtual-environment purelib is not absolute")
    return path


def _write_runtime_lock(
    path: Path,
    source_lock: Path,
    *,
    excluded_project: str,
) -> None:
    rows = mxrelease.parse_builder_lock(source_lock)
    kept = [row for row in rows if row["name"] != excluded_project]
    lines = [
        "# Derived from the repository lock; pip itself was safely extracted first."
    ]
    for row in kept:
        hashes = " \\\n    ".join(f"--hash=sha256:{value}" for value in row["hashes"])
        lines.append(f"{row['name']}=={row['version']} \\\n    {hashes}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_checked(argv: Sequence[str], *, cwd: Path, env: Mapping[str, str]) -> None:
    proc = subprocess.run(list(argv), cwd=str(cwd), env=dict(env), check=False)
    if proc.returncode != 0:
        raise BuilderError(
            f"builder command failed with exit code {proc.returncode}: "
            + " ".join(str(value) for value in argv)
        )


def _installed_versions(python: Path, projects: Sequence[str]) -> dict[str, str]:
    script = (
        "import importlib.metadata,json,sys;"
        "print(json.dumps({n:importlib.metadata.version(n) for n in sys.argv[1:]},sort_keys=True))"
    )
    proc = subprocess.run(
        [str(python), "-c", script, *projects],
        check=False,
        capture_output=True,
        text=True,
        env=_base_builder_env(offline=True),
    )
    if proc.returncode != 0:
        raise BuilderError("could not inspect installed release-builder versions")
    try:
        value = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise BuilderError("release-builder version probe returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise BuilderError("release-builder version probe returned the wrong shape")
    return {str(key): str(item) for key, item in value.items()}


def _prepare_work_directory(work_dir: Path) -> Path:
    candidate = Path(work_dir).expanduser()
    if candidate.is_symlink():
        raise BuilderError(f"builder work directory may not be a symlink: {candidate}")
    if candidate.exists() and not candidate.is_dir():
        raise BuilderError(f"builder work path is not a directory: {candidate}")
    candidate = candidate.resolve()
    if candidate.exists() and any(candidate.iterdir()):
        raise BuilderError(f"builder work directory is not empty: {candidate}")
    candidate.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == "posix":
        candidate.chmod(0o700)
    return candidate


def _freeze_wheelhouse(wheelhouse: Path) -> str:
    """Make verified wheel bytes read-only on platforms with POSIX modes."""

    if os.name != "posix":
        return "platform-best-effort"
    for path in wheelhouse.iterdir():
        path.chmod(0o400)
    wheelhouse.chmod(0o500)
    return "private-posix-read-only"


def _thaw_temporary_tree(root: Path) -> None:
    """Restore owner permissions so a private temporary builder can be removed."""

    if os.name != "posix" or not root.exists():
        return
    # The wheelhouse is intentionally non-writable while untrusted installer
    # code consumes it.  TemporaryDirectory cannot unlink children from a 0500
    # directory, so restore only owner access after the child has exited.  Do
    # not chmod symlinks: a child process must not be able to redirect cleanup
    # permissions to an object outside the private tree.
    root.chmod(0o700)
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        for name in directories:
            path = current_path / name
            try:
                mode = path.lstat().st_mode
            except OSError:
                continue
            if stat.S_ISDIR(mode):
                path.chmod(0o700)
        for name in files:
            path = current_path / name
            try:
                mode = path.lstat().st_mode
            except OSError:
                continue
            if stat.S_ISREG(mode):
                path.chmod(0o600)


def build_environment(
    root: Path,
    work_dir: Path,
    *,
    bootstrap_python: Path | None = None,
) -> tuple[Path, Path, dict[str, object]]:
    """Acquire and construct one verified offline builder environment."""

    root = root.resolve()
    work_dir = _prepare_work_directory(work_dir)
    lock_path = root / DEFAULT_LOCK
    report = mxrelease.package_input_report(root)
    if report.get("ok") is not True:
        issues = report.get("issues")
        detail = (
            "; ".join(str(item) for item in issues)
            if isinstance(issues, list)
            else "unknown"
        )
        raise BuilderError("package input policy failed: " + detail)
    rows = mxrelease.parse_builder_lock(lock_path)
    expected_python = str(report.get("builder_python") or "")
    actual_python = platform.python_version()
    if actual_python != expected_python:
        raise BuilderError(
            f"bootstrap Python {actual_python} does not match declared {expected_python}"
        )

    wheelhouse = work_dir / "wheelhouse"
    wheelhouse.mkdir(mode=0o700)
    bootstrap = (bootstrap_python or Path(sys.executable)).resolve()
    acquire = [
        str(bootstrap),
        "-m",
        "pip",
        "download",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "--index-url",
        PYPI_SIMPLE_INDEX,
        "--require-hashes",
        "--only-binary=:all:",
        "--no-deps",
        "--dest",
        str(wheelhouse),
        "--requirement",
        str(lock_path),
    ]
    _run_checked(acquire, cwd=root, env=_base_builder_env(offline=False))
    wheels_before = verify_wheelhouse(wheelhouse, rows)
    permission_boundary = _freeze_wheelhouse(wheelhouse)

    environment = work_dir / "venv"
    venv.EnvBuilder(with_pip=False, clear=False, symlinks=False).create(environment)
    python = _venv_python(environment)
    pip_row = next(item for item in wheels_before if item["project"] == "pip")
    _extract_verified_pip(
        wheelhouse / str(pip_row["filename"]),
        _purelib_for(python),
        expected_sha256=str(pip_row["sha256"]),
    )

    runtime_lock = work_dir / "requirements-install.txt"
    _write_runtime_lock(runtime_lock, lock_path, excluded_project="pip")
    install = [
        str(python),
        "-m",
        "pip",
        "install",
        "--no-index",
        "--find-links",
        str(wheelhouse),
        "--require-hashes",
        "--only-binary=:all:",
        "--no-deps",
        "--requirement",
        str(runtime_lock),
    ]
    _run_checked(install, cwd=root, env=_base_builder_env(offline=True))

    # Re-open and re-hash every wheel after the installer has consumed them.
    # This closes ordinary accidental/ambient mutation races; same-UID hostile
    # mutation is additionally narrowed by the private, read-only work tree.
    wheels_after = verify_wheelhouse(wheelhouse, rows)
    if wheels_after != wheels_before:
        raise BuilderError("builder wheelhouse changed during offline installation")

    projects = [str(row["name"]) for row in rows]
    installed = _installed_versions(python, projects)
    expected = {str(row["name"]): str(row["version"]) for row in rows}
    if installed != expected:
        raise BuilderError(
            f"installed builder versions differ from the lock: "
            f"{installed!r} != {expected!r}"
        )
    lock_descriptor = report.get("builder_lock")
    if not isinstance(lock_descriptor, dict):
        raise BuilderError("package policy omitted the builder lock descriptor")
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "ok": True,
        "python": {
            "version": actual_python,
            "implementation": platform.python_implementation(),
            "executable_role": "setup-python-bootstrap-and-venv-base",
        },
        "lock": dict(lock_descriptor),
        "wheels": wheels_after,
        "installed": installed,
        "network_boundary": {
            "acquisition": "hash-checked-wheel-download-only",
            "installation": "verified-wheelhouse-pip-no-index",
            "pip_bootstrap": "safe-extract-verified-wheel",
        },
        "wheelhouse_verification": {
            "phase": "identical-before-bootstrap-and-after-install",
            "permission_boundary": permission_boundary,
            "limits": {
                "wheel_bytes": MAX_WHEEL_BYTES,
                "members": MAX_WHEEL_MEMBERS,
                "member_bytes": MAX_WHEEL_MEMBER_BYTES,
                "expanded_bytes": MAX_WHEEL_UNCOMPRESSED_BYTES,
                "metadata_bytes": MAX_METADATA_BYTES,
            },
        },
    }
    receipt = seal_receipt(payload)
    receipt_path = work_dir / DEFAULT_RECEIPT
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if os.name == "posix":
        receipt_path.chmod(0o400)
    return python, receipt_path, receipt


def run_child(
    python: Path,
    receipt_path: Path,
    command: Sequence[str],
    *,
    cwd: Path,
) -> int:
    if not command:
        raise BuilderError("no release command was supplied after --")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BuilderError(f"could not read builder receipt before launch: {exc}") from exc
    if not isinstance(receipt, dict):
        raise BuilderError("builder receipt must be a JSON object")
    validate_receipt_digest(receipt)
    digest = str(receipt["receipt_digest"])

    argv = [str(value) for value in command]
    if Path(argv[0]).name.lower() in {"python", "python3", "python.exe"}:
        argv[0] = str(python)
    env = _base_builder_env(offline=True)
    env["MICROMAX_BUILDER_RECEIPT"] = str(receipt_path.resolve())
    env["MICROMAX_BUILDER_RECEIPT_DIGEST"] = digest
    env["PATH"] = str(_venv_bin(python.parent.parent)) + os.pathsep + env.get("PATH", "")
    return subprocess.run(argv, cwd=str(cwd), env=env, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--work-dir", default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    root = Path(str(args.root)).resolve()
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    temporary: tempfile.TemporaryDirectory[str] | None = None
    try:
        if args.work_dir:
            work_dir = Path(str(args.work_dir))
        else:
            temporary = tempfile.TemporaryDirectory(prefix="micromax-builder-")
            work_dir = Path(temporary.name)
        python, receipt_path, _receipt = build_environment(root, work_dir)
        return run_child(python, receipt_path, command, cwd=root)
    except (BuilderError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"release builder failed: {exc}\n")
    finally:
        if temporary is not None:
            _thaw_temporary_tree(Path(temporary.name))
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
