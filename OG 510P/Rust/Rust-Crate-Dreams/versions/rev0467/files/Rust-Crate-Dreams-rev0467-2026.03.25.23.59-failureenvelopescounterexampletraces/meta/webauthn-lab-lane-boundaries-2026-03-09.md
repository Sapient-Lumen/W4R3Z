# WebAuthn lab lane boundaries — 2026-03-09

## Main judgment

The missing Rust value around passkeys is now **not** another SDK.
It is a boring, reviewable lab layer above real substrate.

That lab layer needs at least five distinct truth surfaces:

1. **scenario truth** — what ceremony/profile/overlay was actually requested,
2. **runner-capability truth** — what the lane could really automate or observe,
3. **ceremony evidence truth** — what normalized events and outcomes were captured,
4. **comparability truth** — whether two results can honestly be compared,
5. **external-program truth** — what came from certification or imported device evidence rather than local automation.

## Working distinctions

### 1. WebAuthn / CTAP specs are not the same thing as browser-lane truth
WebAuthn and CTAP define important protocol behavior.
They do **not** imply that a given browser automation lane can exercise every relevant behavior with release-grade fidelity.

### 2. WebDriver virtual authenticators are not the same thing as physical-device evidence
Virtual-authenticator lanes are extremely valuable.
They are still a lane, not the whole world.
A crate here must preserve **lane identity** instead of flattening virtual and real-device outcomes into one fake “passkey result”.

### 3. Certification and conformance tooling are not the same thing as local regression tooling
FIDO certification and conformance programs are real external substrate.
A Rust crate should import or summarize that evidence when useful, not impersonate those programs or claim their authority.

### 4. Overlay APIs are not silent core behavior
Secure Payment Confirmation and similar surfaces should stay explicit overlays until the crate has a stable reason to treat them as always-on core behavior.

### 5. Capability and stability are separate facts
A lane may expose commands and still be too unstable or unreliable to support cross-lane regression claims.
The archive should preserve both:

- what commands existed,
- and how trustworthy that lane was for comparability.

## Working rule for future passes

When revising passkey or browser-auth proposals, require explicit artifacts for:

- `scenario-profile`,
- `runner-capability.receipt`,
- `ceremony-transcript`,
- `compatibility-matrix.report`,
- and imported `certification-summary` or `device-summary` artifacts when applicable.

Do **not** let future revisions collapse protocol semantics, browser automation, physical-device evidence, and certification status into one fake “interop result”.
