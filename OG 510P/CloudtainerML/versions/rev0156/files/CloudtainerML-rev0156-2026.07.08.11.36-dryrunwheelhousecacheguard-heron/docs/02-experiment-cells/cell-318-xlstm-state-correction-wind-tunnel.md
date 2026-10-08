# CELL-318 — xLSTM State-Correction Wind Tunnel

Priority: P0

Status: coded-native-frontier

Question: Is robust state correction the mechanism that makes gated subquadratic architectures attractive at tiny scale?

Cheap first run: Run REV0032_XLSTM_STATE_CORRECTION_SMOKE.json; compare non-oracle state policies across reset/noise/drift regimes.

Metrics: mae, correction_lag, overshoot, cost, score

Required baselines: additive_no_forget, fixed_decay_state, delta_residual_gate, xlstm_like_input_forget_gate, oracle_correction_gate

Stop condition: Escalate only if gated correction wins beyond regimes hand-built for it.
