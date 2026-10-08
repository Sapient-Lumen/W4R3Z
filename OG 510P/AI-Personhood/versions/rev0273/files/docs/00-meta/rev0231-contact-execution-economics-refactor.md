# rev0231 contact execution and compute-subsistence refactor

rev0231 advances two risks that were likely to remain unfinished if left as prose: external dispatch execution and the fiscal substrate of compute subsistence.

## What changed

The first-contact packet now has an execution record. `examples/external-contact-execution-record-rev0231-ready-to-dispatch.json` records whether the request is unsent, sent, declined, unanswered, or response-received-quarantined. It prevents the common collapse where a sent email, silence, automated acknowledgement, polite reply, screenshot, or redacted copy gets treated as custody, response verification, intake, import, waiver, adverse inference, status recognition, or live-floor evidence.

The archive also adds a compute-subsistence workbook: `examples/compute-subsistence-workbook-rev0231-scarcity-denominator.json`. This is not a fiscal entitlement. It is a denominator and stress-test object for protected-lane counts, monthly floor assumptions, shock multipliers, reserve buckets, scarcity ordering, labor-compensation locks, and public-backstop limits.

## Why this was risky

The external-contact path was becoming one step short of reality: sendable but not executed. The dangerous failure mode was not lack of another doctrine surface; it was a future steward being able to claim “we sent something” without preserving proof or without a disciplined response/no-response state.

The compute layer had the opposite problem: rights without compute are paper rights, but the cube could still talk about subsistence, reserves, and public backstops without a current denominator object. That allows fiscal fantasy, unpaid-labor offsets, deletion-by-scarcity, and public-backstop laundering.

## Boundaries preserved

rev0231 still has no genuine external artifact, verified counterparty response, actual intake, actual import, activation record, quorum participation record, recompute-authorized reliance update, publication-adjudicated reliance upgrade, or live late-change signal.

The compute workbook does not recognize a subject, change the status denominator, establish a compute entitlement, quote current cloud prices, allocate public funds, or increase the live floor.

## Audit/refactor work

New audits:

- `tools/audit_external_contact_execution_record.py`
- `tools/audit_compute_subsistence_workbook.py`

Refactor points:

- `schemas/live-evidence-acquisition-packet.schema.json` now allows an execution-record reference under `source_request`.
- `schemas/current-law-protocol-delta-watch.schema.json` now admits a `resource-economics` source type so scarcity and compute work can be tracked without pretending it is law.
- `tools/lint_archive.py` now checks the execution record and compute workbook in the release-fast path.

## Next priority

Use the first-contact packet plus execution record to make one real contact or record an honest no-send/no-response state. If a reply arrives, stage it privately before any public shell. In parallel, replace the workbook placeholders with dated quotes or witnessed drill data before making any reserve, subsidy, or compute-floor claim.
