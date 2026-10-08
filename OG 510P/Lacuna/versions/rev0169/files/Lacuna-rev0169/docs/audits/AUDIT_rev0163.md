# Audit — rev0163

## Scope

This audit began from accepted rev0162 plus two rev0160 direct-upload companion artifacts. It asked whether the current system serves both intended recipients:

- a player who should be able to begin role-play without learning the protocol; and
- a researcher testing Gwern's compression/forgetting idea without using one contaminated long context as the narrator.

The audit covered post-checkpoint context flow, scenario treatment topology, state-card retention, direct-upload onboarding, capsule construction, final-step checkpoint observability, schemas, documentation, and regressions. Product/provider behavior remains outside the trusted kernel.

## Parent baseline

Rev0162 already supplied managed checkpoints, exact source-bound role cards, four-condition scenario children, preregistered multi-block bundles, delayed unblinding, and strong sidecar audit/recovery. Its role-separated condition required distinct checkpoint-role contexts but did not require the narrator after the checkpoint to be fresh or linked to the selected compressed state.

## Finding A163-01 — checkpoint-worker separation did not reset continuation

**Risk.** A cell could satisfy distinct generator/judge/compressor/verifier context IDs while the continuing narrator retained rejected candidates, rollout details, scores, and parent discussion. The recorded treatment would claim context separation without testing the information bottleneck.

**Repair.** Added `lacuna.checkpoint-narrator-capsule.v1`, `checkpoint run narrator-capsule`, and fresh narrator segment validation in `lacuna-role-separated`.

**Evidence.** Focused tests require commit, validate deterministic capsule content/digests, reject state-card/audience-context tampering, exclude rejected candidate/score/verifier strings, require exact capsule linkage, and refuse narrator context reuse.

## Finding A163-02 — control context policy was underdetermined

**Risk.** An operator could freshen a control or split a serial condition, erasing the contrast needed to attribute any effect to the bottleneck.

**Repair.** Added `continuation_mode`. Forward-only, prompt-only-retcon, and Lacuna-serial now require one persistent declared context for the whole cell. Role-separated requires one narrator context per segment and a fresh context after each completed checkpoint.

**Evidence.** Scenario tests refuse serial context drift and control-side capsule claims before any cell result is written.

## Finding A163-03 — a checkpoint could occur after the final rated turn

**Risk.** The default one-step capsule checkpointed after its only narration. A completed cell could execute expensive checkpoint machinery without any subsequent player-visible continuation influenced by that checkpoint. This weakens the experimental unit and makes the fresh-narrator claim vacuous.

**Repair.** Scenario capsules now require at least two script steps, reject `checkpoint_after` on the final step, and generate a default post-checkpoint continuation probe.

**Evidence.** A focused test receives `bad-scenario-capsule` and observes no run publication when the final step is marked as a checkpoint.

## Finding A163-04 — manual redaction was an avoidable leakage surface

**Risk.** The rev0160 helper copied selected fields from a committed sidecar, but a future parent could accidentally include candidates or judgment while constructing an ad hoc prompt.

**Repair.** The core capsule builder's signature has no candidate, judgment, or verifier inputs. It consumes only already-authenticated accepted objects and fixed digests.

**Evidence.** Unit tests search the canonical capsule for rejected candidate text, weighted-score fields, and verifier provenance; none is present.

## Finding A163-05 — state-card body retention was not prominent enough

**Risk.** The ledger can bind a state-card digest while the useful text remains only in the private checkpoint sidecar. A valid cube can therefore outlive the compact continuation guidance.

**Repair.** The capsule carries the exact body and digest. `OPERATE_LACUNA.md`, `FRESH_NARRATOR.md`, threat documentation, and direct-upload audit make retention explicit.

## Finding A163-06 — the direct-upload manual duplicated too much authority-looking prose

**Risk.** The 600 KB rev0160 manual embedded commands, product notes, generated CLI reference, helper programs, rehearsal evidence, and copies of repository docs. It was useful research material but a poor first entrance and likely to drift independently.

**Repair.** Added one short root operator guide and one focused fresh-narrator protocol. The large manual and host-specific utilities are not copied into core.

## Finding A163-07 — product labels were being asked to stand in for capabilities

**Risk.** Project, Temporary Chat, Agent, subagent, and API labels do not prove isolated prompt state, tools, filesystem scope, persistence, or provider memory behavior.

**Repair.** Current guidance treats those settings as experiment variables, records actual context identifiers and settings, and preserves explicit host-declaration nonclaims.

## Finding A163-08 — narrator reset can expose incomplete public custody

**Risk.** Lacuna stores transcript digests rather than transcript bodies. If material observations remained only in narration, a capsule-only fresh narrator could receive less legitimate public history than persistent-context controls. That would confound forgetting with information loss.

**Disposition.** The operator contract now requires a preregistered public-context policy: either continuity-critical observed canon is typed, or every condition receives the same separately digest-bound player-visible transcript/public summary. The capsule explicitly disclaims transcript completeness.

## Refactor assessment

The implementation is narrow:

- one new `continuation.py` module owns capsule build/validation/digest/rendering;
- checkpoint runs only add one read-only post-commit command and next-action rendering;
- scenario contracts add three linkage fields and one continuation-mode field;
- topology logic owns persistent/fresh segment rules in one validator;
- the default scenario template now encodes an observable continuation; and
- no provider SDK, archive layer, database table, event kind, or worker authority was added.

The design reuses canonical JSON digesting, strict sidecar reads, run locks, existing committed receipt authentication, and existing scenario/bundle state machines.

## Residual risks

- Scenario context/capsule fields remain host declarations and are not cross-signed by a provider.
- The scenario parent does not yet authenticate each declared invocation directly against a provider log or managed-run sidecar export.
- A parent can leak extra material while retaining a formally valid capsule digest.
- Shared filesystem read access can defeat card-only assumptions.
- The capsule can preserve the wrong compact state or omit necessary public transcript detail.
- No built-in randomized canary plan, masking-confidence form, or provider-conformance suite is yet shipped.
- Direct-upload archive, restore, encryption, credentials, network retries, and deletion remain external.

## Acceptance disposition

Rev0163 is acceptable when focused capsule/topology/final-step tests pass, the complete source and clean-extraction suites pass, all JSON/TOML/schemas/Markdown links validate, the clean manifest verifies, and the launcher reports `0.163.0` with the new checkpoint command visible.
