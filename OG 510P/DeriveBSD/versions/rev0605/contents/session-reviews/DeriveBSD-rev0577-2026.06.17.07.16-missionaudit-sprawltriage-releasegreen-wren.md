# DeriveBSD rev0577 session review — mission heart, gaps, and sprawl triage

## Purpose

This session did not change the DeriveBSD executable surface. It is a deep-read mission audit intended to keep the next cloudtainer turns pointed at the smallest useful repairs rather than more doctrine. The archive's current cut is `2026-06-17r604`; this session revision keeps the external package/session naming line at `rev0577`.

## Read basis

Local read basis:

- `README.md`, especially the `2026-06-17r604` front door.
- `docs/current/start-here-now.md` and the current FreeBSD proof packet.
- `docs/00-vision.md`, `docs/12-design-principles.md`, `docs/13-security-model.md`, `docs/22-scope-and-direction.md`.
- `docs/397-pattern-catalog.md`, `docs/401-v0-cutline-and-feature-tiers.md`, `docs/402-adapter-lanes-and-strangler-discipline.md`, and `docs/348-design-review-rubric-and-feature-intake.md`.
- `docs/_generated/risk_register.json`, `docs/_generated/doc_catalog.json`, and the current schema/hygiene generated summaries.
- The checked-in rev0576 session review and validation ledgers.

External research basis:

- FreeBSD 15.1 release announcement and schedule pages, including the June 16, 2026 release announcement, 15.1 support window, and 15.0 EOL.
- FreeBSD project pages for ZFS, bhyve, jails, and Capsicum.
- Qubes OS architecture documentation for the security-by-compartmentalization comparison.
- TUF, in-toto, and SLSA project documentation for update/supply-chain posture comparisons.
- Nix and Guix documentation for generation rollback and declarative system-management comparison.

## Heart of the mission

The heart is not “make another BSD distribution.” It is to make a BSD-rooted operating-system pipeline where every important byte, mutation, import, authority grant, and support handoff becomes a typed, digest-addressed object with a receipt. FreeBSD is the substrate because jails, bhyve, ZFS boot environments, pf, and Capsicum map unusually well onto that idea. The product promise is: build from explicit inputs, launch with small blast radius, mutate only through planned/receipted paths, explain why a thing exists, and roll back without archaeology.

A tighter one-line mission:

> DeriveBSD turns FreeBSD hosts and workloads into explainable, rollbackable, least-authority derivations whose builds, imports, launches, and emergency actions are all evidence-producing.

## What is already unusually strong

- The core workflow is legible: `Spec -> Lock -> Plan -> Artifact -> Activate/Launch`.
- The project has correctly identified “evidence is product” as a differentiator, not a compliance afterthought.
- The pattern catalog is a real anti-sprawl mechanism: Plan→Apply→Receipt, Broker→Lease→Receipt, Registry→Diff→Gate, Quarantine→Promote, Adapter→Shadow→Replace.
- The current FreeBSD host-proof lane has become executable rather than theatrical: collectors, importers, sealers, unsealers, auditors, run receipts, nofollow staging, symlink refusal, deterministic ZIP checks, and release-critical gates all exist.
- Release-critical hygiene passed in this session: 49/49 checks after a resumable continuation; schema-cube-audit passed 3/3.

## What is missing

1. **The scarce proof itself.** The archive still has no checked-in non-simulated FreeBSD receipt. Everything around real-host proof is strong, but the center of the current active lane is still absent.

2. **A v0 walking skeleton.** The archive knows the v0 cutline, but it still needs a small end-to-end artifact path that proves the system shape: source/spec -> jailed build -> artifact -> signed/channel metadata -> ZFS BE activation -> bhyve microVM launch -> explain -> rollback.

3. **A ruthless reader surface.** `docs/current/start-here-now.md` is good, but `docs/00-index.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, and `docs/110-juicy-os-lessons.md` are too large to be the everyday front door. The archive has a ratchet budget, but the budget preserves existing bloat rather than forcing contraction.

4. **A product-story boundary.** The mission is technically coherent, but a new contributor/operator still needs one practical story per profile: fleet host, workstation, general OS, appliance factory. The product profiles exist; the missing piece is the tiny “do this first” path for each profile.

5. **A deletion/merge ritual.** The project has 457 schemas, 469 examples, 368 ADRs, 785 top-level docs, and 423 tool files. Some of this is justified, but without an explicit regular deletion/refactor lane, “receipts everywhere” can become “schemas everywhere.”

6. **A session-revision vs cube-cut explanation.** The package name currently uses `rev0576`/`rev0577` while the cube cut inside says `2026-06-17r604`. That is probably intentional session numbering versus internal cut numbering, but it is easy to misread during handoff. A tiny root-level package manifest should state both fields.

## What should change next

### 1) Make the next scarce-host action the default path

Do not add more proof doctrine before the first non-simulated host handoff. The current next action should be exactly the operator packet path:

```sh
tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh
```

or the handoff-first collect/seal/import path in `docs/current/freebsd-real-host-proof-operator-packet.md` on a real FreeBSD 15.1 host. Bring back either the deterministic sealed handoff ZIP or the exact loose handoff. Import it through the one-command sealed importer unless inspection is needed.

### 2) Add a v0 walking-skeleton ledger

Create one tiny `docs/current/v0-walking-skeleton.md` with exactly these stages and no expansion:

1. build one trivial derivation in a jailed sandbox,
2. emit one artifact receipt,
3. sign or digest-bind one channel target,
4. create one ZFS boot-environment activation plan/receipt mock or real host fixture,
5. launch one bhyve microVM plan/receipt fixture,
6. run `derive explain` or the closest current explain-equivalent over the result,
7. prove rollback selection remains addressable.

If a stage is not implemented, mark it `missing-executable-slice`, not “future work.”

### 3) Convert front-door bloat from “ratcheted” to “shrinking”

The current `tools/baselines/frontdoor_budget.json` prevents silent growth but accepts giant current surfaces: `docs/00-index.md` is about 838 KB / 56k words and `docs/99-llm-runbook.md` is about 254 KB / 22k words. Add a second budget mode: `target_bytes`, lower than current, enforced only when a touched file is edited. This lets the archive shrink opportunistically without blocking unrelated proof work.

### 4) Mark doctrine-only additions as suspect by default

The archive already says this, but the session policy should be blunter: every new ADR/schema/doc must either attach to an executable check, close a named risk-register item, or replace/delete older surface. Otherwise it belongs in an attic/RFC parking lane.

### 5) Add a root package manifest

Add `PACKAGE-REVISION.json` or `docs/current/package-revision.md` in a future cut with:

- `package_revision`: `rev0577`-style session package id,
- `cube_cut`: `2026-06-17r604`-style internal archive id,
- `source_archive`: prior zip basename,
- `validation_ledgers`: release-critical and schema-cube-audit ledger paths,
- `changes_kind`: `analysis-only`, `docs-only`, `code`, or `proof-import`.

This would remove ambiguity without changing the established filename convention.

## Places where something has gone wrong or wasteful

### Prose sediment is the biggest waste

The archive is self-aware about monster growth, but several front-door files have already become too large for human navigation. The cost is not disk size; it is attention. Large generated/catalog docs make it harder to see the one active risk: real FreeBSD proof. The correction is not deletion-first; it is front-door demotion and shrinking budgets.

### The project may be over-optimizing the proof conveyor before carrying real proof

The r576–r604 lane has done useful hardening around sealed handoff import. But every turn spent tightening simulated transport is now competing with the scarce host run. The next high-value correction is a real 15.1 `primary-production` proof handoff. After that, harden whatever failed in the real path.

### Schema gravity is close to self-perpetuating

The schema cube is valuable because it makes evidence joinable. It becomes waste when new schemas are used to avoid building the first vertical path. Current audit numbers already show 457 schemas, 469 examples, 26 refactor-backlog items, and 8 open backlog items. Treat those numbers as load-bearing health metrics: they should trend down or flatten while v0 walking-skeleton code trends up.

### Profile B can become a second product too early

The workstation/AppVM posture is coherent and Qubes-adjacent in the right way, but it can absorb unlimited design energy. Until the fleet-host and removable-media proof lanes are real, B should receive only bug-fixing and boundary-preserving changes, not more feature doctrine.

### “Release green” can hide absence of the real artifact

Release-critical green is meaningful: the checks passed. But it must be read as “the cube’s current invariants hold,” not as “the mission proof exists.” The session review should keep repeating the caveat until the real-host proof is checked in.

## Speculation

DeriveBSD’s best chance is to be the “evidence operating system” rather than the “secure BSD with many features.” Nix/Guix already own much of the declarative/rollback imagination; Qubes already owns compartmentalized desktop mindshare. DeriveBSD’s differentiator is the combination of FreeBSD-native primitives, microVM-first runtime, and receipt-shaped operations across build, import, support, recovery, and breakglass. That could be genuinely novel if the executable path arrives before the documentation mass becomes intimidating.

The failure mode is also clear: it becomes a beautiful evidence ontology around a missing small system. The repair is equally clear: every session should either import real proof, reduce front-door mass, or push the v0 walking skeleton one executable step forward.

## Validation from this session

- Release-critical hygiene: `session-reviews/DeriveBSD-rev0577-2026.06.17.07.16-missionaudit-sprawltriage-releasegreen-wren-release-critical-ledger.json`, passed 49/49 after resumable continuation.
- Schema-cube-audit hygiene: `session-reviews/DeriveBSD-rev0577-2026.06.17.07.16-missionaudit-sprawltriage-releasegreen-wren-schema-cube-audit-ledger.json`, passed 3/3.
- No source/docs/spec/tools changes were made in this review cut; only session-review artifacts and copied ledgers were added.

## Recommended next turn

Add the tiny package/cube revision manifest or run the real FreeBSD 15.1 host-proof handoff. Prefer the host-proof handoff if a real host is available; otherwise add the manifest because it fixes a real handoff ambiguity with minimal surface.
