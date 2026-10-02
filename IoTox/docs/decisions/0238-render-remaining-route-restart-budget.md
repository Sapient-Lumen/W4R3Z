# ADR 0238: Render remaining route restart budget explicitly

Status: accepted through the ADR 0235 direct-UDP and forced-TCP gates, 2026-08-29.

## Context

Each signed route member carries an immutable `restart_budget` ceiling, while the coordinator
separately counts consumed `restarts`. The `routes` status surface rendered these as `restart-budget`
and `restarts`. The three-loss qualification incorrectly treated `restart-budget` as remaining
capacity and required zero after two restarts, even though the field correctly remained the signed
ceiling of two. Diagnostic UDP root `pair.g6nix_0l` completed the substantive transfer and recovery
work, then failed that evidence assertion before emitting an acceptance receipt.

Changing the existing field to a decrementing value would silently change its meaning for operators
and evidence consumers. Requiring every consumer to subtract two fields also leaves room for the same
ambiguity to recur.

## Decision

- Keep `restart-budget` as the signed immutable ceiling.
- Keep `restarts` as the consumed count.
- Add the content-free derived field `restart-budget-remaining`, equal to the checked subtraction of
  the consumed count from the signed ceiling.
- Require the exhausted three-loss route to render
  `restarts=2 restart-budget=2 restart-budget-remaining=0`. Existing one-restart fixtures likewise
  prove `restarts=1 restart-budget=1 restart-budget-remaining=0`.
- Do not change the signed route-set format, coordinator state, recovery admission, or restart policy.

## Consequences

Operators and strict gates can distinguish policy, consumption, and remaining capacity without
guessing a field's semantics. The value is safe to derive because snapshot rendering already rejects
`restarts > restart_budget` before subtraction.

This is an observability and evidence correction, not by itself proof of the three-loss gate. The
failed diagnostic remains non-acceptance evidence. Clean direct-UDP proof `pair.3iufekzy` and
forced-TCP proof `pair.zleebk2k` subsequently render the required exhausted tuple and pass raw plus
compact verification under ADR 0235.
