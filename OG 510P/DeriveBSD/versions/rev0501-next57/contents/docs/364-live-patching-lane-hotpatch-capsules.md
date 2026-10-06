# Live patching lane (receipted hotpatch capsules, timeboxed)

Reboots are still the cleanest way to apply kernel fixes.
But some deployments want “reduce exposure window *now*, reboot later”.

DeriveBSD can support that *without* turning hotpatching into a dark art by treating it as a **derived artifact lane**:
- explicit
- timeboxed
- receipted
- removable

## Prior art worth stealing

- kpatch (Linux): dynamic kernel patching.  
  https://github.com/dynup/kpatch
- RHEL kernel live patching: operational framing + limits.  
  https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/managing_monitoring_and_updating_the_kernel/applying-patches-with-kernel-live-patching_managing-monitoring-and-updating-the-kernel
- Ksplice: rebootless patching as a productized lane.  
  https://www.oracle.com/linux/technologies/updating-system-with-ksplice.html

## The artifact: `hotpatch.capsule`

A hotpatch capsule is an object with:

- **target kernel build digest** (exact match required)
- patch payload (module / trampolines / metadata)
- symbol/function map (what is being replaced)
- safety classification:
  - “CVE fix, localized”
  - “behavior change”
  - “risk: scheduler / memory / fs”
- mandatory expiry (timebox)
- test receipts required for promotion

Produced outputs:

- `hotpatch.plan` (activation steps, rollback steps)
- `hotpatch.receipt` (applied/removed, who/when/why, evidence pointers)

## Policy posture (default: off)

- Live patching is **off by default**.
- Enabling it requires explicit policy:
  - which machines/cohorts
  - which patch publishers/keys
  - which risk classes are allowed
  - maximum timebox

Tie into:
- `docs/102-emergency-grafts.md` (fast fixes, but auditable)
- `docs/358-unified-boot-capsules-and-measured-boot-receipts.md`
- `docs/229-evidence-spine-overview.md`

## Operational ergonomics

- Applying a hotpatch must be reversible and produce evidence:
  - “patch applied” event + receipt
  - “patch removed” event + receipt
- Promotion gates require:
  - a minimal test suite (can be cohort-specific)
  - a rollback story (explicit, rehearsed)
- The system should *nag* if a patch is nearing expiry (expiry without removal is a policy violation).

## Open questions

- What minimal ABI do we require to allow hotpatch modules safely?
- Should we allow user-space live patching (glibc/openssl) in the same lane, or keep it separate?
- What evidence do we store for “was the patch actually active” (probe points, hashes, kernel counters)?

## Related docs

- `docs/257-release-capsules-and-transparency.md`
- `docs/258-staged-rollouts-and-cohorts.md`
- `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`
