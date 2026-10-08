# Native build stack — upstream fit note (2026-03-08)

This note tightens the archive's native-build stack against **real Cargo surfaces** so the proposed crates do not accidentally turn into a Cargo fork.

The stack remains:

1. **P-0046 buildscript-ux-kit**
2. **P-0059 buildscript-testkit**
3. **P-0058 native-deps-kit**

## Main judgment

These crates should be designed to **layer on top of current Cargo substrate** and to remain useful even if upstream Cargo gradually reduces the need for handwritten build scripts.

That means the right shape is not “invent a replacement protocol.”
The right shape is:

- consume existing Cargo JSON/event surfaces where possible,
- normalize only the parts Cargo does not yet make boring,
- reuse existing manifest/config hooks,
- and make migration away from ad-hoc `build.rs` logic easier rather than harder.

## Upstream surfaces that matter

### 1. Cargo already emits build-script results for tools

Cargo's external-tools surface says `--message-format=json` includes **results of build scripts**.
That means P-0046 and P-0059 should not begin from “Cargo tells us nothing machine-readable.”

They should begin from:

- consume Cargo JSON when available,
- capture raw stdout/stderr only as a supplement,
- and keep provenance tied to package IDs / build units rather than inventing a parallel identity scheme.

### 2. Cargo already supports build-script override / handoff flows

Cargo config already supports `target.<triple>.<links>` overrides that skip running a build script entirely and provide the metadata ahead of time.
That means P-0058 cannot treat “live probe ran successfully” as the only honest success path.

Override/handoff success is already part of the real workflow contract.

### 3. Cargo is explicitly exploring ways to reduce handwritten build scripts

There is active upstream thinking about reducing the need for users to write build scripts, and unstable surfaces like `metabuild` and `multiple-build-scripts` already exist.
That means this stack should not hard-code a worldview where one handwritten `build.rs` file is permanent.

Instead:

- P-0046 should report on **build-script executions / units**, not only one file path.
- P-0059 should test **declared build behavior**, not only traditional single-script layouts.
- P-0058 should prefer declarative manifest/config contract shapes that remain useful if probe logic becomes less imperative over time.

### 4. Cargo's package metadata and metadata propagation are real substrate

`system-deps` already proves that `Cargo.toml` metadata can hold declarative native requirements.
Cargo also has unstable work around “any build script metadata”.

That means P-0058 should prefer a design that can live comfortably in `package.metadata` or another low-friction manifest layer, instead of forcing every crate into a wholly separate bespoke manifest unless that extra file clearly earns its keep.

## Design implications for each crate

### P-0046 — buildscript-ux-kit

P-0046 should:

- ingest `--message-format=json` when available,
- preserve package/build-unit identity from Cargo,
- and add value mainly through summarization, redaction, policy evaluation, and support-artifact packaging.

It should **not** redefine the build-script protocol.

### P-0059 — buildscript-testkit

P-0059 should:

- focus on deterministic fixture inputs and normalized outputs,
- model build-script behavior as a test target even if that target is generated or split across future upstream forms,
- and avoid pretending to emulate Cargo's full scheduler or fingerprint engine.

It should **not** become “mini-Cargo in tests.”

### P-0058 — native-deps-kit

P-0058 should:

- prefer declarative support intent,
- treat `links` overrides / handoff as first-class success modes,
- and reuse existing package metadata/config shapes where possible.

It should **not** become a rival package manager or a mandatory replacement for every current `package.metadata.*` convention.

## What this means for example bundles

The first example bundles in this frontier should cover cases that prove alignment with upstream substrate:

1. **transitive warning hidden** — because Cargo warning visibility is already nuanced.
2. **fake pkg-config success** — because testability should not require a live system package manager.
3. **pkg-config then vendored** — because the honest artifact is often the sequence of attempts, not just the final success.
4. **links override handoff** — because skipping the live build script is already a real Cargo path.

## Anti-goals

- Do not fork Cargo's identity or event model.
- Do not require one bespoke manifest format unless existing metadata/config hooks truly fail.
- Do not assume handwritten single-file `build.rs` is the ecosystem's permanent end state.
- Do not design P-0058 as though override/handoff flows were edge cases.

## Sources

- Cargo external tools / JSON messages: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build scripts reference: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo config (`target.<triple>.<links>` overrides): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features (`metabuild`, `multiple-build-scripts`, `any build script metadata`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo issue: reduce the need for users to write build scripts: https://github.com/rust-lang/cargo/issues/14948
- `system-deps` docs: https://docs.rs/system-deps/latest/system_deps/
- `vcpkg` docs: https://docs.rs/vcpkg/latest/vcpkg/
