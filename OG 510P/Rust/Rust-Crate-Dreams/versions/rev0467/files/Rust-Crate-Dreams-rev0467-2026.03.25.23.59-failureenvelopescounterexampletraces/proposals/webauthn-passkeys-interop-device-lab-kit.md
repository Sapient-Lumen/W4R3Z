---
id: P-0200
title: WebAuthn & Passkeys Interop + Device Lab Kit — profile-pinned scenarios, runner capability receipts, comparability matrices, and portable repro bundles for Rust auth teams
status: idea
domains: [security, auth, web, conformance, tooling]
last_reviewed: 2026-03-09
evidence:
  - https://www.w3.org/TR/webauthn-3/
  - https://web-platform-tests.org/writing-tests/testdriver.html
  - https://www.selenium.dev/documentation/webdriver/interactions/virtual_authenticator/
  - https://github.com/mozilla/geckodriver/releases
  - https://fidoalliance.org/certification/functional-certification/
  - https://fidoalliance.org/certification/functional-certification/conformance/
  - https://docs.rs/webauthn-rs/latest/webauthn_rs/
  - https://github.com/1Password/passkey-rs
needs:
  - Rust has real WebAuthn/passkey substrate, but teams still lack a portable way to describe scenarios, record lane capabilities, normalize ceremony evidence, and hand one redacted repro bundle to another maintainer.
  - The missing crate is not another RP/server SDK; it is the interop and evidence layer above server crates, authenticator/client crates, browser automation, and device/import lanes.
  - Browser and device lanes are no longer hypothetical, but they are not equally reliable; the crate must preserve capability truth and comparability truth instead of pretending every automated run means the same thing.
risks:
  - Privacy mistakes are easy and costly; the kit must default to hashing or stripping user-identifying values and never export secret key material.
  - Browser and device automation surfaces are heterogeneous; the crate must make lane differences explicit instead of promising fake cross-browser parity.
  - It must not quietly turn into a generic browser automation framework or a fake certification product.
---

# P-0200 — WebAuthn & Passkeys Interop + Device Lab Kit

**Codename:** `passkeylab`

**Bundle:** `*.webauthnbundle.zip`

**Primary surface:** a layered crate workspace plus `cargo webauthnlab`.

## Problem

WebAuthn is now current enough, and deployed enough, that passkey failures are increasingly **coordination failures** rather than “nobody has a library yet” failures.

The substrate is real:

- WebAuthn Level 3 is now a W3C Candidate Recommendation Snapshot.
- WPT `testdriver` exposes virtual-authenticator commands and Secure Payment Confirmation automation hooks.
- Selenium documents a practical WebDriver virtual-authenticator surface.
- `webauthn-rs` gives Rust teams a secure relying-party/server lane.
- `passkey-rs` gives Rust teams deeper client/authenticator/CTAP2 substrate.
- FIDO certification and conformance tooling already exist outside Rust.

But the missing Rust crate is still obvious when a ceremony fails:

- teams cannot cleanly say which scenario was intended,
- which runner lane actually executed it,
- what that lane could honestly automate,
- what was redacted,
- whether two results are comparable,
- and what bundle another maintainer should inspect.

That is why passkey bugs still collapse into screenshots, ad hoc logs, and vague claims like “works in Chrome but not Firefox.”

## Main judgment

A worthy crate contribution here would **not** mainly be another WebAuthn SDK.

It would be a crate that gives other people a boring, sharable way to answer five receiver-facing questions:

1. **What scenario did you ask for?**
2. **Which lane actually ran it?**
3. **What could that lane honestly automate or observe?**
4. **What normalized ceremony evidence was captured?**
5. **Are these two results actually comparable?**

That is the missing coordination artifact.

## What the crate should provide other people

### 1. A scenario profile contract
The kit should define a portable `scenario-profile` artifact for:

- registration vs assertion,
- discoverable vs non-discoverable credentials,
- UV/UP requirements,
- authenticator attachment preferences,
- attestation conveyance,
- extension requests,
- allow-credentials filters,
- overlay packs such as SPC,
- and expected failure classes.

The same logical scenario should be reusable across Rust-only, WebDriver, and imported/manual lanes.

### 2. Runner capability receipts
Every run should emit a `runner-capability.receipt` that says:

- which lane family ran (`rust-only`, `webdriver-virtual`, `real-browser`, `manual-device-import`, `certification-import`),
- which commands or surfaces were actually available,
- whether the lane is stable, experimental, or unreliable,
- which parts were automated versus imported,
- and what comparability class the result deserves.

This is the core honesty contract.
Without it, the archive would keep confusing “has an API” with “can support release-grade regression claims.”

### 3. A normalized ceremony transcript
The kit should normalize facts like:

- ceremony type,
- RP ID and origin facts,
- challenge digests,
- client-data and authenticator-data summaries,
- user presence / user verification outcomes,
- sign-count and discoverability facts,
- attestation summary class,
- extension outcomes,
- transport hints,
- timeline events,
- and error families.

But it must not casually export stable user identifiers, raw secrets, or unnecessary attestation material.

### 4. Comparability matrices and diagnosis reports
The crate should produce compact receiver-facing reports that answer:

- which scenarios passed in Chromium virtual-authenticator lanes,
- which lanes are only comparable within the same runner family,
- which failures likely came from RP policy, runner limitation, or device behavior,
- and which cases need real-device or certification-lane follow-up.

This is how the crate becomes useful to other people doing triage and release review.

### 5. Redacted repro bundles
`*.webauthnbundle.zip` should contain:

- the pinned scenario profile,
- the runner capability receipt,
- the normalized transcript,
- the diagnosis report,
- the compatibility matrix or lane comparison report,
- the active redaction policy,
- and optional imported server or certification summaries.

A good bundle should make it fast to distinguish:

- RP policy mismatch,
- origin / RP ID mismatch,
- UV / UP mismatch,
- discoverability mismatch,
- attestation-policy mismatch,
- runner-limitation mismatch,
- or a browser/device-specific quirk.

### 6. Shrinking and overlay-aware minimization
Many passkey failures hide inside a larger ceremony profile.
The crate should try to minimize failures by reducing:

- optional extensions,
- attestation settings,
- discoverability hints,
- and overlay packs,

while preserving the same failure family and preserving comparability honesty.

## Lane boundaries that matter

The crate should make at least these lanes explicit.

### Rust-only substrate lane
Built from Rust libraries such as `webauthn-rs`, `passkey-rs`, or adjacent authenticator/client crates.
Useful for scenario authoring and some repeatable substrate checks.
Not a substitute for browser/device evidence.

### Chromium-class WebDriver virtual-authenticator lane
A strong first MVP lane because WebDriver/WPT virtual-authenticator surfaces are real and widely used.
Good for repeatable automated scenarios, matrix runs, and shrinking.
Still not the whole truth about real-device UX.

### Firefox / geckodriver virtual-authenticator lane
The crate should treat this as **capability-gated and currently cautionary**, not as silently equivalent to Chromium.
If the runner emits an unreliable-lane receipt, the result may still be useful, but only with a stricter comparability class.

### Manual / real-device import lane
Needed for platform authenticator UX, attachment reality, cross-device behavior, or physical-token quirks that automation cannot honestly reproduce.
The key requirement is that imported/manual evidence still lands in the same normalized bundle grammar.

### Certification / conformance import lane
FIDO conformance and certification tooling already exist.
The Rust crate should import or summarize those results where useful, not impersonate them.

## Persona / who it’s for

- auth and identity teams
- Rust library authors building on `webauthn-rs` or `passkey-rs`
- QA / interop engineers
- browser / device compatibility maintainers
- security reviewers who need evidence without raw secrets

## Users & user stories

- **Auth team:** “This registration scenario passes in a Chromium virtual lane but fails on a real-device imported lane; show me whether that is a comparability break, a policy mismatch, or an authenticator quirk.”
- **Library author:** “We changed our RP stack and need one redacted bundle that separates our bug from a browser-runner limitation.”
- **QA engineer:** “Run the same scenario profile through Rust-only and WebDriver lanes, then export one compatibility report.”
- **Security reviewer:** “Show exactly what was captured, what was hashed, and which evidence lane was trusted.”

## Prior art scan (and why it’s insufficient)

### `webauthn-rs`
Valuable Rust relying-party/server substrate.
But it is not a cross-runner lab, a comparability contract, or a portable repro-bundle format.

### `passkey-rs`
Valuable Rust client/authenticator/CTAP2 substrate.
It makes a Rust-only lane more credible, but it still does not solve browser/device/certification evidence packaging.

### WPT `testdriver` and Selenium virtual authenticators
These are crucial automation substrate.
But they are not a Rust scenario DSL, a redaction policy, a comparability receipt, or a sharable repro-bundle standard.

### FIDO certification / conformance tooling
This is real external test and interoperability substrate.
But it is not the same thing as a day-to-day Rust workflow for scenario authoring, regression triage, and bundle exchange between maintainers.

## Design goals

1. **Scenario-first, not log-first**
2. **Capability honesty before automation bravado**
3. **Redaction by default**
4. **Comparability truth before cross-lane claims**
5. **Interop usefulness over certification cosplay**
6. **Incremental adoption above existing Rust auth substrate**

## Proposed architecture

```text
passkeylab-scenario/      # scenario-profile grammar and overlays
passkeylab-ir/            # normalized ceremony transcript and event IR
passkeylab-runner/        # lane traits, capability receipts, comparability rules
passkeylab-rust/          # Rust-only relying-party/authenticator lane
passkeylab-webdriver/     # WebDriver virtual-authenticator lane(s)
passkeylab-import/        # manual-device and certification import adapters
passkeylab-bundle/        # webauthnbundle writer/reader and redaction
passkeylab-report/        # diagnosis, diff, and compatibility reports
passkeylab-cli/           # cargo webauthnlab commands
```

### Core public artifact types

- `ScenarioProfile`
- `RunnerCapabilityReceipt`
- `CeremonyTranscript`
- `DiagnosisReport`
- `CompatibilityMatrixReport`
- `RedactionReport`
- `WebauthnBundleManifest`

## Bundle draft

`*.webauthnbundle.zip`

```text
manifest.json
scenario/scenario-profile.json
receipts/runner-capability.receipt.json
outputs/ceremony-transcript.json
outputs/events.jsonl
reports/diagnosis.report.json
reports/compatibility-matrix.report.json
policies/redaction-profile.json
reports/redaction.report.json
imports/server-summary.json                 # optional
imports/certification-summary.json          # optional
artifacts/screenshots/*.png                 # optional
notes/README.md
```

## Compatibility story

Interoperates with:

- Rust relying-party/server crates such as `webauthn-rs`,
- Rust client/authenticator substrate such as `passkey-rs`,
- WebDriver/WPT virtual-authenticator runners,
- manual device evidence imports,
- and FIDO conformance/certification result summaries.

Does **not** promise:

- replacement of browser automation frameworks,
- replacement of FIDO certification,
- or total equivalence between virtual, software, and physical authenticators.

Instead, it promises that those differences become explicit and reviewable.

## MVP surface

### 0.1
- scenario-profile grammar for registration / assertion basics
- one Rust-only lane
- one Chromium-class WebDriver virtual-authenticator lane
- runner-capability receipts
- normalized ceremony transcript
- redacted `webauthnbundle.zip`
- `cargo webauthnlab run`, `diff`, and `bundle`

### 0.2
- diagnosis reports and compatibility matrices
- shrinking / minimization
- richer attestation-policy summaries
- imported server summaries
- explicit Firefox/geckodriver experimental lane receipts

### 0.3
- manual real-device import lane
- certification-summary imports
- SPC overlay pack
- richer browser / device capability registries

## Conformance & fixtures

The repo should ship fixture schemas for:

- scenario profiles,
- runner capability receipts,
- transcript events,
- normalized ceremony transcripts,
- diagnosis reports,
- compatibility matrices,
- and bundle manifests.

The same logical scenario must remain representable across all lanes even when automation scope and comparability differ.

## Path to boring stability

- Freeze the scenario and receipt schemas before chasing broad device coverage.
- Treat redaction as part of the public contract, not an implementation detail.
- Preserve lane instability or unreliability as machine-readable facts.
- Keep protocol mismatches distinct from runner limitations.
- Keep certification import distinct from local automation evidence.

## Minimum lovable MVP

A crate workspace that can run one discoverable-passkey scenario through a Rust-only lane and a Chromium-class virtual-authenticator lane, then export one redacted `webauthnbundle.zip` that explains whether the difference came from RP policy, runner support, or lane incomparability.

## De-risk plan

1. Start with registration / assertion basics, not every extension.
2. Ship Chromium virtual-authenticator support before claiming broad browser parity.
3. Treat geckodriver results as capability-receipted and potentially non-comparable until the automation surface is trustworthy.
4. Freeze a conservative redaction profile early.
5. Pilot with one Rust RP library and one Rust authenticator/client substrate.

## Explicit non-goals

- Not a replacement for WebAuthn or FIDO certification.
- Not a general-purpose browser automation framework.
- Not a hosted auth platform.
- Not a promise that real-device UX can be fully virtualized.

## Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 25/30**

## Open questions

- How much attestation detail should be normalized versus hashed or summarized by default?
- Which manual/device import facts are essential before a result can be compared to a virtual lane?
- When should SPC stay an overlay pack versus graduate into first-class scenario surface?

## Sources

- https://www.w3.org/TR/webauthn-3/
- https://web-platform-tests.org/writing-tests/testdriver.html
- https://www.selenium.dev/documentation/webdriver/interactions/virtual_authenticator/
- https://github.com/mozilla/geckodriver/releases
- https://fidoalliance.org/certification/functional-certification/
- https://fidoalliance.org/certification/functional-certification/conformance/
- https://docs.rs/webauthn-rs/latest/webauthn_rs/
- https://github.com/1Password/passkey-rs
