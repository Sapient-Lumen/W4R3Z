# 187 — Publication compliance and coverage (from promises to measurable outcomes)

**Track:** A (Deployable core)

This project assumes attackers may win by **corrupting the verification ecosystem** rather than the tally:
they delay, suppress, or selectively disclose evidence and communications so different audiences see different realities.

Docs/181 introduces *PublicationContract* (promises). This doc adds a minimal mechanism to make those promises
**measurable** and to make "missingness" both provable and mirrorable.

## Core objects (new)

1) **PublicationTriggerEvent** (`hfv.publication.trigger_event`)

A signed/gossiped declaration that a deadline trigger occurred at a specific time.
It is a *deadline anchor* that can be mirrored and audited.

Payload schema: `schemas/PublicationTriggerEvent.json`

Typical issuers:
- operator (declared incident, polls open/close, ENR generation start)
- watcher/monitor (observed incident, detected deadline breach, detected rumor/attack)

2) **PublicationCoverageReport** (`hfv.coverage.publication_report`)

A computed report that summarizes (for a time window) whether required publications occurred on time
for each contract rule, given a set of TriggerEvents.

Payload schema: `schemas/PublicationCoverageReport.json`

This report is itself a public evidence artifact and is (per registry) **receipted + gossiped**.

## How compliance is computed (reference semantics)

Given:
- a `PublicationContract` (docs/181),
- a set of `PublicationTriggerEvent`s,
- the set of published `EvidenceEnvelope`s,

then for each TriggerEvent and each contract rule with a matching trigger_id:

- compute: `deadline = occurred_at + max_delay_seconds`
- satisfied iff there exists at least one envelope of the rule's `kind`
  with `issued_at` in `[occurred_at, deadline]`

This is deliberately simple:
- it avoids fragile semantic coupling early (v0),
- it is enough to measure **selective delay** and **selective omission** in practice.

Future work can strengthen linkage (e.g., requiring PublicNotices to cite the event_id).

## Public notices and narrative integrity

Public communications are evidence objects (docs/186).
To make narrative suppression measurable, jurisdictions SHOULD:

- include a contract rule for `hfv.public.notice` triggered by `incident_declared`,
- publish a TriggerEvent when an incident is declared or detected,
- publish a PublicNotice within the contract delay,
- publish a PublicationSuppressionReport if the deadline is missed.

This turns "they didn't tell us" into a portable, cryptographically bound statement.

## Tooling (stdlib-only reference)

`tools/publication_compliance.py` computes a PublicationCoverageReport from an evidence packet directory:

```bash
python tools/publication_compliance.py artifacts/examples/evidence_packet_publication_compliance_minimal
```

This tool is intentionally conservative: it treats `issued_at` as publication time and checks for existence.

Operator helper (bounded card, copy/pasteable):
- `python3 tools/publication_coverage_report_card.py --packet <packet_dir>`

## Anti-gaming notes

- TriggerEvents MUST be receipted + gossiped (registry) to prevent **suppression of the anchor**.
- Multiple issuers are expected; conflicting TriggerEvents are *useful evidence* and should not be normalized away.
- Coverage reports should be published by multiple watchers; "watchers inspecting monitors" is a core stance.
- Where suppression of publication evidence is suspected, independent watchers SHOULD also publish receipted+gossiped **LivenessBeacons** (`hfv.coverage.liveness_beacon`, docs/210) that record reachability and observed digests for the public pointer surfaces.

## Related docs

- docs/181 — PublicationContract and deadline breach proofs
- docs/184 — Trigger vocabulary registry (drift firewall)
- docs/186 — Incident communications as evidence (PublicNotice)
- docs/174 — Coverage accounting and representativeness
