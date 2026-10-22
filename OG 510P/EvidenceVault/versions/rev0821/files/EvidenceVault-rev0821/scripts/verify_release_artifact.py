#!/usr/bin/env python3
"""Verify an emitted EvidenceVault release ZIP without relying on a live tree.

This verifier is intentionally detached from package_release.py's in-memory file
list.  It checks the ZIP as an external artifact: optional SHA-256 sidecar,
portable ZIP metadata, single-root membership, embedded RELEASE_MANIFEST.json,
release-manifest included_roots coverage, embedded MANIFEST.sha256 path/digest
coverage, embedded INDEX/files.* semantics, release-manifest identity digests,
embedded RO-Crate bridge semantics, embedded revision-anchor crosswalk semantics, and indexed positive/negative crypto fixture verification from artifact bytes.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import csv
import hashlib
import io
import json
import re
import stat
import sys
import zipfile
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_COMPRESSION_NAME = 'ZIP_DEFLATED'
HEX64 = re.compile(r'^[0-9a-f]{64}$')
ROOT_RE = re.compile(r'^EvidenceVault-rev\d{4}/$')
BUNDLE_RE = re.compile(r'^EvidenceVault-rev\d{4}-\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}-[a-z0-9-]+\.zip$')
INDEX_FIELDS = ['path', 'size', 'sha256', 'category', 'project', 'ext']
EXCLUDE_FROM_INDEX = {'MANIFEST.sha256', 'INDEX/files.json', 'INDEX/files.csv'}
IDENTITY_DIGEST_TARGETS = {
    'revision_receipt_sha256': 'REVISION_RECEIPT.json',
    'opening_contract_sha256': 'OPENING_CONTRACT.json',
    'revision_anchors_sha256': 'REVISION_ANCHORS.json',
    'context_pack_sha256': 'CONTEXT_PACK.json',
    'agents_sha256': 'AGENTS.md',
    'makefile_sha256': 'Makefile',
    'source_index_json_sha256': 'SOURCE_INDEX.json',
    'current_frontier_json_sha256': 'CURRENT_FRONTIER.json',
    'validation_index_json_sha256': 'VALIDATION_INDEX.json',
    'assimilation_ledger_json_sha256': 'ASSIMILATION_LEDGER.json',
    'adr_index_json_sha256': 'ADR_INDEX.json',
    'rfc_index_json_sha256': 'RFC_INDEX.json',
    'archive_index_json_sha256': 'ARCHIVE_INDEX.json',
    'control_surfaces_sha256': 'CONTROL_SURFACES.json',
    'lifecycle_gates_sha256': 'LIFECYCLE_GATES.json',
    'artifact_index_json_sha256': 'artifacts/ARTIFACTS_INDEX.json',
    'cert_index_json_sha256': 'certs/CERTS_INDEX.json',
    'toolchain_lock_json_sha256': 'TOOLCHAIN_LOCK.json',
    'claim_obligation_map_json_sha256': 'CLAIM_OBLIGATION_MAP.json',
    'public_status_json_sha256': 'PUBLIC_STATUS.json',
    'command_runner_sequence_json_sha256': 'COMMAND_RUNNER_SEQUENCE.json',
    'release_artifact_verifier_sha256': 'scripts/verify_release_artifact.py',
    'release_artifact_verifier_validator_sha256': 'scripts/validate_command_runners.py',
    'release_manifest_schema_sha256': 'schemas/release_manifest.schema.json',
    'archive_identity_validator_sha256': 'scripts/validate_archive_identity.py',
    'ro_crate_metadata_schema_sha256': 'schemas/ro_crate_metadata.schema.json',
    'ro_crate_metadata_validator_sha256': 'scripts/validate_ro_crate_metadata.py',
}
FORBIDDEN_IDENTITY_DIGEST_KEYS = {'ro_crate_metadata_json_sha256', 'ro_crate_profile_markdown_sha256'}

RO_CRATE_CONTEXT = 'https://w3id.org/ro/crate/1.2/context'
RO_CRATE_CONFORMS_TO = 'https://w3id.org/ro/crate/1.2'
RO_CRATE_REQUIRED_HAS_PARTS = [
    'RELEASE_MANIFEST.json',
    'REVISION_RECEIPT.json',
    'REVISION_ANCHORS.json',
    'VALIDATION_INDEX.json',
    'CLAIM_OBLIGATION_MAP.json',
    'PUBLIC_STATUS.json',
    'TOOLCHAIN_LOCK.json',
    'COMMAND_RUNNER_SEQUENCE.json',
    'SOURCE_INDEX.json',
    'ARCHIVE_INDEX.json',
    'CONTROL_SURFACES.json',
    'LIFECYCLE_GATES.json',
    'papers/EXTRACTION_MAP.json',
    'published/PUBLIC_SURFACE.json',
    'MANIFEST.sha256',
    'INDEX/files.json',
    'ev_acceptability_kernel.pdf',
    'ev_interpretation_profiles.pdf',
    'ev_streamfold.pdf',
    'ev_zkrtp.pdf',
    'ev_pact_ocf.pdf',
    'sources/',
    'artifacts/',
    'certs/',
    'published/',
]
RO_CRATE_DIGESTED_FILE_ENTITIES = [
    'RELEASE_MANIFEST.json',
    'REVISION_RECEIPT.json',
    'REVISION_ANCHORS.json',
    'VALIDATION_INDEX.json',
    'CLAIM_OBLIGATION_MAP.json',
    'PUBLIC_STATUS.json',
    'TOOLCHAIN_LOCK.json',
    'COMMAND_RUNNER_SEQUENCE.json',
    'SOURCE_INDEX.json',
    'ARCHIVE_INDEX.json',
    'CONTROL_SURFACES.json',
    'LIFECYCLE_GATES.json',
    'papers/EXTRACTION_MAP.json',
    'published/PUBLIC_SURFACE.json',
    'ev_acceptability_kernel.pdf',
    'ev_interpretation_profiles.pdf',
    'ev_streamfold.pdf',
    'ev_zkrtp.pdf',
    'ev_pact_ocf.pdf',
]
RO_CRATE_SELF_REFERENTIAL_FILE_ENTITIES = {'MANIFEST.sha256', 'INDEX/files.json'}
RO_CRATE_DIRECTORY_ENTITIES = {'sources/', 'artifacts/', 'certs/', 'published/'}
RO_CRATE_RELEASE_MANIFEST_PATHS = {
    'ro_crate_metadata_json': 'ro-crate-metadata.json',
    'ro_crate_profile_markdown': 'RO_CRATE_PROFILE.md',
    'ro_crate_metadata_schema': 'schemas/ro_crate_metadata.schema.json',
    'ro_crate_metadata_validator': 'scripts/validate_ro_crate_metadata.py',
    'release_artifact_verifier': 'scripts/verify_release_artifact.py',
    'release_artifact_verifier_validator': 'scripts/validate_command_runners.py',
}
RO_CRATE_IDENTITY_DIGEST_EXCLUSIONS = [
    {
        'path': 'ro-crate-metadata.json',
        'reason': 'acyclic_release_identity_boundary: ro-crate-metadata.json digest-checks RELEASE_MANIFEST.json, so RELEASE_MANIFEST.json path-pins but does not digest it',
    },
    {
        'path': 'RO_CRATE_PROFILE.md',
        'reason': 'acyclic_release_identity_boundary: RO_CRATE_PROFILE.md exactly renders ro-crate-metadata.json and would carry the RELEASE_MANIFEST.json digest row',
    },
]

CRYPTO_FIXTURE_INDEX_PATH = 'certs/CRYPTO_FIXTURE_INDEX.json'
CRYPTO_FIXTURE_MARKDOWN_PATH = 'certs/CRYPTO_FIXTURE_INDEX.md'
CRYPTO_FIXTURE_PROFILE = {
    'envelope': 'DSSEv1',
    'signature_scheme': 'Ed25519',
    'pae': 'DSSEv1 PAE over payloadType and decoded payload bytes',
    'keyid_derivation': 'ed25519:<first 16 hex chars of sha256(SubjectPublicKeyInfo DER)>',
}



def fail(msg: str) -> None:
    print(f'release-artifact-verify: FAIL: {msg}', file=sys.stderr)
    sys.exit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()



def decode_b64ish(value: str, label: str) -> bytes:
    if not isinstance(value, str) or not value:
        fail(f'{label} must be a non-empty base64 string')
    try:
        raw = value.encode('ascii')
    except UnicodeEncodeError as exc:
        fail(f'{label} must contain only ASCII base64/base64url characters: {exc}')
    padded = raw + b'=' * ((4 - len(raw) % 4) % 4)
    errors: list[str] = []
    for altchars in (None, b'-_'):
        try:
            return base64.b64decode(padded, altchars=altchars, validate=True)
        except (binascii.Error, ValueError) as exc:
            errors.append(str(exc))
    fail(f'{label} is not decodable as base64/base64url: {errors[-1]}')


def dsse_pae(payload_type: str, payload: bytes) -> bytes:
    encoded_type = payload_type.encode('utf-8')
    return b'DSSEv1 %d %s %d ' % (len(encoded_type), encoded_type, len(payload)) + payload


def public_keyid(key: Ed25519PublicKey) -> str:
    der = key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return 'ed25519:' + sha256_bytes(der)[:16]


def load_embedded_ed25519_public_key(data: bytes, label: str) -> Ed25519PublicKey:
    if b'PRIVATE KEY' in data:
        fail(f'embedded crypto fixture key must not contain private key material: {label}')
    try:
        key = serialization.load_pem_public_key(data)
    except Exception as exc:
        fail(f'embedded crypto fixture public key does not parse in {label}: {exc}')
    if not isinstance(key, Ed25519PublicKey):
        fail(f'embedded crypto fixture public key is not Ed25519: {label}')
    return key


def parse_sidecar(sidecar: Path, bundle: Path) -> str:
    try:
        text = sidecar.read_text(encoding='utf-8')
    except FileNotFoundError:
        fail(f'sidecar not found: {sidecar}')
    if not text.endswith('\n') or '\r' in text:
        fail('SHA-256 sidecar must be UTF-8/LF text with exactly one terminal newline')
    lines = text.splitlines()
    if len(lines) != 1:
        fail('SHA-256 sidecar must contain exactly one digest row')
    parts = lines[0].split()
    if len(parts) != 2:
        fail('SHA-256 sidecar row must be: <sha256> <bundle-name>')
    digest, name = parts
    if not HEX64.fullmatch(digest):
        fail('SHA-256 sidecar digest is not 64 lowercase hex characters')
    if name != bundle.name:
        fail(f'SHA-256 sidecar bundle name mismatch: expected {bundle.name}, got {name}')
    actual = sha256_file(bundle)
    if actual != digest:
        fail(f'SHA-256 sidecar digest mismatch: expected {digest}, got {actual}')
    return digest


def parse_manifest_bytes(data: bytes) -> list[tuple[str, str]]:
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        fail(f'embedded MANIFEST.sha256 is not UTF-8: {exc}')
    if not text.endswith('\n') or '\r' in text:
        fail('embedded MANIFEST.sha256 must use LF line endings and end with a newline')
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            fail(f'embedded MANIFEST.sha256 line {n} is blank')
        try:
            digest, rel = line.split(None, 1)
        except ValueError:
            fail(f'embedded MANIFEST.sha256 line {n} is malformed')
        rel = rel.strip()
        if not HEX64.fullmatch(digest):
            fail(f'embedded MANIFEST.sha256 line {n} has invalid digest')
        if rel.startswith('/') or '\\' in rel or '..' in Path(rel).parts:
            fail(f'embedded MANIFEST.sha256 line {n} has unsafe path: {rel}')
        if rel == 'MANIFEST.sha256':
            fail('embedded MANIFEST.sha256 must not include itself')
        if rel in seen:
            fail(f'embedded MANIFEST.sha256 duplicates path: {rel}')
        seen.add(rel)
        rows.append((digest, rel))
    return rows



def classify(rel_path: str) -> tuple[str, str, str]:
    parts = rel_path.split('/')
    category = parts[0]
    project = parts[1] if len(parts) > 1 else ''
    ext = Path(rel_path).suffix.lower()
    return category, project, ext


def expected_index_row(zf: zipfile.ZipFile, root_prefix: str, rel: str) -> dict[str, object]:
    category, project, ext = classify(rel)
    data = zf.read(root_prefix + rel)
    return {
        'path': rel,
        'size': len(data),
        'sha256': sha256_bytes(data),
        'category': category,
        'project': project,
        'ext': ext,
    }


def validate_embedded_index(zf: zipfile.ZipFile, root_prefix: str, names: list[str], release_manifest: dict) -> int:
    if release_manifest.get('inventory') != 'INDEX/files.json':
        fail('embedded RELEASE_MANIFEST.json inventory must be INDEX/files.json')
    expected_rels = [name[len(root_prefix):] for name in names if name[len(root_prefix):] not in EXCLUDE_FROM_INDEX]
    try:
        index_rows = json.loads(zf.read(root_prefix + 'INDEX/files.json').decode('utf-8'))
    except KeyError:
        fail('ZIP missing embedded INDEX/files.json')
    except Exception as exc:
        fail(f'embedded INDEX/files.json is invalid: {exc}')
    if not isinstance(index_rows, list):
        fail('embedded INDEX/files.json must be a list')
    expected_by_path = {rel: expected_index_row(zf, root_prefix, rel) for rel in expected_rels}
    actual_rels: list[str] = []
    seen: set[str] = set()
    for i, row in enumerate(index_rows, start=1):
        if not isinstance(row, dict):
            fail(f'embedded INDEX/files.json row {i} is not an object')
        if set(row) != set(INDEX_FIELDS):
            fail(f'embedded INDEX/files.json row {i} has unexpected fields: {sorted(row)}')
        rel = row.get('path')
        if not isinstance(rel, str):
            fail(f'embedded INDEX/files.json row {i} path is not a string')
        if rel in seen:
            fail(f'embedded INDEX/files.json duplicates path: {rel}')
        seen.add(rel)
        actual_rels.append(rel)
        if rel in EXCLUDE_FROM_INDEX:
            fail(f'embedded INDEX/files.json includes excluded generated/self path: {rel}')
        expected = expected_by_path.get(rel)
        if expected is None:
            fail(f'embedded INDEX/files.json references unexpected path: {rel}')
        if row != expected:
            fail(f'embedded INDEX/files.json row mismatch for {rel}')
    if actual_rels != expected_rels:
        missing = sorted(set(expected_rels) - set(actual_rels))[:10]
        extra = sorted(set(actual_rels) - set(expected_rels))[:10]
        fail(f'embedded INDEX/files.json path coverage/order mismatch; missing={missing}, extra={extra}')

    try:
        csv_text = zf.read(root_prefix + 'INDEX/files.csv').decode('utf-8')
    except KeyError:
        fail('ZIP missing embedded INDEX/files.csv')
    except UnicodeDecodeError as exc:
        fail(f'embedded INDEX/files.csv is not UTF-8: {exc}')
    if not csv_text.endswith('\n') or '\r' in csv_text:
        fail('embedded INDEX/files.csv must use LF line endings and end with a newline')
    reader = csv.DictReader(io.StringIO(csv_text))
    if reader.fieldnames != INDEX_FIELDS:
        fail(f'embedded INDEX/files.csv fieldnames mismatch: {reader.fieldnames}')
    csv_rows = list(reader)
    expected_csv_rows = [
        {
            'path': str(row['path']),
            'size': str(row['size']),
            'sha256': str(row['sha256']),
            'category': str(row['category']),
            'project': str(row['project']),
            'ext': str(row['ext']),
        }
        for row in index_rows
    ]
    if csv_rows != expected_csv_rows:
        fail('embedded INDEX/files.csv rows do not exactly mirror embedded INDEX/files.json')
    return len(index_rows)


def included_root_covers(rel: str, included_root: str) -> bool:
    if included_root.endswith('/'):
        return rel.startswith(included_root)
    return rel == included_root


def validate_included_roots_coverage(zf: zipfile.ZipFile, root_prefix: str, names: list[str], release_manifest: dict) -> int:
    """Replay RELEASE_MANIFEST.included_roots from ZIP bytes.

    The packager ships the full archive root, but the release manifest is the
    named inclusion fence.  A detached verifier should reject an artifact that is
    made self-consistent at the MANIFEST/INDEX level while silently adding a
    payload outside the declared included_roots perimeter.
    """
    del zf  # Kept in the signature so this mirrors other ZIP-byte validators.
    included_roots = release_manifest.get('included_roots')
    if not isinstance(included_roots, list) or not included_roots:
        fail('embedded RELEASE_MANIFEST.json included_roots must be a non-empty list')
    seen: set[str] = set()
    rels = [name[len(root_prefix):] for name in names]
    rel_set = set(rels)
    for i, item in enumerate(included_roots, start=1):
        if not isinstance(item, str) or not item:
            fail(f'embedded RELEASE_MANIFEST.json included_roots[{i}] must be a non-empty string')
        if item in seen:
            fail(f'embedded RELEASE_MANIFEST.json included_roots duplicates entry: {item}')
        seen.add(item)
        if item.startswith('/') or '\\' in item or '..' in Path(item).parts:
            fail(f'embedded RELEASE_MANIFEST.json included_roots has unsafe entry: {item}')
        if item.endswith('/'):
            if not any(rel.startswith(item) for rel in rels):
                fail(f'embedded RELEASE_MANIFEST.json included_roots missing directory payload: {item}')
        elif item not in rel_set:
            fail(f'embedded RELEASE_MANIFEST.json included_roots missing file payload: {item}')
    for rel in rels:
        if not any(included_root_covers(rel, item) for item in included_roots):
            fail(f'embedded RELEASE_MANIFEST.json included_roots does not cover ZIP member: {rel}')
    return len(included_roots)


def validate_embedded_identity_digests(zf: zipfile.ZipFile, root_prefix: str, release_manifest: dict) -> int:
    digests = release_manifest.get('identity_digests')
    if not isinstance(digests, dict):
        fail('embedded RELEASE_MANIFEST.json identity_digests must be an object')
    for forbidden in sorted(FORBIDDEN_IDENTITY_DIGEST_KEYS):
        if forbidden in digests:
            fail(f'embedded RELEASE_MANIFEST.json must not carry cyclic identity digest key {forbidden}')
    for key, rel in IDENTITY_DIGEST_TARGETS.items():
        expected = digests.get(key)
        if not isinstance(expected, str) or not HEX64.fullmatch(expected):
            fail(f'embedded RELEASE_MANIFEST.json identity_digests.{key} is missing or not lowercase SHA-256')
        try:
            actual = sha256_bytes(zf.read(root_prefix + rel))
        except KeyError:
            fail(f'identity digest target missing from ZIP: {rel}')
        if actual != expected:
            fail(f'embedded RELEASE_MANIFEST.json identity digest mismatch for {key}')
    return len(IDENTITY_DIGEST_TARGETS)



def read_embedded_json(zf: zipfile.ZipFile, root_prefix: str, rel: str) -> dict:
    try:
        data = zf.read(root_prefix + rel)
    except KeyError:
        fail(f'ZIP missing embedded {rel}')
    try:
        parsed = json.loads(data.decode('utf-8'))
    except Exception as exc:
        fail(f'embedded {rel} is invalid: {exc}')
    if not isinstance(parsed, dict):
        fail(f'embedded {rel} must be a JSON object')
    return parsed




def resolve_anchor_pair(data, pointer: str):
    """Resolve the dotted/indexed pair syntax used by REVISION_ANCHORS.json."""
    cur = data
    for token in pointer.split('.'):
        if '[' in token:
            name, rest = token.split('[', 1)
            if not rest.endswith(']'):
                fail(f'embedded REVISION_ANCHORS.json invalid required-pair pointer: {pointer}')
            try:
                idx = int(rest[:-1])
            except ValueError:
                fail(f'embedded REVISION_ANCHORS.json invalid list index in pointer: {pointer}')
            try:
                cur = cur[name][idx]
            except Exception:
                fail(f'embedded REVISION_ANCHORS.json required-pair pointer not resolvable: {pointer}')
        else:
            try:
                cur = cur[token]
            except Exception:
                fail(f'embedded REVISION_ANCHORS.json required-pair pointer not resolvable: {pointer}')
    return cur


def validate_safe_embedded_path(rel: str, label: str, names: list[str], root_prefix: str) -> None:
    if not isinstance(rel, str) or not rel:
        fail(f'{label} must be a non-empty relative path')
    if rel.startswith('/') or '\\' in rel or '..' in Path(rel).parts:
        fail(f'{label} is unsafe: {rel}')
    if rel.endswith('/'):
        if not any(name.startswith(root_prefix + rel) for name in names):
            fail(f'{label} directory target missing from ZIP: {rel}')
    elif root_prefix + rel not in names:
        fail(f'{label} target missing from ZIP: {rel}')


def validate_embedded_revision_anchors(
    zf: zipfile.ZipFile,
    root_prefix: str,
    names: list[str],
    release_manifest: dict,
    revision_receipt: dict,
) -> int:
    """Replay REVISION_ANCHORS.json semantics from ZIP bytes.

    The release manifest identity perimeter can prove the byte hash of
    REVISION_ANCHORS.json, but a detached verifier should also reject an artifact
    whose anchor crosswalk has been made hash/self-consistent while pointing at
    wrong current-revision fields, stale required pairs, or a validator inventory
    that no longer mirrors VALIDATION_INDEX.json.
    """
    anchors = read_embedded_json(zf, root_prefix, 'REVISION_ANCHORS.json')
    if anchors.get('project') != 'EvidenceVault':
        fail('embedded REVISION_ANCHORS.json project must be EvidenceVault')
    current = anchors.get('current_revision')
    if not isinstance(current, dict):
        fail('embedded REVISION_ANCHORS.json current_revision must be an object')
    expected_archive_name = f"EvidenceVault-{current.get('revision')}-{current.get('timestamp')}-{release_manifest.get('slug')}"
    expected_current = {
        'revision': revision_receipt.get('revision'),
        'previous_revision': revision_receipt.get('previous_revision'),
        'date': revision_receipt.get('date'),
        'timestamp': revision_receipt.get('timestamp'),
        'archive_name': release_manifest.get('archive_name'),
        'bundle': release_manifest.get('bundle'),
        'root_dir': root_prefix.rstrip('/'),
    }
    for key, expected in expected_current.items():
        if current.get(key) != expected:
            fail(f'embedded REVISION_ANCHORS.json current_revision.{key} mismatch: expected {expected!r}, got {current.get(key)!r}')
    if current.get('archive_name') != expected_archive_name:
        fail('embedded REVISION_ANCHORS.json current_revision archive_name does not match revision/timestamp/manifest slug')
    if current.get('bundle') != current.get('archive_name') + '.zip':
        fail('embedded REVISION_ANCHORS.json current_revision bundle does not match archive_name')

    surfaces = anchors.get('anchored_surfaces')
    if not isinstance(surfaces, list) or not surfaces:
        fail('embedded REVISION_ANCHORS.json anchored_surfaces must be a non-empty list')
    seen: set[str] = set()
    for i, entry in enumerate(surfaces, start=1):
        if not isinstance(entry, dict):
            fail(f'embedded REVISION_ANCHORS.json anchored_surfaces[{i}] must be an object')
        path = entry.get('path')
        if path in seen:
            fail(f'embedded REVISION_ANCHORS.json duplicate anchored surface: {path}')
        seen.add(path)
        validate_safe_embedded_path(path, f'embedded REVISION_ANCHORS.json anchored_surfaces[{i}].path', names, root_prefix)
        required_pairs = entry.get('required_pairs')
        if not isinstance(required_pairs, dict) or not required_pairs:
            fail(f'embedded REVISION_ANCHORS.json anchored surface {path} must declare required_pairs')
        target = read_embedded_json(zf, root_prefix, path)
        for pointer, expected in required_pairs.items():
            actual = resolve_anchor_pair(target, pointer)
            if actual != expected:
                fail(f'embedded REVISION_ANCHORS.json anchored surface {path} mismatch at {pointer}: expected {expected!r}, got {actual!r}')

    required_anchor_paths = {
        'REVISION_RECEIPT.json',
        'RELEASE_MANIFEST.json',
        'ARCHIVE_INDEX.json',
        'CONTROL_SURFACES.json',
        'LIFECYCLE_GATES.json',
        'VALIDATION_INDEX.json',
        'SOURCE_INDEX.json',
        'CURRENT_FRONTIER.json',
        'CONTEXT_PACK.json',
        'AUDIT/HISTORICAL_ANOMALIES.json',
        'certs/CRYPTO_FIXTURE_INDEX.json',
        'TOOLCHAIN_LOCK.json',
        'CLAIM_OBLIGATION_MAP.json',
        'PUBLIC_STATUS.json',
        'ro-crate-metadata.json',
        'COMMAND_RUNNER_SEQUENCE.json',
    }
    if not required_anchor_paths.issubset(seen):
        missing = sorted(required_anchor_paths - seen)
        fail(f'embedded REVISION_ANCHORS.json anchored_surfaces missing required paths: {missing}')

    validation_index = read_embedded_json(zf, root_prefix, 'VALIDATION_INDEX.json')
    expected_validators = sorted({
        script
        for check in validation_index.get('checks', [])
        for script in check.get('scripts', [])
        if isinstance(script, str) and script.startswith('scripts/validate_')
    })
    validators = anchors.get('validators')
    if validators != expected_validators:
        missing = sorted(set(expected_validators) - set(validators or []))
        extra = sorted(set(validators or []) - set(expected_validators))
        fail(f'embedded REVISION_ANCHORS.json validator inventory mismatch; missing={missing}, extra={extra}')
    for rel in validators:
        validate_safe_embedded_path(rel, 'embedded REVISION_ANCHORS.json validator', names, root_prefix)
    return len(surfaces)


def ro_crate_type_set(value) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return set(value)
    fail(f'embedded ro-crate-metadata.json invalid @type value: {value!r}')


def ro_crate_entity_map(crate: dict) -> dict[str, dict]:
    graph = crate.get('@graph')
    if not isinstance(graph, list):
        fail('embedded ro-crate-metadata.json @graph must be a list')
    out: dict[str, dict] = {}
    for entity in graph:
        if not isinstance(entity, dict):
            fail('every embedded RO-Crate @graph entity must be an object')
        eid = entity.get('@id')
        if not isinstance(eid, str) or not eid:
            fail('every embedded RO-Crate @graph entity must have a non-empty @id')
        if eid in out:
            fail(f'embedded ro-crate-metadata.json duplicates @graph entity id: {eid}')
        out[eid] = entity
    return out


def ro_crate_target_exists(names: list[str], root_prefix: str, rel: str) -> bool:
    if rel.endswith('/'):
        return any(name.startswith(root_prefix + rel) for name in names)
    return root_prefix + rel in names


def render_ro_crate_profile(crate: dict) -> str:
    entities = ro_crate_entity_map(crate)
    root = entities['./']
    descriptor = entities['ro-crate-metadata.json']
    has_part = [item['@id'] for item in root['hasPart']]
    digest_rows = []
    for rel in RO_CRATE_DIGESTED_FILE_ENTITIES:
        ent = entities[rel]
        digest_rows.append((rel, ent['contentSize'], ent['sha256']))
    lines = [
        '# RO-Crate metadata bridge',
        '',
        'This file is the exact human-facing companion to `ro-crate-metadata.json`.',
        'The bridge exposes selected EvidenceVault core archive surfaces as compact JSON-LD research-object metadata without replacing `RELEASE_MANIFEST.json`, `MANIFEST.sha256`, or `INDEX/files.*` as governing inventory surfaces.',
        '',
        f"- Context: `{crate['@context']}`",
        f"- Descriptor: `{descriptor['@id']}`",
        f"- Conforms to: `{descriptor['conformsTo']['@id']}`",
        f"- Root entity: `{root['@id']}`",
        f"- Root version: `{root['version']}`",
        f"- Date published: `{root['datePublished']}`",
        f"- Identifier: `{root['identifier']}`",
        f"- Required hasPart entries: `{len(has_part)}`",
        f"- Digest-checked file entities: `{len(digest_rows)}`",
        '',
        '## Required root hasPart entries',
        '',
    ]
    lines.extend(f'- `{rel}`' for rel in has_part)
    lines.extend(['', '## Digest-checked file entities', ''])
    for rel, size, digest in digest_rows:
        lines.append(f'- `{rel}` — size `{size}` — sha256 `{digest}`')
    lines.extend([
        '',
        '## Self-referential inventory entries',
        '',
        '`MANIFEST.sha256` and `INDEX/files.json` are listed as core inventory surfaces but their own size/hash are omitted from this bridge to avoid a metadata/manifest digest cycle. Their governing verification remains `make manifest-check`.',
        '',
        '## Directory entities',
        '',
    ])
    for rel in sorted(RO_CRATE_DIRECTORY_ENTITIES):
        lines.append(f'- `{rel}`')
    return '\n'.join(lines).rstrip() + '\n'


def validate_embedded_ro_crate_metadata(
    zf: zipfile.ZipFile,
    root_prefix: str,
    names: list[str],
    release_manifest: dict,
    revision_receipt: dict,
) -> tuple[int, int]:
    """Replay the RO-Crate metadata bridge from ZIP bytes.

    RELEASE_MANIFEST.json intentionally path-pins ro-crate-metadata.json and
    RO_CRATE_PROFILE.md instead of digesting them, because those metadata
    surfaces digest RELEASE_MANIFEST.json and would otherwise create a cycle.
    This verifier compensates at the artifact boundary by checking the embedded
    RO-Crate root, exact Markdown companion, required hasPart entries, directory
    entities, and all digest-bearing file entities directly from ZIP bytes.
    """
    for key, expected in RO_CRATE_RELEASE_MANIFEST_PATHS.items():
        if release_manifest.get(key) != expected:
            fail(f'embedded RELEASE_MANIFEST.json {key} must be {expected}')
    if release_manifest.get('identity_digest_exclusions') != RO_CRATE_IDENTITY_DIGEST_EXCLUSIONS:
        fail('embedded RELEASE_MANIFEST.json must document the acyclic RO-Crate metadata/profile digest boundary')

    crate = read_embedded_json(zf, root_prefix, 'ro-crate-metadata.json')
    if crate.get('@context') != RO_CRATE_CONTEXT:
        fail('embedded ro-crate-metadata.json @context must be RO-Crate 1.2 context')
    entities = ro_crate_entity_map(crate)
    for required_id in ['ro-crate-metadata.json', './', *RO_CRATE_REQUIRED_HAS_PARTS]:
        if required_id not in entities:
            fail(f'embedded ro-crate-metadata.json missing entity: {required_id}')

    descriptor = entities['ro-crate-metadata.json']
    if 'CreativeWork' not in ro_crate_type_set(descriptor.get('@type')):
        fail('embedded RO-Crate descriptor must have @type CreativeWork')
    if descriptor.get('about') != {'@id': './'}:
        fail('embedded RO-Crate descriptor about must reference ./')
    if descriptor.get('conformsTo') != {'@id': RO_CRATE_CONFORMS_TO}:
        fail('embedded RO-Crate descriptor conformsTo must reference RO-Crate 1.2')

    root = entities['./']
    if 'Dataset' not in ro_crate_type_set(root.get('@type')):
        fail('embedded RO-Crate root entity must have @type Dataset')
    if root.get('conformsTo') != {'@id': RO_CRATE_CONFORMS_TO}:
        fail('embedded RO-Crate root conformsTo must reference RO-Crate 1.2')
    if root.get('datePublished') != revision_receipt.get('date'):
        fail('embedded RO-Crate root datePublished must match embedded REVISION_RECEIPT.json date')
    if root.get('version') != revision_receipt.get('revision'):
        fail('embedded RO-Crate root version must match embedded REVISION_RECEIPT.json revision')
    if root.get('identifier') != release_manifest.get('archive_name'):
        fail('embedded RO-Crate root identifier must match embedded RELEASE_MANIFEST.json archive_name')
    has_part = root.get('hasPart')
    if not isinstance(has_part, list) or not all(isinstance(item, dict) and set(item) == {'@id'} for item in has_part):
        fail('embedded RO-Crate root hasPart must be a list of {@id} references')
    has_part_ids = [item['@id'] for item in has_part]
    if has_part_ids != RO_CRATE_REQUIRED_HAS_PARTS:
        fail('embedded RO-Crate root hasPart drift')
    for rel in has_part_ids:
        if not ro_crate_target_exists(names, root_prefix, rel):
            fail(f'embedded RO-Crate hasPart target missing from ZIP: {rel}')

    for rel in RO_CRATE_DIGESTED_FILE_ENTITIES:
        entity = entities[rel]
        if 'File' not in ro_crate_type_set(entity.get('@type')):
            fail(f'embedded RO-Crate {rel} entity must have @type File')
        try:
            payload = zf.read(root_prefix + rel)
        except KeyError:
            fail(f'embedded RO-Crate digest-bearing file missing from ZIP: {rel}')
        if entity.get('contentSize') != str(len(payload)):
            fail(f'embedded RO-Crate {rel} contentSize mismatch')
        if entity.get('sha256') != sha256_bytes(payload):
            fail(f'embedded RO-Crate {rel} sha256 mismatch')
        if 'encodingFormat' not in entity:
            fail(f'embedded RO-Crate {rel} missing encodingFormat')

    for rel in RO_CRATE_SELF_REFERENTIAL_FILE_ENTITIES:
        entity = entities[rel]
        if 'File' not in ro_crate_type_set(entity.get('@type')):
            fail(f'embedded RO-Crate {rel} entity must have @type File')
        if 'sha256' in entity or 'contentSize' in entity:
            fail(f'embedded RO-Crate {rel} must omit sha256/contentSize to avoid self-reference cycle')
    for rel in RO_CRATE_DIRECTORY_ENTITIES:
        if 'Dataset' not in ro_crate_type_set(entities[rel].get('@type')):
            fail(f'embedded RO-Crate {rel} directory entity must have @type Dataset')
        if not ro_crate_target_exists(names, root_prefix, rel):
            fail(f'embedded RO-Crate directory entity has no ZIP payload: {rel}')

    try:
        profile_text = zf.read(root_prefix + 'RO_CRATE_PROFILE.md').decode('utf-8')
    except KeyError:
        fail('ZIP missing embedded RO_CRATE_PROFILE.md')
    except UnicodeDecodeError as exc:
        fail(f'embedded RO_CRATE_PROFILE.md is not UTF-8: {exc}')
    if profile_text != render_ro_crate_profile(crate):
        fail('embedded RO_CRATE_PROFILE.md must exactly mirror embedded ro-crate-metadata.json')

    return len(entities), len(RO_CRATE_DIGESTED_FILE_ENTITIES)



def safe_embedded_fixture_path(value, label: str, names: list[str], root_prefix: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f'embedded crypto fixture {label} must be a non-empty relative path')
    path = Path(value)
    if path.is_absolute() or '\\' in value or '..' in path.parts:
        fail(f'embedded crypto fixture {label} is unsafe: {value}')
    if value.endswith('/') or root_prefix + value not in names:
        fail(f'embedded crypto fixture {label} target missing from ZIP: {value}')
    return value


def render_crypto_fixture_markdown(index: dict) -> str:
    profile = index['verification_profile']
    lines = [
        '# Crypto fixture index',
        '',
        'This file is the human-readable companion to `certs/CRYPTO_FIXTURE_INDEX.json`.',
        '`scripts/validate_crypto_envelopes.py` treats the listed fixtures as verification obligations, not merely syntax examples.',
        '',
        '## Verification profile',
        '',
        f"- Envelope: `{profile['envelope']}`",
        f"- Signature scheme: `{profile['signature_scheme']}`",
        f"- PAE: `{profile['pae']}`",
        f"- Key ID derivation: `{profile['keyid_derivation']}`",
        '',
        '## Fixtures',
        '',
    ]
    for fixture in index['fixtures']:
        negative_reason = fixture.get('negative_reason') or 'not_applicable'
        lines.extend([
            f"### `{fixture['id']}`",
            f"- Role: `{fixture['role']}`",
            f"- Expected result: `{fixture['expected_result']}`",
            f"- Envelope: `{fixture['envelope_path']}`",
            f"- Public key: `{fixture['public_key_path']}`",
            f"- Key ID: `{fixture['keyid']}`",
            f"- Payload SHA-256: `{fixture['payload_sha256']}`",
            f"- PAE SHA-256: `{fixture['pae_sha256']}`",
            f"- Signature SHA-256: `{fixture['signature_sha256']}`",
            f"- Negative reason: `{negative_reason}`",
            '',
        ])
    return '\n'.join(lines).rstrip()


def validate_embedded_crypto_fixtures(
    zf: zipfile.ZipFile,
    root_prefix: str,
    names: list[str],
    revision_receipt: dict,
) -> tuple[int, int]:
    """Replay indexed positive/negative Ed25519 DSSE fixtures from ZIP bytes."""
    index = read_embedded_json(zf, root_prefix, CRYPTO_FIXTURE_INDEX_PATH)
    if index.get('format') != 'evidencevault-crypto-fixture-index':
        fail('embedded certs/CRYPTO_FIXTURE_INDEX.json format mismatch')
    if index.get('revision') != revision_receipt.get('revision'):
        fail('embedded certs/CRYPTO_FIXTURE_INDEX.json revision must match embedded REVISION_RECEIPT.json')
    if index.get('verification_profile') != CRYPTO_FIXTURE_PROFILE:
        fail('embedded certs/CRYPTO_FIXTURE_INDEX.json verification_profile mismatch')
    fixtures = index.get('fixtures')
    if not isinstance(fixtures, list) or not fixtures:
        fail('embedded certs/CRYPTO_FIXTURE_INDEX.json fixtures must be a non-empty list')

    try:
        fixture_markdown = zf.read(root_prefix + CRYPTO_FIXTURE_MARKDOWN_PATH).decode('utf-8')
    except KeyError:
        fail(f'ZIP missing embedded {CRYPTO_FIXTURE_MARKDOWN_PATH}')
    except UnicodeDecodeError as exc:
        fail(f'embedded {CRYPTO_FIXTURE_MARKDOWN_PATH} is not UTF-8: {exc}')
    if fixture_markdown != render_crypto_fixture_markdown(index):
        fail('embedded certs/CRYPTO_FIXTURE_INDEX.md must exactly mirror embedded certs/CRYPTO_FIXTURE_INDEX.json')

    seen_ids: set[str] = set()
    positive = 0
    negative = 0
    for i, fixture in enumerate(fixtures):
        if not isinstance(fixture, dict):
            fail(f'embedded crypto fixture[{i}] must be an object')
        fixture_id = fixture.get('id')
        if not isinstance(fixture_id, str) or not fixture_id:
            fail(f'embedded crypto fixture[{i}].id must be a non-empty string')
        if fixture_id in seen_ids:
            fail(f'embedded crypto fixture id duplicates: {fixture_id}')
        seen_ids.add(fixture_id)

        role = fixture.get('role')
        expected_result = fixture.get('expected_result')
        if role == 'positive':
            if expected_result != 'verify_pass':
                fail(f'{fixture_id} positive fixture must expect verify_pass')
            positive += 1
        elif role == 'negative':
            if expected_result != 'verify_fail':
                fail(f'{fixture_id} negative fixture must expect verify_fail')
            negative += 1
        else:
            fail(f'{fixture_id} role must be positive or negative')

        envelope_path = safe_embedded_fixture_path(fixture.get('envelope_path'), f'{fixture_id}.envelope_path', names, root_prefix)
        public_key_path = safe_embedded_fixture_path(fixture.get('public_key_path'), f'{fixture_id}.public_key_path', names, root_prefix)
        if not envelope_path.endswith('.dsse.json'):
            fail(f'{fixture_id} envelope_path must end with .dsse.json')
        if not public_key_path.endswith('.pem'):
            fail(f'{fixture_id} public_key_path must end with .pem')

        key = load_embedded_ed25519_public_key(zf.read(root_prefix + public_key_path), public_key_path)
        computed_keyid = public_keyid(key)
        if fixture.get('keyid') != computed_keyid:
            fail(f'{fixture_id} keyid mismatch: expected {computed_keyid}, got {fixture.get("keyid")!r}')

        envelope = read_embedded_json(zf, root_prefix, envelope_path)
        payload_type = envelope.get('payloadType')
        if not isinstance(payload_type, str) or not payload_type.strip():
            fail(f'{fixture_id} envelope payloadType must be non-empty')
        if fixture.get('payload_type') != payload_type:
            fail(f'{fixture_id} payload_type mismatch')
        payload = decode_b64ish(envelope.get('payload'), f'{fixture_id} payload')
        signatures = envelope.get('signatures')
        if not isinstance(signatures, list) or len(signatures) != 1 or not isinstance(signatures[0], dict):
            fail(f'{fixture_id} must carry exactly one DSSE signature object')
        signature_obj = signatures[0]
        if signature_obj.get('keyid') != computed_keyid:
            fail(f'{fixture_id} DSSE signature keyid mismatch')
        signature = decode_b64ish(signature_obj.get('sig'), f'{fixture_id} signature')
        if len(signature) != 64:
            fail(f'{fixture_id} signature length must be 64 bytes for Ed25519')
        pae = dsse_pae(payload_type, payload)

        expected_digests = {
            'payload_sha256': sha256_bytes(payload),
            'pae_sha256': sha256_bytes(pae),
            'signature_sha256': sha256_bytes(signature),
        }
        for field, actual in expected_digests.items():
            if fixture.get(field) != actual:
                fail(f'{fixture_id} {field} mismatch: expected {actual}, got {fixture.get(field)!r}')

        verified = True
        try:
            key.verify(signature, pae)
        except InvalidSignature:
            verified = False
        except Exception as exc:
            fail(f'{fixture_id} verification raised unexpected error: {exc}')
        if role == 'positive' and not verified:
            fail(f'{fixture_id} expected Ed25519 DSSE verification to pass')
        if role == 'negative' and verified:
            fail(f'{fixture_id} expected Ed25519 DSSE verification to fail')

    if positive < 1 or negative < 1:
        fail('embedded crypto fixture index must include at least one positive and one negative verification fixture')
    return positive, negative

def single_root_prefix(names: list[str]) -> str:
    if not names:
        fail('ZIP has no members')
    prefixes = {name.split('/', 1)[0] + '/' for name in names if '/' in name}
    if len(prefixes) != 1:
        fail(f'ZIP must contain exactly one root directory prefix, got {sorted(prefixes)!r}')
    root_prefix = next(iter(prefixes))
    if not ROOT_RE.fullmatch(root_prefix):
        fail(f'ZIP root prefix must be EvidenceVault-rev####/, got {root_prefix!r}')
    return root_prefix


def verify_zip(bundle: Path, expected_digest: str | None = None) -> tuple[str, str, int, int, int, int, int, int, int, int, int]:
    if not bundle.exists() or not bundle.is_file():
        fail(f'bundle is not a regular file: {bundle}')
    if not BUNDLE_RE.fullmatch(bundle.name):
        fail(f'bundle filename does not match EvidenceVault naming policy: {bundle.name}')
    digest = sha256_file(bundle)
    if expected_digest is not None and digest != expected_digest:
        fail('bundle digest changed after sidecar verification')

    with zipfile.ZipFile(bundle, 'r') as zf:
        bad = zf.testzip()
        if bad is not None:
            fail(f'ZIP integrity check failed at {bad}')
        names = zf.namelist()
        if names != sorted(names):
            fail('ZIP member order must be lexicographic')
        if len(names) != len(set(names)):
            fail('ZIP contains duplicate member names')
        if any(name.endswith('/') for name in names):
            fail('ZIP must not contain directory entries')
        if zf.comment:
            fail('ZIP file comment must be empty')
        root_prefix = single_root_prefix(names)
        info_by_name = {info.filename: info for info in zf.infolist()}
        for name in names:
            if not name.startswith(root_prefix):
                fail(f'ZIP entry outside root prefix: {name}')
            rel = name[len(root_prefix):]
            if not rel or rel.startswith('/') or '\\' in rel or '..' in Path(rel).parts:
                fail(f'unsafe ZIP entry path: {name}')
            if rel.endswith('.pyc') or '__pycache__' in Path(rel).parts:
                fail(f'transient Python bytecode in ZIP: {name}')
            info = info_by_name[name]
            if info.date_time != FIXED_ZIP_TIMESTAMP:
                fail(f'ZIP entry timestamp is not fixed for {name}')
            if info.compress_type != zipfile.ZIP_DEFLATED:
                fail(f'ZIP entry compression is not {ZIP_COMPRESSION_NAME} for {name}')
            if info.extra:
                fail(f'ZIP entry has non-empty extra metadata for {name}')
            if info.create_system != 3:
                fail(f'ZIP entry must use Unix external attributes for {name}')
            encoded_mode = info.external_attr >> 16
            if stat.S_IFMT(encoded_mode) != stat.S_IFREG:
                fail(f'ZIP entry is not marked as a regular file: {name}')
            if stat.S_IMODE(encoded_mode) != 0o644:
                fail(f'ZIP entry mode must be 0644 for {name}, got {stat.S_IMODE(encoded_mode):o}')

        try:
            release_manifest = json.loads(zf.read(root_prefix + 'RELEASE_MANIFEST.json').decode('utf-8'))
        except KeyError:
            fail('ZIP missing embedded RELEASE_MANIFEST.json')
        except Exception as exc:
            fail(f'embedded RELEASE_MANIFEST.json is invalid: {exc}')
        if release_manifest.get('repo_root') != root_prefix.rstrip('/'):
            fail('embedded RELEASE_MANIFEST.json repo_root does not match ZIP root prefix')
        if release_manifest.get('bundle') != bundle.name:
            fail('embedded RELEASE_MANIFEST.json bundle does not match artifact filename')
        if release_manifest.get('file_count') != len(names):
            fail('embedded RELEASE_MANIFEST.json file_count does not match ZIP member count')
        if release_manifest.get('archive_name') != bundle.name[:-4]:
            fail('embedded RELEASE_MANIFEST.json archive_name does not match bundle filename')

        revision_receipt = read_embedded_json(zf, root_prefix, 'REVISION_RECEIPT.json')
        if revision_receipt.get('revision') != release_manifest.get('revision'):
            fail('embedded REVISION_RECEIPT.json revision does not match embedded RELEASE_MANIFEST.json')
        if revision_receipt.get('previous_revision') != release_manifest.get('previous_revision'):
            fail('embedded REVISION_RECEIPT.json previous_revision does not match embedded RELEASE_MANIFEST.json')
        if revision_receipt.get('timestamp') != release_manifest.get('timestamp'):
            fail('embedded REVISION_RECEIPT.json timestamp does not match embedded RELEASE_MANIFEST.json')

        inclusion_count = validate_included_roots_coverage(zf, root_prefix, names, release_manifest)

        try:
            manifest_rows = parse_manifest_bytes(zf.read(root_prefix + 'MANIFEST.sha256'))
        except KeyError:
            fail('ZIP missing embedded MANIFEST.sha256')
        expected_manifest_rels = [name[len(root_prefix):] for name in names if name[len(root_prefix):] != 'MANIFEST.sha256']
        actual_manifest_rels = [rel for _digest, rel in manifest_rows]
        if actual_manifest_rels != expected_manifest_rels:
            missing = sorted(set(expected_manifest_rels) - set(actual_manifest_rels))[:10]
            extra = sorted(set(actual_manifest_rels) - set(expected_manifest_rels))[:10]
            fail(f'embedded MANIFEST.sha256 path coverage/order mismatch; missing={missing}, extra={extra}')
        for expected, rel in manifest_rows:
            actual = sha256_bytes(zf.read(root_prefix + rel))
            if actual != expected:
                fail(f'embedded MANIFEST.sha256 digest mismatch for {rel}')

        index_count = validate_embedded_index(zf, root_prefix, names, release_manifest)
        identity_count = validate_embedded_identity_digests(zf, root_prefix, release_manifest)
        revision_anchor_count = validate_embedded_revision_anchors(
            zf, root_prefix, names, release_manifest, revision_receipt
        )
        ro_crate_entities, ro_crate_digests = validate_embedded_ro_crate_metadata(
            zf, root_prefix, names, release_manifest, revision_receipt
        )
        crypto_positive, crypto_negative = validate_embedded_crypto_fixtures(
            zf, root_prefix, names, revision_receipt
        )

    return digest, root_prefix.rstrip('/'), len(names), index_count, identity_count, inclusion_count, revision_anchor_count, ro_crate_entities, ro_crate_digests, crypto_positive, crypto_negative


def main() -> None:
    parser = argparse.ArgumentParser(description='Verify an emitted EvidenceVault release ZIP artifact and optional SHA-256 sidecar.')
    parser.add_argument('bundle', type=Path, help='Path to EvidenceVault release ZIP')
    parser.add_argument('--sidecar', type=Path, default=None, help='Path to .zip.sha256 sidecar; defaults to <bundle>.sha256 when present')
    parser.add_argument('--require-sidecar', action='store_true', help='Fail if no SHA-256 sidecar is present')
    args = parser.parse_args()

    bundle = args.bundle
    sidecar = args.sidecar if args.sidecar is not None else bundle.with_name(bundle.name + '.sha256')
    expected_digest = None
    if sidecar.exists():
        expected_digest = parse_sidecar(sidecar, bundle)
    elif args.require_sidecar:
        fail(f'required sidecar not found: {sidecar}')
    digest, root, count, index_count, identity_count, inclusion_count, revision_anchor_count, ro_crate_entities, ro_crate_digests, crypto_positive, crypto_negative = verify_zip(bundle, expected_digest)
    sidecar_note = 'sidecar=present' if expected_digest else 'sidecar=absent'
    print(f'release-artifact-verify: OK ({bundle.name}, root={root}, files={count}, index_rows={index_count}, identity_digests={identity_count}, included_roots={inclusion_count}, revision_anchors={revision_anchor_count}, ro_crate_entities={ro_crate_entities}, ro_crate_digests={ro_crate_digests}, crypto_positive={crypto_positive}, crypto_negative={crypto_negative}, sha256={digest}, {sidecar_note})')


if __name__ == '__main__':
    main()
