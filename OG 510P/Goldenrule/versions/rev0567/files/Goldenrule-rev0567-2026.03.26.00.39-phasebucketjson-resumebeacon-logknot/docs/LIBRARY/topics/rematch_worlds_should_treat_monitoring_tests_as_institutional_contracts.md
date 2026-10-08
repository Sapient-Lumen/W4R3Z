# Rematch worlds should treat monitoring tests as institutional contracts

A repeated-game benchmark stops being just a partner/environment test once deviations are observed only through noisy or partial evidence.
At that point, the monitoring rule itself becomes part of the institution.

Recent work on repeated games with imperfect monitoring makes this explicit: cooperation can be sustained by a **test-then-punish** design, but the induced behavior depends on exactly how evidence is accumulated and when punishment is triggered.
That means Concord should not hide monitoring policy inside implementation details or scratch notebooks.

## Implementor-facing rule

If a world or benchmark lane uses imperfect monitoring, retain one compact monitoring contract that records:

1. the observation model,
2. the test family (`sequential`, `batched`, or other declared rule),
3. the false-punishment budget or Type I control target,
4. the detection horizon or batch size, and
5. the punishment trigger / persistence rule.

## Why this matters

Two benchmark runs can share the same agents, payoffs, and world geometry yet implement materially different institutions if one uses an anytime-valid sequential detector and another uses fixed batches.
The current literature shows that this difference can trade off broader deviation coverage against stronger global false-alarm control.
So an inheritor should read those choices as benchmark semantics, not as post hoc analysis settings.

## Archive consequence

Do not answer this by minting a wide new report family.
Instead, add one tiny monitoring-contract section to the retained benchmark artifact or its nearest compact receipt whenever imperfect monitoring is introduced.
That keeps the archive small while preventing a silent shift in what “cooperation under this institution” actually means.
