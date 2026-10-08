# 440 — Determination registers, waiver ledgers, and expiring deviations

## One-line thesis

Whenever a public AI team decides that a use case falls outside a stricter risk category, or waives a baseline safeguard, that choice should become a **numbered determination record** with scope, justification, evidence, owner, expiry, and a public-facing summary.

## Why this matters

Governance failures often enter through the side door. The dangerous moment is not always a dramatic incident; it is the quiet internal decision that a use case is “not really high-impact,” that a minimum safeguard can be skipped this quarter, or that an exception can stay in place indefinitely because delivery pressure is high. If those decisions remain informal, they become invisible precedent.

Recent U.S. federal compliance materials show a more disciplined direction. OMB Memorandum M-25-21 requires written documentation when agencies determine that a use case in a presumed high-impact category does not actually meet the definition, and agencies must update compliance plans, inventories, and related reporting. NARA’s 2025 AI compliance plan says waivers will be approached with utmost scrutiny, that the CAIO has sole non-delegable authority to issue them, and that waivers will be centrally tracked, certified annually, reported to OMB within 30 days, and publicly disclosed. The Federal Reserve’s 2025 compliance plan goes further by requiring documented scope, justification, and supporting evidence for granting or revoking a waiver, annual recertification for high-impact waivers, and public summaries of determinations and waivers.

The archive should turn that emerging practice into a broader pattern: **every deviation from the default control stack should leave an expiring record, not just a meeting memory**.

## Pattern pack

### 1. Create a determination register, not only case-by-case email chains

Maintain a single register for decisions such as:

- presumed-high-impact but determined not high-impact,
- waiver of a minimum safeguard,
- temporary exception to a publication or testing requirement,
- extension of a pilot under exception conditions,
- or acceptance of a residual risk above the normal floor.

Each entry should have a durable identifier.

### 2. Require a fixed minimum entry shape

Each determination or waiver record should state:

- the use case and system version,
- the specific control, category, or safeguard being deviated from,
- the reason for the decision,
- supporting evidence,
- the approving authority,
- the time period or expiry date,
- any compensating controls,
- and the trigger for automatic reconsideration or revocation.

### 3. Make deviations expire unless actively recertified

Exceptions should decay by default. A deviation that remains justified should be recertified after a defined period with fresh evidence and fresh sign-off. Otherwise it should lapse automatically.

### 4. Distinguish determination, waiver, and emergency stop-gap

Not all deviations are the same. The register should distinguish:

- **determinations** about category or scope,
- **waivers** of baseline requirements,
- **temporary operational accommodations** pending remediation,
- and **emergency stop-gaps** used to maintain continuity under incident conditions.

These categories should not borrow each other’s standards invisibly.

### 5. Publish a public summary even when full details must stay internal

Some supporting material may be security-sensitive or otherwise protected. But even then, a public summary should usually still state:

- that a deviation exists,
- what category of control was affected,
- when it was approved,
- who approved it by role,
- when it expires or will be reviewed,
- and what compensating controls were used at a high level.

### 6. Link the deviation ledger to inventories and public records

A determination or waiver should automatically update related records such as:

- public AI inventories,
- deployment registries,
- impact dossiers,
- system cards,
- and internal risk registers.

That prevents a public record from falsely presenting the system as fully baseline-compliant when it is operating under an exception.

### 7. Ban indefinite “temporary” status

A deviation that survives multiple review cycles without closure should be escalated as a governance issue. Long-lived temporary waivers are often just permanent policy drift in disguise.

## Guardrails

- No meaningful deviation without a durable record.
- Waivers should name an approving authority and an expiry date.
- Public summaries should exist unless law or security strictly prevents them.
- Compensating controls should be explicit, not assumed.
- Repeated recertification should trigger deeper review.

## Failure modes

- **shadow exception**: a safeguard is skipped in practice but no formal waiver exists.
- **permanent temporary**: an exception is repeatedly rolled over without real reconsideration.
- **category gaming**: a risky use case is declared out of scope without durable reasoning.
- **silent mismatch**: public records imply baseline compliance while internal ledgers show a live exception.
- **ownerless deviation**: a waiver persists after the approving team has moved on.

## Practical tests

A deviation-governance system passes when it can answer yes to all of the following:

1. Does every nonstandard determination or waiver receive a durable ID in a central register?
2. Does each entry include scope, justification, evidence, owner, compensating controls, and expiry?
3. Are deviations recertified or revoked on a schedule rather than quietly carried forward?
4. Is there a public-facing summary or a documented reason why none can be published?
5. Do related public records and inventories reflect the live exception state?

## Compression rule for the archive

If a public AI safeguard can be skipped without leaving an **expiring record**, it can usually be skipped too quietly.
