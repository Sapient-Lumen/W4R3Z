# DeriveBSD rev0588 session review — mission kernel and runtime-first correction

## Executive judgment

DeriveBSD's heart is not “a new BSD distribution.” It is a **FreeBSD-native proof-carrying authority system**: declarative intent should compile into immutable host and workload artifacts, and every privileged transition should be least-authority, explainable, reproducible, rollbackable, and receipt-producing.

The archive expresses that idea with unusual depth. The decisive problem is an inversion between specification and product. The cube is excellent at validating its own contracts, but the promised system is not yet executable end to end. In this archive I found no implementation path for `derive lock`, `derive plan`, `derive build`, `derive activate`, `derive explain`, or `derive-vmmd`; the checked-in real-host proof count is also zero. A green cube therefore means “the archive is internally coherent,” not “DeriveBSD exists as a usable system.”

The correction is to make **profile A fleet host** the sole first product and require one golden thread before widening any contract surface:

`Spec → Lock → Plan → Artifact → Activate/Rollback → bhyve Launch/Stop → Explain`

## Heart of the mission

A concise mission statement:

> Compile intent into verified FreeBSD state while preserving an inspectable chain of inputs, authority, execution, and rollback.

This has four inseparable parts:

1. **Derivation:** typed intent, locked inputs, explicit plans, content-addressed outputs.
2. **Authority control:** builds and runtime operations receive only the capabilities they need.
3. **Operational reversibility:** ZFS boot environments and immutable artifacts make switching and rollback ordinary.
4. **Evidence:** builds, imports, activations, launches, emergency actions, and support handoffs emit joinable receipts that answer “what, why, from where, and under whose authority?”

FreeBSD is a coherent substrate for this mission: jails for build isolation, ZFS boot environments for activation and rollback, bhyve for workload boundaries, pf for composable networking, and Capsicum/Casper for authority reduction.

## What is already strong

- The foundational pipeline and identity chain are conceptually clear.
- The archive consistently treats introspection and evidence as product features rather than afterthoughts.
- The pattern catalog provides reusable security shapes: Plan→Apply→Receipt, Broker→Lease→Receipt, Registry→Diff→Gate, Quarantine→Promote, and Adapter→Shadow→Replace.
- The current FreeBSD removable-media proof kit is genuinely executable within its narrow lane. It has collectors, validators, deterministic handoff sealing, safe import, audits, idempotent retry, race exclusion, and explicit simulation-versus-real-proof classification.
- Release evidence is honest about incompleteness: an empty import root remains blocked rather than becoming a synthetic pass.

## What is missing

### 1. The executable Derive core

The largest gap is not another schema or proof wrapper. It is product code. The archive describes store, sandbox, lock, plan, activation, microVM control, and explainability, but does not connect them into one runnable command path.

A v0 needs at least:

- a small `derive` CLI;
- canonical parsing of one minimal system/workload spec;
- source and toolchain locking;
- one network-denied FreeBSD build sandbox;
- a content-addressed output store;
- ZFS boot-environment activation and rollback;
- one bhyve workload lifecycle;
- a human-readable `derive explain` traversal over the resulting receipts.

### 2. Real FreeBSD execution evidence

The live proof report remains:

- `status = blocked-no-real-host-proof-import`
- `proof_complete = false`
- `real_host_proof = 0`
- `primary_production_real_host_proof = 0`

The existing work order should be run once on a primary-production FreeBSD 15.1 host. Further transport hardening should follow observed failures, not precede evidence indefinitely.

### 3. A product acceptance test

There is no single test whose success means “DeriveBSD v0 worked.” The release gate should include a clean-host acceptance run that builds, activates, launches, explains, and rolls back. Contract consistency remains a supporting gate, not the ship criterion.

### 4. A narrow initial customer and deployment story

Four profiles are designed before one product exists. Profile A, a minimal fleet host/control plane, is the best wedge. Workstation, general-purpose OS, and appliance-factory profiles should remain future compilation targets until A is demonstrated.

### 5. Independent reality checks

Most current validation is self-referential: project-authored contracts checked by project-authored checkers against project-authored fixtures. Needed next are real FreeBSD CI, destructive integration tests in disposable hosts, hardware/VM coverage, and eventually external users attempting the documented path.

## Quantitative shape of the cube

Measured before adding this review artifact:

| Surface | Size |
|---|---:|
| Documentation | 823 files / 105,484 lines |
| ADR-like files | 368 |
| RFC files | 184 |
| Specification tree | 1,277 files / 167,968 lines |
| Schemas | 457 |
| Canonical top-level examples | 469 |
| All JSON examples/fixtures | 816 |
| Python tools | 421 |
| Checker/validator-like Python tools | 392 (93.1%) |
| Top-level `check_*.py` tools | 384 |
| Removable-media-named files | 644 / 5,069,430 bytes |
| Session-review surface | 302 files / 6,763,207 bytes |
| Changelog release headings | 283 across 25 dates |
| Median / maximum headings per release date | 8 / 43 |

These numbers do not prove poor quality. They do show that the project has invested far more visible mass in contracts, validation, and historical bookkeeping than in an executable product path.

## Where things have gone severely wrong or wasteful

### Control-plane inversion

The project set out to make operating-system operations typed and provable. It has instead built a large **meta-control plane for validating descriptions of a future control plane**. With 93.1% of Python tools classified as checker/validator-like and no golden-thread CLI implementation, the assurance machinery is outrunning the thing it is supposed to assure.

### A proof conveyor without the scarce proof

The removable-media lane is careful and technically serious, but 644 filenames now carry removable-media terminology while the real-host import root remains empty. The local optimum became making the handoff increasingly exact rather than crossing the hardware boundary once. The correct next action is collection, not another envelope.

### Green status can reward internal consistency over semantic truth

Two concrete defects demonstrate this:

1. Hygiene runner identity hashed the literal `sys.executable` path. Calling the same interpreter as `python` versus `python3`, or using the documented wrapper's `-S`, could invalidate canonical evidence even though the validation engine had not changed.
2. “Current” schema summaries carried the r614 version and counts while retaining r613 priority prose. Structural synchronization passed while meaning was stale.

The first made proof stricter than the fact being proved. The second shows that token/count checks cannot establish semantic freshness.

### Manually duplicated release identity

The FreeBSD proof bundle ID was frozen to an r613 literal while version fields moved to r614. Generated IDs that duplicate release state by hand invite drift. The ID is now derived from the canonical cube cut.

### Release and front-door sediment

The changelog contains 283 cut headings over 25 dates, with as many as 43 on one date. The index is 838,076 bytes, the LLM runbook 254,182 bytes, the “juicy lessons” document 468,173 bytes, and the short current front door still contains 5,782-character lines. This preserves history but imposes a high attention tax. Ratchet budgets prevent further growth; they do not make the active reader surface usable.

### Standards risk being reimplemented as native ontology

DeriveBSD has a legitimate internal evidence model, but SLSA provenance, in-toto attestations, TUF update trust, and Sigstore bundles already cover major interoperability needs. Native objects should exist only where DeriveBSD has a distinct authority or rollback semantic. Everything else should be a bounded adapter.

## What changed in r614

### Mission and priority

- Named the mission kernel explicitly in the README and scope document.
- Selected profile A fleet host as the sole first product.
- Added the executable golden thread to the v0 cutline.
- Added an admission rule: no new ADR, RFC, schema, example family, checker, or proof transport layer unless it directly unblocks a golden-thread failure or turns an observed real-host failure into a regression.
- Reframed real-host removable-media proof as a necessary evidence task subordinate to, not a substitute for, the executable product gate.

### Proof correctness

- Replaced launcher-path identity with a digest of interpreter bytes plus Python/platform and installed `jsonschema` facts.
- Made normal and `-S` runner discovery agree without hiding real interpreter/package drift.
- Added regressions for renamed identical interpreters and no-site execution.
- Renamed the evidence scope to `python-binary-version-platform-jsonschema`.
- Derived the proof-bundle ID from the current cube release token.
- Corrected stale current-summary priority prose.

### Front-door discipline

- Compacted the already-at-ceiling archive index rather than raising its byte/line budget.
- Put the honest pre-product status and runtime-first gate at the beginning of the README and current start page.

## Online research synthesis

The external comparison supports a narrower product, not a broader feature list:

- **Nix/NixOS** demonstrates the value of declarative, isolated, reproducible system construction. DeriveBSD should borrow the discipline, not recreate the entire Nix ecosystem.
- **Qubes OS** demonstrates that a product can organize itself around one memorable security idea—compartmentalization. DeriveBSD's memorable idea should be proof-carrying authority and rollback on FreeBSD.
- **Talos Linux** and **Bottlerocket** demonstrate subtractive host design: one host role, constrained management, atomic updates, and minimal mutable surface. Profile A should follow that discipline.
- **SLSA** and **in-toto** provide interoperable provenance/attestation models; **TUF** addresses update trust under key compromise; **Sigstore** provides portable verification bundles. DeriveBSD should translate to/from these rather than multiply parallel native formats without a distinct need.
- FreeBSD 15.1 is a timely primary target. Its current packaged-base direction also suggests that DeriveBSD can initially be a control plane layered on stock FreeBSD instead of first becoming a complete base-system distribution.

## Speculation and strategic interpretation

These are inferences, not proven facts:

1. **The archive likely entered an agentic/LLM flywheel.** Repeated sessions can cheaply produce a new contract, checker, fixture, changelog entry, and green ledger. That is measurable and rewarding, while a real OS path requires scarce FreeBSD execution and integration risk. The release cadence and formulaic surface are consistent with this dynamic.
2. **Goodhart's law is operating.** Once “green checkers” became the visible progress measure, the project optimized for more checkable surface. The measure remained useful but stopped tracking product existence.
3. **The strongest near-term product may be “Derive Control Plane for FreeBSD,” not a distribution.** Install onto stock FreeBSD 15.1, manage a jailed builder, a CAS, ZFS boot environments, and bhyve workloads, then earn the right to own more of the base system.
4. **Without the runtime correction, the cube risks becoming a reference ontology rather than software.** That could still have intellectual value, but it would be a different mission.
5. **Receipts everywhere can become surveillance and retention debt.** The evidence spine eventually needs defaults for redaction, retention, aggregation, and deliberate non-collection, or explainability will create its own risk surface.

## Recommended correction sequence

### Phase 1 — Freeze and walk

- Freeze new schemas, ADRs, RFCs, registries, and proof wrappers.
- Implement one small `derive` executable with subcommands behind a single internal object model.
- Use one checked-in minimal profile-A spec as the acceptance fixture.
- Run the full path on one clean FreeBSD 15.1 VM before extending semantics.

### Phase 2 — Prove the host lifecycle

- Build one deterministic artifact in a jailed, network-denied sandbox.
- Put it in a content-addressed store with standard provenance export.
- Create/activate a ZFS boot environment, observe health, and roll back.
- Start and stop one bhyve workload through a small least-privilege service.
- Make `derive explain` traverse the exact spec, lock, plan, artifact, activation, and workload receipts.

### Phase 3 — Replace self-reference with reality

- Add FreeBSD 15.1 CI or a repeatable VM farm.
- Classify evidence levels explicitly: fixture, checker simulation, virtual real-host, physical real-host, and user acceptance.
- Make the product acceptance run release-blocking.
- Run the existing removable-media work order once; only then harden failures it exposes.

### Phase 4 — Contract and archive contraction

- Keep five to seven stable front-door documents; move per-cut prose to generated/archive views.
- Separate session package revisions from semantic product releases.
- Track deletion and consolidation, not only additions.
- Reuse SLSA/in-toto/TUF/Sigstore at interoperability boundaries.
- Add a contract budget: any new Tier A/B object must delete/merge comparable surface or accompany executable product code.

## Validation

Final source fingerprint: `sha256:0793445775a6307c6f087844e1b8f3eef842959dec5ab43713c92b34e786e9d1`

- Release-critical hygiene: **51/51 passed**, 0 failed, 0 timed out, run complete.
- Schema-cube-audit: **3/3 passed**, 0 failed, 0 timed out, run complete.
- Canonical bootstrap ledger validates under both `python` and `python3` launcher names.
- Current proof status: `blocked-no-real-host-proof-import`.
- Real-host proof count: **0**.
- Primary-production real-host proof count: **0**.

## Remaining truth and next highest-risk work

This revision improves truthfulness, proof identity, and strategic focus. It does **not** create a working DeriveBSD runtime and it does **not** supply FreeBSD host evidence from this Linux cloudtainer.

The next highest-risk work is to implement the smallest profile-A golden-thread executable slice on stock FreeBSD 15.1. In parallel, the already-prepared work order should collect exactly one real-host removable-media proof; no additional transport design is justified before that run.
