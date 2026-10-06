"""Small shared helpers for semantic cube guardrails.

This module deliberately stays narrower than a framework: it only collects the
checker plumbing that was already being copied across cube-audit scripts and the
release-version/id invariant that caused the r532/r533 skew found in rev0502.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

from cube_digest_lib import load_json

_VERSION_RE = re.compile(r"^(?P<yyyy>\d{4})-(?P<mm>\d{2})-(?P<dd>\d{2})r(?P<rev>\d+)$")


def fail(msg: str) -> None:
    """Print a guardrail failure and exit non-zero."""
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(root: Path, schema_rel: str, obj: Any) -> list[str]:
    """Return sorted JSON-Schema validation errors for a repo-relative schema."""
    # Keep jsonschema lazy so pure semantic checks do not pay the schema import
    # cost just to validate release/id tokens.
    from jsonschema import Draft202012Validator

    schema = load_json(root, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def require_text_tokens(root: Path, required: Mapping[str, Iterable[str]], label: str = "required") -> None:
    """Require small discoverability tokens in repo-relative text files."""
    for rel, tokens in required.items():
        path = root / rel
        if not path.exists():
            fail(f"missing {label} surface: {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing {label} token {token!r}")


def release_token(version: str) -> str:
    """Convert a DeriveBSD release string into the token used by durable IDs.

    Example: ``2026-05-30r533`` -> ``20260530-r533``.
    """
    m = _VERSION_RE.match(version)
    if not m:
        raise ValueError(f"unrecognized generated_for_version {version!r}")
    return f"{m.group('yyyy')}{m.group('mm')}{m.group('dd')}-r{m.group('rev')}"


def generated_artifact_id_errors(obj: Mapping[str, Any], id_fields: Iterable[str] | None = None) -> list[str]:
    """Return semantic errors for generated_for_version/id-token skew.

    The invariant is intentionally simple: when a top-level generated artifact
    carries ``generated_for_version``, each durable top-level ``*_id`` field must
    contain the exact date/revision token for that version. This catches local
    equality checks that regenerated stale IDs and compared stale-to-stale.
    """
    version = obj.get("generated_for_version")
    if not isinstance(version, str):
        return ["missing generated_for_version"]

    try:
        token = release_token(version)
    except ValueError as exc:
        return [str(exc)]

    fields = list(id_fields or [k for k in sorted(obj) if k.endswith("_id")])
    if not fields:
        return ["no top-level *_id field to bind to generated_for_version"]

    errors: list[str] = []
    for field in fields:
        value = obj.get(field)
        if not isinstance(value, str):
            errors.append(f"{field} is missing or not a string")
        elif token not in value:
            errors.append(f"{field}={value!r} does not contain release token {token!r}")
    return errors


def require_generated_artifact_id_consistency(obj: Mapping[str, Any], id_fields: Iterable[str] | None = None) -> None:
    """Fail unless generated artifact IDs agree with generated_for_version."""
    errors = generated_artifact_id_errors(obj, id_fields)
    if errors:
        fail("generated artifact release-id consistency failed: " + "; ".join(errors))
