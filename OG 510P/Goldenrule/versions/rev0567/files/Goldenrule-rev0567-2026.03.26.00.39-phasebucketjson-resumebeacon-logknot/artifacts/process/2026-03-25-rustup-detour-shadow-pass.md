# 2026-03-25 rustup-detour shadow pass

## Boundary observed locally

- `make doctor` still fails only at the Rust boundary: native `cargo` absent, native `rustc` absent, JuNest binary absent.
- A resumed cloudtainer shadow pass successfully refreshed the static Rust queue through seed-loader, bundle-plan, patchset, and patch-shard generation before the wrapper terminated again.
- Targeted follow-up refreshes succeeded for `RUST_PATCH_PREFIX_FRONTIER`, `RUST_COMEBACK_CARD`, `RUST_COMEBACK_EXECUTION_CARD`, and `CLOUDTAINER_RUST_RECOVERY_CARD`.

## Durable additions from this pass

- `docs/CLOUDTAINER_USERSPACE_RUSTUP_DETOUR.md`
- `docs/RUST_PATCH_PREFIX_FRONTIER.md`
- `artifacts/reports/rust_patch_prefix_frontier.json`
- refreshed comeback/recovery cards and reports
- `docs/RESEARCH_SOURCES.md` entries `RS-GR-556` through `RS-GR-559`

## Why these were worth keeping

The archive already had a strong static comeback plan, but it still jumped from “JuNest missing” straight to “wait for another machine.” This pass keeps the canonical blocked-session lane intact while adding one smaller userspace recovery idea for the first later machine that has HTTPS egress but still no system Rust: rustup into archive-local homes, with the repo's own `rustfmt` requirement carried forward.

## Recommended next move

1. In still-blocked sandboxes, keep using `make cloudtainer-shadow-pass-medium` plus the comeback cards.
2. On the first egress-capable machine with no system Rust and no JuNest, try the userspace rustup detour before giving up on local Rust entirely.
3. After any successful bootstrap, verify the exact first shard witness before widening to broader Rust tests.
