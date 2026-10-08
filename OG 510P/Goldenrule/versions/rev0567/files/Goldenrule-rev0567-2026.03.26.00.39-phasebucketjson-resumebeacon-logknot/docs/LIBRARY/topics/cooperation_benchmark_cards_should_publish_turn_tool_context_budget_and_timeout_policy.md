# Cooperation benchmark cards should publish turn, tool, context, and timeout policy

A compact cooperation benchmark card is still too weak if the published result quietly depends on **how much interaction, context, or runtime budget the evaluated system received**.
Even when the task, evaluated subject, wrapper, judge, and scoring rule are fixed, a cooperation result can move because one run had more turns, more tool calls, a longer retained history, a larger token budget, or a more generous timeout / retry window than another.

Recent evaluation work makes the archive rule clear:

- `RS-GR-098` argues that an evaluation pipeline is an instrument rather than just a dataset, and that for agentic systems the effective input includes task specification, tool interfaces, and initial environment state rather than only the final prompt surface.
- `RS-GR-099` shows a concrete reproducible protocol with a fixed tool-use budget, per-call timeout, retry policy, deterministic caching, and full trace logging, which means these limits are part of the benchmark contract rather than harmless harness internals.
- `RS-GR-100` shows that sequential test-time scaling in general agents is bounded by a context ceiling: longer interaction histories can eventually make performance fluctuate or degrade rather than monotonically improve.
- `RS-GR-101` shows that agent effectiveness changes under token and time budgets and that expensive failures can consume large resources while getting stuck, so resource budgets are part of what is being measured.

## Minimum contract

Whenever a retained cooperation result could change because of execution limits, publish four short fields on the card or neighboring compact receipt:

1. **turn / action / tool-call budget** — maximum interaction turns, action steps, tool-use rounds, or per-tool / total call caps, plus whether the budget was fixed or adaptively expanded;
2. **context / history-retention policy** — nominal context window, whether prior turns were kept verbatim, summarized, retrieved, or truncated, and whether overflow changed what the system could still see;
3. **token / compute / latency budget** — major generation limits, thinking-token or compute budgets when material, wall-clock or per-call timeouts, and whether these limits were held fixed across compared subjects;
4. **limit-hit handling / stop rule** — what happens when a cap is hit: forced final answer, truncation, stop-without-answer, failure, retry budget, escalation, or other declared policy.

If the result comes from a deliberately budget-amplified run, say that directly.
If the benchmark fixes a small and reproducible cap for all subjects, say that directly too.

## Implementor consequence

Do not compare a 5-turn capped result, a 100-turn capped result, a full-context result, a summarized-history result, and an open-ended retrying result as though they were the same cooperation object.
A retained result may still be useful under any of those regimes, but the comparison license should say which regime it belongs to.
If the benchmark intentionally studies cooperation under constrained budgets, that should appear as the experimental claim rather than as hidden evaluation plumbing.

## Archive consequence

Keep the retained object tiny.
One short turn/tool-budget / history-policy / compute-latency-budget / limit-hit-rule quartet is enough.
That prevents future sessions from laundering extra interaction slack or timeout generosity into an inheritor-facing cooperation gain while still keeping the archive compact.
