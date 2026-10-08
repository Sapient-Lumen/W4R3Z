# Publish-surface and release-identity lanes — 2026-03-16

This note exists to stop the archive from collapsing several adjacent crates.io / Cargo release ideas into one vague “publish security crate”.

Recent crates.io signals make the boundary sharper:

- trusted publishing now supports **GitHub Actions and GitLab CI/CD**,
- crates can enable **trusted-publishing-only mode**,
- crates.io blocks certain risky GitHub triggers from trusted publishing,
- crates.io now sends **publish notifications**,
- and crates.io’s February 2026 policy update says malware removals will always get a **RustSec advisory**, while routine malicious-crate blog posts will be reduced.

That means the archive now has multiple real lanes, and they should stay separate.

## The stack to preserve

### 1. Trusted-publishing orchestration and rehearsal
This is **P-0175 Trusted Publishing Tooling Kit** territory:

- provider capability
- trigger eligibility
- trusted-publishing-only planning
- release rehearsal / doctoring
- policy bundles before a release happens

The receiver-facing question is:

> is this release workflow eligible and well-configured for trusted publishing before we try to publish?

### 2. Post-publish release receipts
This is **P-0477 Cargo Publish Receipt Join Kit** territory:

- local `.crate` facts
- registry checksum and `pubtime` confirmation
- publish-mode labeling
- release-history diffs

The receiver-facing question is:

> what was actually released, how was it authorized, and what registry-visible facts confirm it?

### 3. Provenance and attestation publication
This is **P-0015 Cargo Attest** (and related attestation work) territory:

- in-toto / SLSA predicates
- build provenance
- signing / verification policy
- optional publication to external transparency or registry-adjacent systems

The receiver-facing question is:

> what provenance statement or attestation should downstream consumers verify about this artifact?

### 4. Registry auth-stage diagnosis
This is **P-0492 Cargo Registry Auth Doctor Kit** territory:

- provider-chain behavior
- login / index / download / search / publish-stage failures
- auth-required sparse registries
- redacted auth support bundles

The receiver-facing question is:

> why did auth fail for this registry operation, and at what stage?

### 5. Malware and incident communication
This is **not** the job of the publish-surface crates.
It belongs to crates.io team policy, RustSec advisories, and incident response.

The receiver-facing question is:

> how is a malicious or suspicious crate event communicated to the community?

A publish receipt may help an incident, but it is not itself the public notification system.

## Working rule

When touching crates.io / Cargo publish work, future revisions must state explicitly:

1. whether the crate owns **pre-publish rehearsal**, **post-publish receipts**, **artifact provenance**, or **auth-stage diagnosis**,
2. whether the main artifact is a **policy/rehearsal bundle**, a **release receipt**, an **attestation**, or an **auth doctor bundle**,
3. whether crates.io-specific enrichments like **trusted-publishing-only mode**, **`pubtime`**, or **publish notifications** are inputs or core semantics,
4. and whether malware / RustSec / public notification behavior is merely **context** rather than the crate’s own job.

Do not let the archive silently collapse:

- trusted publishing rehearsal,
- publish receipts,
- provenance attestations,
- registry auth diagnosis,
- and malicious-crate communication

into one fake “publish security result”.

The worthy crates here are the **lane-honest artifacts** above increasingly real crates.io substrate.

## Sources

- crates.io development update (2026-01-21): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io development update (2025-02-05): https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- crates.io malicious crate notification policy update: https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- RFC 3691 trusted publishing: https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
