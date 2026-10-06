# Breakglass does not silently reopen ordinary attestation-gated authority

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt

The archive already made several hard attestation decisions:

- ordinary secret and workload-identity lanes stay fail-closed on rejected posture,
- breakglass remains the explicit emergency lane,
- decisive consuming receipts pin the exact attestation decision tuple,
- and those receipts now mirror the exact pinned verifier verdict through `attestation_receipt_verdict`.

What still needed one more narrow cut was the **after-effect** of breakglass itself.
Even if breakglass is explicit, implementations can still drift into a sticky emergency model where a pre-breakglass accepted/degraded receipt gets reused later, or where operators assume “we used breakglass successfully, so ordinary lanes are open again.”

Related:
- ADR: `adrs/ADR-0239-breakglass-does-not-silently-reopen-ordinary-attestation-gated-authority.md`
- rejected ordinary-authority boundary: `docs/647-rejected-attestation-does-not-silently-mint-ordinary-authority-breakglass-stays-explicit.md`
- pinned-verdict boundary: `docs/648-attestation-consuming-action-receipts-carry-the-exact-pinned-attestation-verdict.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`

## The boundary

`breakglass.receipt` now carries:

- `ordinary_resumption_posture = fresh-attestation-after-breakglass-created-at-required`

That field is evidence-only, but it makes one operational rule explicit:

- breakglass does **not** silently reopen ordinary attestation-gated authority,
- the relevant time boundary is the breakglass receipt `created_at`,
- and any later ordinary attestation-gated authority must consume a fresh `attestation.receipt` issued **after** that breakglass `created_at`.

In plain terms:

- breakglass can be the explicit emergency lane,
- but it is not standing ordinary authority,
- and it does not let the system reuse pre-breakglass accepted/degraded evidence as though nothing happened.

## Why this matters

### 1) It removes the hidden “return to normal” loophole

Without an explicit post-breakglass resumption rule, operators and services still need dashboards, notes, or memory to decide whether a later ordinary secret release or workload identity issuance had truly fresh posture.
That makes backend state the real product.

### 2) It keeps emergency recovery from becoming sticky authority

Breakglass is supposed to be bounded and reviewable.
If it implicitly reopens ordinary lanes afterward, it becomes a shadow policy override instead of an explicit emergency lane.

### 3) It keeps A/B/C/D coherent

- **A / fleet host:** post-recovery secret/identity lanes can require fresh measured posture instead of inheriting old accepted evidence.
- **B / workstation:** trusted UI can explain that emergency recovery happened, but ordinary sensitive lanes need fresh posture afterward.
- **C / general-purpose OS:** compatibility stays possible, but Derive-managed attestation lanes do not silently inherit emergency-state authority.
- **D / appliance factory / regulatory:** audit review gets one portable answer for when ordinary attestation-gated authority may resume.

## Schema/example consequence

The canonical emergency receipt now teaches this directly:

- `spec/breakglass.receipt.schema.json`
- `spec/examples/breakglass.receipt.json`
- `spec/examples/breakglass.receipt.rejected.json`

Ordinary attestation-gated authority schemas now also teach the complementary rule:

- `spec/secret.receipt.schema.json`
- `spec/workload.identity.issue.receipt.schema.json`

Those ordinary lanes still carry their own exact attestation tuple and exact pinned verdict mirror.
This new boundary adds the missing temporal rule:
that ordinary post-breakglass authority must use fresh post-breakglass attestation evidence rather than reusing older accepted/degraded evidence.

## Guardrail

`tools/check_breakglass_resumption_contract.py`

This guardrail checks that:

- `breakglass.receipt` requires `ordinary_resumption_posture`,
- the fixed value remains `fresh-attestation-after-breakglass-created-at-required`,
- the canonical breakglass examples carry that field,
- and the nearby attestation/breakglass/runbook docs continue to teach that ordinary resumption requires a fresh `attestation.receipt` issued after breakglass receipt `created_at`.

## What stays open

This cut does **not** settle:

- whether a later denied ordinary action should get its own dedicated “post-breakglass stale-attestation” event/receipt,
- every future authority lane that might eventually consume `attestation_verification`,
- or how UX should best present “ordinary authority blocked pending fresh post-breakglass attestation” in each product shape.

It only makes one narrow decision now:
**breakglass stays explicit and bounded, and ordinary attestation-gated authority only resumes on fresh post-breakglass attestation evidence.**

The next coherence cut now exists too: `docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md` makes the phrase “relevant breakglass receipt” exact by requiring `relevant_breakglass_receipt_digest` on ordinary secret/identity receipts whenever breakglass materially formed the resumption barrier.
Last updated: 2026-03-21r380
