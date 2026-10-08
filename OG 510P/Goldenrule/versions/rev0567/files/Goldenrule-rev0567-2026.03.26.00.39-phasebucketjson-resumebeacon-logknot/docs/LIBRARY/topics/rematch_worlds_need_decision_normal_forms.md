# Rematch worlds need decision normal forms

The archive had already derived nearly everything needed for the final family-`10/20/50/100` handoff, but the logic was still spread across several separate passes:
- certify the policy box,
- derive the hazard-normalized scalar `rho`,
- remember the three exact thresholds,
- and then choose a probe contract only if direct classification is unavailable.

That scattering itself had become a handoff risk.

The tighter normal form is:

1. **First certify applicability.**  
   Stay inside the corner-certified family10 policy box:
   - width floor `0.00026 < floor <= 0.00129`;
   - delta ceiling `0.00822 < ceiling <= 0.01944`;
   - additional-budget cap checked on `[10, 10000]`.

2. **If declared preference weights are known, do not probe at all.**  
   Compute the baseline non-hazard surplus
   `0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties`.
   When `w_hazard > 0`, divide by `w_hazard` to get `rho`, then compare to:
   - `tau(10) = -0.000463764`
   - `tau(10000) = 0.000033068`
   - `tau(20) = 0.000313597`

   This gives the entire strict cap-path class directly:
   - `rho < tau(10)` -> always material;
   - `tau(10) < rho < tau(10000)` -> stability at low cap, then material;
   - `tau(10000) < rho < tau(20)` -> stability, then mid-cap material, then tail stability;
   - `rho > tau(20)` -> always stability.

3. **Only fall back to cap probes when the choice is black-box.**
   - exact strict-path portable record -> `[10, 20, 10000]`
   - exact strict-path live diagnosis -> `10000 -> (10 after M, 20 after S)`
   - overturn-risk portable record -> `[10, 20]`
   - overturn-risk early-stop diagnosis -> `10 -> 20` or `20 -> 10`

So the key operational correction is simple:

**Cap probes are no longer the default interface.**  
They are the fallback interface for black-box diagnosis when the inheritor cannot or does not want to compute `rho` directly from declared weights.

That keeps the archive smaller, makes the handoff procedure explicit, and prevents future sessions from paying probe cost when the direct scalar route already answers the whole question.

Pointers:
- report: `artifacts/reports/rematch_proxy_delta_decision_normal_form_snapshot_20260306.md`
- builder: `scripts/report/build_rematch_proxy_delta_decision_normal_form_snapshot.py`
- validator: `scripts/test/check_rematch_delta_decision_normal_form.py`
