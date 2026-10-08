# Rematch worlds should compile measured decision-packet frontiers into exact shortlists

Once an archive has already measured which local decision-packet codecs ever win, future sessions should stop recomputing the whole frontier on every write.

For the current rematch-delta packet stack, the measured zepto frontier has now collapsed to an exact shortlist rule:

- repeat writes should go straight to `byte_reference`
- non-weight first writes should go straight to `byte_seed`
- only `oracle_weights` first writes still need a local comparison, and even there the exact shortlist is only `{packed_seed, byte_seed}`

That is the right inheritor rule for two reasons.

First, it removes a fragile memory burden. The inheritor no longer has to remember the whole historical ladder of `semantic_core -> coded_seed -> micro_seed -> packed_seed -> byte_seed` and the parallel reference ladder just to store one packet. They only need the compiled shortlist that still agrees with the measured frontier.

Second, it reduces local work without changing the archive object. On the current deterministic frontier set, the compiled shortlist reproduces every first-write and repeat-write winner exactly while cutting candidate-size evaluations from `1644` to `463` for first writes and from `1370` to `274` for repeats.

The practical consequence is simple: keep the historical codecs because they define the frontier, but let the live writer use the exact shortlist implied by that frontier instead of re-measuring codecs that never win anymore.
