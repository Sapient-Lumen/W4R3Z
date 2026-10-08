# Rev0010 scout notes

## New high-value additions

- **EASE-TTT / evidence-aligned adaptation**: retrieval can be used as soft supervision for query-side attention adaptation while preserving the full context.
- **Parametric memory vs KV memory**: adapter/parameter memory is most interesting when KV evidence is missing or compressed, and dangerous when stale.
- **Still / single-pass latent compaction**: query-independent latent slots are attractive, but isolated needles are the obvious failure mode.
- **SMT / supervised memory labels**: decoupling memory labels from one-step update learning is a strong bridge from tensor probes to tiny trained recurrent memory.
- **SparseX / segment reuse** and **SCD / state patching**: cache reuse is becoming a semantic state-transfer problem, not just a prefix-cache optimization.

## Working intuition shift

The biggest shift is that compression is not one thing. This revision separates: query supervision, parametric prior, latent compactor, segment reuse, and memory-transition teacher labels. These roles should not be forced into a single leaderboard.

## Next questions

1. Which rev0010 probes deserve a tiny trained-model escalation?
2. Should latent compaction be judged query-independently or with query-aware anchors?
3. Can adapter memory be safely gated when context and parameter memory disagree?
4. Can evidence-target noise make test-time adaptation worse than full-context base inference?
5. Does graph/report refactoring now make probe comparison easier enough to justify more probes?
