# Cooperation benchmarks should publish information visibility and asymmetry regime

Two cooperation benchmark lanes can use the same task, counterpart class, and score metric while still measure materially different coordination problems.
If one lane gives all parties the same full state, another withholds critical facts behind private views, and another requires the partners to discover hidden asymmetries through communication, then the resulting cooperation numbers are not directly comparable.
Two recent sources make the compact archive rule clear:

- `RS-GR-067` introduces HiddenBench and shows that multi-agent LLMs perform far worse when task-relevant information is distributed across agents than when a single agent sees the full profile, tracing the gap to failures to surface unshared information rather than failures to reason once the information is disclosed.
- `RS-GR-068` introduces a human-AI common-ground benchmark with varying conditions of situation awareness, reinforcing that collaboration conclusions depend on what information is jointly visible and what must be inferred or repaired during interaction.

## Minimum contract

Whenever a cooperation benchmark includes any hidden state, asymmetric observations, or partial views, publish:

1. which task-relevant facts are **shared, private, delayed, or never observable** to each side;
2. whether the information regime is **symmetric, role-asymmetric, or dynamically changing** over time;
3. what **history window** each participant sees, including whether prior messages, actions, scores, or latent-state summaries are truncated;
4. whether participants are **told that asymmetry exists** or must discover it implicitly;
5. and whether headline results pool across multiple visibility regimes or report them lane-by-lane.

## Implementor consequence

Do not compare or pool cooperation results across lanes unless their information structure is actually aligned.
A system can look more cooperative or more competent simply because it was given a fuller shared state, because hidden information was surfaced automatically, or because the benchmark removed the need to actively probe for what the partner uniquely knows.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: shared/private state split, observability symmetry, history window, and whether asymmetry was explicit or latent.
That prevents future sessions from laundering an information-structure choice into a policy-quality claim.
