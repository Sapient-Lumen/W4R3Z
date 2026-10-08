# Rematch worlds need cap-robustness probe contracts

The archive had already shown two different cap-sensitive contracts for the final family-`10/20/50/100` two-anchor choice:
- a three-cap fixed signature `[10, 20, 10000]` that classifies all four strict path classes,
- and a two-step adaptive tree rooted at cap `10000` that does the same classification with two probes in the worst case.

Those are the right tools when the inheritor cares about the **exact path shape** as budget rises. But many handoff moments ask a smaller question: *can the declared additional-budget cap ever overturn the final choice at all?*

For that smaller question, the middle strict boundary `tau(10000)` is unnecessary. It only separates the two already cap-sensitive subclasses. Once those are merged, the problem collapses to three robustness classes:
- robust material: `rho < tau(10)`;
- cap-sensitive: `tau(10) < rho < tau(20)`;
- robust stability: `rho > tau(20)`.

That means the unique minimal non-adaptive probe pair is just `[10, 20]`.
- cap `10` is forced because only it separates robust material from the cap-sensitive middle class;
- cap `20` is forced because only it separates the cap-sensitive middle class from robust stability;
- cap `10000` drops out because it only distinguishes *which kind* of cap sensitivity occurs, not whether cap sensitivity exists.

This also gives two symmetric early-stop adaptive trees:
- probe `10` first if you want the fastest robust-material certificate;
- probe `20` first if you want the fastest robust-stability certificate.

So future inheritors should keep three distinct probe contracts straight:
- `[10, 20, 10000]` for fixed strict-path reporting,
- `10000 -> (10 or 20)` for adaptive strict-path diagnosis,
- `[10, 20]` for cap-robustness triage.

Pointers:
- report: `artifacts/reports/rematch_proxy_delta_robustness_probe_snapshot_20260306.md`
- builder: `scripts/report/build_rematch_proxy_delta_robustness_probe_snapshot.py`
- validator: `scripts/test/check_rematch_delta_robustness_probes.py`
