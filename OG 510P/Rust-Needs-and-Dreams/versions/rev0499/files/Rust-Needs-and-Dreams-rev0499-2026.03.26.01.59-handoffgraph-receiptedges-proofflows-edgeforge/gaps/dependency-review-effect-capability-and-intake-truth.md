# Gap: dependency intake still lacks one reviewable effect + capability + artifact boundary

## Summary
Rust now has stronger supply-chain and dependency-review ingredients than it did even a year ago:
- crates.io has a Security tab, richer Trusted Publishing posture, and `pubtime` in the index;
- malicious-crate removals are now expected to land durably in RustSec advisories;
- `cargo vet` already models imported audits, criteria semantics, subtree-sensitive policy, and differential review;
- Cargo Scan has now published evidence that effect-focused review can radically shrink the code humans must inspect;
- `cargo-capslock` and Rust Foundation security work are turning runtime-capability review into a practical lane rather than only a research idea;
- `cargo-auditable` and Cargo-native SBOM work make shipped-artifact dependency truth more attachable.

What Rust still lacks is the **portable dependency-review boundary for dependency intake and upgrade review itself**.

Today, teams can answer fragments such as:
- “this crate has no current RustSec advisory,”
- “Mozilla or another org already audited this version in `cargo vet`,"
- “Cargo Scan flagged only a few effectful paths,”
- “this service only needs these filesystem/network/process capabilities,”
- or “the shipped binary embeds a dependency list.”

What they still struggle to answer cleanly is:
- what exact dependency subject (new crate, version bump, lockfile slice, release candidate, binary, or service) is under review,
- which trust/advisory/publisher facts versus local policy decisions actually apply,
- which potentially dangerous effects were found and whether they were locally safe versus caller-checked,
- which runtime authorities the code appears to need if it runs,
- which shipped artifacts or binaries can be tied back to the reviewed dependency set,
- and what a maintainer, security reviewer, release gate, or assistant may honestly conclude without recomputing everything.

That missing layer is not another vulnerability feed, not another registry score, not another malware scanner, and not a universal policy engine.
It is a **review boundary above trust signals, effect audit, runtime capability, and artifact linkage**.

## Why now
Current ecosystem signals make this much more concrete than it used to be:
- crates.io now exposes a Security tab for RustSec advisories, GitLab Trusted Publishing support, Trusted Publishing-only mode, blocked risky GitHub Actions triggers, and `pubtime` in index entries;
- the crates.io malicious-crate policy now says routine malware removals will always get RustSec advisories, which increases the value of local diffable review artifacts over ambient announcement noise;
- `cargo vet` already optimizes human review attention by suggesting the smallest available diff or full audit, importing trusted external audits, and treating attack-surface reduction as a first-class outcome when shrinking exemptions;
- Cargo Scan’s 2026 paper says developers can decide effect safety locally in most cases (69.2%), can reduce median auditing burden to 0.2% of lines of code compared with whole-crate auditing, can automatically classify 3.5K of the top 10K crates as safe, and finds most effectful code concentrated in roughly 3% of crates;
- Alpha-Omega / Rust Foundation security updates say crate-scanning pilots are underway and a Rust-focused Capslock implementation exists, while `cargo-capslock` and FOSDEM 2026 material make “generate seccomp-style enforcement from capability analysis” a real Rust path rather than a vague aspiration;
- `cargo-auditable` already embeds the dependency tree JSON into compiled executables and explicitly aims at a future where Cargo itself encodes this data in binaries.

Sources:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://mozilla.github.io/cargo-vet/how-it-works.html
- https://mozilla.github.io/cargo-vet/performing-audits.html
- https://arxiv.org/html/2602.06466v1
- https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- https://github.com/ksuzuki/cargo-capslock
- https://fosdem.org/2026/schedule/event/QGCFDA-using_capslock_analysis_to_develop_seccomp_filters_for_rust_and_other_services/
- https://docs.rs/crate/cargo-auditable/latest

## The current seam is awkward
Today, dependency-intake truth gets improvised from incompatible ingredients:
- lockfile diffs,
- crates.io pages and RustSec links,
- `cargo vet` audits or exemptions,
- experimental effect-audit files,
- capability-analysis output,
- binary/SBOM attachments,
- and human summaries in PRs, security reviews, or release notes.

That usually leads to five failures:
1. trust signals and local decisions get flattened into one “safe dependency” verdict;
2. advisories and publisher identity hide the more practical question “what dangerous code or authority is here?”;
3. effect review, capability review, and shipped-artifact review drift apart even when they refer to the same subject;
4. PR/release/support/assistant summaries overclaim what the underlying evidence proved;
5. every org reinvents the same dependency-intake checklist without a portable handoff boundary.

## Why this matters
This gap matters to:
1. **maintainers and reviewers** — because upgrades need more than “no advisory found”;
2. **security teams** — because trust, dangerous-code review, and least-privilege posture should compose instead of competing;
3. **release and packaging engineers** — because reviewed dependency sets should attach cleanly to binaries and release artifacts;
4. **registry/search/review UX** — because thin views need an honest source artifact instead of re-scraped folklore;
5. **assistant/editor consumers** — because LLM-era dependency guidance needs explicit evidence and lossiness, not ambient vibes.

## What good looks like
A worthy contribution here is a thin composition layer above **Trust Decision Stack**, **Runtime Capability Kit**, **SBOM / artifact-linked inventory**, and **effect-audit imports** such as Cargo Scan.

It should provide at least:
- `dependency-review-brief/v0` — why this review subject exists and who it serves;
- `dependency-review-subject/v0` — the exact crate/version/lockfile/binary/release slice under review;
- `dependency-review-pack/v0` — imported trust/effect/capability/artifact evidence with explicit caveats;
- `dependency-review-diff/v0` — what changed between two dependency-review points;
- `dependency-review-handoff/v0` — bounded summaries for PR, security, release, policy, and assistant consumers.

The winning version should keep these distinctions visible:
- **chosen graph / subject truth** versus **trust-signal truth**,
- **effect-audit truth** versus **runtime-capability truth**,
- **binary / artifact linkage truth** versus **registry/package truth**,
- **local decision / waiver truth** versus **thin consumer renderings**,
- and **reviewable uncertainty** versus **final gate language**.

The bar is not a better dashboard.
The bar is a durable, explainable, importable **dependency review boundary** for Rust dependency intake and upgrades.
