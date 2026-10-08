# rev0037 scout notes — learned bridge, route/gain, posthoc sparse gates

The deep move this turn was not another broad paper sweep. It was to harden the boundary-repair lane by asking whether a tiny trained model can discover bridge edges from an overcomplete candidate set.

Newly useful sources:

- Boundary Repair remains the core target: locality and reachability are different, and fixed block masks can disconnect adjacent cross-boundary tokens.
- Sparse Attention Post-Training adds a posthoc-sparsification counterpoint to end-to-end learned sparse gates.
- Variational Routing is parked as a P1 uncertainty-router idea: routers may need calibrated uncertainty before choosing sparse/repair/dense modes.

Fresh result summary:

- `tiny_learned_boundary_mask` solves the copy task and ranks true bridge edges top-k, but soft gates do not harden above a naive threshold.
- `tiny_route_gain_train` suggests importance-aware routing is a stronger first baseline than explicit gain in the constrained readout.

The next honest escalation is sparse-post-training or annealed hard-gate repair on the boundary task, not another symbolic mask table.
