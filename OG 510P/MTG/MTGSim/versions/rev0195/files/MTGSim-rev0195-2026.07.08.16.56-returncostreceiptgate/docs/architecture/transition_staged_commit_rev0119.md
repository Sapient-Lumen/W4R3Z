# rev0119 — transition staged commit spine

## Audit finding

rev0117 introduced `TransitionResult` and rev0118 made committed results carry selected-choice proof hashes. The remaining risk at that seam was subtler: after preflight validation succeeded, `commit_action_transition(...)` still mutated the caller's `GameState` directly and only then appended the causal receipt. If a future multi-step action body returned false after a partial write, the public transition API could no longer uphold the reducer contract that rejected transitions leave StateCore and journal evidence unchanged.

That risk is especially relevant for the next semantic slices: paid casting and activated abilities need mode/target locking, auto-mana activation, tap/sacrifice costs, stack placement, trigger creation, and receipt persistence to behave as one transaction rather than a chain of partially visible writes.

## Refactor

`commit_action_transition(...)` now commits through a staged `GameState` copy:

1. capture StateCore, journal, receipt, and event-sequence facts from the caller state;
2. run shared `preflight_action_transition(...)` to compute the APNAP choice queue, selected local `ChoiceRequest`, validation result, and legal-action page proof without mutation;
3. reject illegal proposals before any staged mutation;
4. copy the state into a staged GameState;
5. run the shared legal-action mutation body on the staged state only;
6. if staging fails, return `commit_failed_without_adoption` with the caller StateCore and journal still unchanged;
7. if staging succeeds, append the causal receipt to the staged state, capture after-hashes from the staged state, and atomically adopt it with `game = std::move(staged_game)`.

The refactor also removes duplicated preflight code from legacy `apply_action(...)` by adding the internal `ActionTransitionPreflight` / `preflight_action_transition(...)` helper. Legacy `apply_action(...)` still keeps its historical full-trace behavior: illegal attempts append an `illegal_action` event and an unapplied receipt. The staged adoption guarantee is intentionally scoped to `commit_action_transition(...)`, the stricter public reducer seam.

## New transition evidence

`TransitionResult` now exposes three staging sentinels:

- `staged_commit_attempted`
- `staged_commit_applied`
- `staged_commit_adopted`

`committed_with_staged_adoption()` combines those sentinels with the existing single-receipt commit predicate. A committed transition should now satisfy both `committed_with_staged_adoption()` and `committed_with_choice_proofs()`.

## Guardrail

`test_commit_action_transition_adopts_the_staged_legacy_equivalent` compares the adopted staged transition against the same action applied through the legacy mutation/receipt path, proving the new staging wrapper reaches the same StateCore and journal while moving adoption to the final step. Existing rejection tests also assert that preflight rejections do not start, apply, or adopt a staged commit.

`tools/audit_datacube.py` now probes the staged commit seam across public result fields, the shared preflight helper, the staged `GameState` copy/adoption code, tests, this note, audit notes, and the rules ledger.

## Scope retained

This is still a wrapper-level staging cut. It makes the top-level transition boundary atomic for today's action bodies and prepares the next paid-cast/activated-ability work, but it does not yet split individual rule procedures into explicit phase objects. The next semantic slice should stage one multi-step rule action internally: lock modes/targets, pay costs, place the object/ability on stack, and commit one receipt only after every phase succeeds.

The intended safety property is atomic adoption: the caller state changes only after the staged mutation and staged receipt both succeed.
