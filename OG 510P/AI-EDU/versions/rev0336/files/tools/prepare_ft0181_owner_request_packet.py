#!/usr/bin/env python3
"""Prepare the outbound FT-0181 owner request packet.

This utility creates a local/scratch send packet for AIEDU-SR-003. It does not
send anything, accept evidence, certify source truth, or close FT-0181. The goal
is to make the next real field action executable without copying contact details,
learner records, or owner names into the archive. The current release also emits a local field-texture memo and send-now brief so owner-contact friction can be captured and the outbound action can be completed without becoming evidence or a new release-control family.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ft0181_field_guards import FIRST_CONTACT_MAX_DAYS, operator_due_date_iso, operator_today_iso, output_allowed

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')
TEMPLATE_PATH = ROOT / 'templates' / 'ft0181-eight-row-owner-reply-template.csv'
DEFAULT_OUTPUT = ROOT / 'scratch' / 'field' / 'ft0181' / 'owner-request-packets' / 'aiedu-sr-003-owner-request'

EXPECTED_COLUMNS = [
    'row_id',
    'required_owner_reply',
    'owner_response',
    'local_only_check',
    'intake_note',
]
EXPECTED_ROW_IDS = [str(i) for i in range(1, 9)]
FORBIDDEN_ARG_TERMS = [
    'student id',
    'learner id',
    'student name',
    'learner name',
    'full export',
    'raw lms export',
    'gradebook row',
    'screenshot',
    'chat transcript',
    'api key',
    'credential',
    'protected status',
    'disability facts',
    'accommodation facts',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prepare a local FT-0181 owner request send packet.')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT), help='Local/scratch output directory for the send packet.')
    parser.add_argument('--service-label', default='AIEDU-SR-003 draft reminder pilot', help='Non-sensitive service label to use in the email/checklist.')
    parser.add_argument('--owner-role', default='accountable service owner', help='Role, not a person name, for the intended owner recipient.')
    parser.add_argument('--source-record-set', default='local service record set or source system, to be named by the owner', help='Aggregate source record-set label; do not include learner identifiers.')
    parser.add_argument('--date-range', default='owner-named date range', help='Aggregate date range for the owner to confirm.')
    parser.add_argument('--return-date', default='', help='Requested return date; defaults to the bounded first-contact clock from today.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing packet directory.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable manifest instead of the short note.')
    return parser.parse_args()



def argument_boundary_error(*values: str) -> str | None:
    combined = ' '.join(values).lower()
    for term in FORBIDDEN_ARG_TERMS:
        if term in combined:
            return term
    return None

def default_return_date() -> str:
    return operator_due_date_iso(FIRST_CONTACT_MAX_DAYS)


def load_template_rows() -> list[dict[str, str]]:
    if not TEMPLATE_PATH.exists():
        raise SystemExit(f'owner reply template missing: {TEMPLATE_PATH.relative_to(ROOT)}')
    with TEMPLATE_PATH.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        columns = reader.fieldnames or []
    if columns != EXPECTED_COLUMNS:
        raise SystemExit('owner reply template columns changed; refuse packet prep')
    if [row.get('row_id') for row in rows] != EXPECTED_ROW_IDS:
        raise SystemExit('owner reply template row ids changed; refuse packet prep')
    for row in rows:
        if row.get('owner_response'):
            raise SystemExit('owner reply template must keep owner_response blank')
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def path_ref(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def email_body(*, service_label: str, owner_role: str, source_record_set: str, date_range: str, return_date: str) -> str:
    return f"""Subject: AIEDU-SR-003 bounded owner reply request for {service_label}

Hello,

I am preparing the first FT-0181 owner-reviewed intake packet for {service_label}.
This is a bounded eight-row request, not a request for learner-level records, names,
raw LMS exports, screenshots, chat transcripts, gradebook rows, security payloads,
protected-status facts, staff surveillance records, vendor dashboard dumps, or small-cell cuts.

Requested owner role: {owner_role}
Source record set/date boundary to confirm locally: {source_record_set}; {date_range}
Requested return date: {return_date}

Please fill only the blank owner_response column in the attached CSV. Keep all raw,
protected, identifying, or small-cell material local. Unknown is acceptable where the
method/source is named. The most important confirmations are:

1. service/source/date boundary;
2. aggregate counts above local privacy thresholds;
3. draft-only, no automatic send, no durable write, no penalty, and no protected-status inference;
4. human fallback, rollback owner, incident class labels if any, and one stop condition;
5. workload signal if known;
6. training/use-guidance note if known;
7. public claim ceiling; and
8. redaction assertion plus owner attestation that this is real operational material, not a mock,
   vendor-only claim, rehearsal, or unreviewed analytics export.

A response can be short. If the answer cannot be provided safely, please return the CSV with
"NO-OWNER-PACKET" or the safe reason in the relevant rows rather than broadening the transfer.

Thank you.
"""


def checklist(*, service_label: str, output_dir: Path, return_date: str) -> str:
    rel_template = TEMPLATE_PATH.relative_to(ROOT).as_posix()
    return f"""# FT-0181 owner request send checklist

Packet state: `PREPARED_NOT_SENT`
Evidence state: `NO-OWNER-PACKET-YET`
Service: `{service_label}`
Requested return date: `{return_date}`

This local packet is an execution aid for first contact. It is not evidence, does not
upgrade source truth, does not authorize live-window work, and does not close `FT-0181`.

## Before sending

- Confirm the intended recipient is an accountable owner or their delegated local route.
- Keep recipient names, contact details, learner facts, protected facts, and raw records out of this archive.
- Attach only `AIEDU-SR-003-eight-row-owner-reply-template.csv`, copied from `{rel_template}`.
- Do not add rows, columns, screenshots, transcripts, gradebook exports, vendor dashboards, or raw LMS data.
- Do not ask for small cells, protected-status cuts, staff surveillance residue, credentials, prompts, or security payloads.
- Use `FIELD-TEXTURE-MEMO.md` only for local friction notes; do not paste owner answers or protected facts into it.
- If no accountable owner route exists, run `make owner-route-block` from the
  packet/router fallback instead of recording a send log or creating new doctrine.

## After sending

Do not handwrite dates into a contact-clock command. After the human send or
adaptation actually happened, run the router and execute only the dated
`make owner-after-human-send` command it emits. That guarded helper records the
minimal send log and the SENT_AWAITING_REPLY contact clock together, with no
recipient names, addresses, owner answers, learner facts, or raw/protected
material:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/aiedu-sr-003-after-send
```

The lower-level `owner-send-log` and `owner-contact-status` targets remain repair
paths for already-written local scratch state, but the normal first-contact path
is now the one-command `owner-after-human-send` helper. The sent clock must still
source `send-log.json`, not the prepared packet manifest.

If no viable packet returns after the clock, rerun the same router. It will emit
one bounded re-ask and, after that clock passes, a dated `STATUS=no-owner-packet`
command instead of a wider ask or a new doctrine surface.

## After a reply

Do not run intake directly from a remembered command. Route the returned, owner-attested CSV through the field router first so archive fixtures, examples,
templates, and copied smoke files are blocked before intake:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
```

Execute only the command emitted in `FIELD-NEXT-ACTION.md`. After intake writes a
local bundle, rerun the router without `CSV=`. It will emit the bounded workbench
seed command only when the latest intake bundle is `PROCEED-STAGED`:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake
```

## If no viable packet returns

After the local response clock and no more than one clarification, record `NO-OWNER-PACKET`.
Do not create another first-contact surface to compensate for the missing packet.

Generated packet directory: `{output_dir.as_posix()}`
"""




def no_packet_note(*, service_label: str, owner_role: str, source_record_set: str, date_range: str, return_date: str) -> str:
    return f"""# FT-0181 NO-OWNER-PACKET local note

Outcome: `NO-OWNER-PACKET`
Evidence state: `not SRC2+; not real pilot evidence; not closure evidence`
Service attempted: `{service_label}`
Owner role attempted: `{owner_role}`
Source/date boundary attempted: `{source_record_set}; {date_range}`
Requested return date: `{return_date}`

Use this only if the first bounded request and no more than one clarification do not
produce a viable eight-row owner reply. Do not paste owner emails, recipient names,
contact details, learner records, protected facts, screenshots, small cells, prompts,
credentials, vendor dashboards, or raw exports into this note.

## Decision

Keep `FT-0181` live. Do not widen the request, add a workaround registry, import
synthetic evidence, or claim learning, safety, access, workload, compliance, scale,
or effectiveness.
"""

def field_texture_memo(*, service_label: str, owner_role: str, source_record_set: str, date_range: str, return_date: str) -> str:
    return f"""# FT-0181 owner-contact field texture memo

Memo state: `LOCAL_FIELD_TEXTURE_NOT_EVIDENCE`
Evidence state: `not SRC2+; not real pilot evidence; not closure evidence`
Service attempted: `{service_label}`
Owner role attempted: `{owner_role}`
Source/date boundary attempted: `{source_record_set}; {date_range}`
Requested return date: `{return_date}`

Use this memo outside the release archive or in `scratch/` to capture implementation
friction from the first bounded owner-contact attempt. It is for local learning only.
It must not copy recipient names, email addresses, learner identifiers, protected
facts, small cells, screenshots, raw exports, vendor dashboards, prompts, credentials,
or owner answer text.

## Fill locally after contact

| Field | Local note |
|---|---|
| Packet sent or adapted? |  |
| Sent-date clock recorded through router? |  |
| Owner route clear, ambiguous, wrong owner, or unavailable? |  |
| Approximate owner/staff time burden, if volunteered |  |
| Rows that were confusing, without copying answers |  |
| Rows owner could not answer safely |  |
| Any refusal class: overbroad, protected, authority, security, evidence, or no packet |  |
| Whether the bounded ask avoided a broader export request |  |
| Whether a narrower future ask is obvious |  |
| Public language impact: none, lower, or hold |  |

## Use boundary

This memo may inform the next field action or a future trim. It cannot be used as evidence, cannot support a public claim, cannot bypass
returned-CSV triage, and cannot close `FT-0181`. If the memo contains raw owner answers or protected facts, quarantine
it locally and do not copy it into the release archive.
"""


def send_now_brief(*, service_label: str, owner_role: str, source_record_set: str, date_range: str, return_date: str, packet_manifest_ref: str) -> str:
    return f"""# FT-0181 send-now brief

Brief state: `OPERATOR_SEND_AID_NOT_EVIDENCE`
Evidence state: `not SRC2+; not real pilot evidence; not closure evidence`
Service: `{service_label}`
Owner route: `{owner_role}`
Source/date boundary: `{source_record_set}; {date_range}`
Requested return date: `{return_date}`

This is the one-page action surface for completing the first owner contact. It is
local/scratch material only and must not be copied into the release archive after
adaptation.

## Do exactly this

The only field judgment before sending is whether a real accountable owner route
exists. If yes, send the packet. If no, stop and record the route block locally with
`make owner-route-block`; do not create more archive doctrine or a fake send log
to compensate.

1. Choose the accountable owner or delegated owner route outside this archive.
2. Copy the subject and body from `AIEDU-SR-003-owner-request-email.txt`.
3. Attach only `AIEDU-SR-003-eight-row-owner-reply-template.csv`.
4. Do not attach `FIELD-TEXTURE-MEMO.md`, this brief, screenshots, raw exports,
   transcripts, gradebook rows, vendor dashboards, protected facts, credentials,
   prompts, or learner-level records.
5. If no accountable owner route exists, do **not** record a send log. Record the
   local route block instead and then rerun the router:

```bash
make owner-route-block PACKET={packet_manifest_ref} CONFIRM=human-confirmed-owner-route-block-no-send OUT=scratch/field/ft0181/owner-route-blocks/aiedu-sr-003-route-block
```

6. After the human send/adaptation is complete, run the router and execute only its
   dated `make owner-after-human-send` command. The emitted command includes
   `CONFIRM=` and a `PACKET=` reference; do not remove them, and do not run the
   command before the human send/adaptation actually happened. The helper writes
   both `send-log.json` and the sourced `SENT_AWAITING_REPLY` contact clock:

```bash
make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/aiedu-sr-003-after-send
```

## If blocked while sending

| Block | Local action |
|---|---|
| No accountable owner route is available | Run `make owner-route-block`; optionally add route texture in `FIELD-TEXTURE-MEMO.md`; do not invent a recipient or record a send log. |
| Owner asks for a broader export instead | Keep raw material local and classify the result as overbroad if a reply arrives. |
| Recipient asks whether unknown is acceptable | Confirm that `unknown` is acceptable when the source or method is named. |
| Recipient wants to answer in prose | Ask them to preserve the eight row meanings or return the CSV; do not add rows. |
| Protected, small-cell, security, or credential material appears | Quarantine locally; do not import it or paste it into this packet. |

## Claim boundary

Sending this request, adapting it, recording a route block, recording the send log, or recording the send clock does not prove that
the service works, is safe, preserves access, reduces workload, is compliant,
scales, or improves learning. It only moves `FT-0181` from prepared-not-sent
toward either a real returned owner packet or a bounded no-owner-packet outcome.
"""

def build_packet(
    *,
    output_dir: Path,
    service_label: str,
    owner_role: str,
    source_record_set: str,
    date_range: str,
    return_date: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    forbidden = argument_boundary_error(service_label, owner_role, source_record_set, date_range)
    if forbidden:
        return {
            'ok': False,
            'error': 'OWNER-REQUEST-ARG-BLOCKED',
            'reason': f'argument includes forbidden first-contact term: {forbidden}',
            'output_dir': str(output_dir),
            'state': 'NOT_PREPARED',
        }
    allowed, reason = output_allowed(output_dir, archive_root=ROOT)
    if not allowed:
        return {
            'ok': False,
            'error': 'OWNER-REQUEST-OUTPUT-BLOCKED',
            'reason': reason,
            'output_dir': str(output_dir),
            'state': 'NOT_PREPARED',
        }

    rows = load_template_rows()
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        return {
            'ok': False,
            'error': 'OWNER-REQUEST-OUTPUT-EXISTS',
            'reason': 'use --overwrite or choose an empty directory',
            'output_dir': str(output_dir),
            'state': 'NOT_PREPARED',
        }
    if output_dir.exists() and overwrite:
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / 'AIEDU-SR-003-eight-row-owner-reply-template.csv'
    email_path = output_dir / 'AIEDU-SR-003-owner-request-email.txt'
    checklist_path = output_dir / 'SEND-CHECKLIST.md'
    no_packet_path = output_dir / 'NO-OWNER-PACKET-NOTE.md'
    field_texture_path = output_dir / 'FIELD-TEXTURE-MEMO.md'
    send_brief_path = output_dir / 'SEND-NOW-BRIEF.md'
    manifest_path = output_dir / 'packet-manifest.json'

    write_csv(csv_path, rows)
    email_path.write_text(
        email_body(
            service_label=service_label,
            owner_role=owner_role,
            source_record_set=source_record_set,
            date_range=date_range,
            return_date=return_date,
        ),
        encoding='utf-8',
    )
    checklist_path.write_text(
        checklist(service_label=service_label, output_dir=output_dir, return_date=return_date),
        encoding='utf-8',
    )
    no_packet_path.write_text(
        no_packet_note(
            service_label=service_label,
            owner_role=owner_role,
            source_record_set=source_record_set,
            date_range=date_range,
            return_date=return_date,
        ),
        encoding='utf-8',
    )
    field_texture_path.write_text(
        field_texture_memo(
            service_label=service_label,
            owner_role=owner_role,
            source_record_set=source_record_set,
            date_range=date_range,
            return_date=return_date,
        ),
        encoding='utf-8',
    )
    send_brief_path.write_text(
        send_now_brief(
            service_label=service_label,
            owner_role=owner_role,
            source_record_set=source_record_set,
            date_range=date_range,
            return_date=return_date,
            packet_manifest_ref=path_ref(manifest_path),
        ),
        encoding='utf-8',
    )

    manifest = {
        'packet_id': 'AIEDU-SR-003-OWNER-REQUEST',
        'followthrough_id': 'FT-0181',
        'packet_version': REVISION,
        'created_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'operator_local_date': operator_today_iso(),
        'packet_state': 'PREPARED_NOT_SENT',
        'evidence_state': 'NO-OWNER-PACKET-YET',
        'source_truth_class': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'service_label': service_label,
        'owner_role_label': owner_role,
        'source_record_set_label': source_record_set,
        'date_range_label': date_range,
        'requested_return_date': return_date,
        'output_boundary': reason,
        'generated_files': [
            csv_path.name,
            email_path.name,
            checklist_path.name,
            no_packet_path.name,
            field_texture_path.name,
            send_brief_path.name,
            manifest_path.name,
        ],
        'request_exclusions': [
            'learner_identifiers',
            'names_or_contact_details_in_archive',
            'raw_lms_exports',
            'screenshots_or_transcripts',
            'gradebook_rows',
            'protected_status_facts',
            'small_cell_cuts',
            'security_payloads_or_credentials',
            'vendor_dashboard_dumps',
            'staff_surveillance_records',
        ],
        'next_commands': [
            'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/aiedu-sr-003-after-send',
            'if no accountable owner route exists, make owner-route-block PACKET=<packet-manifest.json> CONFIRM=human-confirmed-owner-route-block-no-send and rerun owner-field-next',
            'make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply',
            'make owner-field-next OUT=scratch/field/ft0181/ft0181-field-next-action/after-intake',
            'execute only the command emitted by FIELD-NEXT-ACTION.md; do not bypass the router-first source firebreak with direct intake or staging commands',
        ],
        'router_expected_outcomes': [
            'RECORD-SEND-LOG-AFTER-HUMAN-SEND emits make owner-after-human-send with PACKET, fresh dates, and CONFIRM, plus a make owner-route-block fallback command if no accountable owner route exists',
            'OWNER-ROUTE-BLOCK-RECORDED-NO-SEND stops the route without a send log, contact clock, evidence, closure, or public claim',
            'RECORD-SENT-FROM-SEND-LOG emits make owner-contact-status STATUS=sent-awaiting-reply with fresh dates, CONFIRM, and SOURCE_ARTIFACT=.../send-log.json',
            'SEND-ONE-BOUNDED-REASK emits make owner-contact-status STATUS=reask-awaiting-reply with fresh dates, CONFIRM, and SOURCE_ARTIFACT',
            'RECORD-NO-OWNER-PACKET emits make owner-contact-status STATUS=no-owner-packet after the bounded re-ask clock with CONFIRM and SOURCE_ARTIFACT',
            'RUN-OWNER-REPLY-INTAKE only accepts plausible non-fixture returned CSV paths before intake',
            'SEED-WORKBENCH is emitted only after a local PROCEED-STAGED intake bundle exists',
        ],
        'limits': [
            'prepared packet is not sent evidence',
            'real returned CSV must be owner-attested before staging',
            'do not copy local contacts or learner records into release archive',
            'record NO-OWNER-PACKET rather than widening the request if no safe reply arrives',
            'the generated NO-OWNER-PACKET note is local non-evidence and keeps FT-0181 live',
            'the generated field-texture memo captures local implementation friction only and must not copy raw owner answers',
            'the generated send-now brief is an operator aid only and cannot become evidence or public claim support',
            'owner-route-block commands require operator confirmation and a valid scratch packet manifest, and do not create a sent or reask clock',
            'owner-after-human-send commands require operator confirmation, a valid scratch packet manifest, and a bounded first-contact response clock; the lower-level owner-send-log remains a repair path',
            'contact-status sent commands require a verified send-log source rather than a prepared packet manifest and cannot extend the first-contact clock beyond the bounded limit',
            'contact-status reask/no-owner commands require status-specific operator confirmation and verified source-artifact trace values',
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return {
        'ok': True,
        'packet_state': manifest['packet_state'],
        'evidence_state': manifest['evidence_state'],
        'followthrough_id': 'FT-0181',
        'output_dir': str(output_dir),
        'files': manifest['generated_files'],
        'manifest': manifest,
    }


def main() -> None:
    args = parse_args()
    return_date = args.return_date or default_return_date()
    result = build_packet(
        output_dir=Path(args.output_dir),
        service_label=args.service_label,
        owner_role=args.owner_role,
        source_record_set=args.source_record_set,
        date_range=args.date_range,
        return_date=return_date,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get('ok'):
        print(
            'prepare_ft0181_owner_request_packet: OK '
            f"({result['packet_state']}, {result['evidence_state']}, {result['output_dir']})"
        )
    else:
        raise SystemExit(f"prepare_ft0181_owner_request_packet: {result['error']} ({result['reason']})")


if __name__ == '__main__':
    main()
