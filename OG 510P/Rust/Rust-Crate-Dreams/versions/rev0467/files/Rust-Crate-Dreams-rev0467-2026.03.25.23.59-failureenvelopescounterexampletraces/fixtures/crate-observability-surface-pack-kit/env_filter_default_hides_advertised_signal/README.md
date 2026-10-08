# Scenario family — advertised signal hidden by default filter posture

This fixture family exists for crates that truthfully emit a signal, but only under a filtering posture that many downstream users will not see by default.

It is meant to catch support drift such as:

- the crate advertises an `info` or `debug` event as part of its supported observability surface,
- but the documented default `EnvFilter` / `RUST_LOG` posture only shows `warn` and above,
- or a per-layer filter hides the signal even though the main subscriber is installed,
- or a release changes the needed directive without updating the support contract.

A good observability pack should make four things explicit:

1. whether the signal is **visible by default** or only under a named filter directive,
2. whether that directive is part of the official activation recipe,
3. whether the recipe was actually observed in a witness run,
4. and whether the signal should be downgraded from `stable_query_surface` if it is too easy to mis-activate.

This family keeps “the crate emits a signal” separate from “a downstream operator can reliably see the signal they were told to expect”.
