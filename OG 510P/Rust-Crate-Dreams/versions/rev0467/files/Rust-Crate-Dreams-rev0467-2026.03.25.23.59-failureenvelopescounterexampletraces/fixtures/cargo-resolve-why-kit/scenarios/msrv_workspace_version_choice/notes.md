# Scenario — mixed-MSRV workspace version choice

Goal: show that a resolver explanation bundle should freeze **MSRV policy** and **workspace membership** when explaining why one version was selected.

Workspace sketch:

- member `a`: `rust-version = "1.62"`, depends on `clap = "4.2"`
- member `b`: no explicit `rust-version`, depends on `clap = "4.5"`
- workspace resolver: `"3"`
- `resolver.incompatible-rust-versions = "fallback"`

Interesting outcome:

- one shared `clap` version is selected,
- the choice is influenced by mixed-workspace MSRV pressure,
- and the explanation should be careful not to claim Cargo explored and reported every rejected branch.
