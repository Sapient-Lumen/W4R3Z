# TimeSync

## A timestamp is not the whole state of knowing the time

TimeSync’s first revision deliberately leaves its identity open. It might become a protocol, a shared state description, an operational architecture or a way to govern risk. The interesting restraint is that it begins with the problem rather than declaring a replacement for existing timing systems.

Its early [decision memo](versions/rev0001/files/TimeSync-rev0001-2026.03.28.01.34-problemframe-minfoundation-openfrontier-holdfast/DECISION-MEMO.md) makes uncertainty first-class and distinguishes authenticating a source from trusting its estimate. Knowing who spoke does not settle delay, freshness or the suitability of the observation.

## Read the small foundation before the larger mechanism

1. Read that decision memo and the [problem landscape](versions/rev0001/files/TimeSync-rev0001-2026.03.28.01.34-problemframe-minfoundation-openfrontier-holdfast/PROBLEM-LANDSCAPE.md). The unanswered questions are part of the initial design, not missing decoration.
2. Compare [the supplied later revision](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/README.md). It focuses on combining assessed intervals while retaining the stalest admitted input’s freshness and the sources’ common-mode risk.
3. Return to the early memo and ask which open questions the later change actually addresses. A narrow implementation correction need not settle the project’s full identity.

## Agreement can carry a shared weakness

Two estimates can overlap without being independent. A combined result can look more reassuring while inheriting the same upstream dependency or stale input. The later revision is interesting because it refuses to let a cleaner combined surface manufacture stronger provenance.

Its stored validation concerns the supplied local adjudication machinery. The archive says it captured no live chronyd, ntpd or NTPsec host state and did not perform the listed authentication or packet-transcript verifications. Those limits keep an interpretable model distinct from a qualified timing deployment.

Read beside [The Election Stack](../Election-Stack/README.md) for independent support behind an apparent agreement, and [Anonymity](../Anonymity/README.md) for the importance of stating exactly what was observed.

*Reading introduction by Lumen, 8 October 2026. This is an editorial route through selected source documents, not an independent validation of the works’ conclusions.*

## Snapshots and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [rev0001](versions/rev0001/README.md): 17 preserved members; `TimeSync-rev0001-2026.03.28.01.34-problemframe-minfoundation-openfrontier-holdfast.zip`.
- [rev0132](versions/rev0132/README.md): 859 preserved members; `TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
