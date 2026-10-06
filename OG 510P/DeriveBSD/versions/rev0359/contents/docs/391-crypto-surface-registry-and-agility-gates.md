# Crypto surface registry + agility gates (make crypto drift reviewable)

Cryptography in an OS ecosystem is not “a library choice”.
It is a **long-lived surface** that tends to drift silently:
- new protocols show up (QUIC, WebAuthn, WireGuard, new attestation schemes)
- algorithms/modes creep in ("just use AES-CBC", "just use SHA-1")
- compatibility ossifies (hard-coded suites; no migration plan)
- different components use different defaults (and nobody remembers why)

DeriveBSD already treats other high-risk drift as reviewable artifacts (UAPI/contract/parser/authority/boundaries).
Crypto deserves the same treatment.

## The DeriveBSD stance

1) **Crypto choices are registered** (inventory)
2) **Crypto changes are diffed** (what changed?)
3) **Crypto changes are gated** (is the change acceptable?)
4) **Crypto approval is receipted** (who/what/why)

This makes "we added a new crypto thing" show up like "we added a new parser".

## `crypto.registry`

A `crypto.registry` is a derived artifact that inventories:
- protocols in use (TLS, SSH, WireGuard, NTS, attestation transports)
- primitives/suites (AEAD, signature, hash, KDF)
- blessed libraries and versions (what we actually build and link)
- security profiles ("default", "strict", "legacy")
- linkages to other surfaces (contracts, parsers, trust boundaries)

Schema:
- `spec/crypto.registry.schema.json`

## `crypto.diff`

A `crypto.diff` is the delta between two registries.
It captures:
- added/removed crypto surfaces
- broadened usage (e.g. enabling a legacy suite)
- upgrades (e.g. tightening defaults)
- risky changes (new parser+crypto combo, new JITed verifier, etc)

Schema:
- `spec/crypto.diff.schema.json`

## Why this is worth baking in early

Crypto failures are rarely caused by "no crypto".
They are caused by:
- inconsistent defaults across components
- silent algorithm drift
- deprecation without a migration path
- bespoke crypto invented by apps because the platform didn't provide a clean lane

A greenfield OS can enforce the boring, survivable posture:
- **one crypto portal lane** for high-value key operations (sign/decrypt)
- **a small set of blessed libraries** for in-process crypto
- **policy-defined suites** (not hard-coded in code)
- **deprecations as artifacts** (bounded EOL windows, removal receipts)

See:
- split-key operations as a portal: `docs/306-crypto-operations-portal-and-split-keys.md`
- secrets lane (brokers + receipts): `docs/223-secrets-and-key-management-as-evidence.md`
- deprecations discipline: `docs/385-deprecation-policies-and-removal-receipts.md`

## Gating rules of thumb

Crypto gates should be conservative and mechanical:

- **New protocol**: must name threat model deltas and link to `trust.boundary.diff`.
- **New primitive/suite**: must justify why the existing blessed profile doesn't suffice.
- **Downgrades / enabling legacy**: require explicit `deprecation.notice` or "compat profile" rationale.
- **New parser + crypto** (e.g. new handshake or certificate format): must appear in `parser.diff` and have fuzz/conformance plans.
- **New key material**: must have a `crypto.key.policy` object (non-exportable default).

See: `docs/348-design-review-rubric-and-feature-intake.md`.

## Where this plugs in

- Blast-radius diffs can include a `crypto` section.
- Permission Center can surface crypto grants ("this service may sign with key X").

See:
- blast-radius diffs: `docs/106-blast-radius-diff.md`, `spec/blast_radius.diff.schema.json`
- permission/authority introspection: `docs/371-permission-center-and-authority-introspection.md`

Last updated: 2026-02-27r111
