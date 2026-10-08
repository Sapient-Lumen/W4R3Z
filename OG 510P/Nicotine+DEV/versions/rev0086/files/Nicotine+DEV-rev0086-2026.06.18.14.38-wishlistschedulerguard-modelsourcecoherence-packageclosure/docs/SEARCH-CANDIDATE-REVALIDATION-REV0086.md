# Search candidate evidence revalidation — rev0086

The Search Again candidate bytes and both executable source identities are
unchanged from rev0085. Rev0086 therefore does not manufacture a duplicate
patch or imply four fresh pytest executions.

`tools/revalidate_current_search_candidate.py` verifies the immutable rev0085
result records, candidate digest, source refs, JUnit digests, completion-marker
digests, terminal summaries, and 60-pass/1-skip outcome in each lane. It then
creates revision-current records whose provenance says `fresh_execution: false`.

```text
profiles:                 2
lanes:                    4
test cases revalidated: 244
checks:                  80/80 pass
```

This corrects a wasteful rollover pattern: validation recency belongs in an
evidence binding, while artifact origin belongs in an immutable ID and path.
