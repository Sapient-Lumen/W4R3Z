# Vision & Definitions

## 1.1 What this project is
Concord is a **norm-design laboratory** for exploring and stress-testing a *family* of Golden Rule–like stances in strategic interaction.

It aims to:
- **map tensions and tradeoffs** between competing Golden Rule lenses,
- find **better** strategies under explicit commitments and contexts,
- and grow a shared **experimental vocabulary** (probes, worlds, failure modes).

## 1.2 Definitions are artifacts (clarity, not paranoia)
If we optimize hard, the system will converge on:
> “best under the scorecard and world suite we chose.”

That’s fine—if we are explicit about what we chose.

Therefore:
- scorecards, probes, and holdouts MUST be versioned artifacts,
- reports MUST show which versions were used,
- and “best available” claims must include the failure envelope.

This is a reproducibility + meaning requirement, not a trust issue.

## 1.3 Golden Rule lenses (plural)
We track multiple lenses that can conflict:
- role-reversal / reciprocity
- restraint (“silver rule” harm-avoidance)
- universalization (what if everyone did this?)
- justifiability / complaint floors (proxy)
- restorative repair (rebuilding trust without enabling cycles of abuse)
- anti-exploitation / anti-domination (resisting leverage snowball)
- intention calibration (noise, mistakes, incapacity)

Each lens becomes:
- metrics,
- probes,
- and institutional toggles.

## 1.4 Better vs best: how we speak
We speak in two registers:

### Register A — “Better under commitments”
Given:
- a ScorecardSpec (explicit commitments),
- a WorldSuite (explicit contexts),
we can say “A is better than B” with evidence (Pareto + constraints).

### Register B — “Best available (for now)”
We MAY say “best available” only if:
- robust across multiple competing scorecards,
- robust across holdout suites,
- and failure modes are understood (minimal counterexamples exist).

## 1.5 Two-path plan (required)

### Path A — Interpretable strategies (Phase 1)
Goal: discover robust design patterns and failure modes.
- classes: memory-one, finite-memory FSMs, belief-based heuristics
- artifacts: traces, minimal probes, analytic payoffs where possible
- promotion: strict; minimize + explain every new failure

### Path B — Learned policies (Phase 2, gated)
Goal: explore broader strategy space (partial observability, richer games).

Rules:
- learned policies MUST still be evaluated with holdouts + metamorphic checks + adversarial probes,
- SHOULD be distilled into interpretable approximations when possible (FSM distillation),
- MUST never be promoted based on a single scalar reward.

Path B is “explore widely”; Path A is “understand deeply.” Both remain active.

## 1.6 Autonomy, creativity, and disciplined iteration
The LLM operator is trusted with significant autonomy.

The system exists to help them:
- form hypotheses,
- try risky variations quickly,
- discover weird corners,
- and then turn surprises into crisp probes and explanations humans can learn from.

The discipline we require is:
- keep definitions explicit,
- keep artifacts reproducible,
- and keep human-facing explanations anchored to traces.
