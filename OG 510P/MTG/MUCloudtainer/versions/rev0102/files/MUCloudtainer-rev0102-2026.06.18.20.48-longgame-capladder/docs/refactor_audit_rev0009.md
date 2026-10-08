# rev0009 Refactor / Audit

## Refactors

### 1. Observation redaction

`GameState.observation(player)` now redacts pending-choice payloads for non-actors.

### 2. GameState revision

`GameState` now has:

```python
revision: int = 0
```

`apply_action` increments it after each macro-action. DecisionFrame uses this to reject stale action choices.

### 3. DecisionFrame safe fast path

New file:

```text
src/muc5/decision.py
```

It adds a public, hidden-information-correct agent interface.

### 4. Payoff mulligan-policy bug fix

`play_strategy_pair` now gives each seat its own `RuleMulliganAgent`. Previously, different bundle mulligan policies could silently fall through to no shared mulligan policy. That was acceptable only while all default bundles shared `land_band`; it would become wrong once mulligans varied as strategy components.

### 5. Payoff row scoring visibility

Payoff rows now include:

```text
p0_terminal_win
p1_terminal_win
is_nonterminal_draw
is_truncation
```

Aggregates now label the draw-half convention explicitly:

```text
p0_mean_score_draw_half
p1_mean_score_draw_half
p0_terminal_win_rate
```

## New audits

```text
scripts/audit_leakage_rev0009.py
scripts/profile_decisionframe_rev0009.py
scripts/inspect_cloudtainer_tools.py
scripts/run_rev0009_mulligan_bundle_payoff.py
```

## Tests

```text
tests/test_rev0009_decision_leakguard.py
```

Checks:

- Jace +2 private top-card data is visible to the actor and redacted for non-actor.
- DecisionFrame stale reuse is rejected.
- public-agent game path runs.
- payoff pairs support seat-specific mulligan policies.
