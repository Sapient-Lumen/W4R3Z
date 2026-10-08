# WebAuthn & Passkeys Interop + Device Lab Kit fixtures

These fixtures exist to make **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit** look buildable instead of merely persuasive.

The receiver-facing questions are:

> what scenario was requested, which lane actually ran it, what could that lane honestly automate, what ceremony evidence was captured, and are two results truly comparable?

## Minimal pack for 0.1

- `scenario-profile.schema.json` — pinned ceremony/profile/overlay contract.
- `runner-capability.receipt.schema.json` — lane identity, supported commands, automation class, stability, and comparability truth.
- `transcript-event.schema.json` — shared event grammar across all lanes.
- `ceremony-transcript.schema.json` — normalized ceremony summary for one run.
- `diagnosis.report.schema.json` — failure family, likely source, and next-action hints.
- `compatibility-matrix.report.schema.json` — lane-by-lane verdicts and comparability classes.
- `manifest.schema.json` — compact `webauthnbundle@1` bundle index.

## Design rules

- Keep **scenario truth**, **lane capability truth**, **evidence truth**, and **comparability truth** separate.
- Treat `webdriver-virtual`, `rust-only`, `manual-device-import`, and `certification-import` as explicit lanes, not implementation details.
- Allow `experimental` and `unreliable` lane statuses; do not force fake certainty.
- Default to hashed identifiers and summarized attestation material.
- Reuse the shared bundle substrate instincts from the evidence-bundle work rather than inventing a forever-one-off zip grammar.

## Intended first scenarios

1. `discoverable_passkey_uv_required_chromium_virtual` — a happy-path virtual-authenticator run with an honest capability receipt and a portable repro bundle.
2. `firefox_virtual_authenticator_capability_warning` — a runner-lane warning scenario where the lane is present but explicitly not trusted for strong cross-browser comparability.
