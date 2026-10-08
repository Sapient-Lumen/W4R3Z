from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import mxbuilder  # noqa: E402


def _wheel_info(name: str, *, directory: bool = False) -> zipfile.ZipInfo:
    value = name if not directory or name.endswith("/") else name + "/"
    info = zipfile.ZipInfo(value)
    info.create_system = 3
    info.external_attr = ((stat.S_IFDIR | 0o755) if directory else (stat.S_IFREG | 0o644)) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def _write_wheel(
    path: Path,
    *,
    project: str = "demo",
    version: str = "1.2.3",
    extra_members: list[tuple[str, bytes]] | None = None,
) -> bytes:
    dist = f"{project.replace('-', '_')}-{version}.dist-info"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            _wheel_info(f"{dist}/METADATA"),
            (
                "Metadata-Version: 2.4\n"
                f"Name: {project}\n"
                f"Version: {version}\n\n"
            ).encode("utf-8"),
        )
        archive.writestr(_wheel_info(f"{project}/__init__.py"), b"VALUE = 1\n")
        for name, payload in extra_members or []:
            archive.writestr(_wheel_info(name), payload)
    return path.read_bytes()


def _lock_row(project: str, version: str, raw: bytes) -> dict[str, object]:
    return {
        "name": project,
        "version": version,
        "hashes": [hashlib.sha256(raw).hexdigest()],
    }


def test_safe_wheel_member_rejects_raw_aliases_before_normalization() -> None:
    assert mxbuilder._safe_wheel_member("pkg/module.py").as_posix() == "pkg/module.py"
    assert mxbuilder._safe_wheel_member("pkg/").as_posix() == "pkg"

    for name in (
        "",
        "/absolute",
        "../escape",
        "pkg/../escape",
        "pkg/./module.py",
        "pkg//module.py",
        "pkg//",
        "C:/drive.py",
        "pkg\\module.py",
        "pkg\x00module.py",
    ):
        with pytest.raises(mxbuilder.BuilderError, match="unsafe wheel member"):
            mxbuilder._safe_wheel_member(name)


def test_verify_wheelhouse_binds_exact_project_version_and_bytes(tmp_path: Path) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    path = wheelhouse / "demo-1.2.3-py3-none-any.whl"
    raw = _write_wheel(path)

    rows = mxbuilder.verify_wheelhouse(
        wheelhouse,
        [_lock_row("demo", "1.2.3", raw)],
    )

    assert rows == [
        {
            "project": "demo",
            "version": "1.2.3",
            "filename": path.name,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    ]

    path.write_bytes(raw + b"substitution")
    with pytest.raises(mxbuilder.BuilderError, match="digest is not authorized"):
        mxbuilder.verify_wheelhouse(
            wheelhouse,
            [_lock_row("demo", "1.2.3", raw)],
        )


def test_verify_wheelhouse_rejects_extras_missing_and_oversized_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    path = wheelhouse / "demo-1.2.3-py3-none-any.whl"
    raw = _write_wheel(path)
    row = _lock_row("demo", "1.2.3", raw)

    (wheelhouse / "README.txt").write_text("not a wheel", encoding="utf-8")
    with pytest.raises(mxbuilder.BuilderError, match="only .whl"):
        mxbuilder.verify_wheelhouse(wheelhouse, [row])
    (wheelhouse / "README.txt").unlink()

    with pytest.raises(mxbuilder.BuilderError, match="incomplete"):
        mxbuilder.verify_wheelhouse(wheelhouse, [row, {**row, "name": "other"}])

    monkeypatch.setattr(mxbuilder, "MAX_WHEEL_BYTES", len(raw) - 1)
    with pytest.raises(mxbuilder.BuilderError, match="size is outside"):
        mxbuilder.verify_wheelhouse(wheelhouse, [row])


def test_wheel_validation_rejects_duplicate_casefold_alias_and_traversal(
    tmp_path: Path,
) -> None:
    duplicate = tmp_path / "duplicate.whl"
    _write_wheel(
        duplicate,
        extra_members=[("Demo/__init__.py", b"alias\n")],
    )
    with pytest.raises(mxbuilder.BuilderError, match="duplicate wheel member alias"):
        mxbuilder.wheel_identity(duplicate)

    traversal = tmp_path / "traversal.whl"
    _write_wheel(traversal, extra_members=[("pkg/../escape.py", b"escape\n")])
    with pytest.raises(mxbuilder.BuilderError, match="unsafe wheel member"):
        mxbuilder.wheel_identity(traversal)


def test_extract_verified_pip_checks_digest_and_writes_only_validated_members(
    tmp_path: Path,
) -> None:
    wheel = tmp_path / "pip-1.0-py3-none-any.whl"
    raw = _write_wheel(wheel, project="pip", version="1.0")
    target = tmp_path / "purelib"

    mxbuilder._extract_verified_pip(
        wheel,
        target,
        expected_sha256=hashlib.sha256(raw).hexdigest(),
    )

    assert (target / "pip" / "__init__.py").read_bytes() == b"VALUE = 1\n"
    assert (target / "pip-1.0.dist-info" / "METADATA").is_file()
    with pytest.raises(mxbuilder.BuilderError, match="changed before bootstrap"):
        mxbuilder._extract_verified_pip(
            wheel,
            tmp_path / "wrong",
            expected_sha256="0" * 64,
        )


def test_runtime_lock_preserves_hashes_and_excludes_bootstrapped_pip(
    tmp_path: Path,
) -> None:
    source = tmp_path / "builder.txt"
    source.write_text(
        "pip==1.0 --hash=sha256:" + "1" * 64 + "\n"
        "demo==2.0 --hash=sha256:" + "2" * 64 + "\n",
        encoding="utf-8",
    )
    runtime = tmp_path / "runtime.txt"

    mxbuilder._write_runtime_lock(runtime, source, excluded_project="pip")

    text = runtime.read_text(encoding="utf-8")
    assert "pip==" not in text
    assert "demo==2.0" in text
    assert "--hash=sha256:" + "2" * 64 in text


def test_receipt_self_digest_detects_tampering() -> None:
    receipt = mxbuilder.seal_receipt({"schema": mxbuilder.SCHEMA, "ok": True})
    mxbuilder.validate_receipt_digest(receipt)

    receipt["ok"] = False
    with pytest.raises(mxbuilder.BuilderError, match="self digest mismatch"):
        mxbuilder.validate_receipt_digest(receipt)


def test_run_child_sanitizes_ambient_python_and_binds_receipt_digest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt = mxbuilder.seal_receipt({"schema": mxbuilder.SCHEMA, "ok": True})
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    python = tmp_path / "venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_bytes(b"")
    monkeypatch.setenv("PYTHONPATH", "/ambient/source")
    monkeypatch.setenv("PYTHONHOME", "/ambient/home")
    monkeypatch.setenv("PIP_INDEX_URL", "https://attacker.invalid/simple")
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 7)

    monkeypatch.setattr(mxbuilder.subprocess, "run", fake_run)

    result = mxbuilder.run_child(
        python,
        receipt_path,
        ["python", "tools/mxrepro.py"],
        cwd=tmp_path,
    )

    assert result == 7
    argv, kwargs = calls[0]
    assert argv[0] == str(python)
    env = kwargs["env"]
    assert isinstance(env, dict)
    assert "PYTHONPATH" not in env
    assert "PYTHONHOME" not in env
    assert env["PIP_NO_INDEX"] == "1"
    assert env["PIP_CONFIG_FILE"] == os.devnull
    assert env["MICROMAX_BUILDER_RECEIPT"] == str(receipt_path.resolve())
    assert env["MICROMAX_BUILDER_RECEIPT_DIGEST"] == receipt["receipt_digest"]


def test_build_environment_detects_wheelhouse_change_after_install(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "source"
    lock = root / "release" / "requirements-builder.txt"
    lock.parent.mkdir(parents=True)
    lock.write_text(
        "pip==1.0 --hash=sha256:" + "1" * 64 + "\n",
        encoding="utf-8",
    )
    lock_descriptor = {
        "path": "release/requirements-builder.txt",
        "bytes": lock.stat().st_size,
        "sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "entries": [{"name": "pip", "version": "1.0", "hashes": ["1" * 64]}],
    }
    monkeypatch.setattr(
        mxbuilder.mxrelease,
        "package_input_report",
        lambda _root: {
            "ok": True,
            "builder_python": "3.13.14",
            "builder_lock": lock_descriptor,
        },
    )
    monkeypatch.setattr(mxbuilder.platform, "python_version", lambda: "3.13.14")
    monkeypatch.setattr(mxbuilder, "_run_checked", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        mxbuilder.venv.EnvBuilder,
        "create",
        lambda _self, path: Path(path).mkdir(parents=True),
    )
    monkeypatch.setattr(mxbuilder, "_purelib_for", lambda _python: tmp_path / "purelib")
    monkeypatch.setattr(mxbuilder, "_extract_verified_pip", lambda *args, **kwargs: None)
    before = [
        {
            "project": "pip",
            "version": "1.0",
            "filename": "pip.whl",
            "bytes": 10,
            "sha256": "1" * 64,
        }
    ]
    after = [{**before[0], "sha256": "2" * 64}]
    sequence = iter((before, after))
    monkeypatch.setattr(mxbuilder, "verify_wheelhouse", lambda *_args: next(sequence))

    with pytest.raises(mxbuilder.BuilderError, match="changed during offline installation"):
        mxbuilder.build_environment(root, tmp_path / "work")


def test_prepare_work_directory_rejects_file_symlink_and_nonempty(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(mxbuilder.BuilderError, match="not a directory"):
        mxbuilder._prepare_work_directory(file_path)

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(mxbuilder.BuilderError, match="not empty"):
        mxbuilder._prepare_work_directory(nonempty)

    if hasattr(os, "symlink"):
        target = tmp_path / "target"
        target.mkdir()
        link = tmp_path / "link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            pytest.skip("symlinks are unavailable")
        with pytest.raises(mxbuilder.BuilderError, match="may not be a symlink"):
            mxbuilder._prepare_work_directory(link)


def test_thaw_temporary_tree_restores_cleanup_access_without_following_symlinks(
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX permission boundary only")

    root = tmp_path / "builder"
    wheelhouse = root / "wheelhouse"
    wheelhouse.mkdir(parents=True)
    wheel = wheelhouse / "locked.whl"
    wheel.write_bytes(b"locked")
    nested = root / "nested"
    nested.mkdir()
    nested_file = nested / "result.json"
    nested_file.write_text("{}", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.write_text("outside", encoding="utf-8")
    outside.chmod(0o400)
    link = root / "outside-link"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlinks are unavailable")

    wheel.chmod(0o400)
    wheelhouse.chmod(0o500)
    nested_file.chmod(0o400)
    nested.chmod(0o500)
    mxbuilder._thaw_temporary_tree(root)

    assert stat.S_IMODE(root.stat().st_mode) == 0o700
    assert stat.S_IMODE(wheelhouse.stat().st_mode) == 0o700
    assert stat.S_IMODE(wheel.stat().st_mode) == 0o600
    assert stat.S_IMODE(nested.stat().st_mode) == 0o700
    assert stat.S_IMODE(nested_file.stat().st_mode) == 0o600
    assert stat.S_IMODE(outside.stat().st_mode) == 0o400
