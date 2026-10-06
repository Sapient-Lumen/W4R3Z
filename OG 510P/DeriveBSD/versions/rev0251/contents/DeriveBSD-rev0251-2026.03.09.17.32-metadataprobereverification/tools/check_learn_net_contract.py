#!/usr/bin/env python3
"""Guardrail for the bounded network-learning contract.

This checker keeps DeriveBSD's learn/audit network lane wired:
- `net-flow-summary` stays the compact evidence-only review surface
- learn/audit sessions remain explicitly time-bounded and event-bounded
- canonical examples stay joined to `net-flow-receipt`, optional DNS receipts, and `net-egress-policy`
- docs keep the review-before-enforce boundary visible
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(obj: dict) -> str:
    return f"sha256:{hashlib.sha256(jcs_bytes(obj)).hexdigest()}"


def main() -> int:
    errors: list[str] = []

    summary_schema = load_json("spec/net.flow.summary.schema.json")
    props = summary_schema.get("properties") or {}
    if props.get("kind", {}).get("const") != "net-flow-summary":
        errors.append("spec/net.flow.summary.schema.json kind const must be net-flow-summary")
    if props.get("authority_semantics", {}).get("const") != "network-learning-evidence-only":
        errors.append("spec/net.flow.summary.schema.json authority_semantics const must be network-learning-evidence-only")
    for key in ("authority_semantics", "session", "aggregates", "evidence"):
        if key not in (summary_schema.get("required") or []):
            errors.append(f"spec/net.flow.summary.schema.json missing required field: {key}")

    session_props = ((props.get("session") or {}).get("properties") or {})
    window_props = ((session_props.get("window") or {}).get("properties") or {})
    for key in ("max_duration_seconds", "max_events"):
        if key not in window_props:
            errors.append(f"spec/net.flow.summary.schema.json session.window missing {key}")

    policy_suggestion_schema = load_json("spec/policy.suggestion.schema.json")
    ps_session_props = (((policy_suggestion_schema.get("properties") or {}).get("session") or {}).get("properties") or {})
    for key in ("mode", "window"):
        if key not in ps_session_props:
            errors.append(f"spec/policy.suggestion.schema.json session missing {key}")

    summary = load_json("spec/examples/net.flow.summary.json")
    flow = load_json("spec/examples/net.flow.receipt.json")
    dns = load_json("spec/examples/net.dns.query.receipt.json")
    policy = load_json("spec/examples/net.egress.policy.json")

    flow_d = digest(flow)
    dns_d = digest(dns)
    policy_d = digest(policy)

    if summary.get("authority_semantics") != "network-learning-evidence-only":
        errors.append("spec/examples/net.flow.summary.json authority_semantics must be network-learning-evidence-only")

    sess = summary.get("session") or {}
    if sess.get("mode") not in {"observe", "audit", "learn"}:
        errors.append("spec/examples/net.flow.summary.json session.mode must be observe/audit/learn")
    window = sess.get("window") or {}
    if not isinstance(window.get("max_duration_seconds"), int) or window.get("max_duration_seconds", 0) <= 0:
        errors.append("spec/examples/net.flow.summary.json session.window.max_duration_seconds must be a positive integer")
    if not isinstance(window.get("max_events"), int) or window.get("max_events", 0) <= 0:
        errors.append("spec/examples/net.flow.summary.json session.window.max_events must be a positive integer")

    if ((summary.get("policy_ref") or {}).get("digest") != policy_d):
        errors.append("spec/examples/net.flow.summary.json policy_ref.digest != computed digest of spec/examples/net.egress.policy.json")
    flow_refs = ((summary.get("evidence") or {}).get("flow_receipt_digests") or [])
    dns_refs = ((summary.get("evidence") or {}).get("dns_query_receipt_digests") or [])
    if flow_refs != [flow_d]:
        errors.append("spec/examples/net.flow.summary.json evidence.flow_receipt_digests must match computed digest of spec/examples/net.flow.receipt.json")
    if dns_refs != [dns_d]:
        errors.append("spec/examples/net.flow.summary.json evidence.dns_query_receipt_digests must match computed digest of spec/examples/net.dns.query.receipt.json")

    aggregates = summary.get("aggregates") or []
    if not aggregates:
        errors.append("spec/examples/net.flow.summary.json must contain at least one aggregate")
    else:
        agg = aggregates[0]
        if agg.get("policy_view") != "audit-only-would-deny":
            errors.append("canonical net-flow-summary example must demonstrate audit-only-would-deny")
        if ((agg.get("destination") or {}).get("resolution_scope") != "brokered-dns"):
            errors.append("canonical net-flow-summary example must keep resolution_scope=brokered-dns")

    doc_checks = {
        "docs/328-learned-network-policies-from-flow-receipts.md": [
            "`net-flow-summary`",
            "bounded",
            "`policy-suggestion`",
            "`net-egress-policy`",
        ],
        "docs/459-outbound-network-posture-by-profile.md": [
            "`net-flow-summary`",
            "learn/audit",
            "`docs/505-network-learn-audit-convergence-contract.md`",
        ],
        "docs/505-network-learn-audit-convergence-contract.md": [
            "`net-flow-summary`",
            "evidence-only",
            "`policy-suggestion`",
            "`net-egress-policy`",
            "bounded",
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "`net-flow-summary`",
            "ADR-0095",
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    print("Learned-network contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
