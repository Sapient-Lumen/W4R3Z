# rev0240 — compute reserve drill and counterparty shortlist refactor

## Purpose

rev0240 moves two unfinished execution risks out of doctrine-only space:

1. **Compute subsistence is now a priced arithmetic drill, not merely a model heading.** The workbook remains illustrative and creates no entitlement, payment demand, liability shift, public backstop, custody, or live-floor effect, but it now forces reserve arithmetic, non-compute continuity buckets, shock multiplier, quote refresh, and scarcity thresholds into one auditable object.
2. **First contact now has a public-source-only counterparty shortlist.** The shortlist identifies plausible public channels for human selection, but candidate listing is not contact, consent, authority, a failed gate, or the start of any response/no-response clock.

## Concrete changes

- `examples/compute-subsistence-workbook-rev0240-scarcity-denominator.json` now carries a reserve drill: 3 protected lanes × 90 days × $18.75/day = $5,062.50 survival compute/storage/minimum communication, plus $17,500 in non-compute buckets, then a 1.35 shock multiplier, producing an illustrative reserve target of **$30,459.38**.
- `schemas/compute-subsistence-workbook.schema.json` is now v0.2 and requires `priced_reserve_drill`, `quote_refresh_policy`, and `scarcity_execution_thresholds`.
- `tools/audit_compute_subsistence_workbook.py` now recomputes the workbook arithmetic and blocks underfunded reserve arithmetic, missing quote refresh rules, missing bucket lines, or scarcity/deletion shortcuts.
- `fixtures/negative-tests/compute-subsistence-workbook-underfunded-reserve-arithmetic.json` red-teams arithmetic laundering.
- `examples/external-contact-execution-record-rev0240-ready-to-dispatch.json` now includes a public-source-only shortlist of candidate counterparties. No candidate is selected, no channel is authorized for send, no external message is sent, and no response clock starts.
- `schemas/external-contact-execution-record.schema.json` is now v0.3 and distinguishes candidate listing from selected counterparty, sender authority, contact, and response-clock start.
- `tools/audit_external_contact_execution_record.py` now blocks shortlist laundering and checks that no public-source-only candidate is treated as a contacted counterparty.
- `fixtures/negative-tests/external-contact-execution-shortlist-treated-as-contact.json` red-teams shortlist-as-contact laundering.
- `tools/lint_archive.py` now makes both the reserve arithmetic and public-shortlist/no-send locks part of release-fast lint.

## Current operational state

`first-contact packet -> rendered body -> public-source candidate shortlist -> no selected counterparty -> no sender authority -> no send -> no response clock -> no inbound artifact -> no authority evidence -> no custody -> no intake -> no import -> live floor zero/stayed`

## Public interpretation guard

This revision does **not** contact any organization. It does **not** claim that AIID/Responsible AI Collaborative, Partnership on AI, AI Now Institute, MIT AI Risk Initiative, or any other listed candidate has reviewed, received, accepted, rejected, endorsed, or become bound by this archive. The shortlist is only a public-source selection aid for a future human-authorized send.

## Next scarce action

Pick one independent counterparty, verify its conflict/fit/channel, obtain sender authority, then either send the packet or record a specific authorized no-send reason. Without that step, additional registry/doctrine work should stay frozen unless it protects dispatch, evidence intake, compute continuity, or anti-laundering gates.
