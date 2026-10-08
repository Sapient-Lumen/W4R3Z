# rev0048 public/pretrained trace gate surrogate

This probe addresses the public/pretrained trace blocker without pretending to
solve it.  It provides a deterministic offline trace-evaluation harness and a
surrogate suite shaped like common attention-head regimes.  If an external NPZ
trace bundle is supplied, the same evaluator ingests rows from that bundle.

Supported NPZ schemas:

- `scores`: float array `[rows, n]`, and `values`: float array `[rows, n, dv]`.
- or `q`: `[rows, d]`, `k`: `[rows, n, d]`, and `v`: `[rows, n, dv]`; scores are
  computed as `q @ k.T / sqrt(d)`.
- optional `value_norms`: `[rows, n]` metadata sidecar.
- optional labels: `regime`, `layer`, `head`, `position`.

The default run is **surrogate only**.  Its output must not be cited as public or
pretrained model evidence.
