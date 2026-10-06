# DeriveBSD rev0578 mission audit: sprawl triage + target-floor correction note

Generated: 2026-06-17T18:00:18.149891-04:00 (2026-06-17T22:00:18.149891+00:00 UTC)

Source archive: `DeriveBSD-rev0577-2026.06.17.07.16-missionaudit-sprawltriage-releasegreen-wren(2).zip`
Source SHA-256: `3dfeea84b9cd13872f1d78e58d2bcd76411b35c2452462a8fa442312f6fd031d`

## Heart of the mission

DeriveBSD's heart is not simply “make a BSD distribution.” The mission I read in the cube is: **make BSD host generations and workload environments derivable, explainable, rollbackable, and evidence-bound by default.** The system wants every important transition to pass through typed manifests, locks, plans, artifacts, closure proofs, atomic ZFS boot-environment activation, and receipts. It treats builders and runtime workloads as hostile until constrained by capability boundaries, microVMs, jails, brokers, leases, and auditable policy.

A sharper one-line mission:

> DeriveBSD turns FreeBSD systems into signed, reproducible, reversible host/workload generations whose provenance, authority, isolation, and operator actions can be explained from receipts rather than folklore.

The strongest local design spine appears repeatedly:

- `Spec → Lock → Plan → Artifact → Closure → Install/Activate`.
- `Plan → Apply → Receipt` for privileged changes.
- `Broker → Lease → Receipt` for authority.
- `Registry → Diff → Gate` for surfaces that can drift.
- Product profiles are compilation targets, not forks.
- Evidence is not postmortem logging; evidence is a product surface.

This is valuable because it combines several ideas that are usually separate: Nix-like derivation discipline, Qubes-like compartmentalization, Talos-like immutable/API-managed host posture, and SLSA/in-toto-like provenance. The cube’s unique center is the BSD/ZFS/microVM/control-plane version of that combination.

## What is missing

### 1. A real host proof is still the main missing proof

`docs/current/start-here-now.md` says the riskiest unfinished item is a **non-simulated FreeBSD host proof** for removable-media local fallback. The strict collection, import, finalization, and validation machinery exists, but `validation/freebsd-host-proof-imports/` is empty in this archive. The system has a large proof harness before it has the decisive real proof.

Corrective direction: prioritize one imported proof bundle from a real FreeBSD host over any further expansion of removable-media theory. One green real-host transcript is worth dozens of boundary documents here.

### 2. The v0 product story is too implicit

The cube contains product profiles and cutline language, but the reader still has to assemble the smallest compelling demonstration. The v0 story should be a small path that can be executed and narrated:

1. read a tiny product profile,
2. produce a locked derivation,
3. build or select a host generation,
4. activate through a reversible ZFS boot environment,
5. launch one isolated workload,
6. run `derive explain` to show exactly why the deployed bits and authority are trusted.

Anything not serving that story should be Tier C/D until the story works repeatedly.

### 3. Receipts need a human UX layer

The evidence model is powerful, but most of the archive still feels like internal contracts. The missing user-facing layer is: what does an operator see when something is unverified, expired, stale, revoked, drifted, or restored? The mission will be easier to sell if `derive explain` has a small number of memorable views: “what changed,” “who authorized it,” “what is isolated from what,” “what can be rolled back,” and “what is unverified.”

### 4. Evidence retention and privacy budgets need to become first-class

The evidence spine can become a liability if receipts preserve secrets, paths, hostnames, user identity hints, or payload metadata forever. The risk register already sees this pattern. The missing operational policy is a default retention/privacy budget per evidence class: what is immutable, what is redacted, what is exported, what expires, and what is deliberately not collected.

### 5. Legacy target-floor freshness needs correction

`tools/freebsd/host_proof_contract.py` still names `14.3-RELEASE` as the supported legacy floor while primary proof targets are `15.1-RELEASE`. This was reasonable historically, but the online release schedule makes it a near-term stale edge: 14.3 reaches EOL on 2026-06-30 and 14.4 is the supported 14.x point release through 2026-12-31.

Corrective direction: move the supported legacy floor to `14.4-RELEASE`, update the osreldate threshold from a 14.3-era value to a 14.4-era value, and revise operator packet text plus examples together. Keep 14.3 only as an importable historical fixture, not a living supported floor.

## What should change

### Near-term changes

1. **Promote “real-host proof imported” above all other proof work.** Freeze new removable-media branches until one strict real FreeBSD proof is checked in.
2. **Update the FreeBSD legacy floor from 14.3 to 14.4.** This should be a focused contract/docs/examples patch, not a broad redesign.
3. **Create a single v0 story spine.** Name the canonical flow and make other features explicitly optional/profile-specific.
4. **Turn repeated boundary prose into tables.** The repeated “exactness/stays/carries/boundary” pattern is semantically useful but too fragmented. Make rule rows data; keep prose as overview.
5. **Put an evidence privacy budget beside every receipt class.** Each receipt should say what it may reveal, what it must not reveal, and when it can be pruned or summarized.

### Medium-term changes

1. **Use SLSA/in-toto/Sigstore as adapters, not as native authority.** DeriveBSD should export/import those forms where useful but keep its internal digest/receipt spine simpler.
2. **Consolidate release-critical hygiene.** The current 382 top-level check scripts create confidence but also maintenance gravity. Keep release-critical checks small and group deep contracts into generated manifests or shared harnesses.
3. **Separate “architecture memory” from “operator front door.”** `docs/00-index.md` and `CHANGELOG.md` are huge. Keep historical detail, but move the default reader path to 5-7 stable pages and let generated catalogs carry the rest.
4. **Make product profiles prove subtraction.** The product profile system is right, but each profile should remove features by default rather than accumulate them.

## Where something has gone severely wrong or wasteful

### Archive sprawl has become a real product risk

The archive contains **3352 files before this audit note**, with **823 docs files**, **368 ADRs**, **184 RFCs**, and **382 top-level check scripts** referenced by the hygiene manifest. `docs/00-index.md` alone is about 818 KiB, and `CHANGELOG.md` is about 544 KiB. This is not merely aesthetic clutter; it makes the system harder to audit because important invariants are dispersed across hundreds of small documents.

### The harness may be outrunning the executable core

The release-critical ledger in rev0577 says 49/49 checks passed, which is good. But the shape of the cube suggests a deeper inversion: DeriveBSD has become extremely good at describing and validating its intended boundaries, while the decisive real-world target remains missing. The highest-value correction is not more validation language; it is one end-to-end proof from hardware into the cube.

### Removable-media proof work dominates the archive

Filename-level metrics show `removable-media` in **531 files** totaling about **3.36 MiB**, while the real host proof import directory is empty. That ratio is the clearest waste signal I found. The idea is important, but the cube should stop expanding it until hardware reality is represented.

### The cutline doctrine is right but not fully enforced

`docs/401-v0-cutline-and-feature-tiers.md` correctly warns that the failure mode is “shipping nothing because the design surface never stops expanding.” The archive itself appears to be living in that danger zone. The rule “new core forbidden by default” should be enforced socially and mechanically in the next several turns.

## Online research checkpoint

- FreeBSD 15.1 is the current primary release target to track for the proof lane; the official FreeBSD release process lists the 15.1 announcement on 2026-06-16 and 15.1 EOL on 2027-03-31.
- FreeBSD 14.4 is now the better supported 14.x legacy floor; the official 14.4 schedule lists 14.3 EOL on 2026-06-30, 14.4 EOL on 2026-12-31, and stable/14 EOL on 2028-11-30.
- Nix/NixOS is the obvious comparison for isolated reproducible/declarative builds, but DeriveBSD should not imitate Nix’s whole universe. It should borrow the derivation discipline and make the BSD host/workload evidence story simpler.
- Qubes is the obvious comparison for compartmentalization; DeriveBSD’s best differentiation is server/fleet/appliance/workstation profiles over FreeBSD primitives rather than a desktop-only security OS.
- Talos is the obvious comparison for immutable, minimal, declarative infrastructure hosts. DeriveBSD can learn from Talos’s subtractive discipline: no general shell-shaped snowflake host if the profile does not need it.
- SLSA, in-toto, and Sigstore are relevant export/import ecosystems. They should be compatibility surfaces, not reasons to multiply DeriveBSD-native receipt types forever.

## Local validation note

The checked-in rev0577 release-critical ledger reports:

- result: `passed`
- passed: `49`
- failed: `0`
- run complete: `True`
- generated-for version: `2026-06-17r604`

During this audit I also corrected my own extraction method after noticing that Python ZIP extraction can drop executable mode bits. Re-extracting with ZIP Unix mode metadata preserved made the executable-bit guard pass locally. I did not claim a new full release-critical pass for this rev0578 audit archive.

## Recommended next turn

Make a focused `targetfloor` patch:

1. update `tools/freebsd/host_proof_contract.py` from 14.3 legacy floor to 14.4 legacy floor,
2. update the real-host operator packet text,
3. add or adjust canonical examples that reference the floor,
4. keep 14.3 only as historical/import fixture language,
5. run the release-critical hygiene lane after the patch.

This is small, time-sensitive, and mission-aligned: it reduces stale support ambiguity without widening the system.
