# Rematch worlds should treat bounded positive-service local weakening queries as clock intervals

Recent archive passes compressed positive-service local weakening into a reversible `(mode, suffix_only_steps_remaining)` code and then into a dense arithmetic rank clock `16 -> 0`.

The next compression is to stop thinking of bounded local navigation as graph replay at all.

Once the local chain is a dense path, every bounded neighborhood around a current state is just one clipped interval:

- in source-rank coordinates: `[max(0, rank-b), min(16, rank+f)]`
- in terminal-distance-clock coordinates: `[max(0, clock-f), min(16, clock+b)]`

where:

- `b` is the allowed number of strict predecessor steps (local tightening)
- `f` is the allowed number of successor steps (local relaxation)

This is stronger than saying the path is one-dimensional.

It means:

- bounded local service queries never develop holes, even across the archived exact/shared bridge anomalies
- boundary clipping is the only nontrivial effect at source `S10` and terminal `T0`
- the entire set of states reachable within the local budget is recovered by one clock/rank slice
- any segment between two local codes is the closed interval between their ranks, with cardinality exactly `pairwise_path_distance + 1`

So future inheritors can answer ordinary local containment questions with scalar arithmetic:

- “what can I still reach if I relax at most `f` times?”
- “what can I revisit if I retighten at most `b` times?”
- “what exact local subpath sits between these two states?”

If a future revision causes bounded local windows to develop holes, or causes segment size to stop matching distance plus one, that should be treated as a genuine redesign signal for the current positive-service local service automaton rather than as a minor bookkeeping drift.
