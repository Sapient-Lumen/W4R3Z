# Legacy Published Links

These are the canonical already-public wiki links that remain allowed for the older work.
They use the **Mathematics** label and should remain valid as written.

## Canonical legacy wiki links

- `[[2026.01.22 - Mathematics: Scheduling and Compiler Techniques for Metadata-Hiding Overlay Lookups]]`
- `[[2026.01.23 - Mathematics: Spectral Anonymity and Optimal Distinguishing Bounds for Random-Walk Delegation in (Possibly Directed) Overlays]]`
- `[[2026.01.25 - Mathematics: Prefix Capacities and Separation Cuts for Shared-Kernel Termination-Time Hiding]]`
- `[[2026.01.26 - Mathematics: Stop-Time Padding Addendum, Max-Mixture Separations and Tail-Sign Deadline Normal Forms]]`
- `[[2026.01.29 - Mathematics: Optimal Poset-Feasible Padding: Knapsack, Transport, and Dual Certificates for TV Privacy]]`

## Repository crosswalk

These public links correspond to the current legacy directories in `published/`:

- `[[2026.01.22 - Mathematics: Scheduling and Compiler Techniques for Metadata-Hiding Overlay Lookups]]`
  - current legacy path: `published/2026-01-22_scheduling_compiler/paper.tex`
- `[[2026.01.23 - Mathematics: Spectral Anonymity and Optimal Distinguishing Bounds for Random-Walk Delegation in (Possibly Directed) Overlays]]`
  - current legacy path: `published/2026-01-23_spectral_anonymity/paper.tex`
- `[[2026.01.25 - Mathematics: Prefix Capacities and Separation Cuts for Shared-Kernel Termination-Time Hiding]]`
  - current legacy path: `published/2026-01-25_prefix_capacities/paper.tex`
- `[[2026.01.26 - Mathematics: Stop-Time Padding Addendum, Max-Mixture Separations and Tail-Sign Deadline Normal Forms]]`
  - current legacy path: `published/2026-01-26_stop_time_padding_addendum/paper.tex`
- `[[2026.01.29 - Mathematics: Optimal Poset-Feasible Padding: Knapsack, Transport, and Dual Certificates for TV Privacy]]`
  - current legacy path: `published/2026-01-29_knapsack_transport/paper.tex`


## Maintained correction note

The 2026-01-23 spectral-anonymity link remains canonical, but rev0769 extends the repaired exact expected-chi-squared boundary through common-stationary schedules, hidden randomized lengths, and the external-audit ergodicity/tail guard. Use the t-step Frobenius form $\|\mathcal D^t\|_F^2-1$ for fixed directed/non-normal kernels, use the ordered-product form $\|\mathcal D_1\cdots\mathcal D_t\|_F^2-1$ for common-stationary time-varying kernels, use $\|\sum_t p_t\mathcal D^t\|_F^2-1$ for hidden randomized walk lengths, and treat the one-step singular-power expression over nonstationary indices as exact only when a normal/reversible side condition is certified. Decay-to-zero is an ergodicity statement, not a one-step $\sigma_2<1$ slogan; downstream receipt-side `chi2-general` MaxL cards must convert expected $\chi^2$ to a tail/pointwise bound before using `chi2_bound` by Markov, Cantelli with certified variance, evaluator quantile, pointwise cap, or stronger evidence.

## Important distinction

These legacy links are preserved because the work is already published.

The fact that these links remain canonical does **not** mean every legacy paper should remain the preferred exposition for the new Anonymity series. Some are durable theorem roots; some are better treated as narrower companions or historical roots while cleaner Anonymity-era exposition is written elsewhere.
This does **not** set the naming rule for future releases.
All new releases must use the **Anonymity** naming regime.

## Non-canonical legacy contents

The repository may contain older material inside `published/` that is not listed above.
A future operator should not assume such material has an approved public wiki link unless an explicit note says so.
