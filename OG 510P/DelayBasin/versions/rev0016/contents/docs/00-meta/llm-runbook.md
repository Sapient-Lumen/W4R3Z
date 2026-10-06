# LLM runbook

Read this before editing.

## What matters most

DelayBasin is trying to preserve **continuity under partial observability** while also discovering what such continuity implies about transformer systems.

The archive is not only content. It is also a scaffold for recurrence:
runbook + trajectory + registries + prompt pairs + changelog + package discipline + quarantine.

When useful, preserve the archive as a **typed continuation protocol**:
- workflow request surface,
- bounded state/resource surface,
- deterministic check/tool surface.

## Required reading before meaningful edits

- `README.md`
- `docs/00-meta/charter.md`
- `docs/00-meta/trajectory-map.md`
- `docs/10-method/method-overview.md`
- `docs/10-method/constitutional-pidgin-and-control-lexicon.md`
- `docs/10-method/portable-state-interface.md`
- `docs/10-method/typed-continuation-protocol.md`
- `docs/10-method/certified-core-vocabulary-and-recertification.md`
- `docs/10-method/certified-moves-and-procedural-admission.md`
- `docs/10-method/practice-observation-mechanism-speculation.md`
- `docs/10-method/self-stabilizing-recovery-and-legitimacy-kernel.md`
- `docs/10-method/revision-receipts-and-audit-objects.md`
- `docs/10-method/counterfactual-shadow-and-nearby-rejected-moves.md`
- `docs/20-constitution/recovery-kernel.md`
- `docs/20-constitution/revision-receipt-contract.md`
- `docs/10-method/constitutive-compression-and-prior-matching.md`
- `docs/20-constitution/claim-registry.md`
- `docs/20-constitution/invariant-registry.md`
- `docs/20-constitution/open-question-registry.md`
- `docs/50-promptcraft/prompt-pairs.md`
- `docs/90-quarantine/wild-speculations-2026-03-08.md`

## Editing method

Prefer small, composable edits.

Every serious revision should do at least one:
- research online when useful and translate the result into a small archive-native update,
- refine a distinction,
- add a guardrail,
- improve a prompt pair,
- convert a repeated intuition into a registry or invariant,
- capture an open disagreement without flattening it,
- or quarantine a genuinely fertile risky idea.

## House rules

- Do not report speculation as settled mechanism.
- Do not erase disagreement to make the archive look clean.
- Do not add new docs casually; justify the entropy cost.
- Do not retain PDFs or other large non-crucial research artifacts in the packaged archive.
- Do not let “method” become a license for vagueness.
- Do not lose the causal role of prompt pairs.
- Do not casually normalize away archive-private idiolect that may be functioning as a real local steering handle.
- Do not let provisional/private handles silently masquerade as certified core vocabulary.
- Do not claim archive progress without being able to say what certified move class the revision actually instantiated.
- Do not let a revision claim progress without emitting a compact revision receipt once receipt discipline exists.
- Do not let the accepted move erase the nearest rejected alternative when that local boundary actually mattered.
- Do not sand away transformer-facing implications just because they sound wild.
- Do not confuse “be risky” with “stop discriminating.”

## Risk mandate

This archive explicitly demands **speculation with risk**.

When a risky idea seems valuable:
- write it clearly,
- state its status honestly,
- state what would follow if it were true,
- state what would count against it,
- and place it in quarantine if canon would otherwise become polluted.

## Required outputs per run

1. What changed and why.
2. Which files changed.
3. Which open questions were clarified, sharpened, or added.
4. Confirmation that `make lint` ran.
5. What was researched online, if anything.
6. A packaged release link when a release is requested.
7. Preserve or update `REVISION-RECEIPT.json` when the revision materially changes canon/quarantine/move state.
8. Preserve a compact counterfactual shadow when a substantial revision had a real nearby rejected alternative.


## Additional admission rule

If you are effectively promoting or demoting canon-level trust, preserve the promotion contract or demotion reason explicitly. Do not let repetition, neat wording, or tool-boundary prestige silently raise epistemic status.


## Temporal honesty

If a revision strengthens a canon-level claim using fresh external research, ask whether the claim now deserves a **decay-watch** entry. Not every claim needs one. But fast-moving mechanism syntheses should not get indefinite trust for free.


## Recovery honesty

If a revision starts from stale canon, corrupted context, or unclear status, do not keep pretending progress happened. Use `MV-0010` / `recover-resync`: reopen the recovery kernel, regenerate `context-pack.json`, run `make lint`, and quarantine or demote ambiguous material before resuming ordinary work.
