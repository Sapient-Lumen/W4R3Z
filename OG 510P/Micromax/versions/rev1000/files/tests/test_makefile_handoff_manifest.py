from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_makefile_defaults_to_archive_carried_64_chunk_manifest() -> None:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "TEST_MANIFEST ?= .artifacts/mxtest-all-64.json" in text
    assert "--json \"$(TEST_MANIFEST)\"" in text
    assert "--verify-current \"$(TEST_MANIFEST)\"" in text
    assert "--manifest-summary \"$(TEST_MANIFEST)\"" in text


def test_makefile_aggregate_runtime_budget_defaults_to_cloudtainer_safe_checkpoint() -> None:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "MAX_RUNTIME_SECONDS ?= 18" in text
    assert "--max-runtime-seconds \"$(MAX_RUNTIME_SECONDS)\"" in text


def test_makefile_manifest_default_remains_overridable() -> None:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "TEST_MANIFEST ?=" in text
    assert "$(TEST_MANIFEST)" in text


def test_makefile_doctor_chunked_uses_same_manifest_and_budget_knobs() -> None:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert 'python tools/mxdoctor.py --chunked --chunks "$(CHUNKS)"' in text
    assert '--manifest "$(TEST_MANIFEST)"' in text
    assert '--max-runtime-seconds "$(MAX_RUNTIME_SECONDS)"' in text
    assert '--max-new-tests "$(MAX_NEW_TESTS)"' in text
    assert '--max-new-files "$(MAX_NEW_FILES)"' in text
    assert '--test-batch-size "$(TEST_BATCH_SIZE)"' in text
    assert '--file-timeout "$(FILE_TIMEOUT)"' in text


def test_makefile_timely_target_uses_bounded_manifest() -> None:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "TIMELY_MANIFEST ?= .artifacts/mxtimely-mxtest.json" in text
    assert "TIMELY_TIMEOUT_SCALE ?= 1" in text
    assert "timely:" in text
    assert 'python tools/mxtimely.py --manifest "$(TIMELY_MANIFEST)"' in text
    assert "timely-tests:" in text
    assert "--with-tests --skip-doctor" in text


def test_makefile_release_suite_target_uses_bounded_manifest() -> None:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "RELEASE_MANIFEST ?= .artifacts/mxrelease-full-suite.json" in text
    assert "RELEASE_MAX_RUNTIME_SECONDS ?= 8" in text
    assert "RELEASE_BATCH_TIMEOUT ?= 20" in text
    assert "RELEASE_BATCH_SIZE ?= 12" in text
    assert "release-suite:" in text
    assert 'python tools/mxrelease.py --manifest "$(RELEASE_MANIFEST)"' in text
    assert "--allow-partial" in text
    assert "release-verify:" in text
    assert "--verify" in text
    assert "release-next:" in text
    assert "--next" in text
