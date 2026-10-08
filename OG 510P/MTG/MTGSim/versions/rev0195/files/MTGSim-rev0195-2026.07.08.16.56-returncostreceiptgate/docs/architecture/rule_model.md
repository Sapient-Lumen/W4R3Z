# Rule-model roadmap — rev0002

## Traceability format

Each rule-backed feature should eventually have:

```yaml
rule: "704.5b"
summary: "state-based loss for life total <= 0"
module: "rules/state_based_actions.cpp"
tests:
  - "tests/rules/704_5b_life_loss.cpp"
status: tested
source_effective: "2026-04-17"
```

rev0002 starts with the section-level coverage file in `data/rules/coverage/rules_sections.yaml`.

## Highest-risk rule areas

1. **Priority and timing**: legal timing, special actions, mana abilities, nested priority loops.
2. **Casting/activation costs**: alternative/additional costs, cost reducers/increasers, X, hybrid/phyrexian, convoke/improvise-like payments.
3. **Replacement/prevention effects**: ordering, affected-player/controller choices, self-replacement, event rewriting.
4. **Continuous effects/layers**: dependency, timestamps, characteristic-defining abilities, copy effects, text changes, type/color/ability/PT layers.
5. **Triggered abilities**: intervening-if, reflexive triggers, delayed triggers, missed/optional triggers under tournament policy if supported.
6. **State-based actions**: simultaneous processing, token cleanup, aura/equipment/fortification legality, planeswalkers/battles, legends, commanders.
7. **Hidden information**: search, reveal, look, shuffle, face-down objects, derived observations for agents.
8. **Loops and shortcuts**: mandatory loops, optional loops, tournament shortcuts, deterministic loop summaries for simulation.

## Acceptance target

A feature is not complete until it has:

- deterministic unit tests,
- at least one integration scenario,
- rule-number traceability,
- replay/log coverage,
- benchmark impact if it is in a hot path.
