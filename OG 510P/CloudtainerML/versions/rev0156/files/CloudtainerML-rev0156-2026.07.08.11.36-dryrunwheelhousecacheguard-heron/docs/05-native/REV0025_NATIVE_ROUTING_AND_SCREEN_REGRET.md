# Native routing and screen-regret notes — rev0025

New native probes:

- `dot_moe_transport_assignment`: dense-to-MoE assignment and route consistency.
- `group_shared_sparse_tail`: group-shared fan-in and sparse output kernel overhead.
- `sparse_frontier_isoflops`: sparse/dense/hybrid phase comparison at soft equal compute.
- `dynconv_repair_hpo`: local dynamic convolution with global bypass / anti-alias repairs.
- `polyhard_routing_optimizer`: forward-only hard-routing optimizer screen.

The big methodological change is the screen-regret report. It is meant to prevent cheap toy winners from being promoted unless they expose cost and reversal information.
