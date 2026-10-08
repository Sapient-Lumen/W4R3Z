# Golden Rule Scorecard (multi-lens, definition clarity, and robustness)

## 5.1 Why a scorecard?
We cannot reduce “Golden Rule” to one number without losing meaning.
Therefore we use:
- multiple lenses/metrics,
- explicit constraints,
- and Pareto reasoning.

## 5.2 ScorecardCard (required)
Every ScorecardSpec MUST ship with a ScorecardCard:
- intent: what it is trying to capture
- non-goals: what it does not claim
- lenses included (and why)
- known risks (Goodhart-ish failure modes)
- required holdouts and metamorphic checks
- appropriate / inappropriate contexts
- change log and version

ScorecardCards MUST appear in reports next to results.

## 5.3 WorldDatasheets (required)
Every WorldSuite MUST include a datasheet-style description:
- composition and rationale
- gaps and limitations
- brittleness tendencies
- update policy (how probes get added)

## 5.4 Core metric families (baseline)
- welfare: expected payoffs (individual + global)
- robustness: variance, tail collapse risk
- cooperation: mutual cooperation rate, recovery time
- anti-exploitation: worst-case regret vs adversary families
- forgiveness: grudge half-life, repair curves
- intention calibration: response quality under noise/miscommunication
- anti-domination: leverage snowball containment (when enabled)

## 5.5 Constraint gates (must)
Promotion requires meeting hard constraints, e.g.:
- floors vs AlwaysD-like families
- bounded retaliation spirals under noise
- bounded collateral damage (complaint floors)
- stability under self-play and friendly pools

## 5.6 Robustness “confidence signals” (required)
When you optimize any measure, you can accidentally overfit it.
We don’t treat this as moral failure—just a normal scientific issue.

Therefore the lab MUST include:
- holdout suites never used for search decisions,
- metamorphic relations (oracle-free checks),
- definition sensitivity (vary weights/thresholds; test rank stability),
- rare-case mining (tail failure discovery),
- metric triangulation (multiple measures per lens),
- auditability (reason traces + minimal repros).

Reports MUST surface these signals clearly:
- “stable across scorecards?”,
- “stable across seeds?”,
- “stable across minor world perturbations?”,
- “tail risk changed?”

## 5.7 Sensitivity analysis (required)
Reports MUST include:
- robustness of rankings to score weighting,
- robustness to alternative lens bundles,
- and “best available” claims must list which scorecards support them.

## 5.8 No single scalar rule (default)
By default, the system MUST NOT promote based on a single scalar objective.
If a scalar is used internally for search, promotion MUST still be based on:
- Pareto + constraints + holdouts.

## 5.9 Publication and dual-use note
Public artifacts MUST omit or redact recipe-level exploit details.
See `06_Red_Team_and_Adversaries.md`.
