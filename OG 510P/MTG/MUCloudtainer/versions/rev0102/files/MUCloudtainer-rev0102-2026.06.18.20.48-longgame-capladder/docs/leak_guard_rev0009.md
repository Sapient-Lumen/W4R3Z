# rev0009 Leak Guard and Reward-Hack Notes

The MUC-5 referee is omniscient. The learning methods must not be.

rev0009 formalizes the boundary:

```text
GameState             = omniscient simulator state
observation(player)  = hidden-information-correct public/private view
DecisionFrame        = observation + legal action list + revision guard
agent                = chooses an index from the legal list
```

## Fixed in rev0009

`GameState.observation(player)` previously exposed `pending_choice_data` to any caller. That is wrong for private choices. The immediate example is Jace +2: the controller sees the target player's top card and chooses leave/bottom. The non-acting player should know a choice exists, but not the card seen.

Now:

```text
pending_choice.player == observer:
  observer sees full pending_choice_data

pending_choice.player != observer:
  observer sees {redacted: true, player, kind}
```

The gametable renderer now follows the same rule unless explicit debug reveal is requested.

## Important remaining boundary

Trusted baseline agents still receive `GameState` through the old `Agent.choose_action(state, rng)` interface. They are allowed only as scripted baselines and simulator smoke tests. Future learned agents should use the DecisionFrame path.

The old interface is dangerous because a malicious or careless agent could inspect:

- opponent hand
- opponent library order
- own future draws
- full deck counts in closed-decklist experiments
- private pending-choice payloads

The correct interface for learning/search/evolution is:

```text
build_decision_frame(state)
agent.choose_action_index(frame, rng)
apply_decision_index(state, frame, index, rng)
```

## Legal action masks can leak if misused

For the acting player, the legal action list is allowed to include choices derived from that player's own hand and public state.

For the non-acting player, never expose the acting player's legal actions as if they were part of the non-actor observation. This is especially important during discard/Brainstorm/Jace choices, because legal choice actions encode cards in the acting player's hand.

The rule is:

```text
legal_actions(state) belongs only to state.current_player()
```

## Reward-hack traps to isolate

The simulator should keep these concepts separate:

- terminal win/loss
- nonterminal truncation from `max_decisions`
- speed/short-game diagnostics
- human-interest labels
- training reward

Do not silently reward speed unless speed is the experimental objective. Do not treat `max_decisions_reached` as a real win. rev0009 payoff rows now include both draw-half score and terminal-win indicators:

```text
p0_score / p1_score              # current draw-half payoff convention
p0_terminal_win / p1_terminal_win
is_nonterminal_draw
is_truncation
```

This avoids hiding the scoring convention inside aggregate tables.

## Construction-context traps

Life total is always known during gameplay. The uncertainty experiment is construction-only:

```text
known_life_20 constructor: knows it is 20 before registering
known_life_40 constructor: knows it is 40 before registering
unknown_robust constructor: only knows {20, 40}
```

Do not pass the actual life value into an unknown-life constructor.

Likewise, future closed-decklist experiments must not pass opponent deck counts to the pilot. Open-decklist and closed-decklist modes need separate configs.

## rev0009 audit artifacts

```text
scripts/audit_leakage_rev0009.py
data/rev0009_leakage_audit.json
src/muc5/fairness.py
```

These are cheap checks, not proofs. They catch obvious observation-shape leaks and stale DecisionFrame reuse.
