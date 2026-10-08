# Policy exception and expiry contracts — 2026-03-24

This note exists to keep the archive from silently normalizing temporary relief into permanent truth.

Packet families already answer:
- compare,
- freeze,
- intake,
- materialize,
- trigger,
- recheck,
- revalidate,
- adjudicate,
- and carry forward.

What they still need is a disciplined answer for:
- **exception**,
- **expiry**,
- and **removal path**.

## Why this matters now

Current Rust tooling already has multiple exception-like surfaces:
- Cargo Vet uses `exemptions`, `trust`, `renew`, and expiry-bearing wildcard entries.
- cargo-deny supports ignored advisories with reasons and per-crate license exceptions.
- cargo-semver-checks is headed toward override-bearing release checks and can already describe witness generation for specific breakage.
- docs.rs build limits and metadata knobs often explain why a public support surface is partial rather than absent.
- crates.io trust/timing surfaces improve visibility without proving task fit.

A worthy control-plane crate should never hide those distinctions in one vague “approved for now” note.

## Contract 1 — exception is append-only

A policy exception must point to:
- the prior decision or adjudication artifact,
- the exact subject and scope,
- the owner and approving authority,
- the evidence basis,
- the reason for temporary relief,
- and the expiry/removal conditions.

It must **not** overwrite the original decision in place.

## Contract 2 — exception is not support truth

A policy exception must say:
- what remains unsupported,
- what is only locally accepted,
- what scope is excluded,
- and what manual or future work is still required.

It must **not** imply that a temporary allowance equals a general recommendation.

## Contract 3 — expiry is first-class

Every exception must include at least one of:
- `expires_at`,
- `renews_on_review`,
- `removed_when`,
- or `transition_when`.

Exceptions without any exit path are debt, not product.

## Contract 4 — preserve evidence route identity

When an exception is justified, the artifact must preserve:
- route (`cargo_vet_exemption`, `cargo_vet_trust`, `cargo_deny_ignore`, `docsrs_build_limit`, `semver_witness`, `cratesio_pubtime`, etc.),
- time basis,
- target/profile scope,
- and policy scope.

A later consumer should be able to see whether the exception was narrow, stale, or still justified.

## Contract 5 — assistants must inherit the same ceilings

Any assistant/search consumer downstream of these packets must:
- cite the exception receipt,
- preserve its scope and expiry,
- and refuse to retell a temporary exception as ecosystem-wide support.

## New first-class artifacts

### `policy-exception.receipt.json`
Must say:
- source decision refs,
- subject and scope,
- owner and authority,
- evidence refs,
- rationale,
- support ceilings,
- expiry/removal path,
- and next action.

### `exception-expiry.ticket.json`
Must say:
- exception ref,
- why review reopens,
- what evidence should be re-imported,
- possible outcomes (`renew`, `remove`, `revalidate`, `transition`),
- and deadline/owner.

## Minimal exception flow

1. import prior packet(s)
2. locate the unresolved gap
3. record the narrowest acceptable exception
4. attach evidence and removal path
5. emit one exception receipt
6. schedule one expiry ticket

## Failure modes to avoid

- silent blanket “approved for now” notes with no owner
- importing Cargo Vet or cargo-deny exceptions as if they were general task-fit truth
- treating docs.rs partial builds as proof of local incompatibility or local compatibility without route notes
- keeping semver override decisions without witness linkage
- letting exceptions accumulate with no budget, no expiry, and no removal path

## Sources

- https://mozilla.github.io/cargo-vet/commands.html
- https://mozilla.github.io/cargo-vet/performing-audits.html
- https://embarkstudios.github.io/cargo-deny/cli/init.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/cargo-semver-checks/latest/cargo_semver_checks/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
