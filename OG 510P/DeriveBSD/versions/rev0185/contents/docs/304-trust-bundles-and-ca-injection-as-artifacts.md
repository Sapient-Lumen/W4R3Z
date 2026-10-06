# Trust bundles + CA injection as artifacts (stop trust-store drift early)

OS ecosystems routinely fail at "boring PKI":
- *trust roots drift* host-to-host
- apps and libraries disagree on where the trust store lives
- operators patch `/etc/ssl/certs` and hope every tool notices
- incident response can't answer "what trust roots were in effect when this happened?"

DeriveBSD already has the pattern to fix this:
**inventory → explicit plans → receipts → typed events → bounded export**.

This note tightens the PKI lane into a concrete, runtime-usable artifact story:
- trust anchors are **signed objects** in the store
- runtime gets **digest-pinned CA handles** (not ambient paths)
- trust store updates become **reviewable diffs + receipts**

## Prior art worth stealing

- **p11-kit trust module**: a shared, library-agnostic way to expose system trust policy and anchors via a PKCS#11 module.
  - https://p11-glue.github.io/p11-glue/trust-module.html
  - https://p11-glue.github.io/p11-glue/p11-kit/manual/trust-module.html

- **SPIFFE trust bundles**: explicit trust-bundle distribution as an operational primitive.
  - https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE_Trust_Domain_and_Bundle.md

- FreeBSD’s historical CA-path footguns illustrate why "ambient trust store" is brittle.
  - Example bug thread: libfetch default CA file/path confusion.
    https://bugs.freebsd.org/193871

## DeriveBSD primitives (schemas)

Make the PKI lane concrete with typed objects:

- `pki-trust-bundle` (signed): declared trust anchors + intended use.
  - Schema: `spec/pki.trust.bundle.schema.json`

- `pki-issue-plan` (signed): desired identities/certs + issuer backend + rotation policy.
  - Schema: `spec/pki.issue.plan.schema.json`

- `pki-issue-receipt` (signed): evidence of issuance/renewal/install outcomes.
  - Schema: `spec/pki.issue.receipt.schema.json`

See also: `docs/228-pki-and-identity-lifecycle-as-evidence.md`.

## Runtime problem statement: “a trust store is a dependency”

In DeriveBSD, a component should not implicitly depend on:
- `/etc/ssl/cert.pem`
- `/usr/local/share/certs`
- whichever CA path a random TLS library defaults to

Instead, a component’s runtime contract should explicitly declare:
- which trust bundle(s) it relies on
- which identities/certs it expects to have available
- how trust material is delivered (FD, mount, env var, PKCS#11 module config)

This makes trust state:
- reviewable (diffable)
- reproducible (digest-pinned)
- auditable (receipted)

## Proposed compilation: descriptor → trust artifacts

Extend the component descriptor (`derive.unit`) to declare a **pki section**:
- `trust_bundle_digests[]`: which trust anchors are allowed
- `identity_refs[]`: which identities/certs this component needs
- `ca_bundle`: delivery mode (e.g. `fd` or `ro-file`), and the in-sandbox path

During Plan, compile this into deterministic outputs:

1) `trust.bundle.map.json`
- binds each unit to trust bundle digests
- declares extraction/rendering modes required by that unit (PEM bundle, JWK set, PKCS#11)

2) `preopen.map` additions
- provides a **CA bundle FD** (or PKCS#11 module config FD) to the launcher
- rights-masked, read-only

3) `pki.profile.json`
- a resolved list of identity requirements
- references to the `pki-issue-plan` objects that must be satisfied during activation

## Interop: make "one trust store" real

DeriveBSD should support multiple TLS stacks without forcing every app to agree on one format.
A practical approach:

- store canonical trust anchors as `pki-trust-bundle` objects
- provide **renderers** as derived artifacts:
  - OpenSSL-style CAfile/CApath trees
  - NSS database snapshots (optional)
  - a p11-kit trust module view (optional)

Importantly, *renderers are deterministic and digest-bound*:
- the same trust bundle always renders to the same CAfile bytes
- renderers emit receipts so a host can prove what trust store view it served

## Shadow trust: apps shipping their own roots

Even with a clean trust-bundle lane, real ecosystems often reintroduce drift when applications ship:
- embedded `ca-bundle` files
- `cert8.db` / `cert9.db` NSS databases
- bespoke “pin lists” that silently outlive fleet policy

DeriveBSD should make these bypasses **detectable** (closure scans + policy gates) and **containable** (mount masking + trust portal handles).

See: `docs/327-shadow-trust-and-system-ca-governance.md`.

## Evidence and operability

- Trust bundle updates must be:
  - reviewed (blast-radius diffs)
  - receipted (`pki.trust-bundle.updated` event)
  - optionally gated (two-person/quorum approval for high-value bundles)

- Incident bundles should include:
  - active trust bundle digests
  - recent `pki-issue-receipt` digests
  - (optional) the rendered CA bundle digest actually injected into the failing component

See: `docs/216-incident-snapshots-and-support-bundles.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`.

## Default constraints (safe-by-default)

- No ambient trust store reads.
  - if a component wants TLS validation, it must declare a trust bundle dependency.

- Trust bundles are scoped:
  - separate bundles for “public internet”, “corp MITM proxy”, “pkg signing”, “internal mTLS”.

- Tighten exports:
  - trust bundles are public-ish, but their *selection* can reveal org structure.
  - include digests by default, not full material, unless policy allows.

## Open questions

- Do we adopt SPIFFE’s JWK-bundle representation directly as one supported encoding, or keep DeriveBSD’s bundle format and render to JWK?
- Which interop renderers are worth shipping on day-0 (OpenSSL CAfile is mandatory; p11-kit module is optional)?
- How do we express "pin to this intermediate" vs "trust root" cleanly in the trust bundle object?

Last updated: 2026-02-26
