# Runtime dreambank 029 — model-oracled provider resilience

Current revision: rev0054

The ambitious idea: BrowserRT eventually becomes a runtime where every serious provider has a model oracle close enough to catch semantic drift before browser/provider budget is spent.

## Dream

A future BrowserRT test could generate a whole runtime history:

```txt
storage provider fails
retry asks for a budget lease
breaker opens
fallback lane is attempted
spill mailbox queues pending deliveries
compaction runs
worker crashes
recovery replays
model checks allowed outcomes
```

Rev0034 only earns the tiny local rung: fake-provider provider-resilience histories are compared against `ProviderResilienceModelOracle`.

## Why this matters

The composed resilience stack is fragile because each layer can be locally correct but globally leaky:

- retry policy can acquire a lease after the operation's own attempt cap;
- breaker rejection can skip provider mutation but still leave budget state dirty;
- storage-lane health can turn provider failure into scheduler rejection;
- generated histories can surface cases hand-written examples miss.

Rev0034 found and fixed one such issue: when an operation-level `maxAttempts` was lower than the retry policy's max attempts, `ProviderResilienceHistoryRunner` could acquire a retry-budget lease after the last allowed operation attempt. The fix makes the operation-level cap authoritative.

## Future ambition

- provider-resilience concurrent histories;
- provider-resilience fault injection with explicit operation call/return events;
- history shrinking/minimization;
- fake time, fake storage, fake worker, and fake GPU providers sharing a model harness;
- optional external-style checker compatibility, without making BrowserRT depend on external tools.
