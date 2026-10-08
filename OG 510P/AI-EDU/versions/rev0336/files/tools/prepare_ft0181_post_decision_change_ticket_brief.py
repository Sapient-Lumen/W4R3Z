#!/usr/bin/env python3
"""Prepare a minimized post-decision change-ticket brief from a board record.

This helper is deliberately a bridge, not a change ticket. It validates the
scratch-local first-packet decision record, writes a one-screen ticket brief and
bounded command skeletons, and then stops. It copies no owner answers, raw CSV
rows, contact details, learner data, protected facts, security payloads, or
public claim text. A human still must choose and record one bounded
post-decision change ticket before any activation receipt, live-window card,
service-record mutation, custody, public summary, lifecycle movement, or closure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import (
    archive_relative,
    field_scratch_lane_error,
    output_allowed,
    owner_first_packet_decision_integrity_error,
    owner_post_decision_change_ticket_brief_integrity_error,
)
from record_ft0181_post_decision_change_ticket import OPERATOR_CONFIRMATION

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-post-decision-change-ticket-briefs'
CLAIM_CEILING = (
    'Post-decision change-ticket brief only; not a change-ticket record, not evidence, '
    'not SRC2+ acceptance, not custody evidence, not closure evidence, not public-summary '
    'support, and not proof of learning, safety, access, workload, compliance, scale, or effectiveness.'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a bounded FT-0181 post-decision change-ticket brief from a first-packet decision.')
    parser.add_argument('--decision', required=True, type=Path, help='scratch/.../first-packet-decision.json produced by owner-first-packet-decision.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the change-ticket brief.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing change-ticket brief directory.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable result.')
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def default_output_dir(decision_path: Path) -> Path:
    digest = sha256_file(decision_path)[:12] if decision_path.exists() and decision_path.is_file() else 'missingdecision'
    stem = decision_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'first-packet-decision'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{digest}'


def shell_quote(value: str) -> str:
    if value.replace('/', '').replace('-', '').replace('_', '').replace('.', '').isalnum():
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def command_templates(decision_ref: str) -> dict[str, str]:
    decision = shell_quote(decision_ref)
    base = f'make owner-post-decision-change-ticket DECISION={decision} '
    confirm = f'CONFIRM={OPERATOR_CONFIRMATION}'
    return {
        'ready_for_real_packet_sandbox': (
            base + 'TICKET_STATE=ready-for-real-packet CHANGE_CLASS=pct-c-sandbox-adjustment '
            'SOURCE_TRUTH_REQUIRED=SRC2 PUBLIC_CLAIM_CEILING=example-only-no-outcome-claim '
            'ALLOWED_CHANGE_COUNT=1 PROHIBITED_CHANGE_COUNT=4 ROLLBACK_TRIGGER_COUNT=3 '
            'ROLLBACK_OWNER_ROLE_COUNT=<1-5> LIVE_WINDOW_REQUIRED=1 ' + confirm
        ),
        'ready_for_real_packet_trim': (
            base + 'TICKET_STATE=ready-for-real-packet CHANGE_CLASS=pct-a-trim '
            'SOURCE_TRUTH_REQUIRED=SRC2 PUBLIC_CLAIM_CEILING=draft-only-no-outcome-claim '
            'ALLOWED_CHANGE_COUNT=1 PROHIBITED_CHANGE_COUNT=4 ROLLBACK_TRIGGER_COUNT=3 '
            'ROLLBACK_OWNER_ROLE_COUNT=<1-5> LIVE_WINDOW_REQUIRED=1 ' + confirm
        ),
        'blocked_no_real_packet': (
            base + 'TICKET_STATE=blocked-no-real-packet CHANGE_CLASS=pct-b-suppress '
            'SOURCE_TRUTH_REQUIRED=not_evidence PUBLIC_CLAIM_CEILING=suppress-public-language '
            'ALLOWED_CHANGE_COUNT=0 PROHIBITED_CHANGE_COUNT=5 ROLLBACK_TRIGGER_COUNT=2 '
            'ROLLBACK_OWNER_ROLE_COUNT=<1-5> ' + confirm
        ),
        'quarantine': (
            base + 'TICKET_STATE=quarantined CHANGE_CLASS=pct-x-quarantine '
            'SOURCE_TRUTH_REQUIRED=not_evidence PUBLIC_CLAIM_CEILING=suppress-public-language '
            'ALLOWED_CHANGE_COUNT=0 PROHIBITED_CHANGE_COUNT=5 ROLLBACK_TRIGGER_COUNT=3 '
            'ROLLBACK_OWNER_ROLE_COUNT=<1-5> ' + confirm
        ),
        'active_change_after_activation_receipt_only': (
            base + 'TICKET_STATE=active-change CHANGE_CLASS=pct-c-sandbox-adjustment '
            'SOURCE_TRUTH_REQUIRED=SRC2 PUBLIC_CLAIM_CEILING=example-only-no-outcome-claim '
            'ALLOWED_CHANGE_COUNT=1 PROHIBITED_CHANGE_COUNT=4 ROLLBACK_TRIGGER_COUNT=3 '
            'ROLLBACK_OWNER_ROLE_COUNT=<1-5> LIVE_WINDOW_REQUIRED=1 '
            'ACTIVATION_RECEIPT=<scratch/.../activation-receipt.json> ' + confirm
        ),
    }


def build_markdown(brief: dict[str, Any]) -> str:
    decision = brief['source_first_packet_decision']
    slices = decision.get('decision_slices', {})
    commands = brief['bounded_change_ticket_command_templates']
    return f"""# FT-0181 post-decision change-ticket brief

Brief state: `{brief['brief_state']}`  
Source decision: `{decision['reference']}`  
Decision SHA-256: `{decision['decision_sha256']}`  
Board state: `{decision['board_state']}`  
Acceptance state: `{brief['acceptance_state']}`  
Evidence effect: `not_evidence`  
Closure effect: `does_not_close_ft0181`

## Decision-board context, without owner text

| Slice | Action |
|---|---|
| Authority | `{slices.get('authority_action')}` |
| Evidence | `{slices.get('evidence_action')}` |
| Construct | `{slices.get('construct_action')}` |
| Public | `{slices.get('public_action')}` |
| Lifecycle | `{slices.get('lifecycle_action')}` |
| Changed slice count | `{decision.get('changed_slice_count')}` |
| Rollback owner role count | `{decision.get('rollback_owner_role_count')}` |
| Source truth class from review | `{decision.get('source_truth_class')}` |

## Human ticket job

Choose exactly one bounded change-ticket route below, replace only the bounded
count placeholder and, for active-change only, an already-created activation
receipt path. Do not paste owner answer text, raw CSV rows, public claim
language, learner facts, protected facts, contact details, screenshots, or
security payloads into the command or release surfaces.

## Bounded route commands

### Ready for real packet / sandbox adjustment

Use this when the board chose a bounded sandbox adjustment but the same real
owner-reviewed source packet has not yet been accepted through
`owner-activation-receipt`.

```bash
{commands['ready_for_real_packet_sandbox']}
```

### Ready for real packet / trim

```bash
{commands['ready_for_real_packet_trim']}
```

### Blocked: no real packet

```bash
{commands['blocked_no_real_packet']}
```

### Quarantine

```bash
{commands['quarantine']}
```

### Active change only after activation receipt

Do not use this template until `make owner-activation-receipt` has created a
valid scratch-local activation receipt from the same first-packet decision and a
real owner-reviewed SRC2+ source packet.

```bash
{commands['active_change_after_activation_receipt_only']}
```

## Hard boundary

This brief is not a change ticket, source-truth acceptance, custody evidence,
public-summary support, service-record mutation, live-window authorization,
lifecycle movement, or closure. It is a scratch-local bridge from a
human-entered first-packet decision record to a human-entered post-decision
change-ticket record.
"""


def build_change_ticket_brief(*, decision: Path, output_dir: Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    decision_path = decision if decision.is_absolute() else ROOT / decision
    decision_path = decision_path.resolve()
    inside, parts = archive_relative(decision_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(decision_path, archive_root=ROOT, field_name='decision')
    if lane_error or decision_path.name != 'first-packet-decision.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-BRIEF-DECISION-BLOCKED',
            'message': 'Change-ticket brief requires a scratch-local first-packet-decision.json source.',
            'decision': relative(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not decision_path.exists() or not decision_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-BRIEF-DECISION-MISSING',
            'message': 'Referenced first-packet decision does not exist.',
            'decision': relative(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        decision_data = load_json(decision_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-BRIEF-DECISION-BLOCKED',
            'message': 'Referenced first-packet decision is not readable JSON.',
            'error': str(exc),
            'decision': relative(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    decision_error = owner_first_packet_decision_integrity_error(decision_data, archive_root=ROOT)
    if decision_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-BRIEF-DECISION-BLOCKED',
            'message': 'Referenced first-packet decision failed integrity checks: ' + decision_error,
            'decision': relative(decision_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir if output_dir is not None else default_output_dir(decision_path)
    out = out if out.is_absolute() else ROOT / out
    allowed, boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-BRIEF-OUTPUT-BLOCKED',
            'output_dir': relative(out),
            'output_boundary': boundary,
            'message': 'Change-ticket briefs are local/scratch artifacts and cannot be written into release-controlled surfaces.',
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if out.exists():
        if overwrite:
            if out.is_dir():
                shutil.rmtree(out)
            else:
                out.unlink()
        else:
            raise FileExistsError(f'output already exists: {out}; pass --overwrite to replace it')
    out.mkdir(parents=True, exist_ok=True)

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    decision_hash = sha256_file(decision_path)
    decision_ref = relative(decision_path)
    decision_slices = decision_data.get('decision_slices') if isinstance(decision_data.get('decision_slices'), dict) else {}
    source_truth = decision_data.get('source_workbench_review', {}).get('source_truth_class')
    brief = {
        'brief_type': 'FT-0181-post-decision-change-ticket-brief',
        'brief_version': REVISION,
        'created_at_utc': created,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'brief_state': 'CHANGE_TICKET_BRIEF_PREPARED_NOT_RECORDED',
        'source_first_packet_decision': {
            'reference': decision_ref,
            'decision_sha256': decision_hash,
            'board_state': decision_data.get('board_state'),
            'acceptance_state': decision_data.get('acceptance_state'),
            'evidence_state': decision_data.get('evidence_state'),
            'changed_slice_count': decision_data.get('changed_slice_count'),
            'rollback_owner_role_count': decision_data.get('rollback_owner_role_count'),
            'decision_slices': decision_slices,
            'source_truth_class': source_truth,
            'change_ticket_effect': decision_data.get('change_ticket_effect'),
            'revalidated_for_ticket_brief': True,
        },
        'acceptance_state': 'NOT_ACCEPTED',
        'ticket_effect': 'does_not_record_change_ticket',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'required_next_surface': 'docs/30-operations/ft0181-post-decision-change-ticket.md',
        'recommended_next_action': 'human-record-bounded-post-decision-change-ticket',
        'bounded_change_ticket_command_templates': command_templates(decision_ref),
        'allowed_ticket_states': ['blocked-no-real-packet', 'blocked-incomplete-board', 'ready-for-real-packet', 'active-change', 'rolled-back', 'quarantined'],
        'allowed_change_classes': ['pct-a-trim', 'pct-b-suppress', 'pct-c-sandbox-adjustment', 'pct-d-bounded-pilot', 'pct-x-quarantine'],
        'activation_boundary': 'active-change templates require an existing owner activation receipt; this brief does not create or imply SRC2+ activation.',
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_first_packet_decision_text': False,
            'copies_contact_details': False,
            'copies_learner_identifiers_or_protected_facts': False,
            'source_first_packet_decision_revalidated': True,
            'contains_hashes_counts_and_command_skeletons_only': True,
        },
        'forbidden_effects': [
            'change-ticket-automation',
            'raw-answer-copy-to-release',
            'custody-or-acceptance',
            'activation-receipt-creation',
            'service-record-edit',
            'public-claim-upgrade',
            'live-window-activation',
            'lifecycle-or-closure',
        ],
    }
    brief_error = owner_post_decision_change_ticket_brief_integrity_error(brief, archive_root=ROOT)
    if brief_error:
        shutil.rmtree(out)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'POST-DECISION-CHANGE-TICKET-BRIEF-BLOCKED',
            'message': brief_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    brief_path = out / 'change-ticket-brief.json'
    summary_path = out / 'POST-DECISION-CHANGE-TICKET-BRIEF.md'
    brief_path.write_text(json.dumps(brief, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    summary_path.write_text(build_markdown(brief), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'POST-DECISION-CHANGE-TICKET-BRIEF-PREPARED',
        'output_dir': relative(out),
        'brief_path': relative(brief_path),
        'summary_path': relative(summary_path),
        'source_decision': decision_ref,
        'acceptance_state': 'NOT_ACCEPTED',
        'ticket_effect': 'does_not_record_change_ticket',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'required_next_surface': 'docs/30-operations/ft0181-post-decision-change-ticket.md',
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_change_ticket_brief(decision=args.decision, output_dir=args.output_dir, overwrite=args.overwrite)
    except Exception as exc:
        if args.json:
            try:
                payload = json.loads(str(exc))
            except json.JSONDecodeError:
                payload = {'ok': False, 'outcome': 'POST-DECISION-CHANGE-TICKET-BRIEF-ERROR', 'message': str(exc), 'claim_ceiling': CLAIM_CEILING}
            print(json.dumps(payload, indent=2))
            return 1
        raise
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
