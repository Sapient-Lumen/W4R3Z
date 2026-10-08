from __future__ import annotations

from pathlib import Path

import pytest

import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import mxrelease  # noqa: E402


def test_parse_pytest_counts_handles_plural_and_singular_errors() -> None:
    output = "== 7 passed, 2 skipped, 1 xfailed, 1 error in 0.12s ==\n== 3 failed, 4 errors =="

    assert mxrelease.parse_pytest_counts(output) == {
        "passed": 7,
        "failed": 3,
        "skipped": 2,
        "xfailed": 1,
        "xpassed": 0,
        "errors": 5,
    }


def test_manifest_issues_accepts_complete_current_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    source = {
        "digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "file_count": 0,
        "total_bytes": 0,
        "files": [],
    }
    files = ["tests/test_one.py"]
    batches = [
        {
            "index": 1,
            "total": 1,
            "files": files,
            "status": "passed",
            "returncode": 0,
            "timed_out": False,
            "elapsed_seconds": 0.01,
            "counts": {"passed": 1, "failed": 0, "skipped": 0, "xfailed": 0, "xpassed": 0, "errors": 0},
            "output_tail": "1 passed",
            "started_at_utc": "2026-01-01T00:00:00Z",
            "finished_at_utc": "2026-01-01T00:00:01Z",
        }
    ]
    monkeypatch.setattr(mxrelease, "discover_test_files", lambda: files)
    monkeypatch.setattr(mxrelease, "source_manifest_payload", lambda: source)
    payload = mxrelease.build_payload(
        batches=batches,
        source_manifest=source,
        files=files,
        batch_size=12,
        started_at_utc="2026-01-01T00:00:00Z",
        finished_at_utc="2026-01-01T00:00:01Z",
    )

    assert payload["ok"] is True
    assert payload["test_status_counts"] == {"passed": 1, "failed": 0, "timed_out": 0, "not_run": 0}
    assert payload["timing"]["measured_batch_count"] == 1
    assert payload["next_action"]["state"] == "verify"
    assert mxrelease.manifest_issues(payload, current_source=source) == []


def test_initial_batches_resets_when_source_digest_changes() -> None:
    previous = {
        "source_digest": "old",
        "batches": [
            {
                "files": ["tests/test_one.py"],
                "status": "passed",
                "index": 1,
                "total": 1,
                "counts": {"passed": 1},
            }
        ],
    }

    rows = mxrelease.initial_batches(
        ["tests/test_one.py"],
        previous=previous,
        source_digest="new",
        reset=False,
        batch_size=12,
    )

    assert rows[0]["status"] == "not_run"


def test_split_retryable_batches_halves_timed_out_multi_file_batch() -> None:
    row = {
        "index": 1,
        "total": 1,
        "files": ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py", "tests/test_d.py"],
        "status": "timed_out",
    }

    split = mxrelease.split_retryable_batches([row])

    assert [item["files"] for item in split] == [
        ["tests/test_a.py", "tests/test_b.py"],
        ["tests/test_c.py", "tests/test_d.py"],
    ]
    assert [item["status"] for item in split] == ["not_run", "not_run"]
    assert [item["index"] for item in split] == [1, 2]
    assert [item["total"] for item in split] == [2, 2]


def test_initial_batches_preserves_same_source_split_manifest() -> None:
    files = ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py"]
    previous = {
        "source_digest": "same",
        "batches": [
            {"index": 1, "total": 2, "files": ["tests/test_a.py"], "status": "passed"},
            {
                "index": 2,
                "total": 2,
                "files": ["tests/test_b.py", "tests/test_c.py"],
                "status": "not_run",
            },
        ],
    }

    rows = mxrelease.initial_batches(
        files,
        previous=previous,
        source_digest="same",
        reset=False,
        batch_size=12,
    )

    assert [row["files"] for row in rows] == [["tests/test_a.py"], ["tests/test_b.py", "tests/test_c.py"]]
    assert [row["status"] for row in rows] == ["passed", "not_run"]
    assert [row["index"] for row in rows] == [1, 2]


def test_split_retryable_single_file_timeout_can_split_to_collected_nodes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        mxrelease,
        "discover_test_nodes",
        lambda path: [
            f"{path}::test_one",
            f"{path}::test_two",
            f"{path}::test_three",
            f"{path}::test_four",
        ],
    )
    row = {
        "index": 1,
        "total": 1,
        "files": ["tests/test_slow.py"],
        "targets": ["tests/test_slow.py"],
        "status": "timed_out",
    }

    split = mxrelease.split_retryable_batches([row])

    assert [item["targets"] for item in split] == [
        ["tests/test_slow.py::test_one", "tests/test_slow.py::test_two"],
        ["tests/test_slow.py::test_three", "tests/test_slow.py::test_four"],
    ]
    assert [item["files"] for item in split] == [["tests/test_slow.py"], ["tests/test_slow.py"]]
    assert mxrelease.status_counts_for_files(split) == {"passed": 0, "failed": 0, "timed_out": 0, "not_run": 1}


def test_batch_timing_summary_reports_slowest_batches() -> None:
    rows = [
        {"index": 1, "files": ["tests/test_a.py"], "targets": ["tests/test_a.py"], "status": "passed", "elapsed_seconds": 0.5},
        {"index": 2, "files": ["tests/test_b.py"], "targets": ["tests/test_b.py"], "status": "passed", "elapsed_seconds": 2.0},
    ]

    timing = mxrelease.batch_timing_summary(rows, limit=1)

    assert timing["measured_batch_count"] == 2
    assert timing["total_batch_elapsed_seconds"] == 2.5
    assert timing["slowest_batches"][0]["index"] == 2
    assert timing["slowest_batches"][0]["sample"] == "tests/test_b.py"


def test_next_action_for_partial_manifest_is_copy_pasteable() -> None:
    payload = {
        "ok": False,
        "status": "partial",
        "batch_size": 3,
        "batches": [
            {"index": 1, "files": ["tests/test_a.py"], "status": "passed"},
            {"index": 2, "files": ["tests/test_b.py"], "status": "not_run"},
        ],
    }

    action = mxrelease.next_action_for_payload(payload, manifest_path=".artifacts/demo.json")

    assert action["state"] == "continue"
    assert action["make_command"] == "make release-suite"
    assert "--manifest .artifacts/demo.json" in action["command"]
    assert action["remaining_batches"] == 1
    assert action["next_batch"]["sample"] == "tests/test_b.py"


def test_next_action_for_failed_manifest_points_to_summary() -> None:
    payload = {
        "ok": False,
        "status": "failed",
        "batches": [
            {"index": 1, "targets": ["tests/test_bad.py::test_one"], "status": "failed"},
        ],
    }

    action = mxrelease.next_action_for_payload(payload, manifest_path=".artifacts/demo.json")

    assert action["state"] == "inspect-failure"
    assert action["make_command"] == "make release-summary"
    assert action["problem_batch"]["sample"] == "tests/test_bad.py::test_one"


def _write_package_input_root(
    root: Path,
    *,
    runtime_dependencies: str = "",
    dev_dependencies: str = '"pytest>=7", "ruff>=0.6"',
    requirements_dev: str = "pytest>=7\nruff>=0.6\n",
    dependency_policy: str = "hash-locked-release-builder",
    version_policy: str = "archive-revision-independent",
    backend_requirement: str = "setuptools>=77.0.3",
    build_requires: str | None = None,
    source_date_epoch: object = 1767225600,
    builder_setuptools: str = "83.0.0",
    precommit_rev: str = "v1.2.3",
) -> None:
    deps = f"dependencies = [{runtime_dependencies}]\n" if runtime_dependencies else ""
    declared_build_requires = backend_requirement if build_requires is None else build_requires
    epoch_line = f"source_date_epoch = {source_date_epoch}"
    (root / "pyproject.toml").write_text(
        "\n".join(
            [
                "[build-system]",
                f'requires = ["{declared_build_requires}"]',
                'build-backend = "setuptools.build_meta"',
                "[project]",
                'name = "demo"',
                'version = "0.1.0"',
                deps.rstrip(),
                "[project.optional-dependencies]",
                f"dev = [{dev_dependencies}]",
                "[tool.micromax.release]",
                f'dependency_policy = "{dependency_policy}"',
                f'package_version_policy = "{version_policy}"',
                f'build_backend_requirement = "{backend_requirement}"',
                'wheel_build_frontend = "pip-wheel-no-build-isolation"',
                epoch_line,
                'builder_python = "3.13.14"',
                'builder_pip = "26.1.2"',
                f'builder_setuptools = "{builder_setuptools}"',
                'builder_pytest = "9.0.3"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "requirements-dev.txt").write_text(requirements_dev, encoding="utf-8")
    (root / ".pre-commit-config.yaml").write_text(
        "\n".join(
            [
                "repos:",
                "  - repo: https://example.invalid/hooks",
                f"    rev: {precommit_rev}",
                "    hooks:",
                "      - id: demo",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "Makefile").write_text("release-inputs:\n\tpython tools/mxrelease.py --package-inputs\n", encoding="utf-8")
    lock = root / "release" / "requirements-builder.txt"
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(
        "\n".join(
            [
                "pip==26.1.2 --hash=sha256:" + "1" * 64,
                f"setuptools=={builder_setuptools or '83.0.0'} --hash=sha256:" + "2" * 64,
                "pytest==9.0.3 --hash=sha256:" + "3" * 64,
                "iniconfig==2.3.0 --hash=sha256:" + "4" * 64,
                "packaging==25.0 --hash=sha256:" + "5" * 64,
                "pluggy==1.6.0 --hash=sha256:" + "6" * 64,
                "pygments==2.20.0 --hash=sha256:" + "7" * 64,
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_package_input_report_accepts_hash_locked_release_builder() -> None:
    report = mxrelease.package_input_report(ROOT)

    assert report["ok"] is True
    assert report["schema"] == mxrelease.PACKAGE_INPUT_SCHEMA
    assert report["dependency_policy"] == "hash-locked-release-builder"
    assert report["package_version_policy"] == "archive-revision-independent"
    assert report["build_backend_requirement"] == "setuptools>=77.0.3"
    assert report["build_system_requires"] == ["setuptools>=77.0.3"]
    assert report["builder_setuptools"] == "83.0.0"
    assert report["source_date_epoch"] == 1784329200
    assert report["runtime_dependencies"] == []
    assert report["lock_status"] == "verified-hash-lock"
    assert report["lock_files"] == ["release/requirements-builder.txt"]
    assert report["builder_lock"]["sha256"]
    assert len(report["builder_lock"]["entries"]) == 7


def test_package_input_report_rejects_runtime_dependencies_without_lock(tmp_path: Path) -> None:
    _write_package_input_root(tmp_path, runtime_dependencies='"requests>=2"')

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("runtime project dependencies require" in issue for issue in report["issues"])


def test_package_input_report_rejects_dev_requirement_drift(tmp_path: Path) -> None:
    _write_package_input_root(tmp_path, requirements_dev="pytest>=7\n")

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("requirements-dev.txt does not mirror" in issue for issue in report["issues"])


def test_package_input_report_rejects_unpinned_precommit_rev(tmp_path: Path) -> None:
    _write_package_input_root(tmp_path, precommit_rev="main")

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("pre-commit hook revisions are not pinned" in issue for issue in report["issues"])


def test_package_input_report_rejects_unapproved_build_backend_floor(tmp_path: Path) -> None:
    _write_package_input_root(
        tmp_path,
        backend_requirement="setuptools>=68",
    )

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("build_backend_requirement must be" in issue for issue in report["issues"])


def test_package_input_report_rejects_build_requirement_drift(tmp_path: Path) -> None:
    _write_package_input_root(
        tmp_path,
        build_requires="setuptools==81.0.0",
    )

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("must contain only build_backend_requirement" in issue for issue in report["issues"])


def test_package_input_report_rejects_missing_exact_release_builder(tmp_path: Path) -> None:
    _write_package_input_root(tmp_path, builder_setuptools="")

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("builder_setuptools" in issue for issue in report["issues"])


def test_package_input_report_rejects_invalid_source_date_epoch(tmp_path: Path) -> None:
    _write_package_input_root(tmp_path, source_date_epoch=0)

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("source_date_epoch" in issue for issue in report["issues"])


def test_builder_lock_rejects_unhashed_or_unpinned_rows(tmp_path: Path) -> None:
    lock = tmp_path / "builder.txt"
    lock.write_text("pip==26.1.2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no SHA-256 hash"):
        mxrelease.parse_builder_lock(lock)

    lock.write_text("pip>=26 --hash=sha256:" + "a" * 64 + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exact project==version"):
        mxrelease.parse_builder_lock(lock)


def test_package_input_report_rejects_builder_lock_version_drift(tmp_path: Path) -> None:
    _write_package_input_root(tmp_path)
    lock = tmp_path / "release" / "requirements-builder.txt"
    lock.write_text(
        lock.read_text(encoding="utf-8").replace("pytest==9.0.3", "pytest==9.0.4"),
        encoding="utf-8",
    )

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("builder_pytest" in issue and "9.0.4" in issue for issue in report["issues"])


def test_package_input_report_rejects_extra_lock_file(tmp_path: Path) -> None:
    _write_package_input_root(tmp_path)
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")

    report = mxrelease.package_input_report(tmp_path)

    assert report["ok"] is False
    assert any("release lock set" in issue for issue in report["issues"])
