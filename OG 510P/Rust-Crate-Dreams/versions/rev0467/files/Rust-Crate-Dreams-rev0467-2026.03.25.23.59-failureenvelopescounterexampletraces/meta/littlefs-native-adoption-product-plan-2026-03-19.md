# LittleFS Native Adoption Kit — product plan (2026-03-19)

This note sharpens **P-0527 LittleFS Native Adoption Kit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to be “the one true embedded filesystem framework.”
It should be a **small crate family plus CLI** that helps embedded teams publish one reviewable answer to:

- which littlefs engine/backend they are actually using,
- which flash/storage contract they are assuming,
- whether async behavior is native, cooperative, or wrapped-blocking,
- whether the produced image is compatible with the target littlefs profile,
- and what evidence they have for recovery after interrupted writes.

The missing value is now the **boring adoption and evidence layer** above today’s engines and adapters.

## What the crate should provide other people

For firmware teams, embedded platform maintainers, and tooling authors, the crate should provide:

1. **One reviewable storage-adapter contract** instead of each project inventing ad hoc flash assumptions.
2. **One compatibility-witness workflow** instead of “it mounted on my board once.”
3. **One power-cut evidence workflow** instead of vague copy-on-write folklore.
4. **One host-side image toolchain** for pack/list/diff/inspect operations.
5. **One compact support bundle** that can travel between maintainers, CI, and board labs.

## Three first-class review objects

### 1. Storage adapter receipt

Named classes for `0.1` should focus on adapter truth such as:

- `embedded_storage_blocking`
- `embedded_storage_async_native`
- `embedded_storage_async_cooperative`
- `wrapped_blocking_manual_review`
- `bad_block_policy_declared`
- `partition_geometry_declared`

This object should answer:

- what read/program/erase granularities were assumed,
- whether async behavior is native or merely wrapped,
- what yield/sync boundaries exist,
- and whether simulated or RAM-backed storage was used.

### 2. Compatibility witness receipt

Named classes for `0.1` should focus on format/behavior truth such as:

- `mount_roundtrip_passed`
- `dir_ops_passed`
- `file_rewrite_passed`
- `custom_attributes_unchecked`
- `upstream_crosscheck_passed`
- `manual_review_required`

This object should answer:

- which fixture/image corpus was exercised,
- which backend was used,
- whether mount/read/write/delete behavior matched expectations,
- and what compatibility claim is actually warranted.

### 3. Power-cut run report

Named classes for `0.1` should focus on resilience truth such as:

- `interruption_injected`
- `last_known_good_state_recovered`
- `partial_write_lost_but_fs_consistent`
- `mount_failed_after_interruption`
- `campaign_scope_limited`
- `manual_review_required`

This object should answer:

- where interruptions were injected,
- what state survived remount,
- whether the filesystem remained mountable,
- and which failure model was actually exercised.

## Recommended `0.1` command surface

### `cargo littlefs doctor`
Inspect a backend and emit:
- `storage-adapter.receipt.json`
- `littlefs-doctor.report.json`

### `cargo littlefs compat`
Exercise a compatibility corpus and emit:
- `compatibility-witness.receipt.json`

### `cargo littlefs powercut`
Run an interruption campaign and emit:
- `powercut-run.report.json`

### `cargo littlefs image pack|ls|diff`
Host-side image creation and inspection.

### `cargo littlefs bundle`
Produce one compact `.littlefsbundle.zip` containing reports, notes, and image metadata.

## Recommended crate/workspace split

- `littlefs_engine_bridge`
- `littlefs_embedded_storage`
- `littlefs_embedded_storage_async`
- `littlefs_image`
- `littlefs_compat`
- `littlefs_powercut`
- `cargo-littlefs-kit`

## `0.1` artifact set

Core artifacts should be:
- `littlefs.toml`
- `storage-adapter.receipt.json`
- `compatibility-witness.receipt.json`
- `powercut-run.report.json`
- `littlefs-doctor.report.json`
- `image-diff.report.json`
- `notes.md`

## Discovery order

1. **Storage adapter import**
   - geometry
   - granularities
   - blocking/async truth
2. **Compatibility corpus selection**
   - image fixtures
   - operation fixtures
3. **Compatibility witness generation**
   - mount/read/write/delete
   - backend identity
4. **Power-cut campaign**
   - injection points
   - remount/recovery classification
5. **Image tooling**
   - pack/list/diff/inspect
6. **Bundle export**
   - receipts
   - image metadata
   - manual-review notes

## Ranking discipline

A good `0.1` should not treat “the image mounted once” as the verdict.
It should keep separate:

- `storage_truth_known`
- `compatibility_truth_known`
- `powercut_truth_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- upstream littlefs design constraints and format expectations
- existing Rust FFI wrappers (`littlefs2`, `littlefs2-sys`)
- emerging pure-Rust backend work (`littlefs-rust-core`, `littlefs-rust`)
- `embedded-storage` / `embedded-storage-async`
- Embassy flash utilities and RAM simulation

### Do not flatten into one fake verdict
- “pure Rust exists now”
- “async storage traits exist now”
- “the filesystem mounted”
- “the image tool packed bytes”
- “copy-on-write means every power-loss claim is proven”

## Preferred proving grounds

- a roundtrip image that mounts on both the reviewed Rust path and an upstream-compatible path
- a file rewrite interrupted between program and sync boundaries
- a partitioned flash backend imported from Embassy-style utilities
- an async flash path where busy-wait would be unacceptable and the receipt must classify the strategy honestly

## Non-goals

- not a generic embedded database
- not a new OTA framework
- not a generic persistence-policy crate
- not a proof that every flash controller is interchangeable

## MVP API sketch

```rust
pub fn inspect_storage_adapter(cfg: &AdapterConfig) -> Result<StorageAdapterReceipt>;
pub fn witness_compatibility(case: &CompatCase) -> Result<CompatibilityWitnessReceipt>;
pub fn run_powercut_campaign(case: &PowercutCase) -> Result<PowercutRunReport>;
pub fn pack_image(plan: &ImagePlan) -> Result<Vec<u8>>;
pub fn diff_image_bytes(old: &[u8], new: &[u8]) -> Result<ImageDiffReport>;
pub fn write_bundle(bundle: &LittleFsBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Track pure-Rust backend maturity without assuming one crate has already won.
- Keep compatibility witnesses separate from convenience API growth.
- Preserve manual-review classes whenever async behavior, bad-block behavior, or power-cut scope cannot be stated honestly.
- Keep the kit small and evidence-first.

## Sources

- https://github.com/littlefs-project/littlefs
- https://docs.rs/crate/littlefs2/latest
- https://github.com/trussed-dev/littlefs2-sys
- https://github.com/littlefs-project/littlefs/issues/1112
- https://docs.rs/littlefs-rust/latest/src/littlefs_rust/lib.rs.html
- https://docs.rs/embedded-storage-async/latest/embedded_storage_async/
- https://docs.rs/embassy-embedded-hal/latest/embassy_embedded_hal/
- https://github.com/littlefs-project/littlefs/issues/143
