#!/usr/bin/env python3
"""Guardrail for publish-session path-prefix normalization posture."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))]


def path_prefix_errors(doc: dict) -> list[str]:
    endpoint = doc.get("published_endpoint") or {}
    path_prefix = endpoint.get("path_prefix")
    if path_prefix is None:
        return []
    errs: list[str] = []
    path = str(path_prefix)
    if not path.startswith("/"):
        errs.append("published_endpoint.path_prefix must start with /")
    if "?" in path or "#" in path:
        errs.append("published_endpoint.path_prefix must not carry query or fragment material")
    if "//" in path:
        errs.append("published_endpoint.path_prefix must not contain repeated / separators")
    if any(segment in {".", ".."} for segment in path.split("/")[1:]):
        errs.append("published_endpoint.path_prefix must not contain . or .. path segments")
    return errs


def validate_with_contract(validator: Draft202012Validator, doc: dict) -> list[str]:
    errs = validate(validator, doc)
    errs.extend(path_prefix_errors(doc))
    endpoint = doc.get("published_endpoint") or {}
    if endpoint.get("access_model") == "relay-url" and endpoint.get("url_hint") and endpoint.get("path_prefix"):
        parsed = urlsplit(str(endpoint["url_hint"]))
        if parsed.path != endpoint["path_prefix"]:
            errs.append("url_hint path must equal normalized published_endpoint.path_prefix")
    return errs


def main() -> int:
    errors: list[str] = []
    schema = load_json("spec/net.publish.session.schema.json")
    example = load_json("spec/examples/net.publish.session.json")
    validator = Draft202012Validator(schema)

    errs = validate_with_contract(validator, example)
    for msg in errs[:20]:
        errors.append(f"spec/examples/net.publish.session.json invalid: {msg}")
    if len(errs) > 20:
        errors.append(f"spec/examples/net.publish.session.json invalid with {len(errs) - 20} additional errors")

    relay_ok = deepcopy(example)
    relay_ok["session_id"] = "publish-normalized-path-7c3f"
    if validate_with_contract(validator, relay_ok):
        errors.append("relay-url share whose path_prefix is already normalized should validate")

    root_ok = deepcopy(example)
    root_ok["session_id"] = "publish-root-path-7c3f"
    root_ok["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/"
    root_ok["published_endpoint"]["path_prefix"] = "/"
    if validate_with_contract(validator, root_ok):
        errors.append("relay-url share whose normalized path_prefix is / should validate")

    slash_bad = deepcopy(example)
    slash_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/hooks//demo"
    slash_bad["published_endpoint"]["path_prefix"] = "/hooks//demo"
    if not validate_with_contract(validator, slash_bad):
        errors.append("publish-session example with repeated-separator path_prefix must fail validation")

    dot_bad = deepcopy(example)
    dot_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/hooks/../admin"
    dot_bad["published_endpoint"]["path_prefix"] = "/hooks/../admin"
    if not validate_with_contract(validator, dot_bad):
        errors.append("publish-session example with dot-segment path_prefix must fail validation")

    cur_bad = deepcopy(example)
    cur_bad["published_endpoint"]["url_hint"] = "https://preview-7c3f.relay.example.invalid:443/./hooks"
    cur_bad["published_endpoint"]["path_prefix"] = "/./hooks"
    if not validate_with_contract(validator, cur_bad):
        errors.append("publish-session example with current-directory path_prefix must fail validation")

    query_bad = deepcopy(example)
    query_bad["published_endpoint"]["path_prefix"] = "/hooks/demo?x=1"
    if not validate_with_contract(validator, query_bad):
        errors.append("publish-session example with query-bearing path_prefix must fail validation")

    doc_checks = {
        "docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md": ["path_prefix", "normalized", "docs/582-publish-session-path-prefixes-stay-normalized.md"],
        "docs/575-publish-session-endpoint-hints-follow-access-model.md": ["path_prefix", "normalized", "docs/582-publish-session-path-prefixes-stay-normalized.md"],
        "docs/579-publish-session-url-hints-follow-endpoint-tuple.md": ["path_prefix", "normalized", "docs/582-publish-session-path-prefixes-stay-normalized.md"],
        "docs/582-publish-session-path-prefixes-stay-normalized.md": ["path_prefix", "normalized", "dot-segment"],
        "docs/286-inbound-listen-broker-and-firewall-leases.md": ["path_prefix", "normalized", "docs/582-publish-session-path-prefixes-stay-normalized.md"],
        "docs/460-inbound-listen-posture-by-profile.md": ["path_prefix", "normalized", "docs/582-publish-session-path-prefixes-stay-normalized.md"],
        "docs/98-archive-hygiene.md": ["tools/check_publish_session_path_prefix_contract.py", "path_prefix", "normalized"],
        "docs/99-llm-runbook.md": ["docs/582-publish-session-path-prefixes-stay-normalized.md", "tools/check_publish_session_path_prefix_contract.py"],
        "docs/110-juicy-os-lessons.md": ["Temporary sharing path prefixes should stay normalized", "docs/582-publish-session-path-prefixes-stay-normalized.md"],
        "docs/266-open-questions-and-risk-register.md": ["ADR-0172", "path_prefix"],
        "README.md": ["docs/582-publish-session-path-prefixes-stay-normalized.md", "path_prefix", "normalized"],
        "docs/00-index.md": ["docs/582-publish-session-path-prefixes-stay-normalized.md", "path_prefix", "normalized"],
        "CHANGELOG.md": ["ADR-0172", "docs/582-publish-session-path-prefixes-stay-normalized.md"],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required publish-session path-prefix token: {needle}")

    if errors:
        print("Publish-session path-prefix posture contract check FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Publish-session path-prefix posture contract check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
