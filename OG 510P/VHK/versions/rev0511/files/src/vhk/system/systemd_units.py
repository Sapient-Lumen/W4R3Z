from __future__ import annotations

import os
import random
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence


@dataclass
class SystemdUnitSample:
    unit: str
    scope: str
    status: str
    load_state: str | None = None
    active_state: str | None = None
    sub_state: str | None = None
    unit_file_state: str | None = None
    fragment_path: str | None = None
    description: str | None = None
    tool: str | None = None
    error: str | None = None


AttemptCallback = Callable[[int, SystemdUnitSample, bool], None]
_FIELDS = "Id,LoadState,ActiveState,SubState,UnitFileState,FragmentPath,Description"


def _normalized_scope(scope: str) -> str:
    return "user" if str(scope).strip().lower() == "user" else "system"


def _classify_systemctl_error(text: str) -> str:
    lowered = (text or "").strip().lower()
    if not lowered:
        return "probe_failed"
    if "failed to connect to bus" in lowered or "not been booted with systemd" in lowered or "no medium found" in lowered:
        return "manager_unavailable"
    if "could not be found" in lowered or "not loaded" in lowered or "no such file or directory" in lowered:
        return "unit_missing"
    return "probe_failed"


def parse_systemctl_show(stdout: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in (stdout or "").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def get_systemd_unit_state(unit: str, *, scope: str = "system", env: Mapping[str, str | None] | None = None) -> SystemdUnitSample:
    scope_value = _normalized_scope(scope)
    env_map = os.environ if env is None else env
    systemctl = shutil.which("systemctl")
    if not systemctl:
        return SystemdUnitSample(unit=unit, scope=scope_value, status="probe_tool_missing")

    cmd = [systemctl]
    if scope_value == "user":
        cmd.append("--user")
    cmd.extend(["show", unit, f"--property={_FIELDS}", "--no-pager"])
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, env=dict(env_map))
    except Exception as exc:
        return SystemdUnitSample(unit=unit, scope=scope_value, status="probe_failed", tool=systemctl, error=str(exc))

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip() or "systemctl show failed"
        return SystemdUnitSample(unit=unit, scope=scope_value, status=_classify_systemctl_error(err), tool=systemctl, error=err)

    fields = parse_systemctl_show(proc.stdout)
    sample = SystemdUnitSample(
        unit=unit,
        scope=scope_value,
        status="unknown",
        load_state=fields.get("LoadState"),
        active_state=fields.get("ActiveState"),
        sub_state=fields.get("SubState"),
        unit_file_state=fields.get("UnitFileState"),
        fragment_path=fields.get("FragmentPath"),
        description=fields.get("Description"),
        tool=systemctl,
    )

    active_state = str(sample.active_state or "").strip().lower()
    load_state = str(sample.load_state or "").strip().lower()
    if load_state in {"not-found", "bad-setting", "error"}:
        sample.status = "unit_missing" if load_state == "not-found" else "probe_failed"
    elif active_state in {"active", "reloading"}:
        sample.status = "ok"
    elif active_state == "inactive":
        sample.status = "inactive"
    elif active_state == "failed":
        sample.status = "failed"
    elif active_state == "activating":
        sample.status = "activating"
    elif active_state == "deactivating":
        sample.status = "deactivating"
    else:
        sample.status = "loaded" if load_state == "loaded" else "unknown"
    return sample


def _matches_field(value: str | None, expected: str | Sequence[str] | None) -> bool:
    if expected is None:
        return True
    actual = "" if value is None else str(value)
    if isinstance(expected, (list, tuple, set, frozenset)):
        return any(actual == str(item) for item in expected)
    return actual == str(expected)


def matches_systemd_unit_state(
    sample: SystemdUnitSample,
    *,
    status: str | Sequence[str] | None = None,
    load_state: str | Sequence[str] | None = None,
    active_state: str | Sequence[str] | None = None,
    sub_state: str | Sequence[str] | None = None,
    unit_file_state: str | Sequence[str] | None = None,
) -> bool:
    return (
        _matches_field(sample.status, status)
        and _matches_field(sample.load_state, load_state)
        and _matches_field(sample.active_state, active_state)
        and _matches_field(sample.sub_state, sub_state)
        and _matches_field(sample.unit_file_state, unit_file_state)
    )


def wait_for_systemd_unit_state(
    unit: str,
    *,
    scope: str = "system",
    status: str | Sequence[str] | None = None,
    load_state: str | Sequence[str] | None = None,
    active_state: str | Sequence[str] | None = None,
    sub_state: str | Sequence[str] | None = None,
    unit_file_state: str | Sequence[str] | None = None,
    timeout_ms: int = 10_000,
    poll_ms: int = 250,
    max_poll_ms: int = 1_000,
    jitter_ms: int = 30,
    max_attempts: int | None = None,
    env: Mapping[str, str | None] | None = None,
    on_attempt: AttemptCallback | None = None,
) -> SystemdUnitSample:
    deadline = time.time() + (max(1, int(timeout_ms)) / 1000.0)
    attempt = 0
    delay_ms = max(1, int(poll_ms))
    last_sample: SystemdUnitSample | None = None

    while time.time() <= deadline:
        sample = get_systemd_unit_state(unit, scope=scope, env=env)
        last_sample = sample
        attempt += 1
        matched = matches_systemd_unit_state(
            sample,
            status=status,
            load_state=load_state,
            active_state=active_state,
            sub_state=sub_state,
            unit_file_state=unit_file_state,
        )
        if on_attempt is not None:
            on_attempt(attempt, sample, matched)
        if matched:
            return sample
        if max_attempts is not None and attempt >= max_attempts:
            break
        if time.time() >= deadline:
            break
        sleep_ms = delay_ms
        if jitter_ms > 0:
            sleep_ms += random.randint(0, max(0, int(jitter_ms)))
        time.sleep(sleep_ms / 1000.0)
        delay_ms = min(max(1, int(max_poll_ms)), max(1, int(delay_ms * 1.5)))

    detail = "no successful probe"
    if last_sample is not None:
        detail = f"last status={last_sample.status!r} active_state={last_sample.active_state!r} sub_state={last_sample.sub_state!r}"
    raise TimeoutError(f"timed out after {timeout_ms}ms ({detail})")
