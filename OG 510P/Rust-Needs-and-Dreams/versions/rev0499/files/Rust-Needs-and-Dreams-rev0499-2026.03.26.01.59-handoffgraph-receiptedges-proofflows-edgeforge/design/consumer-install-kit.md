# Design: Consumer Install Kit (`cargo installproof`, visible candidates, install plans, and receipts)

## Goal
Turn Rust’s first-install story from a mix of Cargo defaults, prebuilt-download helpers, CI fallback glue, and tool-local logs into a **portable consumer-install boundary**.

This kit should make six things explicit:
1. **what install subject was requested**,
2. **which candidates were visible**,
3. **what policy ranked or refused them**,
4. **what plan was chosen**,
5. **what actually happened on disk**,
6. **what later consumers may import without redefining the install.**

The worthy contribution here is **not** another installer wrapper, another package-manager shim, or another self-update engine.
It is the thin leaf-level boundary above ordinary install tools that multiple higher stacks already need.

Read this together with:
- [`design/consumer-lifecycle-continuity-bundle.md`](./consumer-lifecycle-continuity-bundle.md)
- [`design/consumer-install-lane-map.md`](./consumer-install-lane-map.md)
- [`design/consumer-install-pilot-program.md`](./consumer-install-pilot-program.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/update-continuity-kit.md`](./update-continuity-kit.md)
- [`proposals/epic-consumer-install-kit.md`](../proposals/epic-consumer-install-kit.md)

## Why now
Fresh upstream signals all point the same way, and the new lane map/pilot work makes the lane split harder to blur:
- Cargo’s install docs say the packaged `Cargo.lock` is ignored by default unless `--locked` is passed, say Cargo keeps install metadata in the install root by default, and document `--no-track` as disabling that file and Cargo’s concurrent-install protection.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo packaging docs now say `--exclude-lockfile` is not for general use because some consumers expect the lockfile, including `cargo install --locked`.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo-binstall` now clearly exposes a different lane: prebuilt binary acquisition with explicit signature policy controls like `--only-signed` and `--skip-signatures`.
  https://github.com/cargo-bins/cargo-binstall
- cargo-dist’s 0.31 release added mirror-aware hosting fallback, proving that visible host order and actual selected source are now first-class install facts rather than host-page trivia.
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- `taiki-e/install-action` exposes fallback choices between `cargo-binstall` and `cargo install`, proving CI acquisition is already a composition problem instead of one canonical lane.
  https://github.com/taiki-e/install-action
- `axoupdater` already has an install-receipt concept, which is useful evidence that receipts are real but still tool-local rather than portable ecosystem substrate.
  https://docs.rs/axoupdater/latest/axoupdater/
- Rust’s 2026 flagships keep supply-chain work active through public/private dependencies and Cargo SBOM work, which increases the value of preserving package → release → install handoffs honestly.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

Taken together, that means the next missing contribution is not “help users install a tool”.
It is “make the **install event itself** portable, reviewable, and handoff-ready.”

## Core artifact family

### 1. `install-brief/v0`
A concise summary for humans and assistants:
- install subject label
- selected version / target / root summary
- candidate-class summary
- selected lane (`SOURCE_BUILD`, `PREBUILT`, `INSTALLER`, `PACKAGE_MANAGER`, `LOCAL_PATH`, `UNKNOWN`)
- verification posture summary
- ownership / managed-content summary
- freshness / review timestamp

### 2. `install-subject/v0`
Identity for the requested install:
- requested package / app / binary name
- requested version or range
- requested binary subset when relevant
- host tuple / target triple
- intended install root or mutation scope
- caller intent (`prebuilt-first`, `source-only`, `mirror-only`, `package-manager-only`, etc.)
- direct tool lane when already fixed (`cargo install`, `cargo-binstall`, package-manager import, installer import)
- local-vs-remote subject posture

### 3. `install-candidate/v0`
One visible way the subject could be obtained:
- candidate id
- class (`SOURCE_BUILD`, `PREBUILT`, `INSTALLER`, `PACKAGE_MANAGER`, `LOCAL_PATH`, `SCRIPT_IMPORT`)
- host / mirror / package-manager / local-path identity
- version / asset / target posture
- declared verification affordances (checksum, signature, attestation, none)
- lockfile posture when applicable
- support-envelope pointer when available
- explicit unknowns or import-lossiness notes

### 4. `install-catalog/v0`
The visible candidate set:
- imported `install-subject/v0`
- ordered or unordered candidate collection
- channel / host / mirror grouping
- missing-expected-candidate notes
- restricted-network or local-only posture when relevant
- exported-at timestamp and integrity metadata

### 5. `install-policy/v0`
Optional caller or org rules:
- preferred candidate classes
- allowed hosts / mirrors / issuers / package managers
- required verification levels
- whether unsigned artifacts are allowed
- whether source fallback is allowed
- whether local-path installs are allowed
- allowed roots and managed-content expectations
- `FAIL` / `WARN` / `INCONCLUSIVE` posture

### 6. `install-plan/v0`
The ranked decision before mutation:
- imported subject + catalog + policy ids
- ordered candidate list
- refusal reasons for skipped candidates such as:
  - `TARGET_MISMATCH`
  - `MISSING_VERIFICATION`
  - `HOST_UNAVAILABLE`
  - `MIRROR_PREFERRED`
  - `SOURCE_FALLBACK_DISALLOWED`
  - `PACKAGE_MANAGER_REQUIRED`
  - `POLICY_BLOCKED`
- selected candidate id
- expected verification steps
- expected local mutations

### 7. `install-receipt/v0`
What actually happened:
- imported `install-plan/v0`
- timestamp and runner identity
- fetched URLs / paths / mirrors used
- actual build or fetch lane used
- verification results and skipped checks
- source-build lock posture (`PACKAGED_LOCK`, `RECOMPUTED`, `LOCAL_LOCK`, `UNKNOWN`)
- installed files / symlinks / root mutations when practical
- manager identity and claimed managed-content scope
- warnings / partial failures / lossy imports
- backreferences to imported release/signature evidence

### 8. `install-pack/v0`
Attachable bundle linking:
- `install-brief/v0`
- `install-catalog/v0`
- optional `install-policy/v0`
- `install-plan/v0`
- `install-receipt/v0`
- imported producer-side evidence pointers
- bounded downstream handoff documents

### 9. `install-handoff/v0`
Lossy but explicit exports for downstream consumers such as:
- Distribution Contract Stack
- Update Continuity Kit
- Support / incident intake
- Policy / trust / inventory consumers
- productization stacks that need acquisition truth

## Reference UX
A reference implementation could expose:
- `cargo installproof catalog <subject>` — emit visible candidate set
- `cargo installproof plan <subject>` — emit ranked install plan with refusal reasons
- `cargo installproof record --from <tool|receipt|log>` — normalize a real install into `install-receipt/v0`
- `cargo installproof diff --receipt <a> --against <b>` — compare installs without flattening them into update truth
- `cargo installproof pack` — bundle `install-pack/v0`

## Theory of change
The key design move is to separate:
- **install subject**,
- **visible candidates**,
- **policy and refusal reasons**,
- **chosen plan**,
- **actual receipt**,
- and **downstream handoff**.

That separation matters because today’s Rust tooling often collapses these into one fake story:
- a release manifest becomes “what the user installed,”
- a prebuilt download becomes “Cargo install, but faster,”
- a package-manager formula becomes “the same install, just from somewhere else,”
- a self-update receipt becomes “what originally landed on disk,”
- or a shell transcript becomes “the consumer-install record.”

If those truths stay flattened together, Rust will keep getting better point tools without ever gaining one boring install vocabulary that other layers can reuse.

## Shared stack role
This kit is a lower-level anchor inside the archive’s **Distribution Contract corridor**.
It should be treated as:
- the **leaf acquisition/install boundary** beneath the stack-level `distribution-contract-pack/v0`,
- the canonical source for **install-plan** and **install-receipt** truth,
- the handoff source for **Update Continuity Kit**,
- and a reusable import for CLI / client / extension / operator / host-package productization lanes.

## Adjacent kits and boundaries
- **Release Truth Stack** owns what the producer published and attached.
- **Signed Binaries Kit** owns downloadable-artifact issuer and verification evidence.
- **Airgap Kit** owns restricted-network mirror topology and validation posture.
- **Distribution Contract Stack** owns stack-level diffs, imports, and downstream handoffs above the leaf install event.
- **Update Continuity Kit** owns post-install compare/plan/apply/rollback/uninstall continuity, not first install.
- **Support Envelope / Policy / Inventory** remain importing consumers rather than silently becoming the install authority.

## Early pilots
Use [`design/consumer-install-pilot-program.md`](./consumer-install-pilot-program.md) as the ranked rollout. The initial order should stay:
1. **`cargo install` source-build lane**
2. **prebuilt binary lane**
3. **mirror / host-order lane**
4. **CI wrapper lane**
5. **delegated-manager / imported lane**
6. **update/support handoff lane**

The point of the order is to prove direct first-install truth before widening to wrappers, delegated ownership, and downstream lifecycle imports.

## Success criteria
- Tools can answer “what did this install event actually do?” without shell-history archaeology.
- Source builds, prebuilt downloads, package-manager imports, and local-path installs gain one shared vocabulary without pretending they are the same lane.
- Ownership and managed-content claims remain explicit enough for later update/uninstall tooling.
- Higher layers can import install truth without redefining release truth or lifecycle continuity.

## Failure modes to avoid
- A fake universal “safe install” score.
- Treating first install and later update continuity as the same event.
- Treating release manifests or updater receipts as full substitutes for install truth.
- Swallowing every package manager or installer into one fake native lane.
- Pretending a terminal transcript is an install receipt.


## Lane-map rule
Use [`design/consumer-install-lane-map.md`](./consumer-install-lane-map.md) as the archive rule for what must stay separate: source-build installs, prebuilt installs, mirror/host fallback, CI-wrapper installs, delegated/imported installs, and durable receipt/managed-content claims are adjacent lanes, not one install story with cosmetic adapters.
