# StrategySpec & the Golden Rule Strategy DSL

## 4.1 StrategySpec requirements
A `StrategySpec` MUST be serializable and reproducible.

Required fields:
- `id`, `version`, `author` (can be “auto-llm”)
- `family`: rule-based | memory-one | FSM | belief-model | RL-policy
- `parameters`: typed dictionary
- `resource_limits`: time/memory bounds
- `determinism`: deterministic or stochastic (with seed handling)
- `signals`: supported communication primitives (optional)
- `ethos_tags`: declarative intentions (for analysis, not enforcement)

## 4.2 Strategy families (initial support)

### A) Memory-one stochastic
Parameterized by conditional cooperation probabilities given last move:
- CC, CD, DC, DD (+ optional initial prob)
Useful for fast sweeps and extortion/adversary generation.

### B) Finite state machine (FSM)
- explicit states,
- transition rules based on observation,
- outputs per state,
- optional counters with caps.

### C) Debt / forgiveness state machine (“Restorative Gradual”)
First-class variables:
- `debt` (unrepaired harm, decays),
- `trust` (belief in cooperativeness, increases with evidence),
- `contrition` (if self suspects accidental defect, triggers repair),
- `noise_estimate` (learned on the fly).

This implements “how much should I forgive?” as **decay + repair** rather than “how much should I punish?” as fixed blocks.

### D) Belief model (light theory of mind)
- opponent type posterior over a small library (AlwaysD, TFT-like, extortion-like, noisy cooperator, repentant/forgiving types),
- policy conditioned on posterior.

### E) Preference inference (“Platinum rule mode”)
When worlds include heterogeneous agent preferences (or “what counts as cooperation” differs),
a strategy MAY maintain:
- `pref_model`: estimate of what the other side values (or requests),
- `respect_score`: how well the strategy aligns to the other’s expressed preferences,
subject to security constraints.

This is a formalization of “treat others as they would like to be treated” under uncertainty.

## 4.3 GRDSL (“GRDSL”)
A small declarative language compiled to Rust strategy bytecode.

Design goals:
- interpretable (auditable),
- resource-bounded,
- expressive enough for “weighted gradual,” contrition, generosity, universalization heuristics.

### GRDSL primitives
State:
- numeric vars: `debt`, `trust`, `p_noise`, `p_hostile`, `pref_align`, counters
Observations:
- `opp_last_obs`, `opp_last_exec?` (if audit), `self_last_intent`, `round`, `signal_last`
Actions:
- `C`, `D`, `Exit`, `Signal(type, payload)`
Control:
- `if`, `else`, `clamp`, `decay`, `update_bayes_simple`, `rand(p)`, `sigmoid(x)`

### Example patterns (sketch)
- **Discounted harm:** `debt = decay(debt, lambda) + w_intent * is_defect(opp_last_obs)`
- **Contrition:** if `self_last_intent == C` but executed was D => enter apology/repair phase
- **Retaliation as probability:** `p_defect = sigmoid(k*(debt - thresh))`
- **Restoration:** if `trust` high and opponent defects once, reduce `w_intent` (Hanlonian prior)

## 4.4 Compilation and sandboxing
- GRDSL compiled to a compact IR.
- Rust executes IR with fixed instruction limits per move.
- Randomness uses per-match RNG stream; MUST be reproducible.

## 4.5 Strategy promotion gates
A strategy MUST pass:
- self-play stability under noise,
- security floor vs AlwaysD/extortion family,
- bounded compute,
before being considered in Pareto selection.

## 4.6 Interpretability outputs
Strategies SHOULD emit “explanations” (structured logs):
- state variables per round,
- why an action was chosen (rule id / condition),
to support failure-case debugging.

## 4.7 “Signals are strategic”
If the world includes signals, strategies MUST assume:
- apologies can be faked,
- commitments can be broken,
- reputation can be laundered.
Signal handling MUST be tested against fake-signal adversaries.
