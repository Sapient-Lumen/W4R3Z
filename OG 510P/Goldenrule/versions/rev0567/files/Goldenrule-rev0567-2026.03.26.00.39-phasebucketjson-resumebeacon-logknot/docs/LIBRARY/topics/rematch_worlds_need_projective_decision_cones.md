# Rematch worlds need projective decision cones

The family `10/20/50/100` direct classifier had already become nearly probe-free, but one small handoff hazard remained: the normal form still described the generic case as “divide by `w_hazard` to get `rho`” and then separately mentioned the zero-hazard exception.

That is operationally correct, but it still leaves a fake singularity in the inheritor’s interface.

The tighter form is to stop centering the story on division and instead write the final choice directly in homogeneous coordinates:
- `B = baseline_nonhazard_surplus`
- `H = w_hazard`

On the nonnegative half-plane `H >= 0`, classify by comparing `B` against the three threshold rays:
- `B = tau(10) * H`
- `B = tau(10000) * H`
- `B = tau(20) * H`

That yields a true cone partition:
- `H = 0, B < 0` -> always material
- `H > 0, B < tau(10)H` -> always material
- `H > 0, tau(10)H < B < tau(10000)H` -> low-cap stability then material
- `H > 0, tau(10000)H < B < tau(20)H` -> stability, then mid-cap material, then tail stability
- `H > 0, B > tau(20)H` -> always stability
- `H = 0, B > 0` -> always stability
- `H = 0, B = 0` -> exact tie on every checked cap

This matters for three reasons.

First, it removes the last artificial branch from the direct classifier. The inheritor no longer needs one rule for `w_hazard > 0` and another for `w_hazard = 0`; the zero-hazard axis is just part of the same geometric contract.

Second, it exposes the real invariance: only **ratios** of declared preference weights matter. Positive global rescaling cannot change the strict class because the classifier is homogeneous.

Third, it shows that cap-sensitive behavior requires `H > 0`. The zero-hazard axis carries only robust material, robust stability, or total tie. So once an inheritor explicitly sets `w_hazard = 0`, there is nothing left for cap probes to diagnose.

Pointers:
- report: `artifacts/reports/rematch_proxy_delta_projective_decision_cone_snapshot_20260306.md`
- builder: `scripts/report/build_rematch_proxy_delta_projective_decision_cone_snapshot.py`
- validator: `scripts/test/check_rematch_delta_projective_decision_cones.py`
