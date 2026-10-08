from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import os
import stat
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import mkrevzip  # noqa: E402
import mxbuilder  # noqa: E402
import mxrelease  # noqa: E402
import mxrepro  # noqa: E402

EPOCH = 1784329200


def _record_digest(data: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
    return "sha256=" + digest.decode("ascii")


def _set_snapshot_fixture_modes(root: Path, *files: Path) -> None:
    """Make snapshot tests independent of the pytest process umask."""
    if os.name != "posix":
        return
    root.chmod(mxrepro.mkrevzip.SNAPSHOT_DIR_MODE)
    for file_path in files:
        file_path.chmod(mxrepro.mkrevzip.SNAPSHOT_FILE_MODE)


def _wheel_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 7, 17, 23, 0, 0))
    info.create_system = 3
    info.external_attr = (0o100644 << 16)
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def _write_synthetic_wheel(path: Path, *, bad_payload_digest: bool = False) -> None:
    dist = "demo-1.0.dist-info"
    files = {
        "demo/__init__.py": b'__version__ = "1.0"\n',
        f"{dist}/METADATA": (
            "Metadata-Version: 2.4\n"
            "Name: demo\n"
            "Version: 1.0\n"
            "License-Expression: MIT\n"
            "License-File: LICENSE\n\n"
        ).encode(),
        f"{dist}/WHEEL": (
            "Wheel-Version: 1.0\n"
            "Generator: test\n"
            "Root-Is-Purelib: true\n"
            "Tag: py3-none-any\n\n"
        ).encode(),
        f"{dist}/licenses/LICENSE": b"MIT\n",
    }
    record_name = f"{dist}/RECORD"
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for name, data in files.items():
        digest = "sha256=AAAAAAAA" if bad_payload_digest and name == "demo/__init__.py" else _record_digest(data)
        writer.writerow([name, digest, str(len(data))])
    writer.writerow([record_name, "", ""])
    files[record_name] = output.getvalue().encode()

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(_wheel_info(name), data)


def test_verify_wheel_checks_record_license_and_source_date_epoch(tmp_path: Path) -> None:
    wheel = tmp_path / "demo-1.0-py3-none-any.whl"
    _write_synthetic_wheel(wheel)

    result = mxrepro.verify_wheel(wheel, source_date_epoch=EPOCH)

    assert result["schema"] == mxrepro.WHEEL_VERIFICATION_SCHEMA
    assert result["filename"] == wheel.name
    assert result["member_count"] == 5
    assert result["record_entries"] == 5
    assert result["license_expression"] == "MIT"
    assert result["normalized_timestamp"] == "2026-07-17T23:00:00Z"


def test_verify_wheel_rejects_record_digest_mismatch(tmp_path: Path) -> None:
    wheel = tmp_path / "demo-1.0-py3-none-any.whl"
    _write_synthetic_wheel(wheel, bad_payload_digest=True)

    with pytest.raises(mxrepro.ReproducibleReleaseError, match="RECORD digest mismatch"):
        mxrepro.verify_wheel(wheel, source_date_epoch=EPOCH)


def _expected_builder_versions() -> dict[str, str]:
    rows = mxrelease.parse_builder_lock(ROOT / mxrelease.BUILDER_LOCK_PATH)
    return {
        "python": "3.13.14",
        **{str(row["name"]): str(row["version"]) for row in rows},
    }


def _builder_receipt() -> dict[str, object]:
    report = mxrelease.package_input_report(ROOT)
    lock = report["builder_lock"]
    wheels = []
    for row in lock["entries"]:
        wheels.append(
            {
                "project": row["name"],
                "version": row["version"],
                "filename": f"{row['name']}-{row['version']}-py3-none-any.whl",
                "bytes": 100,
                "sha256": row["hashes"][0],
            }
        )
    return mxbuilder.seal_receipt(
        {
            "schema": mxbuilder.SCHEMA,
            "ok": True,
            "python": {
                "version": "3.13.14",
                "implementation": "CPython",
                "executable_role": "setup-python-bootstrap-and-venv-base",
            },
            "lock": lock,
            "wheels": wheels,
            "installed": {
                row["name"]: row["version"] for row in lock["entries"]
            },
            "network_boundary": {
                "acquisition": "hash-checked-wheel-download-only",
                "installation": "verified-wheelhouse-pip-no-index",
                "pip_bootstrap": "safe-extract-verified-wheel",
            },
            "wheelhouse_verification": {
                "phase": "identical-before-bootstrap-and-after-install",
                "permission_boundary": "private-posix-read-only",
                "limits": {
                    "wheel_bytes": mxbuilder.MAX_WHEEL_BYTES,
                    "members": mxbuilder.MAX_WHEEL_MEMBERS,
                    "member_bytes": mxbuilder.MAX_WHEEL_MEMBER_BYTES,
                    "expanded_bytes": mxbuilder.MAX_WHEEL_UNCOMPRESSED_BYTES,
                    "metadata_bytes": mxbuilder.MAX_METADATA_BYTES,
                },
            },
        }
    )


def test_declared_environment_matches_current_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(mxrepro, "_actual_builder_versions", lambda _projects: _expected_builder_versions())

    environment = mxrepro.declared_environment(ROOT)

    assert environment["python_declared"] == "3.13.14"
    assert environment["python"] == "3.13.14"
    assert environment["pip"] == "26.1.2"
    assert environment["setuptools"] == "83.0.0"
    assert environment["pytest"] == "9.0.3"
    assert environment["builder_snapshot"] is None
    assert environment["zlib_compile"]
    assert environment["zlib_runtime"]
    assert environment["source_date_epoch"] == EPOCH


def test_declared_environment_requires_and_validates_byte_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(mxrepro, "_actual_builder_versions", lambda _projects: _expected_builder_versions())
    with pytest.raises(mxrepro.ReproducibleReleaseError, match="mxbuilder.py"):
        mxrepro.declared_environment(ROOT, require_builder_receipt=True)

    receipt = _builder_receipt()
    path = tmp_path / "builder.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    environment = mxrepro.declared_environment(
        ROOT,
        builder_receipt_path=path,
        require_builder_receipt=True,
    )
    assert environment["builder_snapshot"] == receipt

    receipt["wheels"][0]["sha256"] = "0" * 64
    path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(mxrepro.ReproducibleReleaseError, match="self digest"):
        mxrepro.declared_environment(
            ROOT, builder_receipt_path=path, require_builder_receipt=True
        )



def test_declared_environment_rejects_unbound_environment_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        mxrepro,
        "_actual_builder_versions",
        lambda _projects: _expected_builder_versions(),
    )
    receipt = _builder_receipt()
    path = tmp_path / "builder.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    monkeypatch.setenv("MICROMAX_BUILDER_RECEIPT", str(path))
    monkeypatch.delenv("MICROMAX_BUILDER_RECEIPT_DIGEST", raising=False)

    with pytest.raises(mxrepro.ReproducibleReleaseError, match="digest capability"):
        mxrepro.declared_environment(ROOT, require_builder_receipt=True)

    monkeypatch.setenv("MICROMAX_BUILDER_RECEIPT_DIGEST", "0" * 64)
    with pytest.raises(mxrepro.ReproducibleReleaseError, match="launch capability"):
        mxrepro.declared_environment(ROOT, require_builder_receipt=True)

    monkeypatch.setenv(
        "MICROMAX_BUILDER_RECEIPT_DIGEST", str(receipt["receipt_digest"])
    )
    environment = mxrepro.declared_environment(ROOT, require_builder_receipt=True)
    assert environment["builder_snapshot"] == receipt

def test_deterministic_environment_drops_ambient_python_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PYTHONPATH", "/tmp/unrelated-one:/tmp/unrelated-two")
    monkeypatch.setenv("PYTHONHOME", "/tmp/unrelated-home")
    root = tmp_path / "source"

    environment = mxrepro.deterministic_env(
        root,
        source_date_epoch=EPOCH,
        home=tmp_path / "home",
    )

    assert environment["PYTHONPATH"] == str(root / "src")
    assert "PYTHONHOME" not in environment
    assert environment["PIP_NO_INDEX"] == "1"
    assert environment["SOURCE_DATE_EPOCH"] == str(EPOCH)


def test_release_receipt_is_compact_self_digested_and_accepted() -> None:
    provenance = mkrevzip.archive_member_provenance(
        [{"path": "README.md", "bytes": 4, "sha256": hashlib.sha256(b"read").hexdigest()}]
    )
    source = mkrevzip.release_source_descriptor(
        provenance=provenance,
        context={"project": "micromax", "rev": 965},
        revision=965,
        context_path="MICROMAX-CONTEXT.json",
        source_date_epoch=EPOCH,
        epoch_origin="test",
    )
    wheel = {
        "schema": mxrepro.WHEEL_VERIFICATION_SCHEMA,
        "filename": "micromax-0.0.8-py3-none-any.whl",
        "sha256": "a" * 64,
        "bytes": 12,
    }

    receipt = mxrepro.create_release_receipt(
        source=source,
        environment={"python": "3.13.14"},
        tests={"ok": True, "commands": []},
        first_wheel=wheel,
        second_wheel=dict(wheel),
        build_commands=[],
    )

    assert "entries" not in source["archive_members"]
    assert len(json.dumps(receipt)) < 5000
    assert mkrevzip.validate_release_receipt(receipt, expected_source=source) == receipt


def test_verify_snapshot_detects_changed_tracked_bytes(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    payload = source / "README.md"
    payload.write_text("original\n", encoding="utf-8")
    context_bytes = b'{"project":"micromax","rev":965}\n'
    context = source / "MICROMAX-CONTEXT.json"
    context.write_bytes(context_bytes)
    _set_snapshot_fixture_modes(source, payload, context)
    rows = [
        {
            "path": "README.md",
            "bytes": len(b"original\n"),
            "sha256": hashlib.sha256(b"original\n").hexdigest(),
        }
    ]

    mxrepro.verify_snapshot(
        source,
        rows=rows,
        context_bytes=context_bytes,
        phase="test",
    )
    payload.write_text("changed\n", encoding="utf-8")

    with pytest.raises(mxrepro.ReproducibleReleaseError, match="changed=README.md"):
        mxrepro.verify_snapshot(
            source,
            rows=rows,
            context_bytes=context_bytes,
            phase="test",
        )


def test_verify_snapshot_rejects_permission_drift(tmp_path: Path) -> None:
    if os.name != "posix":
        pytest.skip("POSIX permission modes are the reproducibility input under test")
    source = tmp_path / "source"
    source.mkdir()
    payload = source / "README.md"
    payload.write_text("original\n", encoding="utf-8")
    context_bytes = b'{"project":"micromax","rev":965}\n'
    context = source / "MICROMAX-CONTEXT.json"
    context.write_bytes(context_bytes)
    _set_snapshot_fixture_modes(source, payload, context)
    rows = [{
        "path": "README.md",
        "bytes": len(b"original\n"),
        "sha256": hashlib.sha256(b"original\n").hexdigest(),
    }]

    mxrepro.verify_snapshot(source, rows=rows, context_bytes=context_bytes, phase="test")
    payload.chmod(0o600)

    with pytest.raises(mxrepro.ReproducibleReleaseError, match="file mode changed"):
        mxrepro.verify_snapshot(source, rows=rows, context_bytes=context_bytes, phase="test")


def test_reproducible_release_workflow_is_pinned_hash_locked_and_least_authority() -> None:
    workflow = (ROOT / ".github" / "workflows" / "reproducible-release.yml").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "permissions:\n  contents: read" in workflow
    assert "verify-unprivileged:" in workflow
    pr_job = workflow.split("verify-unprivileged:", 1)[1].split("build-and-attest:", 1)[0]
    assert "id-token: write" not in pr_job
    assert "attestations: write" not in pr_job
    assert "artifact-metadata: write" not in pr_job
    assert "!startsWith(github.ref, 'refs/tags/')" in pr_job
    assert "build-and-attest:" in workflow
    attestation_job = workflow.split("build-and-attest:", 1)[1]
    assert "github.event_name == 'workflow_dispatch'" in attestation_job
    assert "startsWith(github.ref, 'refs/tags/')" in attestation_job
    assert "id-token: write" in workflow
    assert "attestations: write" in workflow
    assert "artifact-metadata: write" in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in workflow
    assert "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97" in workflow
    assert 'python-version: "3.13.14"' in workflow
    assert "actions/attest@f7c74d28b9d84cb8768d0b8ca14a4bac6ef463e6" in workflow
    assert "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in workflow
    assert "name: micromax-attested-release-${{ github.run_id }}-${{ github.run_attempt }}" in workflow
    assert "if-no-files-found: error" in workflow
    assert "include-hidden-files: true" in workflow
    assert "retention-days: 30" in workflow
    assert workflow.count(".artifacts/mxrepro/micromax-release-receipt.json") == 2
    assert workflow.count(".artifacts/mxrepro/Micromax-rev*.zip") == 2
    assert "uses: actions/checkout@v" not in workflow
    assert "uses: actions/setup-python@v" not in workflow
    assert "uses: actions/attest@v" not in workflow
    assert "uses: actions/upload-artifact@v" not in workflow
    assert workflow.count("run: make repro-release") == 2
    assert "repro-release:" in makefile
    assert "python tools/mxbuilder.py" in makefile
    assert "--work-dir" not in makefile.split("repro-release:", 1)[1].split("\n\n", 1)[0]
    assert "--require-hashes" in (ROOT / "tools" / "mxbuilder.py").read_text(encoding="utf-8")
    assert "--archive-tag" in makefile
    assert "date +%Y" not in makefile



def test_archive_stamp_is_python_timezone_portable() -> None:
    from datetime import datetime, timezone

    stamp = mxrepro.resolve_archive_stamp(
        None,
        timezone_name="America/New_York",
        now=datetime(2026, 7, 29, 19, 5, tzinfo=timezone.utc),
    )

    assert stamp == "2026.07.29.15.05"
    assert mxrepro.resolve_archive_stamp(
        "2026.01.02.03.04", timezone_name="invalid/not-used"
    ) == "2026.01.02.03.04"
