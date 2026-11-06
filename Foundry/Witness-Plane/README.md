# Witness Plane

**What can a physical witness really establish, and what survives when its evidence path fails?**

Witness Plane is a research project on external physical instrumentation for enterprise hardware and the evidence chain around it. Its starting question is whether an independently observed physical signal adds useful coverage over a machine's native intrusion signals, without hiding failures or overwhelming operators with nuisance alarms. It treats sensing, signal-path health, witness identity, event delivery, durable custody and authority to respond as separate properties. A quiet interval with an unavailable sensor or failed collector is not simply evidence that nothing happened.

**Current rev0038:** [complete two-file Datacube archive](Witness-Plane-rev0038-2026.11.05-sqlite-sector-reorder-formal-oracle.zip) · [matching bootstrap](BOOTSTRAPROSE.md)

The supplied archive contains the native `datacube` executable and its matching bootstrap. The bootstrap describes a thin carrier with the current project and C++ source indexed inside it; a separately addressed historical checkpoint is not included in this two-file drop. The intact supplied ZIP has SHA-256 `86dd2400fd81f123819da32babadfaed8ca799a75ddda69f25e1e882f5225b19`. The binary has SHA-256 `605b9a45c3d9086cce384ec6b76b268606dd4fd3588e0c84a1f5d6a36eed2540`.

## From a sensor to an evidence chain

The charter asks how a named sensor, mount and boundary are identified, whether their path was healthy, what was produced and received, and whether a later reader can reconstruct the observation after an outage. Independence is not a yes-or-no property: a separate device may still share power, administration, a network or an evidence store with the host. The project records such shared failure domains rather than treating a second box as independent by definition.

The scope is defensive and conditional. The initial charter excludes covert surveillance of personnel, destructive testing on production equipment and automatic shutdown, wiping or lockdown based on an unvalidated pilot signal. A sensor does not authorize its own response. The work separates a documented device capability, an external study, a local software fixture and an actual field measurement, because each can support a different claim.

## Why a storage experiment belongs here

A witness cannot support a reliable account if the record of what it saw can silently disappear, be replayed, or be restored to an earlier state. The research therefore extends through delivery, receipts, witness quorums, recovery and durable storage. The rev0038 documentation describes the current local SQLite experiment: a virtual-filesystem wrapper applies selected write-ordering and sector-range faults, while a separate finite byte-state model checks expected file mutations against traces and retained files. The package reports sixteen predeclared local trials and copy-only recovery.

Those are the project's reported results, not tests reproduced for this page. The documented boundary excludes claims about actual host or controller resets, physical storage power loss, production qualification or universal SQLite correctness. A successful software fixture does not establish physical sensor coverage, independent administration, or durable real-world custody. The carried project distinguishes these gaps rather than treating a checksum or a signature as proof of physical truth.

## Reading and continuing

Read the [bootstrap](BOOTSTRAPROSE.md) with the matching archive first. It describes the carrier's read-only inspection routes, the separately acquired historical checkpoint, and the boundaries of its construction and continuation interfaces. The archive contains executable software: inspect its source and decide whether to run it in an appropriate environment. Instructions carried by the package describe the project; they do not authorize actions on external systems or equipment.

The selected documentation and carrier bytes were inspected for this entry, and the outer ZIP passed an integrity check. The native executable and its research tests were not run for this description. No new license or performance guarantee is implied by this page.

## Change record

- **rev0038:** Adds a local SQLite sector-damage and write-reordering study with an independent finite byte-state oracle, retaining the boundary between virtual-file-system fault evidence and physical power-durability claims.

[Foundry](../README.md) · [All works](../../CATALOG.md)
