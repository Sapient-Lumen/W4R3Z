#!/usr/bin/env python3
"""Run `codex exec` through the shared load balancer and runtime lock."""

from __future__ import annotations

import argparse
import fcntl
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import tempfile
import time
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
OVERSEER_HOME = ROOT
DEFAULT_CODEX_HOME = OVERSEER_HOME / ".codex"
CODEX = OVERSEER_HOME / ".local" / "bin" / "codex"
AUTH_DIR = OVERSEER_HOME / "authcreds"
WORKSPACE = ROOT
LOAD_BALANCER = ROOT / "scripts" / "codex_load_balancer.py"
SESSION_INDEX_BIN = OVERSEER_HOME / ".human" / "scripts" / "overseer-session-index.py"
RUNTIME_LOCK = ROOT / "state" / "codex-load-balancer" / "runtime.lock"
RUNS_ROOT = ROOT / "state" / "codex-load-balancer" / "runs"
CHECKPOINTS_ROOT = ROOT / "state" / "codex-load-balancer" / "checkpoints"
EVIDENCE_ROOT = ROOT / "state" / "codex-load-balancer" / "evidence"
QUOTA_READER = ROOT / "scripts" / "read_codex_usage_quota_best.py"
PROVEN_QUOTA_REFRESH = ROOT / "scripts" / "refresh_proven_quota_truth.py"
PYTHON_BIN = pathlib.Path("/run/current-system/sw/bin/overseer-python3")
if not PYTHON_BIN.exists():
    PYTHON_BIN = pathlib.Path(sys.executable)

OUTPUT_TAIL_MAX_CHARS = 12000
AUTO_HEALABLE_NEAR_SUPPLY_ACTIONS = {
    "claim_playwriter_desktop_lane",
    "attach_playwriter_tab",
    "launch_playwriter_profile",
    "restart_playwriter_profile",
    "install_or_stage_playwriter_extension",
}
RETRY_AFTER_SECONDS_RE = re.compile(r"(?:try again in|retry after)\s+([0-9]+(?:\.[0-9]+)?)s", re.IGNORECASE)
RETRY_AFTER_MILLISECONDS_RE = re.compile(r"retry(?:ing)?(?: [0-9]+/[0-9]+)? in ([0-9]+(?:\.[0-9]+)?)ms", re.IGNORECASE)

FAILURE_PATTERNS: list[dict[str, Any]] = [
    {
        "class": "continuity_invalid",
        "retryable": False,
        "interruption_class": "dependency-block",
        "action": "start_fresh_session_or_rebind_auth_context",
        "patterns": [
            r"invalid_encrypted_content",
            r"organization_id mismatch",
            r"previous response cannot be used for this organization",
            r"zero data retention",
        ],
    },
    {
        "class": "auth_invalid",
        "retryable": False,
        "interruption_class": "dependency-block",
        "action": "refresh_auth_or_switch_profile",
        "patterns": [
            r"\b401\b",
            r"unauthorized",
            r"authentication error",
            r"authenticationerror",
            r"invalid authentication",
            r"incorrect api key",
            r"no auth credentials found",
            r"token exchange (?:failed|error)",
            r"get_chatgpt_account_error",
            r"must be a member of an organization",
            r"login required",
        ],
    },
    {
        "class": "access_denied",
        "retryable": False,
        "interruption_class": "dependency-block",
        "action": "switch_profile_or_repair_provider_access_posture",
        "patterns": [
            r"\b403\b",
            r"forbidden",
            r"access denied",
            r"permissiondeniederror",
            r"country, region, or territory not supported",
            r"unsupported country",
            r"ip not authorized",
            r"not authorized to access",
        ],
    },
    {
        "class": "quota_exhausted",
        "retryable": False,
        "interruption_class": "quota",
        "action": "switch_profile_or_wait_for_reset",
        "patterns": [
            r"hit your usage limit",
            r"usage limit",
            r"exceeded your current quota",
            r"insufficient_quota",
            r"plan and billing details",
            r"upgrade to pro",
            r"upgrade to plus",
        ],
    },
    {
        "class": "rate_limited",
        "retryable": True,
        "interruption_class": "quota",
        "action": "backoff_then_retry_or_switch_profile",
        "patterns": [
            r"rate limit reached",
            r"rate_limit_exceeded",
            r"too many requests",
            r"\b429\b",
            r"tokens per min",
            r"requests per min",
            r"slow down",
        ],
    },
    {
        "class": "content_filtered",
        "retryable": False,
        "interruption_class": "dependency-block",
        "action": "inspect_prompt_or_operator_review",
        "patterns": [
            r"content filter",
            r"rejected by the content filter",
        ],
    },
    {
        "class": "request_invalid",
        "retryable": False,
        "interruption_class": "dependency-block",
        "action": "repair_request_shape_or_provider_configuration",
        "patterns": [
            r"\b400\b",
            r"\b404\b",
            r"\b409\b",
            r"\b422\b",
            r"bad request",
            r"invalid_request_error",
            r"unprocessableentityerror",
            r"resource not found",
            r"conflict",
            r"context length exceeded",
            r"maximum context length",
            r"token limit exceeded",
        ],
    },
    {
        "class": "response_parse_failure",
        "retryable": False,
        "interruption_class": "incident-or-recovery",
        "action": "shorten_or_reframe_request_then_retry_fresh",
        "patterns": [
            r"could not parse response content",
            r"length limit was reached",
            r"failed to parse response",
            r"response_format_error",
        ],
    },
    {
        "class": "transport_failure",
        "retryable": True,
        "interruption_class": "dependency-block",
        "action": "check_network_then_retry",
        "patterns": [
            r"error sending request",
            r"apiconnectionerror",
            r"connection error",
            r"stream error",
            r"stream disconnected",
            r"timed out",
            r"timeout",
            r"econnrefused",
            r"econnreset",
            r"tls",
            r"certificate",
            r"dns",
        ],
    },
    {
        "class": "local_timeout",
        "retryable": True,
        "interruption_class": "incident-or-recovery",
        "action": "retry_with_backoff_or_reduce_turn_scope",
        "patterns": [
            r"request timed out",
            r"timed out waiting",
            r"deadline exceeded",
            r"operation timed out",
            r"failed to start request",
        ],
    },
    {
        "class": "server_overloaded",
        "retryable": True,
        "interruption_class": "incident-or-recovery",
        "action": "retry_with_backoff",
        "patterns": [
            r"\b500\b",
            r"\b502\b",
            r"\b503\b",
            r"\b504\b",
            r"server had an error",
            r"overloaded",
            r"bad gateway",
            r"gateway timeout",
        ],
    },
    {
        "class": "unsupported_request",
        "retryable": False,
        "interruption_class": "dependency-block",
        "action": "adjust_request_or_provider_configuration",
        "patterns": [
            r"unsupported_parameter",
            r"unprocessableentityerror",
            r"invalid_request_error",
            r"not supported",
            r"unsupported input item type",
        ],
    },
    {
        "class": "environment_failure",
        "retryable": False,
        "interruption_class": "dependency-block",
        "action": "repair_local_environment_or_host_dependencies",
        "patterns": [
            r"command not found",
            r"bash not found",
            r"cannot open display",
            r"no such file or directory",
            r"permission denied",
            r"failed to create container",
            r"module not found",
        ],
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer-id", required=True)
    parser.add_argument("--session-id")
    parser.add_argument("--requested-profile")
    parser.add_argument("--mode", default="daemon-exec")
    parser.add_argument("--workspace", default=str(WORKSPACE))
    parser.add_argument("--codex-home", default=str(DEFAULT_CODEX_HOME))
    parser.add_argument("--active-auth-path")
    parser.add_argument("--runtime-lock-root")
    parser.add_argument("--meta-out")
    parser.add_argument("--verify-quota-after", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--wait-seconds", type=int, default=900)
    parser.add_argument("--exec-timeout-seconds", type=int, default=900)
    parser.add_argument("--poll-interval", type=float, default=10.0)
    parser.add_argument("--heartbeat-interval", type=float, default=30.0)
    parser.add_argument(
        "--near-supply-self-heal",
        action=argparse.BooleanOptionalAction,
        default=os.environ.get("CODEX_EXEC_NEAR_SUPPLY_SELF_HEAL_ENABLE", "1") != "0",
    )
    parser.add_argument(
        "--near-supply-self-heal-timeout-seconds",
        type=int,
        default=int(os.environ.get("CODEX_EXEC_NEAR_SUPPLY_SELF_HEAL_TIMEOUT_SECONDS", "35")),
    )
    parser.add_argument("codex_args", nargs=argparse.REMAINDER)
    return parser.parse_args()


def codex_exec_base_args() -> list[str]:
    return [
        "--dangerously-bypass-approvals-and-sandbox",
        "--model",
        "gpt-5.4",
        "-c",
        'model_reasoning_effort="high"',
    ]


def utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def trim_output_tail(text: Any, limit: int = OUTPUT_TAIL_MAX_CHARS) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[-limit:]


def extract_retry_after_seconds(text: str) -> float | None:
    match = RETRY_AFTER_SECONDS_RE.search(text)
    if match:
        return float(match.group(1))
    match = RETRY_AFTER_MILLISECONDS_RE.search(text)
    if match:
        return round(float(match.group(1)) / 1000.0, 3)
    return None


def classify_codex_failure(exit_code: int, stdout_text: str, stderr_text: str) -> dict[str, Any]:
    combined = "\n".join(part for part in [stderr_text.strip(), stdout_text.strip()] if part).strip()
    combined_lower = combined.lower()
    retry_after_seconds = extract_retry_after_seconds(combined)

    for rule in FAILURE_PATTERNS:
        for pattern in rule["patterns"]:
            if re.search(pattern, combined_lower, re.IGNORECASE):
                payload = {
                    "class": rule["class"],
                    "retryable": rule["retryable"],
                    "interruption_class": rule["interruption_class"],
                    "action": rule["action"],
                    "matched_pattern": pattern,
                    "exit_code": exit_code,
                }
                if retry_after_seconds is not None:
                    payload["retry_after_seconds"] = retry_after_seconds
                return payload

    payload = {
        "class": "unknown_failure",
        "retryable": False,
        "interruption_class": "incident-or-recovery",
        "action": "inspect_output_and_receipts",
        "matched_pattern": None,
        "exit_code": exit_code,
    }
    if retry_after_seconds is not None:
        payload["retry_after_seconds"] = retry_after_seconds
    return payload


def run_lb(args: list[str]) -> tuple[int, dict[str, Any]]:
    result = subprocess.run(
        [str(PYTHON_BIN), str(LOAD_BALANCER), *args, "--json-only"],
        check=False,
        text=True,
        capture_output=True,
    )
    if not result.stdout.strip():
        return result.returncode, {"status": "lb_exception", "error": "no JSON", "stderr": result.stderr.strip()}
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return result.returncode, {
            "status": "lb_exception",
            "error": f"invalid JSON: {exc}",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    payload["lb_exit_code"] = result.returncode
    payload["lb_stderr"] = result.stderr.strip()
    return result.returncode, payload


def near_supply_action_is_auto_healable(action: Any) -> bool:
    return isinstance(action, str) and action in AUTO_HEALABLE_NEAR_SUPPLY_ACTIONS


def near_supply_self_heal_candidates(selection: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    if selection.get("status") == "ok":
        profile = selection.get("selected_profile")
        if (
            selection.get("selected_posture") == "near_supply_browser_recovery"
            and isinstance(profile, str)
            and near_supply_action_is_auto_healable(selection.get("recommended_action"))
        ):
            candidates.append(profile)
        return candidates
    if selection.get("status") != "no_profile_available":
        return candidates
    details = selection.get("near_supply_details")
    if not isinstance(details, dict):
        return candidates
    for profile, detail in details.items():
        if not isinstance(profile, str) or not isinstance(detail, dict):
            continue
        if near_supply_action_is_auto_healable(detail.get("action")) and profile not in candidates:
            candidates.append(profile)
    return candidates


def run_near_supply_self_heal(
    profiles: list[str],
    *,
    timeout_seconds: int,
) -> dict[str, Any]:
    try:
        result = subprocess.run(
            [
                str(PYTHON_BIN),
                str(PROVEN_QUOTA_REFRESH),
                "--profiles",
                ",".join(profiles),
                "--json",
            ],
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return {
            "requested_profiles": profiles,
            "status": "timeout",
            "error": f"near-supply self-heal timed out after {timeout_seconds}s",
            "provider_exit_code": 124,
        }

    payload: dict[str, Any]
    if not result.stdout.strip():
        payload = {
            "status": "invalid_json",
            "error": "near-supply self-heal returned no JSON",
            "stderr": result.stderr.strip(),
        }
    else:
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            payload = {
                "status": "invalid_json",
                "error": f"near-supply self-heal returned invalid JSON: {exc}",
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        else:
            if isinstance(parsed, dict):
                payload = parsed
            else:
                payload = {
                    "status": "invalid_payload",
                    "error": "near-supply self-heal payload is not a JSON object",
                    "payload": parsed,
                }
    payload["requested_profiles"] = profiles
    payload["provider_exit_code"] = result.returncode
    payload["provider_stderr"] = result.stderr.strip()
    return payload


def latest_session_id(workspace: pathlib.Path, codex_home: pathlib.Path) -> str | None:
    result = subprocess.run(
        [
            str(SESSION_INDEX_BIN),
            "--sessions-root",
            str(codex_home / "sessions"),
            "--history",
            str(codex_home / "history.jsonl"),
            "--workspace",
            str(workspace),
            "--scope-dir",
            str(workspace),
            "--scope-dir",
            str(OVERSEER_HOME),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not payload:
        return None
    payload.sort(key=lambda item: item.get("last_activity_ts", 0), reverse=True)
    return payload[0].get("session_id")


def switch_profile(profile: str, active_auth_path: pathlib.Path) -> None:
    src = AUTH_DIR / f"{profile}.auth.json"
    if not src.exists():
        raise FileNotFoundError(src)
    active_auth_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, active_auth_path)
    os.chmod(active_auth_path, 0o600)


def write_meta(path: str | None, payload: dict[str, Any]) -> None:
    if not path:
        return
    meta_path = pathlib.Path(path)
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def atomic_write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def slugify(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "unknown"


def atomic_write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        pathlib.Path(tmp_name).replace(path)
    finally:
        tmp_path = pathlib.Path(tmp_name)
        if tmp_path.exists():
            tmp_path.unlink()


def append_jsonl(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def write_run_receipt(consumer_id: str, payload: dict[str, Any]) -> pathlib.Path:
    run_id = payload.get("run_id") or f"run-{int(time.time())}"
    consumer_root = RUNS_ROOT / slugify(consumer_id)
    timestamped = consumer_root / f"{run_id}.json"
    latest = consumer_root / "latest.json"
    atomic_write_json(timestamped, payload)
    atomic_write_json(latest, payload)
    return timestamped


def write_active_run_state(consumer_id: str, payload: dict[str, Any]) -> pathlib.Path:
    consumer_root = RUNS_ROOT / slugify(consumer_id)
    active = consumer_root / "active.json"
    stamped_payload = dict(payload)
    stamped_payload["updated_at"] = utc_now_iso()
    stamped_payload.setdefault("last_heartbeat_at", stamped_payload["updated_at"])
    atomic_write_json(active, stamped_payload)
    return active


def touch_active_run_state(active_path: pathlib.Path | None, **updates: Any) -> None:
    if not active_path or not active_path.exists():
        return
    try:
        payload = json.loads(active_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    payload.update(updates)
    payload["updated_at"] = utc_now_iso()
    atomic_write_json(active_path, payload)


def remove_active_run_state(active_path: pathlib.Path | None) -> None:
    if active_path and active_path.exists():
        active_path.unlink()


def checkpoint_root_for_consumer(consumer_id: str) -> pathlib.Path:
    return CHECKPOINTS_ROOT / slugify(consumer_id)


def evidence_root_for_consumer(consumer_id: str) -> pathlib.Path:
    return EVIDENCE_ROOT / slugify(consumer_id)


def render_checkpoint_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Latest Daemon Checkpoint",
        "",
        f"- written_at: {payload.get('written_at')}",
        f"- consumer_id: {payload.get('consumer_id')}",
        f"- run_id: {payload.get('run_id')}",
        f"- phase: {payload.get('phase')}",
        f"- selected_profile: {payload.get('selected_profile') or '(none)'}",
        f"- next_action: {payload.get('next_action')}",
        f"- context_pressure: {payload.get('context_pressure')}",
        "",
        "## Summary",
        "",
        payload.get("summary", ""),
        "",
    ]
    resume_hint = payload.get("resume_hint")
    if resume_hint:
        lines.extend(["## Resume Hint", "", resume_hint, ""])
    return "\n".join(lines)


def write_semantic_checkpoint(consumer_id: str, payload: dict[str, Any]) -> pathlib.Path:
    checkpoint_payload = {
        "schema_version": 1,
        "written_at": utc_now_iso(),
        **payload,
    }
    consumer_root = checkpoint_root_for_consumer(consumer_id)
    latest = consumer_root / "latest.json"
    latest_md = consumer_root / "latest.md"
    history = consumer_root / "history.jsonl"
    atomic_write_json(latest, checkpoint_payload)
    atomic_write_text(latest_md, render_checkpoint_markdown(checkpoint_payload) + "\n")
    append_jsonl(history, checkpoint_payload)
    return latest


def outcome_class_for_meta(meta: dict[str, Any]) -> str:
    selection = meta.get("selection") or {}
    failure = meta.get("failure_classification") or {}
    if meta.get("runner_exception"):
        return "degraded"
    if selection.get("status") == "deferred":
        return "blocked"
    if failure.get("class") in {
        "quota_exhausted",
        "rate_limited",
        "auth_invalid",
        "continuity_invalid",
        "access_denied",
        "request_invalid",
        "environment_failure",
        "content_filtered",
    }:
        return "blocked"
    if failure:
        return "degraded" if failure.get("retryable") else "failed"
    if selection.get("status") not in {None, "ok"}:
        return "failed"
    if int(meta.get("exit_code", 1)) == 0:
        return "completed"
    return "failed"


def open_uncertainty_for_meta(meta: dict[str, Any]) -> list[str]:
    selection = meta.get("selection") or {}
    failure = meta.get("failure_classification") or {}
    uncertainties: list[str] = []
    continuity = selection.get("continuity_status")
    if continuity == "warm-with-risk":
        uncertainties.append("interactive same-session continuity remains risky across account or auth-context drift")
    quota_verification = meta.get("post_run_quota_verification") or {}
    if quota_verification and quota_verification.get("status") != "ok":
        uncertainties.append(f"post-run quota verification did not return ok ({quota_verification.get('status')})")
    if selection.get("status") == "deferred":
        uncertainties.append("daemon work deferred under current interactive or queue pressure")
    if failure:
        uncertainties.append(
            f"failure classified as {failure.get('class')} with action {failure.get('action')}"
        )
    return uncertainties


def build_evidence_packet(meta: dict[str, Any], checkpoint_path: pathlib.Path) -> dict[str, Any]:
    selection = meta.get("selection") or {}
    outcome_class = outcome_class_for_meta(meta)
    next_open_hint = "inspect latest daemon receipt and checkpoint"
    if outcome_class == "completed":
        next_open_hint = "inspect latest receipt, then schedule or admit the next daemon turn"
    elif outcome_class == "blocked":
        next_open_hint = "inspect queue or interactive pressure, then retry through the load balancer"
    elif meta.get("runner_exception"):
        next_open_hint = "inspect runner exception, checkpoint, and receipt before retry"

    return {
        "schema_version": 1,
        "generated_at": utc_now_iso(),
        "turn_ledger": {
            "turn_id": meta.get("run_id"),
            "session_id": meta.get("completed_session") or meta.get("before_session"),
            "started_at": meta.get("started_at"),
            "ended_at": meta.get("completed_at"),
            "wake_cause": meta.get("mode") or "daemon-exec",
            "continuity_posture": selection.get("continuity_status"),
            "account_or_profile": meta.get("selected_profile"),
            "turn_outcome_class": outcome_class,
            "next_open_hint": next_open_hint,
        },
        "intent": {
            "consumer_id": meta.get("consumer_id"),
            "mode": meta.get("mode"),
            "workspace": meta.get("workspace"),
            "requested_profile": meta.get("requested_profile"),
            "requested_session_id": meta.get("requested_session_id"),
            "execution_mode": meta.get("execution_mode"),
            "execution_mode_reason": meta.get("execution_mode_reason"),
            "resume_demoted_reason": meta.get("resume_demoted_reason"),
            "codex_arg_count": int(meta.get("codex_arg_count", 0)),
        },
        "opening_context": {
            "before_session": meta.get("before_session"),
            "queue": meta.get("queue"),
            "selection_reason": selection.get("selection_reason"),
            "continuity_status": selection.get("continuity_status"),
            "continuity_reason": selection.get("continuity_reason"),
        },
        "selected_profile_record": {
            "profile": meta.get("selected_profile"),
            "selected_account_id": selection.get("selected_account_id"),
            "quota_snapshot": selection.get("quota_snapshot"),
            "continuity_handles": selection.get("continuity_handles"),
        },
        "action_summary": {
            "command_kind": "codex exec resume" if meta.get("execution_mode") == "resume" else "codex exec",
            "duration_ms": meta.get("duration_ms"),
            "verify_quota_after": meta.get("verify_quota_after"),
        },
        "checks_summary": {
            "near_supply_self_heal": meta.get("near_supply_self_heal"),
            "completion": meta.get("completion"),
            "post_run_quota_verification": meta.get("post_run_quota_verification"),
            "post_run_quota_record": meta.get("post_run_quota_record"),
            "failure_classification": meta.get("failure_classification"),
            "runner_exception": meta.get("runner_exception"),
        },
        "state_transition_result": {
            "exit_code": meta.get("exit_code"),
            "completed_session": meta.get("completed_session"),
            "binding": (meta.get("completion") or {}).get("binding"),
        },
        "open_uncertainty": open_uncertainty_for_meta(meta),
        "raw_pointers": {
            "run_receipt": meta.get("run_receipt"),
            "latest_checkpoint": str(checkpoint_path),
            "meta_out": meta.get("meta_out"),
            "codex_stdout_tail": meta.get("codex_stdout_tail"),
            "codex_stderr_tail": meta.get("codex_stderr_tail"),
        },
    }


def render_evidence_markdown(payload: dict[str, Any]) -> str:
    ledger = payload["turn_ledger"]
    lines = [
        "# Latest Daemon Evidence Packet",
        "",
        f"- turn_id: {ledger.get('turn_id')}",
        f"- session_id: {ledger.get('session_id') or '(none)'}",
        f"- continuity_posture: {ledger.get('continuity_posture') or '(none)'}",
        f"- account_or_profile: {ledger.get('account_or_profile') or '(none)'}",
        f"- turn_outcome_class: {ledger.get('turn_outcome_class')}",
        f"- next_open_hint: {ledger.get('next_open_hint')}",
        "",
    ]
    uncertainties = payload.get("open_uncertainty") or []
    if uncertainties:
        lines.extend(["## Open Uncertainty", ""])
        for item in uncertainties:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def write_evidence_packet(consumer_id: str, payload: dict[str, Any]) -> pathlib.Path:
    consumer_root = evidence_root_for_consumer(consumer_id)
    run_id = payload["turn_ledger"].get("turn_id") or f"run-{int(time.time())}"
    latest = consumer_root / "latest.json"
    latest_md = consumer_root / "latest.md"
    timestamped = consumer_root / f"{run_id}.json"
    history = consumer_root / "history.jsonl"
    atomic_write_json(timestamped, payload)
    atomic_write_json(latest, payload)
    atomic_write_text(latest_md, render_evidence_markdown(payload) + "\n")
    append_jsonl(history, payload)
    return timestamped


def verify_quota(profile: str) -> tuple[int, dict[str, Any]]:
    result = subprocess.run(
        [str(PYTHON_BIN), str(QUOTA_READER), "--profile", profile, "--json-only"],
        check=False,
        text=True,
        capture_output=True,
    )
    if not result.stdout.strip():
        return result.returncode, {
            "status": "reader_exception",
            "error": f"no JSON output (rc={result.returncode})",
            "stderr": result.stderr.strip(),
        }
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return result.returncode, {
            "status": "reader_exception",
            "error": f"invalid JSON: {exc}",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    return result.returncode, payload


def heartbeat_loop(
    lease_id: str,
    stop_event: threading.Event,
    interval: float,
    run_handle: str,
    run_id: str,
    process_id: int,
    active_run_path: pathlib.Path,
) -> None:
    while not stop_event.wait(interval):
        heartbeat_at = utc_now_iso()
        touch_active_run_state(
            active_run_path,
            last_heartbeat_at=heartbeat_at,
            state="active",
        )
        run_lb(
            [
                "heartbeat",
                "--lease-id",
                lease_id,
                "--run-handle",
                run_handle,
                "--run-id",
                run_id,
                "--process-id",
                str(process_id),
                "--active-run-path",
                str(active_run_path),
            ]
        )


def acquire_runtime_lock(lock_path: pathlib.Path, wait_seconds: int, poll_interval: float) -> tuple[io.TextIOWrapper | None, int]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("w", encoding="utf-8")
    waited_ms = 0
    deadline = time.monotonic() + max(0, wait_seconds)
    while True:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return handle, waited_ms
        except BlockingIOError:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                handle.close()
                return None, waited_ms
            sleep_for = min(poll_interval, remaining)
            time.sleep(sleep_for)
            waited_ms += int(sleep_for * 1000)


def runtime_lock_path(selected_profile: str, runtime_lock_root_arg: str | None) -> pathlib.Path:
    if runtime_lock_root_arg:
        root = pathlib.Path(runtime_lock_root_arg)
        root.mkdir(parents=True, exist_ok=True)
        return root / f"{selected_profile}.lock"
    return RUNTIME_LOCK


def select_with_wait(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
    select_args = [
        "select",
        "--consumer-kind",
        "daemon",
        "--consumer-id",
        args.consumer_id,
        "--mode",
        args.mode,
    ]
    if args.session_id:
        select_args.extend(["--session-id", args.session_id])
    if args.requested_profile:
        select_args.extend(["--requested-profile", args.requested_profile])

    queue_payload: dict[str, Any] | None = None
    near_supply_self_heal_payload: dict[str, Any] | None = None
    near_supply_self_heal_attempted = False
    deadline = time.monotonic() + max(0, args.wait_seconds)
    process_id = os.getpid()
    while True:
        _, selection = run_lb(select_args)
        if args.near_supply_self_heal and not near_supply_self_heal_attempted:
            profiles = near_supply_self_heal_candidates(selection)
            if profiles:
                near_supply_self_heal_attempted = True
                near_supply_self_heal_payload = run_near_supply_self_heal(
                    profiles,
                    timeout_seconds=args.near_supply_self_heal_timeout_seconds,
                )
                continue
        if selection.get("status") == "ok":
            return selection, queue_payload, near_supply_self_heal_payload
        if selection.get("status") != "deferred":
            return selection, queue_payload, near_supply_self_heal_payload
        _, queue_payload = run_lb(
            [
                "enqueue",
                "--consumer-kind",
                "daemon",
                "--consumer-id",
                args.consumer_id,
                "--mode",
                args.mode,
                "--process-id",
                str(process_id),
                *(["--session-id", args.session_id] if args.session_id else []),
                *(["--requested-profile", args.requested_profile] if args.requested_profile else []),
            ]
        )
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return {
                "status": "deferred",
                "reason": "wait_timeout",
                "last_selection": selection,
                "queue": queue_payload,
            }, queue_payload, near_supply_self_heal_payload
        time.sleep(min(args.poll_interval, remaining))


def main() -> int:
    args = parse_args()
    workspace = pathlib.Path(args.workspace)
    codex_home = pathlib.Path(args.codex_home)
    active_auth_path = pathlib.Path(args.active_auth_path) if args.active_auth_path else (codex_home / "auth.json")
    run_started_monotonic = time.monotonic()
    run_started_at = utc_now_iso()
    run_id = f"{int(time.time())}-{slugify(args.consumer_id)}"
    before_session = latest_session_id(workspace, codex_home) if not args.session_id else args.session_id

    selection, queue_payload, near_supply_self_heal_payload = select_with_wait(args)
    meta: dict[str, Any] = {
        "selection": selection,
        "run_id": run_id,
        "started_at": run_started_at,
        "consumer_id": args.consumer_id,
        "mode": args.mode,
        "workspace": str(workspace),
        "codex_home": str(codex_home),
        "active_auth_path": str(active_auth_path),
        "requested_profile": args.requested_profile,
        "requested_session_id": args.session_id,
        "verify_quota_after": args.verify_quota_after,
        "meta_out": args.meta_out,
    }
    if queue_payload is not None:
        meta["queue"] = queue_payload
    if near_supply_self_heal_payload is not None:
        meta["near_supply_self_heal"] = near_supply_self_heal_payload
    if selection.get("status") != "ok":
        checkpoint_path = write_semantic_checkpoint(
            args.consumer_id,
            {
                "run_id": run_id,
                "consumer_id": args.consumer_id,
                "session_id": args.session_id,
                "lease_id": None,
                "selected_profile": None,
                "phase": "blocked" if selection.get("status") != "deferred" else "waiting_for_capacity",
                "summary": selection.get("reason", selection.get("status", "selection failed")),
                "next_action": "retry through the load balancer when pressure or quota posture changes",
                "resume_hint": "inspect the latest queue and guardian state before retrying unattended work",
                "context_pressure": "unknown",
                "continuity_status": selection.get("continuity_status"),
            },
        )
        meta["latest_checkpoint"] = str(checkpoint_path)
        meta["completed_at"] = utc_now_iso()
        meta["duration_ms"] = int((time.monotonic() - run_started_monotonic) * 1000)
        receipt_path = write_run_receipt(args.consumer_id, meta)
        meta["run_receipt"] = str(receipt_path)
        evidence_path = write_evidence_packet(args.consumer_id, build_evidence_packet(meta, checkpoint_path))
        meta["evidence_packet"] = str(evidence_path)
        write_meta(args.meta_out, meta)
        run_lb(["dequeue", "--consumer-id", args.consumer_id])
        if selection.get("status") == "deferred":
            return 30
        return 31

    selected_profile = selection["selected_profile"]
    switch_profile(selected_profile, active_auth_path)

    codex_args = list(args.codex_args)
    if codex_args and codex_args[0] == "--":
        codex_args = codex_args[1:]

    resume_allowed = bool(args.session_id) and selection.get("continuity_status") != "cold-required"
    if resume_allowed:
        command = [str(CODEX), "exec", "resume", *codex_exec_base_args(), args.session_id]
        execution_mode = "resume"
        execution_mode_reason = "requested_session_continuity_allowed"
    else:
        command = [str(CODEX), "exec", *codex_exec_base_args()]
        execution_mode = "fresh"
        if args.session_id and selection.get("continuity_status") == "cold-required":
            execution_mode_reason = "requested_resume_demoted_by_cold_required"
        elif args.session_id:
            execution_mode_reason = "requested_resume_not_allowed"
        else:
            execution_mode_reason = "no_requested_session"
    if not any(arg in {"-C", "--cd"} for arg in codex_args):
        command.extend(["-C", str(workspace)])
    command.extend(codex_args)

    env = os.environ.copy()
    env["HOME"] = str(codex_home.parent)
    env["PATH"] = f"{OVERSEER_HOME / '.local' / 'bin'}:/run/current-system/sw/bin:/run/wrappers/bin:/usr/bin:/bin"
    env["CODEX_HOME"] = str(codex_home)

    selected_runtime_lock = runtime_lock_path(selected_profile, args.runtime_lock_root)
    selected_runtime_lock.parent.mkdir(parents=True, exist_ok=True)
    meta["runtime_lock_path"] = str(selected_runtime_lock)
    active_payload = {
        "run_id": run_id,
        "consumer_id": args.consumer_id,
        "session_id": args.session_id,
        "selected_profile": selected_profile,
        "selection": selection,
        "started_at": run_started_at,
        "last_heartbeat_at": run_started_at,
        "state": "active",
        "pid": os.getpid(),
    }
    active_run_path = write_active_run_state(args.consumer_id, active_payload)
    checkpoint_path = write_semantic_checkpoint(
        args.consumer_id,
        {
            "run_id": run_id,
            "consumer_id": args.consumer_id,
            "session_id": args.session_id,
            "lease_id": selection["lease_id"],
            "selected_profile": selected_profile,
            "phase": "lease_acquired",
            "summary": f"selected {selected_profile} with {selection.get('continuity_status', 'unknown')} continuity posture",
            "next_action": "switch auth and launch codex exec under the runtime lock",
            "resume_hint": "if the wrapper dies before launch, inspect selection and lease artifacts before retrying",
            "context_pressure": "unknown",
            "continuity_status": selection.get("continuity_status"),
        },
    )
    meta["latest_checkpoint"] = str(checkpoint_path)
    run_lb(
        [
            "heartbeat",
            "--lease-id",
            selection["lease_id"],
            "--run-handle",
            args.consumer_id,
            "--run-id",
            run_id,
            "--process-id",
            str(os.getpid()),
            "--active-run-path",
            str(active_run_path),
        ]
    )
    stop_event = threading.Event()
    heartbeat_thread = threading.Thread(
        target=heartbeat_loop,
        args=(
            selection["lease_id"],
            stop_event,
            args.heartbeat_interval,
            args.consumer_id,
            run_id,
            os.getpid(),
            active_run_path,
        ),
        daemon=True,
    )
    heartbeat_thread.start()
    runner_exception: dict[str, Any] | None = None
    exit_code = 0
    result = None
    runtime_lock_timed_out = False
    try:
        checkpoint_path = write_semantic_checkpoint(
            args.consumer_id,
            {
                "run_id": run_id,
                "consumer_id": args.consumer_id,
                "session_id": args.session_id,
                "lease_id": selection["lease_id"],
                "selected_profile": selected_profile,
                "phase": "exec_running",
                "summary": f"{execution_mode} codex exec is running under the serialized runtime lock",
                "next_action": "allow the run to continue, or inspect active receipt and heartbeat if it stalls",
                "resume_hint": "if the process dies without outcome, reconstruct from this checkpoint and the latest receipt",
                "context_pressure": "unknown",
                "continuity_status": selection.get("continuity_status"),
            },
        )
        meta["latest_checkpoint"] = str(checkpoint_path)
        lock_handle, lock_wait_ms = acquire_runtime_lock(selected_runtime_lock, args.wait_seconds, args.poll_interval)
        meta["runtime_lock_wait_ms"] = lock_wait_ms
        if lock_handle is None:
            runtime_lock_timed_out = True
            exit_code = 30
            meta["runtime_lock_timeout"] = True
            checkpoint_path = write_semantic_checkpoint(
                args.consumer_id,
                {
                    "run_id": run_id,
                    "consumer_id": args.consumer_id,
                    "session_id": args.session_id,
                    "lease_id": selection["lease_id"],
                    "selected_profile": selected_profile,
                    "phase": "waiting_for_capacity",
                    "summary": "serialized codex runtime remained busy until wait timeout",
                    "next_action": "retry when the interactive or other serialized codex work yields the runtime lock",
                    "resume_hint": "inspect active leases, runtime.lock pressure, and the latest daemon receipt before retrying",
                    "context_pressure": "runtime-lock-busy",
                    "continuity_status": selection.get("continuity_status"),
                },
            )
            meta["latest_checkpoint"] = str(checkpoint_path)
        else:
            with lock_handle:
                result = subprocess.run(
                    command,
                    env=env,
                    check=False,
                    text=True,
                    capture_output=True,
                    timeout=max(1, args.exec_timeout_seconds),
                )
            exit_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        result = None
        exit_code = 124
        runner_exception = {
            "type": type(exc).__name__,
            "message": f"codex exec exceeded local timeout after {args.exec_timeout_seconds} seconds",
        }
    except Exception as exc:
        result = None
        exit_code = 70
        runner_exception = {"type": type(exc).__name__, "message": str(exc)}
    stop_event.set()
    heartbeat_thread.join(timeout=max(1.0, args.heartbeat_interval))

    completed_session = args.session_id if resume_allowed else None
    if not completed_session:
        after_session = latest_session_id(workspace, codex_home)
        if after_session and after_session != before_session:
            completed_session = after_session

    _, completion = run_lb(
        [
            "complete",
            "--lease-id",
            selection["lease_id"],
            "--exit-code",
            str(exit_code),
            *(["--session-id", completed_session] if completed_session else []),
        ]
    )
    meta["completion"] = completion
    meta["selected_profile"] = selected_profile
    meta["exit_code"] = exit_code
    meta["command"] = command
    meta["execution_mode"] = execution_mode
    meta["execution_mode_reason"] = execution_mode_reason
    if args.session_id and execution_mode == "fresh":
        meta["resume_demoted_reason"] = selection.get("continuity_reason") or selection.get("continuity_status")
    meta["before_session"] = before_session
    meta["completed_session"] = completed_session
    meta["completed_at"] = utc_now_iso()
    meta["duration_ms"] = int((time.monotonic() - run_started_monotonic) * 1000)
    if runner_exception is not None:
        meta["runner_exception"] = runner_exception
    if result is not None:
        stdout_tail = trim_output_tail(getattr(result, "stdout", ""))
        stderr_tail = trim_output_tail(getattr(result, "stderr", ""))
        if stdout_tail:
            meta["codex_stdout_tail"] = stdout_tail
        if stderr_tail:
            meta["codex_stderr_tail"] = stderr_tail
        if exit_code != 0:
            meta["failure_classification"] = classify_codex_failure(exit_code, stdout_tail, stderr_tail)
    elif runtime_lock_timed_out:
        meta["failure_classification"] = {
            "class": "runtime_lock_busy",
            "action": "retry after the serialized codex runtime becomes available",
            "interruption_class": "capacity",
            "retryable": True,
        }
    elif runner_exception is not None and runner_exception.get("type") == "TimeoutExpired":
        meta["failure_classification"] = {
            "class": "local_timeout",
            "action": "retry with backoff or reduce turn scope before the next daemon attempt",
            "interruption_class": "incident-or-recovery",
            "retryable": True,
            "exit_code": exit_code,
            "timeout_seconds": args.exec_timeout_seconds,
        }

    checkpoint_path = write_semantic_checkpoint(
        args.consumer_id,
        {
            "run_id": run_id,
            "consumer_id": args.consumer_id,
            "session_id": completed_session or args.session_id,
            "lease_id": selection["lease_id"],
            "selected_profile": selected_profile,
            "phase": "codex_returned"
            if runner_exception is None and exit_code == 0
            else "codex_failed"
            if runner_exception is None
            else "runner_exception",
            "summary": "codex exec returned control to the wrapper"
            if runner_exception is None and exit_code == 0
            else f"codex failure classified as {(meta.get('failure_classification') or {}).get('class', 'unknown_failure')}"
            if runner_exception is None
            else f"runner exception: {runner_exception['type']}",
            "next_action": "complete lease state and verify quota if configured"
            if runner_exception is None and exit_code == 0
            else (meta.get("failure_classification") or {}).get("action", "inspect failure output and latest receipt")
            if runner_exception is None
            else "inspect exception, checkpoint, and latest receipt before retrying",
            "resume_hint": "use the latest receipt plus binding state to decide whether the next daemon turn should be fresh",
            "context_pressure": "prepare-rollover"
            if (meta.get("failure_classification") or {}).get("class") in {"quota_exhausted", "rate_limited"}
            else "unknown",
            "continuity_status": selection.get("continuity_status"),
        },
    )
    meta["latest_checkpoint"] = str(checkpoint_path)

    if args.verify_quota_after and runner_exception is None:
        quota_rc, quota_payload = verify_quota(selected_profile)
        meta["post_run_quota_verification"] = quota_payload
        meta["post_run_quota_verification_exit_code"] = quota_rc
        if quota_payload.get("status") == "ok":
            _, record_payload = run_lb(
                [
                    "record-quota",
                    "--profile",
                    selected_profile,
                    "--source",
                    "post-run-verify",
                    "--quota-json",
                    json.dumps(quota_payload, sort_keys=True),
                ]
            )
            meta["post_run_quota_record"] = record_payload

    checkpoint_path = write_semantic_checkpoint(
        args.consumer_id,
        {
            "run_id": run_id,
            "consumer_id": args.consumer_id,
            "session_id": completed_session or args.session_id,
            "lease_id": selection["lease_id"],
            "selected_profile": selected_profile,
            "phase": "completed" if exit_code == 0 and runner_exception is None else "failed",
            "summary": "daemon turn completed cleanly"
            if exit_code == 0 and runner_exception is None
            else f"daemon turn ended with exit_code={exit_code}",
            "next_action": "inspect receipt/evidence packet and decide whether to schedule the next turn",
            "resume_hint": "the latest checkpoint is now a truthful bounded reopen surface for this daemon turn",
            "context_pressure": "prepare-rollover"
            if (meta.get("failure_classification") or {}).get("class") in {"quota_exhausted", "rate_limited"}
            else "unknown",
            "continuity_status": selection.get("continuity_status"),
        },
    )
    meta["latest_checkpoint"] = str(checkpoint_path)
    remove_active_run_state(active_run_path)
    receipt_path = write_run_receipt(args.consumer_id, meta)
    meta["run_receipt"] = str(receipt_path)
    evidence_path = write_evidence_packet(args.consumer_id, build_evidence_packet(meta, checkpoint_path))
    meta["evidence_packet"] = str(evidence_path)
    write_meta(args.meta_out, meta)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
