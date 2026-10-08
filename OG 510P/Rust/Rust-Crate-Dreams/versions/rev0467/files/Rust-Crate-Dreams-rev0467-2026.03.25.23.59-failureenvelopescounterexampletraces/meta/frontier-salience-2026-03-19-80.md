# Frontier salience snapshot — 2026-03-19 (80)

This pass did **not** add another serializer, another migration runner, another embedded database, or another “atomic save” helper.
It sharpened a top-ranked support-surface lane:

- **P-0522 Crate Persistence Surface Pack Kit** — because Rust now has real format, file-write, and storage-engine substrate, but still lacks one boring receiver-facing contract for publication target, identity retention, durability boundary, compatibility authority, and recovery evidence.

## Main judgment

The next worthy move here was **not** more substrate.
That substrate already exists.

The sharper missing layer is the **joined persistence contract** above today’s substrate, especially once five facts stay explicit:

- **publication-target truth** — which object is actually replaced or committed, including symlink-versus-target semantics,
- **identity-retention truth** — which metadata classes survive replacement and which can drift,
- **durability-boundary truth** — what success means at return time,
- **compatibility-authority truth** — why a stable-format claim should be trusted,
- **recovery-witness truth** — which recovery/repair paths were actually observed rather than merely declared.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces;
- `std::fs::File` documents `sync_all` / `sync_data` and still warns that close errors are ignored on drop;
- `std::fs::rename` still only works on the same mount point and has platform-specific replace behavior;
- `tempfile::NamedTempFile::persist` still says replacement is atomic, while also warning that contents and containing directory are not synchronized on return;
- `atomic-write-file` now documents no-intermediate-state replacement, but also documents symlink replacement and metadata-retention limitations;
- `tokio::fs` still performs ordinary file IO via `spawn_blocking`, which helps ergonomics without creating a stronger commit guarantee;
- redb documents automatic recovery from crashes / power loss and a distinct integrity-check / repair boundary for suspected external modification;
- Postcard documents a stable wire format, while `serde-reflection` and `revision` show different, weaker-or-different compatibility authority classes.

So the gap is no longer “Rust lacks persistence building blocks”.
The gap is that teams still rarely get a **reviewable crate-authored persisted-state promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth is so often missing.
3. **P-0522 Crate Persistence Surface Pack Kit** — now a stronger implementation-ready lane because the substrate below it is real and the receiver-facing contract above it is still weak.
4. **P-0521 Crate Resource Surface Pack Kit** — now a strong support lane because waiting-room truth is finally concrete.
5. **P-0524 Crate Example Surface Pack Kit** — still a strong first-success lane.
6. **P-0525 Crate Diagnosis Surface Pack Kit** — still a strong first-diagnosis lane.
7. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
8. **P-0483 Public API Readiness Bundle Kit** — still a strong joined release-review lane.
9. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest adoption-trust lanes.
10. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
11. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
12. **P-0515 Crate Off-Ramp Pack Kit** — still a strong survivability / supportiveness follow-on.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0519** pass because the support stack still needed a more concrete answer for “what exactly did the save path change?” before going further into ambient-power posture.
- It beat a deeper **P-0523** pass because test-surface truth matters, but today’s persistence substrate makes durable-byte support unusually buildable right now.
- It beat more **foreign-package shipping** work because the archive already has several fresh shipping-contract revisions and still needed a stronger core supportiveness lane.
- It beat more **pathfinder** work because the ecosystem-choice lane is already strong enough that the archive now benefits more from tightening what happens *after* a crate is chosen.

## What changed in the archive

Added:
- `entries/2026-03-19-260.md`
- `meta/frontier-salience-2026-03-19-80.md`
- `meta/crate-persistence-surface-product-plan-2026-03-19.md`
- `meta/crate-persistence-surface-lane-boundaries-2026-03-19.md`
- `fixtures/crate-persistence-surface-pack-kit/README.md`
- `fixtures/crate-persistence-surface-pack-kit/publication-target.report.schema.json`
- `fixtures/crate-persistence-surface-pack-kit/identity-retention.report.schema.json`
- `fixtures/crate-persistence-surface-pack-kit/symlink_replace_changes_link_not_target/README.md`
- `fixtures/crate-persistence-surface-pack-kit/symlink_replace_changes_link_not_target/publication-target.report.example.json`
- `fixtures/crate-persistence-surface-pack-kit/atomic_replace_loses_xattrs_acls_and_timestamps/README.md`
- `fixtures/crate-persistence-surface-pack-kit/atomic_replace_loses_xattrs_acls_and_timestamps/identity-retention.report.example.json`
- `fixtures/crate-persistence-surface-pack-kit/tokio_fs_async_surface_does_not_upgrade_commit_contract/README.md`
- `fixtures/crate-persistence-surface-pack-kit/tokio_fs_async_surface_does_not_upgrade_commit_contract/durability-boundary.report.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-persistence-surface-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
