# Cooperation benchmarks should publish human-proxy provenance and real-human escalation status

Human-proxy partners are useful, but they are not interchangeable with actual humans.
The archive should treat them as a **distinct benchmark lane with provenance**, not as a quiet substitute for real-human evaluation.

Two standing sources now make the implementor rule clear:

- `RS-GR-049` shows that cooperation conclusions can change depending on whether models face other models, human-like strategies, or real humans.
- `RS-GR-050` shows why human-proxy evaluation is attractive anyway: proxies can be reproducible, hosted, and cheaper than direct human evaluation, but they are still proxy partners learned from a particular data source and training recipe.

## Minimum contract

Whenever a benchmark card contains a human-proxy lane, publish:

1. whether the lane is **actual human**, **hosted human proxy**, or **released proxy**;
2. the proxy's **data provenance / budget** and broad construction recipe;
3. whether the proxy is **held out / hosted to limit overfitting**;
4. whether any **real-human lane** was also run;
5. and the **escalation rule** for when proxy success is strong enough to justify a real-human follow-up.

## Implementor consequence

Do not let “works with humans” silently mean “works with a human-like proxy.”
A policy that coordinates with one hosted proxy family may still fail with real people or with differently trained proxies.

## Archive consequence

Keep the retained object compact.
One small benchmark-card row is enough: human-lane type, proxy provenance, hosting posture, and real-human escalation status.
That prevents future sessions from laundering proxy success into a full human-compatibility claim.
