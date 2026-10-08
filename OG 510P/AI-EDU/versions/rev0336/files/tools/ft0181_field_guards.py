#!/usr/bin/env python3
"""Shared FT-0181 local-field boundary guards.

These helpers keep local execution aids and returned-owner inputs out of
archive-controlled surfaces while allowing only scratch and explicitly external
local paths. They are deliberately small: the goal is to prevent drift between the
owner-request, owner-route-block, owner-contact, field-next-action, returned-CSV, workbench-seed,
workbench-review-brief, workbench-review, first-packet decision-brief, and first-packet decision routing tools without creating another
registry or policy surface.
"""
from __future__ import annotations

from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import hashlib
import json
import os

CONTROLLED_TOP_LEVEL = {
    'docs',
    'examples',
    'fixtures',
    'schemas',
    'templates',
    'tools',
}
CONTROLLED_ROOT_FILES = {
    'AGENTS.md',
    'ARCHIVE_INDEX.md',
    'ASSUMPTION_LEDGER.json',
    'BRANCH_FAMILY_INDEX.json',
    'CHANGELOG.md',
    'CUBE_SCHEMA_REGISTRY.json',
    'CUBE_SURFACE_CONTRACTS.json',
    'CUBE_TOOLCHAIN_REGISTRY.json',
    'FOLLOWTHROUGH_QUEUE.json',
    'FOREIGN_PRESSURE_LEDGER.json',
    'Makefile',
    'README.md',
    'RELEASE-MANIFEST.json',
    'REVISION_RECEIPT.json',
    'START_HERE.md',
    'SURFACES.json',
    'context-pack.json',
}

DEFAULT_OPERATOR_TIMEZONE = 'America/New_York'
OPERATOR_TIMEZONE_ENV = 'CUBE_OPERATOR_TIMEZONE'
OPERATOR_DATE_ENV = 'CUBE_AS_OF_DATE'
LEGACY_OPERATOR_DATE_ENV = 'FT0181_AS_OF_DATE'


def operator_today(*, tz_name: str | None = None) -> date:
    """Return the operator-local field date for FT-0181 clock defaults.

    Cloudtainers often run on UTC while the operator works in a local timezone.
    Field clocks should not silently move one day ahead near local evening. An
    explicit CUBE_AS_OF_DATE / FT0181_AS_OF_DATE override wins for reproducible
    lint fixtures and handoffs; otherwise use CUBE_OPERATOR_TIMEZONE, defaulting
    to the project operator timezone. UTC is only a last-resort fallback for an
    unavailable timezone database entry.
    """
    override = (os.environ.get(OPERATOR_DATE_ENV) or os.environ.get(LEGACY_OPERATOR_DATE_ENV) or '').strip()
    if override:
        return date.fromisoformat(override)
    zone_name = (tz_name or os.environ.get(OPERATOR_TIMEZONE_ENV) or DEFAULT_OPERATOR_TIMEZONE).strip()
    try:
        zone = ZoneInfo(zone_name)
    except ZoneInfoNotFoundError:
        zone = timezone.utc
    return datetime.now(zone).date()


def operator_today_iso(*, tz_name: str | None = None) -> str:
    return operator_today(tz_name=tz_name).isoformat()


def operator_due_date_iso(days: int, *, tz_name: str | None = None) -> str:
    return (operator_today(tz_name=tz_name) + timedelta(days=days)).isoformat()


def packet_creation_field_date(manifest: dict) -> date | None:
    operator_local = manifest.get('operator_local_date')
    if isinstance(operator_local, str):
        try:
            return date.fromisoformat(operator_local)
        except ValueError:
            pass
    created = manifest.get('created_at_utc')
    if isinstance(created, str) and created.endswith('Z'):
        try:
            return datetime.fromisoformat(created[:-1] + '+00:00').astimezone(timezone.utc).date()
        except ValueError:
            return None
    return None

RETURNED_CSV_SMOKE_MARKERS = {
    'synthetic smoke fixture',
    'smoke fixture only',
    'for cli smoke testing only',
    'not a returned owner packet',
    'src0 synthetic',
    'src0-smoke',
    'pipeline smoke',
}

NON_FIELD_SCRATCH_EXACT_PARTS = {'checks', 'releases'}
NON_FIELD_SCRATCH_PREFIXES = ('check-', 'smoke-', 'test-', 'fixture-')


def non_field_scratch_lane_block(path: Path, *, archive_root: Path) -> str | None:
    """Return why an archive-local path is in a non-field scratch lane.

    Field inputs may be external to the archive or deliberately staged under the
    live field lane. Validator fixtures and release-packaging scratch can look
    like plausible local files, so this helper blocks them before they become a
    returned-owner CSV or provenance source.
    """
    inside, parts = archive_relative(path.resolve(), archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return None
    if len(parts) == 1:
        return 'scratch-root-without-field-lane'
    for part in parts[1:]:
        if part in NON_FIELD_SCRATCH_EXACT_PARTS:
            return f'non-field-scratch-lane:{part}'
        if part.startswith(NON_FIELD_SCRATCH_PREFIXES):
            return f'non-field-scratch-fixture:{part}'
    if parts[1] != 'field':
        return f'legacy-scratch-lane:{parts[1]}'
    if len(parts) >= 3 and parts[2] != 'ft0181':
        return f'non-ft0181-field-lane:{parts[2]}'
    return None


def field_scratch_lane_error(path: Path, *, archive_root: Path, field_name: str) -> str | None:
    """Return an error when a source artifact is outside the live FT-0181 field lane.

    External returned CSV/source-packet inputs have separate guards. Once an
    artifact is part of the local FT-0181 source chain, direct CLI references and
    embedded provenance references must stay under scratch/field/ft0181/. This
    prevents checker, release, legacy, smoke, test, or fixture scratch from
    becoming a plausible source for a later field action.
    """
    inside, parts = archive_relative(path.resolve(), archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return f'{field_name} must resolve under archive scratch/'
    lane_block = non_field_scratch_lane_block(path.resolve(), archive_root=archive_root)
    if lane_block:
        return f'{field_name} must resolve under scratch/field/ft0181/ ({lane_block})'
    return None

EXPECTED_OWNER_PACKET_FIELDS = {
    'followthrough_id': 'FT-0181',
    'packet_state': 'PREPARED_NOT_SENT',
    'evidence_state': 'NO-OWNER-PACKET-YET',
    'source_truth_class': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
}


def owner_request_packet_integrity_error(manifest: dict) -> str | None:
    """Return why a local owner-request packet manifest cannot drive routing.

    The field router should only turn a generated packet into a SENT clock when
    the packet still has the exact non-evidence, not-sent boundary written by
    the packet-prep tool. A hand-edited manifest that claims sent, evidence,
    closure, or another followthrough may be useful for debugging, but it must
    not become the next executable FT-0181 field action.
    """
    if not isinstance(manifest, dict):
        return 'manifest is not an object'
    for key, expected in EXPECTED_OWNER_PACKET_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    generated = manifest.get('generated_files')
    if not isinstance(generated, list) or 'AIEDU-SR-003-eight-row-owner-reply-template.csv' not in generated:
        return 'generated_files missing owner reply template'
    requested = manifest.get('requested_return_date')
    if requested is not None:
        if not isinstance(requested, str):
            return f'requested_return_date={requested!r} is not a string'
        requested_error = _parse_iso_date(requested, 'requested_return_date')
        if requested_error:
            return requested_error
    created = manifest.get('created_at_utc')
    if not isinstance(created, str) or not created.endswith('Z'):
        return f'created_at_utc={created!r} must be a UTC timestamp ending in Z'
    try:
        datetime.fromisoformat(created[:-1] + '+00:00').astimezone(timezone.utc)
    except ValueError:
        return f'created_at_utc={created!r} is not parseable as an ISO UTC timestamp'
    operator_local = manifest.get('operator_local_date')
    if operator_local is not None:
        error = _parse_iso_date(operator_local, 'operator_local_date')
        if error:
            return error
    return None


FIRST_CONTACT_MAX_DAYS = 7
REASK_MAX_DAYS = 3

EXPECTED_OWNER_SEND_LOG_FIELDS = {
    'send_log_type': 'FT-0181-owner-send-log',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'evidence_state': 'not_evidence',
    'source_truth_class': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'contact_status_effect': 'may_source_sent_awaiting_reply_clock_only',
}


def _parse_iso_date(value: object, field: str) -> str | None:
    if not isinstance(value, str) or not value:
        return f'{field}={value!r} must be a YYYY-MM-DD string'
    try:
        date.fromisoformat(value)
    except ValueError:
        return f'{field}={value!r} is not parseable as YYYY-MM-DD'
    return None




def _date_value(value: object) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None

def _parse_utc_timestamp(value: object, field: str) -> str | None:
    if not isinstance(value, str) or not value.endswith('Z'):
        return f'{field}={value!r} must be a UTC timestamp ending in Z'
    try:
        datetime.fromisoformat(value[:-1] + '+00:00').astimezone(timezone.utc)
    except ValueError:
        return f'{field}={value!r} is not parseable as an ISO UTC timestamp'
    return None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def owner_send_log_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a local owner-send log cannot source a SENT contact clock.

    The send log is still local non-evidence, but it closes the rev0271 gap where
    a packet manifest could source a SENT clock before any separate operator send
    artifact existed. The log must be scratch-local, point back to a valid packet
    manifest, and carry only route-class metadata rather than contact details.
    """
    if not isinstance(manifest, dict):
        return 'send log is not an object'
    for key, expected in EXPECTED_OWNER_SEND_LOG_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('send_log_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'send_log_version={version!r} must name the release revision'
    for field in ['sent_date', 'response_due_date']:
        error = _parse_iso_date(manifest.get(field), field)
        if error:
            return error
    sent = date.fromisoformat(manifest['sent_date'])
    due = date.fromisoformat(manifest['response_due_date'])
    if due < sent:
        return 'response_due_date cannot precede sent_date'
    if (due - sent).days > FIRST_CONTACT_MAX_DAYS:
        return f'response_due_date cannot be more than {FIRST_CONTACT_MAX_DAYS} days after sent_date'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-sent-bounded-owner-request':
        return 'operator_confirmation must be human-sent-bounded-owner-request'
    if manifest.get('no_contact_details_stored') is not True:
        return 'no_contact_details_stored must be true'
    if manifest.get('no_raw_or_protected_material_stored') is not True:
        return 'no_raw_or_protected_material_stored must be true'
    if manifest.get('no_widening_confirmation') is not True:
        return 'no_widening_confirmation must be true'
    if manifest.get('max_response_clock_days') != FIRST_CONTACT_MAX_DAYS:
        return f'max_response_clock_days must be {FIRST_CONTACT_MAX_DAYS}'
    if not isinstance(manifest.get('send_channel_class'), str) or not manifest['send_channel_class']:
        return 'send_channel_class must be a non-empty class label'
    if not isinstance(manifest.get('owner_route_class'), str) or not manifest['owner_route_class']:
        return 'owner_route_class must be a non-empty class label'
    ref = manifest.get('packet_manifest_ref')
    if not isinstance(ref, str) or not ref:
        return 'packet_manifest_ref must be a non-empty archive-relative path'
    packet_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(packet_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'packet_manifest_ref must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(packet_path, archive_root=archive_root, field_name='packet_manifest_ref')
    if lane_error:
        return lane_error
    if packet_path.name != 'packet-manifest.json' or not packet_path.exists() or not packet_path.is_file():
        return 'packet_manifest_ref must point to an existing packet-manifest.json file'
    try:
        packet_data = json.loads(packet_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'packet_manifest_ref is not readable JSON'
    packet_error = owner_request_packet_integrity_error(packet_data)
    if packet_error:
        return f'packet_manifest_ref failed packet integrity: {packet_error}'
    requested = packet_data.get('requested_return_date')
    if isinstance(requested, str) and requested:
        requested_error = _parse_iso_date(requested, 'packet requested_return_date')
        if requested_error:
            return requested_error
    return None




EXPECTED_OWNER_ROUTE_BLOCK_FIELDS = {
    'route_block_type': 'FT-0181-owner-route-block',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'block_state': 'ROUTE_BLOCKED_NO_SEND',
    'evidence_state': 'not_evidence',
    'source_truth_class': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'contact_status_effect': 'does_not_create_sent_or_reask_clock',
}
OWNER_ROUTE_BLOCK_CLASSES = {
    'no-accountable-owner-route',
    'owner-route-ambiguous',
    'owner-route-requires-authorization',
    'owner-route-wrong-domain',
    'owner-route-unavailable',
}


def owner_route_block_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a local route-block record cannot halt packet routing.

    A route block is intentionally weaker than a send log: it does not create a
    contact clock. It only prevents the archive from treating an unsent packet as
    field progress when no accountable owner route exists.
    """
    if not isinstance(manifest, dict):
        return 'route block is not an object'
    for key, expected in EXPECTED_OWNER_ROUTE_BLOCK_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('route_block_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'route_block_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    error = _parse_iso_date(manifest.get('block_date'), 'block_date')
    if error:
        return error
    if manifest.get('block_class') not in OWNER_ROUTE_BLOCK_CLASSES:
        return f'block_class={manifest.get("block_class")!r} is not allowed'
    if manifest.get('operator_confirmation') != 'human-confirmed-owner-route-block-no-send':
        return 'operator_confirmation must be human-confirmed-owner-route-block-no-send'
    for field in [
        'source_packet_verified',
        'no_owner_contact_made',
        'no_send_log_created',
        'no_contact_details_stored',
        'no_raw_or_protected_material_stored',
        'no_widening_confirmation',
    ]:
        if manifest.get(field) is not True:
            return f'{field} must be true'
    ref = manifest.get('packet_manifest_ref')
    if not isinstance(ref, str) or not ref:
        return 'packet_manifest_ref must be a non-empty archive-relative path'
    packet_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(packet_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'packet_manifest_ref must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(packet_path, archive_root=archive_root, field_name='packet_manifest_ref')
    if lane_error:
        return lane_error
    if packet_path.name != 'packet-manifest.json' or not packet_path.exists() or not packet_path.is_file():
        return 'packet_manifest_ref must point to an existing packet-manifest.json file'
    try:
        packet_data = json.loads(packet_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'packet_manifest_ref is not readable JSON'
    packet_error = owner_request_packet_integrity_error(packet_data)
    if packet_error:
        return f'packet_manifest_ref failed packet integrity: {packet_error}'
    packet_requested = packet_data.get('requested_return_date')
    if packet_requested != manifest.get('packet_requested_return_date'):
        return 'packet_requested_return_date must match referenced packet manifest'
    block_date = date.fromisoformat(manifest['block_date'])
    packet_created_date = packet_creation_field_date(packet_data)
    if packet_created_date is not None and block_date < packet_created_date:
        return 'block_date cannot precede referenced packet operator-local creation date'
    allowed = manifest.get('allowed_next_commands')
    if not isinstance(allowed, list) or not any('owner-field-next' in str(item) for item in allowed):
        return 'allowed_next_commands must route back through owner-field-next'
    forbidden = manifest.get('forbidden_actions')
    if not isinstance(forbidden, list) or 'record_send_log_without_human_send' not in forbidden:
        return 'forbidden_actions must block send-log recording without a human send'
    return None

EXPECTED_OWNER_CONTACT_STATUS_FIELDS = {
    'status_id': 'AIEDU-SR-003-OWNER-CONTACT-STATUS',
    'followthrough_id': 'FT-0181',
    'evidence_state': 'not_evidence',
    'source_truth_class': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
}
ACTIVE_OWNER_REPLY_SOURCE_STATUSES = {
    'SENT_AWAITING_REPLY': (1, FIRST_CONTACT_MAX_DAYS),
    'REASK_AWAITING_REPLY': (2, REASK_MAX_DAYS),
}


def _load_json_object(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _contact_status_source_anchor_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Re-read the artifact that created a contact clock before intake uses it.

    Contact-status JSON is an easy handoff target: many later tools only need a
    clock saying "a bounded owner route is awaiting a reply." Without re-reading
    the referenced send/reask log, a copied or hand-edited status could preserve
    plausible metadata while the actual source artifact is missing, stale, or from
    the wrong lane. This helper keeps the contact clock non-evidence, but anchors
    it back to the local send/reask artifact that created it.
    """
    source_ref = manifest.get('source_artifact_ref')
    if not isinstance(source_ref, str) or not source_ref:
        return 'source_artifact_ref must be a non-empty archive-relative scratch reference'
    source_path = (archive_root / source_ref).resolve()
    inside, parts = archive_relative(source_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_artifact_ref must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(source_path, archive_root=archive_root, field_name='source_artifact_ref')
    if lane_error:
        return lane_error
    if not source_path.exists() or not source_path.is_file():
        return 'source_artifact_ref must point to an existing source artifact file'
    source_data = _load_json_object(source_path)
    if source_data is None:
        return 'source_artifact_ref is not readable JSON'

    status = manifest.get('contact_status')
    expected_type = 'send-log' if status == 'SENT_AWAITING_REPLY' else 'reask-log'
    if manifest.get('source_artifact_type') != expected_type:
        return f'source_artifact_type must be {expected_type!r} for {status}'

    if status == 'SENT_AWAITING_REPLY':
        if source_path.name != 'send-log.json':
            return 'SENT_AWAITING_REPLY source_artifact_ref must end with send-log.json'
        source_error = owner_send_log_integrity_error(source_data, archive_root=archive_root)
        if source_error:
            return 'source send-log failed integrity: ' + source_error
    elif status == 'REASK_AWAITING_REPLY':
        if source_path.name != 'reask-log.json':
            return 'REASK_AWAITING_REPLY source_artifact_ref must end with reask-log.json'
        source_error = owner_reask_log_integrity_error(source_data, archive_root=archive_root)
        if source_error:
            return 'source reask-log failed integrity: ' + source_error
    else:
        return f'contact_status={status!r} cannot source returned-CSV intake; expected active sent or reask clock'

    for key in ['sent_date', 'response_due_date']:
        if manifest.get(key) != source_data.get(key):
            return f'{key} must match referenced {source_path.name}'
    if manifest.get('source_artifact_verification') not in {None, '', f'verified local owner-{expected_type.replace("-", " ")}'}:
        # Older local status records may not carry this exact phrase, so this is
        # deliberately informational-only: the source hash/date/type checks above
        # are the authority.
        pass
    return None


def owner_contact_status_integrity_error(manifest: dict, *, archive_root: Path | None = None) -> str | None:
    """Return why a contact-status clock cannot source returned-CSV intake.

    A plausible returned owner CSV should be tied to the local bounded contact
    clock that created the opportunity for a reply. When ``archive_root`` is
    provided, the clock is also anchored back to the send-log/reask-log JSON that
    created it, so copied or stale contact metadata cannot launder owner CSV
    intake. A valid status remains non-evidence and still cannot close FT-0181 or
    support public claims.
    """
    if not isinstance(manifest, dict):
        return 'contact status is not an object'
    for key, expected in EXPECTED_OWNER_CONTACT_STATUS_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    status = manifest.get('contact_status')
    if status not in ACTIVE_OWNER_REPLY_SOURCE_STATUSES:
        return f'contact_status={status!r} cannot source returned-CSV intake; expected active sent or reask clock'
    expected_attempt, max_days = ACTIVE_OWNER_REPLY_SOURCE_STATUSES[status]
    for field in ['sent_date', 'response_due_date', 'status_date']:
        error = _parse_iso_date(manifest.get(field), field)
        if error:
            return error
    sent = date.fromisoformat(manifest['sent_date'])
    due = date.fromisoformat(manifest['response_due_date'])
    recorded = date.fromisoformat(manifest['status_date'])
    if due < sent:
        return 'response_due_date cannot precede sent_date'
    if recorded < sent:
        return 'status_date cannot precede sent_date'
    if (due - sent).days > max_days:
        return f'{status} response clock cannot exceed {max_days} days'
    try:
        attempt_count = int(manifest.get('attempt_count'))
    except (TypeError, ValueError):
        return 'attempt_count must be numeric'
    if attempt_count != expected_attempt:
        return f'attempt_count={attempt_count!r} (expected {expected_attempt} for {status})'
    if manifest.get('max_response_clock_days') != max_days:
        return f'max_response_clock_days must be {max_days}'
    if manifest.get('source_artifact_verified') is not True:
        return 'source_artifact_verified must be true'
    if manifest.get('no_widening_confirmation') is not True:
        return 'no_widening_confirmation must be true'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    source_ref = manifest.get('source_artifact_ref')
    if not isinstance(source_ref, str) or not source_ref:
        return 'source_artifact_ref must be a non-empty trace reference'
    if archive_root is not None:
        anchor_error = _contact_status_source_anchor_error(manifest, archive_root=archive_root)
        if anchor_error:
            return anchor_error
    return None



EXPECTED_WORKBENCH_SEED_FIELDS = {
    'seed_type': 'FT-0181-owner-packet-workbench-seed',
    'source_truth_status': 'UNVERIFIED_OWNER_REPLY_PENDING_CUSTODY',
    'acceptance_state': 'NOT_ACCEPTED',
    'required_next_surface': 'docs/30-operations/ft0181-owner-packet-workbench.md',
    'ft0181_status': 'live',
}


def owner_workbench_seed_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a workbench seed cannot source manual workbench review.

    Rev0274 closes the one-step-later bypass after returned-CSV intake: a seed
    must preserve and revalidate the active contact-status clock from the intake
    bundle before it can route a maintainer to manual workbench review. The seed
    remains non-evidence and NOT_ACCEPTED even when this check passes.
    """
    if not isinstance(manifest, dict):
        return 'workbench seed is not an object'
    for key, expected in EXPECTED_WORKBENCH_SEED_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('seed_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'seed_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_proceed_staged_row_text', 'copies_contact_details']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    contact_revalidated = content.get('source_contact_status_revalidated') is True
    context_revalidated = content.get('source_post_readout_context_receipt_revalidated') is True
    if contact_revalidated == context_revalidated:
        return 'content_minimization must revalidate exactly one source provenance: source_contact_status or source_post_readout_context_receipt'
    if content.get('contains_hashes_and_next_steps_only') is not True:
        return 'content_minimization.contains_hashes_and_next_steps_only must be true'
    ceiling = manifest.get('claim_ceiling')
    if not isinstance(ceiling, str) or 'not SRC2+ acceptance' not in ceiling or 'not closure evidence' not in ceiling:
        return 'claim_ceiling must preserve not-SRC2+ and not-closure boundaries'

    if contact_revalidated:
        source = manifest.get('source_contact_status')
        if not isinstance(source, dict):
            return 'source_contact_status must be present in the seed'
        ref = source.get('reference')
        if not isinstance(ref, str) or not ref:
            return 'source_contact_status.reference must be a non-empty archive-relative path'
        status_path = (archive_root / ref).resolve()
        inside, parts = archive_relative(status_path, archive_root=archive_root)
        if not inside or not parts or parts[0] != 'scratch':
            return 'source_contact_status.reference must resolve under archive scratch/'
        lane_error = field_scratch_lane_error(status_path, archive_root=archive_root, field_name='source_contact_status.reference')
        if lane_error:
            return lane_error
        if status_path.name != 'contact-status.json' or not status_path.exists() or not status_path.is_file():
            return 'source_contact_status.reference must point to an existing contact-status.json file'
        try:
            status_data = json.loads(status_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return 'source_contact_status.reference is not readable JSON'
        status_error = owner_contact_status_integrity_error(status_data, archive_root=archive_root)
        if status_error:
            return 'source_contact_status failed contact-status integrity: ' + status_error
        for key in ['contact_status', 'sent_date', 'response_due_date', 'status_date', 'attempt_count', 'evidence_state']:
            if source.get(key) != status_data.get(key):
                return f'source_contact_status.{key} does not match referenced contact-status.json'
        if source.get('claim_effect') != 'none; provenance gate only':
            return 'source_contact_status.claim_effect must remain provenance-only'
        if manifest.get('source_post_readout_context_receipt') is not None:
            return 'source_post_readout_context_receipt must be null when source_contact_status is revalidated'
    else:
        source = manifest.get('source_post_readout_context_receipt')
        if not isinstance(source, dict):
            return 'source_post_readout_context_receipt must be present in the seed'
        ref = source.get('reference')
        if not isinstance(ref, str) or not ref:
            return 'source_post_readout_context_receipt.reference must be a non-empty archive-relative path'
        receipt_path = (archive_root / ref).resolve()
        inside, parts = archive_relative(receipt_path, archive_root=archive_root)
        if not inside or not parts or parts[0] != 'scratch':
            return 'source_post_readout_context_receipt.reference must resolve under archive scratch/'
        lane_error = field_scratch_lane_error(receipt_path, archive_root=archive_root, field_name='source_post_readout_context_receipt.reference')
        if lane_error:
            return lane_error
        if receipt_path.name != 'post-readout-context-receipt.json' or not receipt_path.exists() or not receipt_path.is_file():
            return 'source_post_readout_context_receipt.reference must point to an existing post-readout-context-receipt.json file'
        try:
            receipt_data = json.loads(receipt_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return 'source_post_readout_context_receipt.reference is not readable JSON'
        receipt_error = owner_post_readout_context_receipt_integrity_error(receipt_data, archive_root=archive_root)
        if receipt_error:
            return 'source_post_readout_context_receipt failed post-readout context receipt integrity: ' + receipt_error
        for key in ['receipt_state', 'source_truth_class', 'evidence_state']:
            if source.get(key) != receipt_data.get(key):
                return f'source_post_readout_context_receipt.{key} does not match referenced post-readout-context-receipt.json'
        if source.get('source_csv_sha256') != manifest.get('source_csv', {}).get('sha256'):
            return 'source_post_readout_context_receipt.source_csv_sha256 must match source_csv.sha256'
        if source.get('claim_effect') != 'none; post-readout provenance gate only':
            return 'source_post_readout_context_receipt.claim_effect must remain post-readout provenance-only'
        if source.get('revalidated_for_seed') is not True:
            return 'source_post_readout_context_receipt.revalidated_for_seed must be true'
        if manifest.get('source_contact_status') is not None:
            return 'source_contact_status must be null when source_post_readout_context_receipt is revalidated'
    return None


EXPECTED_WORKBENCH_REVIEW_BRIEF_FIELDS = {
    'brief_type': 'FT-0181-workbench-review-brief',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'brief_state': 'REVIEW_BRIEF_PREPARED_NOT_REVIEWED',
    'acceptance_state': 'NOT_ACCEPTED',
    'review_effect': 'does_not_record_review',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'required_next_surface': 'docs/30-operations/ft0181-workbench-review-record.md',
    'ft0181_status': 'live',
}


def owner_workbench_review_brief_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a review brief cannot route to human workbench review.

    A brief is an execution bridge from a NOT_ACCEPTED seed to a human-entered
    workbench-review command. It must remain scratch-local and non-evidence; it
    can only prepare command skeletons and cannot record review, acceptance,
    custody, public claims, lifecycle movement, or closure.
    """
    if not isinstance(manifest, dict):
        return 'workbench review brief is not an object'
    for key, expected in EXPECTED_WORKBENCH_REVIEW_BRIEF_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('brief_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'brief_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    ceiling = manifest.get('claim_ceiling')
    if not isinstance(ceiling, str) or 'not a human review' not in ceiling or 'not SRC2+ acceptance' not in ceiling or 'not closure evidence' not in ceiling:
        return 'claim_ceiling must preserve not-review, not-SRC2+, and not-closure boundaries'

    source_seed = manifest.get('source_seed')
    if not isinstance(source_seed, dict):
        return 'source_seed must be an object'
    ref = source_seed.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_seed.reference must be a non-empty archive-relative scratch path'
    seed_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(seed_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_seed.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(seed_path, archive_root=archive_root, field_name='source_seed.reference')
    if lane_error:
        return lane_error
    if seed_path.name != 'workbench-seed.json' or not seed_path.exists() or not seed_path.is_file():
        return 'source_seed.reference must point to an existing workbench-seed.json file'
    try:
        seed_data = json.loads(seed_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_seed.reference is not readable JSON'
    seed_error = owner_workbench_seed_integrity_error(seed_data, archive_root=archive_root)
    if seed_error:
        return 'source_seed failed workbench-seed integrity: ' + seed_error
    seed_sha = source_seed.get('seed_sha256')
    if not isinstance(seed_sha, str) or not seed_sha:
        return 'source_seed.seed_sha256 must be recorded'
    if seed_sha != _sha256_file(seed_path):
        return 'source_seed.seed_sha256 does not match referenced workbench-seed.json'
    if source_seed.get('acceptance_state') != seed_data.get('acceptance_state'):
        return 'source_seed.acceptance_state does not match referenced workbench seed'
    if source_seed.get('source_truth_status') != seed_data.get('source_truth_status'):
        return 'source_seed.source_truth_status does not match referenced workbench seed'
    if source_seed.get('triage_outcome') != seed_data.get('triage_outcome'):
        return 'source_seed.triage_outcome does not match referenced workbench seed'

    commands = manifest.get('bounded_review_command_templates')
    if not isinstance(commands, dict) or not commands:
        return 'bounded_review_command_templates must be a non-empty object'
    required = {
        'proceed_decision_board': 'DECISION=proceed-decision-board',
        'reask_owner': 'DECISION=reask-owner',
        'block_overbroad': 'DECISION=block-overbroad',
        'block_protected': 'DECISION=block-protected',
        'block_security': 'DECISION=block-security',
        'block_evidence': 'DECISION=block-evidence',
        'no_change_trim': 'DECISION=no-change-trim',
    }
    for key, decision_token in required.items():
        command = commands.get(key)
        if not isinstance(command, str) or not command.startswith('make owner-workbench-review '):
            return f'bounded_review_command_templates.{key} must be an owner-workbench-review command'
        if decision_token not in command:
            return f'bounded_review_command_templates.{key} missing {decision_token}'
        if f'SEED={ref}' not in command and f"SEED='{ref}'" not in command:
            return f'bounded_review_command_templates.{key} must reference the source seed'
        if 'CONFIRM=human-reviewed-minimized-workbench-record' not in command:
            return f'bounded_review_command_templates.{key} must carry workbench review confirmation token'
        lowered = command.lower()
        for forbidden in ['student id', 'learner id', 'student name', 'email address', '@', 'screenshot', 'api key', 'credential']:
            if forbidden in lowered:
                return f'bounded_review_command_templates.{key} includes forbidden raw/contact term: {forbidden}'

    routes = manifest.get('allowed_decision_routes')
    if not isinstance(routes, list) or sorted(routes) != sorted([
        'proceed-decision-board',
        'reask-owner',
        'block-overbroad',
        'block-protected',
        'block-security',
        'block-evidence',
        'no-change-trim',
    ]):
        return 'allowed_decision_routes must enumerate the bounded workbench-review routes'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_proceed_staged_row_text', 'copies_contact_details', 'copies_learner_identifiers_or_protected_facts']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('source_seed_revalidated') is not True:
        return 'content_minimization.source_seed_revalidated must be true'
    if content.get('contains_hashes_counts_and_command_skeletons_only') is not True:
        return 'content_minimization.contains_hashes_counts_and_command_skeletons_only must be true'
    forbidden_effects = manifest.get('forbidden_effects')
    if not isinstance(forbidden_effects, list) or 'human-review-automation' not in forbidden_effects or 'lifecycle-or-closure' not in forbidden_effects:
        return 'forbidden_effects must block review automation and lifecycle/closure effects'
    return None


EXPECTED_FIRST_PACKET_DECISION_BRIEF_FIELDS = {
    'brief_type': 'FT-0181-first-packet-decision-brief',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'brief_state': 'DECISION_BRIEF_PREPARED_NOT_RECORDED',
    'acceptance_state': 'NOT_ACCEPTED',
    'decision_effect': 'does_not_record_decision',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'required_next_surface': 'docs/30-operations/ft0181-first-packet-decision-board.md',
    'ft0181_status': 'live',
}


def owner_first_packet_decision_brief_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a first-packet decision brief cannot route board work.

    A decision brief is an execution bridge from a PROCEED workbench review to a
    human-entered first-packet decision command. It must remain scratch-local and
    non-evidence; it can only prepare command skeletons and cannot record the
    board, open a change ticket, accept evidence, create custody, mutate service
    records, support public claims, activate a live window, or close FT-0181.
    """
    if not isinstance(manifest, dict):
        return 'first-packet decision brief is not an object'
    for key, expected in EXPECTED_FIRST_PACKET_DECISION_BRIEF_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('brief_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'brief_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    ceiling = manifest.get('claim_ceiling')
    if not isinstance(ceiling, str) or 'not a decision-board record' not in ceiling or 'not SRC2+ acceptance' not in ceiling or 'not closure evidence' not in ceiling:
        return 'claim_ceiling must preserve not-decision, not-SRC2+, and not-closure boundaries'

    source = manifest.get('source_workbench_review')
    if not isinstance(source, dict):
        return 'source_workbench_review must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_workbench_review.reference must be a non-empty archive-relative scratch path'
    review_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(review_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_workbench_review.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(review_path, archive_root=archive_root, field_name='source_workbench_review.reference')
    if lane_error:
        return lane_error
    if review_path.name != 'workbench-review.json' or not review_path.exists() or not review_path.is_file():
        return 'source_workbench_review.reference must point to an existing workbench-review.json file'
    try:
        review_data = json.loads(review_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_workbench_review.reference is not readable JSON'
    review_error = owner_workbench_review_integrity_error(review_data, archive_root=archive_root)
    if review_error:
        return 'source_workbench_review failed workbench-review integrity: ' + review_error
    if review_data.get('decision') != 'PROCEED-DECISION-BOARD':
        return 'source_workbench_review.decision must be PROCEED-DECISION-BOARD'
    review_sha = source.get('review_sha256')
    if not isinstance(review_sha, str) or not review_sha:
        return 'source_workbench_review.review_sha256 must be recorded'
    if review_sha != _sha256_file(review_path):
        return 'source_workbench_review.review_sha256 does not match referenced workbench-review.json'
    for key in ['decision', 'review_state', 'acceptance_state', 'source_truth_class', 'reviewer_role_count']:
        if source.get(key) != review_data.get(key):
            return f'source_workbench_review.{key} does not match referenced workbench-review.json'
    counts = source.get('field_counts')
    if not isinstance(counts, dict):
        return 'source_workbench_review.field_counts must be an object'
    review_counts = review_data.get('field_counts') if isinstance(review_data.get('field_counts'), dict) else {}
    for key in ['surviving_field_count', 'decision_changed_count', 'local_only_field_count', 'trimmed_field_count', 'reask_field_count']:
        if counts.get(key) != review_counts.get(key):
            return f'source_workbench_review.field_counts.{key} does not match referenced workbench review'
    if source.get('revalidated_for_decision_brief') is not True:
        return 'source_workbench_review.revalidated_for_decision_brief must be true'

    commands = manifest.get('bounded_decision_command_templates')
    if not isinstance(commands, dict) or not commands:
        return 'bounded_decision_command_templates must be a non-empty object'
    required = {
        'conservative_watch': ('AUTHORITY_ACTION=keep-lower-ceiling', 'LIFECYCLE_ACTION=watch'),
        'sandbox_adjustment': ('CONSTRUCT_ACTION=add-stop-trigger', 'LIFECYCLE_ACTION=sandbox'),
        'suppress_or_quarantine': ('EVIDENCE_ACTION=suppress', 'LIFECYCLE_ACTION=quarantine'),
        'pilot_with_expiry_candidate': ('EVIDENCE_ACTION=stage-claim-with-expiry', 'LIFECYCLE_ACTION=pilot'),
        'no_public_change_watch': ('AUTHORITY_ACTION=no-change', 'CHANGED_SLICE_COUNT=4'),
    }
    for key, tokens in required.items():
        command = commands.get(key)
        if not isinstance(command, str) or not command.startswith('make owner-first-packet-decision '):
            return f'bounded_decision_command_templates.{key} must be an owner-first-packet-decision command'
        if f'REVIEW={ref}' not in command and f"REVIEW='{ref}'" not in command:
            return f'bounded_decision_command_templates.{key} must reference the source review'
        for token in tokens:
            if token not in command:
                return f'bounded_decision_command_templates.{key} missing {token}'
        if 'CONFIRM=human-recorded-five-slice-decision-board' not in command:
            return f'bounded_decision_command_templates.{key} must carry first-packet decision confirmation token'
        lowered = command.lower()
        for forbidden in ['student id', 'learner id', 'student name', 'email address', '@', 'screenshot', 'api key', 'credential', 'claim text']:
            if forbidden in lowered:
                return f'bounded_decision_command_templates.{key} includes forbidden raw/contact/claim term: {forbidden}'

    allowed = manifest.get('allowed_slice_actions')
    if not isinstance(allowed, dict):
        return 'allowed_slice_actions must be an object'
    expected_actions = {
        'authority_action': FIRST_PACKET_AUTHORITY_ACTIONS,
        'evidence_action': FIRST_PACKET_EVIDENCE_ACTIONS,
        'construct_action': FIRST_PACKET_CONSTRUCT_ACTIONS,
        'public_action': FIRST_PACKET_PUBLIC_ACTIONS,
        'lifecycle_action': FIRST_PACKET_LIFECYCLE_ACTIONS,
    }
    for key, expected in expected_actions.items():
        values = allowed.get(key)
        if not isinstance(values, list) or set(values) != set(expected):
            return f'allowed_slice_actions.{key} must enumerate the bounded slice actions'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_workbench_review_text', 'copies_contact_details', 'copies_learner_identifiers_or_protected_facts']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('source_workbench_review_revalidated') is not True:
        return 'content_minimization.source_workbench_review_revalidated must be true'
    if content.get('contains_hashes_counts_and_command_skeletons_only') is not True:
        return 'content_minimization.contains_hashes_counts_and_command_skeletons_only must be true'
    forbidden_effects = manifest.get('forbidden_effects')
    if not isinstance(forbidden_effects, list) or 'decision-board-automation' not in forbidden_effects or 'lifecycle-or-closure' not in forbidden_effects:
        return 'forbidden_effects must block decision automation and lifecycle/closure effects'
    return None


EXPECTED_POST_DECISION_CHANGE_TICKET_BRIEF_FIELDS = {
    'brief_type': 'FT-0181-post-decision-change-ticket-brief',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'brief_state': 'CHANGE_TICKET_BRIEF_PREPARED_NOT_RECORDED',
    'acceptance_state': 'NOT_ACCEPTED',
    'ticket_effect': 'does_not_record_change_ticket',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'required_next_surface': 'docs/30-operations/ft0181-post-decision-change-ticket.md',
    'ft0181_status': 'live',
}


def owner_post_decision_change_ticket_brief_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a change-ticket brief cannot route post-decision work.

    A change-ticket brief is an execution bridge from a valid first-packet
    decision to a human-entered post-decision change-ticket command. It must
    remain scratch-local and non-evidence; it can only prepare command skeletons
    and cannot record a ticket, create an activation receipt, accept evidence,
    create custody, mutate service records, support public claims, activate a
    live window, move lifecycle state, or close FT-0181.
    """
    if not isinstance(manifest, dict):
        return 'activation/live-window entry brief is not an object'
    for key, expected in EXPECTED_POST_DECISION_CHANGE_TICKET_BRIEF_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('brief_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'brief_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    ceiling = manifest.get('claim_ceiling')
    if not isinstance(ceiling, str) or 'not a change-ticket record' not in ceiling or 'not SRC2+ acceptance' not in ceiling or 'not closure evidence' not in ceiling:
        return 'claim_ceiling must preserve not-ticket, not-SRC2+, and not-closure boundaries'

    source = manifest.get('source_first_packet_decision')
    if not isinstance(source, dict):
        return 'source_first_packet_decision must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_first_packet_decision.reference must be a non-empty archive-relative scratch path'
    decision_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(decision_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_first_packet_decision.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(decision_path, archive_root=archive_root, field_name='source_first_packet_decision.reference')
    if lane_error:
        return lane_error
    if decision_path.name != 'first-packet-decision.json' or not decision_path.exists() or not decision_path.is_file():
        return 'source_first_packet_decision.reference must point to an existing first-packet-decision.json file'
    try:
        decision_data = json.loads(decision_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_first_packet_decision.reference is not readable JSON'
    decision_error = owner_first_packet_decision_integrity_error(decision_data, archive_root=archive_root)
    if decision_error:
        return 'source_first_packet_decision failed first-packet-decision integrity: ' + decision_error
    decision_sha = source.get('decision_sha256')
    if not isinstance(decision_sha, str) or not decision_sha:
        return 'source_first_packet_decision.decision_sha256 must be recorded'
    if decision_sha != _sha256_file(decision_path):
        return 'source_first_packet_decision.decision_sha256 does not match referenced first-packet-decision.json'
    for key in ['board_state', 'acceptance_state', 'evidence_state', 'changed_slice_count', 'rollback_owner_role_count', 'decision_slices']:
        if source.get(key) != decision_data.get(key):
            return f'source_first_packet_decision.{key} does not match referenced first-packet-decision.json'
    expected_source_truth = decision_data.get('source_workbench_review', {}).get('source_truth_class')
    if source.get('source_truth_class') != expected_source_truth:
        return 'source_first_packet_decision.source_truth_class does not match referenced first-packet-decision.json'
    if source.get('change_ticket_effect') != 'may_source_post_decision_change_ticket_only':
        return 'source_first_packet_decision.change_ticket_effect must preserve post-decision ticket routing only'
    if source.get('revalidated_for_ticket_brief') is not True:
        return 'source_first_packet_decision.revalidated_for_ticket_brief must be true'

    commands = manifest.get('bounded_change_ticket_command_templates')
    if not isinstance(commands, dict) or not commands:
        return 'bounded_change_ticket_command_templates must be a non-empty object'
    required = {
        'ready_for_real_packet_sandbox': ('TICKET_STATE=ready-for-real-packet', 'CHANGE_CLASS=pct-c-sandbox-adjustment', 'SOURCE_TRUTH_REQUIRED=SRC2', 'LIVE_WINDOW_REQUIRED=1'),
        'ready_for_real_packet_trim': ('TICKET_STATE=ready-for-real-packet', 'CHANGE_CLASS=pct-a-trim', 'SOURCE_TRUTH_REQUIRED=SRC2', 'LIVE_WINDOW_REQUIRED=1'),
        'blocked_no_real_packet': ('TICKET_STATE=blocked-no-real-packet', 'CHANGE_CLASS=pct-b-suppress', 'SOURCE_TRUTH_REQUIRED=not_evidence'),
        'quarantine': ('TICKET_STATE=quarantined', 'CHANGE_CLASS=pct-x-quarantine', 'SOURCE_TRUTH_REQUIRED=not_evidence'),
        'active_change_after_activation_receipt_only': ('TICKET_STATE=active-change', 'ACTIVATION_RECEIPT=<scratch/.../activation-receipt.json>', 'LIVE_WINDOW_REQUIRED=1'),
    }
    for key, tokens in required.items():
        command = commands.get(key)
        if not isinstance(command, str) or not command.startswith('make owner-post-decision-change-ticket '):
            return f'bounded_change_ticket_command_templates.{key} must be an owner-post-decision-change-ticket command'
        if f'DECISION={ref}' not in command and f"DECISION='{ref}'" not in command:
            return f'bounded_change_ticket_command_templates.{key} must reference the source first-packet decision'
        for token in tokens:
            if token not in command:
                return f'bounded_change_ticket_command_templates.{key} missing {token}'
        if 'CONFIRM=human-recorded-bounded-post-decision-change-ticket' not in command:
            return f'bounded_change_ticket_command_templates.{key} must carry post-decision change-ticket confirmation token'
        if key != 'active_change_after_activation_receipt_only' and 'ACTIVATION_RECEIPT=' in command:
            return f'bounded_change_ticket_command_templates.{key} must not jump to active-change activation receipt'
        lowered = command.lower()
        for forbidden in ['student id', 'learner id', 'student name', 'email address', '@', 'screenshot', 'api key', 'credential', 'claim text']:
            if forbidden in lowered:
                return f'bounded_change_ticket_command_templates.{key} includes forbidden raw/contact/claim term: {forbidden}'

    states = manifest.get('allowed_ticket_states')
    if not isinstance(states, list) or set(states) != {'blocked-no-real-packet', 'blocked-incomplete-board', 'ready-for-real-packet', 'active-change', 'rolled-back', 'quarantined'}:
        return 'allowed_ticket_states must enumerate the bounded post-decision ticket states'
    classes = manifest.get('allowed_change_classes')
    if not isinstance(classes, list) or set(classes) != {'pct-a-trim', 'pct-b-suppress', 'pct-c-sandbox-adjustment', 'pct-d-bounded-pilot', 'pct-x-quarantine'}:
        return 'allowed_change_classes must enumerate the bounded post-decision change classes'
    if 'activation receipt' not in str(manifest.get('activation_boundary') or '').lower() or 'does not create' not in str(manifest.get('activation_boundary') or '').lower():
        return 'activation_boundary must say active-change requires but is not created by the brief'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_first_packet_decision_text', 'copies_contact_details', 'copies_learner_identifiers_or_protected_facts']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('source_first_packet_decision_revalidated') is not True:
        return 'content_minimization.source_first_packet_decision_revalidated must be true'
    if content.get('contains_hashes_counts_and_command_skeletons_only') is not True:
        return 'content_minimization.contains_hashes_counts_and_command_skeletons_only must be true'
    forbidden_effects = manifest.get('forbidden_effects')
    if not isinstance(forbidden_effects, list) or 'change-ticket-automation' not in forbidden_effects or 'activation-receipt-creation' not in forbidden_effects or 'lifecycle-or-closure' not in forbidden_effects:
        return 'forbidden_effects must block ticket automation, activation creation, and lifecycle/closure effects'
    return None


EXPECTED_WORKBENCH_REVIEW_FIELDS = {
    'review_type': 'FT-0181-owner-packet-workbench-review',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'review_state': 'REVIEWED_NOT_ACCEPTED',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'ft0181_status': 'live',
}
WORKBENCH_REVIEW_DECISIONS = {
    'PROCEED-DECISION-BOARD',
    'REASK-OWNER',
    'BLOCK-OVERBROAD',
    'BLOCK-PROTECTED',
    'BLOCK-SECURITY',
    'BLOCK-EVIDENCE',
    'NO-CHANGE-TRIM',
}
WORKBENCH_REVIEW_CANDIDATE_SOURCE_CLASS = 'SRC2-CANDIDATE-NOT-ACCEPTED'
WORKBENCH_REVIEW_PROCEED_SOURCE_CLASSES = {'SRC2', 'SRC2+', 'SRC3', 'SRC3+', WORKBENCH_REVIEW_CANDIDATE_SOURCE_CLASS}


def _non_negative_int(value: object, field: str) -> tuple[int | None, str | None]:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None, f'{field} must be an integer'
    if parsed < 0:
        return None, f'{field} cannot be negative'
    return parsed, None


def owner_workbench_review_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a workbench review record cannot route the next field step.

    A review record is the first local artifact after a NOT_ACCEPTED workbench
    seed. It still is not evidence, acceptance, custody, closure, or public-claim
    support; it only records that a human performed the minimized workbench review
    and selected either a bounded block/reask/trim route or the first-packet
    decision board. The referenced seed must remain scratch-local and valid.
    """
    if not isinstance(manifest, dict):
        return 'workbench review is not an object'
    for key, expected in EXPECTED_WORKBENCH_REVIEW_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('review_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'review_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    decision = manifest.get('decision')
    if decision not in WORKBENCH_REVIEW_DECISIONS:
        return f'decision={decision!r} is not a recognized bounded workbench-review decision'
    if manifest.get('operator_confirmation') != 'human-reviewed-minimized-workbench-record':
        return 'operator_confirmation must be human-reviewed-minimized-workbench-record'
    if manifest.get('claim_ceiling') is None or 'not SRC2+ acceptance' not in str(manifest.get('claim_ceiling')) or 'not custody evidence' not in str(manifest.get('claim_ceiling')):
        return 'claim_ceiling must preserve not-SRC2+ and not-custody boundaries'

    input_seed = manifest.get('input_seed')
    if not isinstance(input_seed, dict):
        return 'input_seed must be an object'
    ref = input_seed.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'input_seed.reference must be a non-empty archive-relative scratch path'
    seed_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(seed_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'input_seed.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(seed_path, archive_root=archive_root, field_name='input_seed.reference')
    if lane_error:
        return lane_error
    if seed_path.name != 'workbench-seed.json' or not seed_path.exists() or not seed_path.is_file():
        return 'input_seed.reference must point to an existing workbench-seed.json file'
    try:
        seed_data = json.loads(seed_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'input_seed.reference is not readable JSON'
    seed_error = owner_workbench_seed_integrity_error(seed_data, archive_root=archive_root)
    if seed_error:
        return 'input_seed failed workbench-seed integrity: ' + seed_error
    if input_seed.get('seed_sha256') in {None, ''}:
        return 'input_seed.seed_sha256 must be recorded'
    if input_seed.get('acceptance_state') != seed_data.get('acceptance_state'):
        return 'input_seed.acceptance_state does not match referenced workbench seed'
    if input_seed.get('source_truth_status') != seed_data.get('source_truth_status'):
        return 'input_seed.source_truth_status does not match referenced workbench seed'

    counts = manifest.get('field_counts')
    if not isinstance(counts, dict):
        return 'field_counts must be an object'
    parsed_counts: dict[str, int] = {}
    for key in ['surviving_field_count', 'decision_changed_count', 'local_only_field_count', 'trimmed_field_count', 'reask_field_count']:
        parsed, count_error = _non_negative_int(counts.get(key), f'field_counts.{key}')
        if count_error:
            return count_error
        assert parsed is not None
        if parsed > 8:
            return f'field_counts.{key} cannot exceed the eight-row owner reply bound'
        parsed_counts[key] = parsed

    risk_flags = manifest.get('risk_flags')
    if not isinstance(risk_flags, dict):
        return 'risk_flags must be an object'
    for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']:
        if risk_flags.get(key) not in {True, False}:
            return f'risk_flags.{key} must be boolean'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_proceed_staged_row_text', 'copies_contact_details']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('contains_counts_hashes_and_routes_only') is not True:
        return 'content_minimization.contains_counts_hashes_and_routes_only must be true'
    if content.get('source_seed_revalidated') is not True:
        return 'content_minimization.source_seed_revalidated must be true'

    reviewer_roles, reviewer_error = _non_negative_int(manifest.get('reviewer_role_count'), 'reviewer_role_count')
    if reviewer_error:
        return reviewer_error
    assert reviewer_roles is not None
    if reviewer_roles < 1:
        return 'reviewer_role_count must be at least 1'

    source_class = manifest.get('source_truth_class')
    if not isinstance(source_class, str) or not source_class:
        return 'source_truth_class must be a non-empty string'
    if decision == 'PROCEED-DECISION-BOARD':
        if source_class not in WORKBENCH_REVIEW_PROCEED_SOURCE_CLASSES:
            return 'PROCEED-DECISION-BOARD requires source_truth_class SRC2/SRC3 or SRC2-CANDIDATE-NOT-ACCEPTED'
        if reviewer_roles < 2:
            return 'PROCEED-DECISION-BOARD requires at least two reviewer roles'
        if parsed_counts['surviving_field_count'] < 1:
            return 'PROCEED-DECISION-BOARD requires at least one surviving field'
        if parsed_counts['decision_changed_count'] < 1:
            return 'PROCEED-DECISION-BOARD requires at least one decision-changing field'
        if parsed_counts['reask_field_count'] != 0:
            return 'PROCEED-DECISION-BOARD cannot have pending re-ask fields'
        if any(risk_flags.get(key) is True for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']):
            return 'PROCEED-DECISION-BOARD requires raw/protected/security/public-claim-upgrade flags to be false'
        if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-first-packet-decision-board.md':
            return 'PROCEED-DECISION-BOARD must route to the first-packet decision board'
        if manifest.get('decision_board_effect') != 'may_source_first_packet_decision_board_only':
            return 'PROCEED-DECISION-BOARD must preserve decision_board_effect=may_source_first_packet_decision_board_only'
    else:
        if manifest.get('decision_board_effect') != 'none':
            return 'non-proceed workbench reviews must preserve decision_board_effect=none'
    if decision == 'REASK-OWNER' and parsed_counts['reask_field_count'] < 1:
        return 'REASK-OWNER requires at least one reask field count'
    if decision == 'BLOCK-PROTECTED' and risk_flags.get('protected_facts_present') is not True:
        return 'BLOCK-PROTECTED requires protected_facts_present=true'
    if decision == 'BLOCK-SECURITY' and risk_flags.get('security_payloads_present') is not True:
        return 'BLOCK-SECURITY requires security_payloads_present=true'
    if decision == 'BLOCK-EVIDENCE' and source_class in WORKBENCH_REVIEW_PROCEED_SOURCE_CLASSES and parsed_counts['decision_changed_count'] > 0:
        return 'BLOCK-EVIDENCE should not carry a proceed-capable source class with decision-changing fields'
    return None


EXPECTED_OWNER_REASK_LOG_FIELDS = {
    'reask_log_type': 'FT-0181-owner-reask-log',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'evidence_state': 'not_evidence',
    'source_truth_class': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'contact_status_effect': 'may_source_reask_awaiting_reply_clock_only',
}
OWNER_REASK_LOG_SOURCE_FILENAMES = {
    'contact-status.json',
    'bundle-manifest.json',
    'workbench-review.json',
}
OWNER_REASK_CHANNEL_CLASSES = {
    'email',
    'ticket',
    'form',
    'delegated-local-route',
    'other-bounded-route',
}
OWNER_REASK_ROUTE_CLASSES = {
    'same-accountable-owner-route',
    'delegated-local-owner-route',
    'governance-intake',
    'other-bounded-owner-route',
}


def owner_reask_log_source_error(source_path: Path, *, archive_root: Path, sent_date: date) -> str | None:
    """Return why a source artifact cannot justify one bounded reask send-log.

    The source can be only one of the existing field-session artifacts that
    legitimately creates a clarification need: an expired first-contact clock, a
    RE-ASK-ONCE intake bundle, or a REASK-OWNER workbench review. The source does
    not prove a message was sent; the reask log records that separate human-send
    assertion before any REASK contact clock can exist.
    """
    inside, parts = archive_relative(source_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'reask_source_ref must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(source_path, archive_root=archive_root, field_name='reask_source_ref')
    if lane_error:
        return lane_error
    if source_path.name not in OWNER_REASK_LOG_SOURCE_FILENAMES or not source_path.exists() or not source_path.is_file():
        return 'reask_source_ref must point to contact-status.json, bundle-manifest.json, or workbench-review.json under scratch/'
    try:
        data = json.loads(source_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'reask_source_ref is not readable JSON'

    if source_path.name == 'contact-status.json':
        status_error = owner_contact_status_integrity_error(data, archive_root=archive_root)
        if status_error:
            return 'prior SENT contact-status failed integrity: ' + status_error
        if data.get('contact_status') != 'SENT_AWAITING_REPLY':
            return 'prior contact-status source for reask must be SENT_AWAITING_REPLY'
        try:
            attempt = int(data.get('attempt_count') or 0)
        except (TypeError, ValueError):
            return 'prior contact-status attempt_count must be numeric'
        if attempt != 1:
            return 'prior contact-status source for reask must have attempt_count=1'
        due = date.fromisoformat(str(data.get('response_due_date')))
        if due > sent_date:
            return 'prior SENT contact clock must be due before a reask send-log can be recorded'
        return None

    if source_path.name == 'bundle-manifest.json':
        if data.get('bundle_type') != 'FT-0181-owner-reply-local-intake-bundle':
            return 'reask intake source must be an FT-0181 owner-reply local intake bundle'
        if data.get('triage_outcome') != 'RE-ASK-ONCE':
            return 'reask intake source must have triage_outcome=RE-ASK-ONCE'
        if data.get('ft0181_status') != 'live':
            return 'reask intake source must keep ft0181_status=live'
        if data.get('claim_ceiling') is not None and 'not' not in str(data.get('claim_ceiling')).lower():
            return 'reask intake source claim_ceiling must preserve non-evidence boundary'
        return None

    if source_path.name == 'workbench-review.json':
        review_error = owner_workbench_review_integrity_error(data, archive_root=archive_root)
        if review_error:
            return 'reask source workbench review failed integrity: ' + review_error
        if data.get('decision') != 'REASK-OWNER':
            return 'reask workbench review source must have decision=REASK-OWNER'
        return None

    return 'unrecognized reask source artifact type'


def owner_reask_log_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a local owner-reask log cannot source a REASK contact clock.

    Rev0282 closes the clarification-clock bypass: a REASK clock must be sourced
    from a local reask-log artifact, not directly from triage, an intake bundle,
    or a workbench review. The log remains non-evidence and stores no contact or
    owner-answer content.
    """
    if not isinstance(manifest, dict):
        return 'reask log is not an object'
    for key, expected in EXPECTED_OWNER_REASK_LOG_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('reask_log_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'reask_log_version={version!r} must name the release revision'
    for field in ['sent_date', 'response_due_date']:
        error = _parse_iso_date(manifest.get(field), field)
        if error:
            return error
    sent = date.fromisoformat(manifest['sent_date'])
    due = date.fromisoformat(manifest['response_due_date'])
    if due < sent:
        return 'response_due_date cannot precede sent_date'
    if (due - sent).days > REASK_MAX_DAYS:
        return f'reask response clock cannot exceed {REASK_MAX_DAYS} days'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-sent-bounded-reask':
        return 'operator_confirmation must be human-sent-bounded-reask'
    if manifest.get('max_response_clock_days') != REASK_MAX_DAYS:
        return f'max_response_clock_days must be {REASK_MAX_DAYS}'
    if manifest.get('reask_channel_class') not in OWNER_REASK_CHANNEL_CLASSES:
        return f'reask_channel_class={manifest.get("reask_channel_class")!r} is not allowed'
    if manifest.get('owner_route_class') not in OWNER_REASK_ROUTE_CLASSES:
        return f'owner_route_class={manifest.get("owner_route_class")!r} is not allowed'
    for field in ['no_contact_details_stored', 'no_raw_or_protected_material_stored', 'no_widening_confirmation']:
        if manifest.get(field) is not True:
            return f'{field} must be true'
    ref = manifest.get('reask_source_ref')
    if not isinstance(ref, str) or not ref:
        return 'reask_source_ref must be a non-empty archive-relative path'
    source_path = (archive_root / ref).resolve()
    source_error = owner_reask_log_source_error(source_path, archive_root=archive_root, sent_date=sent)
    if source_error:
        return source_error
    return None


EXPECTED_FIRST_PACKET_DECISION_FIELDS = {
    'decision_type': 'FT-0181-first-packet-decision-board',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'board_state': 'DECISION_RECORDED_NOT_ACCEPTED',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'ft0181_status': 'live',
}
FIRST_PACKET_AUTHORITY_ACTIONS = {'keep-lower-ceiling', 'revise-ceiling', 'block', 'no-change'}
FIRST_PACKET_EVIDENCE_ACTIONS = {'suppress', 'downgrade', 'keep-example-only', 'stage-claim-with-expiry', 'no-change'}
FIRST_PACKET_CONSTRUCT_ACTIONS = {'add-stop-trigger', 'keep-teacher-review', 'require-unaided-segment', 'fall-back-service', 'no-change'}
FIRST_PACKET_PUBLIC_ACTIONS = {'publish-limited', 'revise-claims', 'suppress', 'draft-only', 'no-change'}
FIRST_PACKET_LIFECYCLE_ACTIONS = {'sandbox', 'pilot', 'watch', 'deprecate', 'archive-only', 'quarantine', 'no-change'}
FIRST_PACKET_SLICE_ACTIONS = {
    'authority_action': FIRST_PACKET_AUTHORITY_ACTIONS,
    'evidence_action': FIRST_PACKET_EVIDENCE_ACTIONS,
    'construct_action': FIRST_PACKET_CONSTRUCT_ACTIONS,
    'public_action': FIRST_PACKET_PUBLIC_ACTIONS,
    'lifecycle_action': FIRST_PACKET_LIFECYCLE_ACTIONS,
}


def owner_first_packet_decision_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a first-packet decision board cannot source a change ticket.

    Rev0276 closes the post-review prose bypass: a proceed-capable workbench
    review must become a minimized five-slice decision record before any change
    ticket, lifecycle action, public-summary edit, custody step, or closure review.
    The decision record remains not evidence and NOT_ACCEPTED.
    """
    if not isinstance(manifest, dict):
        return 'first-packet decision is not an object'
    for key, expected in EXPECTED_FIRST_PACKET_DECISION_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('decision_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'decision_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-recorded-five-slice-decision-board':
        return 'operator_confirmation must be human-recorded-five-slice-decision-board'
    if manifest.get('claim_ceiling') is None or 'not evidence' not in str(manifest.get('claim_ceiling')).lower() or 'not custody evidence' not in str(manifest.get('claim_ceiling')).lower():
        return 'claim_ceiling must preserve not-evidence and not-custody boundaries'

    source = manifest.get('source_workbench_review')
    if not isinstance(source, dict):
        return 'source_workbench_review must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_workbench_review.reference must be a non-empty archive-relative scratch path'
    review_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(review_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_workbench_review.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(review_path, archive_root=archive_root, field_name='source_workbench_review.reference')
    if lane_error:
        return lane_error
    if review_path.name != 'workbench-review.json' or not review_path.exists() or not review_path.is_file():
        return 'source_workbench_review.reference must point to an existing workbench-review.json file'
    try:
        review_data = json.loads(review_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_workbench_review.reference is not readable JSON'
    review_error = owner_workbench_review_integrity_error(review_data, archive_root=archive_root)
    if review_error:
        return 'source_workbench_review failed workbench-review integrity: ' + review_error
    if review_data.get('decision') != 'PROCEED-DECISION-BOARD':
        return 'source_workbench_review.decision must be PROCEED-DECISION-BOARD'
    if source.get('review_sha256') in {None, ''}:
        return 'source_workbench_review.review_sha256 must be recorded'
    for key in ['decision', 'review_state', 'acceptance_state', 'source_truth_class', 'decision_changed_count', 'surviving_field_count', 'reviewer_role_count']:
        expected = review_data.get(key)
        if key in {'decision_changed_count', 'surviving_field_count'}:
            expected = review_data.get('field_counts', {}).get(key)
        if source.get(key) != expected:
            return f'source_workbench_review.{key} does not match referenced workbench-review.json'
    if source.get('revalidated_for_decision_board') is not True:
        return 'source_workbench_review.revalidated_for_decision_board must be true'

    slices = manifest.get('decision_slices')
    if not isinstance(slices, dict):
        return 'decision_slices must be an object'
    for key, allowed in FIRST_PACKET_SLICE_ACTIONS.items():
        value = slices.get(key)
        if value not in allowed:
            return f'decision_slices.{key}={value!r} is not an allowed bounded slice action'
    changed_count, changed_error = _non_negative_int(manifest.get('changed_slice_count'), 'changed_slice_count')
    if changed_error:
        return changed_error
    assert changed_count is not None
    if changed_count > 5:
        return 'changed_slice_count cannot exceed five decision slices'
    actual_changed = sum(1 for value in slices.values() if value != 'no-change')
    if changed_count != actual_changed:
        return f'changed_slice_count={changed_count} must equal non-no-change slice actions ({actual_changed})'
    if changed_count < 1:
        return 'changed_slice_count must be at least 1 for a proceed-capable first packet'
    rollback_roles, rollback_error = _non_negative_int(manifest.get('rollback_owner_role_count'), 'rollback_owner_role_count')
    if rollback_error:
        return rollback_error
    assert rollback_roles is not None
    if rollback_roles < 1 or rollback_roles > 5:
        return 'rollback_owner_role_count must be between 1 and 5'

    risk_flags = manifest.get('risk_flags')
    if not isinstance(risk_flags, dict):
        return 'risk_flags must be an object'
    for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']:
        if risk_flags.get(key) is not False:
            return f'risk_flags.{key} must be false for first-packet decision-board routing'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_workbench_review_text', 'copies_contact_details']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('contains_slice_classes_counts_hashes_and_routes_only') is not True:
        return 'content_minimization.contains_slice_classes_counts_hashes_and_routes_only must be true'
    if content.get('source_workbench_review_revalidated') is not True:
        return 'content_minimization.source_workbench_review_revalidated must be true'
    if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-post-decision-change-ticket.md':
        return 'required_next_surface must route to the post-decision change ticket'
    if manifest.get('change_ticket_effect') != 'may_source_post_decision_change_ticket_only':
        return 'change_ticket_effect must be may_source_post_decision_change_ticket_only'
    return None



EXPECTED_ACTIVATION_RECEIPT_FIELDS = {
    'receipt_type': 'FT-0181-active-change-activation-receipt',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'activation_state': 'REAL_PACKET_ACCEPTED_FOR_ACTIVE_CHANGE',
    'acceptance_state': 'ACTIVATION_RECEIPT_ONLY',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'change_ticket_effect': 'may_source_active_change_ticket_only',
}
ACTIVATION_RECEIPT_SRC2_PLUS = {'SRC2', 'SRC3', 'SRC4'}


def source_packet_path_allowed(packet_path: Path, *, archive_root: Path) -> tuple[bool, str]:
    """Return whether a real owner packet path is allowed for activation receipts.

    Real packets must be external-to-archive artifacts or deliberately staged
    under the live FT-0181 field lane. Checker, release, legacy, smoke, test, and
    fixture scratch lanes can contain byte-identical validation packets, so they
    must not be eligible for the SRC2+ activation receipt path.
    """
    resolved = packet_path.resolve()
    inside, parts = archive_relative(resolved, archive_root=archive_root)
    if not inside:
        return True, 'outside-archive-source-packet'
    if not parts:
        return False, 'archive-root-source-packet'
    if parts[0] == 'scratch':
        lane_block = non_field_scratch_lane_block(resolved, archive_root=archive_root)
        if lane_block:
            return False, f'archive-nonfield-scratch-source-packet:{lane_block}'
        return True, 'scratch-field-ft0181-source-packet'
    if parts[0] in CONTROLLED_TOP_LEVEL:
        return False, f'archive-controlled-source-packet:{parts[0]}'
    if len(parts) == 1 and parts[0] in CONTROLLED_ROOT_FILES:
        return False, f'archive-controlled-root-source-packet:{parts[0]}'
    return False, f'archive-nonscratch-source-packet:{parts[0]}'


def _archive_relative_ref(path: Path, *, archive_root: Path) -> str:
    """Return an archive-relative reference when possible, otherwise a path string."""
    try:
        return path.resolve().relative_to(archive_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def decision_chain_source_csv_snapshot(decision_path: Path, decision_data: dict, *, archive_root: Path) -> tuple[dict | None, str | None]:
    """Return the source CSV hash preserved by the decision's intake chain.

    Activation receipts are allowed to mention only hashes/counts. To avoid a
    false-active change from an unrelated local file, the receipt source packet
    must hash-match the same returned CSV that flowed through intake ->
    workbench seed -> workbench review -> first-packet decision. This helper
    reopens that scratch chain and verifies the intermediate hashes rather than
    trusting copied references in the receipt.
    """
    if not isinstance(decision_data, dict):
        return None, 'decision_data must be an object'
    source_review = decision_data.get('source_workbench_review')
    if not isinstance(source_review, dict):
        return None, 'decision source_workbench_review must be present'
    review_ref = source_review.get('reference')
    if not isinstance(review_ref, str) or not review_ref:
        return None, 'decision source_workbench_review.reference must be a non-empty scratch path'
    review_path = (archive_root / review_ref).resolve()
    inside, parts = archive_relative(review_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return None, 'decision source_workbench_review.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(review_path, archive_root=archive_root, field_name='decision source_workbench_review.reference')
    if lane_error:
        return None, lane_error
    if review_path.name != 'workbench-review.json' or not review_path.exists() or not review_path.is_file():
        return None, 'decision source_workbench_review.reference must point to an existing workbench-review.json file'
    review_sha = _sha256_file(review_path)
    if source_review.get('review_sha256') != review_sha:
        return None, 'decision source_workbench_review.review_sha256 must match referenced workbench-review.json'
    try:
        review_data = json.loads(review_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None, 'decision source_workbench_review.reference is not readable JSON'
    review_error = owner_workbench_review_integrity_error(review_data, archive_root=archive_root)
    if review_error:
        return None, 'decision source_workbench_review failed workbench-review integrity: ' + review_error

    input_seed = review_data.get('input_seed')
    if not isinstance(input_seed, dict):
        return None, 'workbench review input_seed must be present'
    seed_ref = input_seed.get('reference')
    if not isinstance(seed_ref, str) or not seed_ref:
        return None, 'workbench review input_seed.reference must be a non-empty scratch path'
    seed_path = (archive_root / seed_ref).resolve()
    inside, seed_parts = archive_relative(seed_path, archive_root=archive_root)
    if not inside or not seed_parts or seed_parts[0] != 'scratch':
        return None, 'workbench review input_seed.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(seed_path, archive_root=archive_root, field_name='workbench review input_seed.reference')
    if lane_error:
        return None, lane_error
    if seed_path.name != 'workbench-seed.json' or not seed_path.exists() or not seed_path.is_file():
        return None, 'workbench review input_seed.reference must point to an existing workbench-seed.json file'
    seed_sha = _sha256_file(seed_path)
    if input_seed.get('seed_sha256') != seed_sha:
        return None, 'workbench review input_seed.seed_sha256 must match referenced workbench-seed.json'
    try:
        seed_data = json.loads(seed_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None, 'workbench review input_seed.reference is not readable JSON'
    seed_error = owner_workbench_seed_integrity_error(seed_data, archive_root=archive_root)
    if seed_error:
        return None, 'workbench review input_seed failed workbench-seed integrity: ' + seed_error

    source_csv = seed_data.get('source_csv')
    if not isinstance(source_csv, dict):
        return None, 'workbench seed source_csv must be present for activation lineage'
    source_csv_sha = source_csv.get('sha256')
    if not isinstance(source_csv_sha, str) or not source_csv_sha:
        return None, 'workbench seed source_csv.sha256 must be present for activation lineage'
    return {
        'source_csv_sha256': source_csv_sha,
        'source_csv_basename': source_csv.get('basename'),
        'source_csv_reference': source_csv.get('reference'),
        'source_csv_path_scope': source_csv.get('path_scope'),
        'workbench_seed_reference': _archive_relative_ref(seed_path, archive_root=archive_root),
        'workbench_seed_sha256': seed_sha,
        'workbench_review_reference': _archive_relative_ref(review_path, archive_root=archive_root),
        'workbench_review_sha256': review_sha,
        'first_packet_decision_reference': _archive_relative_ref(decision_path, archive_root=archive_root),
        'first_packet_decision_sha256': _sha256_file(decision_path),
        'revalidated_for_activation_receipt': True,
    }, None


def activation_receipt_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why an activation receipt cannot unlock an active-change ticket.

    This receipt is a local non-evidence firebreak: it says a human has a real
    owner-reviewed SRC2+ packet and has confirmed minimal activation conditions.
    It is not the evidence itself, but an active_change ticket may not exist
    without this scratch-local receipt.
    """
    if not isinstance(manifest, dict):
        return 'activation receipt is not an object'
    for key, expected in EXPECTED_ACTIVATION_RECEIPT_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('receipt_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'receipt_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-confirmed-real-packet-accepted-for-active-change':
        return 'operator_confirmation must be human-confirmed-real-packet-accepted-for-active-change'
    source_truth_class = manifest.get('source_truth_class')
    if source_truth_class not in ACTIVATION_RECEIPT_SRC2_PLUS:
        return 'activation receipt requires SRC2/SRC3/SRC4 source_truth_class'
    ceiling = str(manifest.get('claim_ceiling') or '')
    for phrase in ['not evidence', 'not closure evidence', 'not public-summary support']:
        if phrase not in ceiling.lower():
            return f'claim_ceiling must include {phrase}'

    source_packet = manifest.get('source_packet')
    if not isinstance(source_packet, dict):
        return 'source_packet must be an object'
    packet_ref = source_packet.get('reference')
    if not isinstance(packet_ref, str) or not packet_ref:
        return 'source_packet.reference must be a non-empty path'
    packet_path = Path(packet_ref)
    if not packet_path.is_absolute():
        packet_path = (archive_root / packet_path).resolve()
    allowed, boundary = source_packet_path_allowed(packet_path, archive_root=archive_root)
    if not allowed:
        return f'source_packet.reference is not allowed: {boundary}'
    if not packet_path.exists() or not packet_path.is_file():
        return 'source_packet.reference must point to an existing local packet file'
    if source_packet.get('path_boundary') != boundary:
        return 'source_packet.path_boundary must match the resolved source packet boundary'
    packet_sha = source_packet.get('sha256')
    if packet_sha in {None, ''}:
        return 'source_packet.sha256 must be recorded'
    if packet_sha != _sha256_file(packet_path):
        return 'source_packet.sha256 does not match referenced source packet'
    marker = returned_owner_csv_marker_block(packet_path)
    if marker:
        return f'source_packet appears to be a smoke/fixture artifact: {marker}'
    if source_packet.get('source_truth_class') != source_truth_class:
        return 'source_packet.source_truth_class must match receipt source_truth_class'

    source_decision = manifest.get('source_first_packet_decision')
    if not isinstance(source_decision, dict):
        return 'source_first_packet_decision must be an object'
    ref = source_decision.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_first_packet_decision.reference must be a non-empty archive-relative scratch path'
    decision_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(decision_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_first_packet_decision.reference must stay under scratch'
    lane_error = field_scratch_lane_error(decision_path, archive_root=archive_root, field_name='source_first_packet_decision.reference')
    if lane_error:
        return lane_error
    if decision_path.name != 'first-packet-decision.json' or not decision_path.exists() or not decision_path.is_file():
        return 'source_first_packet_decision.reference must point to an existing first-packet-decision.json file'
    try:
        decision_data = json.loads(decision_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_first_packet_decision.reference is not readable JSON'
    decision_error = owner_first_packet_decision_integrity_error(decision_data, archive_root=archive_root)
    if decision_error:
        return 'source_first_packet_decision failed first-packet-decision integrity: ' + decision_error
    decision_sha = source_decision.get('decision_sha256')
    if decision_sha in {None, ''}:
        return 'source_first_packet_decision.decision_sha256 must be recorded'
    if decision_sha != _sha256_file(decision_path):
        return 'source_first_packet_decision.decision_sha256 does not match referenced decision'
    for key in ['board_state', 'acceptance_state', 'evidence_state', 'changed_slice_count', 'rollback_owner_role_count', 'decision_slices', 'change_ticket_effect']:
        if source_decision.get(key) != decision_data.get(key):
            return f'source_first_packet_decision.{key} does not match referenced decision'
    if source_decision.get('revalidated_for_activation_receipt') is not True:
        return 'source_first_packet_decision.revalidated_for_activation_receipt must be true'

    expected_chain, chain_error = decision_chain_source_csv_snapshot(decision_path, decision_data, archive_root=archive_root)
    if chain_error or expected_chain is None:
        return 'decision source chain failed activation lineage check: ' + str(chain_error)
    recorded_chain = manifest.get('decision_source_chain')
    if not isinstance(recorded_chain, dict):
        return 'decision_source_chain must be an object'
    for key in [
        'source_csv_sha256',
        'source_csv_basename',
        'source_csv_reference',
        'source_csv_path_scope',
        'workbench_seed_reference',
        'workbench_seed_sha256',
        'workbench_review_reference',
        'workbench_review_sha256',
        'first_packet_decision_reference',
        'first_packet_decision_sha256',
    ]:
        if recorded_chain.get(key) != expected_chain.get(key):
            return f'decision_source_chain.{key} does not match the current intake/workbench/decision chain'
    if recorded_chain.get('revalidated_for_activation_receipt') is not True:
        return 'decision_source_chain.revalidated_for_activation_receipt must be true'
    if source_packet.get('decision_chain_source_csv_sha256') != expected_chain.get('source_csv_sha256'):
        return 'source_packet.decision_chain_source_csv_sha256 must match decision_source_chain.source_csv_sha256'
    if source_packet.get('matches_decision_chain_source_csv_sha256') is not True:
        return 'source_packet.matches_decision_chain_source_csv_sha256 must be true'
    if packet_sha != expected_chain.get('source_csv_sha256'):
        return 'source_packet.sha256 must equal the returned CSV hash preserved by the decision source chain'

    counts = manifest.get('activation_counts')
    if not isinstance(counts, dict):
        return 'activation_counts must be an object'
    for field, minimum, upper in [
        ('accepted_field_count', 1, 8),
        ('reviewer_role_count', 2, 5),
        ('dictionary_or_map_ref_count', 1, 10),
        ('blocked_or_trimmed_field_count', 0, 8),
    ]:
        value, value_error = _non_negative_int(counts.get(field), f'activation_counts.{field}')
        if value_error:
            return value_error
        assert value is not None
        if value < minimum or value > upper:
            return f'activation_counts.{field} must be between {minimum} and {upper}'
    confirmations = manifest.get('activation_confirmations')
    if not isinstance(confirmations, dict):
        return 'activation_confirmations must be an object'
    for field in [
        'owner_reviewed_packet',
        'source_packet_hash_recorded',
        'dictionary_or_map_reviewed',
        'protected_security_exclusions_confirmed',
        'two_role_review_confirmed',
        'no_contact_details_stored',
        'no_raw_or_protected_material_copied',
        'no_public_claim_upgrade',
    ]:
        if confirmations.get(field) is not True:
            return f'activation_confirmations.{field} must be true'
    return None

EXPECTED_POST_DECISION_CHANGE_TICKET_FIELDS = {
    'ticket_type': 'FT-0181-post-decision-change-ticket',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'ft0181_status': 'live',
}
POST_DECISION_TICKET_STATES = {
    'blocked_no_real_packet',
    'blocked_incomplete_board',
    'ready_for_real_packet',
    'active_change',
    'rolled_back',
    'quarantined',
}
POST_DECISION_CHANGE_CLASSES = {
    'PCT-A-trim',
    'PCT-B-suppress',
    'PCT-C-sandbox-adjustment',
    'PCT-D-bounded-pilot',
    'PCT-X-quarantine',
}
POST_DECISION_SOURCE_TRUTH_CLASSES = {'SRC0', 'SRC1', 'SRC2', 'SRC3', 'SRC4', 'SRCX', 'UNVERIFIED-OWNER-REPLY', 'not_evidence'}
POST_DECISION_SRC2_PLUS = {'SRC2', 'SRC3', 'SRC4'}
POST_DECISION_PUBLIC_CEILINGS = {
    'example-only-no-outcome-claim',
    'draft-only-no-outcome-claim',
    'suppress-public-language',
    'limited-process-language-no-outcome-claim',
}


def owner_post_decision_change_ticket_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a post-decision change ticket cannot source a live-window card.

    Rev0277 closes the first-packet-decision prose bypass: a valid decision-board
    record must become a minimized change-ticket artifact before any live-window,
    service-record, lifecycle, custody, acceptance, public-summary, or closure
    step. The ticket remains local, NOT_ACCEPTED, and not evidence.
    """
    if not isinstance(manifest, dict):
        return 'post-decision change ticket is not an object'
    for key, expected in EXPECTED_POST_DECISION_CHANGE_TICKET_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('ticket_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'ticket_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-recorded-bounded-post-decision-change-ticket':
        return 'operator_confirmation must be human-recorded-bounded-post-decision-change-ticket'
    ceiling = str(manifest.get('claim_ceiling') or '')
    if 'not evidence' not in ceiling.lower() or 'not custody evidence' not in ceiling.lower() or 'not closure evidence' not in ceiling.lower():
        return 'claim_ceiling must preserve not-evidence, not-custody, and not-closure boundaries'

    state = manifest.get('ticket_state')
    if state not in POST_DECISION_TICKET_STATES:
        return f'ticket_state={state!r} is not allowed'
    change_class = manifest.get('change_class')
    if change_class not in POST_DECISION_CHANGE_CLASSES:
        return f'change_class={change_class!r} is not allowed'
    source_truth_required = manifest.get('source_truth_required')
    if source_truth_required not in POST_DECISION_SOURCE_TRUTH_CLASSES:
        return f'source_truth_required={source_truth_required!r} is not allowed'
    public_ceiling = manifest.get('public_claim_ceiling')
    if public_ceiling not in POST_DECISION_PUBLIC_CEILINGS:
        return f'public_claim_ceiling={public_ceiling!r} is not allowed'

    source = manifest.get('source_first_packet_decision')
    if not isinstance(source, dict):
        return 'source_first_packet_decision must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_first_packet_decision.reference must be a non-empty archive-relative scratch path'
    decision_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(decision_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_first_packet_decision.reference must stay under scratch'
    lane_error = field_scratch_lane_error(decision_path, archive_root=archive_root, field_name='source_first_packet_decision.reference')
    if lane_error:
        return lane_error
    if decision_path.name != 'first-packet-decision.json' or not decision_path.exists() or not decision_path.is_file():
        return 'source_first_packet_decision.reference must point to an existing first-packet-decision.json file'
    try:
        decision_data = json.loads(decision_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_first_packet_decision.reference is not readable JSON'
    decision_error = owner_first_packet_decision_integrity_error(decision_data, archive_root=archive_root)
    if decision_error:
        return 'source_first_packet_decision failed first-packet-decision integrity: ' + decision_error
    if source.get('decision_sha256') in {None, ''}:
        return 'source_first_packet_decision.decision_sha256 must be recorded'
    if source.get('decision_sha256') != _sha256_file(decision_path):
        return 'source_first_packet_decision.decision_sha256 does not match referenced decision'
    if source.get('board_state') != decision_data.get('board_state'):
        return 'source_first_packet_decision.board_state does not match referenced decision'
    if source.get('acceptance_state') != decision_data.get('acceptance_state'):
        return 'source_first_packet_decision.acceptance_state does not match referenced decision'
    if source.get('evidence_state') != decision_data.get('evidence_state'):
        return 'source_first_packet_decision.evidence_state does not match referenced decision'
    if source.get('changed_slice_count') != decision_data.get('changed_slice_count'):
        return 'source_first_packet_decision.changed_slice_count does not match referenced decision'
    if source.get('rollback_owner_role_count') != decision_data.get('rollback_owner_role_count'):
        return 'source_first_packet_decision.rollback_owner_role_count does not match referenced decision'
    if source.get('decision_slices') != decision_data.get('decision_slices'):
        return 'source_first_packet_decision.decision_slices does not match referenced decision'
    expected_source_truth = decision_data.get('source_workbench_review', {}).get('source_truth_class')
    if source.get('source_truth_class') != expected_source_truth:
        return 'source_first_packet_decision.source_truth_class does not match referenced decision'
    if source.get('change_ticket_effect') != 'may_source_post_decision_change_ticket_only':
        return 'source_first_packet_decision.change_ticket_effect must preserve post-decision ticket routing only'
    if source.get('revalidated_for_change_ticket') is not True:
        return 'source_first_packet_decision.revalidated_for_change_ticket must be true'

    counts = manifest.get('change_counts')
    if not isinstance(counts, dict):
        return 'change_counts must be an object'
    parsed: dict[str, int] = {}
    for field, minimum, upper in [
        ('allowed_change_count', 0, 5),
        ('prohibited_change_count', 1, 10),
        ('rollback_trigger_count', 1, 10),
    ]:
        value, value_error = _non_negative_int(counts.get(field), f'change_counts.{field}')
        if value_error:
            return value_error
        assert value is not None
        if value < minimum or value > upper:
            return f'change_counts.{field} must be between {minimum} and {upper}'
        parsed[field] = value
    rollback_roles, rollback_error = _non_negative_int(manifest.get('rollback_owner_role_count'), 'rollback_owner_role_count')
    if rollback_error:
        return rollback_error
    assert rollback_roles is not None
    if rollback_roles < 1 or rollback_roles > 5:
        return 'rollback_owner_role_count must be between 1 and 5'
    if state in {'ready_for_real_packet', 'active_change'} and parsed['allowed_change_count'] < 1:
        return 'ready_for_real_packet and active_change require at least one allowed change count'
    if state == 'active_change' and manifest.get('live_window_required') is not True:
        return 'active_change requires live_window_required=true'
    if state == 'active_change':
        receipt = manifest.get('source_activation_receipt')
        if not isinstance(receipt, dict):
            return 'active_change requires source_activation_receipt from a real-packet activation receipt'
        receipt_ref = receipt.get('reference')
        if not isinstance(receipt_ref, str) or not receipt_ref:
            return 'source_activation_receipt.reference must be a non-empty archive-relative scratch path'
        receipt_path = (archive_root / receipt_ref).resolve()
        inside, receipt_parts = archive_relative(receipt_path, archive_root=archive_root)
        if not inside or not receipt_parts or receipt_parts[0] != 'scratch':
            return 'source_activation_receipt.reference must stay under scratch'
        lane_error = field_scratch_lane_error(receipt_path, archive_root=archive_root, field_name='source_activation_receipt.reference')
        if lane_error:
            return lane_error
        if receipt_path.name != 'activation-receipt.json' or not receipt_path.exists() or not receipt_path.is_file():
            return 'source_activation_receipt.reference must point to an existing activation-receipt.json file'
        try:
            receipt_data = json.loads(receipt_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return 'source_activation_receipt.reference is not readable JSON'
        receipt_error = activation_receipt_integrity_error(receipt_data, archive_root=archive_root)
        if receipt_error:
            return 'source_activation_receipt failed activation-receipt integrity: ' + receipt_error
        if receipt.get('receipt_sha256') in {None, ''}:
            return 'source_activation_receipt.receipt_sha256 must be recorded'
        if receipt.get('receipt_sha256') != _sha256_file(receipt_path):
            return 'source_activation_receipt.receipt_sha256 does not match referenced receipt'
        receipt_decision = receipt_data.get('source_first_packet_decision', {})
        if receipt_decision.get('reference') != source.get('reference'):
            return 'source_activation_receipt decision reference must match source_first_packet_decision.reference'
        if receipt_decision.get('decision_sha256') != source.get('decision_sha256'):
            return 'source_activation_receipt decision hash must match source_first_packet_decision.decision_sha256'
        if receipt_data.get('source_truth_class') != source_truth_required:
            return 'active_change source_truth_required must match activation receipt source_truth_class'
        for key in ['activation_state', 'acceptance_state', 'evidence_state', 'source_truth_class', 'change_ticket_effect']:
            if receipt.get(key) != receipt_data.get(key):
                return f'source_activation_receipt.{key} does not match referenced receipt'
        if receipt.get('revalidated_for_active_change_ticket') is not True:
            return 'source_activation_receipt.revalidated_for_active_change_ticket must be true'
    elif manifest.get('source_activation_receipt') is not None:
        return 'source_activation_receipt is allowed only on active_change tickets'
    if change_class == 'PCT-D-bounded-pilot':
        if source_truth_required not in POST_DECISION_SRC2_PLUS:
            return 'PCT-D-bounded-pilot requires source_truth_required SRC2/SRC3/SRC4'
        if manifest.get('live_window_required') is not True:
            return 'PCT-D-bounded-pilot requires live_window_required=true'
    if change_class == 'PCT-X-quarantine' and state not in {'quarantined', 'rolled_back'}:
        return 'PCT-X-quarantine must use quarantined or rolled_back ticket_state'

    risk_flags = manifest.get('risk_flags')
    if not isinstance(risk_flags, dict):
        return 'risk_flags must be an object'
    for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']:
        if risk_flags.get(key) is not False:
            return f'risk_flags.{key} must be false for post-decision change-ticket routing'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_first_packet_decision_text', 'copies_contact_details']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('contains_change_classes_counts_hashes_and_routes_only') is not True:
        return 'content_minimization.contains_change_classes_counts_hashes_and_routes_only must be true'
    if content.get('source_first_packet_decision_revalidated') is not True:
        return 'content_minimization.source_first_packet_decision_revalidated must be true'
    if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-live-window-stop-rollback-card.md':
        return 'required_next_surface must route to the live-window stop/rollback card'
    if manifest.get('live_window_effect') != 'may_source_live_window_stop_rollback_card_only':
        return 'live_window_effect must be may_source_live_window_stop_rollback_card_only'
    if manifest.get('change_ticket_effect') != 'does_not_modify_service_records_without_live_window_card':
        return 'change_ticket_effect must prevent service-record changes without live-window card'
    return None



EXPECTED_ACTIVATION_LIVE_WINDOW_BRIEF_FIELDS = {
    'brief_type': 'FT-0181-activation-live-window-entry-brief',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'ft0181_status': 'live',
}
ACTIVATION_LIVE_WINDOW_BRIEF_STATES = {
    'ACTIVATION_ENTRY_BRIEF_PREPARED_NOT_ACCEPTED',
    'LIVE_WINDOW_ENTRY_BRIEF_PREPARED_NOT_RECORDED',
}


def owner_activation_live_window_brief_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why an activation/live-window entry brief cannot route late field work.

    The brief is a scratch-local execution bridge only. It may show the exact
    activation receipt or live-window card commands that a human could run next,
    but it cannot accept a source packet, record an activation receipt, record an
    active-change ticket, create a live-window card, mutate service records,
    support public claims, move lifecycle state, or close FT-0181.
    """
    if not isinstance(manifest, dict):
        return 'activation/live-window brief is not an object'
    for key, expected in EXPECTED_ACTIVATION_LIVE_WINDOW_BRIEF_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('brief_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'brief_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    brief_state = manifest.get('brief_state')
    if brief_state not in ACTIVATION_LIVE_WINDOW_BRIEF_STATES:
        return f'brief_state={brief_state!r} is not a recognized activation/live-window brief state'
    ceiling = str(manifest.get('claim_ceiling') or '')
    for phrase in ['not an activation receipt', 'not a live-window card', 'not evidence', 'not closure evidence']:
        if phrase not in ceiling.lower():
            return f'claim_ceiling must preserve {phrase}'

    source = manifest.get('source_post_decision_change_ticket')
    if not isinstance(source, dict):
        return 'source_post_decision_change_ticket must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_post_decision_change_ticket.reference must be a non-empty archive-relative scratch path'
    ticket_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(ticket_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_post_decision_change_ticket.reference must stay under scratch'
    lane_error = field_scratch_lane_error(ticket_path, archive_root=archive_root, field_name='source_post_decision_change_ticket.reference')
    if lane_error:
        return lane_error
    if ticket_path.name != 'post-decision-change-ticket.json' or not ticket_path.exists() or not ticket_path.is_file():
        return 'source_post_decision_change_ticket.reference must point to an existing post-decision-change-ticket.json file'
    try:
        ticket_data = json.loads(ticket_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_post_decision_change_ticket.reference is not readable JSON'
    ticket_error = owner_post_decision_change_ticket_integrity_error(ticket_data, archive_root=archive_root)
    if ticket_error:
        return 'source_post_decision_change_ticket failed post-decision ticket integrity: ' + ticket_error
    if source.get('ticket_sha256') in {None, ''}:
        return 'source_post_decision_change_ticket.ticket_sha256 must be recorded'
    if source.get('ticket_sha256') != _sha256_file(ticket_path):
        return 'source_post_decision_change_ticket.ticket_sha256 does not match referenced ticket'
    for key in [
        'ticket_state',
        'change_class',
        'source_truth_required',
        'public_claim_ceiling',
        'live_window_required',
        'change_counts',
        'rollback_owner_role_count',
        'acceptance_state',
        'evidence_state',
        'source_first_packet_decision',
        'source_activation_receipt',
        'live_window_effect',
        'change_ticket_effect',
    ]:
        if source.get(key) != ticket_data.get(key):
            return f'source_post_decision_change_ticket.{key} does not match referenced ticket'
    if source.get('revalidated_for_activation_live_window_brief') is not True:
        return 'source_post_decision_change_ticket.revalidated_for_activation_live_window_brief must be true'

    ticket_state = ticket_data.get('ticket_state')
    if ticket_state == 'ready_for_real_packet':
        if brief_state != 'ACTIVATION_ENTRY_BRIEF_PREPARED_NOT_ACCEPTED':
            return 'ready_for_real_packet tickets require activation-entry brief state'
        activation_command = manifest.get('activation_receipt_command_template')
        if not isinstance(activation_command, str) or not activation_command.startswith('make owner-activation-receipt '):
            return 'ready_for_real_packet brief must include an owner-activation-receipt command template'
        source_decision = ticket_data.get('source_first_packet_decision') if isinstance(ticket_data.get('source_first_packet_decision'), dict) else {}
        decision_ref = source_decision.get('reference')
        if not isinstance(decision_ref, str) or decision_ref not in activation_command:
            return 'activation receipt command must reference the source first-packet decision'
        for token in [
            'SOURCE_PACKET=/path/to/same-returned-owner-csv-that-seeded-this-decision.csv',
            'SOURCE_TRUTH_CLASS=SRC2',
            'CONFIRM=human-confirmed-real-packet-accepted-for-active-change',
        ]:
            if token not in activation_command:
                return f'activation receipt command missing {token}'
        active_command = manifest.get('active_change_ticket_command_template')
        if not isinstance(active_command, str) or not active_command.startswith('make owner-post-decision-change-ticket '):
            return 'ready_for_real_packet brief must include an active-change ticket command template'
        for token in [
            'TICKET_STATE=active-change',
            'ACTIVATION_RECEIPT=<scratch/.../activation-receipt.json>',
            'CONFIRM=human-recorded-bounded-post-decision-change-ticket',
        ]:
            if token not in active_command:
                return f'active-change ticket command missing {token}'
        if manifest.get('live_window_card_command_templates') not in ({}, None):
            return 'ready_for_real_packet brief must not emit live-window card command templates before active_change'
        if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-post-decision-change-ticket.md':
            return 'ready_for_real_packet brief must route next to the activation/change-ticket surface'
    elif ticket_state == 'active_change':
        if brief_state != 'LIVE_WINDOW_ENTRY_BRIEF_PREPARED_NOT_RECORDED':
            return 'active_change tickets require live-window-entry brief state'
        if manifest.get('activation_receipt_command_template') is not None:
            return 'active_change brief must not request another activation receipt'
        commands = manifest.get('live_window_card_command_templates')
        if not isinstance(commands, dict) or not commands:
            return 'active_change brief must include live-window card command templates'
        required = {
            'staged_small_window': ('WINDOW_STATE=staged', 'NO_EXPANSION_CONFIRMED=1', 'HUMAN_PAUSE_CONFIRMED=1', 'FALLBACK_ROUTE_CONFIRMED=1'),
            'active_small_window': ('WINDOW_STATE=active', 'NO_EXPANSION_CONFIRMED=1', 'HUMAN_PAUSE_CONFIRMED=1', 'FALLBACK_ROUTE_CONFIRMED=1'),
            'paused_stop_state': ('WINDOW_STATE=paused', 'NO_EXPANSION_CONFIRMED=1', 'HUMAN_PAUSE_CONFIRMED=1', 'FALLBACK_ROUTE_CONFIRMED=1'),
            'quarantine_without_expansion': ('WINDOW_STATE=quarantined', 'NO_EXPANSION_CONFIRMED=1', 'HUMAN_PAUSE_CONFIRMED=1', 'FALLBACK_ROUTE_CONFIRMED=1'),
        }
        for key, tokens in required.items():
            command = commands.get(key)
            if not isinstance(command, str) or not command.startswith('make owner-live-window-card '):
                return f'live_window_card_command_templates.{key} must be an owner-live-window-card command'
            if f'TICKET={ref}' not in command and f"TICKET='{ref}'" not in command:
                return f'live_window_card_command_templates.{key} must reference the source ticket'
            for token in tokens:
                if token not in command:
                    return f'live_window_card_command_templates.{key} missing {token}'
            if 'CONFIRM=human-recorded-bounded-live-window-card' not in command:
                return f'live_window_card_command_templates.{key} must carry the live-window confirmation token'
        if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-live-window-stop-rollback-card.md':
            return 'active_change brief must route next to the live-window card surface'
    else:
        return 'activation/live-window brief only supports ready_for_real_packet or active_change source tickets'

    for key, text in {
        'activation_boundary': manifest.get('activation_boundary'),
        'live_window_boundary': manifest.get('live_window_boundary'),
    }.items():
        lowered = str(text or '').lower()
        if 'does not' not in lowered or ('activation' not in lowered and 'live-window' not in lowered):
            return f'{key} must state the no-effect boundary'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_post_decision_ticket_text', 'copies_contact_details', 'copies_learner_identifiers_or_protected_facts']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('source_post_decision_ticket_revalidated') is not True:
        return 'content_minimization.source_post_decision_ticket_revalidated must be true'
    if content.get('contains_hashes_counts_and_command_skeletons_only') is not True:
        return 'content_minimization.contains_hashes_counts_and_command_skeletons_only must be true'
    forbidden_effects = manifest.get('forbidden_effects')
    if not isinstance(forbidden_effects, list):
        return 'forbidden_effects must be a list'
    for required in ['source-packet-acceptance', 'activation-receipt-creation', 'live-window-card-recording', 'lifecycle-or-closure']:
        if required not in forbidden_effects:
            return f'forbidden_effects must include {required}'
    for command in [manifest.get('activation_receipt_command_template'), manifest.get('active_change_ticket_command_template'), *list((manifest.get('live_window_card_command_templates') or {}).values())]:
        if not isinstance(command, str):
            continue
        lowered = command.lower()
        for forbidden in ['student id', 'learner id', 'student name', 'email address', '@', 'screenshot', 'api key', 'credential', 'claim text']:
            if forbidden in lowered:
                return f'brief command includes forbidden raw/contact/claim term: {forbidden}'
    return None


EXPECTED_LIVE_WINDOW_CARD_FIELDS = {
    'card_type': 'FT-0181-live-window-stop-rollback-card',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'ft0181_status': 'live',
}
LIVE_WINDOW_STATES = {
    'blocked_no_real_packet',
    'blocked_incomplete_ticket',
    'staged',
    'active',
    'paused',
    'rolled_back',
    'completed_no_closure',
    'quarantined',
}
LIVE_WINDOW_SRC2_PLUS_STATES = {'staged', 'active', 'paused', 'rolled_back', 'completed_no_closure'}
LIVE_WINDOW_READOUT_READY_STATES = {'paused', 'rolled_back', 'completed_no_closure', 'quarantined'}
LIVE_WINDOW_SOURCE_TRUTH_CLASSES = {'SRC0', 'SRC2', 'SRC3', 'SRC4'}
LIVE_WINDOW_PUBLIC_CEILINGS = POST_DECISION_PUBLIC_CEILINGS


def owner_live_window_card_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a live-window card cannot source a post-window readout.

    Rev0278 closes the next prose bypass after a valid post-decision change
    ticket. A local card must preserve the ticket hash, stop/rollback counts,
    no-expansion controls, source-truth boundary, and terminal readout routing.
    It remains NOT_ACCEPTED and not evidence even when it is well-formed.
    """
    if not isinstance(manifest, dict):
        return 'live-window card is not an object'
    for key, expected in EXPECTED_LIVE_WINDOW_CARD_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('card_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'card_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-recorded-bounded-live-window-card':
        return 'operator_confirmation must be human-recorded-bounded-live-window-card'
    ceiling = str(manifest.get('claim_ceiling') or '')
    if 'not evidence' not in ceiling.lower() or 'not closure evidence' not in ceiling.lower():
        return 'claim_ceiling must preserve not-evidence and not-closure boundaries'

    state = manifest.get('window_state')
    if state not in LIVE_WINDOW_STATES:
        return f'window_state={state!r} is not allowed'
    source_truth_class = manifest.get('source_truth_class')
    if source_truth_class not in LIVE_WINDOW_SOURCE_TRUTH_CLASSES:
        return f'source_truth_class={source_truth_class!r} is not allowed'
    public_ceiling = manifest.get('public_claim_ceiling')
    if public_ceiling not in LIVE_WINDOW_PUBLIC_CEILINGS:
        return f'public_claim_ceiling={public_ceiling!r} is not allowed'

    source = manifest.get('source_post_decision_change_ticket')
    if not isinstance(source, dict):
        return 'source_post_decision_change_ticket must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_post_decision_change_ticket.reference must be a non-empty scratch path'
    ticket_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(ticket_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_post_decision_change_ticket.reference must stay under scratch'
    lane_error = field_scratch_lane_error(ticket_path, archive_root=archive_root, field_name='source_post_decision_change_ticket.reference')
    if lane_error:
        return lane_error
    if ticket_path.name != 'post-decision-change-ticket.json' or not ticket_path.exists() or not ticket_path.is_file():
        return 'source_post_decision_change_ticket.reference must point to an existing post-decision-change-ticket.json file'
    try:
        ticket_data = json.loads(ticket_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_post_decision_change_ticket.reference is not readable JSON'
    ticket_error = owner_post_decision_change_ticket_integrity_error(ticket_data, archive_root=archive_root)
    if ticket_error:
        return 'source_post_decision_change_ticket failed post-decision ticket integrity: ' + ticket_error
    if source.get('ticket_sha256') in {None, ''}:
        return 'source_post_decision_change_ticket.ticket_sha256 must be recorded'
    if source.get('ticket_sha256') != _sha256_file(ticket_path):
        return 'source_post_decision_change_ticket.ticket_sha256 does not match referenced ticket'
    for key in [
        'ticket_state',
        'change_class',
        'source_truth_required',
        'public_claim_ceiling',
        'live_window_required',
        'change_counts',
        'rollback_owner_role_count',
        'acceptance_state',
        'evidence_state',
        'live_window_effect',
    ]:
        if source.get(key) != ticket_data.get(key):
            return f'source_post_decision_change_ticket.{key} does not match referenced ticket'
    if source.get('revalidated_for_live_window_card') is not True:
        return 'source_post_decision_change_ticket.revalidated_for_live_window_card must be true'

    controls = manifest.get('window_controls')
    if not isinstance(controls, dict):
        return 'window_controls must be an object'
    parsed: dict[str, int] = {}
    for field, minimum, upper in [
        ('window_day_count', 0, 14),
        ('allowed_activity_count', 0, 5),
        ('prohibited_activity_count', 1, 10),
        ('stop_trigger_count', 1, 10),
        ('rollback_step_count', 1, 10),
        ('rollback_owner_role_count', 1, 5),
        ('evidence_readout_count', 0, 7),
    ]:
        value, value_error = _non_negative_int(controls.get(field), f'window_controls.{field}')
        if value_error:
            return value_error
        assert value is not None
        if value < minimum or value > upper:
            return f'window_controls.{field} must be between {minimum} and {upper}'
        parsed[field] = value
    source_roles = ticket_data.get('rollback_owner_role_count')
    if isinstance(source_roles, int) and parsed['rollback_owner_role_count'] < source_roles:
        return 'window_controls.rollback_owner_role_count cannot be below source ticket count'
    if state in {'blocked_no_real_packet', 'blocked_incomplete_ticket'}:
        if source_truth_class != 'SRC0':
            return 'blocked live-window cards must use SRC0 source truth'
        if parsed['window_day_count'] != 0 or parsed['allowed_activity_count'] != 0:
            return 'blocked live-window cards must have zero days and zero allowed live activities'
    if state in LIVE_WINDOW_SRC2_PLUS_STATES:
        if ticket_data.get('ticket_state') != 'active_change':
            return f'{state} live-window card requires an active_change source ticket; ready_for_real_packet cannot source a live/staged window'
        if source_truth_class not in POST_DECISION_SRC2_PLUS:
            return f'{state} live-window card requires SRC2+ source truth'
        if ticket_data.get('source_truth_required') not in POST_DECISION_SRC2_PLUS:
            return f'{state} live-window card requires source ticket with SRC2+ requirement'
        if parsed['window_day_count'] < 1 or parsed['allowed_activity_count'] < 1:
            return f'{state} live-window card requires at least one day and one allowed activity'
        if parsed['evidence_readout_count'] < 1:
            return f'{state} live-window card requires at least one aggregate readout class'
        for key in ['no_expansion_confirmed', 'human_pause_confirmed', 'fallback_route_confirmed']:
            if controls.get(key) is not True:
                return f'window_controls.{key} must be true for live/staged window states'
    if state == 'active' and ticket_data.get('live_window_required') is not True:
        return 'active live-window card requires source ticket live_window_required=true'

    risk_flags = manifest.get('risk_flags')
    if not isinstance(risk_flags, dict):
        return 'risk_flags must be an object'
    for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']:
        if risk_flags.get(key) is not False:
            return f'risk_flags.{key} must be false for live-window card routing'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_post_decision_ticket_text', 'copies_contact_details']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('contains_window_counts_hashes_and_routes_only') is not True:
        return 'content_minimization.contains_window_counts_hashes_and_routes_only must be true'
    if content.get('source_post_decision_ticket_revalidated') is not True:
        return 'content_minimization.source_post_decision_ticket_revalidated must be true'
    if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-end-of-window-readout-disposition-gate.md':
        return 'required_next_surface must route to the end-of-window readout gate'
    if manifest.get('readout_effect') != 'may_source_end_of_window_readout_only_after_terminal_window_state':
        return 'readout_effect must preserve terminal-state readout-only routing'
    expected_effect = 'does_not_modify_service_records_or_public_summaries_without_readout'
    if manifest.get('live_window_card_effect') != expected_effect:
        return 'live_window_card_effect must block service/public changes without a readout'
    readout_states = manifest.get('readout_ready_states')
    if sorted(LIVE_WINDOW_READOUT_READY_STATES) != readout_states:
        return 'readout_ready_states must name the bounded terminal states'
    return None


EXPECTED_LIVE_WINDOW_TERMINAL_BRIEF_FIELDS = {
    'brief_type': 'FT-0181-live-window-terminal-state-brief',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'brief_state': 'TERMINAL_STATE_BRIEF_PREPARED_NOT_RECORDED',
    'acceptance_state': 'NOT_ACCEPTED',
    'terminal_card_effect': 'does_not_record_live_window_card',
    'readout_effect': 'does_not_record_readout',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'required_next_surface': 'docs/30-operations/ft0181-live-window-stop-rollback-card.md',
    'ft0181_status': 'live',
}
LIVE_WINDOW_TERMINAL_BRIEF_SOURCE_STATES = {'staged', 'active'}
LIVE_WINDOW_TERMINAL_BRIEF_COMMAND_STATES = {
    'paused_stop_state': 'paused',
    'rolled_back_stop_state': 'rolled-back',
    'completed_no_closure': 'completed-no-closure',
    'quarantined_stop_state': 'quarantined',
}


def owner_live_window_terminal_brief_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a live-window terminal-state brief cannot route card closure.

    The terminal-state brief is a scratch-local execution bridge from a staged or
    active live-window card to a human-entered terminal card command. It must not
    record the terminal card or readout; it only preserves card hashes/counts and
    bounded command skeletons so nonterminal live-window work does not stall or
    drift into service-record/public/closure language.
    """
    if not isinstance(manifest, dict):
        return 'live-window terminal-state brief is not an object'
    for key, expected in EXPECTED_LIVE_WINDOW_TERMINAL_BRIEF_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('brief_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'brief_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    ceiling = str(manifest.get('claim_ceiling') or '')
    for phrase in ['not a live-window card', 'not a readout', 'not evidence', 'not closure evidence']:
        if phrase not in ceiling.lower():
            return f'claim_ceiling must preserve {phrase}'

    source = manifest.get('source_live_window_card')
    if not isinstance(source, dict):
        return 'source_live_window_card must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_live_window_card.reference must be a non-empty archive-relative scratch path'
    card_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(card_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_live_window_card.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(card_path, archive_root=archive_root, field_name='source_live_window_card.reference')
    if lane_error:
        return lane_error
    if card_path.name != 'live-window-card.json' or not card_path.exists() or not card_path.is_file():
        return 'source_live_window_card.reference must point to an existing live-window-card.json file'
    try:
        card_data = json.loads(card_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_live_window_card.reference is not readable JSON'
    card_error = owner_live_window_card_integrity_error(card_data, archive_root=archive_root)
    if card_error:
        return 'source_live_window_card failed live-window-card integrity: ' + card_error
    if card_data.get('window_state') not in LIVE_WINDOW_TERMINAL_BRIEF_SOURCE_STATES:
        return 'source_live_window_card.window_state must be staged or active'
    if source.get('card_sha256') in {None, ''}:
        return 'source_live_window_card.card_sha256 must be recorded'
    if source.get('card_sha256') != _sha256_file(card_path):
        return 'source_live_window_card.card_sha256 does not match referenced live-window-card.json'
    for key in [
        'window_state',
        'source_truth_class',
        'public_claim_ceiling',
        'window_controls',
        'source_post_decision_change_ticket',
        'acceptance_state',
        'evidence_state',
        'readout_effect',
        'live_window_card_effect',
    ]:
        if source.get(key) != card_data.get(key):
            return f'source_live_window_card.{key} does not match referenced live-window-card.json'
    if source.get('revalidated_for_terminal_brief') is not True:
        return 'source_live_window_card.revalidated_for_terminal_brief must be true'

    commands = manifest.get('terminal_card_command_templates')
    if not isinstance(commands, dict) or not commands:
        return 'terminal_card_command_templates must be a non-empty object'
    source_ticket = card_data.get('source_post_decision_change_ticket') if isinstance(card_data.get('source_post_decision_change_ticket'), dict) else {}
    ticket_ref = source_ticket.get('reference')
    if not isinstance(ticket_ref, str) or not ticket_ref:
        return 'source live-window card must preserve source ticket reference'
    controls = card_data.get('window_controls') if isinstance(card_data.get('window_controls'), dict) else {}
    count_tokens = {
        'SOURCE_TRUTH_CLASS': card_data.get('source_truth_class'),
        'WINDOW_DAY_COUNT': controls.get('window_day_count'),
        'ALLOWED_ACTIVITY_COUNT': controls.get('allowed_activity_count'),
        'PROHIBITED_ACTIVITY_COUNT': controls.get('prohibited_activity_count'),
        'STOP_TRIGGER_COUNT': controls.get('stop_trigger_count'),
        'ROLLBACK_STEP_COUNT': controls.get('rollback_step_count'),
        'ROLLBACK_OWNER_ROLE_COUNT': controls.get('rollback_owner_role_count'),
        'EVIDENCE_READOUT_COUNT': controls.get('evidence_readout_count'),
    }
    for key, state_token in LIVE_WINDOW_TERMINAL_BRIEF_COMMAND_STATES.items():
        command = commands.get(key)
        if not isinstance(command, str) or not command.startswith('make owner-live-window-card '):
            return f'terminal_card_command_templates.{key} must be an owner-live-window-card command'
        if f'WINDOW_STATE={state_token}' not in command:
            return f'terminal_card_command_templates.{key} missing WINDOW_STATE={state_token}'
        if f'TICKET={ticket_ref}' not in command and f"TICKET='{ticket_ref}'" not in command:
            return f'terminal_card_command_templates.{key} must reference the source post-decision ticket'
        for token_key, token_value in count_tokens.items():
            if f'{token_key}={token_value}' not in command:
                return f'terminal_card_command_templates.{key} missing {token_key}={token_value}'
        for token in ['NO_EXPANSION_CONFIRMED=1', 'HUMAN_PAUSE_CONFIRMED=1', 'FALLBACK_ROUTE_CONFIRMED=1', 'CONFIRM=human-recorded-bounded-live-window-card', 'OUT=scratch/field/ft0181/owner-live-window-cards/']:
            if token not in command:
                return f'terminal_card_command_templates.{key} missing {token}'
        lowered = command.lower()
        for forbidden in ['student id', 'learner id', 'student name', 'email address', '@', 'screenshot', 'api key', 'credential', 'claim text']:
            if forbidden in lowered:
                return f'terminal_card_command_templates.{key} includes forbidden raw/contact/claim term: {forbidden}'
    states = manifest.get('allowed_terminal_states')
    if not isinstance(states, list) or set(states) != {'paused', 'rolled_back', 'completed_no_closure', 'quarantined'}:
        return 'allowed_terminal_states must enumerate paused, rolled_back, completed_no_closure, and quarantined'
    boundary = str(manifest.get('terminal_boundary') or '').lower()
    if 'does not record' not in boundary or 'terminal' not in boundary or 'before readout' not in boundary:
        return 'terminal_boundary must state no terminal-card recording and readout precondition'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_live_window_card_text', 'copies_contact_details', 'copies_learner_identifiers_or_protected_facts']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('source_live_window_card_revalidated') is not True:
        return 'content_minimization.source_live_window_card_revalidated must be true'
    if content.get('contains_hashes_counts_and_command_skeletons_only') is not True:
        return 'content_minimization.contains_hashes_counts_and_command_skeletons_only must be true'
    forbidden_effects = manifest.get('forbidden_effects')
    if not isinstance(forbidden_effects, list):
        return 'forbidden_effects must be a list'
    for required in ['terminal-card-recording', 'readout-recording', 'service-record-mutation', 'public-claim-upgrade', 'custody-or-acceptance', 'lifecycle-or-closure']:
        if required not in forbidden_effects:
            return f'forbidden_effects must include {required}'
    return None


EXPECTED_LIVE_WINDOW_READOUT_BRIEF_FIELDS = {
    'brief_type': 'FT-0181-live-window-readout-brief',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'brief_state': 'READOUT_BRIEF_PREPARED_NOT_RECORDED',
    'acceptance_state': 'NOT_ACCEPTED',
    'readout_effect': 'does_not_record_readout',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'required_next_surface': 'docs/30-operations/ft0181-end-of-window-readout-disposition-gate.md',
    'ft0181_status': 'live',
}
LIVE_WINDOW_READOUT_BRIEF_REQUIRED_COMMAND_KEYS = {
    'primary',
}
LIVE_WINDOW_READOUT_BRIEF_DISPOSITION_ARGS = {
    'stopped': 'stopped',
    'rolled_back': 'rolled-back',
    'continue_bounded': 'continue-bounded',
    'rerun_narrower': 'rerun-narrower',
    'quarantine': 'quarantine',
    'no_change': 'no-change',
}


def owner_live_window_readout_brief_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a terminal live-window readout brief cannot route readout.

    The readout brief is a scratch-local execution bridge from a terminal
    live-window card to a human-entered aggregate readout command. It must not
    record a readout or dispatch; it only preserves card hashes/counts and
    state-matched command skeletons so terminal card work does not stall or drift
    into service-record/public/closure language.
    """
    if not isinstance(manifest, dict):
        return 'live-window readout brief is not an object'
    for key, expected in EXPECTED_LIVE_WINDOW_READOUT_BRIEF_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('brief_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'brief_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    ceiling = str(manifest.get('claim_ceiling') or '').lower()
    for phrase in ['not a readout', 'not evidence', 'not custody evidence', 'not closure evidence']:
        if phrase not in ceiling:
            return f'claim_ceiling must preserve {phrase}'

    source = manifest.get('source_live_window_card')
    if not isinstance(source, dict):
        return 'source_live_window_card must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_live_window_card.reference must be a non-empty archive-relative scratch path'
    card_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(card_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_live_window_card.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(card_path, archive_root=archive_root, field_name='source_live_window_card.reference')
    if lane_error:
        return lane_error
    if card_path.name != 'live-window-card.json' or not card_path.exists() or not card_path.is_file():
        return 'source_live_window_card.reference must point to an existing live-window-card.json file'
    try:
        card_data = json.loads(card_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_live_window_card.reference is not readable JSON'
    card_error = owner_live_window_card_integrity_error(card_data, archive_root=archive_root)
    if card_error:
        return 'source_live_window_card failed live-window-card integrity: ' + card_error
    source_state = card_data.get('window_state')
    if source_state not in LIVE_WINDOW_READOUT_TERMINAL_STATES:
        return 'source_live_window_card.window_state must be terminal/readout-ready'
    if source.get('card_sha256') != _sha256_file(card_path):
        return 'source_live_window_card.card_sha256 does not match referenced live-window-card.json'
    for key in [
        'window_state',
        'source_truth_class',
        'public_claim_ceiling',
        'window_controls',
        'acceptance_state',
        'evidence_state',
        'readout_effect',
        'live_window_card_effect',
        'source_post_decision_change_ticket',
    ]:
        if source.get(key) != card_data.get(key):
            return f'source_live_window_card.{key} does not match referenced live-window-card.json'
    if source.get('revalidated_for_live_window_readout_brief') is not True:
        return 'source_live_window_card.revalidated_for_live_window_readout_brief must be true'

    preferred = manifest.get('preferred_readout_disposition')
    allowed = manifest.get('allowed_readout_dispositions')
    expected_allowed = sorted(LIVE_WINDOW_STATE_TO_DISPOSITIONS.get(str(source_state), set()))
    if allowed != expected_allowed:
        return 'allowed_readout_dispositions must match source card terminal state'
    if preferred not in expected_allowed:
        return 'preferred_readout_disposition must be allowed for source card terminal state'

    commands = manifest.get('readout_command_templates')
    if not isinstance(commands, dict) or not commands:
        return 'readout_command_templates must be a non-empty object'
    for required in LIVE_WINDOW_READOUT_BRIEF_REQUIRED_COMMAND_KEYS:
        if required not in commands:
            return f'readout_command_templates must include {required}'
    controls = card_data.get('window_controls') if isinstance(card_data.get('window_controls'), dict) else {}
    expected_min_readout = controls.get('evidence_readout_count')
    expected_role_count = max(2, int(controls.get('rollback_owner_role_count') or 1))
    for key, command in commands.items():
        if not isinstance(command, str) or not command.startswith('make owner-live-window-readout '):
            return f'readout_command_templates.{key} must be an owner-live-window-readout command'
        if f'CARD={ref}' not in command and f"CARD='{ref}'" not in command:
            return f'readout_command_templates.{key} must reference the source terminal card'
        if f'SOURCE_TRUTH_CLASS={card_data.get("source_truth_class")}' not in command:
            return f'readout_command_templates.{key} must preserve source truth class'
        if isinstance(expected_min_readout, int) and f'AGGREGATE_EVIDENCE_READ_COUNT={expected_min_readout}' not in command:
            return f'readout_command_templates.{key} must preserve source evidence readout count'
        if f'REVIEWER_ROLE_COUNT={expected_role_count}' not in command:
            return f'readout_command_templates.{key} must preserve reviewer role count minimum'
        for token in ['NO_PUBLIC_CLAIM_UPGRADE=1', 'NO_SERVICE_RECORD_EDIT=1', 'NO_LIFECYCLE_CHANGE=1', 'NO_CLOSURE_FROM_READOUT=1', 'CONFIRM=human-recorded-aggregate-readout-no-closure', 'OUT=scratch/field/ft0181/owner-live-window-readouts/']:
            if token not in command:
                return f'readout_command_templates.{key} missing {token}'
        disposition = None
        for normalized, arg in LIVE_WINDOW_READOUT_BRIEF_DISPOSITION_ARGS.items():
            if f'WINDOW_DISPOSITION={arg}' in command:
                disposition = normalized
                break
        if disposition is None:
            return f'readout_command_templates.{key} must include a valid WINDOW_DISPOSITION'
        if disposition not in expected_allowed:
            return f'readout_command_templates.{key} disposition {disposition} is not allowed for source state {source_state}'
        if disposition in {'continue_bounded', 'rerun_narrower'} and 'DECISION_DELTA_COUNT=1' not in command:
            return f'readout_command_templates.{key} continue/rerun route must include a decision delta'
        if disposition in {'rerun_narrower', 'no_change'} and 'FIELD_TRIM_COUNT=1' not in command:
            return f'readout_command_templates.{key} rerun/no-change route must include a field trim'
        lowered = command.lower()
        for forbidden in ['student id', 'learner id', 'student name', 'email address', '@', 'screenshot', 'api key', 'credential', 'claim text', 'live notes']:
            if forbidden in lowered:
                return f'readout_command_templates.{key} includes forbidden raw/contact/claim term: {forbidden}'
    boundary = str(manifest.get('readout_boundary') or '').lower()
    if 'does not record' not in boundary or 'readout' not in boundary or 'post-readout' not in boundary:
        return 'readout_boundary must state no readout recording and post-readout precondition'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_live_window_notes', 'copies_contact_details', 'copies_learner_identifiers_or_protected_facts']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('source_live_window_card_revalidated') is not True:
        return 'content_minimization.source_live_window_card_revalidated must be true'
    if content.get('contains_hashes_counts_and_command_skeletons_only') is not True:
        return 'content_minimization.contains_hashes_counts_and_command_skeletons_only must be true'
    forbidden_effects = manifest.get('forbidden_effects')
    if not isinstance(forbidden_effects, list):
        return 'forbidden_effects must be a list'
    for required in ['readout-recording', 'post-readout-action-dispatch', 'service-record-mutation', 'public-claim-upgrade', 'custody-or-acceptance', 'lifecycle-or-closure']:
        if required not in forbidden_effects:
            return f'forbidden_effects must include {required}'
    return None


EXPECTED_LIVE_WINDOW_READOUT_FIELDS = {
    'readout_type': 'FT-0181-live-window-readout-record',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'ft0181_status': 'live',
}
LIVE_WINDOW_READOUT_STATES = {
    'readout_complete',
    'quarantined',
}
LIVE_WINDOW_READOUT_DISPOSITIONS = {
    'stopped',
    'rolled_back',
    'continue_bounded',
    'rerun_narrower',
    'quarantine',
    'no_change',
}
LIVE_WINDOW_READOUT_SOURCE_TRUTH_CLASSES = {'SRC2', 'SRC3', 'SRC4'}
LIVE_WINDOW_READOUT_TERMINAL_STATES = {'paused', 'rolled_back', 'completed_no_closure', 'quarantined'}
LIVE_WINDOW_STATE_TO_DISPOSITIONS = {
    'paused': {'stopped', 'rerun_narrower', 'quarantine'},
    'rolled_back': {'rolled_back', 'stopped', 'quarantine'},
    'completed_no_closure': {'continue_bounded', 'rerun_narrower', 'no_change', 'stopped'},
    'quarantined': {'quarantine'},
}


def owner_live_window_readout_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a live-window readout cannot source post-readout dispatch.

    The readout is the executable firebreak after a terminal live-window card.
    It may summarize aggregate count classes and a bounded disposition, but it
    must not become evidence, acceptance, closure, service-record mutation, or
    public-claim support. The source live-window card is re-read and hash-checked
    so copied or edited local readouts cannot launder a nonterminal card.
    """
    if not isinstance(manifest, dict):
        return 'live-window readout is not an object'
    for key, expected in EXPECTED_LIVE_WINDOW_READOUT_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('readout_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'readout_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-recorded-aggregate-readout-no-closure':
        return 'operator_confirmation must be human-recorded-aggregate-readout-no-closure'
    if manifest.get('readout_state') not in LIVE_WINDOW_READOUT_STATES:
        return f'readout_state={manifest.get("readout_state")!r} is not allowed'
    disposition = manifest.get('window_disposition')
    if disposition not in LIVE_WINDOW_READOUT_DISPOSITIONS:
        return f'window_disposition={disposition!r} is not allowed'
    source_truth_class = manifest.get('source_truth_class')
    if source_truth_class not in LIVE_WINDOW_READOUT_SOURCE_TRUTH_CLASSES:
        return f'source_truth_class={source_truth_class!r} must be SRC2/SRC3/SRC4 for a real terminal-window readout'
    if manifest.get('closure_permitted') is not False:
        return 'closure_permitted must be false'
    ceiling = str(manifest.get('claim_ceiling') or '')
    if 'not evidence' not in ceiling.lower() or 'does not close' not in ceiling.lower():
        return 'claim_ceiling must preserve not-evidence and non-closure boundaries'

    source = manifest.get('source_live_window_card')
    if not isinstance(source, dict):
        return 'source_live_window_card must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_live_window_card.reference must be a non-empty scratch path'
    card_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(card_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_live_window_card.reference must stay under scratch'
    lane_error = field_scratch_lane_error(card_path, archive_root=archive_root, field_name='source_live_window_card.reference')
    if lane_error:
        return lane_error
    if card_path.name != 'live-window-card.json' or not card_path.exists() or not card_path.is_file():
        return 'source_live_window_card.reference must point to an existing live-window-card.json file'
    try:
        card_data = json.loads(card_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_live_window_card.reference is not readable JSON'
    card_error = owner_live_window_card_integrity_error(card_data, archive_root=archive_root)
    if card_error:
        return 'source_live_window_card failed live-window card integrity: ' + card_error
    expected_hash = _sha256_file(card_path)
    if source.get('card_sha256') != expected_hash:
        return 'source_live_window_card.card_sha256 does not match referenced card'
    for key in [
        'window_state',
        'source_truth_class',
        'public_claim_ceiling',
        'acceptance_state',
        'evidence_state',
        'readout_effect',
        'live_window_card_effect',
    ]:
        if source.get(key) != card_data.get(key):
            return f'source_live_window_card.{key} does not match referenced card'
    if source.get('revalidated_for_live_window_readout') is not True:
        return 'source_live_window_card.revalidated_for_live_window_readout must be true'
    source_state = card_data.get('window_state')
    if source_state not in LIVE_WINDOW_READOUT_TERMINAL_STATES:
        return f'terminal readout requires source card state in {sorted(LIVE_WINDOW_READOUT_TERMINAL_STATES)}, not {source_state!r}'
    allowed_dispositions = LIVE_WINDOW_STATE_TO_DISPOSITIONS.get(str(source_state), set())
    if disposition not in allowed_dispositions:
        return f'window_disposition={disposition!r} is not allowed for source card state {source_state!r}'
    if source_truth_class != card_data.get('source_truth_class'):
        return 'readout source_truth_class must match terminal live-window card source_truth_class'
    if manifest.get('readout_state') == 'quarantined' and disposition != 'quarantine':
        return 'quarantined readout_state requires quarantine disposition'

    counts = manifest.get('readout_counts')
    if not isinstance(counts, dict):
        return 'readout_counts must be an object'
    parsed: dict[str, int] = {}
    for field, minimum, upper in [
        ('aggregate_evidence_read_count', 1, 7),
        ('claim_family_effect_count', 1, 8),
        ('decision_delta_count', 0, 8),
        ('field_trim_count', 0, 8),
        ('reviewer_role_count', 2, 5),
        ('unresolved_disagreement_count', 0, 5),
    ]:
        value, value_error = _non_negative_int(counts.get(field), f'readout_counts.{field}')
        if value_error:
            return value_error
        assert value is not None
        if value < minimum or value > upper:
            return f'readout_counts.{field} must be between {minimum} and {upper}'
        parsed[field] = value
    source_readout_count = card_data.get('window_controls', {}).get('evidence_readout_count')
    if isinstance(source_readout_count, int) and parsed['aggregate_evidence_read_count'] < source_readout_count:
        return 'readout_counts.aggregate_evidence_read_count cannot be below source card evidence_readout_count'
    source_roles = card_data.get('window_controls', {}).get('rollback_owner_role_count')
    if isinstance(source_roles, int) and parsed['reviewer_role_count'] < max(2, source_roles):
        return 'readout_counts.reviewer_role_count must cover source card owner/reviewer role count and at least two reviewers'
    if disposition in {'continue_bounded', 'rerun_narrower'} and parsed['decision_delta_count'] < 1:
        return 'continue/rerun readouts require at least one bounded decision delta count'
    if disposition in {'rerun_narrower', 'no_change'} and parsed['field_trim_count'] < 1:
        return 'rerun/no_change readouts must trim at least one field before the next request'

    for field in ['no_public_claim_upgrade', 'no_service_record_edit', 'no_lifecycle_change', 'no_closure_from_readout']:
        if manifest.get(field) is not True:
            return f'{field} must be true'
    risk_flags = manifest.get('risk_flags')
    if not isinstance(risk_flags, dict):
        return 'risk_flags must be an object'
    for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']:
        if risk_flags.get(key) is not False:
            return f'risk_flags.{key} must be false for live-window readout routing'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_live_window_notes', 'copies_contact_details']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('contains_aggregate_counts_disposition_hashes_and_routes_only') is not True:
        return 'content_minimization.contains_aggregate_counts_disposition_hashes_and_routes_only must be true'
    if content.get('source_live_window_card_revalidated') is not True:
        return 'content_minimization.source_live_window_card_revalidated must be true'
    if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-post-readout-action-dispatch.md':
        return 'required_next_surface must route to post-readout action dispatch'
    if manifest.get('readout_effect') != 'may_source_post_readout_action_dispatch_only':
        return 'readout_effect must limit output to post-readout dispatch only'
    if manifest.get('public_language_effect') != 'does_not_authorize_public_language_without_dispatch':
        return 'public_language_effect must block public language until dispatch'
    boundary = str(manifest.get('closure_boundary') or '').lower()
    if 'does not close ft-0181' not in boundary or 'does not prove' not in boundary:
        return 'closure_boundary must say it does not close FT-0181 and does not prove service claims'

    return None


EXPECTED_POST_READOUT_ACTION_BRIEF_FIELDS = {
    'brief_type': 'FT-0181-post-readout-action-brief',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'acceptance_state': 'NOT_ACCEPTED',
    'action_effect': 'does_not_record_post_readout_action',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'service_record_effect': 'does_not_edit_service_records',
    'lifecycle_effect': 'does_not_change_lifecycle_state',
    'ft0181_status': 'live',
}
POST_READOUT_ACTION_BRIEF_REQUIRED_COMMAND_KEYS = {'primary'}
POST_READOUT_ACTION_BRIEF_LANE_ARGS = {
    'blocked_no_real_packet': 'blocked-no-real-packet',
    'stop': 'stop',
    'rollback_confirmed': 'rollback-confirmed',
    'rerun_narrower': 'rerun-narrower',
    'continue_same_ceiling': 'continue-same-ceiling',
    'quarantine': 'quarantine',
    'no_change_trim': 'no-change-trim',
}
POST_READOUT_ACTION_BRIEF_NEXT_ASK_BY_LANE = {
    'blocked_no_real_packet': 'owner-packet-route-repair',
    'stop': 'fallback-availability-check',
    'rollback_confirmed': 'fallback-availability-check',
    'rerun_narrower': 'rerun-narrower-owner-packet',
    'continue_same_ceiling': 'bounded-owner-recheck',
    'quarantine': 'quarantine-resolution-ask',
    'no_change_trim': 'no-new-ask-with-trim-record',
}
POST_READOUT_ACTION_BRIEF_PUBLIC_ACTION_BY_LANE = {
    'blocked_no_real_packet': 'frozen-example-only',
    'stop': 'suppress-public-language',
    'rollback_confirmed': 'narrow-existing-language',
    'rerun_narrower': 'frozen-example-only',
    'continue_same_ceiling': 'frozen-example-only',
    'quarantine': 'suppress-public-language',
    'no_change_trim': 'no-public-language-change',
}


def owner_post_readout_action_brief_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a post-readout action brief cannot route dispatch.

    The action brief is a scratch-local execution bridge from a terminal
    live-window readout to a human-entered post-readout action dispatch. It must
    not record the dispatch or owner-held action; it only preserves readout hashes,
    lane mapping, due/recheck date, and bounded command skeletons so the field rail
    does not stall after a readout or drift into closure/service-record language.
    """
    if not isinstance(manifest, dict):
        return 'post-readout action brief is not an object'
    for key, expected in EXPECTED_POST_READOUT_ACTION_BRIEF_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('brief_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'brief_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    error = _parse_iso_date(manifest.get('as_of_date'), 'as_of_date')
    if error:
        return error
    error = _parse_iso_date(manifest.get('proposed_due_or_recheck_date'), 'proposed_due_or_recheck_date')
    if error:
        return error
    ceiling = str(manifest.get('claim_ceiling') or '').lower()
    for phrase in ['not a dispatch', 'not evidence', 'not custody evidence', 'not closure evidence', 'not public-summary support']:
        if phrase not in ceiling:
            return f'claim_ceiling must preserve {phrase}'

    source = manifest.get('source_live_window_readout')
    if not isinstance(source, dict):
        return 'source_live_window_readout must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_live_window_readout.reference must be a non-empty archive-relative scratch path'
    readout_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(readout_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_live_window_readout.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(readout_path, archive_root=archive_root, field_name='source_live_window_readout.reference')
    if lane_error:
        return lane_error
    if readout_path.name != 'live-window-readout.json' or not readout_path.exists() or not readout_path.is_file():
        return 'source_live_window_readout.reference must point to an existing live-window-readout.json file'
    try:
        readout_data = json.loads(readout_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_live_window_readout.reference is not readable JSON'
    readout_error = owner_live_window_readout_integrity_error(readout_data, archive_root=archive_root)
    if readout_error:
        return 'source_live_window_readout failed live-window-readout integrity: ' + readout_error
    if source.get('readout_sha256') != _sha256_file(readout_path):
        return 'source_live_window_readout.readout_sha256 does not match referenced live-window-readout.json'
    for key in [
        'readout_state',
        'window_disposition',
        'source_truth_class',
        'public_claim_ceiling',
        'acceptance_state',
        'evidence_state',
        'readout_effect',
        'closure_effect',
        'readout_counts',
        'source_live_window_card',
    ]:
        if source.get(key) != readout_data.get(key):
            return f'source_live_window_readout.{key} does not match referenced live-window-readout.json'
    if source.get('revalidated_for_post_readout_action_brief') is not True:
        return 'source_live_window_readout.revalidated_for_post_readout_action_brief must be true'

    disposition = readout_data.get('window_disposition')
    expected_lane = READOUT_DISPOSITION_TO_ACTION_LANE.get(str(disposition))
    if expected_lane is None:
        return f'source_live_window_readout.window_disposition={disposition!r} cannot map to a dispatch lane'
    if manifest.get('primary_dispatch_lane') != expected_lane:
        return 'primary_dispatch_lane must match source readout disposition'
    if manifest.get('owner_action_class') != POST_READOUT_OWNER_ACTION_BY_LANE.get(expected_lane):
        return 'owner_action_class must match primary dispatch lane'
    if manifest.get('next_evidence_ask_class') != POST_READOUT_ACTION_BRIEF_NEXT_ASK_BY_LANE.get(expected_lane):
        return 'next_evidence_ask_class must match primary dispatch lane'
    if manifest.get('next_evidence_ask_class') not in POST_READOUT_NEXT_ASK_CLASSES:
        return 'next_evidence_ask_class must be an allowed post-readout next ask class'
    if manifest.get('public_language_action') != POST_READOUT_ACTION_BRIEF_PUBLIC_ACTION_BY_LANE.get(expected_lane):
        return 'public_language_action must match primary dispatch lane'
    if manifest.get('public_language_action') not in POST_READOUT_PUBLIC_LANGUAGE_ACTIONS:
        return 'public_language_action must be an allowed post-readout public language action'
    allowed_lanes = manifest.get('allowed_dispatch_lanes')
    if allowed_lanes != [expected_lane]:
        return 'allowed_dispatch_lanes must contain only the lane mapped from the source readout'

    commands = manifest.get('post_readout_action_command_templates')
    if not isinstance(commands, dict) or not commands:
        return 'post_readout_action_command_templates must be a non-empty object'
    for required in POST_READOUT_ACTION_BRIEF_REQUIRED_COMMAND_KEYS:
        if required not in commands:
            return f'post_readout_action_command_templates must include {required}'
    source_truth = readout_data.get('source_truth_class')
    readout_counts = readout_data.get('readout_counts') if isinstance(readout_data.get('readout_counts'), dict) else {}
    expected_role_count = max(2, int(readout_counts.get('reviewer_role_count') or 2))
    for key, command in commands.items():
        if not isinstance(command, str) or not command.startswith('make owner-post-readout-action '):
            return f'post_readout_action_command_templates.{key} must be an owner-post-readout-action command'
        if f'READOUT={ref}' not in command and f"READOUT='{ref}'" not in command:
            return f'post_readout_action_command_templates.{key} must reference the source readout'
        if f'DISPATCH_LANE={POST_READOUT_ACTION_BRIEF_LANE_ARGS[expected_lane]}' not in command:
            return f'post_readout_action_command_templates.{key} must preserve mapped dispatch lane'
        if f'SOURCE_TRUTH_CLASS={source_truth}' not in command:
            return f'post_readout_action_command_templates.{key} must preserve source truth class'
        if f'REVIEWER_ROLE_COUNT={expected_role_count}' not in command:
            return f'post_readout_action_command_templates.{key} must preserve reviewer role count minimum'
        if f'OWNER_ACTION_CLASS={POST_READOUT_OWNER_ACTION_BY_LANE[expected_lane]}' not in command:
            return f'post_readout_action_command_templates.{key} must include owner action class for lane'
        if f'NEXT_EVIDENCE_ASK_CLASS={POST_READOUT_ACTION_BRIEF_NEXT_ASK_BY_LANE[expected_lane]}' not in command:
            return f'post_readout_action_command_templates.{key} must include next evidence ask class for lane'
        if f'PUBLIC_LANGUAGE_ACTION={POST_READOUT_ACTION_BRIEF_PUBLIC_ACTION_BY_LANE[expected_lane]}' not in command:
            return f'post_readout_action_command_templates.{key} must include public language action for lane'
        for token in ['NO_EXPANSION_CONFIRMED=1', 'NO_PUBLIC_CLAIM_UPGRADE=1', 'NO_SERVICE_RECORD_EDIT=1', 'NO_LIFECYCLE_CHANGE=1', 'NO_CLOSURE_FROM_DISPATCH=1', 'CONFIRM=human-recorded-post-readout-action-no-closure', 'OUT=scratch/field/ft0181/owner-post-readout-actions/']:
            if token not in command:
                return f'post_readout_action_command_templates.{key} missing {token}'
        if 'make owner-post-readout-recheck ' in command or 'make owner-post-readout-context-receipt ' in command:
            return f'post_readout_action_command_templates.{key} must not jump to recheck or context receipt'
        lowered = command.lower()
        for forbidden in ['student id', 'learner id', 'student name', 'email address', '@', 'screenshot', 'api key', 'credential', 'claim text', 'live notes']:
            if forbidden in lowered:
                return f'post_readout_action_command_templates.{key} includes forbidden raw/contact/claim term: {forbidden}'
    boundary = str(manifest.get('dispatch_boundary') or '').lower()
    if 'does not record' not in boundary or 'post-readout action dispatch' not in boundary or 'human must record' not in boundary:
        return 'dispatch_boundary must state no dispatch recording and human-record precondition'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_live_window_notes', 'copies_contact_details', 'copies_public_claim_text', 'copies_learner_identifiers_or_protected_facts']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('source_live_window_readout_revalidated') is not True:
        return 'content_minimization.source_live_window_readout_revalidated must be true'
    if content.get('contains_hashes_counts_dates_and_command_skeletons_only') is not True:
        return 'content_minimization.contains_hashes_counts_dates_and_command_skeletons_only must be true'
    forbidden_effects = manifest.get('forbidden_effects')
    if not isinstance(forbidden_effects, list):
        return 'forbidden_effects must be a list'
    for required in ['post-readout-action-dispatch-recording', 'owner-action-completion', 'service-record-mutation', 'public-claim-upgrade', 'custody-or-acceptance', 'lifecycle-or-closure']:
        if required not in forbidden_effects:
            return f'forbidden_effects must include {required}'
    if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-post-readout-action-dispatch.md':
        return 'required_next_surface must route to post-readout action dispatch'
    return None


POST_READOUT_ACTION_DISPATCH_LANES = {
    'blocked_no_real_packet',
    'stop',
    'rollback_confirmed',
    'rerun_narrower',
    'continue_same_ceiling',
    'quarantine',
    'no_change_trim',
}
POST_READOUT_ACTION_STATES = {
    'DISPATCH_RECORDED_NOT_CLOSURE',
    'BLOCKED_NO_REAL_READOUT',
    'QUARANTINED',
    'ROLLBACK_CONFIRMED_NOT_CLOSURE',
}
READOUT_DISPOSITION_TO_ACTION_LANE = {
    'blocked_no_real_packet': 'blocked_no_real_packet',
    'stopped': 'stop',
    'rolled_back': 'rollback_confirmed',
    'continue_bounded': 'continue_same_ceiling',
    'rerun_narrower': 'rerun_narrower',
    'quarantine': 'quarantine',
    'no_change': 'no_change_trim',
}
POST_READOUT_OWNER_ACTION_BY_LANE = {
    'blocked_no_real_packet': 'return-to-owner-packet-request',
    'stop': 'stop-service-path',
    'rollback_confirmed': 'rollback-to-human-fallback',
    'rerun_narrower': 'rerun-narrower-window',
    'continue_same_ceiling': 'continue-within-same-ceiling',
    'quarantine': 'quarantine-evidence-path',
    'no_change_trim': 'trim-no-change-fields',
}
POST_READOUT_NEXT_ASK_CLASSES = {
    'bounded-owner-recheck',
    'rerun-narrower-owner-packet',
    'no-new-ask-with-trim-record',
    'quarantine-resolution-ask',
    'fallback-availability-check',
    'owner-packet-route-repair',
}
POST_READOUT_PUBLIC_LANGUAGE_ACTIONS = {
    'frozen-example-only',
    'narrow-existing-language',
    'suppress-public-language',
    'no-public-language-change',
}
EXPECTED_POST_READOUT_ACTION_FIELDS = {
    'action_type': 'FT-0181-post-readout-action-dispatch',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_permitted': False,
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'does_not_upgrade_public_claims',
    'service_record_effect': 'does_not_edit_service_records_without_separate_owner_action',
    'lifecycle_effect': 'does_not_change_lifecycle_without_separate_owner_action',
    'ft0181_status': 'live',
    'post_readout_action_effect': 'may_source_owner_action_or_recheck_only',
}


def owner_post_readout_action_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a post-readout action dispatch cannot be the next field stop.

    The dispatch is the executable firebreak after a terminal live-window readout.
    It converts a readout disposition into one bounded owner-action/recheck lane,
    but it must not mutate service records, lifecycle state, public language, custody,
    acceptance, or closure by itself. The source readout is re-read and hash-checked
    so copied/edited dispatch records cannot launder a different window result.
    """
    if not isinstance(manifest, dict):
        return 'post-readout action dispatch is not an object'
    for key, expected in EXPECTED_POST_READOUT_ACTION_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('action_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'action_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    error = _parse_iso_date(manifest.get('due_or_recheck_date'), 'due_or_recheck_date')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-recorded-post-readout-action-no-closure':
        return 'operator_confirmation must be human-recorded-post-readout-action-no-closure'
    state = manifest.get('dispatch_state')
    if state not in POST_READOUT_ACTION_STATES:
        return f'dispatch_state={state!r} is not allowed'
    lane = manifest.get('dispatch_lane')
    if lane not in POST_READOUT_ACTION_DISPATCH_LANES:
        return f'dispatch_lane={lane!r} is not allowed'
    source_truth_class = manifest.get('source_truth_class')
    if source_truth_class not in LIVE_WINDOW_READOUT_SOURCE_TRUTH_CLASSES:
        return f'source_truth_class={source_truth_class!r} must be SRC2/SRC3/SRC4 from a real readout'
    owner_action = manifest.get('owner_action_class')
    expected_owner_action = POST_READOUT_OWNER_ACTION_BY_LANE.get(str(lane))
    if owner_action != expected_owner_action:
        return f'owner_action_class={owner_action!r} must match dispatch_lane {lane!r}: {expected_owner_action!r}'
    next_ask_class = manifest.get('next_evidence_ask_class')
    if next_ask_class not in POST_READOUT_NEXT_ASK_CLASSES:
        return f'next_evidence_ask_class={next_ask_class!r} is not allowed'
    expected_next_ask = POST_READOUT_ACTION_BRIEF_NEXT_ASK_BY_LANE.get(str(lane))
    if next_ask_class != expected_next_ask:
        return f'next_evidence_ask_class={next_ask_class!r} must match dispatch_lane {lane!r}: {expected_next_ask!r}'
    public_action = manifest.get('public_language_action')
    if public_action not in POST_READOUT_PUBLIC_LANGUAGE_ACTIONS:
        return f'public_language_action={public_action!r} is not allowed'
    expected_public_action = POST_READOUT_ACTION_BRIEF_PUBLIC_ACTION_BY_LANE.get(str(lane))
    if public_action != expected_public_action:
        return f'public_language_action={public_action!r} must match dispatch_lane {lane!r}: {expected_public_action!r}'

    source = manifest.get('source_live_window_readout')
    if not isinstance(source, dict):
        return 'source_live_window_readout must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_live_window_readout.reference must be a non-empty scratch path'
    readout_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(readout_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_live_window_readout.reference must stay under scratch'
    lane_error = field_scratch_lane_error(readout_path, archive_root=archive_root, field_name='source_live_window_readout.reference')
    if lane_error:
        return lane_error
    if readout_path.name != 'live-window-readout.json' or not readout_path.exists() or not readout_path.is_file():
        return 'source_live_window_readout.reference must point to an existing live-window-readout.json file'
    try:
        readout_data = json.loads(readout_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_live_window_readout.reference is not readable JSON'
    readout_error = owner_live_window_readout_integrity_error(readout_data, archive_root=archive_root)
    if readout_error:
        return 'source_live_window_readout failed live-window readout integrity: ' + readout_error
    expected_hash = _sha256_file(readout_path)
    if source.get('readout_sha256') != expected_hash:
        return 'source_live_window_readout.readout_sha256 does not match referenced readout'
    for key in [
        'readout_state',
        'window_disposition',
        'source_truth_class',
        'public_claim_ceiling',
        'acceptance_state',
        'evidence_state',
        'readout_effect',
        'closure_effect',
    ]:
        if source.get(key) != readout_data.get(key):
            return f'source_live_window_readout.{key} does not match referenced readout'
    if source.get('revalidated_for_post_readout_action') is not True:
        return 'source_live_window_readout.revalidated_for_post_readout_action must be true'
    expected_lane = READOUT_DISPOSITION_TO_ACTION_LANE.get(readout_data.get('window_disposition'))
    if expected_lane != lane:
        return f'dispatch_lane={lane!r} does not match source readout disposition {readout_data.get("window_disposition")!r}'
    if source_truth_class != readout_data.get('source_truth_class'):
        return 'source_truth_class must match the source live-window readout'
    if lane == 'quarantine' and state != 'QUARANTINED':
        return 'quarantine lane requires QUARANTINED dispatch_state'
    if lane == 'rollback_confirmed' and state != 'ROLLBACK_CONFIRMED_NOT_CLOSURE':
        return 'rollback_confirmed lane requires ROLLBACK_CONFIRMED_NOT_CLOSURE dispatch_state'
    if lane == 'blocked_no_real_packet' and state != 'BLOCKED_NO_REAL_READOUT':
        return 'blocked_no_real_packet lane requires BLOCKED_NO_REAL_READOUT dispatch_state'

    counts = manifest.get('dispatch_counts')
    if not isinstance(counts, dict):
        return 'dispatch_counts must be an object'
    parsed: dict[str, int] = {}
    for field, minimum, upper in [
        ('allowed_action_count', 0, 5),
        ('prohibited_action_count', 2, 10),
        ('field_to_reask_count', 0, 8),
        ('field_to_drop_count', 0, 8),
        ('reviewer_role_count', 2, 5),
        ('unresolved_disagreement_count', 0, 5),
    ]:
        value, value_error = _non_negative_int(counts.get(field), f'dispatch_counts.{field}')
        if value_error:
            return value_error
        assert value is not None
        if value < minimum or value > upper:
            return f'dispatch_counts.{field} must be between {minimum} and {upper}'
        parsed[field] = value
    if lane not in {'blocked_no_real_packet', 'quarantine'} and parsed['allowed_action_count'] < 1:
        return f'{lane} requires at least one allowed action count'
    if lane in {'rerun_narrower', 'no_change_trim'} and parsed['field_to_drop_count'] < 1:
        return f'{lane} requires at least one field_to_drop_count'
    if lane == 'rerun_narrower' and parsed['field_to_reask_count'] < 1:
        return 'rerun_narrower requires at least one field_to_reask_count'
    source_roles = readout_data.get('readout_counts', {}).get('reviewer_role_count')
    if isinstance(source_roles, int) and parsed['reviewer_role_count'] < source_roles:
        return 'dispatch_counts.reviewer_role_count cannot be below source readout reviewer_role_count'

    for field in [
        'no_expansion_confirmation',
        'no_public_claim_upgrade',
        'no_service_record_edit_from_dispatch',
        'no_lifecycle_change_from_dispatch',
        'no_closure_from_dispatch',
    ]:
        if manifest.get(field) is not True:
            return f'{field} must be true'
    risk_flags = manifest.get('risk_flags')
    if not isinstance(risk_flags, dict):
        return 'risk_flags must be an object'
    for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']:
        if risk_flags.get(key) is not False:
            return f'risk_flags.{key} must be false for post-readout action dispatch'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_live_window_notes', 'copies_contact_details', 'copies_public_claim_text']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('contains_action_classes_counts_hashes_and_due_dates_only') is not True:
        return 'content_minimization.contains_action_classes_counts_hashes_and_due_dates_only must be true'
    if content.get('source_live_window_readout_revalidated') is not True:
        return 'content_minimization.source_live_window_readout_revalidated must be true'

    ask = manifest.get('next_evidence_ask')
    if not isinstance(ask, dict):
        return 'next_evidence_ask must be an object'
    for field in ['owner_route_class', 'date_range_class', 'packet_ceiling', 'decision_question_class', 'field_minimization_rule', 'fallback_if_unavailable']:
        if not isinstance(ask.get(field), str) or not ask.get(field).strip():
            return f'next_evidence_ask.{field} must be a non-empty class label'
    ask_text = json.dumps(ask).lower() + ' ' + ' '.join(manifest.get('fields_to_reask_classes') or []).lower()
    for bad in RETURNED_CSV_SMOKE_MARKERS | {'raw learner', 'protected-route', 'protected facts', 'small-cell', 'security payload', 'vendor-authored outcome', 'full transcript'}:
        if bad in ask_text:
            return f'next evidence ask appears to request forbidden material: {bad}'
    drop_classes = manifest.get('fields_to_drop_classes')
    if not isinstance(drop_classes, list) or not all(isinstance(v, str) and v for v in drop_classes):
        return 'fields_to_drop_classes must be a non-empty string list'
    drop_text = ' '.join(drop_classes).lower()
    for phrase in ['raw', 'protected', 'small-cell', 'security', 'vendor']:
        if phrase not in drop_text:
            return f'fields_to_drop_classes must explicitly drop {phrase} material'
    reask_classes = manifest.get('fields_to_reask_classes')
    if not isinstance(reask_classes, list):
        return 'fields_to_reask_classes must be a list'
    if parsed['field_to_reask_count'] != len(reask_classes):
        return 'dispatch_counts.field_to_reask_count must equal len(fields_to_reask_classes)'
    if parsed['field_to_drop_count'] > len(drop_classes):
        return 'dispatch_counts.field_to_drop_count cannot exceed len(fields_to_drop_classes)'
    boundary = str(manifest.get('closure_boundary') or '').lower()
    if 'does not close ft-0181' not in boundary or 'does not prove' not in boundary:
        return 'closure_boundary must say it does not close FT-0181 and does not prove service claims'
    ceiling = str(manifest.get('claim_ceiling') or '').lower()
    if 'not evidence' not in ceiling or 'not closure evidence' not in ceiling or 'not public-summary support' not in ceiling:
        return 'claim_ceiling must preserve not-evidence, not-closure, and no public-summary support boundaries'
    if manifest.get('required_next_surface') != 'owner-held action/recheck outside archive, then rerun owner-field-next only with new real owner context':
        return 'required_next_surface must keep next action outside archive until new real owner context exists'
    return None


EXPECTED_POST_READOUT_RECHECK_BRIEF_FIELDS = {
    'brief_type': 'FT-0181-post-readout-recheck-brief',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'brief_state': 'POST_READOUT_RECHECK_BRIEF_PREPARED_NOT_RECHECKED',
    'acceptance_state': 'NOT_ACCEPTED',
    'recheck_effect': 'does_not_record_post_readout_recheck',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'none',
    'service_record_effect': 'does_not_edit_service_records',
    'lifecycle_effect': 'does_not_change_lifecycle_state',
    'ft0181_status': 'live',
}
POST_READOUT_RECHECK_BRIEF_REQUIRED_COMMAND_KEYS = {
    'primary',
    'no_new_owner_context',
    'new_owner_context_available',
    'owner_action_complete_no_closure',
    'route_blocked_no_owner',
}
POST_READOUT_RECHECK_BRIEF_OUTCOME_ARGS = {
    'no_new_owner_context': 'no-new-owner-context',
    'new_owner_context_available': 'new-owner-context-available',
    'owner_action_complete_no_closure': 'owner-action-complete-no-closure',
    'route_blocked_no_owner': 'route-blocked-no-owner',
}


def owner_post_readout_recheck_brief_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a post-readout recheck brief cannot route a due-date recheck.

    The recheck brief is a scratch-local execution bridge from a due post-readout
    action dispatch to a human-entered recheck record. It must not record the
    recheck, copy owner context, intake a CSV, mutate service records, move
    lifecycle state, upgrade public language, create custody/acceptance, or close
    FT-0181.
    """
    if not isinstance(manifest, dict):
        return 'post-readout recheck brief is not an object'
    for key, expected in EXPECTED_POST_READOUT_RECHECK_BRIEF_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('brief_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'brief_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    error = _parse_iso_date(manifest.get('as_of_date'), 'as_of_date')
    if error:
        return error
    error = _parse_iso_date(manifest.get('proposed_check_date'), 'proposed_check_date')
    if error:
        return error
    ceiling = str(manifest.get('claim_ceiling') or '').lower()
    for phrase in ['not a recheck', 'not evidence', 'not custody evidence', 'not closure evidence', 'not public-summary support']:
        if phrase not in ceiling:
            return f'claim_ceiling must preserve {phrase}'

    source = manifest.get('source_post_readout_action')
    if not isinstance(source, dict):
        return 'source_post_readout_action must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_post_readout_action.reference must be a non-empty archive-relative scratch path'
    action_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(action_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_post_readout_action.reference must resolve under archive scratch/'
    lane_error = field_scratch_lane_error(action_path, archive_root=archive_root, field_name='source_post_readout_action.reference')
    if lane_error:
        return lane_error
    if action_path.name != 'post-readout-action.json' or not action_path.exists() or not action_path.is_file():
        return 'source_post_readout_action.reference must point to an existing post-readout-action.json file'
    try:
        action_data = json.loads(action_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_post_readout_action.reference is not readable JSON'
    action_error = owner_post_readout_action_integrity_error(action_data, archive_root=archive_root)
    if action_error:
        return 'source_post_readout_action failed post-readout action integrity: ' + action_error
    if source.get('action_sha256') != _sha256_file(action_path):
        return 'source_post_readout_action.action_sha256 does not match referenced post-readout-action.json'
    for key in [
        'dispatch_state',
        'dispatch_lane',
        'owner_action_class',
        'next_evidence_ask_class',
        'source_truth_class',
        'due_or_recheck_date',
        'acceptance_state',
        'evidence_state',
        'closure_effect',
        'post_readout_action_effect',
        'dispatch_counts',
        'next_evidence_ask',
    ]:
        if source.get(key) != action_data.get(key):
            return f'source_post_readout_action.{key} does not match referenced post-readout-action.json'
    if source.get('revalidated_for_post_readout_recheck_brief') is not True:
        return 'source_post_readout_action.revalidated_for_post_readout_recheck_brief must be true'

    check_day = _date_value(manifest.get('proposed_check_date'))
    due_day = _date_value(action_data.get('due_or_recheck_date'))
    if check_day is None or due_day is None:
        return 'proposed_check_date and source due_or_recheck_date must parse as dates'
    if check_day < due_day:
        return 'proposed_check_date must be on or after source post-readout action due_or_recheck_date'

    source_counts = action_data.get('dispatch_counts') if isinstance(action_data.get('dispatch_counts'), dict) else {}
    source_roles = max(2, int(source_counts.get('reviewer_role_count') or 2))
    allowed = manifest.get('allowed_recheck_outcomes')
    if allowed != sorted(POST_READOUT_RECHECK_BRIEF_OUTCOME_ARGS):
        return 'allowed_recheck_outcomes must list the four bounded recheck outcomes only'
    if manifest.get('default_recheck_outcome') != 'no_new_owner_context':
        return 'default_recheck_outcome must be no_new_owner_context'

    commands = manifest.get('post_readout_recheck_command_templates')
    if not isinstance(commands, dict) or not commands:
        return 'post_readout_recheck_command_templates must be a non-empty object'
    for required in POST_READOUT_RECHECK_BRIEF_REQUIRED_COMMAND_KEYS:
        if required not in commands:
            return f'post_readout_recheck_command_templates must include {required}'
    if commands.get('primary') != commands.get('no_new_owner_context'):
        return 'primary recheck command must default to no_new_owner_context'
    for key, command in commands.items():
        if not isinstance(command, str) or not command.startswith('make owner-post-readout-recheck '):
            return f'post_readout_recheck_command_templates.{key} must be an owner-post-readout-recheck command'
        if f'ACTION={ref}' not in command and f"ACTION='{ref}'" not in command:
            return f'post_readout_recheck_command_templates.{key} must reference the source post-readout action'
        if f'CHECK_DATE={manifest.get("proposed_check_date")}' not in command:
            return f'post_readout_recheck_command_templates.{key} must preserve proposed check date'
        if f'REVIEWER_ROLE_COUNT={source_roles}' not in command:
            return f'post_readout_recheck_command_templates.{key} must preserve source reviewer role count minimum'
        for token in ['NO_EXPANSION_CONFIRMED=1', 'NO_PUBLIC_CLAIM_UPGRADE=1', 'NO_SERVICE_RECORD_EDIT=1', 'NO_LIFECYCLE_CHANGE=1', 'NO_CLOSURE_FROM_RECHECK=1', 'CONFIRM=human-recorded-post-readout-recheck-no-closure', 'OUT=scratch/field/ft0181/owner-post-readout-rechecks/']:
            if token not in command:
                return f'post_readout_recheck_command_templates.{key} missing {token}'
        if 'make owner-post-readout-context-receipt ' in command or 'make owner-field-next ' in command:
            return f'post_readout_recheck_command_templates.{key} must not jump to context receipt or field-next intake'
        if key in POST_READOUT_RECHECK_BRIEF_OUTCOME_ARGS:
            expected_outcome_arg = POST_READOUT_RECHECK_BRIEF_OUTCOME_ARGS[key]
            if f'RECHECK_OUTCOME={expected_outcome_arg}' not in command:
                return f'post_readout_recheck_command_templates.{key} must preserve its recheck outcome'
            has_context_flag = 'NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE=1' in command
            if key == 'new_owner_context_available':
                if not has_context_flag:
                    return 'new_owner_context_available command must require NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE=1'
            elif has_context_flag:
                return f'post_readout_recheck_command_templates.{key} must not set new-owner-context flag'
        lowered = command.lower()
        for forbidden in ['student id', 'learner id', 'student name', 'email address', '@', 'screenshot', 'api key', 'credential', 'claim text', 'owner answer', 'csv=']:
            if forbidden in lowered:
                return f'post_readout_recheck_command_templates.{key} includes forbidden raw/contact/context term: {forbidden}'
    boundary = str(manifest.get('recheck_boundary') or '').lower()
    if 'does not record' not in boundary or 'post-readout recheck' not in boundary or 'human must choose' not in boundary:
        return 'recheck_boundary must state no recheck recording and human-choice precondition'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_live_window_notes', 'copies_contact_details', 'copies_public_claim_text', 'copies_new_owner_context', 'copies_learner_identifiers_or_protected_facts']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('source_post_readout_action_revalidated') is not True:
        return 'content_minimization.source_post_readout_action_revalidated must be true'
    if content.get('contains_hashes_counts_dates_and_command_skeletons_only') is not True:
        return 'content_minimization.contains_hashes_counts_dates_and_command_skeletons_only must be true'
    forbidden_effects = manifest.get('forbidden_effects')
    if not isinstance(forbidden_effects, list):
        return 'forbidden_effects must be a list'
    for required in ['post-readout-recheck-recording', 'new-owner-context-intake', 'service-record-mutation', 'public-claim-upgrade', 'custody-or-acceptance', 'lifecycle-or-closure']:
        if required not in forbidden_effects:
            return f'forbidden_effects must include {required}'
    if manifest.get('required_next_surface') != 'docs/30-operations/ft0181-post-readout-recheck-gate.md':
        return 'required_next_surface must route to post-readout recheck gate'
    return None


POST_READOUT_RECHECK_OUTCOMES = {
    'no_new_owner_context',
    'new_owner_context_available',
    'owner_action_complete_no_closure',
    'route_blocked_no_owner',
}
POST_READOUT_RECHECK_STATES = {
    'RECHECK_RECORDED_NO_NEW_OWNER_CONTEXT',
    'RECHECK_RECORDED_NEW_OWNER_CONTEXT_NOT_INTAKEN',
    'OWNER_ACTION_RECHECKED_COMPLETE_NOT_CLOSURE',
    'RECHECK_RECORDED_ROUTE_BLOCKED_NO_OWNER',
}
POST_READOUT_RECHECK_STATE_BY_OUTCOME = {
    'no_new_owner_context': 'RECHECK_RECORDED_NO_NEW_OWNER_CONTEXT',
    'new_owner_context_available': 'RECHECK_RECORDED_NEW_OWNER_CONTEXT_NOT_INTAKEN',
    'owner_action_complete_no_closure': 'OWNER_ACTION_RECHECKED_COMPLETE_NOT_CLOSURE',
    'route_blocked_no_owner': 'RECHECK_RECORDED_ROUTE_BLOCKED_NO_OWNER',
}
EXPECTED_POST_READOUT_RECHECK_FIELDS = {
    'recheck_type': 'FT-0181-post-readout-action-recheck',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_permitted': False,
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'does_not_upgrade_public_claims',
    'service_record_effect': 'does_not_edit_service_records_from_recheck',
    'lifecycle_effect': 'does_not_change_lifecycle_from_recheck',
    'ft0181_status': 'live',
    'post_readout_recheck_effect': 'may_route_new_owner_context_to_router_or_stop_only',
}


def owner_post_readout_recheck_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a post-readout recheck cannot be the next field stop.

    The recheck is the due-date firebreak after a post-readout action dispatch.
    It can only say whether new owner context exists outside the archive or that
    no new context/action closure exists. It must not copy returned context,
    mutate service records, move lifecycle state, upgrade public language, create
    custody/acceptance, or close FT-0181.
    """
    if not isinstance(manifest, dict):
        return 'post-readout recheck is not an object'
    for key, expected in EXPECTED_POST_READOUT_RECHECK_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('recheck_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'recheck_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    error = _parse_iso_date(manifest.get('check_date'), 'check_date')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-recorded-post-readout-recheck-no-closure':
        return 'operator_confirmation must be human-recorded-post-readout-recheck-no-closure'
    state = manifest.get('recheck_state')
    if state not in POST_READOUT_RECHECK_STATES:
        return f'recheck_state={state!r} is not allowed'
    outcome = manifest.get('recheck_outcome')
    if outcome not in POST_READOUT_RECHECK_OUTCOMES:
        return f'recheck_outcome={outcome!r} is not allowed'
    expected_state = POST_READOUT_RECHECK_STATE_BY_OUTCOME.get(str(outcome))
    if state != expected_state:
        return f'recheck_state={state!r} must match recheck_outcome {outcome!r}: {expected_state!r}'
    source_truth_class = manifest.get('source_truth_class')
    if source_truth_class not in LIVE_WINDOW_READOUT_SOURCE_TRUTH_CLASSES:
        return f'source_truth_class={source_truth_class!r} must be SRC2/SRC3/SRC4 inherited from post-readout action'

    source = manifest.get('source_post_readout_action')
    if not isinstance(source, dict):
        return 'source_post_readout_action must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_post_readout_action.reference must be a non-empty scratch path'
    action_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(action_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_post_readout_action.reference must stay under scratch'
    lane_error = field_scratch_lane_error(action_path, archive_root=archive_root, field_name='source_post_readout_action.reference')
    if lane_error:
        return lane_error
    if action_path.name != 'post-readout-action.json' or not action_path.exists() or not action_path.is_file():
        return 'source_post_readout_action.reference must point to an existing post-readout-action.json file'
    try:
        action_data = json.loads(action_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_post_readout_action.reference is not readable JSON'
    action_error = owner_post_readout_action_integrity_error(action_data, archive_root=archive_root)
    if action_error:
        return 'source_post_readout_action failed post-readout action integrity: ' + action_error
    expected_hash = _sha256_file(action_path)
    if source.get('action_sha256') != expected_hash:
        return 'source_post_readout_action.action_sha256 does not match referenced action'
    for key in [
        'dispatch_state',
        'dispatch_lane',
        'owner_action_class',
        'next_evidence_ask_class',
        'source_truth_class',
        'due_or_recheck_date',
        'acceptance_state',
        'evidence_state',
        'closure_effect',
        'post_readout_action_effect',
    ]:
        if source.get(key) != action_data.get(key):
            return f'source_post_readout_action.{key} does not match referenced action'
    if source.get('revalidated_for_post_readout_recheck') is not True:
        return 'source_post_readout_action.revalidated_for_post_readout_recheck must be true'
    if source_truth_class != action_data.get('source_truth_class'):
        return 'source_truth_class must match source post-readout action'
    check_day = _date_value(manifest.get('check_date'))
    due_day = _date_value(action_data.get('due_or_recheck_date'))
    if check_day is None or due_day is None:
        return 'check_date and source due_or_recheck_date must parse as dates'
    if check_day < due_day:
        return 'check_date must be on or after source post-readout action due_or_recheck_date'

    counts = manifest.get('recheck_counts')
    if not isinstance(counts, dict):
        return 'recheck_counts must be an object'
    reviewer_count, value_error = _non_negative_int(counts.get('reviewer_role_count'), 'recheck_counts.reviewer_role_count')
    if value_error:
        return value_error
    assert reviewer_count is not None
    if reviewer_count < 2 or reviewer_count > 5:
        return 'recheck_counts.reviewer_role_count must be between 2 and 5'
    source_roles = action_data.get('dispatch_counts', {}).get('reviewer_role_count')
    if isinstance(source_roles, int) and reviewer_count < source_roles:
        return 'recheck_counts.reviewer_role_count cannot be below source action reviewer_role_count'
    new_context_count, value_error = _non_negative_int(counts.get('new_owner_context_count'), 'recheck_counts.new_owner_context_count')
    if value_error:
        return value_error
    assert new_context_count is not None
    expected_new_context_count = 1 if outcome == 'new_owner_context_available' else 0
    if new_context_count != expected_new_context_count:
        return f'recheck_counts.new_owner_context_count must be {expected_new_context_count} for {outcome}'
    has_new_context = manifest.get('new_owner_context_held_outside_archive')
    if outcome == 'new_owner_context_available':
        if has_new_context is not True:
            return 'new_owner_context_available requires new_owner_context_held_outside_archive=true'
    elif has_new_context is not False:
        return 'new_owner_context_held_outside_archive must be false unless recheck_outcome is new_owner_context_available'

    next_action = str(manifest.get('required_next_action') or '').lower()
    if outcome == 'new_owner_context_available':
        if 'owner-field-next' not in next_action or 'csv' not in next_action:
            return 'new_owner_context_available must route the actual returned context through owner-field-next CSV=...'
        if 'do not intake from this recheck' not in next_action:
            return 'new_owner_context_available required_next_action must block intake from the recheck record'
    else:
        if 'no field command' not in next_action:
            return f'{outcome} required_next_action must stop with no field command'
    allowed = manifest.get('allowed_next_steps')
    if not isinstance(allowed, list) or not all(isinstance(v, str) and v for v in allowed):
        return 'allowed_next_steps must be a non-empty string list'
    prohibited = manifest.get('prohibited_next_steps')
    if not isinstance(prohibited, list) or not all(isinstance(v, str) and v for v in prohibited):
        return 'prohibited_next_steps must be a non-empty string list'
    prohibited_text = ' '.join(prohibited).lower()
    for phrase in ['service-record', 'public-claim', 'lifecycle', 'custody', 'acceptance', 'closure', 'copy-owner-context']:
        if phrase not in prohibited_text:
            return f'prohibited_next_steps must explicitly block {phrase}'

    for field in [
        'no_expansion_confirmation',
        'no_public_claim_upgrade',
        'no_service_record_edit_from_recheck',
        'no_lifecycle_change_from_recheck',
        'no_closure_from_recheck',
    ]:
        if manifest.get(field) is not True:
            return f'{field} must be true'
    risk_flags = manifest.get('risk_flags')
    if not isinstance(risk_flags, dict):
        return 'risk_flags must be an object'
    for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']:
        if risk_flags.get(key) is not False:
            return f'risk_flags.{key} must be false for post-readout recheck'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_live_window_notes', 'copies_contact_details', 'copies_public_claim_text', 'copies_new_owner_context']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('contains_status_counts_hashes_and_due_dates_only') is not True:
        return 'content_minimization.contains_status_counts_hashes_and_due_dates_only must be true'
    if content.get('source_post_readout_action_revalidated') is not True:
        return 'content_minimization.source_post_readout_action_revalidated must be true'
    boundary = str(manifest.get('closure_boundary') or '').lower()
    if 'does not close ft-0181' not in boundary or 'does not prove' not in boundary:
        return 'closure_boundary must say it does not close FT-0181 and does not prove service claims'
    ceiling = str(manifest.get('claim_ceiling') or '').lower()
    if 'not evidence' not in ceiling or 'not closure evidence' not in ceiling or 'not public-summary support' not in ceiling:
        return 'claim_ceiling must preserve not-evidence, not-closure, and no public-summary support boundaries'
    return None

def archive_relative(path: Path, *, archive_root: Path) -> tuple[bool, tuple[str, ...]]:
    """Return whether a path is inside the archive and its relative parts."""
    try:
        rel = path.resolve().relative_to(archive_root.resolve())
    except ValueError:
        return False, ()
    return True, rel.parts


def output_allowed(output_dir: Path, *, archive_root: Path) -> tuple[bool, str]:
    """Return whether a local FT-0181 output path is allowed and why.

    Only scratch paths and paths outside the release archive are allowed.
    Archive-owned docs/examples/fixtures/schemas/templates/tools, controlled root
    files, and any other nonscratch top-level archive path are blocked so
    generated local execution notes cannot become shipped evidence, release
    metadata, or packaging leakage by accident.
    """
    resolved = output_dir.resolve()
    inside, parts = archive_relative(resolved, archive_root=archive_root)
    if not inside:
        return True, 'outside-archive'
    if not parts:
        return False, 'archive-root'
    if parts[0] in CONTROLLED_TOP_LEVEL:
        return False, f'archive-controlled-top-level:{parts[0]}'
    if len(parts) == 1 and parts[0] in CONTROLLED_ROOT_FILES:
        return False, f'archive-controlled-root-file:{parts[0]}'
    if parts[0] == 'scratch':
        return True, 'scratch'
    return False, f'archive-nonscratch-output:{parts[0]}'



EXPECTED_POST_READOUT_CONTEXT_RECEIPT_FIELDS = {
    'receipt_type': 'FT-0181-post-readout-owner-context-receipt',
    'followthrough_id': 'FT-0181',
    'service_record_id': 'AIEDU-SR-003',
    'receipt_state': 'POST_READOUT_OWNER_CONTEXT_RECEIPTED_NOT_INTAKEN',
    'source_truth_class': 'UNVERIFIED-OWNER-REPLY',
    'acceptance_state': 'NOT_ACCEPTED',
    'evidence_state': 'not_evidence',
    'closure_effect': 'does_not_close_ft0181',
    'public_claim_effect': 'does_not_upgrade_public_claims',
    'service_record_effect': 'does_not_edit_service_records_from_context_receipt',
    'lifecycle_effect': 'does_not_change_lifecycle_from_context_receipt',
    'ft0181_status': 'live',
    'post_readout_context_receipt_effect': 'may_source_owner_reply_intake_only',
}


def owner_post_readout_context_receipt_integrity_error(manifest: dict, *, archive_root: Path) -> str | None:
    """Return why a post-readout owner-context receipt cannot source intake.

    This receipt closes the post-readout new-context lineage gap: a recheck may
    say that new owner context exists outside the archive, but intake must be
    tied to the actual returned CSV/source packet hash rather than to the recheck
    prose or to an older contact clock. The receipt remains local non-evidence.
    """
    if not isinstance(manifest, dict):
        return 'post-readout owner-context receipt is not an object'
    for key, expected in EXPECTED_POST_READOUT_CONTEXT_RECEIPT_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            return f'{key}={actual!r} (expected {expected!r})'
    version = manifest.get('receipt_version')
    if not isinstance(version, str) or not version.startswith('rev'):
        return f'receipt_version={version!r} must name the release revision'
    error = _parse_utc_timestamp(manifest.get('created_at_utc'), 'created_at_utc')
    if error:
        return error
    if manifest.get('operator_confirmation') != 'human-linked-post-readout-owner-context-receipt':
        return 'operator_confirmation must be human-linked-post-readout-owner-context-receipt'

    source = manifest.get('source_post_readout_recheck')
    if not isinstance(source, dict):
        return 'source_post_readout_recheck must be an object'
    ref = source.get('reference')
    if not isinstance(ref, str) or not ref:
        return 'source_post_readout_recheck.reference must be a non-empty scratch path'
    recheck_path = (archive_root / ref).resolve()
    inside, parts = archive_relative(recheck_path, archive_root=archive_root)
    if not inside or not parts or parts[0] != 'scratch':
        return 'source_post_readout_recheck.reference must stay under scratch'
    lane_error = field_scratch_lane_error(recheck_path, archive_root=archive_root, field_name='source_post_readout_recheck.reference')
    if lane_error:
        return lane_error
    if recheck_path.name != 'post-readout-recheck.json' or not recheck_path.exists() or not recheck_path.is_file():
        return 'source_post_readout_recheck.reference must point to an existing post-readout-recheck.json file'
    try:
        recheck_data = json.loads(recheck_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'source_post_readout_recheck.reference is not readable JSON'
    recheck_error = owner_post_readout_recheck_integrity_error(recheck_data, archive_root=archive_root)
    if recheck_error:
        return 'source_post_readout_recheck failed post-readout recheck integrity: ' + recheck_error
    if recheck_data.get('recheck_outcome') != 'new_owner_context_available':
        return 'source_post_readout_recheck.recheck_outcome must be new_owner_context_available'
    expected_hash = _sha256_file(recheck_path)
    if source.get('recheck_sha256') != expected_hash:
        return 'source_post_readout_recheck.recheck_sha256 does not match referenced recheck'
    for key in ['recheck_state', 'recheck_outcome', 'check_date', 'source_truth_class', 'acceptance_state', 'evidence_state', 'closure_effect', 'post_readout_recheck_effect']:
        if source.get(key) != recheck_data.get(key):
            return f'source_post_readout_recheck.{key} does not match referenced recheck'
    if source.get('revalidated_for_post_readout_context_receipt') is not True:
        return 'source_post_readout_recheck.revalidated_for_post_readout_context_receipt must be true'

    source_csv = manifest.get('source_csv')
    if not isinstance(source_csv, dict):
        return 'source_csv must be an object'
    if not isinstance(source_csv.get('basename'), str) or not source_csv.get('basename'):
        return 'source_csv.basename must be non-empty'
    sha = source_csv.get('sha256')
    if not isinstance(sha, str) or len(sha) != 64 or any(ch not in '0123456789abcdef' for ch in sha.lower()):
        return 'source_csv.sha256 must be a lowercase SHA-256 hex digest'
    try:
        size = int(source_csv.get('size_bytes'))
    except (TypeError, ValueError):
        return 'source_csv.size_bytes must be numeric'
    if size <= 0:
        return 'source_csv.size_bytes must be positive'
    columns = source_csv.get('columns')
    if not isinstance(columns, list) or not all(isinstance(col, str) and col for col in columns):
        return 'source_csv.columns must be a non-empty string list'
    path_scope = source_csv.get('path_scope')
    if path_scope not in {'external_local_path', 'scratch_returned_csv'}:
        return 'source_csv.path_scope must be external_local_path or scratch_returned_csv'
    reference = source_csv.get('source_reference')
    if not isinstance(reference, str) or not reference:
        return 'source_csv.source_reference must be non-empty'
    if path_scope == 'scratch_returned_csv':
        csv_path = (archive_root / reference).resolve()
        inside, parts = archive_relative(csv_path, archive_root=archive_root)
        if not inside or not parts or parts[0] != 'scratch':
            return 'scratch_returned_csv source_reference must resolve under scratch'
        lane_error = field_scratch_lane_error(csv_path, archive_root=archive_root, field_name='scratch_returned_csv source_reference')
        if lane_error:
            return lane_error
        if not csv_path.exists() or not csv_path.is_file():
            return 'scratch_returned_csv source_reference must point to an existing file'
        if _sha256_file(csv_path) != sha:
            return 'source_csv.sha256 does not match scratch_returned_csv source_reference'
    else:
        if reference != '[local path withheld; basename only]':
            return 'external_local_path source_reference must withhold the local path'

    counts = manifest.get('context_counts')
    if not isinstance(counts, dict):
        return 'context_counts must be an object'
    for field in ['returned_context_count', 'row_count', 'reviewer_role_count']:
        value, value_error = _non_negative_int(counts.get(field), f'context_counts.{field}')
        if value_error:
            return value_error
        assert value is not None
        if field == 'returned_context_count' and value != 1:
            return 'context_counts.returned_context_count must be 1'
        if field == 'reviewer_role_count' and (value < 2 or value > 5):
            return 'context_counts.reviewer_role_count must be between 2 and 5'

    for field in [
        'no_expansion_confirmation',
        'no_public_claim_upgrade',
        'no_service_record_edit_from_context_receipt',
        'no_lifecycle_change_from_context_receipt',
        'no_closure_from_context_receipt',
    ]:
        if manifest.get(field) is not True:
            return f'{field} must be true'
    risk_flags = manifest.get('risk_flags')
    if not isinstance(risk_flags, dict):
        return 'risk_flags must be an object'
    for key in ['raw_learner_data_present', 'protected_facts_present', 'security_payloads_present', 'public_claim_upgrade_requested']:
        if risk_flags.get(key) is not False:
            return f'risk_flags.{key} must be false for post-readout context receipt'
    content = manifest.get('content_minimization')
    if not isinstance(content, dict):
        return 'content_minimization must be an object'
    for key in ['copies_owner_answers', 'copies_raw_csv_rows', 'copies_live_window_notes', 'copies_contact_details', 'copies_public_claim_text']:
        if content.get(key) is not False:
            return f'content_minimization.{key} must be false'
    if content.get('contains_context_hashes_and_counts_only') is not True:
        return 'content_minimization.contains_context_hashes_and_counts_only must be true'
    if content.get('source_post_readout_recheck_revalidated') is not True:
        return 'content_minimization.source_post_readout_recheck_revalidated must be true'
    if content.get('actual_context_must_be_intaken_separately') is not True:
        return 'content_minimization.actual_context_must_be_intaken_separately must be true'

    next_action = str(manifest.get('required_next_action') or '').lower()
    if 'owner-reply-intake' not in next_action or 'source_post_readout_context_receipt' not in next_action:
        return 'required_next_action must route owner-reply-intake through SOURCE_POST_READOUT_CONTEXT_RECEIPT'
    prohibited = manifest.get('prohibited_next_steps')
    if not isinstance(prohibited, list) or not all(isinstance(v, str) and v for v in prohibited):
        return 'prohibited_next_steps must be a non-empty string list'
    prohibited_text = ' '.join(prohibited).lower()
    for phrase in ['service-record', 'public-claim', 'lifecycle', 'custody', 'acceptance', 'closure']:
        if phrase not in prohibited_text:
            return f'prohibited_next_steps must explicitly block {phrase}'
    boundary = str(manifest.get('closure_boundary') or '').lower()
    if 'does not close ft-0181' not in boundary or 'does not prove' not in boundary:
        return 'closure_boundary must say it does not close FT-0181 and does not prove service claims'
    ceiling = str(manifest.get('claim_ceiling') or '').lower()
    if 'not evidence' not in ceiling or 'not closure evidence' not in ceiling or 'not public-summary support' not in ceiling:
        return 'claim_ceiling must preserve not-evidence, not-closure, and no public-summary support boundaries'
    return None

def returned_owner_csv_allowed(csv_path: Path, *, archive_root: Path) -> tuple[bool, str]:
    """Return whether a returned-owner CSV input path is a plausible field input.

    Real returned owner packets should live outside the release archive or under
    local scratch. Archive examples, fixtures, templates, docs, schemas, and tools
    are never a returned owner packet, even if another intake gate would later
    block them. This keeps the single next-action router from recommending work on
    shipped smoke fixtures or documentation examples.
    """
    resolved = csv_path.resolve()
    inside, parts = archive_relative(resolved, archive_root=archive_root)
    if not inside:
        return True, 'outside-archive-returned-csv'
    if not parts:
        return False, 'archive-root-input'
    if parts[0] == 'scratch':
        lane_block = non_field_scratch_lane_block(resolved, archive_root=archive_root)
        if lane_block:
            return False, f'archive-nonfield-scratch-returned-csv:{lane_block}'
        return True, 'scratch-field-ft0181-returned-csv'
    if parts[0] in CONTROLLED_TOP_LEVEL:
        return False, f'archive-controlled-returned-csv:{parts[0]}'
    if len(parts) == 1 and parts[0] in CONTROLLED_ROOT_FILES:
        return False, f'archive-controlled-root-returned-csv:{parts[0]}'
    return False, f'archive-nonscratch-returned-csv:{parts[0]}'


def returned_owner_csv_marker_block(csv_path: Path) -> str | None:
    """Return a smoke/fixture marker found in a candidate returned CSV, if any."""
    try:
        sample = csv_path.read_text(encoding='utf-8', errors='replace')[:65536].lower()
    except OSError as exc:
        return f'unreadable returned CSV: {exc}'
    for marker in sorted(RETURNED_CSV_SMOKE_MARKERS):
        if marker in sample:
            return marker
    return None


def returned_owner_csv_source_block(csv_path: Path, *, archive_root: Path, allow_src0_smoke: bool = False) -> str | None:
    """Return a boundary reason when a candidate returned CSV source is not plausible.

    Normal field inputs must live outside archive-controlled surfaces or under
    scratch. The smoke harness may opt into shipped fixtures, but that exception
    is deliberately narrow: templates/docs/examples/tools/schemas and root
    release files remain blocked even when smoke is allowed.
    """
    allowed, boundary = returned_owner_csv_allowed(csv_path, archive_root=archive_root)
    if allowed:
        return None
    inside, parts = archive_relative(csv_path.resolve(), archive_root=archive_root)
    if allow_src0_smoke and inside and parts and parts[0] == 'fixtures':
        return None
    return boundary


def returned_owner_csv_source_truth_class(csv_path: Path, *, archive_root: Path, allow_src0_smoke: bool = False) -> str:
    """Classify a candidate returned owner CSV path/content for field gates."""
    inside, parts = archive_relative(csv_path.resolve(), archive_root=archive_root)
    marker = returned_owner_csv_marker_block(csv_path)
    if (inside and parts and parts[0] == 'fixtures') or (marker and not marker.startswith('unreadable returned CSV')):
        return 'SRC0-SMOKE'
    block = returned_owner_csv_source_block(csv_path, archive_root=archive_root, allow_src0_smoke=allow_src0_smoke)
    if block:
        return 'SRC0-CONTROLLED-ARCHIVE'
    return 'UNVERIFIED-OWNER-REPLY'

