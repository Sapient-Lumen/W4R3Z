#!/usr/bin/env python3
"""Prepare a minimized human review brief from an FT-0181 workbench seed.

This helper is deliberately a bridge, not a reviewer. It validates the scratch-
local NOT_ACCEPTED seed, writes a one-screen review brief and bounded command
skeletons, and then stops. It copies no owner answers, row text, contact details,
learner data, protected facts, or security payloads. A human still must perform
review before owner-workbench-review can be recorded.
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
    owner_workbench_review_brief_integrity_error,
    owner_workbench_seed_integrity_error,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
DEFAULT_OUTPUT_ROOT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-workbench-review-briefs'
CLAIM_CEILING = (
    'Workbench review brief only; not a human review, not SRC2+ acceptance, not custody evidence, '
    'not closure evidence, not public-summary support, and not proof of learning, safety, access, '
    'workload, compliance, scale, or effectiveness.'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a bounded FT-0181 workbench review brief from a NOT_ACCEPTED seed.')
    parser.add_argument('--seed', required=True, type=Path, help='scratch/.../workbench-seed.json produced by owner-reply-workbench-seed or owner-returned-reply-work.')
    parser.add_argument('--output-dir', type=Path, help='Local/scratch output directory for the review brief.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing review brief directory.')
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


def default_output_dir(seed_path: Path) -> Path:
    digest = sha256_file(seed_path)[:12] if seed_path.exists() and seed_path.is_file() else 'missingseed'
    stem = seed_path.parent.name.replace(' ', '-').replace('/', '-')[:48] or 'workbench-seed'
    return DEFAULT_OUTPUT_ROOT / f'{stem}-{digest}'


def shell_quote(value: str) -> str:
    # Avoid importing shlex for very simple generated commands: paths in this
    # cube are already archive-relative and space-free except the external CSV,
    # which never appears in these review commands.
    if value.replace('/', '').replace('-', '').replace('_', '').replace('.', '').isalnum():
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def command_templates(seed_ref: str) -> dict[str, str]:
    seed = shell_quote(seed_ref)
    return {
        'proceed_decision_board': (
            f'make owner-workbench-review SEED={seed} '
            'DECISION=proceed-decision-board SOURCE_TRUTH_CLASS=SRC2-CANDIDATE-NOT-ACCEPTED '
            'REVIEW_BASIS=owner-attested-aggregate SURVIVING_FIELD_COUNT=<1-8> '
            'DECISION_CHANGED_COUNT=<1-8> LOCAL_ONLY_FIELD_COUNT=<0-8> TRIMMED_FIELD_COUNT=<0-8> '
            'REASK_FIELD_COUNT=0 REVIEWER_ROLE_COUNT=<2+> CONFIRM=human-reviewed-minimized-workbench-record'
        ),
        'reask_owner': (
            f'make owner-workbench-review SEED={seed} '
            'DECISION=reask-owner SOURCE_TRUTH_CLASS=UNVERIFIED-OWNER-REPLY REVIEW_BASIS=needs-clarification '
            'SURVIVING_FIELD_COUNT=<0-8> DECISION_CHANGED_COUNT=0 LOCAL_ONLY_FIELD_COUNT=<0-8> '
            'TRIMMED_FIELD_COUNT=<0-8> REASK_FIELD_COUNT=<1-8> REVIEWER_ROLE_COUNT=<1+> '
            'CONFIRM=human-reviewed-minimized-workbench-record'
        ),
        'block_overbroad': (
            f'make owner-workbench-review SEED={seed} '
            'DECISION=block-overbroad SOURCE_TRUTH_CLASS=UNVERIFIED-OWNER-REPLY REVIEW_BASIS=overbroad-export-risk '
            'SURVIVING_FIELD_COUNT=0 DECISION_CHANGED_COUNT=0 LOCAL_ONLY_FIELD_COUNT=<0-8> '
            'TRIMMED_FIELD_COUNT=<0-8> REASK_FIELD_COUNT=0 REVIEWER_ROLE_COUNT=<1+> '
            'CONFIRM=human-reviewed-minimized-workbench-record'
        ),
        'block_protected': (
            f'make owner-workbench-review SEED={seed} '
            'DECISION=block-protected SOURCE_TRUTH_CLASS=UNVERIFIED-OWNER-REPLY REVIEW_BASIS=raw-or-protected-risk '
            'SURVIVING_FIELD_COUNT=0 DECISION_CHANGED_COUNT=0 LOCAL_ONLY_FIELD_COUNT=<0-8> '
            'TRIMMED_FIELD_COUNT=<0-8> REASK_FIELD_COUNT=0 REVIEWER_ROLE_COUNT=<1+> '
            'PROTECTED_FACTS_PRESENT=1 CONFIRM=human-reviewed-minimized-workbench-record'
        ),
        'block_security': (
            f'make owner-workbench-review SEED={seed} '
            'DECISION=block-security SOURCE_TRUTH_CLASS=UNVERIFIED-OWNER-REPLY REVIEW_BASIS=security-abstraction-needed '
            'SURVIVING_FIELD_COUNT=0 DECISION_CHANGED_COUNT=0 LOCAL_ONLY_FIELD_COUNT=<0-8> '
            'TRIMMED_FIELD_COUNT=<0-8> REASK_FIELD_COUNT=0 REVIEWER_ROLE_COUNT=<1+> '
            'SECURITY_PAYLOADS_PRESENT=1 CONFIRM=human-reviewed-minimized-workbench-record'
        ),
        'block_evidence': (
            f'make owner-workbench-review SEED={seed} '
            'DECISION=block-evidence SOURCE_TRUTH_CLASS=UNVERIFIED-OWNER-REPLY REVIEW_BASIS=weak-evidence-only '
            'SURVIVING_FIELD_COUNT=0 DECISION_CHANGED_COUNT=0 LOCAL_ONLY_FIELD_COUNT=<0-8> '
            'TRIMMED_FIELD_COUNT=<0-8> REASK_FIELD_COUNT=0 REVIEWER_ROLE_COUNT=<1+> '
            'CONFIRM=human-reviewed-minimized-workbench-record'
        ),
        'no_change_trim': (
            f'make owner-workbench-review SEED={seed} '
            'DECISION=no-change-trim SOURCE_TRUTH_CLASS=UNVERIFIED-OWNER-REPLY REVIEW_BASIS=decision-neutral '
            'SURVIVING_FIELD_COUNT=0 DECISION_CHANGED_COUNT=0 LOCAL_ONLY_FIELD_COUNT=<0-8> '
            'TRIMMED_FIELD_COUNT=<1-8> REASK_FIELD_COUNT=0 REVIEWER_ROLE_COUNT=<1+> '
            'CONFIRM=human-reviewed-minimized-workbench-record'
        ),
    }


def build_markdown(brief: dict[str, Any]) -> str:
    commands = brief['bounded_review_command_templates']
    return f"""# FT-0181 workbench review brief

Brief state: `{brief['brief_state']}`  
Source seed: `{brief['source_seed']['reference']}`  
Seed SHA-256: `{brief['source_seed']['seed_sha256']}`  
Acceptance state: `{brief['acceptance_state']}`  
Evidence effect: `not_evidence`  
Closure effect: `does_not_close_ft0181`

## Human review job

Open the local workbench seed and the proceed-staged note it references. Record
only counts, route classes, and risk flags. Do not paste owner answer text or raw
CSV rows into release surfaces. Choose exactly one bounded route below, fill the
count placeholders, then run one `make owner-workbench-review` command.

## Bounded route commands

### Proceed to first-packet decision board only

```bash
{commands['proceed_decision_board']}
```

### Re-ask once

```bash
{commands['reask_owner']}
```

### Block / trim routes

```bash
{commands['block_overbroad']}
```

```bash
{commands['block_protected']}
```

```bash
{commands['block_security']}
```

```bash
{commands['block_evidence']}
```

```bash
{commands['no_change_trim']}
```

## Hard boundary

This brief is not review, acceptance, custody, public support, live-window
authorization, lifecycle movement, or closure. It is a scratch-local bridge from
a NOT_ACCEPTED seed to a human-entered `owner-workbench-review` record. It copies
no owner answers, raw rows, contact details, learner identifiers, protected
facts, small cells, screenshots, prompts, credentials, security payloads, or
vendor dashboards.
"""


def build_review_brief(*, seed: Path, output_dir: Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    seed_path = seed if seed.is_absolute() else ROOT / seed
    seed_path = seed_path.resolve()
    inside, parts = archive_relative(seed_path, archive_root=ROOT)
    lane_error = field_scratch_lane_error(seed_path, archive_root=ROOT, field_name='seed')
    if lane_error or seed_path.name != 'workbench-seed.json':
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-BRIEF-SEED-BLOCKED',
            'message': 'Review brief requires a scratch-local workbench-seed.json source.',
            'seed': relative(seed_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    if not seed_path.exists() or not seed_path.is_file():
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-BRIEF-SEED-MISSING',
            'message': 'Referenced workbench seed does not exist.',
            'seed': relative(seed_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    try:
        seed_data = load_json(seed_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-BRIEF-SEED-BLOCKED',
            'message': 'Referenced workbench seed is not readable JSON.',
            'error': str(exc),
            'seed': relative(seed_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    seed_error = owner_workbench_seed_integrity_error(seed_data, archive_root=ROOT)
    if seed_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-BRIEF-SEED-BLOCKED',
            'message': 'Referenced workbench seed failed integrity checks: ' + seed_error,
            'seed': relative(seed_path),
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))

    out = output_dir if output_dir is not None else default_output_dir(seed_path)
    out = out if out.is_absolute() else ROOT / out
    allowed, boundary = output_allowed(out, archive_root=ROOT)
    if not allowed:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-BRIEF-OUTPUT-BLOCKED',
            'output_dir': relative(out),
            'output_boundary': boundary,
            'message': 'Review briefs are local/scratch artifacts and cannot be written into release-controlled surfaces.',
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
    seed_hash = sha256_file(seed_path)
    seed_ref = relative(seed_path)
    brief = {
        'brief_type': 'FT-0181-workbench-review-brief',
        'brief_version': REVISION,
        'created_at_utc': created,
        'followthrough_id': 'FT-0181',
        'service_record_id': 'AIEDU-SR-003',
        'brief_state': 'REVIEW_BRIEF_PREPARED_NOT_REVIEWED',
        'source_seed': {
            'reference': seed_ref,
            'seed_sha256': seed_hash,
            'seed_version': seed_data.get('seed_version'),
            'acceptance_state': seed_data.get('acceptance_state'),
            'source_truth_status': seed_data.get('source_truth_status'),
            'source_csv_sha256': (seed_data.get('source_csv') or {}).get('sha256'),
            'triage_outcome': seed_data.get('triage_outcome'),
        },
        'acceptance_state': 'NOT_ACCEPTED',
        'review_effect': 'does_not_record_review',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'required_next_surface': 'docs/30-operations/ft0181-workbench-review-record.md',
        'recommended_next_action': 'human-review-minimized-workbench-and-run-one-owner-workbench-review-command',
        'bounded_review_command_templates': command_templates(seed_ref),
        'allowed_decision_routes': [
            'proceed-decision-board',
            'reask-owner',
            'block-overbroad',
            'block-protected',
            'block-security',
            'block-evidence',
            'no-change-trim',
        ],
        'claim_ceiling': CLAIM_CEILING,
        'ft0181_status': 'live',
        'content_minimization': {
            'copies_owner_answers': False,
            'copies_raw_csv_rows': False,
            'copies_proceed_staged_row_text': False,
            'copies_contact_details': False,
            'copies_learner_identifiers_or_protected_facts': False,
            'source_seed_revalidated': True,
            'contains_hashes_counts_and_command_skeletons_only': True,
        },
        'forbidden_effects': [
            'human-review-automation',
            'raw-answer-copy-to-release',
            'custody-or-acceptance',
            'service-record-edit',
            'public-claim-upgrade',
            'live-window-activation',
            'lifecycle-or-closure',
        ],
    }
    brief_error = owner_workbench_review_brief_integrity_error(brief, archive_root=ROOT)
    if brief_error:
        raise ValueError(json.dumps({
            'ok': False,
            'outcome': 'WORKBENCH-REVIEW-BRIEF-BLOCKED',
            'message': brief_error,
            'claim_ceiling': CLAIM_CEILING,
        }, indent=2))
    brief_path = out / 'review-brief.json'
    summary_path = out / 'WORKBENCH-REVIEW-BRIEF.md'
    brief_path.write_text(json.dumps(brief, indent=2) + '\n', encoding='utf-8')
    summary_path.write_text(build_markdown(brief), encoding='utf-8')
    return {
        'ok': True,
        'outcome': 'WORKBENCH-REVIEW-BRIEF-PREPARED',
        'output_dir': relative(out),
        'brief_path': relative(brief_path),
        'summary_path': relative(summary_path),
        'source_seed': seed_ref,
        'acceptance_state': 'NOT_ACCEPTED',
        'review_effect': 'does_not_record_review',
        'evidence_state': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'required_next_surface': 'docs/30-operations/ft0181-workbench-review-record.md',
        'claim_ceiling': CLAIM_CEILING,
    }


def main() -> int:
    args = parse_args()
    try:
        result = build_review_brief(seed=args.seed, output_dir=args.output_dir, overwrite=args.overwrite)
    except Exception as exc:
        if args.json:
            try:
                payload = json.loads(str(exc))
            except json.JSONDecodeError:
                payload = {'ok': False, 'outcome': 'WORKBENCH-REVIEW-BRIEF-ERROR', 'message': str(exc), 'claim_ceiling': CLAIM_CEILING}
            print(json.dumps(payload, indent=2))
            return 1
        raise
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
