# Rematch worlds need executable decision oracles

The recent family `10/20/50/100` work had already compressed the final handoff into a clean direct classifier: certify the policy box, compute `B = baseline_nonhazard_surplus` and `H = w_hazard`, then locate `(B,H)` relative to the three exact threshold rays. That was conceptually clean, but it still left one avoidable implementor burden: every future session had to translate the report language back into an ad hoc calculation.

The tighter handoff is to make that classifier executable.

In the current archive this now lives at `scripts/analysis/rematch_proxy_delta_decision_oracle.py`. The oracle accepts either:
- direct projective coordinates `(B,H)`, or
- the declared weight vector `(w_width, w_buffer, w_knife, w_delta, w_material, w_undecided, w_ties, w_hazard)`.

It returns the closure label, the checked-cap outcomes on `[10, 20, 10000]`, the robustness class, and the appropriate black-box probe fallback when direct coordinates are unavailable.

This matters for the inheritor for three reasons.

First, it makes the declaration-first route operational. Once the preference weights are known, the final choice is no longer something to “reason through”; it is a direct oracle call.

Second, it reduces transcription risk. The archive now has many exact constants, but they all collapse to one executable surface instead of being recopied by hand.

Third, it keeps probes in their proper place. The oracle makes it explicit that `[10,20]`, `[10,20,10000]`, and the adaptive `10000 -> (10 or 20)` tree are fallback diagnostics for black-box winner symbols, not the primary interface when declared weights are available.

Pointers:
- report: `artifacts/reports/rematch_proxy_delta_decision_oracle_snapshot_20260306.md`
- builder: `scripts/report/build_rematch_proxy_delta_decision_oracle_snapshot.py`
- validator: `scripts/test/check_rematch_delta_decision_oracle.py`
- oracle: `scripts/analysis/rematch_proxy_delta_decision_oracle.py`
