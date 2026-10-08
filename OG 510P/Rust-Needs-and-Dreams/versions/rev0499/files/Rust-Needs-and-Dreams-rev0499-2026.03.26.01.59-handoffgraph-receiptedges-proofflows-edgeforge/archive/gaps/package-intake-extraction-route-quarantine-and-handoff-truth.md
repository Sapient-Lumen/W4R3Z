# Gap: package intake still lacks one honest route / extraction / handoff boundary

Rust is getting stronger at several neighboring layers:
- package publication review,
- dependency trust and advisory review,
- consumer install receipts,
- and compile-time execution governance.

What it still lacks is one portable boundary for the moment when a package crosses from **registry-or-source truth** into **local machine state**.

## Why this matters more now
The March 21, 2026 Cargo advisory made the problem concrete: a vulnerability in the `tar` crate used by Cargo to extract packages during a build could let a malicious crate change permissions on arbitrary directories, and alternate-registry users were told to verify impact with their vendor. That is not just a build-script story or a registry story. It is an **intake** story.

At the same time:
- Cargo source replacement says vendoring and mirroring are exact-copy routes with strict assumptions;
- Cargo registries make alternate registries first-class and separate from source replacement;
- `cargo package` already has rich payload and verify semantics;
- `cargo install` still has different lock/config behavior than ordinary project builds;
- crates.io now has stronger trust and freshness inputs (`pubtime`, Trusted Publishing controls);
- routine malware communication is moving toward RustSec advisories instead of one blog post per case;
- and sandboxed build scripts govern compile-time execution authority **after intake**, not the ingress boundary itself.

Sources:
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://doc.rust-lang.org/cargo/commands/cargo-install.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

## What is missing
The missing layer is not another scanner or another registry policy page.
It is the artifact boundary that can answer:
- what route the package came from;
- what exact payload was under intake;
- what extraction and staging semantics applied locally;
- what lock/resolution posture applied;
- and what later belongs to dependency review, build execution, install, or incident response.

Without that layer, several things keep drifting together:
1. **publication** versus **local intake**;
2. **route trust** versus **payload truth**;
3. **payload extraction** versus **compile-time execution**;
4. **dependency intake** versus **consumer installation**;
5. **later incident diagnosis** versus **earlier intake receipts**.

## What a worthy contribution would look like
A real contribution here would define a thin **Package Intake Gateway** with:
- `intake-subject/v0`
- `intake-route-report/v0`
- `intake-payload-report/v0`
- `intake-staging-receipt/v0`
- `intake-decision-brief/v0`
- `intake-handoff/v0`
- `package-intake-pack/v0`

The point is not to replace Cargo.
The point is to make route/extraction/staging truth reviewable and handoff-ready.

## Strongest path forward in this archive
The archive should now treat **Package Intake Gateway** as a distinct seam between:
- **Package Admission Stack** above it,
- **Dependency Review Stack** beside it,
- **Compile-Time Capabilities** after it,
- and **Consumer Install Kit** below it.

That keeps four important boundaries honest:
- publication is not intake,
- intake is not dependency review,
- intake is not compile-time execution,
- and intake is not consumer install.
