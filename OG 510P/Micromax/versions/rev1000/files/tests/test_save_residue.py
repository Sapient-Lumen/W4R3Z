from __future__ import annotations

import errno
import os
import time
from pathlib import Path

import pytest

import micromax_editor.save_residue as residue_module
from micromax_editor.save_residue import (
    ProcessIdentity,
    TempOwnerState,
    build_private_temp_name,
    current_process_identity,
    parse_private_temp_name,
    private_temp_lease,
    temp_owner_state,
)

PID_NAMESPACE = "fedcba9876543210"


def test_private_temp_name_round_trips_transaction_and_process_identity(
    tmp_path: Path,
) -> None:
    owner = ProcessIdentity("0123456789abcdef", 4321, 987654, PID_NAMESPACE)
    lease = "a" * 32

    name = build_private_temp_name(
        tmp_path,
        "document.txt",
        lease_id=lease,
        owner=owner,
        random_token="b" * 16,
    )
    parsed = parse_private_temp_name(name)

    assert parsed is not None
    assert parsed.name == name
    assert parsed.safe_basename == "document.txt"
    assert parsed.owner == owner
    assert parsed.lease_id == lease
    assert parsed.random_token == "b" * 16


def test_private_temp_lease_binds_multiple_names_to_one_transaction(
    tmp_path: Path,
) -> None:
    lease = "c" * 32
    owner = ProcessIdentity("0123456789abcdef", 4321, 987654, PID_NAMESPACE)

    with private_temp_lease(lease):
        first = parse_private_temp_name(
            build_private_temp_name(
                tmp_path,
                "one.txt",
                owner=owner,
                random_token="1" * 16,
            )
        )
        second = parse_private_temp_name(
            build_private_temp_name(
                tmp_path,
                "two.txt",
                owner=owner,
                random_token="2" * 16,
            )
        )

    assert first is not None and second is not None
    assert first.lease_id == lease
    assert second.lease_id == lease


def test_long_and_control_character_basename_is_bounded_and_parseable(
    tmp_path: Path,
) -> None:
    basename = ("é" * 400) + "\nsecret\t.txt"
    name = build_private_temp_name(
        tmp_path,
        basename,
        lease_id="d" * 32,
        owner=ProcessIdentity(
            "0123456789abcdef", 4321, 987654, PID_NAMESPACE
        ),
        random_token="3" * 16,
    )

    assert len(os.fsencode(name)) <= os.pathconf(str(tmp_path), "PC_NAME_MAX")
    parsed = parse_private_temp_name(name)
    assert parsed is not None
    assert "\n" not in parsed.safe_basename
    assert "\t" not in parsed.safe_basename
    assert "~" in parsed.safe_basename



def test_private_temp_display_name_neutralizes_unicode_format_and_line_controls(
    tmp_path: Path,
) -> None:
    # U+202E is RIGHT-TO-LEFT OVERRIDE, U+2066 is LEFT-TO-RIGHT ISOLATE, and
    # U+2028 is LINE SEPARATOR.  None may influence the cleanup inventory.
    name = build_private_temp_name(
        tmp_path,
        "report\u202egpj.exe\u2066\u2028next.txt",
        lease_id="9" * 32,
        owner=ProcessIdentity(
            "0123456789abcdef", 4321, 987654, PID_NAMESPACE
        ),
        random_token="5" * 16,
    )
    parsed = parse_private_temp_name(name)

    assert parsed is not None
    assert "\u202e" not in parsed.safe_basename
    assert "\u2066" not in parsed.safe_basename
    assert "\u2028" not in parsed.safe_basename
    assert parsed.safe_basename == "report_gpj.exe__next.txt"


def test_too_small_name_limit_is_rejected_instead_of_generating_invalid_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(residue_module, "_name_max", lambda _parent: 32)

    with pytest.raises(OSError) as raised:
        build_private_temp_name(
            tmp_path,
            "x",
            lease_id="e" * 32,
            owner=ProcessIdentity(
                "0123456789abcdef", 4321, 987654, PID_NAMESPACE
            ),
            random_token="4" * 16,
        )

    assert raised.value.errno == errno.ENAMETOOLONG


def test_private_temp_identity_rejects_nonpositive_pid_and_malformed_tokens(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        build_private_temp_name(
            tmp_path,
            "document.txt",
            lease_id="a" * 32,
            owner=ProcessIdentity(
                "0123456789abcdef", 0, 987654, PID_NAMESPACE
            ),
            random_token="b" * 16,
        )

    assert (
        ProcessIdentity("zzzzzzzzzzzzzzzz", 4321, 987654, PID_NAMESPACE).reliable
        is False
    )
    assert (
        ProcessIdentity("0123456789abcdef", 4321, 987654, "g" * 16).reliable
        is False
    )


def test_temp_owner_state_requires_exact_boot_pid_and_start_tick(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identity = ProcessIdentity(
        "0123456789abcdef", 4321, 987654, PID_NAMESPACE
    )
    monkeypatch.setattr(residue_module, "_boot_token", lambda: identity.boot_token)
    monkeypatch.setattr(
        residue_module,
        "_pid_namespace_token",
        lambda _pid: identity.pid_namespace_token,
    )
    monkeypatch.setattr(
        residue_module,
        "_process_start_ticks",
        lambda pid: identity.start_ticks if pid == identity.pid else 1,
    )

    assert temp_owner_state(identity) is TempOwnerState.ACTIVE

    monkeypatch.setattr(
        residue_module,
        "_process_start_ticks",
        lambda _pid: identity.start_ticks + 1,
    )
    assert temp_owner_state(identity) is TempOwnerState.STALE

    monkeypatch.setattr(residue_module, "_boot_token", lambda: "f" * 16)
    assert temp_owner_state(identity) is TempOwnerState.STALE


def test_cross_pid_namespace_owner_is_unknown_even_when_other_fields_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identity = ProcessIdentity(
        "0123456789abcdef", 4321, 987654, PID_NAMESPACE
    )
    monkeypatch.setattr(residue_module, "_boot_token", lambda: identity.boot_token)
    monkeypatch.setattr(
        residue_module,
        "_pid_namespace_token",
        lambda _pid: "1111111111111111",
    )
    monkeypatch.setattr(
        residue_module,
        "_process_start_ticks",
        lambda _pid: identity.start_ticks,
    )

    assert temp_owner_state(identity) is TempOwnerState.UNKNOWN


def test_missing_creator_is_stale_but_unavailable_evidence_is_unknown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identity = ProcessIdentity(
        "0123456789abcdef", 4321, 987654, PID_NAMESPACE
    )
    monkeypatch.setattr(residue_module, "_boot_token", lambda: identity.boot_token)
    monkeypatch.setattr(
        residue_module,
        "_pid_namespace_token",
        lambda _pid: identity.pid_namespace_token,
    )

    def missing(_pid: int) -> int:
        raise FileNotFoundError

    monkeypatch.setattr(residue_module, "_process_start_ticks", missing)
    assert temp_owner_state(identity) is TempOwnerState.STALE

    def denied(_pid: int) -> int:
        raise PermissionError

    monkeypatch.setattr(residue_module, "_process_start_ticks", denied)
    assert temp_owner_state(identity) is TempOwnerState.UNKNOWN
    assert (
        temp_owner_state(ProcessIdentity("x", os.getpid(), 0))
        is TempOwnerState.UNKNOWN
    )


def test_v2_temp_parses_but_cannot_be_cleanup_proof() -> None:
    name = (
        ".document.txt.micromax-v2-b0123456789abcdef-p4321-s987654-"
        f"l{'a' * 32}-r{'b' * 16}.tmp"
    )

    parsed = parse_private_temp_name(name)

    assert parsed is not None
    assert parsed.owner.pid_namespace_token == "x"
    assert parsed.owner.reliable is False
    assert temp_owner_state(parsed.owner) is TempOwnerState.UNKNOWN


@pytest.mark.skipif(not Path("/proc/self/stat").exists(), reason="Linux proc identity")
def test_current_process_identity_classifies_as_active() -> None:
    identity = current_process_identity()
    assert identity.reliable is True
    assert temp_owner_state(identity) is TempOwnerState.ACTIVE


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative worker cleanup")
def test_timeout_cleanup_requires_matching_worker_pid_and_save_lease(
    tmp_path: Path,
) -> None:
    from micromax_editor import file_write

    owner = ProcessIdentity("0123456789abcdef", 54321, 123456, PID_NAMESPACE)
    matching = tmp_path / build_private_temp_name(
        tmp_path,
        "document.txt",
        lease_id="1" * 32,
        owner=owner,
        random_token="6" * 16,
    )
    other_lease = tmp_path / build_private_temp_name(
        tmp_path,
        "document.txt",
        lease_id="2" * 32,
        owner=owner,
        random_token="7" * 16,
    )
    matching.write_bytes(b"matching")
    other_lease.write_bytes(b"other")
    legacy = tmp_path / f".document.txt.micromax-{owner.pid}-deadbeefdeadbeef.tmp"
    legacy.write_bytes(b"legacy")

    file_write._cleanup_micromax_temps_in_parent(
        tmp_path,
        owner.pid,
        lease_id="1" * 32,
        containment_root=None,
    )

    assert not matching.exists()
    assert other_lease.read_bytes() == b"other"
    assert legacy.read_bytes() == b"legacy"


@pytest.mark.skipif(os.name != "posix", reason="descriptor-relative worker cleanup")
def test_timeout_cleanup_without_exact_save_lease_is_a_noop(tmp_path: Path) -> None:
    from micromax_editor import file_write

    owner = ProcessIdentity("0123456789abcdef", 54321, 123456, PID_NAMESPACE)
    private_temp = tmp_path / build_private_temp_name(
        tmp_path,
        "document.txt",
        lease_id="3" * 32,
        owner=owner,
        random_token="8" * 16,
    )
    private_temp.write_bytes(b"keep")

    file_write._cleanup_micromax_temps_in_parent(
        tmp_path,
        owner.pid,
        lease_id=None,
        containment_root=None,
    )

    assert private_temp.read_bytes() == b"keep"


def test_worker_cleanup_scans_a_shared_parent_only_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from micromax_editor import file_write

    target = tmp_path / "nominal.txt"
    concrete = tmp_path / "concrete.txt"
    calls: list[Path] = []
    monkeypatch.setattr(
        file_write,
        "resolve_file_write_target",
        lambda _path: file_write.ResolvedFileWriteTarget(
            requested_path=target,
            write_path=concrete,
            followed_symlink=True,
        ),
    )

    def observe(
        parent: Path,
        worker_pid: int,
        *,
        lease_id: str | None,
        containment_root: str | Path | None,
    ) -> None:
        assert worker_pid == 4321
        assert lease_id == "c" * 32
        assert containment_root is None
        calls.append(parent)

    monkeypatch.setattr(file_write, "_cleanup_micromax_temps_in_parent", observe)

    file_write._cleanup_atomic_write_temps_for_worker(
        target,
        4321,
        lease_id="c" * 32,
        containment_root=None,
    )

    assert calls == [tmp_path]



def test_timeout_residue_cleanup_has_its_own_killable_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from micromax_editor import file_write

    observed: dict[str, object] = {}

    def fake_create(*_args: object, **kwargs: object) -> tuple[object, object]:
        observed["target"] = kwargs.get("target")
        return object(), object()

    def fake_collect(_proc: object, _channel: object, **kwargs: object) -> object:
        observed["timeout"] = kwargs.get("timeout_seconds")
        timeout_error = kwargs.get("timeout_error")
        assert callable(timeout_error)
        raise timeout_error()

    monkeypatch.setattr(file_write, "create_one_shot_worker", fake_create)
    monkeypatch.setattr(file_write, "_collect_write_worker_result", fake_collect)

    started = time.monotonic()
    file_write._cleanup_atomic_write_temps_bounded(
        tmp_path / "document.txt",
        4321,
        lease_id="d" * 32,
        containment_root=None,
        timeout_seconds=0.05,
    )

    assert time.monotonic() - started < 1.0
    assert observed == {
        "target": file_write._cleanup_atomic_write_temps_worker,
        "timeout": 0.05,
    }

