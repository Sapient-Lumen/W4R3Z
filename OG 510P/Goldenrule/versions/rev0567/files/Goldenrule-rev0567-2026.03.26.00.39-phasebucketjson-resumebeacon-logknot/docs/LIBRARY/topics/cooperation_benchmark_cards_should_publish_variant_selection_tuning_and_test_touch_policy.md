# Cooperation benchmark cards should publish variant selection, tuning, and test-touch policy

A compact cooperation benchmark card is still too weak if the published result quietly comes from a **chosen benchmark wrapper** among many plausible prompt, interface, scoring, or agent-shell variants.
Even when the underlying task is nominally the same, small prompt or evaluation-format changes can move rankings materially, and selective disclosure of the best-tested variant can make a result look more stable than it really is.

Recent evaluation work makes the archive rule clear:

- `RS-GR-080` shows that common LLM benchmarks rely on a limited set of prompt templates even though performance can vary across prompt variants, and argues for estimating performance over a prompt family rather than treating one template as the whole capability.
- `RS-GR-081` shows that minor benchmark perturbations such as choice order or answer-selection method can shift leaderboard rankings substantially, so small wrapper choices are not harmless evaluation plumbing.
- `RS-GR-082` shows that undisclosed private testing of multiple variants plus selective disclosure can bias public leaderboard results upward.

## Minimum contract

Whenever a retained cooperation result depends on one chosen evaluation wrapper, publish four short fields on the card or neighboring compact receipt:

1. **variant family** — what could vary (prompt template, wrapper, scoring mode, answer-selection rule, agent shell, UI, or equivalent);
2. **selection / tuning rule** — fixed in advance, sampled, optimized on a development split, hand-picked after pilots, or other declared policy;
3. **search budget** — the number or range of variants, sweeps, or private trials materially considered before the retained result was chosen;
4. **test-touch policy** — whether benchmark test outcomes were seen during selection, and if so whether the published object should be read as tuned-on-test rather than as a clean holdout result.

If a benchmark reports a distribution or quantile over a declared variant family instead of one chosen template, say so directly.
If the wrapper was fixed ex ante and never tuned against benchmark outcomes, say that directly too.

## Implementor consequence

Do not let a best-picked prompt or interface masquerade as a stable cooperation gain.
A retained result may still be useful after wrapper search, but it should then be labeled as a tuned deployment profile, a prompt-family summary, or a tuned-on-test benchmark result rather than as one unqualified cooperation estimate.
If test outcomes were touched during selection, the comparison license should narrow accordingly.

## Archive consequence

Keep the retained object tiny.
One short variant-family / selection-rule / search-budget / test-touch quartet is enough.
That prevents future sessions from laundering hidden prompt/interface search into an inheritor-facing cooperation claim while still keeping the archive compact.
