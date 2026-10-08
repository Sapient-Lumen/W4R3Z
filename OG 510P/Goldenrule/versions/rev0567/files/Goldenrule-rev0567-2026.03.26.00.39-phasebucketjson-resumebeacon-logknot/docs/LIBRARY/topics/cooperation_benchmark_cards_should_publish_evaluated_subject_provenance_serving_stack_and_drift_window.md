# Cooperation benchmark cards should publish evaluated-subject provenance, serving stack, and drift window

A compact cooperation benchmark card is still too weak if the published result quietly depends on **which model or agent deployment was actually evaluated**.
Even when the task, wrapper, judge, and scoring rule are fixed, a cooperation result can move because the evaluated subject was a different provider endpoint, a different dated model marker, a different local weight snapshot, a different serving engine or quantization stack, or a rolling alias that changed during the evaluation window.

Recent evaluation work makes the archive rule clear:

- `RS-GR-094` argues that empirical LLM studies should report model versions, configurations, customizations, and the surrounding tool architecture rather than treating “the model” as a self-explanatory object.
- `RS-GR-095` shows that users rely on version-pinned API endpoints for consistency even though provider-side model or infrastructure changes can remain practically unmonitored, which means deployment drift is part of the evaluation contract.
- `RS-GR-096` shows that deployment scaffolds and evaluation format can move measured safety by meaningful margins, which supports per-model, per-configuration testing rather than assuming one architecture or serving posture stands in for another.
- `RS-GR-097` shows that unofficial or shadow API providers can diverge materially from the official models they claim to expose, which means endpoint provenance itself belongs on the benchmark card.

## Minimum contract

Whenever a retained cooperation result depends on a particular model or agent deployment, publish four short fields on the card or neighboring compact receipt:

1. **evaluated-subject provenance** — provider, model family, exact model marker / endpoint / weight snapshot / commit if known, and whether the subject was official, hosted third-party, shadow API, or local open-weight;
2. **serving stack / execution substrate** — API vs local, runtime / engine / framework when material, quantization or other major inference reductions when known, and any notable provider-managed defaults that were not under experimenter control;
3. **evaluation window / snapshot date** — the date or time interval to which the retained result actually applies, especially when the endpoint is rolling or provider-managed;
4. **update / drift posture** — pinned snapshot vs rolling alias, whether repeated-run or endpoint-drift checks were performed, and whether later revalidation is required before reusing the comparison license.

If the subject is a fully pinned local artifact with frozen weights and a known serving stack, say that directly.
If the subject is a provider-managed alias, a hosted benchmark service, or a shadow API, say that directly too.

## Implementor consequence

Do not let “the model” become an underspecified benchmark subject.
A retained cooperation result from a dated provider marker, a rolling alias, a locally hosted open-weight stack, and a shadow API endpoint are not automatically the same evaluation object.
If the endpoint can drift, if the provider may silently change infrastructure, or if the benchmark relies on a third-party compatibility layer, the comparison license should narrow accordingly.

## Archive consequence

Keep the retained object tiny.
One short subject-provenance / serving-stack / evaluation-window / drift-posture quartet is enough.
That prevents future sessions from laundering endpoint identity or deployment drift into an inheritor-facing cooperation gain while still keeping the archive compact.
