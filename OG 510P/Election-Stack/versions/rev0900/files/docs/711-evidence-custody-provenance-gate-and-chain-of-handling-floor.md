# 711 — Evidence custody/provenance gate and chain-of-handling floor

**Track:** Shared / Release maintenance + Track A pilot readiness

## Purpose

v836 adds a custody/provenance gate for a failure mode the archive could still understate: a packet can verify offline, pass redaction review, pass accessibility/language review, and still be unsafe to treat as field evidence if nobody can show who captured it, who handled it, what changed hands, who accessed private fields, where public derivatives came from, and how the material was sealed, retained, or disposed.

This is a release-safety control, not a chain-of-custody certification. It does not decide court admissibility, public-records duties, legal sufficiency, live authorization, current voter instructions, or election outcome correctness.

## New artifacts

- `artifacts/registries/evidence-custody-provenance-policy.csv` defines 14 policy rows for capture scope, collector role, capture environment, digest lineage, custody transfer, access logs, sealed/private material, public derivative lineage, incident freeze, offline drill transcript custody, source-review custody, chain-gap/dissent handling, retention/disposition, and the gate itself.
- `artifacts/templates/evidence-custody-provenance-worksheet.md` records capture authorization, tool/version/time-source facts, digest lineage, transfer records, access windows, public/private separation, and disposition decisions.
- `artifacts/checklists/evidence-custody-provenance-checklist.md` gives release maintainers a short stop/go path for custody records.
- `tools/evidence_custody_provenance_pack.py` generates the deterministic matrix, burndown, preview index, and no-go notice.
- `scripts/check_evidence_custody_provenance_pack.py` fails the release if the generated pack drifts, loses non-claim language, or forgets the synthetic/no-go boundary.

## Release decision

The current synthetic release decision is:

```text
NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE_INCOMPLETE
```

Synthetic examples may ship, but live-pilot or local public-release reliance should not proceed until applicable custody rows have local evidence or documented exceptions.

## What this prevents

- Treating a digest-valid packet as live field evidence without capture authorization.
- Losing the collector, tool version, time source, or vantage point behind a snapshot.
- Transferring evidence without pre/post digest continuity.
- Publishing a public derivative whose source evidence and redaction rule cannot be traced.
- Hiding chain gaps, reviewer dissent, or unresolved exceptions behind a passing verifier report.
- Treating an offline drill as operational evidence without preserving the transcript, ZIP digest, verifier role, and manifest result.
- Destroying, sealing, returning, or retaining evidence without a digest, owner, date, rule pointer, and legal-hold status.

## Public-language rule

A public reader should be able to distinguish three different statements:

1. “These bytes verify against the manifest.”
2. “These bytes were handled under a documented local custody process.”
3. “A court or local authority accepts the custody record for a legal purpose.”

v836 only makes the second statement visible as a missing local-evidence requirement. It does not make the third statement.

## Gate integration

The new gate is wired into:

- `artifacts/registries/pilot-operational-invariants.csv`
- `artifacts/registries/release-go-no-go-criteria.csv`
- `artifacts/registries/release-maintainer-handoff.csv`
- `artifacts/registries/local-pilot-intake-requirements.csv`
- `artifacts/registries/standards-crosswalk.csv`
- `tools/local_pilot_intake_pack.py`
- `tools/release_maintainer_handoff_pack.py`
- `tools/release_go_no_go_pack.py`
- `scripts/release_gate_steps.py`

## Non-claims

This release does not certify chain of custody, court admissibility, public-records compliance, privacy compliance, live authorization, or election outcome correctness. It only makes custody/provenance records visible as a required gate before live evidence reliance.
