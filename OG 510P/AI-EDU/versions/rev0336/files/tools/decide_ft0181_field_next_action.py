#!/usr/bin/env python3
"""Decide the single next executable FT-0181 field action from local scratch state.

This utility is intentionally a routing aid, not evidence. It scans local scratch
artifacts created by the owner-request packet, owner-route-block, after-human-send helper, owner-send-log, owner-reask-log, owner-contact status, owner-reply
intake, workbench-seed, workbench-review brief, workbench-review, first-packet decision brief, first-packet decision, activation/live-window entry brief,
activation/live-window entry brief, activation-receipt, post-decision change-ticket, live-window card, live-window terminal-state brief, live-window readout brief, live-window readout, post-readout action brief, post-readout action, post-readout recheck brief, post-readout recheck, and post-readout context receipt tools, then emits exactly one recommended next action.
It prevents the common failure mode where owner silence or scattered scratch files
lead to new doctrine, widened asks, or accidental closure language.
"""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

from record_ft0181_owner_contact_status import OPERATOR_CONFIRMATIONS
from record_ft0181_owner_send_log import OPERATOR_CONFIRMATION as SEND_LOG_CONFIRMATION
from record_ft0181_owner_reask_log import OPERATOR_CONFIRMATION as REASK_LOG_CONFIRMATION
from record_ft0181_live_window_card import OPERATOR_CONFIRMATION as LIVE_WINDOW_CONFIRMATION
from record_ft0181_activation_receipt import OPERATOR_CONFIRMATION as ACTIVATION_RECEIPT_CONFIRMATION
from record_ft0181_live_window_readout import OPERATOR_CONFIRMATION as LIVE_WINDOW_READOUT_CONFIRMATION
from record_ft0181_post_readout_action import OPERATOR_CONFIRMATION as POST_READOUT_ACTION_CONFIRMATION
from record_ft0181_post_readout_recheck import OPERATOR_CONFIRMATION as POST_READOUT_RECHECK_CONFIRMATION
from record_ft0181_post_readout_context_receipt import OPERATOR_CONFIRMATION as POST_READOUT_CONTEXT_RECEIPT_CONFIRMATION

from ft0181_field_guards import (
    FIRST_CONTACT_MAX_DAYS,
    REASK_MAX_DAYS,
    output_allowed,
    owner_request_packet_integrity_error,
    owner_send_log_integrity_error,
    owner_reask_log_integrity_error,
    owner_route_block_integrity_error,
    owner_contact_status_integrity_error,
    owner_workbench_seed_integrity_error,
    owner_workbench_review_brief_integrity_error,
    owner_workbench_review_integrity_error,
    owner_first_packet_decision_brief_integrity_error,
    owner_first_packet_decision_integrity_error,
    owner_post_decision_change_ticket_brief_integrity_error,
    owner_activation_live_window_brief_integrity_error,
    owner_live_window_terminal_brief_integrity_error,
    owner_live_window_readout_brief_integrity_error,
    owner_post_readout_action_brief_integrity_error,
    owner_post_readout_recheck_brief_integrity_error,
    activation_receipt_integrity_error,
    owner_post_decision_change_ticket_integrity_error,
    owner_live_window_card_integrity_error,
    owner_live_window_readout_integrity_error,
    owner_post_readout_action_integrity_error,
    owner_post_readout_recheck_integrity_error,
    owner_post_readout_context_receipt_integrity_error,
    returned_owner_csv_allowed,
    returned_owner_csv_marker_block,
    operator_today_iso,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT = ROOT / 'scratch' / 'field' / 'ft0181' / 'ft0181-field-next-action'
DEFAULT_SCRATCH = ROOT / 'scratch' / 'field' / 'ft0181'
CLAIM_CEILING = (
    'Field routing aid only; not evidence, not SRC2+, not custody evidence, not '
    'closure evidence, and not public-summary support.'
)
FIRST_CONTACT_DUE_DAYS = FIRST_CONTACT_MAX_DAYS
REASK_DUE_DAYS = REASK_MAX_DAYS
KNOWN_CONTACT_STATUSES = {'SENT_AWAITING_REPLY', 'REASK_AWAITING_REPLY', 'NO_OWNER_PACKET'}
KNOWN_TRIAGE_OUTCOMES = {
    'PROCEED-STAGED',
    'RE-ASK-ONCE',
    'NO-OWNER-PACKET',
    'BLOCK-SECURITY',
    'BLOCK-PROTECTED',
    'BLOCK-OVERBROAD',
    'BLOCK-AUTHORITY',
    'BLOCK-EVIDENCE',
}


@dataclass(frozen=True)
class LocalArtifact:
    kind: str
    path: Path
    data: dict[str, Any]
    mtime: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Decide the next bounded FT-0181 field command from local scratch state.')
    parser.add_argument('--scratch-root', type=Path, default=DEFAULT_SCRATCH, help='Scratch root to scan for local FT-0181 artifacts.')
    parser.add_argument('--returned-csv', type=Path, help='Optional path to a newly returned owner CSV; routes directly to owner-reply-intake if present.')
    parser.add_argument('--as-of-date', default=operator_today_iso(), help='Decision date, YYYY-MM-DD. Defaults to the operator-local date (CUBE_AS_OF_DATE override, then CUBE_OPERATOR_TIMEZONE).')
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT, help='Local/scratch output directory for the decision docket.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing decision docket directory.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable decision JSON.')
    parser.add_argument('--execute-safe-local', action='store_true', help='Execute safe local bridge-prep routes only: first-contact packet prep, workbench review-brief prep, first-packet decision-brief prep, post-decision change-ticket brief prep, activation/live-window entry brief prep, live-window terminal-state brief prep, live-window readout brief prep, or post-readout action brief prep, or post-readout recheck brief prep. This never records human send, contact, review, decision, change ticket, intake, evidence, custody, public support, live-window terminal state, readout, post-readout recheck, or closure.')
    parser.add_argument('--packet-output-dir', type=Path, help='Packet directory to use with --execute-safe-local. Defaults under the selected scratch root.')
    return parser.parse_args()


def parse_iso(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'{field} must be YYYY-MM-DD') from exc


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


NON_FIELD_SCRATCH_EXACT_PARTS = {'checks', 'releases'}
NON_FIELD_SCRATCH_PREFIXES = ('check-', 'smoke-', 'test-', 'fixture-')
NON_ROUTABLE_FIELD_FIXTURE_EXACT_PARTS = {'validation'}
NON_ROUTABLE_FIELD_FIXTURE_PREFIXES = ('validation-',)
NON_ROUTABLE_FIELD_FIXTURE_SUFFIXES = ('-validation',)
SCRATCH_FIREBREAK_RULE = (
    'field-state scan ignores scratch/checks, scratch/releases, check/smoke/test/fixture '
    'scratch subtrees, scratch/field/ft0181 validation fixture lanes, and artifacts whose '
    'provenance reference points back into those non-field or non-routable subtrees'
)


def scratch_relative_parts(path: Path, root: Path) -> tuple[str, ...]:
    try:
        return path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        return path.parts


def is_non_field_scratch_path(path: Path, root: Path) -> bool:
    parts = scratch_relative_parts(path, root)
    return any(part in NON_FIELD_SCRATCH_EXACT_PARTS or part.startswith(NON_FIELD_SCRATCH_PREFIXES) for part in parts)


def is_non_routable_field_fixture_part(part: str) -> bool:
    return (
        part in NON_ROUTABLE_FIELD_FIXTURE_EXACT_PARTS
        or part.startswith(NON_ROUTABLE_FIELD_FIXTURE_PREFIXES)
        or part.endswith(NON_ROUTABLE_FIELD_FIXTURE_SUFFIXES)
    )


def is_non_routable_field_fixture_path(path: Path, root: Path) -> bool:
    return any(is_non_routable_field_fixture_part(part) for part in scratch_relative_parts(path, root))


def is_router_ignored_scratch_path(path: Path, root: Path) -> bool:
    return is_non_field_scratch_path(path, root) or is_non_routable_field_fixture_path(path, root)


def scratch_root_reference_prefix(root: Path) -> str:
    try:
        return root.resolve().relative_to(ROOT.resolve()).as_posix().rstrip('/')
    except ValueError:
        return root.as_posix().rstrip('/')


def string_references_non_field_scratch(value: str, root: Path) -> bool:
    normalized = value.replace('\\', '/').strip()
    if not normalized:
        return False
    root_ref = scratch_root_reference_prefix(root)
    prefix_hits = tuple(f'{root_ref}/{prefix}' for prefix in NON_FIELD_SCRATCH_PREFIXES)
    exact_hits = tuple(f'{root_ref}/{part}' for part in NON_FIELD_SCRATCH_EXACT_PARTS)
    if (
        normalized.startswith(prefix_hits)
        or normalized in exact_hits
        or any(normalized.startswith(f'{hit}/') for hit in exact_hits)
        or any(f'/{prefix}' in normalized for prefix in prefix_hits)
    ):
        return True
    if normalized.startswith(f'{root_ref}/'):
        remainder_parts = normalized[len(root_ref) + 1:].split('/')
        if any(is_non_routable_field_fixture_part(part) for part in remainder_parts):
            return True
    return False


def artifact_references_non_field_scratch(value: Any, root: Path) -> bool:
    if isinstance(value, str):
        return string_references_non_field_scratch(value, root)
    if isinstance(value, dict):
        return any(artifact_references_non_field_scratch(child, root) for child in value.values())
    if isinstance(value, list):
        return any(artifact_references_non_field_scratch(child, root) for child in value)
    return False


def collect(root: Path, pattern: str, kind: str, expected_key: str) -> list[LocalArtifact]:
    artifacts: list[LocalArtifact] = []
    if not root.exists():
        return artifacts
    for path in root.glob(pattern):
        if is_router_ignored_scratch_path(path, root):
            continue
        data = load_json(path)
        if not data or data.get(expected_key) is None:
            continue
        if artifact_references_non_field_scratch(data, root):
            continue
        artifacts.append(LocalArtifact(kind=kind, path=path, data=data, mtime=path.stat().st_mtime))
    return artifacts


def parse_manifest_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    try:
        if text.endswith('Z'):
            text = text[:-1] + '+00:00'
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_manifest_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def status_rank(status: Any) -> int:
    return {
        'SENT_AWAITING_REPLY': 1,
        'REASK_AWAITING_REPLY': 2,
        'NO_OWNER_PACKET': 3,
    }.get(str(status), 0)


def artifact_sort_key(item: LocalArtifact) -> tuple[float, int, int, float, float]:
    """Rank local field artifacts by their own manifest clocks, not file mtime.

    File modification time is only a final tie-breaker. Copying an old scratch
    artifact into a fresh directory must not make an old SENT clock outrank a
    newer REASK or NO_OWNER_PACKET status.
    """
    if item.kind == 'contact_status':
        status_date = parse_manifest_date(item.data.get('status_date')) or date.min
        due_date = parse_manifest_date(item.data.get('response_due_date')) or date.min
        manifest_dt = parse_manifest_datetime(item.data.get('created_at_utc'))
        if manifest_dt is None:
            manifest_dt = datetime.combine(status_date, time.min, tzinfo=timezone.utc)
        attempt = int(item.data.get('attempt_count') or 0)
        rank = status_rank(item.data.get('contact_status'))
        return (manifest_dt.timestamp(), attempt, rank, float(due_date.toordinal()), item.mtime)
    if item.kind == 'send_log':
        created = parse_manifest_datetime(item.data.get('created_at_utc'))
        sent = parse_manifest_date(item.data.get('sent_date')) or date.min
        due = parse_manifest_date(item.data.get('response_due_date')) or date.min
        if created is not None:
            return (created.timestamp(), 0, 0, float(due.toordinal()), item.mtime)
        return (float(sent.toordinal()), 0, 0, float(due.toordinal()), item.mtime)
    if item.kind == 'reask_log':
        created = parse_manifest_datetime(item.data.get('created_at_utc'))
        sent = parse_manifest_date(item.data.get('sent_date')) or date.min
        due = parse_manifest_date(item.data.get('response_due_date')) or date.min
        if created is not None:
            return (created.timestamp(), 2, 2, float(due.toordinal()), item.mtime)
        return (float(sent.toordinal()), 2, 2, float(due.toordinal()), item.mtime)
    if item.kind in {'intake_bundle', 'workbench_seed', 'workbench_review_brief', 'workbench_review', 'first_packet_decision_brief', 'first_packet_decision', 'post_decision_change_ticket_brief', 'activation_live_window_brief', 'activation_receipt', 'post_decision_change_ticket', 'live_window_card', 'live_window_terminal_brief', 'live_window_readout_brief', 'live_window_readout', 'post_readout_action_brief', 'post_readout_action', 'post_readout_recheck_brief', 'post_readout_recheck', 'post_readout_context_receipt'}:
        created = parse_manifest_datetime(item.data.get('created_at_utc'))
        if created is not None:
            return (created.timestamp(), 0, 0, 0.0, item.mtime)
    if item.kind == 'packet':
        created = parse_manifest_datetime(item.data.get('created_at_utc'))
        if created is not None:
            requested = parse_manifest_date(item.data.get('requested_return_date')) or date.min
            return (created.timestamp(), 0, 0, float(requested.toordinal()), item.mtime)
        requested = parse_manifest_date(item.data.get('requested_return_date'))
        if requested is not None:
            requested_dt = datetime.combine(requested, time.min, tzinfo=timezone.utc)
            return (requested_dt.timestamp(), 0, 0, 0.0, item.mtime)
    return (0.0, 0, 0, 0.0, item.mtime)


def latest(items: list[LocalArtifact]) -> LocalArtifact | None:
    return max(items, key=artifact_sort_key, default=None)


def latest_no_owner_packet_status(items: list[LocalArtifact]) -> LocalArtifact | None:
    return latest([item for item in items if item.data.get('contact_status') == 'NO_OWNER_PACKET'])


def event_order(item: LocalArtifact | None) -> tuple[float, int, int, float, float]:
    if item is None:
        return (float('-inf'), 0, 0, 0.0, 0.0)
    return artifact_sort_key(item)


def artifact_counts(*groups: list[LocalArtifact]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for group in groups:
        for item in group:
            counts[item.kind] = counts.get(item.kind, 0) + 1
    return counts


def selected_artifact_context(item: LocalArtifact | None) -> dict[str, Any] | None:
    if item is None:
        return None
    return {
        'kind': item.kind,
        'path': relative(item.path),
        'selection_key': list(artifact_sort_key(item)),
    }


def latest_artifact_contexts(candidates: dict[str, LocalArtifact | None]) -> dict[str, dict[str, Any]]:
    return {kind: context for kind, item in candidates.items() if (context := selected_artifact_context(item)) is not None}


def with_context(
    decision: dict[str, Any],
    *,
    counts: dict[str, int],
    selected: LocalArtifact | None = None,
    candidates: dict[str, LocalArtifact | None] | None = None,
) -> dict[str, Any]:
    enriched = dict(decision)
    enriched['scratch_selection_rule'] = 'manifest-clock-first-file-mtime-tiebreaker-only'
    enriched['scratch_firebreak_rule'] = SCRATCH_FIREBREAK_RULE
    enriched['observed_artifact_counts'] = counts
    candidate_contexts = latest_artifact_contexts(candidates or {})
    if candidates is not None:
        enriched['latest_artifact_candidates'] = candidate_contexts
    selected_context = selected_artifact_context(selected) if selected is not None else None
    if selected_context is not None:
        enriched['selected_artifact'] = selected_context
    enriched['field_session_summary'] = {
        'artifact_counts': counts,
        'candidate_kinds': sorted(candidate_contexts.keys()),
        'selected_kind': selected_context.get('kind') if selected_context else None,
        'selected_path': selected_context.get('path') if selected_context else None,
        'selection_rule': enriched['scratch_selection_rule'],
        'scratch_firebreak_rule': SCRATCH_FIREBREAK_RULE,
        'one_action_outcome': enriched.get('outcome'),
        'no_evidence_or_closure_effect': True,
    }
    return enriched


def shell_quote(value: str | Path) -> str:
    return shlex.quote(value.as_posix() if isinstance(value, Path) else str(value))


def command_for_returned_csv(csv_path: Path, source_contact_status: Path) -> str:
    return (
        f'make owner-returned-reply-work CSV={shell_quote(csv_path)} '
        f'SOURCE_CONTACT_STATUS={shell_quote(relative(source_contact_status))}'
    )


def packet_command() -> str:
    return 'make owner-request-packet OUT=scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact'


def owner_send_log_output(as_of: date) -> str:
    return f'scratch/field/ft0181/owner-send-logs/aiedu-sr-003-sent-{as_of.isoformat()}'


def owner_after_human_send_output(as_of: date) -> str:
    return f'scratch/field/ft0181/owner-after-human-send/aiedu-sr-003-sent-{as_of.isoformat()}'


def owner_route_block_output(as_of: date) -> str:
    return f'scratch/field/ft0181/owner-route-blocks/aiedu-sr-003-route-block-{as_of.isoformat()}'


def route_block_command(packet_manifest: Path, as_of: date) -> str:
    return (
        f'make owner-route-block PACKET={shell_quote(relative(packet_manifest))} '
        'CONFIRM=human-confirmed-owner-route-block-no-send '
        f'OUT={owner_route_block_output(as_of)}'
    )


def send_log_command(packet_manifest: Path, return_date: str, as_of: date) -> str:
    due = parse_iso(safe_due_date(return_date, as_of, FIRST_CONTACT_DUE_DAYS), 'response_due_date')
    return (
        f'make owner-after-human-send PACKET={shell_quote(relative(packet_manifest))} '
        f'SENT_DATE={as_of.isoformat()} RESPONSE_DUE_DATE={due.isoformat()} '
        f'CONFIRM={SEND_LOG_CONFIRMATION} OUT={owner_after_human_send_output(as_of)}'
    )


def safe_due_date(candidate: str, sent: date, default_days: int) -> str:
    try:
        parsed = date.fromisoformat(candidate)
    except (TypeError, ValueError):
        parsed = sent + timedelta(days=default_days)
    bounded = sent + timedelta(days=default_days)
    if parsed < sent or parsed > bounded:
        parsed = bounded
    return parsed.isoformat()


def contact_status_output(status_slug: str, as_of: date) -> str:
    return f'scratch/field/ft0181/owner-contact-status/aiedu-sr-003-{status_slug}-{as_of.isoformat()}'


def contact_status_command(*, status: str, sent: date, due: date, status_date: date, attempt_count: int = 1, status_slug: str, source_artifact: Path | str) -> str:
    source_ref = relative(source_artifact) if isinstance(source_artifact, Path) else str(source_artifact)
    confirmation = OPERATOR_CONFIRMATIONS[status]
    return (
        f'make owner-contact-status STATUS={status} '
        f'SENT_DATE={sent.isoformat()} RESPONSE_DUE_DATE={due.isoformat()} STATUS_DATE={status_date.isoformat()} '
        f'ATTEMPT_COUNT={attempt_count} CONFIRM={confirmation} SOURCE_ARTIFACT={shell_quote(source_ref)} '
        f'OUT={contact_status_output(status_slug, status_date)}'
    )


def contact_sent_command(return_date: str, as_of: date, source_artifact: Path | str) -> str:
    due = parse_iso(safe_due_date(return_date, as_of, FIRST_CONTACT_DUE_DAYS), 'response_due_date')
    return contact_status_command(
        status='sent-awaiting-reply',
        sent=as_of,
        due=due,
        status_date=as_of,
        attempt_count=1,
        status_slug='sent',
        source_artifact=source_artifact,
    )


def contact_sent_from_send_log_command(send_log: LocalArtifact, as_of: date) -> str:
    sent = parse_iso(str(send_log.data.get('sent_date') or ''), 'sent_date')
    due = parse_iso(str(send_log.data.get('response_due_date') or ''), 'response_due_date')
    return contact_status_command(
        status='sent-awaiting-reply',
        sent=sent,
        due=due,
        status_date=as_of,
        attempt_count=1,
        status_slug='sent',
        source_artifact=send_log.path,
    )


def owner_reask_log_output(as_of: date) -> str:
    return f'scratch/field/ft0181/owner-reask-logs/aiedu-sr-003-reask-{as_of.isoformat()}'


def reask_log_command(as_of: date, source_artifact: Path | str) -> str:
    source_ref = relative(source_artifact) if isinstance(source_artifact, Path) else str(source_artifact)
    return (
        f'make owner-reask-log SOURCE_ARTIFACT={shell_quote(source_ref)} '
        f'SENT_DATE={as_of.isoformat()} RESPONSE_DUE_DATE={(as_of + timedelta(days=REASK_DUE_DAYS)).isoformat()} '
        f'CONFIRM={REASK_LOG_CONFIRMATION} OUT={owner_reask_log_output(as_of)}'
    )


def reask_command(as_of: date, source_artifact: Path | str) -> str:
    return contact_status_command(
        status='reask-awaiting-reply',
        sent=as_of,
        due=as_of + timedelta(days=REASK_DUE_DAYS),
        status_date=as_of,
        attempt_count=2,
        status_slug='reask',
        source_artifact=source_artifact,
    )


def contact_reask_from_reask_log_command(reask_log: LocalArtifact, as_of: date) -> str:
    sent = parse_iso(str(reask_log.data.get('sent_date') or ''), 'sent_date')
    due = parse_iso(str(reask_log.data.get('response_due_date') or ''), 'response_due_date')
    return contact_status_command(
        status='reask-awaiting-reply',
        sent=sent,
        due=due,
        status_date=as_of,
        attempt_count=2,
        status_slug='reask',
        source_artifact=reask_log.path,
    )


def no_owner_packet_command(sent: str, due: str, as_of: date, source_artifact: Path | str) -> str:
    try:
        sent_date = parse_iso(sent, 'sent_date')
    except ValueError:
        sent_date = as_of
    try:
        due_date = parse_iso(due, 'response_due_date')
    except ValueError:
        due_date = as_of
    return contact_status_command(
        status='no-owner-packet',
        sent=sent_date,
        due=due_date,
        status_date=as_of,
        attempt_count=2,
        status_slug='no-owner-packet',
        source_artifact=source_artifact,
    )


def workbench_seed_command(bundle_dir: Path) -> str:
    return f'make owner-reply-workbench-seed BUNDLE={shell_quote(relative(bundle_dir))}'


def workbench_review_brief_command(seed_path: Path) -> str:
    return f'make owner-workbench-review-brief SEED={shell_quote(relative(seed_path))}'


def workbench_review_command(seed_path: Path) -> str:
    return (
        f'make owner-workbench-review SEED={shell_quote(relative(seed_path))} '
        'DECISION=proceed-decision-board SOURCE_TRUTH_CLASS=SRC2-CANDIDATE-NOT-ACCEPTED REVIEW_BASIS=owner-attested-aggregate '
        'SURVIVING_FIELD_COUNT=1 DECISION_CHANGED_COUNT=1 LOCAL_ONLY_FIELD_COUNT=0 TRIMMED_FIELD_COUNT=0 '
        'REASK_FIELD_COUNT=0 REVIEWER_ROLE_COUNT=2 CONFIRM=human-reviewed-minimized-workbench-record'
    )


def first_packet_decision_brief_command(review_path: Path) -> str:
    return f'make owner-first-packet-decision-brief REVIEW={shell_quote(relative(review_path))}'


def first_packet_decision_command(review_path: Path) -> str:
    return (
        f'make owner-first-packet-decision REVIEW={shell_quote(relative(review_path))} '
        'AUTHORITY_ACTION=keep-lower-ceiling EVIDENCE_ACTION=downgrade '
        'CONSTRUCT_ACTION=keep-teacher-review PUBLIC_ACTION=draft-only LIFECYCLE_ACTION=watch '
        'CHANGED_SLICE_COUNT=5 ROLLBACK_OWNER_ROLE_COUNT=1 '
        'CONFIRM=human-recorded-five-slice-decision-board'
    )


def activation_receipt_command(decision_path: Path) -> str:
    return (
        f'make owner-activation-receipt DECISION={shell_quote(relative(decision_path))} '
        'SOURCE_PACKET=/path/to/same-returned-owner-csv-that-seeded-this-decision.csv SOURCE_TRUTH_CLASS=SRC2 '
        'ACCEPTED_FIELD_COUNT=1 REVIEWER_ROLE_COUNT=2 DICTIONARY_OR_MAP_REF_COUNT=1 '
        f'CONFIRM={ACTIVATION_RECEIPT_CONFIRMATION} '
        'OUT=scratch/field/ft0181/owner-activation-receipts/aiedu-sr-003-accepted-real-packet'
    )


def post_decision_change_ticket_command(decision_path: Path, activation_receipt: Path | None = None, source_truth_required: str = 'SRC2') -> str:
    if activation_receipt is not None:
        return (
            f'make owner-post-decision-change-ticket DECISION={shell_quote(relative(decision_path))} '
            'TICKET_STATE=active-change CHANGE_CLASS=pct-c-sandbox-adjustment '
            f'SOURCE_TRUTH_REQUIRED={source_truth_required} PUBLIC_CLAIM_CEILING=example-only-no-outcome-claim '
            'ALLOWED_CHANGE_COUNT=1 PROHIBITED_CHANGE_COUNT=4 ROLLBACK_TRIGGER_COUNT=3 '
            'ROLLBACK_OWNER_ROLE_COUNT=1 LIVE_WINDOW_REQUIRED=1 '
            f'ACTIVATION_RECEIPT={shell_quote(relative(activation_receipt))} '
            'CONFIRM=human-recorded-bounded-post-decision-change-ticket'
        )
    return (
        f'make owner-post-decision-change-ticket DECISION={shell_quote(relative(decision_path))} '
        'TICKET_STATE=ready-for-real-packet CHANGE_CLASS=pct-c-sandbox-adjustment '
        'SOURCE_TRUTH_REQUIRED=SRC2 PUBLIC_CLAIM_CEILING=example-only-no-outcome-claim '
        'ALLOWED_CHANGE_COUNT=1 PROHIBITED_CHANGE_COUNT=4 ROLLBACK_TRIGGER_COUNT=3 '
        'ROLLBACK_OWNER_ROLE_COUNT=1 LIVE_WINDOW_REQUIRED=1 '
        'CONFIRM=human-recorded-bounded-post-decision-change-ticket'
    )



def post_decision_change_ticket_brief_command(decision_path: Path) -> str:
    return f'make owner-post-decision-change-ticket-brief DECISION={shell_quote(relative(decision_path))}'




def activation_live_window_brief_command(ticket_path: Path) -> str:
    return f'make owner-activation-live-window-brief TICKET={shell_quote(relative(ticket_path))}'

def activation_from_brief_command(brief: dict[str, Any]) -> str:
    command = brief.get('activation_receipt_command_template')
    return command if isinstance(command, str) and command else 'no field command; activation brief is missing a valid command template; regenerate the brief'


def live_window_from_brief_command(brief: dict[str, Any]) -> str:
    commands = brief.get('live_window_card_command_templates') if isinstance(brief.get('live_window_card_command_templates'), dict) else {}
    command = commands.get('staged_small_window')
    return command if isinstance(command, str) and command else 'no field command; live-window brief is missing a valid staged command template; regenerate the brief'

def live_window_card_command(ticket_path: Path) -> str:
    return (
        f'make owner-live-window-card TICKET={shell_quote(relative(ticket_path))} '
        'WINDOW_STATE=staged SOURCE_TRUTH_CLASS=SRC2 WINDOW_DAY_COUNT=5 '
        'ALLOWED_ACTIVITY_COUNT=1 PROHIBITED_ACTIVITY_COUNT=5 STOP_TRIGGER_COUNT=3 '
        'ROLLBACK_STEP_COUNT=3 ROLLBACK_OWNER_ROLE_COUNT=1 EVIDENCE_READOUT_COUNT=3 '
        'NO_EXPANSION_CONFIRMED=1 HUMAN_PAUSE_CONFIRMED=1 FALLBACK_ROUTE_CONFIRMED=1 '
        f'CONFIRM={LIVE_WINDOW_CONFIRMATION}'
    )


def live_window_terminal_brief_command(card_path: Path) -> str:
    return f'make owner-live-window-terminal-brief CARD={shell_quote(relative(card_path))}'


def terminal_card_from_brief_command(brief: dict[str, Any]) -> str:
    commands = brief.get('terminal_card_command_templates') if isinstance(brief.get('terminal_card_command_templates'), dict) else {}
    command = commands.get('completed_no_closure')
    return command if isinstance(command, str) and command else 'no field command; live-window terminal brief is missing a valid completed_no_closure command template; regenerate the brief'


def live_window_readout_brief_command(card_path: Path) -> str:
    return f'make owner-live-window-readout-brief CARD={shell_quote(relative(card_path))}'


def live_window_readout_from_brief_command(brief: dict[str, Any]) -> str:
    commands = brief.get('readout_command_templates') if isinstance(brief.get('readout_command_templates'), dict) else {}
    command = commands.get('primary')
    return command if isinstance(command, str) and command else 'no field command; live-window readout brief is missing a valid primary command template; regenerate the brief'


def post_readout_action_brief_command(readout_path: Path, as_of: date) -> str:
    return f'make owner-post-readout-action-brief READOUT={shell_quote(relative(readout_path))} AS_OF_DATE={as_of.isoformat()}'


def post_readout_action_from_brief_command(brief: dict[str, Any]) -> str:
    commands = brief.get('post_readout_action_command_templates') if isinstance(brief.get('post_readout_action_command_templates'), dict) else {}
    command = commands.get('primary')
    return command if isinstance(command, str) and command else 'no field command; post-readout action brief is missing a valid primary command template; regenerate the brief'


def post_readout_recheck_brief_command(action_path: Path, as_of: date) -> str:
    return f'make owner-post-readout-recheck-brief ACTION={shell_quote(relative(action_path))} AS_OF_DATE={as_of.isoformat()}'


def post_readout_recheck_from_brief_command(brief: dict[str, Any]) -> str:
    commands = brief.get('post_readout_recheck_command_templates') if isinstance(brief.get('post_readout_recheck_command_templates'), dict) else {}
    command = commands.get('primary')
    return command if isinstance(command, str) and command else 'no field command; post-readout recheck brief is missing a valid primary command template; regenerate the brief'


def live_window_readout_command(card_path: Path, disposition: str = 'continue-bounded') -> str:
    return (
        f'make owner-live-window-readout CARD={shell_quote(relative(card_path))} '
        f'WINDOW_DISPOSITION={disposition} SOURCE_TRUTH_CLASS=SRC2 '
        'AGGREGATE_EVIDENCE_READ_COUNT=3 CLAIM_FAMILY_EFFECT_COUNT=2 '
        'DECISION_DELTA_COUNT=1 FIELD_TRIM_COUNT=0 REVIEWER_ROLE_COUNT=2 '
        'NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_READOUT=1 '
        f'CONFIRM={LIVE_WINDOW_READOUT_CONFIRMATION}'
    )


def post_readout_action_command(readout: LocalArtifact, as_of: date) -> str:
    disposition = str(readout.data.get('window_disposition') or '')
    lane = {
        'blocked_no_real_packet': 'blocked-no-real-packet',
        'stopped': 'stop',
        'rolled_back': 'rollback-confirmed',
        'continue_bounded': 'continue-same-ceiling',
        'rerun_narrower': 'rerun-narrower',
        'quarantine': 'quarantine',
        'no_change': 'no-change-trim',
    }.get(disposition, 'continue-same-ceiling')
    readout_counts = readout.data.get('readout_counts') if isinstance(readout.data.get('readout_counts'), dict) else {}
    reviewer_count = max(2, int(readout_counts.get('reviewer_role_count') or 2))
    field_drop_count = int(readout_counts.get('field_trim_count') or 0)
    field_reask_count = 1 if lane == 'rerun-narrower' else 0
    if lane in {'rerun-narrower', 'no-change-trim'} and field_drop_count < 1:
        field_drop_count = 1
    due = as_of + timedelta(days=7)
    return (
        f'make owner-post-readout-action READOUT={shell_quote(relative(readout.path))} '
        f'DISPATCH_LANE={lane} SOURCE_TRUTH_CLASS={shell_quote(str(readout.data.get("source_truth_class") or "SRC2"))} '
        'ALLOWED_ACTION_COUNT=1 PROHIBITED_ACTION_COUNT=5 '
        f'FIELD_TO_REASK_COUNT={field_reask_count} FIELD_TO_DROP_COUNT={field_drop_count} '
        f'REVIEWER_ROLE_COUNT={reviewer_count} DUE_OR_RECHECK_DATE={due.isoformat()} '
        'NO_EXPANSION_CONFIRMED=1 NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 '
        'NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_DISPATCH=1 '
        f'CONFIRM={POST_READOUT_ACTION_CONFIRMATION}'
    )




def post_readout_recheck_output(as_of: date) -> str:
    return f'scratch/field/ft0181/owner-post-readout-rechecks/aiedu-sr-003-recheck-{as_of.isoformat()}'


def post_readout_recheck_command(action: LocalArtifact, as_of: date, outcome: str = 'no-new-owner-context') -> str:
    action_counts = action.data.get('dispatch_counts') if isinstance(action.data.get('dispatch_counts'), dict) else {}
    reviewer_count = max(2, int(action_counts.get('reviewer_role_count') or 2))
    return (
        f'make owner-post-readout-recheck ACTION={shell_quote(relative(action.path))} '
        f'CHECK_DATE={as_of.isoformat()} RECHECK_OUTCOME={outcome} REVIEWER_ROLE_COUNT={reviewer_count} '
        'NO_EXPANSION_CONFIRMED=1 NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 '
        'NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_RECHECK=1 '
        f'CONFIRM={POST_READOUT_RECHECK_CONFIRMATION} OUT={post_readout_recheck_output(as_of)}'
    )




def sha256_file(path: Path) -> str:
    h = __import__('hashlib').sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def post_readout_context_receipt_output(csv_path: Path) -> str:
    stem = csv_path.stem.replace(' ', '-').replace('/', '-')[:48] or 'post-readout-owner-context'
    return f'scratch/field/ft0181/owner-post-readout-context-receipts/{stem}-{sha256_file(csv_path)[:12]}'


def post_readout_context_receipt_command(recheck: LocalArtifact, csv_path: Path) -> str:
    counts = recheck.data.get('recheck_counts') if isinstance(recheck.data.get('recheck_counts'), dict) else {}
    reviewer_count = max(2, int(counts.get('reviewer_role_count') or 2))
    return (
        f'make owner-post-readout-context-receipt RECHECK={shell_quote(relative(recheck.path))} '
        f'CSV={shell_quote(csv_path.as_posix())} REVIEWER_ROLE_COUNT={reviewer_count} '
        'NO_EXPANSION_CONFIRMED=1 NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 '
        'NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_CONTEXT_RECEIPT=1 '
        f'CONFIRM={POST_READOUT_CONTEXT_RECEIPT_CONFIRMATION} OUT={post_readout_context_receipt_output(csv_path)}'
    )


def intake_from_post_readout_context_receipt_command(csv_path: Path, receipt_path: Path) -> str:
    return (
        f'make owner-returned-reply-work CSV={shell_quote(csv_path.as_posix())} '
        f'SOURCE_POST_READOUT_CONTEXT_RECEIPT={shell_quote(relative(receipt_path))}'
    )


def context_receipt_csv_reroute_command(receipt: LocalArtifact) -> str:
    source_csv = receipt.data.get('source_csv') if isinstance(receipt.data.get('source_csv'), dict) else {}
    source_ref = str(source_csv.get('source_reference') or '')
    if source_csv.get('path_scope') == 'scratch_returned_csv' and source_ref:
        csv_arg = source_ref
    else:
        basename = str(source_csv.get('basename') or 'same-returned-owner-context.csv')
        csv_arg = f'/path/to/same-returned-owner-context/{basename}'
    return (
        f'make owner-field-next CSV={shell_quote(csv_arg)} '
        'OUT=scratch/field/ft0181/ft0181-field-next-action/post-readout-context-receipt-intake'
    )


def receipt_matches_recheck(receipt: LocalArtifact, recheck: LocalArtifact) -> bool:
    source = receipt.data.get('source_post_readout_recheck')
    if not isinstance(source, dict):
        return False
    if source.get('reference') != relative(recheck.path):
        return False
    try:
        recheck_sha = sha256_file(recheck.path)
    except OSError:
        return False
    return source.get('recheck_sha256') == recheck_sha


def matching_post_readout_context_receipt(receipts: list[LocalArtifact], csv_path: Path, source_recheck: LocalArtifact) -> LocalArtifact | None:
    digest = sha256_file(csv_path)
    matches = []
    for item in receipts:
        if item.data.get('source_csv', {}).get('sha256') == digest and receipt_matches_recheck(item, source_recheck):
            matches.append(item)
    return latest(matches)

def parse_due_or_recheck_date(action: LocalArtifact) -> date | None:
    value = action.data.get('due_or_recheck_date')
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None

def integrity_block(outcome: str, reason: str, source_artifact: str | None = None) -> dict[str, Any]:
    return {
        'ok': True,
        'outcome': outcome,
        'reason': reason,
        'recommended_command': 'no field command; inspect or regenerate the selected local scratch artifact through the bounded make targets',
        'source_artifact': source_artifact,
        'allowed_only': ['local-scratch-artifact-repair', 'rerun-owner-field-next-after-repair'],
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
        'integrity_effect': 'blocks_routing_until_selected_local_artifact_is_repaired',
    }


def decision_for(
    *,
    scratch_root: Path,
    returned_csv: Path | None,
    as_of_date: str,
) -> dict[str, Any]:
    as_of = parse_iso(as_of_date, 'as-of-date')
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root

    if returned_csv is not None:
        csv_path = returned_csv if returned_csv.is_absolute() else Path.cwd() / returned_csv
        if not csv_path.exists():
            return {
                'ok': False,
                'outcome': 'RETURNED-CSV-MISSING',
                'error': f'returned CSV does not exist: {returned_csv}',
                'recommended_command': None,
                'claim_ceiling': CLAIM_CEILING,
            }
        allowed, csv_boundary = returned_owner_csv_allowed(csv_path, archive_root=ROOT)
        if not allowed:
            return {
                'ok': False,
                'outcome': 'RETURNED-CSV-SOURCE-BLOCKED',
                'error': csv_boundary,
                'recommended_command': None,
                'claim_ceiling': CLAIM_CEILING,
            }
        marker = returned_owner_csv_marker_block(csv_path)
        if marker:
            return {
                'ok': False,
                'outcome': 'RETURNED-CSV-SMOKE-BLOCKED',
                'error': f'returned CSV includes non-field smoke/fixture marker: {marker}',
                'recommended_command': None,
                'claim_ceiling': CLAIM_CEILING,
            }
        source_rechecks = collect(scratch, 'owner-post-readout-rechecks/**/post-readout-recheck.json', 'post_readout_recheck', 'recheck_state')
        source_context_receipts = collect(scratch, 'owner-post-readout-context-receipts/**/post-readout-context-receipt.json', 'post_readout_context_receipt', 'receipt_state')
        latest_new_context_recheck = latest([item for item in source_rechecks if item.data.get('recheck_outcome') == 'new_owner_context_available'])
        if latest_new_context_recheck is not None:
            recheck_error = owner_post_readout_recheck_integrity_error(latest_new_context_recheck.data, archive_root=ROOT)
            if recheck_error:
                return {
                    'ok': False,
                    'outcome': 'RETURNED-CSV-POST-READOUT-RECHECK-BLOCKED',
                    'error': recheck_error,
                    'recommended_command': None,
                    'source_post_readout_recheck': relative(latest_new_context_recheck.path),
                    'claim_ceiling': CLAIM_CEILING,
                }
            matching_receipt = matching_post_readout_context_receipt(source_context_receipts, csv_path, latest_new_context_recheck)
            if matching_receipt is None:
                return {
                    'ok': True,
                    'outcome': 'RECORD-POST-READOUT-CONTEXT-RECEIPT-BEFORE-INTAKE',
                    'reason': 'A post-readout recheck says new owner context exists. Before intake, link that recheck to the actual returned CSV/source packet hash with a scratch-local post-readout context receipt; do not source intake from the recheck prose or an old contact clock.',
                    'recommended_command': post_readout_context_receipt_command(latest_new_context_recheck, csv_path),
                    'source_artifact': csv_path.as_posix(),
                    'source_post_readout_recheck': relative(latest_new_context_recheck.path),
                    'input_boundary': csv_boundary,
                    'allowed_only': ['owner-post-readout-context-receipt'],
                    'claim_ceiling': CLAIM_CEILING,
                    'ft0181_status': 'live',
                }
            receipt_error = owner_post_readout_context_receipt_integrity_error(matching_receipt.data, archive_root=ROOT)
            if receipt_error:
                return {
                    'ok': False,
                    'outcome': 'RETURNED-CSV-POST-READOUT-CONTEXT-RECEIPT-BLOCKED',
                    'error': receipt_error,
                    'recommended_command': None,
                    'source_post_readout_context_receipt': relative(matching_receipt.path),
                    'claim_ceiling': CLAIM_CEILING,
                }
            return {
                'ok': True,
                'outcome': 'RUN-RETURNED-REPLY-WORK-FROM-POST-READOUT-CONTEXT-RECEIPT',
                'reason': 'The actual returned CSV/source packet is hash-linked to the post-readout new-context recheck by a valid local receipt. Route intake from that receipt, not from the recheck text or an old contact clock.',
                'recommended_command': intake_from_post_readout_context_receipt_command(csv_path, matching_receipt.path),
                'source_artifact': csv_path.as_posix(),
                'source_post_readout_context_receipt': relative(matching_receipt.path),
                'input_boundary': csv_boundary,
                'allowed_only': ['owner-returned-reply-work-from-post-readout-context-receipt'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }

        source_contacts = collect(scratch, 'owner-contact-status/**/contact-status.json', 'contact_status', 'contact_status')
        latest_source_contact = latest(source_contacts)
        if latest_source_contact is None:
            return {
                'ok': False,
                'outcome': 'RETURNED-CSV-SOURCE-PROVENANCE-MISSING',
                'error': 'returned CSV intake requires either an active scratch SENT_AWAITING_REPLY/REASK_AWAITING_REPLY contact-status clock or a post-readout context receipt tied to a new-context recheck; run the packet/send-log/contact-status path first or record the post-readout context receipt.',
                'recommended_command': None,
                'claim_ceiling': CLAIM_CEILING,
            }
        source_contact_error = owner_contact_status_integrity_error(latest_source_contact.data, archive_root=ROOT)
        if source_contact_error:
            return {
                'ok': False,
                'outcome': 'RETURNED-CSV-SOURCE-CLOCK-BLOCKED',
                'error': source_contact_error,
                'recommended_command': None,
                'source_contact_status': relative(latest_source_contact.path),
                'claim_ceiling': CLAIM_CEILING,
            }
        return {
            'ok': True,
            'outcome': 'RUN-RETURNED-REPLY-WORK',
            'reason': 'A plausible local returned owner CSV path was provided and tied to the latest active bounded contact clock; run bounded returned-reply work to intake it and, only if PROCEED-STAGED, create a NOT_ACCEPTED workbench seed before any human review, custody, claim, live-window, or closure step.',
            'recommended_command': command_for_returned_csv(csv_path, latest_source_contact.path),
            'source_artifact': csv_path.as_posix(),
            'source_contact_status': relative(latest_source_contact.path),
            'input_boundary': csv_boundary,
            'allowed_only': ['owner-returned-reply-work'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }

    packets = collect(scratch, 'owner-request-packets/**/packet-manifest.json', 'packet', 'packet_state')
    route_blocks = collect(scratch, 'owner-route-blocks/**/route-block.json', 'route_block', 'route_block_type')
    send_logs = collect(scratch, 'owner-send-logs/**/send-log.json', 'send_log', 'send_log_type')
    reask_logs = collect(scratch, 'owner-reask-logs/**/reask-log.json', 'reask_log', 'reask_log_type')
    contacts = collect(scratch, 'owner-contact-status/**/contact-status.json', 'contact_status', 'contact_status')
    intakes = collect(scratch, 'owner-reply-intakes/**/bundle-manifest.json', 'intake_bundle', 'triage_outcome')
    seeds = collect(scratch, 'owner-reply-workbench-seeds/**/workbench-seed.json', 'workbench_seed', 'acceptance_state')
    review_briefs = collect(scratch, 'owner-workbench-review-briefs/**/review-brief.json', 'workbench_review_brief', 'brief_state')
    reviews = collect(scratch, 'owner-workbench-reviews/**/workbench-review.json', 'workbench_review', 'review_state')
    decision_briefs = collect(scratch, 'owner-first-packet-decision-briefs/**/decision-brief.json', 'first_packet_decision_brief', 'brief_state')
    decisions = collect(scratch, 'owner-first-packet-decisions/**/first-packet-decision.json', 'first_packet_decision', 'board_state')
    change_ticket_briefs = collect(scratch, 'owner-post-decision-change-ticket-briefs/**/change-ticket-brief.json', 'post_decision_change_ticket_brief', 'brief_state')
    activation_live_window_briefs = collect(scratch, 'owner-activation-live-window-briefs/**/activation-live-window-brief.json', 'activation_live_window_brief', 'brief_state')
    live_window_terminal_briefs = collect(scratch, 'owner-live-window-terminal-briefs/**/terminal-brief.json', 'live_window_terminal_brief', 'brief_state')
    live_window_readout_briefs = collect(scratch, 'owner-live-window-readout-briefs/**/live-window-readout-brief.json', 'live_window_readout_brief', 'brief_state')
    activation_receipts = collect(scratch, 'owner-activation-receipts/**/activation-receipt.json', 'activation_receipt', 'activation_state')
    tickets = collect(scratch, 'owner-post-decision-change-tickets/**/post-decision-change-ticket.json', 'post_decision_change_ticket', 'ticket_state')
    live_cards = collect(scratch, 'owner-live-window-cards/**/live-window-card.json', 'live_window_card', 'window_state')
    live_readouts = collect(scratch, 'owner-live-window-readouts/**/live-window-readout.json', 'live_window_readout', 'readout_state')
    post_readout_action_briefs = collect(scratch, 'owner-post-readout-action-briefs/**/post-readout-action-brief.json', 'post_readout_action_brief', 'brief_state')
    post_readout_recheck_briefs = collect(scratch, 'owner-post-readout-recheck-briefs/**/post-readout-recheck-brief.json', 'post_readout_recheck_brief', 'brief_state')
    post_readout_actions = collect(scratch, 'owner-post-readout-actions/**/post-readout-action.json', 'post_readout_action', 'dispatch_state')
    post_readout_rechecks = collect(scratch, 'owner-post-readout-rechecks/**/post-readout-recheck.json', 'post_readout_recheck', 'recheck_state')
    post_readout_context_receipts = collect(scratch, 'owner-post-readout-context-receipts/**/post-readout-context-receipt.json', 'post_readout_context_receipt', 'receipt_state')

    counts = artifact_counts(packets, route_blocks, send_logs, reask_logs, contacts, intakes, seeds, review_briefs, reviews, decision_briefs, decisions, change_ticket_briefs, activation_live_window_briefs, live_window_terminal_briefs, live_window_readout_briefs, activation_receipts, tickets, live_cards, live_readouts, post_readout_action_briefs, post_readout_recheck_briefs, post_readout_actions, post_readout_rechecks, post_readout_context_receipts)
    latest_packet = latest(packets)
    latest_route_block = latest(route_blocks)
    latest_send_log = latest(send_logs)
    latest_reask_log = latest(reask_logs)
    latest_contact = latest(contacts)
    latest_terminal_contact = latest_no_owner_packet_status(contacts)
    latest_intake = latest(intakes)
    latest_seed = latest(seeds)
    latest_review_brief = latest(review_briefs)
    latest_review = latest(reviews)
    latest_decision_brief = latest(decision_briefs)
    latest_decision = latest(decisions)
    latest_change_ticket_brief = latest(change_ticket_briefs)
    latest_activation_live_window_brief = latest(activation_live_window_briefs)
    latest_live_window_terminal_brief = latest(live_window_terminal_briefs)
    latest_live_window_readout_brief = latest(live_window_readout_briefs)
    latest_activation_receipt = latest(activation_receipts)
    latest_ticket = latest(tickets)
    latest_live_card = latest(live_cards)
    latest_live_readout = latest(live_readouts)
    latest_post_readout_action_brief = latest(post_readout_action_briefs)
    latest_post_readout_recheck_brief = latest(post_readout_recheck_briefs)
    latest_post_readout_action = latest(post_readout_actions)
    latest_post_readout_recheck = latest(post_readout_rechecks)
    latest_post_readout_context_receipt = latest(post_readout_context_receipts)
    candidates = {
        'packet': latest_packet,
        'route_block': latest_route_block,
        'send_log': latest_send_log,
        'reask_log': latest_reask_log,
        'contact_status': latest_contact,
        'terminal_no_owner_packet_status': latest_terminal_contact,
        'intake_bundle': latest_intake,
        'workbench_seed': latest_seed,
        'workbench_review_brief': latest_review_brief,
        'workbench_review': latest_review,
        'first_packet_decision_brief': latest_decision_brief,
        'first_packet_decision': latest_decision,
        'post_decision_change_ticket_brief': latest_change_ticket_brief,
        'activation_live_window_brief': latest_activation_live_window_brief,
        'live_window_terminal_brief': latest_live_window_terminal_brief,
        'live_window_readout_brief': latest_live_window_readout_brief,
        'activation_receipt': latest_activation_receipt,
        'post_decision_change_ticket': latest_ticket,
        'live_window_card': latest_live_card,
        'live_window_readout': latest_live_readout,
        'post_readout_action_brief': latest_post_readout_action_brief,
        'post_readout_recheck_brief': latest_post_readout_recheck_brief,
        'post_readout_action': latest_post_readout_action,
        'post_readout_recheck': latest_post_readout_recheck,
        'post_readout_context_receipt': latest_post_readout_context_receipt,
    }

    def ctx(decision: dict[str, Any], selected: LocalArtifact | None = None) -> dict[str, Any]:
        return with_context(decision, counts=counts, selected=selected, candidates=candidates)

    latest_post_packet = latest([item for item in [latest_route_block, latest_send_log, latest_reask_log, latest_contact, latest_intake, latest_seed, latest_review_brief, latest_review, latest_decision_brief, latest_decision, latest_change_ticket_brief, latest_activation_live_window_brief, latest_live_window_terminal_brief, latest_live_window_readout_brief, latest_activation_receipt, latest_ticket, latest_live_card, latest_live_readout, latest_post_readout_action_brief, latest_post_readout_recheck_brief, latest_post_readout_action, latest_post_readout_recheck, latest_post_readout_context_receipt] if item is not None])

    if (
        latest_post_packet is not None
        and latest_post_packet.kind in {'contact_status', 'send_log'}
        and latest_terminal_contact is not None
        and latest_post_packet.data.get('contact_status') != 'NO_OWNER_PACKET'
        and event_order(latest_post_packet) > event_order(latest_terminal_contact)
    ):
        return ctx(integrity_block(
            'CONTACT-STATUS-TERMINAL-REGRESSION-BLOCKED',
            'A NO_OWNER_PACKET status already exists in this scratch root; a later SEND-LOG/SENT/REASK artifact would reopen a bounded no-packet field session without new returned owner context. Start a new scratch root only if genuinely new owner context exists, or keep FT-0181 live as blocked by missing owner packet.',
            relative(latest_post_packet.path),
        ), selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'route_block':
        route_block_error = owner_route_block_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if route_block_error:
            return ctx(integrity_block(
                'OWNER-ROUTE-BLOCK-INTEGRITY-BLOCKED',
                f'The latest local owner-route block cannot halt the field path: {route_block_error}. Rerun make owner-route-block from the packet or router-emitted fallback command instead of editing scratch manifests or treating a route block as evidence.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'OWNER-ROUTE-BLOCK-RECORDED-NO-SEND',
            'reason': 'A local route-block record exists for the bounded packet; keep FT-0181 live and do not record a send log, contact clock, intake, evidence, closure, or public-claim step until a real accountable owner route exists.',
            'recommended_command': 'no field command; keep FT-0181 live as blocked by missing accountable owner route',
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['wait-for-real-accountable-owner-route-or-new-owner-context'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'send_log':
        send_log_error = owner_send_log_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if send_log_error:
            return ctx(integrity_block(
                'OWNER-SEND-LOG-INTEGRITY-BLOCKED',
                f'The latest local owner-send log cannot drive a sent clock: {send_log_error}. Rerun make owner-send-log from the router-emitted command instead of editing scratch manifests or treating a send log as evidence.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'RECORD-SENT-FROM-SEND-LOG',
            'reason': 'A local send-log exists for the bounded packet; record SENT_AWAITING_REPLY from that send-log instead of from the prepared packet manifest. The preferred post-send path is now make owner-after-human-send, but this router branch remains the repair path for already-written send logs.',
            'recommended_command': contact_sent_from_send_log_command(latest_post_packet, as_of),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-contact-status:sent-awaiting-reply'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'reask_log':
        reask_log_error = owner_reask_log_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if reask_log_error:
            return ctx(integrity_block(
                'OWNER-REASK-LOG-INTEGRITY-BLOCKED',
                f'The latest local owner-reask log cannot drive a reask clock: {reask_log_error}. Rerun make owner-reask-log from the router-emitted command instead of editing scratch manifests or treating a reask log as evidence.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'RECORD-REASK-FROM-REASK-LOG',
            'reason': 'A local reask-log exists for the one bounded clarification; record REASK_AWAITING_REPLY from that reask-log instead of from the intake bundle, prior contact clock, or workbench review.',
            'recommended_command': contact_reask_from_reask_log_command(latest_post_packet, as_of),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-contact-status:reask-awaiting-reply'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'post_readout_context_receipt':
        receipt_error = owner_post_readout_context_receipt_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if receipt_error:
            return ctx(integrity_block(
                'POST-READOUT-CONTEXT-RECEIPT-INTEGRITY-BLOCKED',
                f'The latest local post-readout context receipt cannot source intake: {receipt_error}. Rerun make owner-post-readout-context-receipt from the current new-context recheck and the same actual returned owner context CSV instead of editing receipt records or treating them as evidence, service-record changes, public language, lifecycle state, custody, acceptance, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        source_csv = latest_post_packet.data.get('source_csv') if isinstance(latest_post_packet.data.get('source_csv'), dict) else {}
        return ctx({
            'ok': True,
            'outcome': 'POST-READOUT-CONTEXT-RECEIPT-RECORDED-ROUTE-ACTUAL-CONTEXT-CSV',
            'reason': 'A bounded post-readout context receipt exists, but the receipt itself is not intake and does not copy the owner context. Rerun owner-field-next with the same actual returned CSV/source packet so the CSV source/smoke guards and SOURCE_POST_READOUT_CONTEXT_RECEIPT intake path run together.',
            'recommended_command': context_receipt_csv_reroute_command(latest_post_packet),
            'source_artifact': relative(latest_post_packet.path),
            'source_csv_sha256': source_csv.get('sha256'),
            'source_csv_basename': source_csv.get('basename'),
            'allowed_only': ['owner-field-next-with-same-post-readout-owner-context-csv'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'post_readout_recheck':
        recheck_error = owner_post_readout_recheck_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if recheck_error:
            return ctx(integrity_block(
                'POST-READOUT-RECHECK-INTEGRITY-BLOCKED',
                f'The latest local post-readout recheck cannot stop or reroute the owner-action lane: {recheck_error}. Rerun make owner-post-readout-recheck from a valid post-readout action dispatch instead of editing recheck records or treating them as evidence, service-record changes, public language, lifecycle state, custody, acceptance, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        outcome = latest_post_packet.data.get('recheck_outcome')
        if outcome == 'new_owner_context_available':
            return ctx({
                'ok': True,
                'outcome': 'POST-READOUT-RECHECK-RECORDED-NEW-OWNER-CONTEXT-ROUTE-FIRST',
                'reason': 'A bounded post-readout recheck says new real owner context exists outside the archive. Do not intake from the recheck record; rerun owner-field-next with the actual returned CSV/source packet path so source-clock and smoke/source guards run first.',
                'recommended_command': 'make owner-field-next CSV=/path/to/actual-returned-owner-context.csv OUT=scratch/field/ft0181/ft0181-field-next-action/post-readout-returned-owner-context',
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-field-next-with-actual-returned-owner-context-csv'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'POST-READOUT-RECHECK-RECORDED-NO-FURTHER-ARCHIVE-ACTION',
            'reason': f'A bounded post-readout recheck exists with outcome {outcome}; it is local context only and does not authorize service-record edits, lifecycle moves, public-summary updates, custody, acceptance, or FT-0181 closure.',
            'recommended_command': 'no field command; keep FT-0181 live until new real owner context appears and route that context through owner-field-next',
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['wait-for-new-real-owner-context', 'owner-field-next-only-with-actual-returned-csv'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'post_readout_action_brief':
        brief_error = owner_post_readout_action_brief_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if brief_error:
            return ctx(integrity_block(
                'POST-READOUT-ACTION-BRIEF-INTEGRITY-BLOCKED',
                f'The latest local post-readout action brief cannot drive dispatch recording: {brief_error}. Rerun make owner-post-readout-action-brief from a valid terminal live-window readout instead of editing brief records or treating them as post-readout dispatches, owner action, evidence, service-record changes, public language, lifecycle state, custody, acceptance, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'RECORD-POST-READOUT-ACTION-FROM-BRIEF-NOT-CLOSURE',
            'reason': 'A scratch-local post-readout action brief exists for a terminal aggregate readout. A human must record exactly one bounded dispatch lane before any owner-held action, recheck, service-record edit, lifecycle move, public-summary update, custody, acceptance, or closure step.',
            'recommended_command': post_readout_action_from_brief_command(latest_post_packet.data),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-post-readout-action-after-human-dispatch-choice'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'post_readout_recheck_brief':
        brief_error = owner_post_readout_recheck_brief_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if brief_error:
            return ctx(integrity_block(
                'POST-READOUT-RECHECK-BRIEF-INTEGRITY-BLOCKED',
                f'The latest local post-readout recheck brief cannot drive due-date recheck recording: {brief_error}. Rerun make owner-post-readout-recheck-brief from a valid due post-readout action dispatch instead of editing brief records or treating them as rechecks, owner context, evidence, service-record changes, public language, lifecycle state, custody, acceptance, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'RECORD-POST-READOUT-RECHECK-FROM-BRIEF-NOT-CLOSURE',
            'reason': 'A scratch-local post-readout recheck brief exists for a due post-readout action dispatch. A human must choose exactly one bounded recheck outcome before any context receipt, service-record edit, lifecycle move, public-summary update, custody, acceptance, or closure step.',
            'recommended_command': post_readout_recheck_from_brief_command(latest_post_packet.data),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-post-readout-recheck-after-human-recheck-choice'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'post_readout_action':
        action_error = owner_post_readout_action_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if action_error:
            return ctx(integrity_block(
                'POST-READOUT-ACTION-INTEGRITY-BLOCKED',
                f'The latest local post-readout action dispatch cannot stop the readout lane: {action_error}. Rerun make owner-post-readout-action from a valid terminal live-window readout instead of editing dispatch records or treating them as evidence, service-record changes, public language, lifecycle state, custody, acceptance, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        due = parse_due_or_recheck_date(latest_post_packet)
        if due is None:
            return ctx(integrity_block(
                'POST-READOUT-ACTION-DUE-DATE-BLOCKED',
                'The latest local post-readout action dispatch has an invalid due_or_recheck_date; regenerate the dispatch rather than treating an undated owner-action lane as complete.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        if as_of < due:
            return ctx({
                'ok': True,
                'outcome': 'AWAIT-POST-READOUT-ACTION-RECHECK',
                'reason': f'A bounded post-readout action dispatch exists with due/recheck date {due.isoformat()}; do not record completion, service-record edits, lifecycle moves, public-summary updates, custody, acceptance, or closure before that date or before new real owner context appears.',
                'recommended_command': 'no field command; execute only the named owner-held action lane outside the archive and rerun owner-field-next on/after the due/recheck date or with actual new owner context',
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-held-action-outside-archive-until-due-date', 'owner-field-next-with-actual-returned-csv-if-new-context-arrives'],
                'due_or_recheck_date': due.isoformat(),
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'PREPARE-POST-READOUT-RECHECK-BRIEF',
            'reason': 'The bounded post-readout action dispatch has reached its due/recheck date. Prepare a scratch-local recheck brief before any recheck record, new-context receipt, service-record edit, lifecycle move, public-summary update, custody, acceptance, or closure step.',
            'recommended_command': post_readout_recheck_brief_command(latest_post_packet.path, as_of),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-post-readout-recheck-brief'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'live_window_readout':
        readout_error = owner_live_window_readout_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if readout_error:
            return ctx(integrity_block(
                'LIVE-WINDOW-READOUT-INTEGRITY-BLOCKED',
                f'The latest local live-window readout cannot drive post-readout dispatch: {readout_error}. Rerun make owner-live-window-readout from a terminal live-window card instead of treating an edited readout as evidence, custody, acceptance, closure, service-record mutation, or public-claim support.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'PREPARE-POST-READOUT-ACTION-BRIEF',
            'reason': 'A bounded terminal live-window readout exists. Prepare a scratch-local post-readout action brief before any dispatch record, owner-held action, service-record edit, lifecycle move, public-summary update, custody, acceptance, or closure step.',
            'recommended_command': post_readout_action_brief_command(latest_post_packet.path, as_of),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-post-readout-action-brief'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'live_window_readout_brief':
        brief_error = owner_live_window_readout_brief_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if brief_error:
            return ctx(integrity_block(
                'LIVE-WINDOW-READOUT-BRIEF-INTEGRITY-BLOCKED',
                f'The latest local live-window readout brief cannot drive aggregate readout recording: {brief_error}. Rerun make owner-live-window-readout-brief from a valid terminal live-window card instead of editing brief records or treating them as readouts, post-readout dispatches, evidence, service-record changes, public language, lifecycle state, custody, acceptance, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'RECORD-LIVE-WINDOW-READOUT-FROM-BRIEF-NOT-CLOSURE',
            'reason': 'A scratch-local live-window readout brief exists for a terminal card. A human must choose and record exactly one aggregate readout before any post-readout action, service-record edit, lifecycle move, public-summary update, custody, acceptance, or closure step.',
            'recommended_command': live_window_readout_from_brief_command(latest_post_packet.data),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-live-window-readout-after-human-window-readout'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'live_window_terminal_brief':
        brief_error = owner_live_window_terminal_brief_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if brief_error:
            return ctx(integrity_block(
                'LIVE-WINDOW-TERMINAL-BRIEF-INTEGRITY-BLOCKED',
                f'The latest local live-window terminal-state brief cannot drive terminal card recording: {brief_error}. Rerun make owner-live-window-terminal-brief from a valid staged/active live-window card instead of editing brief records or treating them as terminal cards, readouts, evidence, service-record changes, public language, lifecycle state, custody, acceptance, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'RECORD-LIVE-WINDOW-TERMINAL-CARD-NOT-READOUT',
            'reason': 'A scratch-local live-window terminal-state brief exists for a staged/active card. A human must choose and record exactly one terminal card state before any readout, post-readout action, service-record edit, lifecycle move, public-summary update, custody, acceptance, or closure step.',
            'recommended_command': terminal_card_from_brief_command(latest_post_packet.data),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-live-window-card-terminal-state-after-human-window-outcome'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'live_window_card':
        card_error = owner_live_window_card_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if card_error:
            return ctx(integrity_block(
                'LIVE-WINDOW-CARD-INTEGRITY-BLOCKED',
                f'The latest local live-window card cannot drive a readout gate: {card_error}. Rerun make owner-live-window-card from a valid post-decision change ticket instead of treating an edited card as evidence, custody, acceptance, closure, service-record mutation, or public-claim support.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        state = latest_post_packet.data.get('window_state')
        if state in {'paused', 'rolled_back', 'completed_no_closure', 'quarantined'}:
            return ctx({
                'ok': True,
                'outcome': 'PREPARE-LIVE-WINDOW-READOUT-BRIEF',
                'reason': 'A bounded live-window card reached a terminal/readout-ready state; prepare a scratch-local readout brief so the human can record one aggregate readout before any post-readout action, service-record edit, lifecycle move, public-summary change, custody, acceptance, or closure step.',
                'recommended_command': live_window_readout_brief_command(latest_post_packet.path),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-live-window-readout-brief'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        if state in {'staged', 'active'}:
            return ctx({
                'ok': True,
                'outcome': 'PREPARE-LIVE-WINDOW-TERMINAL-STATE-BRIEF',
                'reason': f'A bounded live-window card exists in nonterminal state {state}; prepare a scratch-local terminal-state brief so the human can later record exactly one paused, rolled_back, completed_no_closure, or quarantined card before any readout, service-record edit, lifecycle state, public-summary update, custody, acceptance, or closure step.',
                'recommended_command': live_window_terminal_brief_command(latest_post_packet.path),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-live-window-terminal-brief'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'LIVE-WINDOW-CARD-RECORDED-NOT-READY-FOR-READOUT',
            'reason': f'A bounded live-window card exists in state {state}; do not edit service records, lifecycle state, public summaries, custody, acceptance, or closure until the card reaches paused, rolled_back, completed_no_closure, or quarantined and is read through the end-of-window gate.',
            'recommended_command': 'no field command; preserve the bounded card and rerun owner-field-next only after a valid terminal card exists',
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['wait-for-terminal-live-window-card'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'activation_live_window_brief':
        brief_error = owner_activation_live_window_brief_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if brief_error:
            return ctx(integrity_block(
                'ACTIVATION-LIVE-WINDOW-BRIEF-INTEGRITY-BLOCKED',
                f'The latest local activation/live-window entry brief cannot drive late field work: {brief_error}. Rerun make owner-activation-live-window-brief from a valid ready_for_real_packet or active_change post-decision ticket instead of editing brief records or treating them as acceptance, a live-window card, service-record movement, public support, custody, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        source_ticket = latest_post_packet.data.get('source_post_decision_change_ticket', {}) if isinstance(latest_post_packet.data.get('source_post_decision_change_ticket'), dict) else {}
        ticket_state = source_ticket.get('ticket_state')
        if ticket_state == 'ready_for_real_packet':
            return ctx({
                'ok': True,
                'outcome': 'RECORD-ACTIVATION-RECEIPT-FROM-REAL-PACKET-NOT-ACCEPTANCE',
                'reason': 'A scratch-local activation/live-window entry brief exists for a ready_for_real_packet ticket. Only if the same real owner-reviewed SRC2+ source packet is available, record an activation receipt from the brief command. The brief and receipt are not evidence, custody, public-summary support, lifecycle movement, service-record mutation, live-window authority, or closure.',
                'recommended_command': activation_from_brief_command(latest_post_packet.data),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-activation-receipt-if-same-real-src2plus-source-packet-exists'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        if ticket_state == 'active_change':
            return ctx({
                'ok': True,
                'outcome': 'RECORD-LIVE-WINDOW-CARD-FROM-ACTIVE-CHANGE-BRIEF',
                'reason': 'A scratch-local activation/live-window entry brief exists for an active_change ticket. A human must choose and record a bounded live-window stop/rollback card before any service-record edit, lifecycle movement, public-summary update, custody, acceptance, readout, or closure.',
                'recommended_command': live_window_from_brief_command(latest_post_packet.data),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-live-window-card-after-human-window-choice'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        return ctx(integrity_block(
            'ACTIVATION-LIVE-WINDOW-BRIEF-STATE-BLOCKED',
            f'The latest activation/live-window brief points to ticket_state={ticket_state!r}; regenerate it only from ready_for_real_packet or active_change tickets.',
            relative(latest_post_packet.path),
        ), selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'activation_receipt':
        receipt_error = activation_receipt_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if receipt_error:
            return ctx(integrity_block(
                'ACTIVATION-RECEIPT-INTEGRITY-BLOCKED',
                f'The latest local activation receipt cannot unlock active_change ticketing: {receipt_error}. Rerun make owner-activation-receipt from the wait gate and a real owner-reviewed source packet instead of editing scratch receipts or treating a local decision as acceptance.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        source_decision_ref = latest_post_packet.data.get('source_first_packet_decision', {}).get('reference')
        decision_path = ROOT / source_decision_ref if isinstance(source_decision_ref, str) else None
        if decision_path is None or not decision_path.exists():
            return ctx(integrity_block(
                'ACTIVATION-RECEIPT-SOURCE-DECISION-MISSING',
                'The latest activation receipt no longer points to an existing source first-packet decision; regenerate the receipt from the bounded gate before active_change ticketing.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'RECORD-ACTIVE-CHANGE-TICKET-FROM-ACTIVATION-RECEIPT',
            'reason': 'A scratch-local activation receipt exists for a real owner-reviewed SRC2+ packet. Record an active_change ticket from that receipt before any live-window card, service-record edit, lifecycle move, public-summary update, custody, or closure step.',
            'recommended_command': post_decision_change_ticket_command(decision_path, latest_post_packet.path, str(latest_post_packet.data.get('source_truth_class') or 'SRC2')),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-post-decision-change-ticket:active-change-from-activation-receipt'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'post_decision_change_ticket':
        ticket_error = owner_post_decision_change_ticket_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if ticket_error:
            return ctx(integrity_block(
                'POST-DECISION-CHANGE-TICKET-INTEGRITY-BLOCKED',
                f'The latest local post-decision change ticket cannot drive a live-window card: {ticket_error}. Rerun make owner-post-decision-change-ticket from a valid first-packet decision instead of treating an edited ticket as evidence, custody, acceptance, closure, or public-claim support.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        ticket_state = latest_post_packet.data.get('ticket_state')
        if ticket_state == 'active_change':
            return ctx({
                'ok': True,
                'outcome': 'PREPARE-ACTIVATION-LIVE-WINDOW-BRIEF',
                'reason': 'A minimized post-decision change ticket is active_change and remains NOT_ACCEPTED; prepare the activation/live-window entry brief before any live-window card, service-record edit, lifecycle movement, custody, public-summary, readout, or closure step.',
                'recommended_command': activation_live_window_brief_command(latest_post_packet.path),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-activation-live-window-brief'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        if ticket_state == 'ready_for_real_packet':
            return ctx({
                'ok': True,
                'outcome': 'PREPARE-ACTIVATION-LIVE-WINDOW-BRIEF',
                'reason': 'A post-decision ticket is ready_for_real_packet, but no activation receipt or active_change ticket exists. Prepare the scratch-local activation/live-window entry brief so the same real owner-reviewed source packet can be checked through owner-activation-receipt without laundering pre-acceptance readiness into a live-window card or SRC2+ public claim.',
                'recommended_command': activation_live_window_brief_command(latest_post_packet.path),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-activation-live-window-brief'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'POST-DECISION-TICKET-RECORDED-NO-LIVE-WINDOW',
            'reason': f'A post-decision change ticket exists in state {ticket_state}; do not emit a live-window card, service-record edit, lifecycle move, custody step, public-summary update, or closure step from this non-active ticket.',
            'recommended_command': 'no field command; preserve the bounded post-decision ticket and keep FT-0181 live',
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['blocked-trimmed-quarantined-ticket-record', 'wait-for-new-real-owner-context'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'first_packet_decision_brief':
        brief_error = owner_first_packet_decision_brief_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if brief_error:
            return ctx(integrity_block(
                'FIRST-PACKET-DECISION-BRIEF-INTEGRITY-BLOCKED',
                f'The latest local first-packet decision brief cannot drive board work: {brief_error}. Rerun make owner-first-packet-decision-brief from a valid proceed-capable workbench review instead of treating an edited brief as a board decision, evidence, custody, acceptance, closure, service-record mutation, or public-claim support.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        review_ref = latest_post_packet.data.get('source_workbench_review', {}).get('reference')
        review_path = ROOT / review_ref if isinstance(review_ref, str) and review_ref else Path('scratch/MISSING/workbench-review.json')
        return ctx({
            'ok': True,
            'outcome': 'RECORD-FIRST-PACKET-DECISION-NOT-ACCEPTED',
            'reason': 'A scratch-local first-packet decision brief is prepared, but it is not a board decision; a human must choose exactly one bounded five-slice route and record owner-first-packet-decision before any change ticket, custody, acceptance, public-summary, live-window, lifecycle, or closure step.',
            'recommended_command': first_packet_decision_command(review_path),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-first-packet-decision-after-human-board-choice'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)


    if latest_post_packet is not None and latest_post_packet.kind == 'post_decision_change_ticket_brief':
        brief_error = owner_post_decision_change_ticket_brief_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if brief_error:
            return ctx(integrity_block(
                'POST-DECISION-CHANGE-TICKET-BRIEF-INTEGRITY-BLOCKED',
                f'The latest local activation/live-window entry brief cannot drive ticket work: {brief_error}. Rerun make owner-post-decision-change-ticket-brief from a valid first-packet decision instead of treating an edited brief as a ticket, activation receipt, evidence, custody, acceptance, live-window card, service-record mutation, public-claim support, or closure.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        decision_ref = latest_post_packet.data.get('source_first_packet_decision', {}).get('reference')
        decision_path = ROOT / decision_ref if isinstance(decision_ref, str) and decision_ref else Path('scratch/MISSING/first-packet-decision.json')
        return ctx({
            'ok': True,
            'outcome': 'RECORD-POST-DECISION-CHANGE-TICKET-NOT-ACCEPTED',
            'reason': 'A scratch-local activation/live-window entry brief is prepared, but it is not a change ticket; a human must choose one bounded ticket route before any activation receipt, live-window card, service-record edit, lifecycle move, custody, acceptance, public-summary update, or closure step.',
            'recommended_command': post_decision_change_ticket_command(decision_path),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-post-decision-change-ticket-after-human-ticket-choice'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'first_packet_decision':
        decision_error = owner_first_packet_decision_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if decision_error:
            return ctx(integrity_block(
                'FIRST-PACKET-DECISION-INTEGRITY-BLOCKED',
                f'The latest local first-packet decision cannot drive a change ticket: {decision_error}. Rerun make owner-first-packet-decision from a valid proceed-capable workbench review instead of treating an edited board record as evidence, custody, acceptance, closure, or public-claim support.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'PREPARE-POST-DECISION-CHANGE-TICKET-BRIEF',
            'reason': 'A minimized five-slice first-packet decision record exists and remains NOT_ACCEPTED; prepare a activation/live-window entry brief before any ticket command, activation receipt, live-window card, service-record edit, public summary, lifecycle state, custody, acceptance, or closure step.',
            'recommended_command': post_decision_change_ticket_brief_command(latest_post_packet.path),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-post-decision-change-ticket-brief'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'workbench_review_brief':
        brief_error = owner_workbench_review_brief_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if brief_error:
            return ctx(integrity_block(
                'WORKBENCH-REVIEW-BRIEF-INTEGRITY-BLOCKED',
                f'The latest local workbench review brief cannot drive a next field step: {brief_error}. Rerun make owner-workbench-review-brief from a valid NOT_ACCEPTED workbench seed instead of treating an edited brief as review, evidence, custody, closure, or public-claim support.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        seed_ref = latest_post_packet.data.get('source_seed', {}).get('reference')
        seed_path = ROOT / seed_ref if isinstance(seed_ref, str) and seed_ref else Path('scratch/MISSING/workbench-seed.json')
        return ctx({
            'ok': True,
            'outcome': 'RECORD-WORKBENCH-REVIEW-NOT-ACCEPTED',
            'reason': 'A scratch-local workbench review brief is prepared, but it is not a human review; a human must choose exactly one bounded route and record owner-workbench-review before any decision-board, custody, acceptance, public-summary, live-window, or closure step.',
            'recommended_command': workbench_review_command(seed_path),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-workbench-review-after-human-review'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'workbench_review':
        review_error = owner_workbench_review_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if review_error:
            return ctx(integrity_block(
                'WORKBENCH-REVIEW-INTEGRITY-BLOCKED',
                f'The latest local workbench review cannot drive a next field step: {review_error}. Rerun make owner-workbench-review from a valid NOT_ACCEPTED workbench seed instead of treating an edited review as evidence, custody, closure, or public-claim support.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        decision = latest_post_packet.data.get('decision')
        if decision == 'PROCEED-DECISION-BOARD':
            return ctx({
                'ok': True,
                'outcome': 'PREPARE-FIRST-PACKET-DECISION-BRIEF',
                'reason': 'A local workbench review record exists and is proceed-capable, but it remains NOT_ACCEPTED; prepare a minimized first-packet decision brief before any five-slice board command, change ticket, custody, acceptance, public-summary, live-window, lifecycle, or closure step.',
                'recommended_command': first_packet_decision_brief_command(latest_post_packet.path),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-first-packet-decision-brief'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        if decision == 'REASK-OWNER':
            return ctx({
                'ok': True,
                'outcome': 'RECORD-REASK-LOG-FROM-WORKBENCH-REVIEW',
                'reason': 'The workbench review found one or more fields that need clarification; after the human sends/adapts that bounded re-ask, record a reask-log before creating the dated clarification clock.',
                'recommended_command': reask_log_command(as_of, latest_post_packet.path),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-reask-log-after-human-reask-send'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'WORKBENCH-REVIEW-BLOCK-OR-TRIM-RECORDED',
            'reason': f'The latest workbench review decision is {decision}; keep FT-0181 live and use the local review summary rather than widening the ask or upgrading claims.',
            'recommended_command': 'no field command; preserve the workbench review record and keep FT-0181 live without evidence, custody, closure, or public-claim upgrade',
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['local-review-summary', 'wait-for-new-real-owner-context'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'workbench_seed':
        seed_error = owner_workbench_seed_integrity_error(latest_post_packet.data, archive_root=ROOT)
        if seed_error:
            return ctx(integrity_block(
                'WORKBENCH-SEED-INTEGRITY-BLOCKED',
                f'The latest local workbench seed cannot drive a review brief: {seed_error}. Rerun make owner-reply-workbench-seed from a source-clock-gated PROCEED-STAGED intake bundle instead of treating an older or edited seed as acceptance, custody, closure, or public-claim support.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'PREPARE-WORKBENCH-REVIEW-BRIEF',
            'reason': 'The latest local post-packet artifact is a NOT_ACCEPTED workbench seed; prepare a scratch-local review brief that gives the human reviewer one bounded command set before any review record, decision-board, custody, acceptance, public-summary, live-window, or closure step.',
            'recommended_command': workbench_review_brief_command(latest_post_packet.path),
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['owner-workbench-review-brief'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'intake_bundle':
        triage = latest_post_packet.data.get('triage_outcome')
        if triage not in KNOWN_TRIAGE_OUTCOMES or latest_post_packet.data.get('ft0181_status') != 'live':
            return ctx(integrity_block(
                'INTAKE-BUNDLE-INTEGRITY-BLOCKED',
                f'The latest local intake bundle has triage_outcome={triage!r} and ft0181_status={latest_post_packet.data.get("ft0181_status")!r}; rerun bounded intake from a plausible returned owner CSV instead of routing a malformed scratch bundle.',
                relative(latest_post_packet.path),
            ), selected=latest_post_packet)
        if triage == 'PROCEED-STAGED':
            return ctx({
                'ok': True,
                'outcome': 'SEED-WORKBENCH',
                'reason': 'The latest local post-packet artifact is a PROCEED-STAGED intake bundle; create a NOT_ACCEPTED workbench seed before opening the manual workbench.',
                'recommended_command': workbench_seed_command(latest_post_packet.path.parent),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-reply-workbench-seed'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        if triage == 'RE-ASK-ONCE':
            return ctx({
                'ok': True,
                'outcome': 'RECORD-REASK-LOG-FROM-INTAKE',
                'reason': 'The latest local post-packet artifact requests exactly one clarification; after the human sends/adapts that bounded re-ask, record a reask-log before creating the dated clarification clock.',
                'recommended_command': reask_log_command(as_of, latest_post_packet.path),
                'source_artifact': relative(latest_post_packet.path),
                'allowed_only': ['owner-reask-log-after-human-reask-send'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_post_packet)
        return ctx({
            'ok': True,
            'outcome': 'FOLLOW-INTAKE-ROUTE-NO-WIDENING',
            'reason': f'The latest local post-packet artifact is an intake bundle with triage {triage}; use its routed local note/template instead of creating new doctrine or widening the ask.',
            'recommended_command': 'open the latest local owner-reply intake outcome note under scratch; do not widen the ask, bypass the router, or create a new control surface',
            'source_artifact': relative(latest_post_packet.path),
            'allowed_only': ['routed-intake-note'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_post_packet)

    if latest_post_packet is not None and latest_post_packet.kind == 'contact_status':
        latest_contact = latest_post_packet
        status = latest_contact.data.get('contact_status')
        due_text = latest_contact.data.get('response_due_date') or ''
        sent_text = latest_contact.data.get('sent_date') or ''
        status_date_text = latest_contact.data.get('status_date') or ''
        try:
            attempt_count = int(latest_contact.data.get('attempt_count') or 1)
        except (TypeError, ValueError):
            attempt_count = 0
        try:
            due = parse_iso(due_text, 'response_due_date')
            parse_iso(sent_text, 'sent_date')
            parse_iso(status_date_text, 'status_date')
        except ValueError as exc:
            return ctx(integrity_block(
                'CONTACT-STATUS-INTEGRITY-BLOCKED',
                f'The latest local owner-contact status has invalid date/clock fields: {exc}. Rerun make owner-contact-status from the router-emitted command instead of routing a malformed scratch status.',
                relative(latest_contact.path),
            ), selected=latest_contact)
        if status not in KNOWN_CONTACT_STATUSES or attempt_count not in {1, 2}:
            return ctx(integrity_block(
                'CONTACT-STATUS-INTEGRITY-BLOCKED',
                f'The latest local owner-contact status has contact_status={status!r} and attempt_count={attempt_count!r}; rerun make owner-contact-status from the router-emitted command instead of routing a malformed scratch status.',
                relative(latest_contact.path),
            ), selected=latest_contact)
        if status == 'NO_OWNER_PACKET':
            return ctx({
                'ok': True,
                'outcome': 'NO-OWNER-PACKET-RECORDED',
                'reason': 'A bounded no-owner-packet outcome is already recorded; keep FT-0181 live and do not compensate with synthetic evidence, a broader ask, or a new doctrine surface.',
                'recommended_command': 'no field command; keep FT-0181 live as blocked by missing owner packet',
                'source_artifact': relative(latest_contact.path),
                'allowed_only': ['wait-for-new-real-owner-context'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_contact)
        if due < as_of and attempt_count >= 2:
            return ctx({
                'ok': True,
                'outcome': 'RECORD-NO-OWNER-PACKET',
                'reason': 'The bounded clarification clock has passed; record NO_OWNER_PACKET instead of widening the ask or creating new control surfaces.',
                'recommended_command': no_owner_packet_command(sent_text, due_text, as_of, latest_contact.path),
                'source_artifact': relative(latest_contact.path),
                'allowed_only': ['owner-contact-status:no-owner-packet'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_contact)
        if due < as_of:
            return ctx({
                'ok': True,
                'outcome': 'RECORD-REASK-LOG-AFTER-FIRST-CLOCK',
                'reason': 'The first response clock has passed with no returned CSV; after the human sends/adapts one bounded follow-up, record a reask-log before creating the clarification clock.',
                'recommended_command': reask_log_command(as_of, latest_contact.path),
                'source_artifact': relative(latest_contact.path),
                'allowed_only': ['owner-reask-log-after-human-reask-send'],
                'claim_ceiling': CLAIM_CEILING,
                'ft0181_status': 'live',
            }, selected=latest_contact)
        return ctx({
            'ok': True,
            'outcome': 'AWAIT-OWNER-REPLY',
            'reason': 'A bounded owner-contact clock is open and not past due; wait for a returned CSV or the due date.',
            'recommended_command': 'make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply',
            'source_artifact': relative(latest_contact.path),
            'allowed_only': ['owner-reply-intake-if-csv-arrives', 'owner-contact-status-after-clock'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_contact)

    latest_packet = latest(packets)
    if latest_packet is not None:
        packet_error = owner_request_packet_integrity_error(latest_packet.data)
        if packet_error:
            return ctx(integrity_block(
                'OWNER-REQUEST-PACKET-INTEGRITY-BLOCKED',
                f'The latest local owner-request packet manifest cannot drive a sent clock: {packet_error}. Regenerate the packet with make owner-request-packet instead of editing scratch manifests or treating local packet prep as evidence.',
                relative(latest_packet.path),
            ), selected=latest_packet)
        return ctx({
            'ok': True,
            'outcome': 'RECORD-SEND-LOG-AFTER-HUMAN-SEND',
            'reason': 'A prepared packet exists but no send-log, route-block, or contact-clock status exists. If a real accountable owner route exists and a human sends/adapts the packet, record the minimal local send-log and SENT_AWAITING_REPLY clock through the guarded after-human-send helper; if no accountable owner route exists, use the fallback route-block command instead of faking a send log or adding doctrine.',
            'recommended_command': send_log_command(latest_packet.path, str(latest_packet.data.get('requested_return_date') or ''), as_of),
            'fallback_command_if_no_accountable_owner_route': route_block_command(latest_packet.path, as_of),
            'source_artifact': relative(latest_packet.path),
            'allowed_only': ['owner-after-human-send-after-real-send', 'owner-route-block-if-no-accountable-route'],
            'claim_ceiling': CLAIM_CEILING,
            'ft0181_status': 'live',
        }, selected=latest_packet)

    return ctx({
        'ok': True,
        'outcome': 'PREPARE-FIRST-CONTACT-PACKET',
        'reason': 'No local packet/contact/intake state was found; prepare the AIEDU-SR-003 bounded first-contact packet.',
        'recommended_command': packet_command(),
        'source_artifact': None,
        'allowed_only': ['owner-request-packet'],
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
    })


def compact_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def docket_text(decision: dict[str, Any], as_of_date: str) -> str:
    command = decision.get('recommended_command') or 'none'
    fallback = decision.get('fallback_command_if_no_accountable_owner_route')
    counts = decision.get('observed_artifact_counts', {})
    candidates = decision.get('latest_artifact_candidates', {})
    selected = decision.get('selected_artifact')
    allowed_only = ', '.join(decision.get('allowed_only', [])) or 'none'
    lines = [
        '# FT-0181 field next-action docket',
        '',
        f'Decision date: `{as_of_date}`',
        f'Outcome: `{decision.get("outcome")}`',
        f'FT-0181 state: `{decision.get("ft0181_status", "live")}`',
        'Evidence effect: `not_evidence`',
        f'Claim ceiling: `{CLAIM_CEILING}`',
        '',
        '## Recommended next command',
        '',
        '```bash',
        str(command),
        '```',
    ]
    if fallback:
        lines.extend([
            '',
            '## Fallback only if no accountable owner route exists',
            '',
            '```bash',
            str(fallback),
            '```',
            '',
            'Use the fallback only when the packet cannot be sent because no real accountable',
            'owner route exists. Do not use it after a human send/adaptation.',
        ])
    lines.extend([
        '',
        '## Reason',
        '',
        str(decision.get('reason', decision.get('error', 'No reason provided.'))),
        '',
        '## Observed local state',
        '',
        f'Selection rule: `{decision.get("scratch_selection_rule", "n/a")}`',
        f'Scratch firebreak: `{decision.get("scratch_firebreak_rule", "n/a")}`',
        f'Allowed only: `{allowed_only}`',
        '',
        'Artifact counts:',
        '',
        '```json',
        compact_json(counts),
        '```',
        '',
        'Latest artifact candidates:',
        '',
        '```json',
        compact_json(candidates),
        '```',
        '',
        'Selected artifact:',
        '',
        '```json',
        compact_json(selected),
        '```',
        '',
        '## Anti-drift rule',
        '',
        'Do not convert owner silence, a prepared packet, a local route block, a local',
        'status note, an intake bundle, or a workbench seed into evidence, closure, or',
        'public claims. Do not add new doctrine, a fake send log, a wider data request, a',
        'full export, raw learner records, protected-route details, screenshots, vendor',
        'dashboards, or another registry to compensate for a missing owner packet or',
        'missing accountable owner route.',
    ])
    return '\n'.join(lines) + '\n'


def write_docket(output_dir: Path, decision: dict[str, Any], as_of_date: str, overwrite: bool = False) -> dict[str, Any]:
    allowed, boundary = output_allowed(output_dir, archive_root=ROOT)
    if not allowed:
        return {
            'ok': False,
            'outcome': 'FIELD-NEXT-ACTION-OUTPUT-BLOCKED',
            'error': boundary,
            'claim_ceiling': CLAIM_CEILING,
        }
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        return {
            'ok': False,
            'outcome': 'FIELD-NEXT-ACTION-OUTPUT-EXISTS',
            'error': 'use --overwrite or choose an empty directory',
            'claim_ceiling': CLAIM_CEILING,
        }
    output_dir.mkdir(parents=True, exist_ok=True)
    enriched = dict(decision)
    enriched.update({
        'decision_type': 'FT-0181-field-next-action',
        'decision_version': REVISION,
        'as_of_date': as_of_date,
        'evidence_effect': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'output_boundary': boundary,
    })
    (output_dir / 'field-next-action.json').write_text(json.dumps(enriched, indent=2) + '\n', encoding='utf-8')
    (output_dir / 'FIELD-NEXT-ACTION.md').write_text(docket_text(enriched, as_of_date), encoding='utf-8')
    return enriched




def default_safe_packet_output_dir(scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    return scratch / 'owner-request-packets' / 'aiedu-sr-003-first-contact'



def default_safe_review_brief_output_dir(seed_path: Path, scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    digest = sha256_file(seed_path)[:12] if seed_path.exists() and seed_path.is_file() else 'missingseed'
    stem = seed_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'workbench-seed'
    return scratch / 'owner-workbench-review-briefs' / f'{stem}-{digest}'


def default_safe_decision_brief_output_dir(review_path: Path, scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    digest = sha256_file(review_path)[:12] if review_path.exists() and review_path.is_file() else 'missingreview'
    stem = review_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'workbench-review'
    return scratch / 'owner-first-packet-decision-briefs' / f'{stem}-{digest}'


def default_safe_change_ticket_brief_output_dir(decision_path: Path, scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    digest = sha256_file(decision_path)[:12] if decision_path.exists() and decision_path.is_file() else 'missingdecision'
    stem = decision_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'first-packet-decision'
    return scratch / 'owner-post-decision-change-ticket-briefs' / f'{stem}-{digest}'


def default_safe_activation_live_window_brief_output_dir(ticket_path: Path, scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    digest = sha256_file(ticket_path)[:12] if ticket_path.exists() and ticket_path.is_file() else 'missingticket'
    stem = ticket_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'post-decision-ticket'
    return scratch / 'owner-activation-live-window-briefs' / f'{stem}-{digest}'

def default_safe_live_window_readout_brief_output_dir(card_path: Path, scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    digest = sha256_file(card_path)[:12] if card_path.exists() and card_path.is_file() else 'missingcard'
    stem = card_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'terminal-live-window-card'
    return scratch / 'owner-live-window-readout-briefs' / f'{stem}-{digest}'


def default_safe_post_readout_action_brief_output_dir(readout_path: Path, scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    digest = sha256_file(readout_path)[:12] if readout_path.exists() and readout_path.is_file() else 'missingreadout'
    stem = readout_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'terminal-readout'
    return scratch / 'owner-post-readout-action-briefs' / f'{stem}-{digest}'


def default_safe_post_readout_recheck_brief_output_dir(action_path: Path, as_of_date: str, scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    digest = sha256_file(action_path)[:12] if action_path.exists() and action_path.is_file() else 'missingaction'
    stem = action_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'post-readout-action'
    return scratch / 'owner-post-readout-recheck-briefs' / f'{stem}-{as_of_date}-{digest}'


def default_safe_live_window_terminal_brief_output_dir(card_path: Path, scratch_root: Path) -> Path:
    scratch = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    digest = sha256_file(card_path)[:12] if card_path.exists() and card_path.is_file() else 'missingcard'
    stem = card_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'live-window-card'
    return scratch / 'owner-live-window-terminal-briefs' / f'{stem}-{digest}'

def scratch_root_for_packet_output(packet_dir: Path, fallback: Path) -> Path:
    absolute = packet_dir if packet_dir.is_absolute() else ROOT / packet_dir
    try:
        rel_parts = absolute.resolve().relative_to(ROOT.resolve()).parts
    except ValueError:
        rel_parts = absolute.resolve().parts
        base = Path(absolute.anchor)
    else:
        base = ROOT
    if 'owner-request-packets' not in rel_parts:
        return fallback
    idx = rel_parts.index('owner-request-packets')
    if idx == 0:
        return fallback
    return base.joinpath(*rel_parts[:idx])


def safe_local_session_text(session: dict[str, Any]) -> str:
    local = session.get('safe_local_execution', {}) if isinstance(session.get('safe_local_execution'), dict) else {}
    initial = session.get('initial_decision', {}) if isinstance(session.get('initial_decision'), dict) else {}
    after = session.get('after_local_decision', {}) if isinstance(session.get('after_local_decision'), dict) else {}
    lines = [
        '# FT-0181 safe local field-work session',
        '',
        f"Session state: `{local.get('state', 'not-run')}`",
        'Evidence effect: `not_evidence`',
        'Closure effect: `does_not_close_ft0181`',
        'Public claim effect: `none`',
        '',
        'This session may only collapse local operator friction. It may prepare a first-contact',
        'packet, a workbench review brief, a first-packet decision brief, a post-decision change-ticket brief, an activation/live-window entry brief, a live-window terminal/readout brief, a post-readout action brief, or a post-readout recheck brief, then rerun the router.',
        'It must not record human send/adaptation, contact status, route block, human review,',
        'board decision, change ticket, intake, custody, acceptance, public support, live-window movement, post-readout dispatch, post-readout recheck, owner action, or closure.',
        '',
        '## Initial router outcome',
        '',
        f"Outcome: `{initial.get('outcome')}`",
        '',
        '```bash',
        str(initial.get('recommended_command') or 'none'),
        '```',
    ]
    if local.get('packet_output_dir'):
        lines.extend([
            '',
            '## Local packet prep performed',
            '',
            f"Packet directory: `{local.get('packet_output_dir')}`",
            f"Packet state: `{local.get('packet_state', 'unknown')}`",
            f"Evidence state: `{local.get('evidence_state', 'unknown')}`",
        ])
    if local.get('review_brief_output_dir'):
        lines.extend([
            '',
            '## Local workbench review-brief prep performed',
            '',
            f"Review brief directory: `{local.get('review_brief_output_dir')}`",
            f"Review brief state: `{local.get('review_brief_state', 'unknown')}`",
        ])
    if local.get('decision_brief_output_dir'):
        lines.extend([
            '',
            '## Local first-packet decision-brief prep performed',
            '',
            f"Decision brief directory: `{local.get('decision_brief_output_dir')}`",
            f"Decision brief state: `{local.get('decision_brief_state', 'unknown')}`",
        ])
    if local.get('change_ticket_brief_output_dir'):
        lines.extend([
            '',
            '## Local post-decision change-ticket-brief prep performed',
            '',
            f"Change-ticket brief directory: `{local.get('change_ticket_brief_output_dir')}`",
            f"Change-ticket brief state: `{local.get('change_ticket_brief_state', 'unknown')}`",
        ])
    if local.get('activation_live_window_brief_output_dir'):
        lines.extend([
            '',
            '## Local activation/live-window entry-brief prep performed',
            '',
            f"Activation/live-window brief directory: `{local.get('activation_live_window_brief_output_dir')}`",
            f"Activation/live-window brief state: `{local.get('activation_live_window_brief_state', 'unknown')}`",
        ])
    if local.get('live_window_terminal_brief_output_dir'):
        lines.extend([
            '',
            '## Local live-window terminal-state brief prep performed',
            '',
            f"Terminal-state brief directory: `{local.get('live_window_terminal_brief_output_dir')}`",
            f"Terminal-state brief state: `{local.get('live_window_terminal_brief_state', 'unknown')}`",
        ])
    if local.get('live_window_readout_brief_output_dir'):
        lines.extend([
            '',
            '## Local live-window readout brief prep performed',
            '',
            f"Readout brief directory: `{local.get('live_window_readout_brief_output_dir')}`",
            f"Readout brief state: `{local.get('live_window_readout_brief_state', 'unknown')}`",
        ])
    if local.get('post_readout_action_brief_output_dir'):
        lines.extend([
            '',
            '## Local post-readout action brief prep performed',
            '',
            f"Post-readout action brief directory: `{local.get('post_readout_action_brief_output_dir')}`",
            f"Post-readout action brief state: `{local.get('post_readout_action_brief_state', 'unknown')}`",
        ])
    if local.get('post_readout_recheck_brief_output_dir'):
        lines.extend([
            '',
            '## Local post-readout recheck brief prep performed',
            '',
            f"Post-readout recheck brief directory: `{local.get('post_readout_recheck_brief_output_dir')}`",
            f"Post-readout recheck brief state: `{local.get('post_readout_recheck_brief_state', 'unknown')}`",
        ])
    if after:
        lines.extend([
            '',
            '## Post-prep router outcome',
            '',
            f"Outcome: `{after.get('outcome')}`",
            '',
            '```bash',
            str(after.get('recommended_command') or 'none'),
            '```',
        ])
        fallback = after.get('fallback_command_if_no_accountable_owner_route')
        if fallback:
            lines.extend([
                '',
                'Fallback only if no accountable owner route exists:',
                '',
                '```bash',
                str(fallback),
                '```',
            ])
    lines.extend([
        '',
        '## Human-action boundary',
        '',
        'After local prep, the only substantive next step is still human-owned: send/adapt',
        'the bounded request, record a route block, perform the minimized review, or choose',
        'one bounded decision-board route. Do not create another doctrine,',
        'registry, lint, or example surface to compensate for missing owner action.',
    ])
    return '\n'.join(lines) + '\n'


def safe_local_summary(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        'ok': decision.get('ok'),
        'outcome': decision.get('outcome'),
        'recommended_command': decision.get('recommended_command'),
        'fallback_command_if_no_accountable_owner_route': decision.get('fallback_command_if_no_accountable_owner_route'),
        'source_artifact': decision.get('source_artifact'),
        'allowed_only': decision.get('allowed_only'),
        'claim_ceiling': decision.get('claim_ceiling'),
        'ft0181_status': decision.get('ft0181_status'),
        'evidence_effect': decision.get('evidence_effect'),
        'closure_effect': decision.get('closure_effect'),
        'public_claim_effect': decision.get('public_claim_effect'),
    }


def write_safe_local_session(output_dir: Path, session: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'safe-local-field-session.json').write_text(json.dumps(session, indent=2) + '\n', encoding='utf-8')
    (output_dir / 'SAFE-LOCAL-FIELD-SESSION.md').write_text(safe_local_session_text(session), encoding='utf-8')


def run_safe_local_field_session(
    *,
    scratch_root: Path,
    returned_csv: Path | None,
    as_of_date: str,
    output_dir: Path,
    packet_output_dir: Path | None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Run the router and collapse only safe local bridge-prep steps.

    The function deliberately refuses to automate any step requiring human field
    judgment or actual owner action. It can prepare only these local bridges:
    first-contact packet prep, workbench review brief prep, first-packet
    decision brief prep, change-ticket/activation/live-window briefs, terminal/readout/action/recheck briefs. It then reruns the router so the next visible command is
    a human-owned action or another guarded local command.
    """
    initial = decide_and_write(
        scratch_root=scratch_root,
        returned_csv=returned_csv,
        as_of_date=as_of_date,
        output_dir=output_dir,
        overwrite=overwrite,
    )
    session: dict[str, Any] = {
        'session_type': 'FT-0181-safe-local-field-work',
        'session_version': REVISION,
        'as_of_date': as_of_date,
        'initial_decision': safe_local_summary(initial),
        'safe_local_execution': {
            'requested': True,
            'state': 'not-run',
            'allowed_scope': 'bridge-prep-only',
            'allowed_outcomes': [
                'PREPARE-FIRST-CONTACT-PACKET',
                'PREPARE-WORKBENCH-REVIEW-BRIEF',
                'PREPARE-FIRST-PACKET-DECISION-BRIEF',
                'PREPARE-POST-DECISION-CHANGE-TICKET-BRIEF',
                'PREPARE-ACTIVATION-LIVE-WINDOW-BRIEF',
                'PREPARE-LIVE-WINDOW-TERMINAL-STATE-BRIEF',
                'PREPARE-LIVE-WINDOW-READOUT-BRIEF',
                'PREPARE-POST-READOUT-ACTION-BRIEF',
                'PREPARE-POST-READOUT-RECHECK-BRIEF',
            ],
            'forbidden_scope': [
                'human-send-or-adaptation',
                'route-block-recording',
                'send-log-recording',
                'contact-status-recording',
                'returned-csv-intake-from-owner-field-work',
                'human-review-recording',
                'first-packet-decision-recording',
                'post-decision-change-ticket-recording',
                'post-readout-recheck-recording',
                'custody-or-acceptance',
                'public-claim-support',
                'live-window-or-closure',
            ],
            'no_evidence_or_closure_effect': True,
        },
    }
    if not initial.get('ok'):
        return initial
    if returned_csv is not None:
        session['safe_local_execution']['state'] = 'no-op-returned-csv-route-requires-owner-returned-reply-work'
        write_safe_local_session(output_dir, session)
        result = dict(initial)
        result['safe_local_execution'] = session['safe_local_execution']
        return result

    outcome = initial.get('outcome')
    if outcome == 'PREPARE-FIRST-CONTACT-PACKET':
        from prepare_ft0181_owner_request_packet import build_packet, default_return_date

        packet_dir = packet_output_dir or default_safe_packet_output_dir(scratch_root)
        packet = build_packet(
            output_dir=packet_dir,
            service_label='AIEDU-SR-003 draft reminder pilot',
            owner_role='accountable service owner',
            source_record_set='local service record set or source system, to be named by the owner',
            date_range='owner-named date range',
            return_date=default_return_date(),
            overwrite=overwrite,
        )
        if not packet.get('ok'):
            session['safe_local_execution'].update({
                'state': 'blocked-packet-prep',
                'packet_output_dir': str(packet_dir),
                'packet_error': packet.get('error'),
                'packet_reason': packet.get('reason'),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        post_output_dir = output_dir.parent / f'{output_dir.name}-after-local-packet-prep'
        post_scratch_root = scratch_root_for_packet_output(packet_dir, scratch_root)
        after = decide_and_write(
            scratch_root=post_scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=post_output_dir,
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-first-contact-packet',
            'packet_output_dir': relative(Path(packet['output_dir'])),
            'packet_state': packet.get('packet_state'),
            'evidence_state': packet.get('evidence_state'),
            'generated_files': packet.get('files'),
            'post_prep_output_dir': relative(post_output_dir),
            'post_prep_scratch_root': relative(post_scratch_root) if post_scratch_root.is_absolute() else post_scratch_root.as_posix(),
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result

    if outcome == 'PREPARE-WORKBENCH-REVIEW-BRIEF':
        from prepare_ft0181_workbench_review_brief import build_review_brief

        source = initial.get('source_artifact')
        seed_path = ROOT / source if isinstance(source, str) and source else Path('scratch/MISSING/workbench-seed.json')
        try:
            brief = build_review_brief(seed=seed_path, output_dir=default_safe_review_brief_output_dir(seed_path, scratch_root), overwrite=overwrite)
        except Exception as exc:
            session['safe_local_execution'].update({
                'state': 'blocked-workbench-review-brief-prep',
                'source_seed': relative(seed_path),
                'error': str(exc),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        after = decide_and_write(
            scratch_root=scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=output_dir.parent / f'{output_dir.name}-after-local-review-brief-prep',
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-workbench-review-brief',
            'review_brief_output_dir': brief.get('output_dir'),
            'review_brief_path': brief.get('brief_path'),
            'review_brief_state': 'REVIEW_BRIEF_PREPARED_NOT_REVIEWED',
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result

    if outcome == 'PREPARE-FIRST-PACKET-DECISION-BRIEF':
        from prepare_ft0181_first_packet_decision_brief import build_decision_brief

        source = initial.get('source_artifact')
        review_path = ROOT / source if isinstance(source, str) and source else Path('scratch/MISSING/workbench-review.json')
        try:
            brief = build_decision_brief(review=review_path, output_dir=default_safe_decision_brief_output_dir(review_path, scratch_root), overwrite=overwrite)
        except Exception as exc:
            session['safe_local_execution'].update({
                'state': 'blocked-first-packet-decision-brief-prep',
                'source_review': relative(review_path),
                'error': str(exc),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        after = decide_and_write(
            scratch_root=scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=output_dir.parent / f'{output_dir.name}-after-local-decision-brief-prep',
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-first-packet-decision-brief',
            'decision_brief_output_dir': brief.get('output_dir'),
            'decision_brief_path': brief.get('brief_path'),
            'decision_brief_state': 'DECISION_BRIEF_PREPARED_NOT_RECORDED',
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result


    if outcome == 'PREPARE-POST-DECISION-CHANGE-TICKET-BRIEF':
        from prepare_ft0181_post_decision_change_ticket_brief import build_change_ticket_brief

        source = initial.get('source_artifact')
        decision_path = ROOT / source if isinstance(source, str) and source else Path('scratch/MISSING/first-packet-decision.json')
        try:
            brief = build_change_ticket_brief(decision=decision_path, output_dir=default_safe_change_ticket_brief_output_dir(decision_path, scratch_root), overwrite=overwrite)
        except Exception as exc:
            session['safe_local_execution'].update({
                'state': 'blocked-post-decision-change-ticket-brief-prep',
                'source_decision': relative(decision_path),
                'error': str(exc),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        after = decide_and_write(
            scratch_root=scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=output_dir.parent / f'{output_dir.name}-after-local-change-ticket-brief-prep',
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-post-decision-change-ticket-brief',
            'change_ticket_brief_output_dir': brief.get('output_dir'),
            'change_ticket_brief_path': brief.get('brief_path'),
            'change_ticket_brief_state': 'CHANGE_TICKET_BRIEF_PREPARED_NOT_RECORDED',
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result


    if outcome == 'PREPARE-ACTIVATION-LIVE-WINDOW-BRIEF':
        from prepare_ft0181_activation_live_window_brief import build_activation_live_window_brief

        source = initial.get('source_artifact')
        ticket_path = ROOT / source if isinstance(source, str) and source else Path('scratch/MISSING/post-decision-change-ticket.json')
        try:
            brief = build_activation_live_window_brief(ticket=ticket_path, output_dir=default_safe_activation_live_window_brief_output_dir(ticket_path, scratch_root), overwrite=overwrite)
        except Exception as exc:
            session['safe_local_execution'].update({
                'state': 'blocked-activation-live-window-brief-prep',
                'source_ticket': relative(ticket_path),
                'error': str(exc),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        after = decide_and_write(
            scratch_root=scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=output_dir.parent / f'{output_dir.name}-after-local-activation-live-window-brief-prep',
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-activation-live-window-brief',
            'activation_live_window_brief_output_dir': brief.get('output_dir'),
            'activation_live_window_brief_path': brief.get('brief_path'),
            'activation_live_window_brief_state': 'ACTIVATION_OR_LIVE_WINDOW_BRIEF_PREPARED_NOT_ACTED',
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result

    if outcome == 'PREPARE-LIVE-WINDOW-TERMINAL-STATE-BRIEF':
        from prepare_ft0181_live_window_terminal_brief import build_terminal_brief

        source = initial.get('source_artifact')
        card_path = ROOT / source if isinstance(source, str) and source else Path('scratch/MISSING/live-window-card.json')
        try:
            brief = build_terminal_brief(card=card_path, output_dir=default_safe_live_window_terminal_brief_output_dir(card_path, scratch_root), overwrite=overwrite)
        except Exception as exc:
            session['safe_local_execution'].update({
                'state': 'blocked-live-window-terminal-brief-prep',
                'source_card': relative(card_path),
                'error': str(exc),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        after = decide_and_write(
            scratch_root=scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=output_dir.parent / f'{output_dir.name}-after-local-live-window-terminal-brief-prep',
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-live-window-terminal-brief',
            'live_window_terminal_brief_output_dir': brief.get('output_dir'),
            'live_window_terminal_brief_path': brief.get('brief_path'),
            'live_window_terminal_brief_state': 'TERMINAL_STATE_BRIEF_PREPARED_NOT_RECORDED',
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result

    if outcome == 'PREPARE-LIVE-WINDOW-READOUT-BRIEF':
        from prepare_ft0181_live_window_readout_brief import build_readout_brief

        source = initial.get('source_artifact')
        card_path = ROOT / source if isinstance(source, str) and source else Path('scratch/MISSING/live-window-card.json')
        try:
            brief = build_readout_brief(card=card_path, output_dir=default_safe_live_window_readout_brief_output_dir(card_path, scratch_root), overwrite=overwrite)
        except Exception as exc:
            session['safe_local_execution'].update({
                'state': 'blocked-live-window-readout-brief-prep',
                'source_card': relative(card_path),
                'error': str(exc),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        after = decide_and_write(
            scratch_root=scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=output_dir.parent / f'{output_dir.name}-after-local-live-window-readout-brief-prep',
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-live-window-readout-brief',
            'live_window_readout_brief_output_dir': brief.get('output_dir'),
            'live_window_readout_brief_path': brief.get('brief_path'),
            'live_window_readout_brief_state': 'READOUT_BRIEF_PREPARED_NOT_RECORDED',
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result

    if outcome == 'PREPARE-POST-READOUT-ACTION-BRIEF':
        from prepare_ft0181_post_readout_action_brief import build_post_readout_action_brief

        source = initial.get('source_artifact')
        readout_path = ROOT / source if isinstance(source, str) and source else Path('scratch/MISSING/live-window-readout.json')
        try:
            brief = build_post_readout_action_brief(readout=readout_path, as_of_date=as_of_date, output_dir=default_safe_post_readout_action_brief_output_dir(readout_path, scratch_root), overwrite=overwrite)
        except Exception as exc:
            session['safe_local_execution'].update({
                'state': 'blocked-post-readout-action-brief-prep',
                'source_readout': relative(readout_path),
                'error': str(exc),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        after = decide_and_write(
            scratch_root=scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=output_dir.parent / f'{output_dir.name}-after-local-post-readout-action-brief-prep',
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-post-readout-action-brief',
            'post_readout_action_brief_output_dir': brief.get('output_dir'),
            'post_readout_action_brief_path': brief.get('brief_path'),
            'post_readout_action_brief_state': 'POST_READOUT_ACTION_BRIEF_PREPARED_NOT_DISPATCHED',
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result

    if outcome == 'PREPARE-POST-READOUT-RECHECK-BRIEF':
        from prepare_ft0181_post_readout_recheck_brief import build_post_readout_recheck_brief

        source = initial.get('source_artifact')
        action_path = ROOT / source if isinstance(source, str) and source else Path('scratch/MISSING/post-readout-action.json')
        try:
            brief = build_post_readout_recheck_brief(action=action_path, as_of_date=as_of_date, output_dir=default_safe_post_readout_recheck_brief_output_dir(action_path, as_of_date, scratch_root), overwrite=overwrite)
        except Exception as exc:
            session['safe_local_execution'].update({
                'state': 'blocked-post-readout-recheck-brief-prep',
                'source_action': relative(action_path),
                'error': str(exc),
            })
            write_safe_local_session(output_dir, session)
            result = dict(initial)
            result['safe_local_execution'] = session['safe_local_execution']
            return result
        after = decide_and_write(
            scratch_root=scratch_root,
            returned_csv=None,
            as_of_date=as_of_date,
            output_dir=output_dir.parent / f'{output_dir.name}-after-local-post-readout-recheck-brief-prep',
            overwrite=overwrite,
        )
        session['safe_local_execution'].update({
            'state': 'prepared-post-readout-recheck-brief',
            'post_readout_recheck_brief_output_dir': brief.get('output_dir'),
            'post_readout_recheck_brief_path': brief.get('brief_path'),
            'post_readout_recheck_brief_state': 'POST_READOUT_RECHECK_BRIEF_PREPARED_NOT_RECHECKED',
        })
        session['after_local_decision'] = safe_local_summary(after)
        write_safe_local_session(output_dir, session)
        result = dict(after)
        result['safe_local_execution'] = session['safe_local_execution']
        result['initial_outcome_before_safe_local_execution'] = initial.get('outcome')
        result['safe_local_session_artifact'] = relative(output_dir / 'safe-local-field-session.json')
        return result

    session['safe_local_execution']['state'] = 'no-op-router-outcome-not-safe-local-bridge-prep'
    write_safe_local_session(output_dir, session)
    result = dict(initial)
    result['safe_local_execution'] = session['safe_local_execution']
    return result

def decide_and_write(*, scratch_root: Path, returned_csv: Path | None, as_of_date: str, output_dir: Path, overwrite: bool = False) -> dict[str, Any]:
    decision = decision_for(scratch_root=scratch_root, returned_csv=returned_csv, as_of_date=as_of_date)
    if not decision.get('ok'):
        return decision
    return write_docket(output_dir=output_dir, decision=decision, as_of_date=as_of_date, overwrite=overwrite)


def main() -> None:
    args = parse_args()
    if args.execute_safe_local:
        result = run_safe_local_field_session(
            scratch_root=args.scratch_root,
            returned_csv=args.returned_csv,
            as_of_date=args.as_of_date,
            output_dir=args.output_dir,
            packet_output_dir=args.packet_output_dir,
            overwrite=args.overwrite,
        )
    else:
        result = decide_and_write(
            scratch_root=args.scratch_root,
            returned_csv=args.returned_csv,
            as_of_date=args.as_of_date,
            output_dir=args.output_dir,
            overwrite=args.overwrite,
        )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get('ok'):
        print(f"decide_ft0181_field_next_action: OK ({result['outcome']})")
        print(f"recommended_command: {result['recommended_command']}")
    else:
        raise SystemExit(f"decide_ft0181_field_next_action: {result.get('outcome')} ({result.get('error')})")


if __name__ == '__main__':
    main()
