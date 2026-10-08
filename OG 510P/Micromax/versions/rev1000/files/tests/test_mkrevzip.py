from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import stat
from collections import Counter
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_STAMP = "2026.03.18.16.20"
INTEGRATION_TAG = "archive-context-manifest-mapotter"


def _load_mkrevzip_module():
    spec = importlib.util.spec_from_file_location("mkrevzip_test_module", ROOT / "tools" / "mkrevzip.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mkrevzip_skips_bootstrap_virtualenv_tree() -> None:
    module = _load_mkrevzip_module()

    assert module.should_skip(Path(".venv/lib/site-packages/vendor.py"))
    assert module.should_skip(Path(".pytest_cache/v/cache/nodeids"))
    assert module.should_skip(Path(".artifacts/mxtest-plan.json"))
    assert module.should_skip(Path(".artifacts/mxtest-all-64-rev0835-probe.json"))
    assert not module.should_skip(Path(".artifacts/mxtest-all.json"))
    assert not module.should_skip(Path(".artifacts/mxtest-all-64.json"))
    assert not module.should_skip(Path(".artifacts/mxtimely-summary.json"))
    assert not module.should_skip(Path(".artifacts/mxrelease-full-suite.json"))
    assert not module.should_skip(Path(".artifacts/rev0984-history-retention.json"))
    assert module.should_skip(Path(".artifacts/rev984-history-retention.json"))
    assert module.should_skip(Path(".artifacts/rev0984-history-retention.txt"))
    assert module.should_skip(Path(".artifacts/nested/rev0984-history-retention.json"))
    assert module.should_skip(Path("build/generated.txt"))
    assert module.should_skip(Path("src/micromax_editor/plugin.cpython-313.pyc"))
    assert module.should_skip(Path("src/micromax_editor/__pycache__/plugin.cpython-313.pyc"))
    assert module.should_skip(Path("src/micromax.egg-info/SOURCES.txt"))
    assert module.should_skip(Path("Micromax-rev0000-test.zip"))
    assert not module.should_skip(Path("src/micromax/vm.py"))



@pytest.mark.parametrize(
    ("name", "reason"),
    [
        ("./payload.txt", "current"),
        ("a//payload.txt", "empty"),
        ("a/./payload.txt", "current"),
        ("a/../payload.txt", "parent"),
        ("a/payload.txt/", "empty"),
        ("a\\payload.txt", "backslash"),
        ("C:/payload.txt", "drive"),
        ("a\x00payload.txt", "NUL"),
    ],
)
def test_unsafe_member_reason_rejects_raw_path_aliases(name: str, reason: str) -> None:
    module = _load_mkrevzip_module()

    assert reason in str(module._unsafe_member_reason(name))


def test_mkrevzip_carries_current_aggregate_evidence_manifest(tmp_path) -> None:
    module = _load_mkrevzip_module()
    artifacts = tmp_path / ".artifacts"
    artifacts.mkdir(exist_ok=True)
    carried = artifacts / "mxtest-all.json"
    release = artifacts / "mxrelease-full-suite.json"
    timely = artifacts / "mxtimely-summary.json"
    revision_evidence = artifacts / "rev0984-history-retention.json"
    skipped = artifacts / "mxtest-all-64-rev0835-probe.json"
    carried.write_text('{"sentinel":"carry-me"}\n', encoding="utf-8")
    release.write_text('{"sentinel":"release-me"}\n', encoding="utf-8")
    timely.write_text('{"sentinel":"timely-me"}\n', encoding="utf-8")
    revision_evidence.write_text('{"sentinel":"revision-evidence"}\n', encoding="utf-8")
    skipped.write_text('{"sentinel":"skip-me"}\n', encoding="utf-8")
    rows = module.archive_member_rows(tmp_path, manifest_rel=Path("MICROMAX-CONTEXT.json"))
    names = {str(row["path"]) for row in rows}
    assert ".artifacts/mxtest-all.json" in names
    assert ".artifacts/mxrelease-full-suite.json" in names
    assert ".artifacts/mxtimely-summary.json" in names
    assert ".artifacts/rev0984-history-retention.json" in names
    assert ".artifacts/mxtest-all-64-rev0835-probe.json" not in names


def test_mkrevzip_rejects_invalid_or_oversized_revision_evidence(tmp_path) -> None:
    module = _load_mkrevzip_module()
    artifacts = tmp_path / ".artifacts"
    artifacts.mkdir()
    evidence = artifacts / "rev0984-invalid-evidence.json"
    evidence.write_text('{"duplicate":1,"duplicate":2}\n', encoding="utf-8")

    with pytest.raises(module.RevisionLineageError, match="duplicate JSON name"):
        module.archive_member_rows(
            tmp_path,
            manifest_rel=Path("MICROMAX-CONTEXT.json"),
        )

    evidence.write_text("[]\n", encoding="utf-8")
    with pytest.raises(module.RevisionLineageError, match="root is not an object"):
        module.archive_member_rows(
            tmp_path,
            manifest_rel=Path("MICROMAX-CONTEXT.json"),
        )

    evidence.write_bytes(b"x" * (module.REVISION_EVIDENCE_ARTIFACT_MAX_BYTES + 1))
    with pytest.raises(module.RevisionLineageError, match="exceeds byte budget"):
        module.archive_member_rows(
            tmp_path,
            manifest_rel=Path("MICROMAX-CONTEXT.json"),
        )


def test_archive_member_provenance_records_packaged_files(tmp_path) -> None:
    module = _load_mkrevzip_module()
    rows = module.archive_member_rows(ROOT, manifest_rel=Path("MICROMAX-CONTEXT.json"))
    provenance = module.archive_member_provenance(rows)

    by_path = {str(row["path"]): row for row in provenance["entries"]}
    assert provenance["schema"] == "micromax.mkrevzip.archive-provenance.v1"
    assert provenance["digest"]
    assert provenance["file_count"] == len(rows)
    assert provenance["total_bytes"] == sum(int(row["bytes"]) for row in rows)
    assert "README.md" in by_path
    assert "MICROMAX-CONTEXT.json" not in by_path
    assert len(str(by_path["README.md"]["sha256"])) == 64


def test_mkrevzip_embeds_archive_member_provenance() -> None:
    module = _load_mkrevzip_module()
    rows = module.archive_member_rows(ROOT, manifest_rel=Path("MICROMAX-CONTEXT.json"))
    manifest = module.archive_manifest(
        root=ROOT,
        rev=_expected_rev(),
        archive_name=f"Micromax-rev{_expected_rev():04d}-2026.03.18.16.23-archive-member-provenance-fennec.zip",
        tag="archive-member-provenance-fennec",
        stamp="2026.03.18.16.23",
        tz_name="America/New_York",
        manifest_name="MICROMAX-CONTEXT.json",
        provenance=module.archive_member_provenance(rows),
    )
    provenance = manifest["archive"]["provenance"]
    entry_paths = {str(row["path"]) for row in provenance["entries"]}
    assert provenance["schema"] == "micromax.mkrevzip.archive-provenance.v1"
    assert provenance["file_count"] == len(entry_paths)
    assert "README.md" in entry_paths
    assert "MICROMAX-CONTEXT.json" not in entry_paths
    assert entry_paths == {str(row["path"]) for row in rows}


def test_mkrevzip_embeds_package_input_policy_report() -> None:
    module = _load_mkrevzip_module()
    package_inputs = module.package_input_snapshot(ROOT)
    assert package_inputs["schema"] == "micromax.mxrelease.package-inputs.v1"
    assert package_inputs["ok"] is True
    assert package_inputs["dependency_policy"] == "hash-locked-release-builder"
    assert package_inputs["package_version_policy"] == "archive-revision-independent"
    assert package_inputs["lock_status"] == "verified-hash-lock"
    assert package_inputs["builder_lock"]["path"] == "release/requirements-builder.txt"


def _expected_rev() -> int:
    first = (ROOT / "TODO.md").read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"rev\s*(\d+)", first, flags=re.IGNORECASE)
    assert match is not None
    return int(match.group(1))


def test_context_snapshot_prefers_current_tree_snapshot_without_live_import(tmp_path, monkeypatch) -> None:
    module = _load_mkrevzip_module()
    rev = _expected_rev()
    context = {
        "project": "micromax",
        "rev": rev,
        "checks": {"ok": True},
        "revision_sources": {"ok": True},
        "sentinel": "from-existing-context",
    }
    (tmp_path / "MICROMAX-CONTEXT.json").write_text(json.dumps(context), encoding="utf-8")

    def fail_import(name, *args, **kwargs):
        if name == "mxcontext":
            raise AssertionError("mkrevzip should not rebuild context when the tree snapshot is current")
        return original_import(name, *args, **kwargs)

    import builtins

    original_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", fail_import)

    assert module.context_snapshot(tmp_path, rev=rev)["sentinel"] == "from-existing-context"


def test_context_snapshot_rejects_revision_mismatch(monkeypatch) -> None:
    module = _load_mkrevzip_module()
    monkeypatch.setattr(
        module,
        "_load_existing_context",
        lambda root, rev: {"project": "micromax", "rev": rev - 1},
    )

    with pytest.raises(module.RevisionLineageError, match="does not match requested revision"):
        module.context_snapshot(ROOT, rev=_expected_rev())


@pytest.fixture(scope="module")
def generated_revzip(tmp_path_factory) -> Path:
    tmp_path = tmp_path_factory.mktemp("mkrevzip-integration")
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "mkrevzip.py"),
            "--tag",
            INTEGRATION_TAG,
            "--stamp",
            INTEGRATION_STAMP,
            "--outdir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return Path(proc.stdout.strip())


def test_mkrevzip_embeds_context_manifest(generated_revzip: Path) -> None:
    outpath = generated_revzip
    assert outpath.exists()
    assert outpath.name == (
        f"Micromax-rev{_expected_rev():04d}-{INTEGRATION_STAMP}-{INTEGRATION_TAG}.zip"
    )

    with zipfile.ZipFile(outpath) as zf:
        names = set(zf.namelist())
        assert not any(name.startswith(".tmp") for name in names)
        assert "README.md" in names
        assert "MICROMAX-CONTEXT.json" in names
        assert ".artifacts/rev0984-history-retention.json" in names
        manifest = json.loads(zf.read("MICROMAX-CONTEXT.json"))

    assert manifest["archive"]["name"] == outpath.name
    assert manifest["archive"]["revision"] == _expected_rev()
    assert manifest["archive"]["tag"] == INTEGRATION_TAG
    assert manifest["archive"]["timestamp"] == INTEGRATION_STAMP
    assert manifest["archive"]["timezone"] == "America/New_York"
    assert manifest["archive"]["context_path"] == "MICROMAX-CONTEXT.json"
    assert manifest["archive"]["created_by"] == "tools/mkrevzip.py"

    context = manifest["context"]
    assert context["project"] == "micromax"
    assert context["rev"] == _expected_rev()
    assert context["checks"]["ok"] is True
    assert {
        "README.md",
        "TODO.md",
        "docs/00-vision.md",
        "docs/revision-index.json",
        "docs/installed-help-manifest.txt",
    } <= set(context["docs"])
    assert len(context["docs"]) <= 64
    assert len(context["code"]) <= 64
    assert not any(path.startswith("docs/history/") for path in context["docs"])
    assert context["inventory"]["docs"]["listed"] == len(context["docs"])
    assert context["inventory"]["catalogs"]["revision_history"] == (
        "docs/revision-index.json"
    )


def test_mkrevzip_fixed_stamp_is_byte_reproducible(tmp_path) -> None:
    outputs: list[Path] = []
    for index in range(2):
        outdir = tmp_path / f"run-{index}"
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "mkrevzip.py"),
                "--tag",
                "deterministic-archive-snapshot-kestrel",
                "--stamp",
                INTEGRATION_STAMP,
                "--outdir",
                str(outdir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        outputs.append(Path(proc.stdout.strip()))

    assert outputs[0].read_bytes() == outputs[1].read_bytes()
    expected_time = (2026, 3, 18, 16, 20, 0)
    with zipfile.ZipFile(outputs[0]) as zf:
        infos = zf.infolist()
        assert infos
        assert {info.date_time for info in infos} == {expected_time}
        assert {info.create_system for info in infos} == {3}
        assert {(info.external_attr >> 16) & 0o7777 for info in infos} == {0o644}


def test_parse_archive_name_rejects_year_outside_zip_range() -> None:
    module = _load_mkrevzip_module()

    with pytest.raises(module.RevisionLineageError, match="ZIP range"):
        module.parse_archive_name(
            "Micromax-rev0001-1979.12.31.23.59-invalid-zip-year-otter.zip"
        )

def test_mkrevzip_skips_tree_file_that_matches_manifest_name(tmp_path, monkeypatch) -> None:
    module = _load_mkrevzip_module()
    manifest_name = "ZZZ-TEMP-MANIFEST.json"
    (tmp_path / manifest_name).write_text('{"stale": true}\n', encoding="utf-8")
    (tmp_path / "payload.txt").write_text("payload\n", encoding="utf-8")
    monkeypatch.setattr(
        module,
        "context_snapshot",
        lambda root, rev: {"project": "micromax", "rev": int(rev)},
    )
    monkeypatch.setattr(
        module,
        "package_input_snapshot",
        lambda root: {"schema": "synthetic", "ok": True},
    )

    rows = module.archive_member_rows(tmp_path, manifest_rel=Path(manifest_name))
    counts = Counter(str(row["path"]) for row in rows)
    assert counts[manifest_name] == 0
    manifest = module.archive_manifest(
        root=tmp_path,
        rev=1,
        archive_name=(
            "Micromax-rev0001-2026.03.18.16.21-"
            "archive-context-manifest-skipotter.zip"
        ),
        tag="archive-context-manifest-skipotter",
        stamp="2026.03.18.16.21",
        tz_name="America/New_York",
        manifest_name=manifest_name,
        provenance=module.archive_member_provenance(rows),
    )
    assert manifest["archive"]["context_path"] == manifest_name
    assert manifest["archive"]["name"].endswith("archive-context-manifest-skipotter.zip")
    assert manifest["context"]["project"] == "micromax"



def _write_synthetic_archive(
    tmp_path,
    files: dict[str, bytes],
    *,
    name: str = "Micromax-rev0001-2026.03.18.16.24-synthetic.zip",
    source_rev: int | None = None,
    context_rev: int | None = None,
    archive_rev: int | None = None,
    timezone: str = "America/New_York",
) -> Path:
    module = _load_mkrevzip_module()
    parsed = module.parse_archive_name(name)
    filename_rev = int(parsed["revision"])
    source_revision = filename_rev if source_rev is None else int(source_rev)
    context_revision = filename_rev if context_rev is None else int(context_rev)
    archive_revision = filename_rev if archive_rev is None else int(archive_rev)
    source_files = {
        "TODO.md": (
            f"Rev{source_revision:04d} note: synthetic lineage.\n\n"
            f"# TODO (rev{source_revision:04d})\n"
        ).encode(),
        "README.md": (
            f"Rev{source_revision:04d} note: synthetic lineage.\n\n# Micromax\n"
        ).encode(),
        "docs/revision-index.json": (
            json.dumps(
                {
                    "schema": "micromax.revision-index.v1",
                    "current_rev": source_revision,
                    "entries": [{"rev": source_revision}],
                },
                sort_keys=True,
            )
            + "\n"
        ).encode(),
    }
    source_files.update(files)
    outpath = tmp_path / name
    rows = [
        {
            "path": path,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        for path, data in sorted(source_files.items())
    ]
    manifest = {
        "archive": {
            "name": name,
            "revision": archive_revision,
            "tag": parsed["tag"],
            "timestamp": parsed["timestamp"],
            "timezone": timezone,
            "context_path": "MICROMAX-CONTEXT.json",
            "created_by": "tests/test_mkrevzip.py",
            "provenance": module.archive_member_provenance(rows),
        },
        "context": {"project": "micromax", "rev": context_revision},
    }
    with zipfile.ZipFile(
        outpath,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=module.ZIP_COMPRESSION_LEVEL,
    ) as zf:
        for path, data in sorted(source_files.items()):
            zf.writestr(
                module.deterministic_zip_info(path, stamp=str(parsed["timestamp"])),
                data,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=module.ZIP_COMPRESSION_LEVEL,
            )
        zf.writestr(
            module.deterministic_zip_info(
                "MICROMAX-CONTEXT.json",
                stamp=str(parsed["timestamp"]),
            ),
            json.dumps(manifest, sort_keys=True) + "\n",
            compress_type=zipfile.ZIP_DEFLATED,
            compresslevel=module.ZIP_COMPRESSION_LEVEL,
        )
    return outpath


def _rewrite_synthetic_archive(
    outpath: Path,
    *,
    mutate_info=None,
    mutate_data=None,
    manifest_first: bool = False,
    global_comment: bytes = b"",
) -> None:
    """Rewrite a synthetic archive while preserving every field not under test."""

    with zipfile.ZipFile(outpath) as source:
        rows = [(info, source.read(info)) for info in source.infolist()]
    if manifest_first:
        rows.sort(key=lambda row: row[0].filename != "MICROMAX-CONTEXT.json")
    replacement = outpath.with_name(outpath.name + ".rewrite")
    with zipfile.ZipFile(
        replacement,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as target:
        target.comment = global_comment
        for info, data in rows:
            if mutate_info is not None:
                mutate_info(info)
            if mutate_data is not None:
                data = mutate_data(info.filename, data)
            kwargs = {"compress_type": info.compress_type}
            if info.compress_type == zipfile.ZIP_DEFLATED:
                kwargs["compresslevel"] = 9
            target.writestr(info, data, **kwargs)
    replacement.replace(outpath)


def test_mkrevzip_verifies_generated_archive(generated_revzip: Path) -> None:
    module = _load_mkrevzip_module()
    outpath = generated_revzip

    result = module.verify_archive(outpath)

    assert result["schema"] == "micromax.mkrevzip.archive-verification.v1"
    assert result["ok"] is True
    assert result["archive"] == outpath.name
    assert result["revision"] == _expected_rev()
    assert result["tag"] == INTEGRATION_TAG
    assert result["file_count"] > 0
    assert len(str(result["digest"])) == 64


def test_mkrevzip_verify_archive_cli_json(tmp_path) -> None:
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "mkrevzip.py"),
            "--verify-archive",
            str(outpath),
            "--verify-json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["schema"] == "micromax.mkrevzip.archive-verification.v1"
    assert result["ok"] is True
    assert result["archive"] == outpath.name


def test_mkrevzip_verifier_rejects_member_digest_mismatch(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})
    with zipfile.ZipFile(outpath) as zf:
        rows = [(info, zf.read(info)) for info in zf.infolist()]
    with zipfile.ZipFile(outpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for info, data in rows:
            if info.filename == "payload.txt":
                data = b"tampered readme\n"
            zf.writestr(info, data)

    try:
        module.verify_archive(outpath)
    except module.ArchiveVerificationError as exc:
        assert "changed=payload.txt" in str(exc)
    else:
        raise AssertionError("tampered archive should fail provenance verification")


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("timestamp", "timestamp is not normalized"),
        ("compression", "compression method is not DEFLATE"),
        ("platform", "creator platform is not normalized"),
        ("mode", "mode is not normalized"),
        ("extra", "noncanonical extra fields"),
        ("comment", "member comment is not empty"),
    ],
)
def test_mkrevzip_verifier_rejects_nondeterministic_member_metadata(
    tmp_path,
    mutation: str,
    message: str,
) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})

    def mutate(info: zipfile.ZipInfo) -> None:
        if info.filename != "payload.txt":
            return
        if mutation == "timestamp":
            info.date_time = (2026, 3, 18, 16, 26, 0)
        elif mutation == "compression":
            info.compress_type = zipfile.ZIP_STORED
        elif mutation == "platform":
            info.create_system = 0
        elif mutation == "mode":
            info.external_attr = 0o100600 << 16
        elif mutation == "extra":
            info.extra = b"\xfe\xca\x00\x00"
        elif mutation == "comment":
            info.comment = b"host-specific note"

    _rewrite_synthetic_archive(outpath, mutate_info=mutate)

    with pytest.raises(module.ArchiveVerificationError, match=message):
        module.verify_archive(outpath)


def test_mkrevzip_verifier_rejects_nondeterministic_member_order(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})
    _rewrite_synthetic_archive(outpath, manifest_first=True)

    with pytest.raises(module.ArchiveVerificationError, match="member order is not canonical"):
        module.verify_archive(outpath)


def test_mkrevzip_verifier_rejects_global_zip_comment(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})
    _rewrite_synthetic_archive(outpath, global_comment=b"build host note")

    with pytest.raises(module.ArchiveVerificationError, match="global comment is not empty"):
        module.verify_archive(outpath)


@pytest.mark.parametrize(
    ("member", "replacement", "message"),
    [
        (
            "MICROMAX-CONTEXT.json",
            b'{"archive":{},"archive":{}}\n',
            "archive manifest .* duplicate JSON name",
        ),
        (
            "docs/revision-index.json",
            b'{"current_rev":1,"current_rev":1,"entries":[{"rev":1}]}\n',
            "archive revision index .* duplicate JSON name",
        ),
    ],
)
def test_mkrevzip_verifier_rejects_ambiguous_json_objects(
    tmp_path,
    member: str,
    replacement: bytes,
    message: str,
) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})
    _rewrite_synthetic_archive(
        outpath,
        mutate_data=lambda name, data: replacement if name == member else data,
    )

    with pytest.raises(module.ArchiveVerificationError, match=message):
        module.verify_archive(outpath)


def test_mkrevzip_verifier_rejects_duplicate_members(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})
    with zipfile.ZipFile(outpath, "a", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("payload.txt", b"second readme\n")

    try:
        module.verify_archive(outpath)
    except module.ArchiveVerificationError as exc:
        assert "duplicate archive members" in str(exc)
    else:
        raise AssertionError("duplicate archive members should fail verification")


def test_mkrevzip_verifier_rejects_unsafe_members(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})
    with zipfile.ZipFile(outpath, "a", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("../outside.txt", b"escape\n")

    try:
        module.verify_archive(outpath)
    except module.ArchiveVerificationError as exc:
        assert "unsafe archive member" in str(exc)
        assert "parent path component" in str(exc)
    else:
        raise AssertionError("unsafe archive members should fail verification")


def test_mkrevzip_verifier_rejects_invalid_manifest_timezone(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(
        tmp_path,
        {"payload.txt": b"readme\n"},
        timezone="Mars/Olympus_Mons",
    )

    with pytest.raises(module.ArchiveVerificationError, match="timezone is invalid"):
        module.verify_archive(outpath)


def test_mkrevzip_verifier_rejects_uncompressed_budget_overflow(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(tmp_path, {"payload.txt": b"readme\n"})

    try:
        module.verify_archive(outpath, max_uncompressed_bytes=4)
    except module.ArchiveVerificationError as exc:
        assert "uncompressed bytes exceed verifier budget" in str(exc)
    else:
        raise AssertionError("archives over the verifier byte budget should fail")


def test_infer_rev_rejects_disagreeing_repository_breadcrumbs(tmp_path) -> None:
    module = _load_mkrevzip_module()
    (tmp_path / "docs").mkdir()
    (tmp_path / "TODO.md").write_text(
        "Rev0002 note: todo.\n\n# TODO (rev0002)\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "Rev0001 note: stale readme.\n\n# Micromax\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "revision-index.json").write_text(
        json.dumps({"current_rev": 2, "entries": [{"rev": 2}]}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "MICROMAX-CONTEXT.json").write_text(
        json.dumps({"context": {"project": "micromax", "rev": 2}}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(module.RevisionLineageError, match="revision sources disagree") as exc:
        module.infer_rev(tmp_path)
    assert "README.md note=1" in str(exc.value)
    assert "TODO.md note=2" in str(exc.value)


def test_mkrevzip_rev_argument_is_assertion_not_override(tmp_path) -> None:
    wrong = _expected_rev() + 1
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "mkrevzip.py"),
            "--tag",
            "revision-override-denied-otter",
            "--stamp",
            "2026.03.18.16.26",
            "--rev",
            str(wrong),
            "--outdir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 1
    assert f"requested revision {wrong} does not match repository revision" in proc.stderr
    assert list(tmp_path.glob("*.zip")) == []


def test_mkrevzip_verifier_rejects_filename_context_revision_alias(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(
        tmp_path,
        {"payload.txt": b"payload\n"},
        name="Micromax-rev0002-2026.03.18.16.24-synthetic.zip",
        source_rev=2,
        context_rev=1,
        archive_rev=2,
    )

    with pytest.raises(module.ArchiveVerificationError, match="revision sources disagree") as exc:
        module.verify_archive(outpath)
    assert "context rev=1" in str(exc.value)


def test_mkrevzip_verifier_rejects_archived_source_revision_mismatch(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outpath = _write_synthetic_archive(
        tmp_path,
        {
            "TODO.md": b"Rev0002 note: stale alias.\n\n# TODO (rev0002)\n",
            "payload.txt": b"payload\n",
        },
    )

    with pytest.raises(module.ArchiveVerificationError, match="revision sources disagree") as exc:
        module.verify_archive(outpath)
    assert "TODO.md note=2" in str(exc.value)
    assert "README.md note=1" in str(exc.value)


def test_mkrevzip_rejects_invalid_timezone_before_writing(tmp_path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "mkrevzip.py"),
            "--tag",
            "invalid-timezone-otter",
            "--stamp",
            "2026.03.18.16.27",
            "--tz",
            "Mars/Olympus_Mons",
            "--outdir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 1
    assert "archive timezone is invalid" in proc.stderr
    assert list(tmp_path.glob("*.zip")) == []


def test_mkrevzip_rejects_noncanonical_archive_tag_before_writing(tmp_path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "mkrevzip.py"),
            "--tag",
            "Bad_Tag",
            "--stamp",
            "2026.03.18.16.27",
            "--outdir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 1
    assert "archive filename must match" in proc.stderr
    assert list(tmp_path.glob("*.zip")) == []


def test_archive_member_rows_rejects_symbolic_links(tmp_path) -> None:
    module = _load_mkrevzip_module()
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_text("outside\n", encoding="utf-8")
    (tmp_path / "member-link").symlink_to(outside)

    with pytest.raises(module.RevisionLineageError, match="symbolic link"):
        module.archive_member_rows(
            tmp_path,
            manifest_rel=Path("MICROMAX-CONTEXT.json"),
        )


def test_assert_source_tree_unchanged_detects_byte_mutation(tmp_path) -> None:
    module = _load_mkrevzip_module()
    member = tmp_path / "member.txt"
    member.write_text("generation one\n", encoding="utf-8")
    rows = module.archive_member_rows(
        tmp_path,
        manifest_rel=Path("MICROMAX-CONTEXT.json"),
    )
    member.write_text("generation two\n", encoding="utf-8")

    with pytest.raises(module.RevisionLineageError, match="mixed-generation archive") as exc:
        module.assert_source_tree_unchanged(
            tmp_path,
            manifest_rel=Path("MICROMAX-CONTEXT.json"),
            expected_rows=rows,
            phase="test mutation",
        )
    assert "changed=member.txt" in str(exc.value)


def test_snapshot_archive_members_copies_verified_bytes(tmp_path) -> None:
    module = _load_mkrevzip_module()
    source = tmp_path / "source"
    source.mkdir()
    member = source / "nested" / "member.txt"
    member.parent.mkdir()
    member.write_bytes(b"verified bytes\n")
    rows = module.archive_member_rows(
        source,
        manifest_rel=Path("MICROMAX-CONTEXT.json"),
    )
    snapshot = tmp_path / "snapshot"

    module.snapshot_archive_members(source, snapshot, rows)

    assert (snapshot / "nested" / "member.txt").read_bytes() == b"verified bytes\n"


def test_snapshot_archive_members_rejects_mutated_source(tmp_path) -> None:
    module = _load_mkrevzip_module()
    source = tmp_path / "source"
    source.mkdir()
    member = source / "member.txt"
    member.write_text("before\n", encoding="utf-8")
    rows = module.archive_member_rows(
        source,
        manifest_rel=Path("MICROMAX-CONTEXT.json"),
    )
    member.write_text("after\n", encoding="utf-8")

    with pytest.raises(module.RevisionLineageError, match="mixed-generation archive"):
        module.snapshot_archive_members(source, tmp_path / "snapshot", rows)


def _release_receipt_fixture(module, *, epoch: int = 1784329200):
    provenance = module.archive_member_provenance(
        [
            {
                "path": "README.md",
                "bytes": 4,
                "sha256": hashlib.sha256(b"read").hexdigest(),
            }
        ]
    )
    source = module.release_source_descriptor(
        provenance=provenance,
        context={"project": "micromax", "rev": 965},
        revision=965,
        context_path="MICROMAX-CONTEXT.json",
        source_date_epoch=epoch,
        epoch_origin="test fixture",
    )
    wheel = {
        "schema": "micromax.mxrepro.wheel-verification.v1",
        "filename": "micromax-0.0.8-py3-none-any.whl",
        "sha256": "a" * 64,
        "bytes": 12,
        "member_count": 4,
    }
    receipt = module.seal_release_receipt(
        {
            "schema": module.RELEASE_RECEIPT_SCHEMA,
            "ok": True,
            "source": source,
            "tests": {"ok": True},
            "wheels": {
                "reproducible": True,
                "first": wheel,
                "second": dict(wheel),
            },
        }
    )
    return source, receipt


def test_release_source_digest_includes_source_date_epoch_and_origin() -> None:
    module = _load_mkrevzip_module()
    provenance = module.archive_member_provenance(
        [
            {
                "path": "README.md",
                "bytes": 4,
                "sha256": hashlib.sha256(b"read").hexdigest(),
            }
        ]
    )
    common = {
        "provenance": provenance,
        "context": {"project": "micromax", "rev": 965},
        "revision": 965,
        "context_path": "MICROMAX-CONTEXT.json",
    }

    first = module.release_source_descriptor(
        **common,
        source_date_epoch=1784329200,
        epoch_origin="policy-a",
    )
    second = module.release_source_descriptor(
        **common,
        source_date_epoch=1784329202,
        epoch_origin="policy-a",
    )
    third = module.release_source_descriptor(
        **common,
        source_date_epoch=1784329200,
        epoch_origin="policy-b",
    )

    assert first["digest"] != second["digest"]
    assert first["digest"] != third["digest"]
    assert module.validate_release_source_descriptor(first) == first


def test_release_source_validator_rejects_tampered_epoch() -> None:
    module = _load_mkrevzip_module()
    source, _receipt = _release_receipt_fixture(module)
    source["source_date_epoch"]["value"] += 2

    with pytest.raises(module.RevisionLineageError, match="source digest mismatch"):
        module.validate_release_source_descriptor(source)


def test_release_receipt_loader_rejects_duplicate_json_names(tmp_path: Path) -> None:
    module = _load_mkrevzip_module()
    path = tmp_path / "duplicate.json"
    path.write_text('{"schema":"first","schema":"second"}\n', encoding="utf-8")

    with pytest.raises(module.RevisionLineageError, match="duplicate JSON name"):
        module.load_release_receipt(path)


def test_release_receipt_loader_rejects_oversized_input(tmp_path: Path) -> None:
    module = _load_mkrevzip_module()
    path = tmp_path / "oversized.json"
    path.write_bytes(b"{" + b" " * 128 + b"}")

    with pytest.raises(module.RevisionLineageError, match="exceeds byte budget"):
        module.load_release_receipt(path, max_bytes=32)


def test_release_receipt_rejects_partially_divergent_wheel_records() -> None:
    module = _load_mkrevzip_module()
    _source, receipt = _release_receipt_fixture(module)
    receipt["wheels"]["second"]["member_count"] = 5
    receipt = module.seal_release_receipt(receipt)

    with pytest.raises(module.RevisionLineageError, match="not identical"):
        module.validate_release_receipt(receipt)

def test_snapshot_archive_members_normalizes_modes_independent_of_umask(tmp_path: Path) -> None:
    if os.name != "posix":
        pytest.skip("POSIX permission modes are the reproducibility input under test")
    module = _load_mkrevzip_module()
    source = tmp_path / "source"
    source.mkdir()
    nested = source / "docs" / "note.md"
    nested.parent.mkdir()
    nested.write_text("same bytes\n", encoding="utf-8")
    nested.chmod(0o600)
    rows = module.archive_member_rows(source, manifest_rel=Path("MICROMAX-CONTEXT.json"))
    destination = tmp_path / "snapshot"

    previous = os.umask(0o077)
    try:
        module.snapshot_archive_members(source, destination, rows)
    finally:
        os.umask(previous)

    assert stat.S_IMODE(destination.stat().st_mode) == module.SNAPSHOT_DIR_MODE
    assert stat.S_IMODE((destination / "docs").stat().st_mode) == module.SNAPSHOT_DIR_MODE
    assert stat.S_IMODE((destination / "docs" / "note.md").stat().st_mode) == module.SNAPSHOT_FILE_MODE

