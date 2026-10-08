# Packet adjudication and carry-forward contracts — 2026-03-24

This note exists to keep the archive from silently normalizing disagreement away.

Packet families already answer:
- compare,
- freeze,
- intake,
- materialize,
- trigger,
- recheck,
- revalidate,
- and transition.

What they still need is a disciplined answer for:
- **adjudicate**,
- **inherit**,
- and **supersede**.

## Why this matters now

Current Rust substrate gives us many route-sensitive facts that can look similar while meaning different things:
- `cargo metadata` and registry-index records describe related but different package/dependency surfaces.
- Cargo JSON build messages separate compiler artifacts from build-script output, and build-script output may be cached.
- docs.rs `latest`, semver, pinned version, rustdoc JSON, and download archives are related but not interchangeable.
- crates.io trust/timing surfaces can improve confidence without proving task fit.

A worthy control-plane crate should never hide those distinctions inside a fresh prose answer.

## Contract 1 — adjudication is append-only

An adjudication session must point to:
- imported packet refs,
- the specific conflicting claim IDs or evidence refs,
- the policy or weighting rules used,
- the reviewed outcome,
- and unresolved/manual-review zones.

It must **not** overwrite the old packet in place.

## Contract 2 — carry-forward is not replacement

A carry-forward receipt must say:
- which prior decision is still inherited,
- which claims are superseded,
- which claims are now scope-split,
- and what revisit condition still applies.

It must **not** imply that a later judgment was always true.

## Contract 3 — preserve route identity

When facts conflict, the artifact must preserve:
- route (`cargo_metadata`, `registry_index`, `docsrs_latest`, `docsrs_pinned`, `docs_download_archive`, `build_json`, etc.),
- time basis,
- target/profile scope,
- and policy scope.

A later consumer should be able to see whether the conflict was real or only apparent.

## Contract 4 — unresolved is a first-class outcome

A worthy crate must support:
- `manual_review_required`,
- `split_scope`,
- `temporary_keep`,
- or `open_transition_review`

instead of forcing one synthetic winner.

## Contract 5 — assistants must inherit the same boundaries

Any assistant/search consumer downstream of these packets must:
- cite the adjudication session,
- preserve unresolved/manual-review zones,
- and refuse to treat a carry-forward receipt as if it were a fresh basis lock.

## New first-class artifacts

### `adjudication-session.report.json`
Must say:
- imported packet refs,
- conflict set,
- weighting policy refs,
- reviewed outcome per conflict,
- unresolved list,
- and next action.

### `decision-carryforward.receipt.json`
Must say:
- previous decision ref,
- adjudication session ref,
- resulting decision ref,
- inherited claims,
- superseded claims,
- remaining open issues,
- and next revisit trigger/deadline.

## Minimal adjudication flow

1. import prior packet(s)
2. resolve packet routes into one conflict table
3. classify the disagreement
4. adjudicate each conflict under explicit policy
5. emit one carry-forward receipt
6. open the next ticket only if still needed

## Failure modes to avoid

- silently merging `latest` docs routes into frozen basis
- silently replacing registry/index facts with `cargo metadata` facts
- treating cached build-script output as current execution without recording that caveat
- letting Trusted Publishing / Security / SLOC posture override local fit constraints automatically
- dropping runner-up and excluded candidates from later carry-forward review

## Sources

- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
