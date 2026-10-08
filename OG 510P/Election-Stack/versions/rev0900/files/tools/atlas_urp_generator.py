#!/usr/bin/env python3
"""atlas_urp_generator.py — research/prototype utility, fail-closed by default.

Creates a deterministic RIPE Atlas measurement request draft from an
AtlasMeasurementPlan and an EthicsGuardrailsPolicy, and optionally submits it
only when the operator supplies both --create and --operator-reviewed-payload.

Outputs:
- AtlasMeasurementReceipt.json
- ripe_atlas_create_payload.json
- atlas_raw_results.json (only when measurements are created and results fetched)

Docs:
- 117-automated-unreachability-proofs-ripe-atlas.md
- 118-measurement-ethics-guardrails.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

ATLAS_CREATE_URL = "https://atlas.ripe.net/api/v2/measurements/"
ATLAS_RESULTS_URL_TMPL = "https://atlas.ripe.net/api/v2/measurements/{mid}/results/"
REQUIRED_DISALLOWED_ACTIONS = {
    "port_scanning",
    "high_rate_measurements",
    "large_payloads",
    "embedding_voter_ids",
}
SENSITIVE_PATH_RE = re.compile(r"(?i)(voter|eligibility|token|session|credential|secret|password|auth|jwt)")
TARGET_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str | Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def parse_unix_window(start_unix: int, stop_unix: int) -> tuple[int, int, int]:
    if start_unix <= 0 or stop_unix <= 0:
        raise ValueError("--start and --stop must be positive UNIX timestamps")
    if stop_unix <= start_unix:
        raise ValueError("--stop must be greater than --start")
    return start_unix, stop_unix, stop_unix - start_unix


def validate_ethics_policy(ethics: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rate_caps = ethics.get("rate_caps") if isinstance(ethics, dict) else None
    approval = ethics.get("approval") if isinstance(ethics, dict) else None
    disallowed = set(ethics.get("disallowed_actions") or []) if isinstance(ethics, dict) else set()

    if not isinstance(rate_caps, dict):
        errors.append("ethics.rate_caps must be an object")
        rate_caps = {}
    if not isinstance(approval, dict):
        errors.append("ethics.approval must be an object")
        approval = {}
    if approval.get("two_person_rule") is not True:
        errors.append("ethics.approval.two_person_rule must be true before active measurement creation")
    missing_disallowed = sorted(REQUIRED_DISALLOWED_ACTIONS - {str(x) for x in disallowed})
    if missing_disallowed:
        errors.append("ethics.disallowed_actions missing required controls: " + ",".join(missing_disallowed))
    for key in ("max_duration_seconds", "max_measurements_per_hour", "max_probes_per_measurement"):
        value = rate_caps.get(key)
        if not isinstance(value, int) or value <= 0:
            errors.append(f"ethics.rate_caps.{key} must be a positive integer")
    if not str(ethics.get("contact") or "").strip():
        errors.append("ethics.contact must be present")
    return errors


def validate_plan_against_policy(plan: dict[str, Any], ethics: dict[str, Any], *, start_unix: int, stop_unix: int) -> list[str]:
    errors: list[str] = []
    _start, _stop, duration = parse_unix_window(start_unix, stop_unix)
    rate_caps = ethics.get("rate_caps") if isinstance(ethics.get("rate_caps"), dict) else {}

    policy_ref = str(plan.get("ethics_policy_ref") or "").strip()
    policy_id = str(ethics.get("policy_id") or "").strip()
    if policy_ref and policy_id and policy_ref != policy_id:
        errors.append(f"plan.ethics_policy_ref {policy_ref!r} does not match ethics.policy_id {policy_id!r}")
    max_duration = int(rate_caps.get("max_duration_seconds") or 0)
    if max_duration and duration > max_duration:
        errors.append(f"measurement window duration {duration}s exceeds ethics cap {max_duration}s")

    targets = plan.get("targets") if isinstance(plan.get("targets"), list) else []
    probe_sets = plan.get("probe_sets") if isinstance(plan.get("probe_sets"), list) else []
    max_measurements = int(rate_caps.get("max_measurements_per_hour") or 0)
    if max_measurements and len(targets) > max_measurements:
        errors.append(f"target count {len(targets)} exceeds max_measurements_per_hour {max_measurements}")

    max_probes_cap = int(rate_caps.get("max_probes_per_measurement") or 0)
    for idx, ps in enumerate(probe_sets):
        if not isinstance(ps, dict):
            errors.append(f"probe_sets[{idx}] must be an object")
            continue
        min_probes = ps.get("min_probes")
        max_probes = ps.get("max_probes")
        if not isinstance(min_probes, int) or not isinstance(max_probes, int) or min_probes < 1 or max_probes < min_probes:
            errors.append(f"probe_sets[{idx}] has invalid min/max probes")
        if max_probes_cap and isinstance(max_probes, int) and max_probes > max_probes_cap:
            errors.append(f"probe_sets[{idx}].max_probes {max_probes} exceeds ethics cap {max_probes_cap}")

    for idx, target in enumerate(targets):
        if not isinstance(target, dict):
            errors.append(f"targets[{idx}] must be an object")
            continue
        ttype = target.get("type")
        if ttype not in {"https", "http", "dns", "icmp"}:
            errors.append(f"targets[{idx}].type is unsupported: {ttype!r}")
        identifier = str(target.get("target") or "")
        if not identifier or not TARGET_RE.fullmatch(identifier):
            errors.append(f"targets[{idx}].target must be a bounded host/IP token")
        path = str(target.get("path") or "/")
        if ttype in {"http", "https"}:
            if not path.startswith("/") or "?" in path or "#" in path or len(path) > 128:
                errors.append(f"targets[{idx}].path must be a short path-only HTTP target")
            if SENSITIVE_PATH_RE.search(path):
                errors.append(f"targets[{idx}].path appears to contain voter/session/secret material")
            port = target.get("port", 443 if ttype == "https" else 80)
            if not isinstance(port, int) or not (1 <= port <= 65535):
                errors.append(f"targets[{idx}].port must be 1..65535")
    return errors


def build_create_payload(plan: dict[str, Any], *, start_unix: int, stop_unix: int) -> dict[str, Any]:
    definitions: list[dict[str, Any]] = []
    for target in plan.get("targets", []):
        if not isinstance(target, dict):
            continue
        name = str(target.get("name") or target.get("target") or "target")
        ttype = target.get("type")
        host = str(target.get("target") or "")
        if ttype in {"http", "https"}:
            definitions.append({
                "description": name,
                "type": "http",
                "af": 4,
                "target": host,
                "port": int(target.get("port") or (443 if ttype == "https" else 80)),
                "path": str(target.get("path") or "/"),
                "method": "HEAD",
                "resolve_on_probe": True,
            })
        elif ttype == "dns":
            definitions.append({
                "description": name,
                "type": "dns",
                "af": 4,
                "query_argument": host,
                "query_type": "SOA",
                "use_probe_resolver": True,
            })
        elif ttype == "icmp":
            definitions.append({
                "description": name,
                "type": "ping",
                "af": 4,
                "target": host,
            })

    probes: list[dict[str, Any]] = []
    for ps in plan.get("probe_sets", []):
        if not isinstance(ps, dict):
            continue
        selection = ps.get("selection") if isinstance(ps.get("selection"), dict) else {}
        probe: dict[str, Any] = {
            "requested": int(ps.get("max_probes") or ps.get("min_probes") or 1),
            "type": "area",
            "value": str(selection.get("country_code") or "WW"),
        }
        if "asn_v4" in selection:
            probe = {"requested": int(ps.get("max_probes") or 1), "type": "asn", "value": str(selection["asn_v4"])}
        probes.append(probe)

    return {
        "definitions": definitions,
        "probes": probes,
        "is_oneoff": True,
        "start_time": start_unix,
        "stop_time": stop_unix,
        "bill_to": str(plan.get("election_id") or plan.get("plan_id") or "election-evidence"),
    }


def create_measurement(api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    if requests is None:
        raise RuntimeError("requests not available")
    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    r = requests.post(ATLAS_CREATE_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_results(mid: int, start_unix: int, stop_unix: int) -> Any:
    if requests is None:
        raise RuntimeError("requests not available")
    url = ATLAS_RESULTS_URL_TMPL.format(mid=mid)
    params = {"start": start_unix, "stop": stop_unix}
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def measurement_ids_from_response(resp: Any) -> list[int]:
    mids: list[int] = []
    if isinstance(resp, dict):
        if isinstance(resp.get("measurements"), list):
            for item in resp["measurements"]:
                if isinstance(item, dict) and "id" in item:
                    mids.append(int(item["id"]))
                elif isinstance(item, int):
                    mids.append(item)
        elif isinstance(resp.get("id"), int):
            mids.append(int(resp["id"]))
    return mids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="Path to AtlasMeasurementPlan JSON")
    ap.add_argument("--ethics", required=True, help="Path to EthicsGuardrailsPolicy JSON")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--api-key-env", default="RIPE_ATLAS_API_KEY", help="Env var holding RIPE Atlas API key")
    ap.add_argument("--create", action="store_true", help="Actually create measurements via API")
    ap.add_argument("--operator-reviewed-payload", action="store_true", help="Required with --create after reviewing emitted payload and ethics checks")
    ap.add_argument("--start", type=int, required=True, help="Start UNIX timestamp for results window")
    ap.add_argument("--stop", type=int, required=True, help="Stop UNIX timestamp for results window")
    args = ap.parse_args()

    try:
        start_unix, stop_unix, _duration = parse_unix_window(args.start, args.stop)
    except ValueError as exc:
        print(f"Invalid window: {exc}", file=sys.stderr)
        return 2

    plan = load_json(args.plan)
    ethics = load_json(args.ethics)
    if not isinstance(plan, dict) or not isinstance(ethics, dict):
        print("Plan and ethics inputs must be JSON objects", file=sys.stderr)
        return 2

    errors = validate_ethics_policy(ethics) + validate_plan_against_policy(plan, ethics, start_unix=start_unix, stop_unix=stop_unix)
    if args.create and not args.operator_reviewed_payload:
        errors.append("--create requires --operator-reviewed-payload after reviewing ripe_atlas_create_payload.json")
    if args.create and requests is None:
        errors.append("--create requires the requests package")
    if errors:
        for err in errors:
            print(f"ETHICS/PLAN ERROR: {err}", file=sys.stderr)
        return 2

    os.makedirs(args.outdir, exist_ok=True)
    create_payload = build_create_payload(plan, start_unix=start_unix, stop_unix=stop_unix)
    payload_path = Path(args.outdir) / "ripe_atlas_create_payload.json"
    save_json(payload_path, create_payload)
    raw = json.dumps(create_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    receipt = {
        "plan_id": plan.get("plan_id"),
        "created_measurement_ids": [],
        "api_endpoint": ATLAS_CREATE_URL,
        "created_at": utc_now_iso(),
        "raw_request_hash": sha256_bytes(raw),
        "notes": "dry_run_payload_emitted; network_create_requires_--create_and_--operator-reviewed-payload",
    }

    if args.create:
        api_key = os.environ.get(args.api_key_env)
        if not api_key:
            print(f"Missing API key in env var {args.api_key_env}", file=sys.stderr)
            return 2
        resp = create_measurement(api_key, create_payload)
        receipt["created_measurement_ids"] = measurement_ids_from_response(resp)
        receipt["notes"] = "network_create_attempted_after_operator_review; receipt_ids_depend_on_ripe_atlas_response"

    save_json(Path(args.outdir) / "AtlasMeasurementReceipt.json", receipt)

    if receipt["created_measurement_ids"]:
        all_results = {}
        for mid in receipt["created_measurement_ids"]:
            all_results[str(mid)] = fetch_results(int(mid), start_unix, stop_unix)
        save_json(Path(args.outdir) / "atlas_raw_results.json", all_results)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
