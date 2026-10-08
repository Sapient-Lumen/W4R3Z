# Cargo Publish Receipt Join lane boundaries — 2026-03-23

This note keeps **P-0477 Cargo Publish Receipt Join Kit** sharp after the latest crates.io and Cargo registry/security changes.

## Main judgment

**P-0477** should own the post-publish joined receipt for:

- local package bytes and capture basis,
- registry/index acceptance facts,
- publish identity,
- registry capability,
- registry protection scope,
- publication visibility,
- and portable joined bundles.

It should **not** absorb every nearby trusted-publishing, auth, moderation, or provenance lane.

## The seven truths P-0477 should keep separate

### 1. Local bytes
What exact package artifact or digest was observed locally or re-imported later?

### 2. Registry acceptance
What checksum / yanked / index facts were observed for the published version?

### 3. Publish identity
Was the release manual, token-based, or trusted-publisher based, and what explicit workflow/provider facts support that claim?

### 4. Registry capability
What does this registry lane actually expose: index metadata, `pubtime`, TP-only visibility, docs coupling, notifications, advisory channels?

### 5. Protection scope
Which protective claims were actually in scope for this registry lane and client-version window?

### 6. Publication visibility
Is the release merely uploaded, index-visible, Cargo-ready, docs-pending, docs-visible, or still partial?

### 7. Bundle inventory
What exact receipts/reports belong to one joined review pack?

## What P-0477 must stay separate from

### Separate from **P-0175 Trusted Publishing Tooling Kit**
P-0175 is about preflight eligibility, workflow-route identity, registry-state imports, and authorization drift before/during publish.
P-0477 is about the post-publish joined receipt.

### Separate from registry-auth doctor work
Credential-provider failures, token lookup errors, and login problems are a client-auth lane, not a joined post-publish receipt lane.

### Separate from moderation / malware notification systems
P-0477 may import policy or notification posture, but it does not decide whether a crate is malicious or moderate registry content.

### Separate from provenance / attestation systems
A joined publish receipt can reference provenance artifacts, but it does not replace signed attestations.

### Separate from trust scoring / crate-health work
Long-horizon maintainer support, advisories, and ecosystem health remain adjacent but separate review questions.

## Anti-flattening reminders

Do not say:

- “trusted publishing was used, so the registry lane is fully protected.”
- “crates.io blocks this class of upload, so our alternate registry also does.”
- “Cargo can publish to the registry, therefore `pubtime` and other index enrichments exist there.”
- “the index entry exists, so the whole public story converged.”
- “a crates.io RustSec/blog policy tells us what every registry would report.”

Those are exactly the hidden assumptions P-0477 should make visible.

## Sources

- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
