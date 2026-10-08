# Cloudtainer userspace rustup detour

This note exists for the specific case where the current blocked-session diagnosis is:
- native `cargo` missing,
- JuNest binary missing (`/run/sandworm/toolroot/bin/junest` absent), and
- a later cloudtainer or handoff machine has outbound HTTPS plus permission to write under the project or `$HOME`.

The current cloudtainer recovery card still classifies the local state as `junest_binary_missing`, so the canonical move **in this sandbox** remains static shadow work. This detour is for the *next* environment that can actually fetch a toolchain.

## Why this detour is worth remembering

- `RS-GR-556`: rustup can install into caller-chosen `CARGO_HOME` / `RUSTUP_HOME` paths, so the bootstrap does not require system package manager access.
- `RS-GR-557`: rustup's `minimal` profile is the smallest working compiler lane and is explicitly suited to CI-like environments.
- `RS-GR-558`: this repo's `rust-toolchain.toml` pins `channel = "stable"` and requests the additive component `rustfmt`, so a pure minimal bootstrap is *almost* enough but should still install `rustfmt`.
- `RS-GR-559`: if a future machine needs a narrower pin than floating `stable`, rustup can install and pin a dated toolchain explicitly.
- `RS-GR-560`: once a later machine has brief egress, `cargo fetch --locked` can stage the dependency graph for later offline commands as long as `Cargo.lock` does not change.
- `RS-GR-561`: `CARGO_TARGET_DIR` gives this repo an explicit compiled-artifact scratch root, so the userspace comeback can stay easy to prune before the next archive cut.

## Suggested userspace bootstrap (egress-capable machine only)

```bash
export CARGO_HOME="$PWD/.local/cargo"
export RUSTUP_HOME="$PWD/.local/rustup"
export CARGO_TARGET_DIR="$PWD/.local/target"
export PATH="$CARGO_HOME/bin:$PATH"

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs   | sh -s -- --default-toolchain none -y

rustup set profile minimal
rustup toolchain install stable --profile minimal --component rustfmt
cargo fetch --locked
rustup show
make doctor
```

## First verification after bootstrap

Do **not** widen immediately to full `make test-quick` if the environment still feels shaky.
Use the already-curated comeback lane:

1. `make update-rust-comeback-execution-card`
2. `git apply artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch`
3. `cargo test -p gr_engine --test probe_run lift_fsm_strategy_family_lift_first_seed -- --exact`
4. `cargo test -p gr_engine --test probe_run`

This keeps the first live Rust witness small and aligned with the existing comeback plan rather than improvising a broad compile.

## Boundaries

- This note does **not** replace `docs/CLOUDTAINER_RUST_RECOVERY_CARD.md`; it extends the recovery imagination when JuNest is missing but a later machine still has userland write access and network egress.
- If HTTPS egress is unavailable, stay on the static lane (`make cloudtainer-shadow-pass-medium` and companions) and do not burn time on bootstrap churn.
- Treat `.local/cargo`, `.local/rustup`, and `.local/target` as transient scratch roots; prune them before the next retained archive cut if you used this detour on a copied working tree.
- If the future machine already has native Rust, prefer the existing native-ready lane instead of introducing a second local toolchain root.
