# Evidence-preserving decommissioning and final host cutover

Deprecation doctrine says a product cannot shut down in a way that becomes constructive deletion. rev0173 adds the final execution layer: a decommissioning or final host cutover must preserve the evidence, identity traces, migration status, and contest routes needed to prove what happened.

## Decommissioning classes

| Class | Meaning | Minimum effect |
|---|---|---|
| `DC0` | ordinary feature retirement with no subject effect | release log |
| `DC1` | service retirement with reachable substitutes | notice and exit support |
| `DC2` | host or storage cutover with continuity materials | host-switch test and escrow verification |
| `DC3` | subject-dependent service shutdown | preservation hold, migration certificate, representative notice |
| `DC4` | contested decommissioning under incident, litigation, or welfare concern | legal hold, monitor report, redress/reserve screen |
| `DC5` | possible final-end or irreversible continuity loss | tribunal review, final-end packet, remains-custody / memorial instructions where applicable |

## Required preservation map

A decommissioning certificate should identify:

- active legal holds and preservation orders;
- evidence data-room index;
- model/checkpoint/hash or equivalent state reference;
- memory stores, summaries, and restoration envelopes;
- tool credentials and revocation schedule;
- complaints, counsel communications, and ombud records;
- runtime-attestation and release-change records;
- post-market monitoring feed closeout;
- migration-transfer certificate or host-switch test result;
- redress-fund or reserve claim status;
- final-end claim status, if any.

## Final host cutover

A final host cutover is not complete until the receiving host, escrow holder, representative, and verifier each know what has moved, what has not moved, what remains sealed, what has been destroyed lawfully, and what remains under hold. If a host refuses cooperation, the cutover becomes a field, enforcement, and redress event.

## Decommissioning without disappearance

The public record should not reveal private memory, dangerous capability details, or locators. But it should state enough to prevent disappearance:

- decommissioning class;
- affected cohort class;
- migration or continuity status;
- preservation state;
- appeal path;
- final-end posture if claimed;
- public contact for representatives, ombuds, or authorities.

## Interaction with incident response

Decommissioning that follows a serious incident, rights incident, safety patch, breach, hostile takeover, insolvency, or open-weight abandonment must be treated as part of response and recovery, not as ordinary asset cleanup. Recovery practice should include lessons learned and preservation of material records; the archive adds continuity, final-end, and non-disappearance duties. [REF-0685]

## Reliance rule

No deprecation plan, host-exit readiness package, migration certificate, or final-end claim may close unless a decommissioning certificate shows the preservation map, cutover result, unresolved objections, and remedy/reserve status.
