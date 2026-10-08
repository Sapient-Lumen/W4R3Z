#!/usr/bin/env python3
"""
sandworm_py.py — Python utilities for sandworm diagnostics and state management.

This is a gradual rewrite path: we add Python modules where they buy leverage
(testability, structured output, safety) without breaking the bash reference.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _read_proc_status() -> dict[str, str]:
    status_path = Path("/proc/self/status")
    if not status_path.exists():
        return {}
    out: dict[str, str] = {}
    for line in status_path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip()
    return out


def _netcheck_af_inet() -> tuple[bool, str | None]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.close()
        return True, None
    except Exception as e:
        return False, repr(e)


def _collect_env(prefixes: tuple[str, ...]) -> dict[str, str]:
    collected: dict[str, str] = {}
    for key, value in os.environ.items():
        if key.startswith(prefixes):
            collected[key] = value
    return dict(sorted(collected.items()))


def doctor_payload() -> dict[str, Any]:
    proc = _read_proc_status()
    af_inet_ok, af_inet_err = _netcheck_af_inet()
    env = _collect_env(("SANDWORM_", "SW_", "CODEX_"))
    return {
        "cwd": os.getcwd(),
        "env": env,
        "proc_status": {
            "NoNewPrivs": proc.get("NoNewPrivs"),
            "Seccomp": proc.get("Seccomp"),
            "Seccomp_filters": proc.get("Seccomp_filters"),
        },
        "network": {
            "af_inet_socket_ok": af_inet_ok,
            "af_inet_socket_error": af_inet_err,
        },
        "hints": _hints(env=env, proc=proc, af_inet_ok=af_inet_ok),
    }


def _hints(*, env: dict[str, str], proc: dict[str, str], af_inet_ok: bool) -> list[str]:
    hints: list[str] = []
    if not af_inet_ok:
        if env.get("CODEX_SANDBOX_NETWORK_DISABLED") == "1":
            hints.append(
                "Codex tool sandbox networking appears disabled (CODEX_SANDBOX_NETWORK_DISABLED=1); run outside the sandbox when web access is required."
            )
        if proc.get("Seccomp") == "2":
            hints.append("Seccomp is active (Seccomp: 2); a seccomp profile may be blocking AF_INET sockets.")
    if env.get("SANDWORM_CONTEXT"):
        hints.append(f"Detected sandworm context: {env['SANDWORM_CONTEXT']}")
    return hints


def _print_human(payload: dict[str, Any]) -> None:
    print("sandworm-py doctor")
    print(f"- cwd: {payload.get('cwd')}")
    ps = payload.get("proc_status") or {}
    print(f"- NoNewPrivs: {ps.get('NoNewPrivs')}")
    print(f"- Seccomp: {ps.get('Seccomp')}")
    print(f"- Seccomp_filters: {ps.get('Seccomp_filters')}")
    net = payload.get("network") or {}
    print(f"- AF_INET socket: {'ok' if net.get('af_inet_socket_ok') else 'blocked'}")
    if net.get("af_inet_socket_error"):
        print(f"  - error: {net['af_inet_socket_error']}")
    hints = payload.get("hints") or []
    if hints:
        print("- hints:")
        for hint in hints:
            print(f"  - {hint}")


# =============================================================================
# State Management (state.json)
# =============================================================================

# Known state keys and their validation patterns (mirrors bash _validate_state_kv)
STATE_VALIDATORS: dict[str, re.Pattern[str]] = {
    "SW_STATE_SCHEMA": re.compile(r"^[0-9]+$"),
    "SW_STATE": re.compile(r"^(UNINITIALIZED|NEEDS_BUILD|BUILDING|HEALTHY|DEGRADED|BROKEN)$"),
    "SW_SCRIPT_HASH": re.compile(r"^[a-f0-9]{64}$"),
    "SW_SCRIPT_DRIFT": re.compile(r"^[01]$"),
    "SW_LAST_REFRESH_UTC": re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$|^never$"),
    "SW_REV_CURRENT": re.compile(r"^[0-9]{8}-[0-9]{6}-[a-f0-9]{4}$"),
    "SW_ROOTFS_TAG": re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*(/[A-Za-z0-9][A-Za-z0-9._-]*)*:[A-Za-z0-9][A-Za-z0-9._-]*$"),
    "SW_SEED_TAG": re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*(/[A-Za-z0-9][A-Za-z0-9._-]*)*:[A-Za-z0-9][A-Za-z0-9._-]*$"),
    "SW_NODE_OK": re.compile(r"^[01]$"),
    "SW_RUST_OK": re.compile(r"^[01]$"),
    "SW_NIX_OK": re.compile(r"^[01]$"),
    "SW_CODEX_OK": re.compile(r"^[01]$"),
    "SW_CLAUDE_OK": re.compile(r"^[01]$"),
    "SW_GEMINI_OK": re.compile(r"^[01]$"),
}

# Default validator for unknown keys: boring chars, no path separators
_DEFAULT_VALUE_PATTERN = re.compile(r"^[A-Za-z0-9._,:@+= -]{0,200}$")

# Key must be uppercase alphanumeric with underscores
_KEY_PATTERN = re.compile(r"^[A-Z0-9_]+$")

# Disallow shell metacharacters that could enable injection
_UNSAFE_VALUE_PATTERN = re.compile(r"[`$(){};|]")

# Control characters (disallowed in any value)
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x1f\x7f]")


@dataclass
class StateValidationError:
    """A single validation error."""
    key: str
    value: str
    reason: str


@dataclass
class StateParseResult:
    """Result of parsing state.json."""
    state: dict[str, str] = field(default_factory=dict)
    errors: list[StateValidationError] = field(default_factory=list)
    file_path: Path | None = None

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def validate_state_key(key: str) -> str | None:
    """Validate a state key. Returns error message or None if valid."""
    if not _KEY_PATTERN.match(key):
        return f"invalid key format (must be uppercase alphanumeric with underscores)"
    return None


def validate_state_value(key: str, value: str) -> str | None:
    """Validate a state value. Returns error message or None if valid."""
    # Check for control characters
    if _CONTROL_CHAR_PATTERN.search(value):
        return "contains control characters"

    # Check for shell metacharacters
    if _UNSAFE_VALUE_PATTERN.search(value):
        return "contains unsafe shell metacharacters"

    # Use specific validator if known, otherwise default
    pattern = STATE_VALIDATORS.get(key, _DEFAULT_VALUE_PATTERN)
    if not pattern.match(value):
        return f"value does not match expected pattern for {key}"

    return None


def parse_state(state_file: Path) -> StateParseResult:
    """
    Parse and validate state.json.

    Returns StateParseResult with validated state dict and any validation errors.
    Invalid keys/values are rejected but parsing continues.
    """
    result = StateParseResult(file_path=state_file)

    if not state_file.exists():
        return result

    try:
        content = state_file.read_text(encoding="utf-8")
        obj = json.loads(content)
    except json.JSONDecodeError as e:
        result.errors.append(StateValidationError(
            key="<file>", value="", reason=f"invalid JSON: {e}"
        ))
        return result

    if not isinstance(obj, dict):
        result.errors.append(StateValidationError(
            key="<file>", value="", reason="JSON root must be an object"
        ))
        return result

    for key, value in obj.items():
        # Convert value to string (matching bash behavior)
        if isinstance(value, (dict, list)):
            str_value = json.dumps(value, separators=(",", ":"))
        elif value is None:
            str_value = ""
        else:
            str_value = str(value)

        # Validate key
        key_error = validate_state_key(key)
        if key_error:
            result.errors.append(StateValidationError(key=key, value=str_value, reason=key_error))
            continue

        # Validate value
        value_error = validate_state_value(key, str_value)
        if value_error:
            result.errors.append(StateValidationError(key=key, value=str_value, reason=value_error))
            continue

        result.state[key] = str_value

    return result


def write_state(state_file: Path, state: dict[str, str], schema_version: int = 1) -> None:
    """
    Atomically write state.json.

    Ensures SW_STATE_SCHEMA is always present.
    Uses atomic write (write to temp, then rename) for safety.
    """
    # Ensure schema version is present
    output = {"SW_STATE_SCHEMA": schema_version}
    for key in sorted(state.keys()):
        if key != "SW_STATE_SCHEMA":
            output[key] = state[key]

    json_content = json.dumps(output, indent=2, sort_keys=True) + "\n"

    # Atomic write: write to temp file in same directory, then rename
    state_file.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        dir=state_file.parent,
        prefix=".state.",
        suffix=".tmp"
    )
    try:
        os.write(fd, json_content.encode("utf-8"))
        os.close(fd)
        os.rename(temp_path, state_file)
    except Exception:
        os.close(fd) if fd else None
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def find_control_dir(start: Path | None = None) -> Path | None:
    """
    Find the .sandworm control directory by walking up from start (or cwd).

    Returns the path to .sandworm/ or None if not found.
    """
    current = start or Path.cwd()
    for parent in [current] + list(current.parents):
        candidate = parent / ".sandworm"
        if candidate.is_dir():
            return candidate
    return None


def state_payload(control_dir: Path | None = None) -> dict[str, Any]:
    """Build payload for state show/validate commands."""
    if control_dir is None:
        control_dir = find_control_dir()

    if control_dir is None:
        return {
            "found": False,
            "control_dir": None,
            "state": {},
            "errors": [],
        }

    state_file = control_dir / "state.json"
    result = parse_state(state_file)

    return {
        "found": True,
        "control_dir": str(control_dir),
        "state_file": str(state_file),
        "state": result.state,
        "errors": [
            {"key": e.key, "value": e.value, "reason": e.reason}
            for e in result.errors
        ],
        "valid": result.ok,
    }


def _print_state_human(payload: dict[str, Any]) -> None:
    """Print state in human-readable format."""
    if not payload.get("found"):
        print("No .sandworm/ directory found")
        return

    print(f"Control directory: {payload['control_dir']}")
    print(f"State file: {payload['state_file']}")
    print()

    state = payload.get("state", {})
    if state:
        print("State:")
        for key in sorted(state.keys()):
            print(f"  {key}: {state[key]}")
    else:
        print("State: (empty)")

    errors = payload.get("errors", [])
    if errors:
        print()
        print("Validation errors:")
        for err in errors:
            print(f"  {err['key']}: {err['reason']}")
            if err.get("value"):
                print(f"    value: {err['value'][:50]}...")

    print()
    print(f"Valid: {'yes' if payload.get('valid', False) else 'no'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Python utilities for sandworm diagnostics and state management."
    )
    parser.set_defaults(command="doctor")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human text.")

    subparsers = parser.add_subparsers(dest="command")

    # Doctor command (diagnostics)
    subparsers.add_parser("doctor", help="Print environment + sandbox diagnostics.")

    # Netcheck command
    subparsers.add_parser("netcheck", help="Exit 0 if AF_INET sockets work, else 1.")

    # State command with subcommands
    state_parser = subparsers.add_parser("state", help="Manage state.json.")
    state_parser.add_argument("--json", action="store_true", help="Emit JSON instead of human text.")
    state_subparsers = state_parser.add_subparsers(dest="state_command")
    state_subparsers.add_parser("show", help="Show current state.")
    state_subparsers.add_parser("validate", help="Validate state.json (exit 0 if valid).")
    state_get = state_subparsers.add_parser("get", help="Get a single state value.")
    state_get.add_argument("key", help="State key to retrieve.")

    args = parser.parse_args(argv)

    # Handle netcheck
    if args.command == "netcheck":
        ok, _ = _netcheck_af_inet()
        return 0 if ok else 1

    # Handle state commands
    if args.command == "state":
        state_cmd = getattr(args, "state_command", None) or "show"

        if state_cmd == "get":
            control = find_control_dir()
            if control is None:
                print("No .sandworm/ directory found", file=sys.stderr)
                return 1
            result = parse_state(control / "state.json")
            key = args.key
            if key in result.state:
                print(result.state[key])
                return 0
            else:
                return 1

        # show or validate
        payload = state_payload()

        if state_cmd == "validate":
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            if not payload.get("found"):
                return 1
            return 0 if payload.get("valid", False) else 1

        # show (default)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_state_human(payload)
        return 0

    # Default: doctor
    payload = doctor_payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_human(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
