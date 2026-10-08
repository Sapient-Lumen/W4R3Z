# Frontier salience snapshot — 2026-03-17 (56)

This pass did **not** promote a new lane.
It sharpened an already-strong cross-cutting proposal:

- **P-0522 Crate Persistence Surface Pack Kit** — because the archive still needed a more reviewable answer to the question “what exactly do these durable bytes mean, and why should I trust that answer?”

## Main judgment

The next worthy move here was **not** another serializer helper, another embedded store, another migration runner, or another async file wrapper.
Those already cover important substrate slices.

The sharper missing layer is the **receiver-facing persistence contract** above them, especially once three more facts are separated cleanly:

- explicit **compatibility-authority policies**,
- explicit **atomicity-scope reports**,
- explicit **recovery-witness receipts**,
- plus the already-added contract-level, write-path, failure-model, compatibility-window, recovery-posture, and migration artifacts.

That move is better grounded now because:

- `std::fs::File` distinguishes `sync_data` and `sync_all`, and says `Drop` ignores close errors;
- `std::fs::rename` replaces an existing destination on the same mount point but does not work across mount points;
- `tempfile::NamedTempFile::persist` says neither file contents nor the containing directory are synchronized when it returns;
- `atomic-write-file` explicitly documents no-intermediate-state overwrite semantics;
- Tokio’s `fs` module still runs ordinary blocking file operations behind `spawn_blocking`, which is useful convenience but not a new durability model;
- `serde-reflection`, Postcard, and `revision` provide different kinds of compatibility evidence;
- and redb documents both automatic crash/power-loss recovery and a slower integrity-check/repair path for suspected external modification.

So the gap is no longer “Rust cannot persist things safely”.
The gap is that maintainers still rarely publish a **reviewable compatibility-authority / atomicity-scope / recovery-witness contract** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0451 Cfg Availability Ledger Kit** — still the sharpest item-level conditional-support truth lane.
5. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest ambient-power review lanes.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
7. **P-0524 Crate Example Surface Pack Kit** — still the strongest first-success support lane.
8. **P-0525 Crate Diagnosis Surface Pack Kit** — still the strongest steady-state troubleshooting lane.
9. **P-0522 Crate Persistence Surface Pack Kit** — stronger now because compatibility authority, atomicity scope, and recovery witnesses make durable-byte promises more reviewable instead of leaving them half-implied.
10. **P-0513 Crate Runtime Handoff Pack Kit** — still the strongest post-failure support-bundle lane.

## Why this won over adjacent candidates right now

- It beat **more upgrade-pack follow-ons** because persisted-state promises still need their own authority and recovery language above code-migration support.
- It beat **more resource/lifecycle follow-ons** because queues, workers, and shutdown truth still do not tell a downstream user what durable bytes mean after a restart.
- It beat **more serializer/storage-engine ideas** because the substrate is already good enough that the sharper gap is contract publication, not raw persistence capability.
- It beat **more docs.rs or example-surface work** because persisted-state risk remains one of the least reviewable support surfaces even in otherwise well-documented crates.

## What changed in the archive

Added:
- `meta/frontier-salience-2026-03-17-56.md`
- `fixtures/crate-persistence-surface-pack-kit/compatibility-authority.policy.schema.json`
- `fixtures/crate-persistence-surface-pack-kit/atomicity-scope.report.schema.json`
- `fixtures/crate-persistence-surface-pack-kit/recovery-witness.receipt.schema.json`
- `fixtures/crate-persistence-surface-pack-kit/atomic_no_intermediate_state_mistaken_for_power_loss_durability/`
- `fixtures/crate-persistence-surface-pack-kit/postcard_stable_wire_claim_vs_serde_shape_guard/`
- `fixtures/crate-persistence-surface-pack-kit/repair_path_documented_but_unwitnessed_for_current_surface/`
- `entries/2026-03-17-236.md`

Updated:
- `proposals/crate-persistence-surface-pack-kit.md`
- `meta/crate-persistence-surface-product-plan-2026-03-17.md`
- `meta/crate-persistence-surface-lanes-2026-03-17.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- stable wire specifications,
- schema snapshots under version control,
- Serde-shape guesses,
- no-intermediate-state overwrite helpers,
- synced-data vs durable-directory-entry boundaries,
- automatic crash recovery,
- and explicit repair tooling

into one fake “durable bytes” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/std/fs/struct.File.html
- https://doc.rust-lang.org/std/fs/fn.rename.html
- https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- https://docs.rs/atomic-write-file/latest/atomic_write_file/
- https://docs.rs/tokio/latest/tokio/fs/index.html
- https://docs.rs/serde-reflection/latest/serde_reflection/
- https://docs.rs/postcard/latest/postcard/
- https://docs.rs/revision/latest/revision/
- https://docs.rs/redb/latest/redb/struct.Database.html
