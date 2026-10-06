# PKI + identity lifecycle as evidence (trust bundles / issuance plans / receipts)

Most OSes treat certificates as an application problem:
- CAs and trust roots drift across hosts
- cert renewal is “a cron job” (until it isn’t)
- key material ends up in random paths under `/etc`
- incident response has no clean answer for “what identity did this host present?”

DeriveBSD already has the pattern to make this boring:
**inventory → explicit plans → receipts → typed events → bounded export**.

Bake PKI in early so that:
- identity material is handled like any other evidence lane
- services *reference* identities/certs by stable ids
- rotation/renewal is explicit, receipted, and gateable
- the trust-store itself is a versioned object (not “whatever the base image shipped”)

This lane deliberately overlaps with `docs/223-secrets-and-key-management-as-evidence.md`:
- private keys are secrets (brokered)
- certificates and trust anchors are *public-ish* but still need lifecycle governance

## Lessons worth stealing

### ACME (automated issuance)
ACME’s big lesson is operational:
- issuance is a protocol with explicit challenges and retries
- renewal cadence is predictable
- you can treat cert issuance like a job with receipts

### SPIFFE/SVID (workload identity)
SPIFFE popularized a practical framing:
- workloads have an identity document (SVID)
- identities are short-lived and routinely renewed
- trust bundles are explicit artifacts distributed to verifiers

Even if DeriveBSD doesn’t adopt SPIFFE wholesale, the *artifact boundaries* are excellent.

### OpenSSH certificates (operator-friendly)
OpenSSH certs are an example of “boring PKI” that actually ships:
- an operator CA signs user/host keys
- clients/servers trust the CA, not every individual key
- validity windows + principals are clean levers

## DeriveBSD approach

### 1) `pki-trust-bundle` (explicit trust roots)
A `pki-trust-bundle` is a signed object that declares:
- root/intermediate trust anchors by fingerprint/digest
- intended use (TLS client/server, SSH CA, package signing CA, etc.)
- distribution scope (fleet, cluster, host)

The bundle should be:
- versioned
- referenced from policy and service manifests
- includable in incident bundles (safe by default)

Schema: `spec/pki.trust.bundle.schema.json`

### 2) `pki-issue-plan` (desired issuance/renewal)
A `pki-issue-plan` declares:
- which identity/cert we want (subject, SANs, usages)
- which issuer/provider to use (ACME, internal CA, offline)
- private key handling (reference a `secret-id` + constraints)
- rotation policy (min remaining validity, max lifetime, renewal jitter)

The plan is the “desired state”.

Schema: `spec/pki.issue.plan.schema.json`
The apply engine turns it into concrete requests.

### 3) `pki-issue-receipt` (evidence of issuance/renewal/install)

Schema: `spec/pki.issue.receipt.schema.json`
Every issuance action emits a receipt:
- issued / renewed / failed / revoked
- issuer backend and request id
- cert serial, validity window, SPKI fingerprint
- digests for the cert chain objects placed in the store
- correlation to the triggering `change-set` step

Receipts are what you audit and what rollouts gate on.

### 4) `pki-event` (typed events for correlation)
The structured event journal carries:
- `pki.renewal.scheduled`
- `pki.issued` / `pki.renewed`
- `pki.install.failed`
- `pki.trust-bundle.updated`

Events are metadata-only and correlate to change-sets.

## Interop: one trust store without forcing one TLS stack

Many stacks want different trust-store shapes (OpenSSL CAfile, NSS DB, PKCS#11).
Rather than pick winners, DeriveBSD should treat **renderers** as derived artifacts:
- start from a canonical `pki-trust-bundle` object
- render deterministic CAfile/CApath views for OpenSSL-like consumers
- optionally expose a p11-kit trust module view for library-agnostic consumption

Reference (p11-kit trust module): https://p11-glue.github.io/p11-glue/trust-module.html

## Wiring into the ops spine

- `change-set`: add an `apply-pki` step.
  - validates trust bundle
  - ensures the desired certs/identities exist
  - requests renewals when thresholds are met
  - emits `pki-issue-receipt`
- health gates: can require:
  - “no cert expiring within N days for these identities”
  - “trust bundle matches required digest for this rollout”
- incident bundles: include:
  - `pki-trust-bundle` digest
  - recent `pki-issue-receipt` digests
- secrets: private keys remain brokered via `secret-policy` and `secret-grant`

See: `docs/219-change-sets-and-apply-engine.md`, `docs/215-structured-event-log-as-evidence.md`,
`docs/216-incident-snapshots-and-support-bundles.md`, RFC-0163.

## Ground rules

- No “secret bytes” in PKI evidence objects.
  - private keys are secrets and remain in the credential broker lane
- Prefer short-lived identities with routine renewal.
  - long-lived certs are allowed only with explicit policy
- All issuance/install actions must be receipted.
  - no silent background refresh that bypasses the evidence spine
