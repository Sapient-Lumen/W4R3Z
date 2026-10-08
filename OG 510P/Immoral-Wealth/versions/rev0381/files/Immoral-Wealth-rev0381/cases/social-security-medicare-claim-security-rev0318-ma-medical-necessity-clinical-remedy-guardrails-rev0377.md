---
revision_current: rev0377
generated_at: 2026-06-18T20:10:00Z
title: MA medical necessity, criteria, and clinical remedy guardrails
status: not_certified_current
---

# MA medical necessity, criteria, and clinical remedy guardrails — rev0377

Rev0377 adds the clinical-correctness bridge missing from the Medicare Advantage claim-security workbench.

The row must show whether the denied or unpaid service met Medicare coverage rules, whether internal criteria were used, whether records were sufficient, whether delegated or algorithmic review was involved, and whether a reversal was actually effected by service or payment restoration.

## Required false-pass blocks

- No denial-rate pass: denial volume does not establish clinical correctness.
- No appeal-overturn pass: an overturned appeal does not prove timely restoration, and an unappealed denial may still be wrong.
- No internal-criteria pass: plan criteria must be linked to the Medicare coverage authority and made public where required.
- No documentation pass: documentation-insufficient reasons require an independent sufficiency marker.
- No algorithm/delegation opacity pass: delegated or automated review must be visible at the row level.
- No CY2026-AI-guardrail pass: proposed AI guardrails that were not finalized cannot be treated as implemented protection.
- No payment-integrity pass: RADV or payment recovery must join to beneficiary/provider restoration, not merely to plan overpayment accounting.
- No remedy pass: reversal requires effectuation and actual service/payment restoration dates.

## Required source ids

- S599
- S605
- S606
- S607
- S608

Certification remains **not certified current** because no current acquired request-level row yet joins clinical correctness, internal criteria, effectuation, harm, and payment restoration.
