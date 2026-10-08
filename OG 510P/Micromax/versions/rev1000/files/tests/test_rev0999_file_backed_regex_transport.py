from __future__ import annotations

import importlib.util
import json
import multiprocessing
import os
import stat
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest

import micromax.regex_runtime as regex_runtime
from micromax.regex_runtime import (
    RegexWorkerProtocolError,
    RegexWorkerTimeoutError,
    bounded_regex_replacement_rows_from_chunks,
    run_regex_worker_from_chunks,
)
from micromax.regex_worker_child import (
    HAYSTACK_FILE_PROTOCOL,
    PROTOCOL,
    execute_worker_request,
)
from micromax_editor.query_replace import QueryReplaceSourceSnapshot
from micromax_editor.replace_plan import (
    scan_regex_replacement_edits_lines,
    scan_replacement_edits,
)


ROOT = Path(__file__).resolve().parents[1]


def _load_measurement_tool() -> ModuleType:
    path = ROOT / "tools" / "measure_qreplace_regex_transport.py"
    spec = importlib.util.spec_from_file_location(
        "test_measure_qreplace_regex_transport",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _scan_signature(scan: object) -> tuple[object, ...]:
    return (
        getattr(scan, "ok"),
        getattr(scan, "error"),
        getattr(scan, "edits"),
        getattr(scan, "worker_routed"),
        getattr(scan, "timed_out"),
    )


def _file_request(path: Path, source: str) -> dict[str, object]:
    data = source.encode("utf-8", errors="surrogatepass")
    path.write_bytes(data)
    return {
        "protocol": PROTOCOL,
        "action": "re.search",
        "haystack_file": {
            "protocol": HAYSTACK_FILE_PROTOCOL,
            "path": str(path),
            "bytes": len(data),
            "characters": len(source),
        },
        "pattern": "right",
        "start": 0,
        "flags": "",
        "replacement": None,
        "max_matches": 1,
        "replace_all": True,
        "max_result_bytes": 4096,
        "max_memory_headroom_bytes": None,
    }


def test_chunk_transport_preserves_multiline_unicode_and_capture_expansion() -> None:
    chunks = ("Aİ", "\nnee", "dle-", "42\n", "tail")

    rows = bounded_regex_replacement_rows_from_chunks(
        chunks,
        r"(?m)^needle-([0-9]+)$",
        r"value-\1",
        expected_haystack_chars=len("Aİ\nneedle-42\ntail"),
        timeout_seconds=1.0,
        max_matches=10,
    )

    assert rows == ((3, 12, "value-42"),)


def test_chunk_transport_spawn_adapter_uses_same_file_backed_protocol() -> None:
    value = run_regex_worker_from_chunks(
        action="re.search",
        haystack_chunks=("abc", "\n", "123"),
        expected_haystack_chars=7,
        pattern=r"([0-9]+)$",
        timeout_seconds=5.0,
        worker_context=multiprocessing.get_context("spawn"),
    )

    assert value["start"] == 4
    assert value["end"] == 7
    assert value["groups"] == ["123"]


def test_subprocess_request_contains_only_small_descriptor_and_cleans_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = "left\udcff\nright"
    observed: dict[str, Path] = {}

    def inspect_request(
        request: dict[str, object],
        *,
        timeout: float,
        startup_timeout: float,
        max_result_bytes: int,
    ) -> dict[str, object]:
        del timeout, startup_timeout, max_result_bytes
        assert "haystack" not in request
        descriptor = request["haystack_file"]
        assert isinstance(descriptor, dict)
        assert descriptor["protocol"] == HAYSTACK_FILE_PROTOCOL
        path = Path(str(descriptor["path"]))
        observed["path"] = path
        assert path.is_file()
        if os.name == "posix":
            assert stat.S_IMODE(path.parent.stat().st_mode) & 0o077 == 0
        with path.open(
            "r",
            encoding="utf-8",
            errors="surrogatepass",
            newline="",
        ) as stream:
            assert stream.read() == source
        encoded = json.dumps(
            request,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        assert len(encoded) < 2048
        return {"protocol": PROTOCOL, "ok": True, "value": 0}

    monkeypatch.setattr(
        regex_runtime,
        "_run_stdlib_subprocess_worker",
        inspect_request,
    )

    assert (
        run_regex_worker_from_chunks(
            action="re.search",
            haystack_chunks=("left", "\udcff", "\nright"),
            expected_haystack_chars=len(source),
            pattern="absent",
            timeout_seconds=1.0,
        )
        == 0
    )
    path = observed["path"]
    assert not path.exists()
    assert not path.parent.exists()


@pytest.mark.parametrize(
    "failure",
    [
        RegexWorkerTimeoutError("late"),
        RegexWorkerProtocolError("startup failed"),
        KeyboardInterrupt(),
    ],
)
def test_chunk_transport_cleans_private_source_on_failure_or_interruption(
    monkeypatch: pytest.MonkeyPatch,
    failure: BaseException,
) -> None:
    observed: dict[str, Path] = {}

    def fail_request(
        request: dict[str, object],
        *,
        timeout: float,
        startup_timeout: float,
        max_result_bytes: int,
    ) -> dict[str, object]:
        del timeout, startup_timeout, max_result_bytes
        descriptor = request["haystack_file"]
        assert isinstance(descriptor, dict)
        observed["path"] = Path(str(descriptor["path"]))
        raise failure

    monkeypatch.setattr(
        regex_runtime,
        "_run_stdlib_subprocess_worker",
        fail_request,
    )

    with pytest.raises(type(failure)):
        run_regex_worker_from_chunks(
            action="re.search",
            haystack_chunks=("a" * 4096,),
            expected_haystack_chars=4096,
            pattern="a",
            timeout_seconds=1.0,
        )

    path = observed["path"]
    assert not path.exists()
    assert not path.parent.exists()


def test_chunk_transport_cleans_private_directory_after_staging_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, Path] = {}

    def fail_write(path: Path, chunks: object) -> tuple[int, int]:
        del chunks
        observed["path"] = path
        path.write_text("partial", encoding="utf-8")
        raise RegexWorkerProtocolError("simulated staging failure")

    monkeypatch.setattr(regex_runtime, "_write_haystack_chunks", fail_write)

    with pytest.raises(RegexWorkerProtocolError, match="simulated staging failure"):
        run_regex_worker_from_chunks(
            action="re.search",
            haystack_chunks=("abc",),
            expected_haystack_chars=3,
            pattern="a",
            timeout_seconds=1.0,
        )

    path = observed["path"]
    assert not path.exists()
    assert not path.parent.exists()


def test_chunk_transport_maps_private_directory_setup_failure_before_consumption(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    consumed = False

    def chunks() -> Iterator[str]:
        nonlocal consumed
        consumed = True
        yield "abc"

    def fail_setup(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise OSError("no temporary storage")

    monkeypatch.setattr(regex_runtime.tempfile, "TemporaryDirectory", fail_setup)

    with pytest.raises(
        RegexWorkerProtocolError,
        match="haystack transport setup failed: no temporary storage",
    ):
        run_regex_worker_from_chunks(
            action="re.search",
            haystack_chunks=chunks(),
            expected_haystack_chars=3,
            pattern="a",
            timeout_seconds=1.0,
        )
    assert consumed is False


def test_chunk_transport_surfaces_cleanup_failure_after_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    transport_directory = tmp_path / "transport-success"
    transport_directory.mkdir(mode=0o700)

    class CleanupFailureDirectory:
        name = str(transport_directory)

        def cleanup(self) -> None:
            raise PermissionError("source remains locked")

    monkeypatch.setattr(
        regex_runtime.tempfile,
        "TemporaryDirectory",
        lambda *args, **kwargs: CleanupFailureDirectory(),
    )
    monkeypatch.setattr(
        regex_runtime,
        "_run_stdlib_subprocess_worker",
        lambda *args, **kwargs: {"protocol": PROTOCOL, "ok": True, "value": 0},
    )

    try:
        with pytest.raises(
            RegexWorkerProtocolError,
            match="haystack transport cleanup failed: source remains locked",
        ):
            run_regex_worker_from_chunks(
                action="re.search",
                haystack_chunks=("abc",),
                expected_haystack_chars=3,
                pattern="a",
                timeout_seconds=1.0,
            )
        assert (transport_directory / "haystack.utf8").read_text() == "abc"
    finally:
        (transport_directory / "haystack.utf8").unlink(missing_ok=True)
        transport_directory.rmdir()


def test_chunk_transport_preserves_primary_failure_when_cleanup_also_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    transport_directory = tmp_path / "transport-primary"
    transport_directory.mkdir(mode=0o700)

    class CleanupFailureDirectory:
        name = str(transport_directory)

        def cleanup(self) -> None:
            raise PermissionError("source remains locked")

    def fail_worker(*args: object, **kwargs: object) -> dict[str, object]:
        del args, kwargs
        raise RegexWorkerTimeoutError("late")

    monkeypatch.setattr(
        regex_runtime.tempfile,
        "TemporaryDirectory",
        lambda *args, **kwargs: CleanupFailureDirectory(),
    )
    monkeypatch.setattr(regex_runtime, "_run_stdlib_subprocess_worker", fail_worker)

    try:
        with pytest.raises(RegexWorkerTimeoutError, match="late") as exc_info:
            run_regex_worker_from_chunks(
                action="re.search",
                haystack_chunks=("abc",),
                expected_haystack_chars=3,
                pattern="a",
                timeout_seconds=1.0,
            )
        notes = getattr(exc_info.value, "__notes__", ())
        assert notes == [
            "regex worker haystack transport cleanup failed: "
            "source remains locked"
        ]
    finally:
        (transport_directory / "haystack.utf8").unlink(missing_ok=True)
        transport_directory.rmdir()


def test_chunk_transport_preserves_primary_failure_without_add_note_api(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Python 3.10 has no BaseException.add_note; cleanup must not replace it."""

    transport_directory = tmp_path / "transport-python310"
    transport_directory.mkdir(mode=0o700)

    class CleanupFailureDirectory:
        name = str(transport_directory)

        def cleanup(self) -> None:
            raise PermissionError("source remains locked")

    class LegacyPrimaryFailure(RegexWorkerTimeoutError):
        add_note = None

    def fail_worker(*args: object, **kwargs: object) -> dict[str, object]:
        del args, kwargs
        raise LegacyPrimaryFailure("late")

    monkeypatch.setattr(
        regex_runtime.tempfile,
        "TemporaryDirectory",
        lambda *args, **kwargs: CleanupFailureDirectory(),
    )
    monkeypatch.setattr(regex_runtime, "_run_stdlib_subprocess_worker", fail_worker)

    try:
        with pytest.raises(LegacyPrimaryFailure, match="late"):
            run_regex_worker_from_chunks(
                action="re.search",
                haystack_chunks=("abc",),
                expected_haystack_chars=3,
                pattern="a",
                timeout_seconds=1.0,
            )
    finally:
        (transport_directory / "haystack.utf8").unlink(missing_ok=True)
        transport_directory.rmdir()


def test_file_transport_request_escapes_surrogate_filesystem_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A surrogateescaped temp root must not break the small JSON descriptor."""

    ready = (
        json.dumps({"protocol": PROTOCOL, "ready": True}, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    response = json.dumps(
        {"protocol": PROTOCOL, "ok": True, "value": []},
        separators=(",", ":"),
    ).encode("utf-8")
    captured: list[bytes] = []

    class ReadyStream:
        def readline(self, _limit: int = -1) -> bytes:
            return ready

    class Process:
        stdout = ReadyStream()
        returncode = 0

        def communicate(
            self,
            input: bytes | None = None,
            timeout: float | None = None,
        ) -> tuple[bytes, bytes]:
            del timeout
            captured.append(input or b"")
            return response, b""

        def kill(self) -> None:
            self.returncode = -9

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            return int(self.returncode)

    monkeypatch.setattr(
        regex_runtime,
        "start_subprocess_with_deadline",
        lambda *args, **kwargs: Process(),
    )
    surrogate_path = "/tmp/micromax-regex-\udcff/haystack.utf8"
    request = {
        "protocol": PROTOCOL,
        "action": "re.replace-rows",
        "haystack_file": {
            "protocol": HAYSTACK_FILE_PROTOCOL,
            "path": surrogate_path,
            "bytes": 3,
            "characters": 3,
        },
        "pattern": "a",
        "start": 0,
        "flags": "",
        "replacement": "b",
        "max_matches": 1,
        "replace_all": True,
        "max_result_bytes": 4096,
        "max_memory_headroom_bytes": 4096,
    }

    payload = regex_runtime._run_stdlib_subprocess_worker(
        request,
        timeout=1.0,
        startup_timeout=1.0,
        max_result_bytes=4096,
    )

    assert payload["ok"] is True
    assert len(captured) == 1
    assert b"\\udcff" in captured[0]
    assert json.loads(captured[0].decode("utf-8"))["haystack_file"]["path"] == surrogate_path


def test_child_file_transport_wraps_unexpected_materialization_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import micromax.regex_worker_child as child

    def fail_materialization(request: object) -> object:
        del request
        raise RuntimeError("unexpected read failure")

    monkeypatch.setattr(child, "_materialize_file_haystack", fail_materialization)

    assert child.execute_worker_request({}) == {
        "protocol": PROTOCOL,
        "ok": False,
        "kind": "worker",
        "message": "RuntimeError: unexpected read failure",
    }


def test_child_file_transport_decodes_exact_surrogate_text(tmp_path: Path) -> None:
    source = "left\udcff\nright"
    request = _file_request(tmp_path / "source.utf8", source)

    response = execute_worker_request(request)

    assert response["ok"] is True
    value = response["value"]
    assert isinstance(value, dict)
    # The three-byte surrogatepass sequence remains one source character, so
    # the later ASCII match begins at canonical character offset six.
    assert value["start"] == 6
    assert value["end"] == 11
    assert value["group"] == "right"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("bytes", 999, "regex worker haystack transport size changed"),
        ("characters", 999, "regex worker haystack character count changed"),
        ("bytes", True, "invalid regex worker haystack byte count"),
        ("characters", True, "invalid regex worker haystack character count"),
        ("bytes", 12.0, "invalid regex worker haystack byte count"),
        ("characters", "12", "invalid regex worker haystack character count"),
    ],
)
def test_child_file_transport_rejects_malformed_exactness_witnesses(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    request = _file_request(tmp_path / "source.utf8", "left\udcff\nright")
    descriptor = request["haystack_file"]
    assert isinstance(descriptor, dict)
    descriptor[field] = value

    response = execute_worker_request(request)

    assert response == {
        "protocol": PROTOCOL,
        "ok": False,
        "kind": "protocol",
        "message": message,
    }


def test_child_file_transport_rejects_multiple_source_owners(tmp_path: Path) -> None:
    request = _file_request(tmp_path / "source.utf8", "left\udcff\nright")
    request["haystack"] = "different"

    response = execute_worker_request(request)

    assert response == {
        "protocol": PROTOCOL,
        "ok": False,
        "kind": "protocol",
        "message": "regex worker request has multiple haystack transports",
    }


@pytest.mark.skipif(
    not hasattr(os, "O_NOFOLLOW"),
    reason="the child can reject symlink opening where O_NOFOLLOW is available",
)
def test_child_file_transport_does_not_follow_symlink(tmp_path: Path) -> None:
    source = "left\udcff\nright"
    target = tmp_path / "target.utf8"
    request = _file_request(target, source)
    link = tmp_path / "link.utf8"
    link.symlink_to(target)
    descriptor = request["haystack_file"]
    assert isinstance(descriptor, dict)
    descriptor["path"] = str(link)

    response = execute_worker_request(request)

    assert response == {
        "protocol": PROTOCOL,
        "ok": False,
        "kind": "protocol",
        "message": "regex worker haystack transport could not be read",
    }


@pytest.mark.parametrize(
    ("text", "search", "value", "start", "replace_all", "case_sensitive"),
    [
        (
            "prefix-ABCDEFGHIJ\nKLMNOPQRST-suffix",
            r"(GHIJ\nKLMN)(OP)",
            r"<$1:$2>",
            0,
            True,
            True,
        ),
        ("AİB\nfoo B\nend", r"b\nfoo", "X", 0, True, False),
        ("aa\nbb\ncc\nbb\ncc", r"bb\n(c+)", r"z-$1", 4, False, True),
        ("zero\nneedle-42\ntail", r"(?m)^needle-([0-9]+)$", r"v-$1", 0, True, True),
    ],
)
def test_line_vector_regex_scan_matches_flat_oracle_across_tiny_chunks(
    text: str,
    search: str,
    value: str,
    start: int,
    replace_all: bool,
    case_sensitive: bool,
) -> None:
    expected = scan_replacement_edits(
        text,
        search,
        value,
        start_index=start,
        replace_all=replace_all,
        literal=False,
        case_sensitive=case_sensitive,
        timeout_seconds=1.0,
    )
    snapshot = QueryReplaceSourceSnapshot.capture(tuple(text.split("\n")))

    for chunk_chars in (1, 2, 7):
        actual = scan_regex_replacement_edits_lines(
            snapshot.lines,
            search,
            value,
            start_index=start,
            replace_all=replace_all,
            case_sensitive=case_sensitive,
            timeout_seconds=1.0,
            chunk_chars=chunk_chars,
            line_starts=snapshot.line_starts,
        )
        assert _scan_signature(actual) == _scan_signature(expected)


@pytest.mark.parametrize("expected", [True, 3.0, "3", -1])
def test_chunk_transport_rejects_non_exact_expected_length_before_consuming_source(
    expected: object,
) -> None:
    consumed = False

    def chunks() -> Iterator[str]:
        nonlocal consumed
        consumed = True
        yield "abc"

    with pytest.raises(
        RegexWorkerProtocolError,
        match="invalid regex worker expected haystack length",
    ):
        run_regex_worker_from_chunks(
            action="re.search",
            haystack_chunks=chunks(),
            expected_haystack_chars=expected,  # type: ignore[arg-type]
            pattern="a",
            timeout_seconds=1.0,
        )
    assert consumed is False


def test_chunk_transport_rejects_changed_parent_character_count_before_spawn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def forbidden(*args: object, **kwargs: object) -> dict[str, object]:
        del args, kwargs
        nonlocal called
        called = True
        raise AssertionError("worker started after source length mismatch")

    monkeypatch.setattr(
        regex_runtime,
        "_run_stdlib_subprocess_worker",
        forbidden,
    )

    with pytest.raises(
        RegexWorkerProtocolError,
        match="haystack length changed while staging",
    ):
        run_regex_worker_from_chunks(
            action="re.search",
            haystack_chunks=("abc",),
            expected_haystack_chars=4,
            pattern="a",
            timeout_seconds=1.0,
        )
    assert called is False


def test_regex_transport_measurement_runs_real_reference_and_product() -> None:
    module = _load_measurement_tool()
    report = module.build_report(chars=250_000, line_chars=256, samples=1)

    assert report["schema"] == "micromax.qreplace-regex-transport-measurement.v1"
    reference = report["rev0998_joined_json_reference"]
    product = report["file_backed_chunk_transport_product"]
    comparison = report["comparison"]
    assert comparison["plans_exactly_equal"] is True
    assert comparison["match_views_exactly_equal"] is True
    assert comparison["reference_request_contains_complete_haystack"] is True
    assert comparison["product_request_contains_complete_haystack"] is False
    assert comparison["product_request_uses_file_backed_transport"] is True
    assert comparison["product_staged_exact_document_chars"] is True
    assert comparison["product_cleanup_residue_empty"] is True
    assert product["protocol_request_bytes_median"] < reference[
        "protocol_request_bytes_median"
    ]
