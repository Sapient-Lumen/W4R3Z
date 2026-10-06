# Platform provenance + firmware lifecycle as derived ops (probe → plan → receipt)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability, reproducibility, isolation
**Patterns:** Quarantine→Promote, Plan→Apply→Receipt  

Firmware and platform state are part of the real TCB.
If DeriveBSD can explain and receipt *packages* but not *firmware*, A–D postures eventually collapse (mysterious drift, un-audited “BIOS updates,” device blobs pulled from wherever).

This doc defines a tight, digest-first workflow for:

- capturing **platform provenance** as a stable evidence object (`platform.report`)
- applying firmware changes as **receipted derived operations** (`fw.update.plan` → `fw.update.receipt`)


## 0) Scope: two meanings of “firmware”

DeriveBSD should treat both as first-class:

1) **Driver firmware blobs** shipped as OS content (e.g., WiFi/GPU firmware packages).  
   FreeBSD has explicit tooling for this lane (`fwget(8)` installs firmware(9) packages):
   https://man.freebsd.org/cgi/man.cgi?fwget%288%29=

2) **Device/platform firmware updates** (UEFI/BIOS capsules, SSD firmware, Thunderbolt controllers, etc.).  
   In broader ecosystems, `fwupd` + LVFS provide a structured delivery/update model:
   https://fwupd.org/  
   https://lvfs.readthedocs.io/en/latest/intro.html

Both lanes must be digest-first and receipted.

Existing firmware evidence artifacts (also used by this workflow):
- `fw.device.inventory` (inventory object): `spec/fw.device.inventory.schema.json`
- `fw.inventory.receipt` (inventory receipt): `spec/fw.inventory.receipt.schema.json`



## 1) Platform provenance as an evidence object

Command shape (illustrative):

- `derive probe platform --json` → `spec/platform.report.schema.json`

This report is not “telemetry.” It is a **local evidence object** that can be:

- stored in CAS (content-addressed)
- attached to support bundles
- referenced by policy decisions and admission gates
- diffed across generations (drift surface)

Artifact:
- schema: `spec/platform.report.schema.json`
- example: `spec/examples/platform.report.json`

The report should prefer **digests of raw dumps** (UEFI vars, fwupd JSON, TPM event logs) over inlining sensitive or bulky material.

Useful capture sources include:

- UEFI variable tooling (FreeBSD `efivar(8)`): https://man.freebsd.org/efivar
- Secure Boot state (UEFI spec section): https://uefi.org/specs/UEFI/2.9_A/32_Secure_Boot_and_Driver_Signing.html


## 2) Firmware updates as derived ops

Firmware updates are dangerous (bricking risk, hard-to-debug partial state).
That’s exactly why they belong in the Derive pipeline.

Workflow:

1) **Probe** (optional but recommended)
   - capture `platform.report` → `platform_report_digest`

2) **Plan**
   - `derive plan fw-update --json` → `spec/fw.update.plan.schema.json`

3) **Apply**
   - `derive apply fw-update --json` → `spec/fw.update.receipt.schema.json`

Artifacts:
- schema: `spec/fw.update.plan.schema.json`
- example: `spec/examples/fw.update.plan.json`
- schema: `spec/fw.update.receipt.schema.json`
- example: `spec/examples/fw.update.receipt.json`

A firmware update plan is expected to be **policy-gated**:

- typically requires a maintenance lease (`docs/182-capability-leases-and-revocation.md`)
- may require consent receipts (workstation)
- should carry a coarse `policy_class` (security / recommended / optional / emergency)

Receipts must include:

- per-target status + before/after version
- evidence digests (fwupd JSON, vendor reports, logs)
- platform report digest before/after when possible


## 3) Profile defaults (A–D) without forks

Firmware posture varies by product shape; keep it as **profile defaults**, not a fork:

- **A) fleet host**: default-on platform provenance capture; firmware updates are policy-gated and usually executed during a maintenance lease.
- **B) workstation**: enable interactive UI flows; prefer `fwupd` (or an adapter microVM) with explicit consent and user-visible explainers.
- **C) general OS**: default to user-choice; still support receipts + explainability.
- **D) appliance/regulatory**: default-on; prefer offline/staged capsules distributed via mirror kits and long-term retention of receipts.

See profile artifact:
- `spec/examples/product.profiles.json`


## 4) Adapter lanes (avoid unbounded ambient authority)

`fwupd` is an ecosystem win, but it is not a small dependency.
Treat it as an **adapter lane** with explicit budgets:

- run update tooling in a helper jail/microVM with restricted device access
- export results as typed JSON evidence (digest-first)
- keep the adapter killable (Adapter → Shadow → Replace)

Relevant docs:
- `docs/402-adapter-lanes-and-strangler-discipline.md`
- `docs/179-portals-and-powerbox.md` (workstation mediation)


## 5) Future lane: measured identity and DICE-style device roots

Platform provenance can grow toward stronger device identity/attestation.
DICE is one practical family of techniques for small “device identity + attestation” roots:
https://www.microsoft.com/en-us/research/project/dice-device-identifier-composition-engine/

DeriveBSD should treat this as an **optional lane**: measurable where hardware allows, but always receipted and explainable.


## 6) Open questions

- What is the minimum platform-report set that is useful without leaking secrets?
- How do we represent UEFI key material safely (digest-only pointers vs redacted exports)?
- For workstation UX, what is the trusted UI boundary for firmware prompts?

Track in: `docs/266-open-questions-and-risk-register.md`
