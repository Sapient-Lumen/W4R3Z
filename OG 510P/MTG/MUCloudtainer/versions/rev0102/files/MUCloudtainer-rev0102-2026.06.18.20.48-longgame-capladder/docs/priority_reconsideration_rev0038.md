# Priority reconsideration after rev0038

The ranker itself is not the bottleneck.  The labeler is.

The rev0038 screen increased the concentration of interesting situations: 14 sampled disagreement frames produced 6 decisive labels, while prior unscreened/budgeted runs often spent most rollouts on ties.  The next work should continue to improve label selection and branch allocation before trying larger models.

Current priority order:

```text
1. Compare disagreement-screened labels against unscreened/adaptive labels on matched situations.
2. Increase decisive branch labels by spending rollouts where public policies genuinely disagree.
3. Use C++ segment gates for branch-heavy data collection once no-choice segments become a bottleneck.
4. Run larger MAP-Elites/meta-rank panels only on nontruncated promoted tables.
5. Develop search targets for unchosen gameplay actions after label confidence improves.
```

Pushback: disagreement screening can bias the corpus toward policy-visible controversies.  That is useful for learning from unchosen alternatives, but it may miss quiet high-value decisions where all current policies are wrong together.  Future collectors should mix:

```text
disagreement-screened frames
high-regret frames from prior branch labels
random manageable frames
rare-action frames
```
