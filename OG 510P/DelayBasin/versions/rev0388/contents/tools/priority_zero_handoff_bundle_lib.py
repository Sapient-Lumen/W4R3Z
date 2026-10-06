"""Shared deterministic ZIP builders for Priority-0 external replay bundles."""

from __future__ import annotations

import hashlib
import pathlib
import zipfile
from collections.abc import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_ZIP_DATE_TIME = (1980, 1, 1, 0, 0, 0)


def file_sha256(root: pathlib.Path, rel: str) -> str:
    return hashlib.sha256((root / rel).read_bytes()).hexdigest()


def assert_no_forbidden_tokens(root: pathlib.Path, rels: Iterable[str], tokens: Iterable[str]) -> None:
    token_list = list(tokens)
    if not token_list:
        return
    for rel in rels:
        text = (root / rel).read_text(encoding="utf-8")
        for token in token_list:
            if token in text:
                raise SystemExit(f"responder bundle input {rel} leaked forbidden token: {token}")


def build_zip_bundle(
    *,
    root: pathlib.Path = ROOT,
    bundle_rel: str,
    members: Iterable[str],
    date_time: tuple[int, int, int, int, int, int] = DEFAULT_ZIP_DATE_TIME,
    forbidden_tokens: Iterable[str] = (),
    forbidden_token_members: Iterable[str] | None = None,
) -> str:
    """Build a deterministic ZIP and return its SHA256.

    `forbidden_token_members` lets responder-only bundles scan just the files
    visible before response while scorer bundles can intentionally contain
    answer-key material.
    """
    member_list = list(members)
    if not member_list:
        raise SystemExit("bundle must contain at least one member")
    scan_members = list(forbidden_token_members) if forbidden_token_members is not None else member_list
    assert_no_forbidden_tokens(root, scan_members, forbidden_tokens)
    bundle_path = root / bundle_rel
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in member_list:
            path = root / rel
            if not path.exists():
                raise SystemExit(f"missing bundle member: {rel}")
            info = zipfile.ZipInfo(rel, date_time=date_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes())
    return file_sha256(root, bundle_rel)


def build_responder_bundle(
    *,
    root: pathlib.Path = ROOT,
    bundle_rel: str,
    members: Iterable[str],
    date_time: tuple[int, int, int, int, int, int],
    forbidden_tokens: Iterable[str] = (),
) -> str:
    """Build a deterministic responder-only ZIP and return its SHA256."""
    return build_zip_bundle(
        root=root,
        bundle_rel=bundle_rel,
        members=members,
        date_time=date_time,
        forbidden_tokens=forbidden_tokens,
        forbidden_token_members=members,
    )

def assert_no_embedded_bundle_hash_claims(root: pathlib.Path, rels: Iterable[str], *, actual_bundle_sha256: str | None = None) -> None:
    """Reject responder-visible self-hash claims for the bundle containing them.

    A responder-visible bundle member may tell the responder to compute the
    bundle SHA, and it may include a blank `saw_responder_bundle_sha256` field.
    It must not embed a concrete 64-hex expected `responder_bundle_sha256`, nor
    the actual digest of the containing ZIP, because that creates an unstable
    self-reference and a misleading pre-response authority cue.
    """
    import re

    for rel in rels:
        text = (root / rel).read_text(encoding="utf-8")
        if re.search(r'"responder_bundle_sha256"\s*:\s*"[0-9a-f]{64}"', text):
            raise SystemExit(f"responder-visible member {rel} embeds concrete responder_bundle_sha256")
        if actual_bundle_sha256 and actual_bundle_sha256 in text:
            raise SystemExit(f"responder-visible member {rel} embeds actual containing bundle digest")

