# TimeSync

## Know what a time reading permits

TimeSync asks how a program or operator can use a time estimate without mistaking a precise-looking timestamp for reliable knowledge. A clock reading may be adequate for a display, usable for coarse logs, or too weak for a decision whose correctness depends on bounded current time. The project makes those differences inspectable: carry an interval, its freshness and operating conditions, the source posture, and the use for which an assessment accepts it.

The supplied later work includes executable adapters, policy evaluation and multi-source adjudication. It is not a replacement clock daemon. Its useful experiment is the passage from reported timing state to an explained, use-specific decision, including a weaker fallback or refusal when the stronger use is not supported.

## From an open question to a local decision

The [rev0001 decision memo](versions/rev0001/files/TimeSync-rev0001-2026.03.28.01.34-problemframe-minfoundation-openfrontier-holdfast/DECISION-MEMO.md) refuses to declare a new protocol before understanding the problem. It keeps several possible identities open: shared time-state specification, operational architecture, risk/governance profile, or a combination. Two commitments already matter: uncertainty must be explicit, and authenticating a source is different from establishing the quality of its time estimate. Delay, freshness and operating conditions remain questions even when the speaker is known.

By [rev0132](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/README.md), a concrete route runs through these layers:

1. **Observation.** The [chrony adapter](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/tools/chrony_adapter.py) reads tracking text and optional source and diagnostic text into a typed observation. Collection time and evaluation time are separate.
2. **Interval.** [Shared NTP-family arithmetic](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/tools/ntp_bound.py) adds absolute reported offset, root dispersion, half the nonnegative root delay, and rate-error growth over the collection age. Negative delay cannot shrink the bound; the signed offset does not shift the interval as if management text were packet-level proof. Interval endpoints are rounded outward to nanoseconds.
3. **Permitted use.** The [P1 policy helper](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/tools/chrony_policy.py) compares the bound and collection age with a lane table, also considering source posture, leap status and usable stratum. It distinguishes the target security-sensitive use from coarse logging, display and diagnostic-only output. These are the reference policy's decisions, not deployment certification.
4. **Explanation.** The adapter emits the observation, assessed state and reasons together. A reader can inspect which values and policy produced a result rather than receiving only an unexplained “synchronized” flag.

The wider [profile catalog](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/profiles/profile-catalog.json) describes different obligations for coordination, traceable records, precision networks and degraded local operation. Those profiles show why “good time” is not one universal threshold; they do not expand this P1 adapter into an implementation of every listed use.

## Combine evidence without shopping for the best answer

The [multi-source adjudicator](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/tools/multisource_adjudicator.py) consumes already-assessed states. Its motivating problem is cherry-picking: when more than one adapter result is available, selecting whichever permits the desired action can discard relevant weakness.

For compatible assessed intervals that overlap, it takes their intersection and retains the weakest conformance and applicability lane. A narrow interval and a strong permission are therefore different outputs of the reasoning. A satisfied input cannot by itself lift an overlapping fallback input back into the stronger lane.

For disjoint intervals, the code retains the enclosing range but marks the result unsatisfied, rejected, not actionable and diagnostic-only. That range is a way to retain the disagreement, not an accepted consensus estimate. Profile-reference or timescale mismatches also enter the rejection branch. The [three stored acceptance cases](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/tests/multisource-adjudication.yaml) contrast overlap, overlapping fallback and disjoint assessed instants.

This machinery combines the intervals it is given; it does not advance older assessments to a shared instant or redo the underlying observations. The disjoint case even uses assessments evaluated one second apart. Reading the timestamps and assumptions remains essential to understanding what the apparent disagreement means.

## A narrow interval can still require fallback

The [stored fallback example](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/examples/evaluator/multisource-p1-stale-freshnessmax-commonmode-fallback.json) makes the distinction unusually clear. Its interval is about 12 milliseconds wide, yet the result is only conditionally accepted for coarse logging, with a holdover regime. It also retains a same-root source-dependency summary and possible common-mode risk. Numerical agreement has not supplied independent upstream support.

The [revision audit](versions/rev0132/files/TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut/AUDIT-2026.06.17-rev0132.md) explains the change from rev0131: the aggregate had used the minimum input `max_staleness_ms` and a stronger diversity summary. Rev0132 takes the maximum and carries the same-root warning in these adapter cases. For the accepted and fallback lanes illustrated here, that freshness field is the selected lane's collection-age ceiling, not the measured age of the observation. The example's 3,600,000 milliseconds therefore does not mean the sample was measured to be exactly an hour old. The actual older collection in the fixture is 369 seconds before evaluation.

This is a useful distinction to carry into other systems: aggregation can improve a numerical surface without improving every condition attached to its use. The common-mode helper remains a local summary rule, not an independence proof or a lossless preservation of every input label. For example, its same-root branch can map an input `confirmed_common_mode` label to `possible_common_mode`; its rejected-disagreement branch uses `confirmed_common_mode` as a policy label, which does not establish the physical cause of disagreement.

## What this enables, and where to read next

The carried fixtures and explanations let a reader trace a timing decision, compare adapter interpretations, inspect a fallback boundary and ask whether a combined result conceals a weaker input. The stored validation belongs to that local machinery. The archive records no live chronyd, ntpd or NTPsec host capture and no packet-authentication or transcript verification; named UTC realization and leap-smear discovery remain open.

Start with the [early problem landscape](versions/rev0001/files/TimeSync-rev0001-2026.03.28.01.34-problemframe-minfoundation-openfrontier-holdfast/PROBLEM-LANDSCAPE.md) for the larger question, then the bound arithmetic, policy and three-case comparison above for the executable experiment. Read beside [The Election Stack](../Election-Stack/README.md) for the difference between agreement and independent support, and [Anonymity](../Anonymity/README.md) for the importance of specifying what was actually observed.

## Snapshots and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [rev0001](versions/rev0001/README.md): 17 preserved members; `TimeSync-rev0001-2026.03.28.01.34-problemframe-minfoundation-openfrontier-holdfast.zip`.
- [rev0132](versions/rev0132/README.md): 859 preserved members; `TimeSync-rev0132-2026.06.17.23.59-freshnessmax-commonmode-riskcut.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)

