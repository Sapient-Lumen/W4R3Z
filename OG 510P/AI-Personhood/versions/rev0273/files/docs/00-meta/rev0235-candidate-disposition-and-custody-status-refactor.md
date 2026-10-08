# rev0235 — candidate disposition and custody status refactor

rev0235 focuses on the seam after candidate challenge/replay and before the custody authority gate. The dangerous failure mode was not absence of doctrine; it was a practical operator shortcut: a candidate challenge report could remain open while a later command-line `--challenge-status closed-*` override made the custody gate look resolved.

## Mission move

The archive already separated contact, execution, response triage, vault intake, normalization, candidate challenge, and custody authority. But the custody gate still accepted a raw closed challenge status as an operator argument. That created a silent status-override path: elapsed time, no response, automated acknowledgement, protocol/tool output, or a redacted artifact could be converted into a closed challenge if the operator supplied the right flag.

rev0235 adds a separate human-reviewed disposition record so that cannot happen.

## New operational object

The new object is `examples/candidate-challenge-disposition-record-rev0235-open-stayed.json`, backed by `schemas/candidate-challenge-disposition-record.schema.json` and checked by `tools/audit_candidate_challenge_disposition.py`.

The disposition layer records:

- the source candidate challenge report;
- the source normalization decision;
- whether the challenge is still open, blocked, upheld, rejected, or affirmatively closed;
- whether there is affirmative human counterparty evidence;
- whether request trace, identity, scoped authority, published limitations, and independent timestamp/log support exist;
- whether an objection was received and reviewed by a human;
- whether the apparent closure is only silence, elapsed time, automated acknowledgement, protocol/tool output, or redacted-only material.

The current release state is intentionally `challenge-open-stayed`; it cannot feed the custody authority gate.

## Custody gate refactor

`tools/prepare_custody_authority_gate.py` now distinguishes a legacy/status-display challenge override from a real disposition record. A closed challenge status without `--challenge-disposition-record` is blocked as missing authority even if the operator supplies authority-looking flags.

A positive-control path still exists: a valid candidate-challenge disposition may feed the custody gate, and the gate may then authorize preparation of a separate custody record. Even in that positive-control path, the gate does not create custody, formal response, intake, import, status recognition, or live-floor credit.

## Audit repairs

rev0235 also restores current-release candidate challenge and custody-gate examples. The archive had kept older rev0214–rev0221 examples while later release lint focused on contact/intake surfaces. That allowed the candidate/challenge-to-custody seam to drift out of the current release path.

Release lint now runs:

- `tools/audit_candidate_challenge_replay.py`;
- `tools/audit_candidate_challenge_disposition.py`;
- `tools/audit_custody_authority_gate.py`.

The new negative fixtures block silence-as-no-objection, automated-ack closure, and protocol/tool-output closure.

## What remains missing

No genuine external request has been sent. No genuine counterparty artifact, verified response, disposition, custody record, intake, import, floor activation, quorum participation, entitlement, compute reserve, recognition, or live-floor effect exists.

The next substantive move is still an actual dispatch/no-send record and then a genuine inbound artifact or response. If a candidate challenge ever opens from real material, it must be resolved through the new disposition layer before the custody authority gate may consume a closed status.
