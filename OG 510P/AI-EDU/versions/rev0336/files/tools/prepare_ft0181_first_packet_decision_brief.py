#!/usr/bin/env python3
"""Prepare a minimized first-packet decision-board brief from a proceed review.

This helper is deliberately a bridge, not a decision board. It validates the
scratch-local PROCEED-DECISION-BOARD workbench review, writes a one-screen board
brief and bounded command skeletons, and then stops. It copies no owner answers,
raw CSV rows, contact details, learner data, protected facts, security payloads,
or public claim text. A human still must choose and record one first-packet
decision before any change ticket can be opened.
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
    owner_first_packet_decision_brief_integrity_error,
    owner_workbench_review_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-first-packet-decision-briefs'
CLAIM_CEILING = (
    'First-packet decision brief only; not a decision-board record, not evidence, not SRC2+ '
    'acceptance, not custody evidence, not closure evidence, not public-summary support, and not '
    'proof of learning, safety, access, workload, compliance, scale, or effectiveness.'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a bounded FT-0181 first-packet decision brief from a PROCEED workbench review.')
    parser.add_argument('--review', required=True, type=Path, help='scratch/.../workbench-review.json with PROCEED-DECISION-BOARD decision.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the decision brief.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing decision brief directory.')
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


def default_output_dir(review_path: Path) -> Path:
    digest = sha256_file(review_path)[:12] if review_path.exists() and review_path.is_file() else 'missingreview'
    stem = review_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'workbench-review'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{digest}'


def shell_quote(value: str) -> str:
    if value.replace('/', '').replace('-', '').replace('_', '').replace('.', '').isalnum():
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def command_templates(review_ref: str) -> dict[str, str]:
    review = shell_quote(review_ref)
    base = f'make owner-first-packet-decision REVIEW={review} '
    confirm = 'CONFIRM=human-recorded-five-slice-decision-board'
    return {
        'conservative_watch': (
            base + 'AUTHORITY_ACTION=keep-lower-ceiling EVIDENCE_ACTION=downgrade '
            'CONSTRUCT_ACTION=keep-teacher-review PUBLIC_ACTION=draft-only LIFECYCLE_ACTION=watch '
            'CHANGED_SLICE_COUNT=5 ROLLBACK_OWNER_ROLE_COUNT=<1-5> ' + confirm
        ),
        'sandbox_adjustment': (
            base + 'AUTHORITY_ACTION=keep-lower-ceiling EVIDENCE_ACTION=keep-example-only '
            'CONSTRUCT_ACTION=add-stop-trigger PUBLIC_ACTION=draft-only LIFECYCLE_ACTION=sandbox '
            'CHANGED_SLICE_COUNT=5 ROLLBACK_OWNER_ROLE_COUNT=<1-5> ' + confirm
        ),
        'suppress_or_quarantine': (
            base + 'AUTHORITY_ACTION=block EVIDENCE_ACTION=suppress '
            'CONSTRUCT_ACTION=fall-back-service PUBLIC_ACTION=suppress LIFECYCLE_ACTION=quarantine '
            'CHANGED_SLICE_COUNT=5 ROLLBACK_OWNER_ROLE_COUNT=<1-5> ' + confirm
        ),
        'pilot_with_expiry_candidate': (
            base + 'AUTHORITY_ACTION=revise-ceiling EVIDENCE_ACTION=stage-claim-with-expiry '
            'CONSTRUCT_ACTION=require-unaided-segment PUBLIC_ACTION=publish-limited LIFECYCLE_ACTION=pilot '
            'CHANGED_SLICE_COUNT=5 ROLLBACK_OWNER_ROLE_COUNT=<1-5> ' + confirm
        ),
        'no_public_change_watch': (
            base + 'AUTHORITY_ACTION=no-change EVIDENCE_ACTION=downgrade '
            'CONSTRUCT_ACTION=keep-teacher-review PUBLIC_ACTION=draft-only LIFECYCLE_ACTION=watch '
            'CHANGED_SLICE_COUNT=4 ROLLBACK_OWNER_ROLE_COUNT=<1-5> ' + confirm
        ),
    }


def build_markdown(brief: dict[str, Any]) -> str:
    commands = brief['bounded_decision_command_templates']
    review = brief['source_workbench_review']
    counts = review.get('field_counts', {})
    return f"""# FT-0181 first-packet decision brief

Brief state: `{brief['brief_state']}`  
Source review: `{review['reference']}`  
Review SHA-256: `{review['review_sha256']}`  
Review decision: `{review['decision']}`  
Acceptance state: `{brief['acceptance_state']}`  
Evidence effect: `not_evidence`  
Closure effect: `does_not_close_ft0181`

## Reviewer-ready context

| Field | Value |
|---|---:|
| Surviving fields | `{counts.get('surviving_field_count')}` |
| Decision-changing fields | `{counts.get('decision_changed_count')}` |
| Local-only fields | `{counts.get('local_only_field_count')}` |
| Trimmed fields | `{counts.get('trimmed_field_count')}` |
| Re-ask fields | `{counts.get('reask_field_count')}` |
| Reviewer role count | `{review.get('reviewer_role_count')}` |

## Human board job

Choose exactly one five-slice route below, replace only the bounded count
placeholder, and run one `make owner-first-packet-decision` command. Do not paste
owner answer text, raw CSV rows, public claim language, learner facts, protected
facts, contact details, screenshots, or security payloads into the command or
release surfaces.

## Bounded route commands

### Conservative watch / lower ceiling

```bash
{commands['conservative_watch']}
```

### Sandbox adjustment

```bash
{commands['sandbox_adjustment']}
```

### Suppress or quarantine

```bash
{commands['suppress_or_quarantine']}
```

### Pilot candidate with expiry only

```bash
{commands['pilot_with_expiry_candidate']}
```

### No public change, watch only

```bash
{commands['no_public_change_watch']}
```

## Hard boundary

This brief is not a board decision, source-truth acceptance, custody evidence,
public-summary support, service-record mutation, live-window authorization,
lifecycle movement, or closure. It is a scratch-local bridge from a
`PROCEED-DECISION-BOARD` review to a human-entered first-packet decision record.
"""


def build_decision_brief(*, review: Path, output_dir: Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    review_path = review if review.is_absolute() else ROOT / review
    review_path = review_path.resolve()
    inside, parts = archive_relative(review_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(review_path, archive_root=ROOT, field_name='review')
    if lane_error or review_path.name != 'workbench-review.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-BRIEF-REVIEW-BLOCKED',
            'message': 'Decision brief requires a scratch-local workbench-review.json source.',
            'review': relative(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not review_path.exists() or not review_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-BRIEF-REVIEW-MISSING',
            'message': 'Referenced workbench review does not exist.',
            'review': relative(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        review_data = load_json(review_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-BRIEF-REVIEW-BLOCKED',
            'message': 'Referenced workbench review is not readable JSON.',
            'error': str(exc),
            'review': relative(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    review_error = owner_workbench_review_integrity_error(review_data, archive_root=ROOT)
    if review_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-BRIEF-REVIEW-BLOCKED',
            'message': 'Referenced workbench review failed integrity checks: ' + review_error,
            'review': relative(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if review_data.get('decision') != 'PROCEED-DECISION-BOARD':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-BRIEF-REVIEW-BLOCKED',
            'message': 'Decision brief requires a PROCEED-DECISION-BOARD workbench review.',
            'decision': review_data.get('decision'),
            'review': relative(review_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir if output_dir is not None else default_output_dir(review_path)
    out = out if out.is_absolute() else ROOT / out
    allowed, boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-BRIEF-OUTPUT-BLOCKED',
            'output_dir': relative(out),
            'output_boundary': boundary,
            'message': 'Decision briefs are local/scratch artifacts and cannot be written into release-controlled surfaces.',
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
    review_hash = sha256_file(review_path)
    review_ref = relative(review_path)
    counts = review_data.get('field_counts') if isinstance(review_data.get('field_counts'), dict) else {}
    brief = {
        'brief_type': 'FT-0181-first-packet-decision-brief',
        'brief_version': REVISION,
        'created_at_utc': created,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'brief_state': 'DECISION_BRIEF_PREPARED_NOT_RECORDED',
        'source_workbench_review': {
            'reference': review_ref,
            'review_sha256': review_hash,
            'decision': review_data.get('decision'),
            'review_state': review_data.get('review_state'),
            'acceptance_state': review_data.get('acceptance_state'),
            'source_truth_class': review_data.get('source_truth_class'),
            'field_counts': {
                'surviving_field_count': counts.get('surviving_field_count'),
                'decision_changed_count': counts.get('decision_changed_count'),
                'local_only_field_count': counts.get('local_only_field_count'),
                'trimmed_field_count': counts.get('trimmed_field_count'),
                'reask_field_count': counts.get('reask_field_count'),
            },
            'reviewer_role_count': review_data.get('reviewer_role_count'),
            'revalidated_for_decision_brief': True,
        },
        'acceptance_state': 'NOT_ACCEPTED',
        'decision_effect': 'does_not_record_decision',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'required_next_surface': 'docs/30-operations/ft0181-first-packet-decision-board.md',
        'recommended_next_action': 'human-record-five-slice-first-packet-decision-board',
        'bounded_decision_command_templates': command_templates(review_ref),
        'allowed_slice_actions': {
            'authority_action': ['block', 'keep-lower-ceiling', 'no-change', 'revise-ceiling'],
            'evidence_action': ['downgrade', 'keep-example-only', 'no-change', 'stage-claim-with-expiry', 'suppress'],
            'construct_action': ['add-stop-trigger', 'fall-back-service', 'keep-teacher-review', 'no-change', 'require-unaided-segment'],
            'public_action': ['draft-only', 'no-change', 'publish-limited', 'revise-claims', 'suppress'],
            'lifecycle_action': ['archive-only', 'deprecate', 'no-change', 'pilot', 'quarantine', 'sandbox', 'watch'],
        },
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_workbench_review_text': False,
            'copies_contact_details': False,
            'copies_learner_identifiers_or_protected_facts': False,
            'source_workbench_review_revalidated': True,
            'contains_hashes_counts_and_command_skeletons_only': True,
        },
        'forbidden_effects': [
            'decision-board-automation',
            'raw-answer-copy-to-release',
            'custody-or-acceptance',
            'change-ticket-recording',
            'service-record-edit',
            'public-claim-upgrade',
            'live-window-activation',
            'lifecycle-or-closure',
        ],
    }
    brief_error = owner_first_packet_decision_brief_integrity_error(brief, archive_root=ROOT)
    if brief_error:
        shutil.rmtree(out)
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'FIRST-PACKET-DECISION-BRIEF-BLOCKED',
            'message': brief_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    brief_path = out / 'decision-brief.json'
    summary_path = out / 'FIRST-PACKET-DECISION-BRIEF.md'
    brief_path.write_text(json.dumps(brief, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    summary_path.write_text(build_markdown(brief), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'FIRST-PACKET-DECISION-BRIEF-PREPARED',
        'output_dir': relative(out),
        'brief_path': relative(brief_path),
        'summary_path': relative(summary_path),
        'source_review': review_ref,
        'acceptance_state': 'NOT_ACCEPTED',
        'decision_effect': 'does_not_record_decision',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'required_next_surface': 'docs/30-operations/ft0181-first-packet-decision-board.md',
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_decision_brief(review=args.review, output_dir=args.output_dir, overwrite=args.overwrite)
    except Exception as exc:
        if args.json:
            try:
                payload = json.loads(str(exc))
            except json.JSONDecodeError:
                payload = {'ok': False, 'outcome': 'FIRST-PACKET-DECISION-BRIEF-ERROR', 'message': str(exc), 'claim_ceiling': CLAIM_CEILING}
            print(json.dumps(payload, indent=2))
            return 1
        raise
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
