# Hardware compatibility gates + safe upgrades (avoid bricking remote hosts)

The most painful “atomic upgrade” failures are not package conflicts — they’re hardware regressions:

- new kernel drops a NIC driver and the box never comes back
- storage controller needs a module/firmware floor and boot fails
- GPU stack changes and the console is gone

Traditional OSes handle this with a mix of superstition and out-of-band tooling.
DeriveBSD can treat it as a first-class, typed **gate** that integrates with generations, rollbacks, and receipts.

## Goal

Before switching a host to a new generation, we should be able to answer:

> “Given this host’s hardware, will the target generation boot and provide the minimum required services?”

…and if the answer is “probably not”, we should fail fast **before** flipping the pointer.

## Evidence object: `hw.compat.report`

A compatibility report is emitted during a preflight check and can be used as a gate in change sets.

Schema: `spec/hw.compat.report.schema.json`

Inputs (typical):
- `hw.inventory.receipt` digest (what hardware is present now)
- `fw.inventory.receipt` digest (firmware posture, if emitted)
- target generation digest + closure proof (what we’re about to run)
- planned module set (`kmod.load.plan`) and firmware plans (if any)
- policy decisions (what we’re allowed to do)

Outputs:
- `status`: `ok` | `warn` | `fail`
- structured findings with reason codes (missing driver, policy denied, needs reboot, etc.)
- recommended gating action (`allow`, `deny`, `require-breakglass`, etc.)

## What we check (v0)

### Boot-critical path

- storage controller driver/module present
- rootfs transport supported (ZFS module posture, lazy-rootfs adapters if used)
- required boot artifacts referenced by `boot.manifest` (if secure/measured boot lane is enabled)

### Network reachability floor

For remotely managed fleets, “don’t brick networking” is table stakes:

- at least one primary NIC binding exists and is allowed by policy
- required firmware payloads are in the closure (or a firmware plan is staged)

### Device policy coherence

- device grants + devfs rulesets match the hardware classes discovered
- no new high-risk devices become accessible by default (HID, USB storage, camera/mic)

### Kernel mutation coherence

- planned modules match bindings observed in inventory
- runtime module loads are not required for “basic boot” unless explicitly allowed

## Integration points

### Change sets

A standard host switch can include:

1) generate/refresh `hw.inventory.receipt`
2) run `hw.compat.check` → emit `hw.compat.report`
3) block the switch if `status=fail` (unless policy grants breakglass)

The report digest is included in the `change.receipt` so postmortems can answer: “we knew this was risky”.

### Rollout cohorts

Rollouts can cohort on hardware class summaries from the inventory receipt:

- “Intel i219 NIC class”
- “Broadcom bnxt class”
- “NVMe controller family X”

This makes canaries meaningful without building a bespoke fleet database.

### Boot assessment

If the host boots but fails health checks, boot-try counters can auto-rollback.
The compatibility report then becomes a strong signal for why the rollback happened.

See: `docs/112-health-gated-updates.md`, `docs/69-host-generations-bectl.md`, and curated references on boot assessment.

## Open questions

- What is the minimal “remote management floor” for different deployment classes (headless server vs workstation)?
- How do we represent “driver present but known-bad” (CVE’d firmware, broken module version) as a policy decision?
- How do we keep inventory + compat reports useful without turning them into fingerprinting artifacts?

See risk register item 43.

Last updated: 2026-02-26
