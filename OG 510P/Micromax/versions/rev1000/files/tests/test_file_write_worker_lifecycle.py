from __future__ import annotations

import pytest

from micromax import worker_process
from micromax_editor import file_write
from micromax_editor.file_write import _collect_write_worker_result


def test_file_write_collector_uses_shared_framed_owner_and_clean_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    proc = object()
    channel = object()
    cleanup = object()
    seen: dict[str, object] = {}

    def fake_collect(process, result_channel, **kwargs):  # type: ignore[no-untyped-def]
        seen.update(
            process=process,
            channel=result_channel,
            **kwargs,
        )
        return ("ok", "witness")

    monkeypatch.setattr(file_write, "collect_worker_result", fake_collect)

    result = _collect_write_worker_result(  # type: ignore[arg-type]
        proc,
        channel,
        timeout_seconds=1.25,
        operation="test write",
        timeout_error=lambda: TimeoutError("mapped timeout"),
        abnormal_cleanup=cleanup,  # type: ignore[arg-type]
    )

    assert result == ("ok", "witness")
    assert seen == {
        "process": proc,
        "channel": channel,
        "timeout_seconds": 1.25,
        "operation": "test write",
        "require_clean_exit": True,
        "abnormal_cleanup": cleanup,
    }


def test_file_write_collector_maps_only_shared_timeout_taxonomy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def timeout(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise worker_process.WorkerResultTimeoutError("framed timeout")

    monkeypatch.setattr(file_write, "collect_worker_result", timeout)

    with pytest.raises(TimeoutError, match="mapped timeout") as raised:
        _collect_write_worker_result(  # type: ignore[arg-type]
            object(),
            object(),
            timeout_seconds=1.0,
            operation="test write",
            timeout_error=lambda: TimeoutError("mapped timeout"),
        )

    assert isinstance(raised.value.__cause__, worker_process.WorkerResultTimeoutError)


def test_file_write_collector_preserves_protocol_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = worker_process.WorkerResultProtocolError("incomplete result frame")

    def broken(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise failure

    monkeypatch.setattr(file_write, "collect_worker_result", broken)

    with pytest.raises(worker_process.WorkerResultProtocolError) as raised:
        _collect_write_worker_result(  # type: ignore[arg-type]
            object(),
            object(),
            timeout_seconds=1.0,
            operation="test write",
            timeout_error=lambda: TimeoutError("mapped timeout"),
        )

    assert raised.value is failure


def test_public_atomic_writer_replaces_infinite_deadline(monkeypatch) -> None:
    seen: list[float] = []

    def fake_bounded(_path: object, _payload: bytes, **kwargs: object):
        seen.append(float(kwargs["timeout_seconds"]))
        return file_write.FileWriteResult(
            path="target.txt",
            write_path="target.txt",
            atomic=True,
            preserve_mode=True,
            fsync=False,
        )

    monkeypatch.setattr(file_write, "_write_file_bytes_bounded", fake_bounded)

    result = file_write.write_file_bytes(
        "target.txt",
        b"payload",
        atomic=True,
        timeout_seconds=float("inf"),
    )

    assert result.atomic is True
    assert seen == [5.0]
