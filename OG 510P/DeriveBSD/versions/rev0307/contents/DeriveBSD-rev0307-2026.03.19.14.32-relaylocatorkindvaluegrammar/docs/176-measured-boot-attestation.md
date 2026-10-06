# Measured boot + remote attestation lane (optional)

DeriveBSD’s baseline security model does **not** require TPMs or remote attestation.
But for high-assurance deployments, measured boot can turn “I intended to boot X” into
“here is evidence I *did* boot X”.

This lane is explicitly **policy-gated** and can be adopted incrementally.

For verifier receipts and posture reuse across the OS, see:
- `docs/226-platform-posture-and-attestation-results-as-evidence.md`

For practical implementation lessons (PCR registries, measurement boundaries, Keylime-style verifiers), see:
- `docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md`

## Why this is worth baking in early

If we wait too long, we risk:
- retrofitting evidence formats after tooling already ossifies
- duplicating ad-hoc attestation formats across subsystems
- mixing “identity” and “measurement” in ways that are hard to audit

So: define **evidence objects** and **interfaces** now, even if enforcement is v2.

## Conceptual model (RATS-shaped)

Use the IETF RATS vocabulary:
- **Attester**: the DeriveBSD host (or a trusted boot component)
- **Evidence**: PCRs + event-log digest + quote signature
- **Verifier**: a policy authority / admission controller
- **Relying Party**: the update/activation logic that decides “allow promotion/activation?”

(See RFC-0111.)

## Evidence objects (minimum set)

### 1) `boot.manifest`
A digest-bound list of boot-critical components and inputs for the activated generation:
- EFI loader / boot blocks (as applicable)
- kernel + modules bundle digests
- init/activation binary digest
- kernel cmdline profile digest (if applicable)

This already exists implicitly in Secure Boot discussions; the point is to make it a *first-class*, content-addressed object.

Schema: `spec/boot.manifest.schema.json`.

For the “make this debuggable” story (event-log replay against the manifest), see:
- `docs/313-boot-manifests-and-eventlog-replay.md`


### 1b) `boot.eventlog.canon`
A typed, canonicalized boot event log object:
- order-preserving transcript of measured events
- safe-by-default (digests are primary; human hints are untrusted)
- supports deterministic replay and crisp “why did PCRs change?” diffs

Schema: `spec/boot.eventlog.canon.schema.json` (example: `spec/examples/boot.eventlog.canon.json`).

Wiring: `docs/443-boot-eventlog-canon-as-evidence-artifact.md`

### 2) `boot.attestation`
A signed object that binds:
- **host identity** (key id)
- **deployment reference** (generation/deployment ref digest)
- **PCR bank + PCR values**
- **TPM quote** over selected PCRs
- **measured boot event log digest** (or canonicalized event log digest)

Schema: `spec/boot.attestation.schema.json`.

Note: attestation is only as good as the attester identity lifecycle. Capture provisioning/enrollment as a typed receipt:
- `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`
- `spec/attester.provision.receipt.schema.json`

### 3) `attestation.receipt` (optional)
A verifier-issued receipt that says: “I checked this boot.attestation under reference R/policy P, and it passed.”
This mirrors the “policy decision record” idea, but for platform state.

Schema: `spec/attestation.receipt.schema.json`.

## Policy patterns

- **Promotion gate**: require a verifier receipt for hosts in a high-assurance group before promoting them to `stable`.
- **Activation gate**: allow activation only if the *local* host can produce a boot attestation that matches the expected boot.manifest.
- **Two-lane**: require receipts only for specific namespaces/channels (e.g., `prod/*`).


### Phase markers (make attestation debuggable)

Measured boot becomes much more usable if we also measure **boot phase markers** into a dedicated PCR, so we can tell *which milestone was reached* and gate sensitive capabilities accordingly.

See: `docs/245-boot-measurement-phases-and-pcr-separation.md`, RFC-0177.

### PCR matching philosophy

Avoid “golden PCR values everywhere.” Real fleets have variance.
Prefer policies that verify:
- event log entries correspond to expected boot.manifest components
- PCR values are consistent with the parsed event log
- the quote is signed by a provisioned attestation key

Also: pin PCR meaning to an explicit “registry” rather than folklore.
This can be as simple as documenting the intended PCR semantics in the reference object and verifier policy.

## FreeBSD-first integration sketch

- Start with **evidence production** using standard TPM2 tooling where feasible.
- Keep enforcement optional until the FreeBSD boot chain measurement story is stable for our target platforms.
- Treat measured boot as complementary to Secure Boot:
  - Secure Boot: blocks untrusted *code*
  - Measured boot: produces evidence about *what ran*

## Non-goals (v1)

- mandatory TPM presence
- “fleet-wide remote attestation required” default
- runtime integrity monitoring (IMA-like) as a prerequisite

Last updated: 2026-02-28r163
