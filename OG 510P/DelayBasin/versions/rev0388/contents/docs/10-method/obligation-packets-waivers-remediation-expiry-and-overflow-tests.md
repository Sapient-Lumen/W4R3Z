# Obligation packets, waivers, remediation, expiry, and overflow tests

This is the compact successor surface for `OQ-0110`.

DelayBasin already had a compact `obligation_witness` object and a controlled `obligation_state` family, but one practical gap kept recurring in durable rows:
later careful passes could still agree that support was not fully discharged and yet blur together **still-owed support**, **temporarily waived support**, **suppressed aggregate judgment**, **ordinary remediation planning**, and **already-retired debt**.
When those relations stay ambient, the archive has an obligation witness on paper but not yet as an easy successor surface for future reuse.

The compact repair is:
**preserve one explicit obligation packet that says the existing admitted obligation witness is already the right bounded place to keep support-debt truth public, while leaving waiver rationale, compensating controls, remediation milestones, expiry details, and aggregate-score consequences in surrounding prose.**

This does **not** justify an exception court, waiver senate, or standing debt-governance board.
It only resolves the missing compact successor surface for a witness family DelayBasin already admitted.

## Practice / observation

DelayBasin's obligation rows already preserve target surface, missing support, current support, discharge path, obligation state, and repair.
That was enough to stop many tolerated moves from dissolving into vague future-work prose.
But a smaller gap remained:
- some later rereads still had to recover whether a row was **open support debt** or an explicit **waiver** with bounded acceptance;
- some had to recover whether a row was still owed support at all or whether surrounding systems had merely **suppressed** or excluded a finding from aggregate judgment;
- and some needed an explicit reminder that remediation plans, expiry windows, and compensating controls belong in surrounding prose rather than being silently collapsed into the state token itself.

So the archive did not need a new debt family first.
It needed one compact packet that says the existing witness is already the right public place to preserve **owed-support core truth**.

## External pressure from exemptions, remediation exceptions, POA&Ms, and status-check systems

Current policy, compliance, and release systems repeatedly separate temporary acceptance, remediation planning, and aggregate judgment.

1. Azure Policy exemptions document explicit exemption categories such as **Mitigated** and **Waiver**, support an `expiresOn` field, and keep expired exemptions for record-keeping even after they are no longer honored. That pressures DelayBasin to keep waiver posture explicit without pretending that expiry or mitigation details belong inside one compact state token. ([`REF-0820`](../00-meta/bibliography.md))

2. AWS Config remediation exceptions document an explanation for the exception, an expiration time, and the rule that auto-remediation stays blocked until the exception is cleared. That pressures DelayBasin to keep explicit support debt distinct from surrounding remediation and exception-management prose. ([`REF-0821`](../00-meta/bibliography.md))

3. NIST SP 800-171r3 requires plans of action and milestones to document planned remediation actions and to update them based on assessments, audits, reviews, and continuous monitoring. That pressures DelayBasin to keep remediation-plan detail adjacent to obligation rows rather than silently treating a plan itself as discharged support. ([`REF-0822`](../00-meta/bibliography.md))

4. GitHub required status checks distinguish passing states from checks that remain **Pending** and block merging when a skipped workflow leaves the required check pending. That pressures DelayBasin not to confuse still-unfinished validation or blocked execution with a satisfied or waived obligation state. ([`REF-0823`](../00-meta/bibliography.md))

5. AWS Security Hub derives control status while ignoring `SUPPRESSED` findings and treating all-suppressed cases as **No data**. That pressures DelayBasin not to confuse aggregate suppression or unavailable data with a real waived-or-satisfied support debt. ([`REF-0824`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **obligation packet / owed-support core** on durable support-debt rows, and the admitted family should stay **target surface**, **missing support**, **current support**, **discharge path**, **obligation state**, and **repair** with the controlled state tokens **`open`**, **`staged`**, **`satisfied`**, **`waived`**, and **`retired`**. Use **`waived`** only when the debt is explicitly tolerated or compensatingly accepted. Keep waiver rationale, mitigation method, remediation milestones, expiry windows, and any suppression-from-aggregate or no-data consequences in surrounding prose. Keep the core narrow. Extend only explicitly and fail closed on drift.

## Obligation core vs waiver vs suppression vs followthrough

This distinction is the heart of the successor surface.

- **obligation packet core** says what support is still owed and what row currently carries that debt.
- **waiver** says the debt is explicitly tolerated for now under bounded acceptance.
- **suppression or no-data posture** says aggregate judgment is being hidden, excluded, or is currently unavailable; it does **not** by itself discharge the debt.
- **remediation planning** says what work is intended to reduce the gap; it does **not** by itself satisfy or waive the row.
- **followthrough** says what remainder work is queued, handed off, or blocked; it does **not** replace the owed-support core.

A row can be obligation state `open` while remediation planning exists.
A row can be obligation state `waived` while expiry and compensating-control details stay in prose.
A row can be obligation state `open` even when some neighboring dashboard suppresses or omits the aggregate score.

So the packet does not add a new court.
It only makes the already-admitted separation easier to reopen honestly.

## Countermodels / probes

1. **Existing obligation rows are already enough countermodel**
   - Maybe the current witness object already preserves every practical distinction without a successor packet.
   - Probe: compare later rereads on rows with equally careful obligation prose and inspect whether operators still blur owed support, waived support, and suppressed aggregate posture when the compact packet is not foregrounded.

2. **Waiver detail belongs inside the state token countermodel**
   - Maybe the archive should mint richer state tokens for mitigated, suppressed, pending, or expired posture.
   - Probe: keep those details in prose first and inspect whether the current controlled family remains sufficient once the compact packet says what stays inside versus outside the token.

3. **Remediation-plan-is-enough countermodel**
   - Maybe a plan, milestone list, or followthrough row already says everything an obligation packet needs.
   - Probe: inspect whether later passes can distinguish still-owed support from merely planned repair without the compact packet.

## Design consequences

- keep the controlled `obligation_state` family unchanged in `WITNESS-VOCABULARY.json` for now;
- use the packet only on governed durable support-debt rows that already carry the existing obligation witness fields;
- preserve one compact successor surface for the family so later passes can reopen owed-support truth directly;
- keep waiver rationale, compensating controls, expiry windows, suppression posture, and remediation milestones outside the token itself;
- and quarantine any stronger exception court, waiver senate, or debt-governance board unless repeated overflow shows that one compact packet is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact packet is no longer enough — for example, if the archive honestly needs standing waiver arbitration across many rows, durable expiry governance, aggregate-suppression policy, or a broader exception controller that cannot be expressed as one bounded obligation packet plus existing prose.

Until then, prefer this compact successor surface over an exception court, waiver senate, or debt-governance board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something slightly sharper than “this move still needs more support.”
It is also preserving **what part of the support debt is compactly comparable and what surrounding exception or remediation detail stays adjacent**.
That matters because later stateless passes can otherwise preserve the row and its caveats yet still misread whether the archive is seeing an owed debt, a temporary waiver, a suppressed aggregate, or a remediation plan.
