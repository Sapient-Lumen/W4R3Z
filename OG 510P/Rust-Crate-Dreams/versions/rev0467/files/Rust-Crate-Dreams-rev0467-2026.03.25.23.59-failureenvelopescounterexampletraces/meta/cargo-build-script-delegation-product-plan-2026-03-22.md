# Cargo Build Script Delegation Kit — product plan (2026-03-22)

## Product thesis

`cargo build-delegate` should give maintainers and downstream users one **portable support bundle** for delegated or split build-script behavior.
The bundle’s job is not to replace Cargo.
Its job is to make build-time behavior explainable, comparable, and reviewable.

## Who it is for

- `-sys` crate maintainers,
- generator-heavy library maintainers,
- distro/packaging engineers using override or no-network flows,
- workspace owners centralizing repeated build logic,
- CI/tooling authors who need stable machine-readable artifacts.

## Core user promises

1. **I can see which build units exist and in what order they matter.**
2. **I can see which output lane belongs to which unit.**
3. **I can tell whether a live run, an override, or a delegate package was authoritative.**
4. **I can see where the workflow still depends on unstable bridge substrate.**
5. **I can compare two bundles and know what meaningfully changed.**

## 0.1 deliverables

### Library

- manifest / config / Cargo-observation ingestion,
- typed receipts for topology, output lanes, and override authority,
- doctor reports for bridge posture,
- bundle assembly and diffing.

### Cargo subcommand

- `snapshot`
- `doctor`
- `diff`
- `pack`

### Bundle contents

- declared contract,
- normalized plan,
- observations,
- topology receipt,
- output-lane receipt,
- override-authority receipt,
- bridge report,
- fallback plan,
- drift diff,
- human summary.

## First implementation order

1. **Topology capture** from declared inputs and Cargo observations.
2. **Output-lane capture** for metadata/env/generated files.
3. **Override-authority capture** for `links` config and non-live paths.
4. **Bridge diagnostics** for unstable artifact staging / multi-script dependencies.
5. **Diff + pack** once the vocabulary stops moving.

## Success criteria

A user should be able to answer all of these from one bundle without re-running the build:

- which unit produced the metadata my dependent needs?
- did a config override skip the live build script?
- did unit order change across releases?
- are staged artifacts supportable on stable or only on nightly?
- what do I have to review before saying this delegated setup is safe to ship?

## Anti-goals

- rewriting Cargo’s scheduler,
- emulating full fingerprint / freshness logic,
- promising sandbox/security guarantees Cargo does not provide,
- or auto-migrating every `build.rs` into a delegate package.

## Why this is likely shippable

The crate can deliver value on stable immediately because plan/receipt/diff artifacts do not require upstream Cargo to finish every part of the delegation roadmap.
That keeps the MVP concrete and lets the crate serve as a proving ground instead of a speculative fork.
