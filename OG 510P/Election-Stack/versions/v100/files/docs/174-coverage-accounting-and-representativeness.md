# 174 — Coverage Accounting & Representativeness (Verification Ecosystem)

**Track:** A (Deployable core)

## Why this exists
Attackers often win by corrupting the *verification ecosystem* rather than the tally.

Two classic failure modes:
1. **Challenge grinding:** only “easy” challenges are issued or publicized.
2. **Selective blindness:** some audiences never see missed challenges, suppressed reports, or inconsistent views.

This doc makes “your monitoring isn't representative” a measurable claim: coverage becomes a publishable, auditable artifact.


## CoverageReport as evidence
Coverage is published as a signed `EvidenceEnvelope` of kind `hfv.coverage.report` with payload schema `schemas/CoverageReport.json`.

- In Track A, coverage reports are **public artifacts** and are mirrored like results objects.
- Missed challenges generate `InspectionSuppressionReport` envelopes and MUST be counted in coverage metrics.

## Coverage model (minimal)
Define three sets:

- **Targets:** what should be observed (jurisdictions, endpoints, logs, artifacts).
- **Perspectives:** from where (network vantage points, orgs, regions, political diversity).
- **Time:** when (rounds, deadlines, maximum merge delay, election phases).

Coverage is a function:

`coverage = f(targets, perspectives, time, artifact_types)`

### What must be published
A monitor or watcher SHOULD publish:
- the **ChallengeSchedule** (deterministic sampling inputs),
- the **ChallengeQuotaPolicy** (expected minimum coverage),
- and a **CoverageReport** (what was actually challenged/verified).

## Deterministic sampling (anti-grinding)
Sampling must be tied to public randomness, not operator preference.

Recommended sources:
- NIST randomness beacon (public, auditable) or
- a distributed beacon like drand (public, verifiable chain).

See: `docs/168-public-randomness-beacons-and-seeded-sampling.md`.

## CoverageReport (deliverable)
A CoverageReport is a signed statement (preferably an EvidenceEnvelope) that includes:
- period (start/end; round ids),
- target set definition,
- actual challenges issued (digests),
- missed deadlines and suppression proofs,
- and simple metrics (below).

### Simple metrics (start here)
- **Target coverage:** % of targets touched at least once per window.
- **Temporal coverage:** max gap between challenges per target.
- **Perspective coverage:** number of independent orgs/vantage points that confirmed the same artifact.
- **Suppression rate:** % of challenges with missed deadlines.

## Tooling (toy but executable)
- `tools/coverage_accounting.py` reads a small JSONL event log and produces:
  - `artifacts/coverage/coverage_report_example.json` (example)
  - a markdown summary suitable for publication.

This is intentionally a toy model to prevent analysis paralysis. The point is to institutionalize *coverage accounting* early.

## Links
- CT-style auditing depends on promises within deadlines and checking behavior over time. (Certificate Transparency v2) 
- Gossip is a standard split-world defense pattern.

(See external pins in `evidence/lock/external-sources.toml`.)


## Publication coverage (v46)

Coverage is not only about inspection challenges. The archive now also supports publication compliance coverage (docs/187): TriggerEvents + PublicationContract rules produce a PublicationCoverageReport, and missed deadlines can be turned into portable suppression reports.
