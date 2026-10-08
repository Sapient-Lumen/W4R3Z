# CELL-341 — Multi-Hop Boundary Reachability Training

P0 trained-tiny escalation. Tests whether depth can repair boundary copy only when a transitive relay path exists.

Fresh code: `experiments/tiny_boundary_depth_training/tiny_boundary_depth_train.py`.

Promotion guard: success must track `depth_reachable_fraction`, not simply mask label or dense capacity.
