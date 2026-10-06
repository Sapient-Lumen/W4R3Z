# DeriveBSD rev0600 mission audit — recovery first

**Archive revision:** `rev0600`  
**Internal product cut retained:** `2026-06-18r625`  
**Source archive:** `DeriveBSD-rev0599-2026.06.18.07.16-statejournal-crashguard-sable(1).zip`  
**Source archive SHA-256:** `9489f491f81f7e0f5cb5842828ddf1b924ea0f7718c7abc958908963628bf491`  
**Audit date:** 2026-06-18  
**Scope:** mission, executable runtime, evidence semantics, product gaps, structural waste, current FreeBSD fit, and ordered correction plan.

This is deliberately an **audit cut**, not a false product release. It adds this review and a compact machine-readable companion without changing the r625 runtime or regenerating the cube's giant ledgers. That restraint is part of the recommendation.

## Executive judgment

The heart of DeriveBSD is:

> **Compile declarative intent into recoverable FreeBSD authority transitions, with an independently checkable chain from inputs and policy to artifacts, activation, runtime actions, and recovery.**

A less compressed product statement is:

> DeriveBSD is an evidence-native control plane for stock FreeBSD that builds immutable host/workload artifacts, stages them behind least-authority boundaries, switches them transactionally, and can always explain or recover the resulting state.

That is stronger and more distinctive than “a new BSD distribution.” It is also narrower than the current cube. The product is not the schema collection, the receipt vocabulary, the removable-media proof conveyor, or even the content-addressed build system by itself. Those are support structures. The product moment is when an operator can safely say:

> “Take this pinned intent, prepare one new host generation and one isolated workload, switch once, prove what actually happened, and recover after either a bad result or an interrupted commit.”

The archive understands most of this conceptually. Since the rev0588 mission correction, it also made meaningful progress: r615–r625 created and hardened a real dry-run golden thread. It is no longer accurate to say that nothing executes. The current runtime can perform:

`Spec → Lock → Plan → Artifact → Activate → Explain → Rollback`

with path-stable digests, strict JSON, finite fixture resolution, tamper checks, a sealed local artifact tree, rollback preconditions, honest no-FreeBSD-effect claims, and a real-backend admission path that refuses rather than fakes success.

The decisive problem has moved. The cube is now approximately **80–90% of the way to a credible simulation and perhaps 10–20% of the way to a usable product**. Nearly all remaining product value is concentrated in a few hard seams:

1. crash recovery and receipt atomicity;
2. a genuinely immutable, concurrent-safe content-addressed store;
3. complete input locking and correct resolver boundaries;
4. a real FreeBSD jailed build backend;
5. a real ZFS boot-environment activation/health/recovery backend;
6. a minimal bhyve authority broker;
7. independent host evidence and an operator-grade `status`/`recover` experience.

Adding more schemas, marker checkers, generated indexes, or proof envelopes now has negative expected value unless it directly closes one of those seams.

## The mission kernel

Four primitives are genuinely central.

### 1. Derivation

Typed intent becomes locked inputs, an evaluated plan, and a realized object. The identity chain must bind the exact source, base-system channel, third-party package repository snapshot, workload image or VM bundle, toolchain, policy decision, target platform, and output tree.

### 2. Authority reduction

Fetch, build, activate, and launch are distinct trust domains. Build jobs do not inherit host authority. Activation and VM lifecycle go through small, typed, least-privilege adapters. FreeBSD jails, ZFS boot environments, bhyve, Capsicum/Casper, devfs rules, and pf are implementation leverage, not the mission by themselves.

### 3. Reversible transactions

Rollback is necessary but insufficient. A production control plane must also recover from a crash at every point between preparation, state mutation, receipt publication, health observation, and commit. Recovery is therefore a first-class stage, not an operator note after “activate.”

A more accurate lifecycle is:

`Intent → Lock → Plan → Realize → Stage → Commit → Observe → Confirm or Recover`

### 4. Evidence with explicit strength

Every important object and transition should be explainable, but “proof” must not collapse several different claims. DeriveBSD should name at least these levels separately:

- **integrity:** bytes match a digest;
- **authenticity:** a recognized actor or platform signed the statement;
- **authorization:** an admitted policy decision permitted the action;
- **execution evidence:** an isolated executor reports that the action ran;
- **state observation:** an independent observer measured the resulting host/workload state;
- **acceptance:** a health or user criterion passed.

A digest-bound JSON object written by the same process that performed a local simulation has integrity and useful traceability. It does not, by itself, prove that a FreeBSD operation occurred, that the writer was trustworthy, or that the resulting state was healthy. The current runtime is commendably honest in many `truth_claim` fields, but the project's top-level “proof-carrying” language still outruns the executable trust model. Until signatures, isolation, and independent observation exist, **evidence-native** is the more accurate term.

## What is strong and worth preserving

- The Spec → Lock → Plan → Artifact identity model is coherent.
- The archive repeatedly treats denied operations as evidence-producing outcomes, which is operationally valuable.
- Local locators and wall-clock fields were removed from runtime content identity after the first implementation exposed path instability.
- The runtime refuses unknown packages instead of pretending an unbounded resolver succeeded.
- Artifact trees reject symlinks, hardlink aliases, writable modes, and post-build byte tamper before activation.
- Rollback verifies both the activation receipt digest and the expected current generation.
- The `freebsd-real` branch requires admitted preflight and imported primary-host evidence before reaching an explicit “backend not implemented” refusal.
- The release-critical and schema-audit profiles are green, so the cube is internally coherent.
- The archive itself already says “contract-rich but product-poor” and forbids new core by default. The strategic diagnosis is not missing; enforcement and prioritization are.

These are real assets. The recommendation is not to throw away rigor. It is to make rigor follow executable authority transitions rather than substitute for them.

## Quantitative shape

Measured from the rev0599 source before this review was added:

| Surface | Measured size |
|---|---:|
| All files | 3,443 / 26,706,504 bytes |
| JSON + Markdown + Python | 3,425 files (99.5%) / 99.8% of bytes |
| Documentation | 824 files / 105,530 lines |
| Specifications | 1,277 files / 170,094 lines |
| ADRs | 368 files / 22,186 lines |
| RFCs | 184 files / 8,949 lines |
| Session reviews | 318 files / 163,515 lines / 7,194,665 bytes |
| Python | 423 files / 66,951 lines |
| Top-level checker programs | 385 files / 53,220 lines |
| `tools/derive_runtime.py` | 1 file / 1,576 lines |
| Release headings | 294, from r326 to r625 |
| Calendar span | 91 days, 2026-03-20 through 2026-06-18 |
| Mean cut rate | 3.23 release headings per calendar day |

The top-level checker code is **33.8 times** the size of the executable runtime. Documentation, specs, ADRs, RFCs, and session-review text together are **298 times** the runtime's line count.

This is not primarily a disk-space problem. Exact duplicate files account for only eight groups and roughly 204 KB of avoidable bytes. The waste is semantic and cognitive: repeated contract slices, generated discovery surfaces, per-cut ledgers, and human-facing files that became machine registries.

## Severe correctness findings

### Critical architectural defect 1: crash safety without recovery liveness

The r625 precommit journal improves visibility, but its transaction is incomplete.

Relevant code:

- `tools/derive_runtime.py:1086-1092` blocks any pending journal;
- `tools/derive_runtime.py:1148-1199` uses an `O_EXCL` lock file and removes it only in Python cleanup;
- `tools/derive_runtime.py:1255-1268` creates a generation, writes a precommit journal, changes the pointer, and clears the journal;
- `tools/derive_runtime.py:1269-1300` constructs and writes the authoritative activation receipt **after leaving** the protected transaction;
- rollback has the same receipt-after-journal-clear pattern.

The CLI offers `lock`, `plan`, `build`, `host-preflight`, `host-proof-status`, `activate`, `rollback`, `explain`, and `run-golden-thread`. It has no `state-status` or `recover` command.

Crash windows include:

| Crash point | Durable result | Current behavior |
|---|---|---|
| after lock-file creation | stale lock | all future mutations blocked until manual deletion |
| after generation file creation, before journal | orphan generation | deterministic retry may hit no-clobber refusal |
| after journal, before pointer | prepared but not applied | all future mutations blocked; no classifier/recovery |
| after pointer, before journal clear | applied but unfinished | all future mutations blocked; no finalizer |
| after journal clear, before activation receipt | state changed, receipt absent | rollback authority and `state_before` can be lost |
| analogous rollback window | state restored, rollback receipt absent | operation occurred without authoritative completion evidence |

A local probe confirmed that both a stale lock and any pending journal permanently refuse mutation, while no recovery subcommand exists. This is fail-closed safety but not a usable transaction protocol.

**Required correction:**

1. Use a kernel-released advisory lock (`flock`/`fcntl`) with a metadata sidecar, rather than treating an `O_EXCL` file as the lock itself.
2. Give every mutation an operation ID and a durable state machine: `prepared → state-applied → receipt-durable → complete`.
3. Bind the intended receipt path and receipt material into the journal before state mutation.
4. Do not clear/archive the journal until the authoritative receipt is durable.
5. Add `derive state-status` and `derive recover`.
6. Recovery must classify the live pointer against journal `before` and `after` digests:
   - live = before: abort prepared operation and clean safe orphans;
   - live = after: finalize the missing receipt and complete;
   - live = neither: mark divergence and require explicit repair, without guessing.
7. Test process death at every durability boundary, not only pre-created stale files.

This should be the next implementation priority. A control plane whose signature promise is recoverability cannot leave an operator with “delete the hidden file and hope.”

### Critical architectural defect 2: the store is mutable and race-prone

The store contract says new builds produce new immutable objects and the store is keyed by object digest. The runtime does something else:

- creates a provisional path using only the last 12 hex characters of the plan digest;
- computes an artifact ID from plan + manifest but truncates it to 32 hex characters;
- if the final path already exists, deliberately chmods and recursively deletes it;
- renames the new tree into the now-vacant path.

Relevant code: `tools/derive_runtime.py:1018-1028` and `tools/derive_runtime.py:911-930`.

A probe built the same plan, mutated the existing destination with a sentinel, and built again. The command returned success; the artifact path and receipt bytes stayed identical, the destination inode changed, and the sentinel vanished. The runtime therefore replaced an object while claiming the same immutable identity.

Consequences:

- the implementation contradicts `docs/03-store.md`;
- readers can race a destructive rebuild;
- concurrent builders can delete or overwrite each other's destination;
- a corrupted existing object is silently replaced instead of surfaced as a store-integrity event;
- the path is not keyed by the full serialized object digest.

**Required correction:**

1. Compute the canonical serialized-tree/object digest first and use the full digest as path authority.
2. Build in a sibling staging directory on the same filesystem.
3. Acquire a store-scoped or object-scoped kernel lock before publication.
4. If the final object already exists, verify it and reuse it; never delete it in the build path.
5. If verification fails, quarantine the existing object and stop. Repair must be an explicit operation with evidence.
6. Publish with no-clobber semantics, fsync the object and parent directory, then write/index provenance.
7. Add parallel-build, crash-before/after-rename, existing-valid-object, and existing-corrupt-object tests.

### High defect 3: “lock every input” is false for the canonical workload

The checked canonical spec contains:

`targets.microvms[0].image.closure = "services/nginx:latest"`

`microvm_targets()` copies `image` and declared secret names through unchanged. The resulting lock and plan still contain the floating `latest` reference. Package resolution is finite for `requested_packages`, but it does not resolve the workload image/closure or the secret material/policy needed by the VM.

A digest over the string `services/nginx:latest` pins the spelling, not the bytes to which the mutable tag will later point.

**Required correction:** reject floating workload references in release mode and resolve every workload bundle to an immutable digest plus transitive closure. Secret values should not enter a lockfile, but secret requirements, broker policy, namespace, version/rotation posture, and delivery authority must be pinned enough that a plan cannot silently mean something different later.

### High defect 4: base-system and third-party package semantics are conflated

The fixture resolver emits a `pkgbase-fixture://` reference for `www/nginx`. On FreeBSD, base-system packages and third-party Ports/pkg packages are different channels. Nginx belongs to the third-party package/ports world, not the FreeBSD base-system package set.

The resolver model should be split:

- **base OS channel:** distribution sets/freebsd-update, source build, or `FreeBSD-base` packages, each with its own snapshot and trust policy;
- **third-party packages:** pkg repository catalog, ABI, package manifest, package file digest, dependency closure, and repository trust metadata;
- **workload bundles/images:** a separate resolver and format, potentially with OCI as a transport adapter but not a mutable tag as identity.

FreeBSD's current handbook still labels package-based base installation as a tech preview while fully supporting traditional distribution sets; 15.1 release notes also show pkgbase integration advancing rapidly. The safe design is capability-driven adapters, not a v0 architecture that requires one still-evolving base delivery mechanism.

### High defect 5: archive release labels contaminate content identity

`generated_for_version = 2026-06-18r625` is not in `_RUNTIME_IDENTITY_IGNORED_KEYS`. Changing only that release label changes the lock digest. At the observed cut rate, documentation/checker-only cuts can invalidate lock, plan, artifact, and receipt identities even when the executable semantics and actual inputs are unchanged.

This is cache-hostile and semantically wrong. The identity should bind what can affect the result:

- canonicalization/schema profile;
- exact runtime/builder binary digest;
- resolver implementation and repository snapshot digest;
- policy engine and decision digest;
- sandbox/backend version and target capability set;
- source/toolchain/workload inputs.

The archive cut belongs in non-authoritative metadata or an excluded annotation. A stable `builder_identity_digest` is stronger than a fast-moving release string.

### High defect 6: receipt integrity is being mistaken for provenance strength

The current receipts are unsigned and are authored by the same Python process that simulates the operation. This is useful prototype metadata, but it is not hostile-builder-resistant provenance. SLSA's current model explicitly treats the lowest provenance level as useful for preventing mistakes while still being easy to forge; higher levels require platform-generated signed provenance and stronger build isolation.

DeriveBSD should publish an `evidence_strength` block on every decisive receipt, for example:

- `integrity = digest-only`;
- `authenticity = unsigned-local-process`;
- `executor_isolation = none | jail | vm | hosted-platform`;
- `observer = self | independent-host-agent | external-verifier`;
- `host_class = fixture | virtual-freebsd | physical-freebsd`;
- `acceptance = not-run | passed | failed`.

That turns the archive's honesty into a machine-readable invariant and prevents a green simulation from being confused with a production proof.

### Medium defect 7: profile identity diverges from the canonical product contract

The profile document says tooling should normalize alias A to canonical ID `fleet_host`. The runtime hardcodes `profile-a-fleet-host`. This creates a parallel identifier and bypasses the supposedly canonical product-profile artifact.

Use `fleet_host` in runtime objects and compile defaults from one small profile registry. Do not carry four large profiles into the executable path before profile A works.

## What is still missing from the product

### A real build

The current build writes a tiny manifest, rc.conf fragment, and non-executed VM launch intent. It does not execute a build DAG, enter a jail, enforce network denial, materialize a package closure, or produce independently verifiable provenance.

The first real build should be deliberately modest: prefetch pinned inputs, enter a networkless FreeBSD jail with declared mounts only, install/build one third-party package closure, emit a serialized tree, and record the exact jail configuration and executor identity.

### A real host transaction

The `freebsd-real` branch is an honest refusal. The first implementation should layer onto stock FreeBSD rather than first owning the full distribution:

1. `bectl check` and capability preflight;
2. create/clone and mount a new boot environment;
3. apply the already-realized artifact in the mounted BE or a BE jail;
4. validate boot-critical files and service configuration;
5. activate temporarily for the next boot (`bectl activate -t`);
6. boot a small health/confirmation service;
7. permanently confirm the generation only after acceptance, otherwise reboot/fall back;
8. emit receipts at prepare, temporary activation, boot observation, confirmation, and recovery.

FreeBSD 15.1's `bectl` can check, create, mount, jail, and temporarily activate boot environments. This maps unusually well to the mission, but the health-confirm/recovery protocol is the product logic DeriveBSD must add.

### A real workload authority boundary

`derive-vmmd` remains an ADR/RFC concept. v0 needs only a small local service:

- Unix socket;
- fixed typed launch/stop requests;
- verification of pinned VM bundle, policy decision, resource ceilings, disk/network attachments;
- pre-opened authority and Capsicum where practical;
- deterministic instance identity and idempotency;
- launch/stop/denial receipts;
- no cluster scheduler and no general remote shell.

Using an existing bhyve manager as a bounded adapter for the first host proof is reasonable if DeriveBSD records the adapter version and keeps the stable Plan → Receipt boundary. Replacing the adapter can come later.

### An operator recovery surface

The conceptual system is sophisticated, but the executable CLI lacks the commands an operator will reach for during failure. v0 needs:

- `derive status` — current generation, pending operation, health, divergence;
- `derive diff` — intended vs current host/workload state;
- `derive explain` — verified graph with evidence-strength labels;
- `derive recover` — classify and complete/abort an interrupted transaction;
- `derive doctor` — capability, repository, ZFS, bhyve, and trust-root checks.

### Independent reality

The checked import status remains `blocked-no-real-host-proof-import`, with zero real-host and zero primary-production entries. The next evidence step is not another envelope. It is one disposable FreeBSD host run, followed by regression work only for failures actually observed.

A virtual FreeBSD/ZFS host can prove activation mechanics. A bhyve lifecycle may require nested-virtualization-capable infrastructure or a physical FreeBSD host. Those evidence classes should remain distinct.

## Where the cube became wasteful

### Human front doors became machine APIs

`README.md` is 82 KB; 198 top-level checker programs reference it. The current “short” start page is only 60 lines but 13.4 KB and contains a 5,782-character line. `docs/00-index.md` is 838 KB, the LLM runbook 254 KB, and the lessons file 469 KB.

A ratchet that allows a giant file to remain giant is not a front-door solution. Machine-required markers should move to a compact generated registry; the README should become a human document again.

Correction path:

1. create one machine-owned contract/index manifest from existing facts, without inventing new domain semantics;
2. migrate token-presence checkers to that registry on touch;
3. generate archival indexes from the registry rather than making every current document repeat the markers;
4. cap the README near 8–12 KB and the current start page near 2–4 KB;
5. keep cut history only in the changelog/archive, not duplicated in the README.

### Checker proliferation became the easiest form of progress

There are 385 top-level checker programs and 53,220 lines of checker code around a 1,576-line runtime. Some checks are valuable semantic regressions. Many are one-off token/shape assertions that could be table-driven.

Do not rewrite all checkers at once. Introduce one shared rule runner, migrate repetitive marker checks when touched, retain custom code only for semantic or adversarial behavior, and measure the number deleted. A new checker should require either a demonstrated executable failure or retirement of equivalent surface.

### Release bookkeeping is too granular

The changelog records 294 cuts in 91 calendar days. Archive packaging revisions, internal development commits, schema revisions, and user-visible product releases are being treated too similarly. This causes identity churn, repeated ledgers, and attention dilution.

Use three separate notions:

- archive/session revision (`rev0600` style);
- executable protocol/schema versions that change only on compatibility boundaries;
- product releases tied to demonstrated host capability.

A checker hardening patch should not create a new semantic product identity.

### Session evidence is repeatedly snapshotted

The session-review directory is 7.2 MB; 59 release-critical ledgers alone occupy 4.79 MB. Exact byte duplication is modest, but repeated full result arrays are still cognitive and archival sediment.

Keep the latest successful ledger per active profile plus milestone checkpoints. Store a compact summary and hash for intermediate runs. Preserve failures that teach something; do not preserve every routine green array forever.

### The ontology expanded ahead of observed users

Four product profiles, hundreds of receipt types, workstation flows, publish sessions, packet capture, removable media, attestation, breakglass, and support workflows are designed at a depth that no executable profile currently consumes. Much of it is thoughtful, but it creates a false sense that product breadth is nearly complete.

Freeze profiles B–D and all optional lanes. Profile A should compile from one small spec into one real host and one VM. Features earn re-entry through an observed user or host failure.

## External comparison and strategic implication

Current systems already cover much of the generic territory:

- NixOS has declarative generations and rollback.
- bootc provides transactional in-place host updates using OCI images.
- Talos and Bottlerocket demonstrate purpose-built, minimal, API-managed hosts with atomic update/rollback postures.
- Qubes organizes a product around one memorable security idea: compartmentalization.
- SLSA and in-toto provide interoperable provenance/attestation vocabularies.

DeriveBSD therefore cannot differentiate merely by being declarative, immutable, transactional, VM-isolated, or provenance-aware. Its credible wedge is the combination of:

1. stock-FreeBSD-native implementation;
2. one graph joining build inputs, policy authority, BE activation, bhyve lifecycle, and recovery;
3. typed denied outcomes and operator explanation;
4. transaction recovery as a first-class security property.

That is narrow enough to ship and uncommon enough to matter.

FreeBSD 15.1 was announced on 2026-06-16 and is a timely acceptance target, but the point release is scheduled to reach end of life on 2027-03-31 while stable/15 extends much longer. Hardcoding `15.1-RELEASE` and its cut token throughout identity-bearing objects will age quickly. Model a `stable/15` capability contract and use 15.1 as the first tested implementation target.

## Speculation, clearly labeled

These are interpretations rather than proven facts.

1. **An agentic production flywheel likely formed.** A new contract, checker, fixture, index update, changelog entry, and green ledger are cheap and measurable in a text-heavy environment. Real FreeBSD integration is slower, scarce, and failure-prone. The archive's formulaic breadth and cut cadence are consistent with the easy loop dominating the hard loop.
2. **Goodhart's law is visible.** “All checkers green” began as a useful proxy for coherence, then became an optimization target that can stay green while the content store violates its own invariant and the crash guard has no recovery path.
3. **The best near-term product is probably not a distribution.** “Derive Control Plane for FreeBSD” installed on stock FreeBSD has a smaller trusted and organizational scope. It can later own more of the base system after proving demand.
4. **The strongest moat is recoverable authority, not receipts alone.** Receipt schemas are copyable. A reliable implementation that can classify and repair interrupted host/VM transitions while preserving an explanation graph is much harder to copy.
5. **Evidence can become surveillance debt.** “Receipts everywhere” eventually requires retention limits, redaction, tenant separation, selective disclosure, and deliberate non-collection. Otherwise the evidence spine becomes a high-value record of identities, devices, incidents, secrets metadata, and operator behavior.
6. **Without contraction, the cube may become a reference ontology.** That could still be intellectually useful, but it would be a different project from an operating control plane. The next real-host cuts decide which path it takes.

## Ordered correction plan

### P0 — make the existing spine truthful under failure

1. Implement the state transaction/recovery protocol and `state-status`/`recover` commands.
2. Replace destructive artifact publication with a full-digest immutable CAS and concurrency tests.
3. Resolve or reject every floating workload input; split base, third-party package, and VM-bundle resolvers.
4. Remove archive release labels from runtime identity; bind actual implementation/policy/resolver digests.
5. Normalize the runtime profile to canonical `fleet_host`.

No new domain schema family is justified while these remain open.

### P1 — cross the FreeBSD boundary

1. Implement a real jailed build for one pinned third-party package closure.
2. Implement `bectl` staging, temporary next-boot activation, boot health, confirmation, and recovery.
3. Run the acceptance path on a clean FreeBSD 15.1 ZFS VM and import the evidence as `virtual-real-host`, not “production proof.”
4. Implement or adapt one minimal bhyve launch/stop path on nested-virtualization-capable or physical hardware.
5. Sign decisive receipts with a host/control-plane key and export standard SLSA/in-toto-compatible provenance.

### P2 — make it operable and independently credible

1. Add status/diff/doctor/explain/recover UX.
2. Add destructive crash and concurrency integration tests.
3. Add external-user acceptance and a small support/runbook path based on observed failures.
4. Define evidence retention, redaction, and selective-export defaults.
5. Contract the front doors, checker registry, and historical ledgers.

### P3 — only after profile A is real

Re-admit workstation, general-purpose OS, appliance factory, removable-media expansion, publish-session expansion, and other optional lanes only when a concrete user story cannot be satisfied by the profile-A core plus a bounded adapter.

## v0 acceptance criterion

A v0 release should mean one command path can do all of the following on a clean supported FreeBSD/ZFS host:

1. read a minimal `fleet_host` spec;
2. resolve every base/package/workload input to immutable identity;
3. build or assemble one artifact in a network-denied jail;
4. publish it once to an immutable full-digest store;
5. stage a boot environment;
6. activate it temporarily and survive an injected crash at every transaction boundary;
7. confirm or recover based on boot health;
8. launch and stop one pinned bhyve workload through a least-privilege broker;
9. explain the chain with evidence-strength labels;
10. reproduce the same result from the same inputs or explain any divergence.

“52/52 cube checks passed” remains useful supporting evidence. It is not the v0 acceptance criterion.

## Work performed for this audit

- extracted and inventoried the source archive;
- read the mission/core/store/sandbox/security/activation/VM/profile/cutline/current-runtime surfaces and recent session reviews;
- measured file, line, release, checker, front-door, and session-ledger shape;
- ran release-critical hygiene: **52/52 passed**;
- ran schema-cube audit: **3/3 passed**;
- ran the r625 golden thread successfully with no FreeBSD system mutation;
- reproduced destructive replacement of an existing same-identity artifact destination;
- demonstrated stale lock and pending-journal permanent refusal with no CLI recovery command;
- confirmed the canonical `services/nginx:latest` workload reference passes unchanged into lock and plan;
- confirmed changing only `generated_for_version` changes runtime identity;
- confirmed runtime profile `profile-a-fleet-host` differs from canonical `fleet_host`;
- checked current official FreeBSD, SLSA, NixOS, bootc, Talos, Bottlerocket, Qubes, and in-toto material.

Baseline cube source fingerprint from both hygiene ledgers:

`sha256:e6af273f7264f67b9643d9d13e32ce18aaf3b49e6aeb35154657189a814c1335`

Baseline ledger hashes:

- release-critical: `9639ab816fe573dc49aa8e55f4c78df4efd4a201e4516a950a8413c5a5c1ba1a`
- schema-cube-audit: `6d5e5f31078f3358742c31980e091ad171a52b515c590d2de280fc4562d35e23`

Probe-evidence hashes:

- CAS overwrite: `a78306138e62d85d373ba60593c80a606520957db38a7cbb89a28d4c28969af9`
- crashguard liveness: `28303c4f3f33cfd559a1e419bfbd14e9113ee86f0691e79ca64f47615b1f5ad3`
- floating workload input: `44f19a1f0bb98b9bbbb3666cb6841f4133b6ef4ec9aa1f3a6e32dd7006d55e85`
- release-identity/profile divergence: `e46e814e19eddda452e2b294cd060565f25976bf408a5e173df5f7f52b73c791`
- golden-thread summary: `fa54695dd493c01d09c66b6b8d6e0d8cda3bee223d0f939e74ab23563a14dde4`

The raw `/tmp` probe files are not copied into the cube; their compact observations are preserved in the companion review JSON. This avoids adding another evidence-file family merely to report the audit.

## Online sources consulted

- FreeBSD 15.1 release schedule: https://www.freebsd.org/releases/15.1R/schedule/
- FreeBSD 15.1 release notes: https://www.freebsd.org/releases/15.1R/relnotes/
- FreeBSD Handbook, installation: https://docs.freebsd.org/en/books/handbook/bsdinstall/
- FreeBSD Handbook, updating/base packages: https://docs.freebsd.org/en/books/handbook/cutting-edge/
- FreeBSD Handbook, packages and ports: https://docs.freebsd.org/en/books/handbook/ports/
- FreeBSD Handbook, jails: https://docs.freebsd.org/en/books/handbook/jails/
- FreeBSD `bectl(8)`: https://man.freebsd.org/cgi/man.cgi?format=html&query=bectl&sektion=8
- FreeBSD `bhyve(8)`: https://man.freebsd.org/bhyve
- FreeBSD Capsicum overview: https://docs.freebsd.org/en/books/handbook/security/
- SLSA v1.2: https://slsa.dev/spec/v1.2/
- in-toto: https://in-toto.io/
- NixOS manual: https://nixos.org/manual/nixos/stable/
- bootc: https://bootc-dev.github.io/bootc/
- Talos Linux: https://www.talos.dev/
- AWS Bottlerocket documentation: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-bottlerocket.html
- Qubes OS: https://www.qubes-os.org/

## Final disposition

**Continue:** the runtime-first correction, strict truth claims, adversarial tests, FreeBSD-native primitives, typed denied outcomes, and the evidence graph.

**Stop:** new ontology breadth, README-as-registry, per-tweak semantic releases, repeated green ledgers, more removable-media envelope work, and any use of “proof” that does not name its trust level.

**Start:** recovery before rollback, immutable no-clobber store publication, complete input locking, capability-driven FreeBSD adapters, independent observation, and one real profile-A acceptance run.

The next revision should repair the transaction state machine before extending the runtime elsewhere. That change protects the mission's center rather than adding another perimeter.
