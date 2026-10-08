# Gap: Lifecycle ledger, support windows, and succession are not first-class ecosystem artifacts

## What is missing
Rust has real signals about crate health, but they are scattered across the wrong channels.
Today, maintainers communicate lifecycle state through some combination of:
- README prose,
- changelog notes,
- deprecated badges that crates.io no longer surfaces,
- RustSec `unmaintained` advisories,
- crate deletions,
- issue threads about handoff,
- and heuristics like repo activity or `cargo-unmaintained`.

What is still missing is a **shared lifecycle contract** that makes these questions portable and reviewable:
- which versions are actively supported, security-fix-only, or end-of-life,
- whether a crate is deprecated and what its successor is,
- whether a maintainer is seeking help or consenting to handoff,
- what maintenance work actually happened,
- and which lifecycle signals are *declared* versus merely *inferred*.

That missing layer matters because Rust increasingly has richer registry and security UX, but lifecycle facts still hitchhike on channels that were built for other jobs.

Sources:
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
- https://crates.io/policies
- https://docs.rs/crate/cargo-unmaintained/1.9.0

## The current seam is awkward
Recent signals sharpen the problem:
- the Rust Foundation Maintainer Fund work explicitly says maintenance labor is often invisible and burnout-inducing, and that the project wants ways to publicize maintenance work instead of leaving it hidden;
- crates.io now has a Security tab and richer publish/security UX, which proves the registry is already moving toward more health information at dependency-selection time;
- the crates.io team changed its malicious-crate notification policy so RustSec advisories become the main broadcast channel for most malware removals, which is sensible for security but also underlines that *security channels should not have to carry ordinary lifecycle meaning*;
- Cargo still documents a `[badges].maintenance` vocabulary, but also notes that crates.io no longer uses it;
- RFC 3537 explicitly calls out version maintenance status on crates.io as missing information, especially for users stuck on older but still-supported releases;
- crates.io’s ownership-transfer policy requires explicit owner approval, so “looking for maintainer” or handoff intent cannot safely be approximated from inactivity or forum rumor;
- `cargo-unmaintained` exists because there is real demand for lifecycle signals, but it must fall back to heuristics and explicitly documents their limitations.

The result is a recurring mismatch:
- `unmaintained` in RustSec may mean a package should be avoided, but it is not a general substitute for deprecation or successor metadata;
- a crate may be slow-moving yet intentionally supported, while activity-based heuristics make it look abandoned;
- a version may be old but still within a declared support window, while Cargo/crates.io cannot surface that fact cleanly;
- a maintainer may want help or succession, but there is no standard artifact for publishing that intent;
- and invisible maintenance work (triage, compatibility updates, backports, release hygiene) is hard to point to in a durable way.

Sources:
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
- https://crates.io/policies
- https://docs.rs/crate/cargo-unmaintained/1.9.0

## Why this matters
This is not only a “social” problem.
A good lifecycle substrate would improve:
1. **dependency choice** — users could tell the difference between old-but-supported, deprecated-with-successor, and genuinely abandoned;
2. **policy and trust tooling** — orgs could gate on explicit support windows or deprecation status without scraping READMEs or overusing RustSec;
3. **registry UX** — crates.io could surface richer lifecycle state without inventing an opaque score;
4. **migration planning** — successor pointers and support-window changes could attach to migration and release workflows;
5. **funding and governance** — maintenance work could be made legible enough to support stewarding and maintainer-fund decisions;
6. **incident handling** — emergency deprecations, temporary freezes, and succession notes could travel through an explicit lifecycle channel rather than improvised announcements.

## What “good” looks like
A worthy contribution here is **not** another crate-ranking site or automatic ownership-transfer system.
It is a shared lifecycle boundary with at least:
- `lifecycle-intent/v0` — declared crate and version-line status;
- `support-window-map/v0` — which release lines are active, security-fix-only, frozen, or end-of-life;
- `successor-map/v0` — replacement pointers with verification level and reason;
- `handoff-consent/v0` — explicit maintainer-help or succession consent, without weakening registry ownership rules;
- `maintenance-report/v0` — portable maintenance evidence that makes stewardship work visible;
- `lifecycle-report/v0` — a derived report that keeps declared metadata, RustSec findings, and heuristics separate;
- `lifecycle-pack/v0` — one attachable bundle for crates.io/Cargo/policy/trust/release tooling.

That would let Rust keep advisories, deletions, trust signals, and registry UX in their proper lanes while still giving the ecosystem the lifecycle facts it is clearly missing.
