# Claim mechanism audit — rev0057

Source claim: `rev0056`, `cf34_counter_wall` versus `pub_threat_overlord`.

## Headline

rev0056 replicated both life cells, but the terminal mechanisms show that the result is primarily an endurance/library-out phenomenon.

Across 192 holdout games:

```text
target wins by opponent library-out: 151
target wins by opponent life-total loss: 4
target losses by target library-out: 26
target losses by target life-total loss: 11
```

That means the matchup should not yet be summarized as a normal damage race. It is better described as:

```text
The 60-card cf34 counter-wall/Jace shell often survives and interacts until the 40-card Overlord threat shell draws out.
```

## Life-cell profile

See `data/rev0057_claim_mechanism_profile.csv` for the exact rows.

Key qualitative pattern:

- life 20: target still wins mostly by opponent library-out, but target life-total losses remain visible;
- life 40: target wins more often, still mostly by opponent library-out, with fewer target life-total losses.

## Action profile

See `data/rev0057_claim_action_profile.csv` for role-specific action-kind and normalized action-signature counts.

The target profile is heavily defensive and Jace-centered: many passes, Island development, Counterspell/Force interaction, and Jace zero activations. The opponent profile contains more Overlord casting and attacks, but still a very large pass/interaction footprint.

## What to test next

The next experiment should be decomposition, not another broad retest:

```text
A. same-deck pilot swaps
B. same-pilot deck swaps
C. 40-card counter-wall versus 40-card Overlord
D. 60-card counter-wall versus 60-card Overlord
E. no-Jace or low-Brainstorm variants
F. fixed-mulligan variants
```

Success criterion: each ablation should report target score, terminal mechanism distribution, median decisions/turns, C++ shadow match rate, replay pass count, and whether the result survives seed-disjoint holdout.

