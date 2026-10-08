# CELL-179: Gist Sparse Unfold Trap

Priority: P1

Status: candidate

Idea: IDEA-0178

Source: SRC-0214

Cheap first run: No runnable probe yet; gist summaries route to raw chunk unfolding.

Metrics:
- needle recall
- chunk budget
- false unfold rate

Baselines:
- chunk BM25/top-k
- gist router
- recursive gist
- oracle raw chunks

Stop condition: If gist misses isolated needles, demote.
