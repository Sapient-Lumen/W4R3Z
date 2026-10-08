# Noisy Ecology Test: Why Pairwise Criteria Miss ZD Extraction

## Finding summary

Pairwise anti-vampire criteria in zero-noise environments fail to distinguish
Extortion (ZD) strategies from genuinely cooperative strategies. Under 2%
implementation noise against a cooperative pool, Extortion3 extracts an average
payoff gap of **+0.348** from its partners — while GenTFT-0.9 achieves **-0.037**
(approximately fair) and higher average own payoff.

This finding has a direct implication for scorecard design and search objectives.

---

## Experimental setup

**Simulation**: pure-Python mirror of `gr_engine/src/sim.rs` semantics.
**Script**: `scripts/analysis/universalization_frontier.py`,
`scripts/analysis/ipd_sim.py`.
**Parameters**: 200 rounds, 20–30 replications per matchup, 2% implementation
noise (`NoiseModelSpec::ImplementationFlip { p: 0.02 }`).
**Pool**: TFT, WSLS, GenTFT-0.9, GRIM, AlwaysC.

---

## Zero-noise result (why pairwise tests fail)

In a zero-noise environment, Extortion3 (chi=3 ZD strategy) cooperates fully with
every cooperative pool member: `gap = 0.000` against each. This is a known property
of ZD strategies — when facing a partner who never defects first, the extortion
parameters (p_dc=1/3, p_dd=0) are never triggered. The extraction only appears when
the opponent ever plays D.

Pairwise criteria tested in zero-noise thus **cannot distinguish Extortion3 from
TFT, WSLS, or GenTFT**. All four pass the three-criterion test.

**This is the gap in the current anti-vampire scorecard spec.**

---

## Noisy ecology result (the discriminating test)

With 2% implementation noise, the picture changes:

| Strategy   | avg_own | avg_gap | Assessment               |
|------------|---------|---------|--------------------------|
| GenTFT_0.9 | 2.355   | -0.037  | **Fair + high payoff**   |
| TFT        | 2.289   | +0.015  | Near-fair                |
| AlwaysC    | 2.333   | -1.061  | Exploitable              |
| Extortion3 | 2.004   | +0.348  | **Extracts from pool**   |
| GRIM       | 2.212   | +0.976  | Destroys cooperative world |

Extortion3 against the cooperative pool under noise:

| Opponent  | Focal | Opp   | Gap    |
|-----------|-------|-------|--------|
| TFT       | 1.436 | 1.337 | +0.099 |
| WSLS      | 2.662 | 1.604 | +1.058 |
| GenTFT    | 1.487 | 1.370 | +0.117 |
| GRIM      | 1.265 | 1.291 | -0.026 |
| AlwaysC   | 3.172 | 2.678 | +0.494 |

**Extortion3's worst victim under noise is WSLS** (gap=+1.058). Why: WSLS's
"win-stay, lose-shift" logic oscillates when noise occasionally produces (C,D)
outcomes — it shifts to D, gets punished by extortion (p_dc=1/3 means extortion
defects against D ~67% of the time), then shifts back to C, and the cycle repeats.
WSLS cannot stabilize against an extortioner in a noisy environment.

---

## Why GenTFT-0.9 is the better candidate

GenTFT-0.9 (p0=1, p_cc=1, p_cd=0.1, p_dc=1, p_dd=0) — generous Tit-for-Tat with
10% forgiveness on betrayal — achieves:
- Highest avg_own (2.355) of the genuinely reciprocal strategies
- avg_gap ≈ 0 (approximately fair across the pool)
- Positive recovery behavior under noise (the 10% forgiveness breaks retaliation
  spirals)

This is the behavioral profile closest to the Golden Rule in this test: it is
neither naive (AlwaysC) nor extractive (Extortion3) nor permanently punishing
(GRIM). It sustains cooperative equilibrium while being robust to occasional
defection.

---

## Implication for the anti-vampire scorecard spec

The anti-vampire scorecard (`anti_vampire_scorecard_spec.md`) defines:
1. `own_payoff`
2. `payoff_gap` (vs a canonical vampire)
3. `recovery_rounds`
4. `repair_abuse_rate`

This finding adds a fifth required field:

### 5. `ecology_gap_noisy`

Average payoff gap when the focal strategy plays against a representative pool of
cooperative strategies under realistic noise (e.g., 2% implementation noise).

- Computed as: mean over pool of `(focal_payoff - opponent_payoff)` per matchup.
- Threshold: `ecology_gap_noisy <= 0.1` to pass (allows small noise-induced gaps).
- Rationale: this is the test that catches ZD extraction. A strategy that extracts
  from cooperative partners under noise is not a virtuous agent, regardless of its
  zero-noise pairwise profile.

**Without this field, Extortion3 and GenTFT-0.9 are indistinguishable by the
scorecard.** With it, GenTFT-0.9 passes (avg_gap ≈ 0) and Extortion3 fails
(avg_gap = +0.348).

---

## Implication for search objectives

Do not run the search in a zero-noise pairwise evaluation loop. ZD strategies will
pass all pairwise tests and score well on raw own-payoff.

The correct search evaluates candidates against a cooperative pool under noise.
The objective should be: maximize `own_payoff` subject to `ecology_gap_noisy <= 0.1`.

This is more computationally expensive but correctly identifies strategies that
sustain cooperative equilibrium rather than strategies that exploit it.

---

## Limitations

- Pool composition affects `ecology_gap_noisy`. A pool with more AlwaysC members
  will inflate apparent extraction. Standardize the pool and log its composition
  in the artifact.
- GRIM shows a high positive gap (+0.976) but for a different reason than
  Extortion3: it destroys cooperative equilibrium by never forgiving noise-induced
  defections. Both should fail the ecology test, but their failure modes are
  distinct. The pool avg_own metric (GRIM=2.212, Extortion3=2.004) helps
  distinguish them — GRIM destroys value for itself too.
- The Python simulation mirrors the Rust engine semantics but is unverified against
  it. Results should be replicated with the compiled engine before being treated as
  primary evidence artifacts.

---

## Artifact

`artifacts/reports/universalization_frontier_snapshot.json` — initial snapshot
of the three-criteria tradeoff in 8000 sampled memory-one strategies.

## Further reading

- `anti_vampire_scorecard_spec.md`: scorecard to be updated with field 5
- `virtue_vs_strategy.md`: philosophical grounding for why this test is necessary
- `memory_one_tradeoff_against_extortion.md`: tradeoff context
