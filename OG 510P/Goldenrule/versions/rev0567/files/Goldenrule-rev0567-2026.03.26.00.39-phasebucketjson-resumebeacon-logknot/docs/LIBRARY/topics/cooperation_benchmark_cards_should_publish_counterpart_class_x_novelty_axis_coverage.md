# Cooperation benchmark cards should publish counterpart-class × novelty-axis coverage

Two existing archive lessons are now mature enough to fuse into one compact implementation rule:

- `RS-GR-049` says cooperation claims depend on **who the policy is paired with** (other models, scripted partners, humans).
- `RS-GR-037` says zero-shot coordination depends separately on **what changed** (new partners, new environments, and downstream human collaboration effects).

So one flat cooperation score is no longer an inheritor-grade object.
A compact benchmark card should instead expose a small coverage grid:

1. **counterpart class** on one axis:
   - same-family / self-play,
   - unfamiliar model partners,
   - scripted partners,
   - human or human-proxy partners.
2. **novelty axis** on the other:
   - partner novelty,
   - environment novelty,
   - institution novelty when rules/governance/search/rematch semantics change.

The retained object can stay small.
It does **not** require another wide report family.
A single card can mark which cells were actually tested, which remain untested, and which headline claims are therefore justified.

## Implementor consequence

Before declaring that a Golden Rule policy “generalizes,” publish the tested cells of this grid.
A system that succeeds only in self-play on a fixed world should not inherit the same label as one that also survives unfamiliar partners, changed environments, or human interaction.

## Archive consequence

Keep the publication contract compact:
- one coverage grid,
- one aggregation rule if cells are combined,
- and one explicit list of untested cells.

That is enough to prevent future sessions from laundering partial interoperability into a universal cooperation headline.
