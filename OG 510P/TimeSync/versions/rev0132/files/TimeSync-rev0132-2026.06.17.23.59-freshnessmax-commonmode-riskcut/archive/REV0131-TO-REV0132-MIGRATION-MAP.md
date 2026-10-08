# Migration map — rev0131 to rev0132

## Code

- `tools/multisource_adjudicator.py` now computes combined `freshness.max_staleness_ms` using the maximum input value.
- The same tool now preserves input source-diversity/common-mode summaries when producing the combined `source_diversity_posture` hook.

## Tests

- `tests/multisource-adjudication.yaml` now checks output freshness and diversity posture.
- `TV-132-001` adds a generated fallback local-assessed-state example.

## Consumer impact

Consumers should expect multi-source adjudicated states to be more conservative when one admitted input is stale or when source-diversity evidence indicates same-root/common-mode risk. No TimeState core field was added.
