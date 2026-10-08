#!/usr/bin/env python3
"""Canonical release-lineage validation shared by release audits and packaging checks."""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
from typing import Any

PROJECT_NAME = "Moral-Taxation"
ROOT_PREFIX = "moral_taxation"
REVISION_RE = re.compile(r"^rev(\d{4})$")
CODENAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ZIP_RE = re.compile(
    rf"^{PROJECT_NAME}-rev\d{{4}}-\d{{4}}\.\d{{2}}\.\d{{2}}\.\d{{2}}\.\d{{2}}-[a-z0-9]+(?:-[a-z0-9]+)*\.zip$"
)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def previous_revision(revision: str) -> str:
    match = REVISION_RE.fullmatch(revision)
    if not match:
        raise ValueError(f"invalid revision: {revision}")
    number = int(match.group(1))
    if number <= 0:
        raise ValueError("revision has no predecessor")
    return f"rev{number - 1:04d}"


def canonical_zip_name(revision: str, created_at_utc: str, codename: str) -> str:
    if not REVISION_RE.fullmatch(revision):
        raise ValueError(f"invalid revision: {revision}")
    if not CODENAME_RE.fullmatch(codename):
        raise ValueError(f"invalid codename: {codename}")
    try:
        created = dt.datetime.fromisoformat(created_at_utc.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid created_at_utc: {created_at_utc}") from exc
    if created.utcoffset() != dt.timedelta(0):
        raise ValueError("created_at_utc must use UTC")
    stamp = created.strftime("%Y.%m.%d.%H.%M")
    return f"{PROJECT_NAME}-{revision}-{stamp}-{codename}.zip"


def collect_lineage_errors(root: pathlib.Path) -> tuple[list[str], dict[str, Any]]:
    root = root.resolve()
    errors: list[str] = []
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    try:
        expected_previous = previous_revision(version)
    except ValueError as exc:
        errors.append(str(exc))
        expected_previous = ""

    receipt = load_json(root / "REVISION-RECEIPT.json")
    releases = load_json(root / "RELEASES.json")
    context = load_json(root / "context-pack.json")
    cube = load_json(root / "cube-index.json")
    sources = load_json(root / "SOURCES.json")
    source_count = len(sources.get("sources", []))
    codename = str(receipt.get("codename", ""))
    created = str(receipt.get("created_at_utc", ""))
    try:
        expected_zip = canonical_zip_name(version, created, codename)
    except ValueError as exc:
        errors.append(str(exc))
        expected_zip = ""
    expected_root = f"{ROOT_PREFIX}_{version}"

    equal_checks = [
        (receipt.get("revision"), version, "REVISION-RECEIPT.json revision"),
        (receipt.get("previous_revision"), expected_previous, "REVISION-RECEIPT.json previous_revision"),
        (receipt.get("root"), expected_root, "REVISION-RECEIPT.json root"),
        (receipt.get("zip"), expected_zip, "REVISION-RECEIPT.json zip"),
        (receipt.get("output_zip"), expected_zip, "REVISION-RECEIPT.json output_zip"),
        (receipt.get("source_count"), source_count, "REVISION-RECEIPT.json source_count"),
        (releases.get("latest_revision"), version, "RELEASES.json latest_revision"),
        (releases.get("previous_revision"), expected_previous, "RELEASES.json previous_revision"),
        (releases.get("latest_codename"), codename, "RELEASES.json latest_codename"),
        (releases.get("latest_zip"), expected_zip, "RELEASES.json latest_zip"),
        (releases.get("root"), expected_root, "RELEASES.json root"),
        (releases.get("created_at_utc"), created, "RELEASES.json created_at_utc"),
        (releases.get("latest_created_at_utc"), created, "RELEASES.json latest_created_at_utc"),
        (releases.get("source_count"), source_count, "RELEASES.json source_count"),
        (context.get("revision"), version, "context-pack.json revision"),
        (context.get("codename"), codename, "context-pack.json codename"),
        (context.get("created_at_utc"), created, "context-pack.json created_at_utc"),
        (context.get("generated_at_utc"), created, "context-pack.json generated_at_utc"),
        (context.get("source_count"), source_count, "context-pack.json source_count"),
        (cube.get("revision"), version, "cube-index.json revision"),
        (cube.get("generated_at_utc"), created, "cube-index.json generated_at_utc"),
        (sources.get("revision"), version, "SOURCES.json revision"),
        (sources.get("source_count"), source_count, "SOURCES.json source_count"),
        (sources.get("generated_at_utc"), created, "SOURCES.json generated_at_utc"),
        (root.name, expected_root, "archive root directory"),
    ]
    for actual, expected, label in equal_checks:
        if actual != expected:
            errors.append(f"{label}={actual!r}; expected {expected!r}")

    input_zip = str(receipt.get("input_zip", ""))
    if not ZIP_RE.fullmatch(input_zip):
        errors.append("REVISION-RECEIPT.json input_zip must use the canonical release filename structure")
    elif expected_previous and f"-{expected_previous}-" not in input_zip:
        errors.append("REVISION-RECEIPT.json input_zip must identify the immediate previous revision")

    if expected_zip and not ZIP_RE.fullmatch(expected_zip):
        errors.append("derived output zip does not match the canonical filename structure")

    route_revisions: set[str] = set()
    for key in ("proposal_route", "frontier_route"):
        for value in context.get(key, []):
            route_revisions.update(re.findall(r"rev\d{4}", str(value).lower()))
    stale_route_revisions = sorted(route_revisions - {version})
    if stale_route_revisions:
        errors.append(
            "context-pack proposal/frontier routes contain stale revision labels: "
            + ", ".join(stale_route_revisions)
        )
    if version not in route_revisions:
        errors.append("context-pack proposal/frontier routes must include the active revision report")

    details = {
        "revision": version,
        "previous_revision": expected_previous,
        "codename": codename,
        "created_at_utc": created,
        "canonical_zip": expected_zip,
        "canonical_root": expected_root,
        "source_count": source_count,
        "context_route_revisions": sorted(route_revisions),
        "valid": not errors,
    }
    return errors, details
