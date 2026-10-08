# ML and simulation API direction through rev0011

The eventual simulation/ML interface should expose deterministic state transitions, legal-action masks, compact observations, and reproducible rollouts. rev0009 does not implement that full API; it adds an important action kind and event/trigger seam.

## Current reducer surface

The current `LegalAction` surface includes:

- pass priority;
- cast a simple spell from hand after paying mana;
- cast a simple targeted spell after paying mana and choosing one target;
- activate a tap-for-mana ability;
- declare a simple attacker;
- declare a simple blocker;
- put pending triggered abilities on the stack.

## Why triggers matter for ML/search

A simulator cannot treat triggered abilities as hidden mutations if it needs reproducible search trees or legal-action masks. rev0009 makes pending triggers visible as state and exposes stack placement as an action. That gives future agents a stable observation/action point for trigger ordering and choices.

## Required future work

- Stable numeric action encoding.
- Stable observation encoding with hidden-information views.
- Replay serialization.
- Action masking for modes, targets, costs, and trigger choices.
- Batch rollout API.
- Optional fast unsafe mode after invariant-tested safe mode is mature.

## rev0011 ML/API note: legal actions with derived state

The action API can now encounter a tiny targeted counter spell during fuzzing. For future ML consumers, state encoders should expose both base values and derived values. A model that sees only `power` and `toughness` fields will mis-evaluate combat once counters, layers, static effects, or temporary effects are in play.

## rev0012 action-mask implications

Flying/reach now affects `enumerate_legal_actions(...)`: an illegal ground block of a flying attacker is absent from the legal-action list. This is exactly the shape needed for search/ML: the policy surface should receive legal action variants after rules filters, not learn combat legality from penalties after illegal moves.

## rev0013 ML/action-surface note

Blocked-attacker memory is useful beyond rules correctness. A policy/value model or tree search needs a state representation that distinguishes “never blocked” from “blocked, blockers gone.” rev0013 makes that distinction explicit in `GameObject::blocked`, which will later belong in compact state encodings and replay traces.


## rev0015 implications for action masks

Menace is the first concrete sign that some legal actions are naturally compound. A future ML/search action representation will need structured block-declaration batches, not only one object plus one target. For now, the one-blocker action mask remains conservative and `block_batch` lives in scenario/API tests.

## rev0017 attachment relevance for agents

Attachments matter for legal-action masks because they alter derived power/toughness and keyword abilities without changing the underlying card definition. The current API keeps attachment state observable through deterministic object metadata and shared helpers, which should make future feature extraction simpler than trying to infer attachment effects from event logs.

## rev0018 ML/API note

Token tombstones are useful for replay/debugging but should not appear in legal-action masks or live-object encodings. A future observation encoder should expose live zone containers and optionally a separate recent-event/history stream. That keeps dense object IDs stable without asking policies to act on ceased tokens.


## rev0019 legal-action expansion

Legal action enumeration now includes a scaffold `ActivateLoyaltyAbility` action and target variants for simple loyalty abilities. This expands the future ML action mask beyond casting, mana, combat, and trigger-stack placement without changing the orchestration interface.


## rev0020 legal-action shape for battles

The legal-action API can now enumerate object-targeted attacks against battles. This matters for future ML/search because battle attacks are legal choices that differ from planeswalker attacks by defender/protector semantics.


## rev0021 modal action masks

`LegalAction::mode_index` makes modal spells visible as distinct cast choices. A policy/search caller can now distinguish `cast card X choosing mode 1` from `cast card X choosing mode 2`, and targeted modes expand into source-aware target variants. This is still a scaffold, but it avoids hiding player choices inside resolver code.

## rev0022 timing and land actions

`ActionKind::PlayLand` separates stack-free land play from `CastSpellFromHandPaid`. Legal-action enumeration now filters ordinary noninstants out of instant-speed windows, admits instants and flash cards when the player has priority, and never offers land cards as cast actions. This is a useful ML/search seam because it makes the branch type explicit instead of hiding timing decisions inside resolver code.

## Rev0023 action-mask expansion

`LegalAction` now includes `ability_index` for generic activated abilities. This makes activated abilities first-class actions alongside casting, modal choices, land plays, mana abilities, loyalty abilities, combat declarations, trigger stacking, and pass priority. The current shape is directly usable by a future policy head because each legal target variant is enumerated explicitly.


## rev0024 mana action shape

The action surface now exposes `ActivateManaAbility` with `mana_ability_index` while also letting cast/activation actions auto-pay through a deterministic simple planner. For ML/search this means two compatible modes are possible: fine-grained policies can explicitly choose mana actions, while faster playout policies can let the engine perform the obvious payment plan for simple costs.

## rev0025 legal-action implications

Legal-action enumeration now observes static-effect-granted haste and evasion indirectly through shared helpers. That keeps future ML/action masks closer to true rules-derived legality as continuous effects grow.


## rev0026 control-change implications

Control changes make ownership and control distinct observable features. A future state encoder should expose owner, controller, and zone-owner/container membership separately, because a stolen permanent may be controlled by one player on the battlefield and later move to another player's graveyard. Legal-action masks can already include a targeted gain-control spell; future agents will need stable features for controller-scoped static effects and summoning-sickness refresh after control changes.


## rev0027 type/color implications

The legal-action API should observe current derived characteristics, not printed-only card metadata. rev0027 starts that refactor by routing action enumeration and fuzz fixture selection through `object_type_mask(...)` and by letting source-color legality use static color effects. This matters for simulation and ML because the action mask must change when a continuous effect turns a land into a creature, removes creature status, or changes a source's color.

## rev0028 ML/API note

Legal action generation and combat legality now benefit indirectly from the derived-characteristic seams for ability removal and base-P/T setting. This matters for search/ML because action masks should be computed from current characteristics rather than printed card metadata; otherwise a learned policy would train on actions that are illegal after continuous effects apply.
## Temporary effects and simulation state

Temporary continuous effects live in explicit state rather than hidden mutations. That makes legal-action masks and future ML features easier to serialize: an evaluator can inspect active generated effects, timestamps, and locked targets without reverse-engineering changes from object stats.

## rev0095: an action mask must state whether it is complete

rev0095 corrects a foundational ML/search assumption. A bounded 128-action combat prefix was previously returned through the same vector type as a complete legal set. At eight independent attackers or blockers, legal declarations could be absent; membership-based legality then rejected them. A policy mask built from that vector would have contained false negatives.

The new `LegalActionFrontier` reports `complete` and `generation_limit`, and the same truth is bound into `ChoiceRequest` and receipts. This is necessary but not sufficient for agents. An agent that sees only the bounded prefix is still biased toward the generator's recursive order.

The durable agent API should therefore distinguish:

- authoritative direct validation;
- exact complete enumeration for small states;
- deterministic cursor-based pages;
- structured declaration variables and constraints;
- seeded legal sampling;
- unknown/lower-bound/exact action counts;
- public observation versus player information state;
- chance outcomes, returns, terminal state, clone/undo, and batch stepping.

Flat stable action IDs may be an adapter for small discrete choices, but compound combat, targets, modes, and costs should retain a structured schema. Search should not need to materialize every sibling before validating or applying one declaration.
