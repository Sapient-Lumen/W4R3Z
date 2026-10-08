# Data minimization and purpose-bounded verification routing

This note answers the question that comes **after** a tax, credit, rebate, or controller-side duty looks morally targeted but **before** its proof path can count as legitimate: **is the system asking for more data, retention, or matching than the rule's moral object actually requires?** The archive's stable answer is to collect the **narrowest workable claim**, reuse facts already proved elsewhere where possible, escalate to cross-system matching only for named high-stakes purposes, and block designs that need routine raw sensitive data or open-ended retention to function at all.[S1][S16][S17][S23][S27][S39][S40][S41][S44][S89][S91][S92]

A tax can be progressive in rates and still unjust in proof architecture. Repeated document harvest, full-attribute defaulting, and quiet administrative data-lake growth are not neutral implementation details; they change who can comply, who is excluded, and how much domination the state or a platform can exercise through tax administration.[S23][S27][S39][S40][S41][S44][S89][S91][S92]

## Default lanes

| Situation | Default proof path | Why this path usually wins | Main warning |
|---|---|---|---|
| Ordinary low-value credits, filing distinctions, routine rebates, or recurring support renewals | self-attestation, sampled audit, or simple threshold confirmation | routine universal document harvest often costs more than the moral value of proving every case up front | do not suppress lawful take-up by turning small recurring claims into a document maze.[S27][S64][S65][S66][S91] |
| Rules that really need only a band, threshold, or yes/no condition | binary or banded claim rather than full raw attributes | many tax and transfer rules do not need the whole dossier to answer the operative question | do not ask for full birth dates, diagnoses, or detailed histories when a narrow banded answer would do.[S91][S92] |
| Facts already verified elsewhere inside government or through a trusted provider | reusable credential, event confirmation, or narrow assertion | one-time proof plus narrow reuse reduces burden, storage, and repeat exposure | reusable credentials still need logging, revocation, and correction so convenience does not harden into lock-in.[S89][S91][S92] |
| High-value, fraud-sensitive, or cross-system inconsistency review | purpose-bounded matching with field minimization, logging, and time limits | higher stakes can justify more searching verification than routine claims can | do not let targeted matching turn into a standing administrative data lake.[S39][S40][S41][S44][S89][S91][S92] |
| Controller-side AI, platform, or large-firm obligations | structured event records and narrow operational assertions tied to the liability | large actors can bear richer reporting, but the state still needs only the fields relevant to control, base, threshold, or harm | technical visibility into the stack is not permission to ingest every raw trace indefinitely.[S10][S15][S16][S17][S39][S40][S41][S44][S89] |

## Routing rules

### 1. Ask for the smallest morally sufficient fact

Proof architecture should follow the moral object of the rule. If the rule turns on a threshold, status, timing event, or narrow measured base, the state should usually ask for that fact or band directly rather than the full surrounding file.[S1][S23][S27][S91][S92]

### 2. Reuse once-proved facts before recollecting raw documents

If identity, residence, payroll receipt, controller role, or similar facts have already been verified, later tax and relief channels should usually consume a narrow credential, event record, or signed assertion instead of recollecting the underlying documents from scratch.[S27][S39][S44][S89][S92]

### 3. Treat sensitive attributes as firewall material, not default inputs

Disability detail, migration history, nationality, family-status detail, biometrics, and similar intimate or protected-status-adjacent data require extra justification. Where a narrower proxy, threshold confirmation, or credential can do the work, the richer attribute should stay out of routine tax processing.[S17][S23][S40][S44][S74][S91][S92]

### 4. Escalate to matching only when stakes justify it and the purpose stays bounded

Cross-system matching can be morally justified where the public stakes are high, fraud patterns are serious, or the amount at issue is large enough to justify more invasive verification. But the archive treats matching as an escalated lane, not a default: it should be field-minimized, logged, time-limited, correctable, and tied to a named tax purpose.[S39][S40][S41][S44][S89][S91][S92]

### 5. Redesign or block rules that need excess collection to function

If a proposal only works by demanding raw sensitive data, repeated proofing, broad scraping, or indefinite retention materially wider than the tax or relief purpose, the archive treats that as a design failure. The right response is usually redesign, narrower proxies, or a different instrument, not a privacy footnote.[S16][S17][S39][S40][S41][S44][S89][S91][S92]

## Five anti-patterns

1. **Show-me-everything administration** — full files are demanded because systems can store them, not because the rule morally needs them.  
2. **Same-proof-again syndrome** — people and small firms must re-prove the same fact across filing, correction, and relief lanes.  
3. **Sensitive-attribute defaulting** — intimate or protected-status-adjacent data becomes routine when a threshold claim or credential would do.  
4. **Silent matching creep** — targeted verification quietly becomes broad ongoing matching and retention.  
5. **Raw-trace exceptionalism for AI** — because controller-side systems emit abundant telemetry, the administration assumes it may ingest the whole stack.[S16][S17][S39][S40][S41][S44][S89][S91][S92]

## Compression rule

If a proposal mainly fails because **it asks for too much data**, **re-proves what is already known**, or **defaults to sensitive attributes where narrow claims would do**, route through this card and the relevant administration or filing-parity note rather than writing a new sector-specific doctrine.

## Use with

- [`administration-explanation-and-appeal-routing.md`](administration-explanation-and-appeal-routing.md)
- [`compliance-burden-and-filing-parity-routing.md`](compliance-burden-and-filing-parity-routing.md)
- [`collection-and-remittance-routing.md`](collection-and-remittance-routing.md)
- [`automaticity-and-claim-friction-routing.md`](automaticity-and-claim-friction-routing.md)
- [`../20-calibration/data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md`](../20-calibration/data-minimization-credential-reuse-and-sensitive-attribute-firewall-ladder.md)

[S1]: ../../SOURCES.md#S1
[S10]: ../../SOURCES.md#S10
[S15]: ../../SOURCES.md#S15
[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S23]: ../../SOURCES.md#S23
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S40]: ../../SOURCES.md#S40
[S41]: ../../SOURCES.md#S41
[S44]: ../../SOURCES.md#S44
[S64]: ../../SOURCES.md#S64
[S65]: ../../SOURCES.md#S65
[S66]: ../../SOURCES.md#S66
[S74]: ../../SOURCES.md#S74
[S89]: ../../SOURCES.md#S89
[S91]: ../../SOURCES.md#S91
[S92]: ../../SOURCES.md#S92
