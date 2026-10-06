#!/usr/bin/env python3
"""Guardrail for publish-session endpoint-hint posture by access model."""
from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[1]
def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))
def validate(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))]
def main() -> int:
    errors=[]
    schema=load_json("spec/net.publish.session.schema.json")
    example=load_json("spec/examples/net.publish.session.json")
    validator=Draft202012Validator(schema)
    errs=validate(validator, example)
    for msg in errs[:20]: errors.append(f"spec/examples/net.publish.session.json invalid: {msg}")
    if len(errs)>20: errors.append(f"spec/examples/net.publish.session.json invalid with {len(errs)-20} additional errors")
    relay_missing_host=deepcopy(example); relay_missing_host["published_endpoint"].pop("hostname",None)
    if not validate(validator, relay_missing_host): errors.append("relay-url publish session without hostname must fail validation")
    reverse_ok=deepcopy(example)
    reverse_ok["session_id"]="tailnet-share-7c3f"
    reverse_ok["published_endpoint"]["exposure_scope"]="tailnet"
    reverse_ok["published_endpoint"]["access_model"]="reverse-forward"
    reverse_ok["published_endpoint"]["hostname"]="preview-workstation.tailnet.example.invalid"
    reverse_ok["published_endpoint"]["port"]=8443
    reverse_ok["published_endpoint"]["audience"]["class"]="tailnet-users"
    reverse_ok["published_endpoint"]["audience"]["authn_mode"]="tailnet-identity"
    reverse_ok["published_endpoint"]["locator_posture"]="tailnet-device-name"
    reverse_ok["relay"]["remote_locator"]={"kind":"object-path","value":"tailnet/preview-workstation:8443"}
    reverse_ok["published_endpoint"]["audience"].pop("validation_hint",None)
    reverse_ok["published_endpoint"].pop("secret_handoff",None)
    reverse_ok["published_endpoint"].pop("url_hint",None)
    reverse_ok["published_endpoint"].pop("path_prefix",None)
    if validate(validator, reverse_ok): errors.append("reverse-forward publish session with hostname + port and no URL hints should validate")
    reverse_bad=deepcopy(reverse_ok); reverse_bad["published_endpoint"]["url_hint"]="https://preview-workstation.tailnet.example.invalid"
    if not validate(validator, reverse_bad): errors.append("reverse-forward publish session with url_hint must fail validation")
    peer_ok=deepcopy(example)
    peer_ok["session_id"]="support-share-7c3f"
    peer_ok["published_endpoint"]["exposure_scope"]="support-peer"
    peer_ok["published_endpoint"]["access_model"]="peer-relay"
    peer_ok["relay"]["remote_locator"]={"kind":"portal-object","value":"support-session/7c3f"}
    peer_ok["published_endpoint"]["audience"]["class"]="support-session-peer"
    peer_ok["published_endpoint"]["audience"]["authn_mode"]="support-session"
    peer_ok["published_endpoint"]["audience"].pop("validation_hint",None)
    peer_ok["published_endpoint"].pop("secret_handoff",None)
    for key in ["hostname","port","url_hint","path_prefix"]: peer_ok["published_endpoint"].pop(key,None)
    peer_ok["authority"]["trigger"]="support-session"
    peer_ok["authority"].pop("consent_receipt_digest",None)
    peer_ok["authority"]["support_session_digest"]="sha256:909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeaf"
    ends=set(peer_ok["lifecycle"]["end_conditions"]); ends.discard("initiating-user-session-end"); ends.add("support-session-end"); peer_ok["lifecycle"]["end_conditions"]=sorted(ends)
    if validate(validator, peer_ok): errors.append("peer-relay publish session without URL/host hints should validate")
    peer_bad=deepcopy(peer_ok); peer_bad["published_endpoint"]["hostname"]="support.example.invalid"
    if not validate(validator, peer_bad): errors.append("peer-relay publish session with hostname must fail validation")
    doc_checks={
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md":["hostname + port","peer-relay","docs/575-publish-session-endpoint-hints-follow-access-model.md"],
        "docs/565-publish-session-session-scoped-locator-posture-boundary.md":["hostname + port","docs/575-publish-session-endpoint-hints-follow-access-model.md"],
        "docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md":["url_hint","relay-url","docs/575-publish-session-endpoint-hints-follow-access-model.md"],
        "docs/570-publish-session-access-model-posture-boundary.md":["hostname + port","peer-relay","docs/575-publish-session-endpoint-hints-follow-access-model.md"],
        "docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md":["hostname + port","reverse-forward","docs/575-publish-session-endpoint-hints-follow-access-model.md"],
        "docs/575-publish-session-endpoint-hints-follow-access-model.md":["hostname + port","peer-relay","reverse-forward"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md":["hostname + port","peer-relay","reverse-forward"],
        "docs/460-inbound-listen-posture-by-profile.md":["hostname + port","peer-relay","reverse-forward"],
        "docs/98-archive-hygiene.md":["tools/check_publish_session_endpoint_hint_contract.py","hostname + port"],
        "docs/99-llm-runbook.md":["docs/575-publish-session-endpoint-hints-follow-access-model.md","tools/check_publish_session_endpoint_hint_contract.py"],
        "docs/110-juicy-os-lessons.md":["Temporary sharing endpoint hints should follow access model","docs/575-publish-session-endpoint-hints-follow-access-model.md"],
        "docs/266-open-questions-and-risk-register.md":["ADR-0165","hostname + port"],
        "README.md":["docs/575-publish-session-endpoint-hints-follow-access-model.md","hostname + port"],
        "docs/00-index.md":["docs/575-publish-session-endpoint-hints-follow-access-model.md","hostname + port"],
        "CHANGELOG.md":["ADR-0165","docs/575-publish-session-endpoint-hints-follow-access-model.md"],
    }
    for rel,needles in doc_checks.items():
        text=(ROOT/rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text: errors.append(f"{rel} missing required publish-session endpoint-hint token: {needle}")
    if errors:
        print("Publish-session endpoint-hint posture contract check FAILED:")
        for err in errors: print(f"- {err}")
        return 1
    print("Publish-session endpoint-hint posture contract check OK")
    return 0
if __name__=="__main__": raise SystemExit(main())
