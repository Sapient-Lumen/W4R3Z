# Transparency monitors and witness gossip

Transparency logs are only useful if someone actually **watches them**.

DeriveBSD already models transparency as optional evidence (`export.transparency.entry`, `release.transparency.entry`, and `transparency.proof`). This document makes the *operational half* explicit: monitors, witnesses, and gossip.

## Problem

Without monitoring:
- A malicious (or buggy) publisher can log unexpected artifacts and no one notices.
- A log can present **split views** to different clients (consistency failures go undiscovered).
- Clients that rely on “log lookup” for verification are forced online at exactly the wrong time.

## Lessons to steal

- **“Bundle verification”**: sigstore/cosign explicitly supports verifying inclusion without contacting the log by using a bundled proof artifact (a “bundle” annotation). This pattern matches DeriveBSD’s evidence model and is friendly to incident response and offline environments.
- **Witness networks + checkpoint cosigning**: a witness cosigns checkpoints only if consistent with what it previously signed. This makes split-view attacks harder and turns “monitor diversity” into a security parameter.
- **Production monitors**: sigstore-style monitors are becoming a practical, productized workflow (e.g., rekor-monitor work to detect tampering and unauthorized uses).

## DeriveBSD design

### New first-class objects

- `log.checkpoint.receipt` (witness-cosigned checkpoint bundle)
  - schema: `spec/log.checkpoint.receipt.schema.json`

- `transparency.monitor.policy`
  - which log(s) to watch
  - what entries to consider “in scope” (export, release, or both)
  - what constitutes a policy violation
  - required witness cosignature quorum (optional)
  - how to emit alerts (as evidence, not just pages)

- `transparency.monitor.snapshot`
  - last verified checkpoint / tree size
  - last verified time
  - last processed entry index
  - local state digest (so monitors can be replaced without losing continuity)

- `transparency.monitor.alert.event`
  - policy violation / consistency failure / split-view suspicion
  - minimal evidence pointers to reproduce the claim (checkpoint(s), proofs, offending entry digest)
  - optional “suggested actions” (halt rollout, freeze exports, rotate keys)

### Monitor roles

Keep roles explicit (least authority):

1) **Consistency monitor**
   - verifies checkpoint signatures
   - verifies consistency proofs between successive checkpoints
   - can be run by many independent parties

2) **Policy monitor**
   - validates new logged entries against a local expected policy set:
     - `release.authority.policy` (who is allowed to publish)
     - `export.policy` / `bundle.plan` constraints
     - metadata minimization rules

3) **Witness client** (optional)
   - fetches a checkpoint
   - validates it against previous signed checkpoints
   - cosigns if consistent

### How alerts integrate

- Alerts are **typed events** in the structured event log (and therefore attachable to incident bundles).
- Rollout halt conditions may reference monitor alert events (e.g., “halt on any `split_view_suspected` within last N hours”).
- Export policies may require “monitor clean” gates before allowing `public` class exports.

## Policy defaults (greenfield ergonomics)

- The default client verification flow prefers bundled proofs:
  - accept `transparency.proof` with inclusion+checkpoint (+ optional witness cosigs)
  - optionally refresh from the log only when policy demands it

- Make monitor diversity cheap:
  - allow multiple monitors with different operators
  - allow witness quorum thresholds to be tuned per channel

## Related docs

- `docs/254-export-transparency-logs.md`
- `docs/257-release-capsules-and-transparency.md`
- `docs/187-witnessed-transparency-checkpoints.md`
- `docs/253-bundle-plans-and-deterministic-exports.md`
