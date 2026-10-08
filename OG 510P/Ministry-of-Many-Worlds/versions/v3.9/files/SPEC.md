# Ministry of Many Worlds — Language Spec (Draft v3.9)

**Status:** living draft (brainstorm → spec).  
**Last updated:** 2026-01-04  
**Archive:** mmw_spec_2026-01-04_v3.9.zip

## 0. Purpose

Ministry of Many Worlds (MMW) is an esoteric-but-useful programming language whose *runtime semantics* unify:

- **Scoped multiset rewriting** (chemical “soup” execution)
- **Conserved resources & authority** (double-entry / ledger invariants)
- **Receipted reversibility** (time travel with leased undo + fossilization)
- **Fork/choose/merge** (auditable branching search + interference-style merging)
- **Compartment borders** (bureaucratic membranes with treaties, stamps, tariffs)
- **Federated consensus** (mycelial gossip + quorum-minted permits)

MMW’s “weirdness” is not in syntax; it’s in governance: **every step is a stamped, balanced, leased transaction**.

## 1. Core Model

### 1.1 State is a Scoped Multiset

Global state is a multiset of **molecules**, each at a **scope address**:

`Scope = (branch?, cell?, node?, epoch?)`

Example (informal):

- `@branch:b7 @cell:Compliance @node:N3 @epoch:12 : Mol(Form, {id: 9, kind: "restart_pool"})`

Scopes may omit coordinates when unused (e.g., single-node programs).

### 1.2 Molecules

A molecule is an immutable datum with a type/tag and payload.

- `Mol(type, payload)` — general facts, jobs, messages, forms, etc.

Molecules may optionally carry an **Origin Handle**:
- `Origin(mol_id) = (receipt_id, output_slot)`
meaning the molecule was produced by a particular transaction’s receipt in a specific output position.

Origin handles enable minimal provenance, custody enforcement, and refutation targeting without dumping full history.

### 1.3 Conserved Quantities: Resources and Capabilities

MMW distinguishes **data** from **authority**.

- `Res(account, amount, nonce)` — conserved quantities (budgets, entropy, bandwidth, risk, etc.)
- `Cap(kind, scope_tag, nonce)` — **opaque** capabilities/permits

**Opacity rule:** program rules may test for presence/absence of a capability token, but must not pattern-match or introspect its internal fields beyond equality/identity.

### 1.4 Receipts, Seals, Leases, Fossils

Every step emits a receipt and can be undone *while the receipt is leased*.

- `ReceiptH(id, rule, scope, time, delta_digest)` — header (crossable/indexable)
- `ReceiptP(id, payload_digest)` — payload handle (may be sealed / local-only)
- `Seal(id, mode)` — hides payload details while preserving header verifiability
- `Lease(id, until)` — undo window for this receipt
- `Fossil(id)` — receipt is irreversible; history cannot be erased beyond this boundary
- `Witness(claim, receipt_ids)` — compact proof artifact
- `Refuted(id, because)` — evidence is never deleted; it can only be refuted/overturned

### 1.5 Time and Governance

- `Now(t)` — monotone per scope (does not roll back)
- `Epoch(e)` — monotone per node/federation context (used for consensus rounds)
- `Phase(name)` — runtime phase gate (Collect | Explore | Commit)

## 2. The One Event: Transactional Rewrite

### 2.1 Rule Firing is a Transaction

A **rule** matches molecules (typically within one scope) and produces effects.
A step is valid only if it forms a well-defined transaction:

1) **Match** molecules (LHS) in the rule’s legal scope(s)  
2) **Consume/Produce** molecules (RHS)  
3) **Ledger delta** is balanced (conservation) unless explicitly allowed by privileged finalize rules  
4) Emit `ReceiptH` (and optional `ReceiptP`)  
5) Attach `Lease` (and optionally `Seal`)  
6) Optionally emit `Fossil` (finality boundary)

### 2.2 Balancing / Conservation

For accounts designated conserved, the net delta over a transaction must satisfy:

`Σ ΔRes(account) = 0` for each conserved account.

(Accounts can be configured as conserved; the language’s “moral code” emerges from which accounts are conserved and how they’re minted.)

Capabilities (`Cap`) are treated as conserved by default: they cannot be duplicated unless a privileged rule explicitly mints them under strict conditions.

### 2.3 Progress Contract (Anti-Livelock)

To prevent silent infinite spinning, each step must satisfy **at least one**:

- Decrease a well-founded `Potential(name, value)`
- Spend from a finite `Budget(name, amount)` (represented as a `Res` or `Budget` molecule)
- Produce a terminal artifact (`Committed(...)` or `Stuck(...)`)

This contract is enforced by runtime policy (and optionally declared by rules).

## 3. Phase Machine (Chimera Governance)

### 3.2 Regime Effects on Phases (Normative Guidance)

Regimes may alter phase behavior without changing kernel legality.

Recommended effects:
- **Due Process:** Explore enabled; higher budgets for fork/merge; longer grace windows; MDS default on PUBLISH.
- **Emergency Powers:** Explore may be shortened; fork/merge allowed only with explicit standing; CCF default on PUBLISH; sealing defaults to Opaque/Commitment-only; postmortem obligations emitted automatically.
- **Martial Law:** Explore disabled by default; deterministic scheduling in Collect/Commit; aggressive fossilization; narrow grace windows; appeals restricted.

These effects SHOULD be represented by explicit artifacts (RegimeActive + witnesses) and may emit obligations.


MMW alternates among phases:

- **Collect:** LOCAL + GOSSIP
- **Explore:** LOCAL + FORK + MERGE
- **Commit:** LOCAL + BORDER + FINALIZE (and narrowly-scoped distribution of commitments)

### 3.1 Quiescence Gates

Transitions are guarded by quiescence/budget conditions:

- Collect → Explore only when Collect is quiescent (or a budget deadline forces transition)
- Explore → Commit when `Choose(...)` has produced a selected branch with witness, or `ExploreCredit` is exhausted
- Commit → Collect after required fossilization/commitments complete, or `Stuck(...)` is produced for remaining work

### 3.3 Ephemeral Deliberation and FORGET (Creative, Useful)

MMW distinguishes between *governed history* (receipts, fossils, published artifacts) and *deliberation exhaust*.
To keep exploration usable and privacy-preserving, implementations MAY support **ephemeral artifacts**:

- ephemeral artifacts are allowed in Explore forks and counterfactual dockets
- ephemeral artifacts MUST NOT be required to justify a published ruling unless they are converted into admissible evidence (witness/docket)
- ephemeral artifacts may be forgotten via `FORGET`, subject to policy

`FORGET` is an explicit act that:
- marks a set of ephemeral artifacts as no longer retrievable by default
- may destroy local keys for sealed ephemeral payloads (implementation-defined)
- MUST emit a header-visible receipt indicating what was forgotten (scope + epoch + counts), without exposing the content

`FORGET` MUST NOT apply to fossilized receipts or published artifacts. It is a deliberation hygiene tool, not a history rewrite.



## 4. Privileged Standard Library (Constitutional Rules)

These are semantic primitives; implementations may vary, but pre/postconditions are normative.


### 3.4 Legal Holds and Retention Policies (Creative, Normative-ish)

If `FORGET` exists, the system also needs “do NOT forget.”
MMW therefore supports **legal holds** and **retention policies** as governance artifacts.

Recommended artifacts:
- `RetentionPolicy(scope, kind="ephemeral"|"sealed", keep_epochs, by=jurisdiction)`
- `Hold(scope, reason, until_epoch)` / `HoldReleased(scope, ...)`
- `Obligation(RetentionReviewDue, scope, due_epoch)`

Guidance:
- a hold MUST prevent `FORGET` for the affected scope/kind until released or expired
- retention policies SHOULD be treaty-defined across borders (meta-treaties may require them)
- holds SHOULD be time-bounded (sunset by default), and renewal should be explicit and costly
- releasing a hold SHOULD be witnessed and may require a court ruling if a dispute exists

This keeps “forgetting” from becoming an anti-audit loophole while still allowing privacy-preserving deliberation hygiene.





### 3.4.1 Hold Review and Habeas Petitions (Creative, Necessary)

Holds and quarantines can become indefinite power if they are not challengeable.
MMW supports explicit **hold review** procedures and a “habeas”-style petition mechanism.

Recommended artifacts:
- `HabeasPetition(target=Hold|Quarantine|Seal, because=..., by=scope)`
- `HoldReviewScheduled(target, at_epoch)`
- `HoldReviewed(target, outcome=upheld|modified|lifted, witness_id)`
- `HoldLifted(target, because=..., by=jurisdiction)` / `HoldModified(target, new_terms, ...)`
- `ReviewDenied(target, because=...)` (must have a reason summary)

Guidance:
- petitions SHOULD be time-bounded (timebar) and must respect standing
- emergency regimes may temporarily narrow review rights, but MUST sunset and trigger mandatory postmortem
- repeated bad-faith petitions may be throttled (livelock rules), but minimum review service should remain for high-stakes holds
- treaties may require cross-border minimum review guarantees for certain seal/hazard classes

This prevents “hold forever” from becoming a covert veto.

### 3.5 Oblivion Receipts and Forget Proofs (Optional, Esoteric-Useful)

If the system supports `FORGET`, parties may later need confidence that forgetting happened,
*without* reintroducing the forgotten content.

MMW therefore allows optional **oblivion receipts**:

- each ephemeral sealed payload MAY have an associated commitment id (e.g., `EphemeralCommit(id)`)
- `FORGET` MAY emit `OblivionProof(commit_id, scope, epoch, method=...)`

Guidance:
- an oblivion proof SHOULD attest that local keys for the committed payload were destroyed or rendered inaccessible
  under a declared method (implementation-defined)
- oblivion proofs MUST remain header-visible and auditable, but MUST NOT allow payload recovery by themselves
- legal holds MUST prevent issuance of oblivion proofs for affected scopes/kinds

This gives “right to be forgotten” semantics a verifiable footprint without making deletion a lie.


### 4.1 CROSS (Borders / Bureaucracy)
**Pre:** Treaty allows schema; required border capability present; tariffs/budgets available.  
**Post:** Molecule appears in destination scope; `Stamp` emitted; tariffs deducted; receipt emitted; origin updated.

### 4.2 FORK (Branching Search)

### 4.2.1 Allocation References (Normative)

#### Reconciliation on MERGE (Normative)

When branches merge, allocation references must reconcile spent status.

- If exactly one branch contains `Spent(id)`, the merged state contains `Spent(id)`.
- If neither branch has `Spent(id)`, the merged state contains the unspent allocation (or equivalent representation).
- If **both** branches contain `Spent(id)` for the same allocation, this is a **double-spend conflict**.

Double-spend conflicts MUST NOT be silently resolved. An implementation MUST either:
1) produce `Stuck("DoubleSpend", evidence=...)` in the merged scope, OR
2) fork an **appeal** procedure that adjudicates which spend is admissible, emitting a ruling witness and refuting the losing spend.

Regimes may choose (1) strict failure under Martial Law, or (2) adjudication under Due Process.


To prevent double-spend across branches, conserved resources and capabilities must be **split** or **referenced** on `FORK`.

MMW permits two equivalent strategies:

- **Split:** replace a token with two smaller tokens whose amounts sum to the original.
- **Reference:** replace a token with an **allocation reference** that can be spent at most once.

An allocation reference is conceptually:

- `Alloc(id, amount)` with a global uniqueness guarantee for `id`

Spending requires consuming the allocation and producing a `Spent(id)` marker (or equivalent),
which prevents reuse across branches and merges.

Implementations may encode `Alloc`/`Spent` as molecules, as ledger entries, or as runtime-managed identifiers,
but the semantics must ensure: **no branch can spend the same allocation twice**, and merges must reconcile spent status.

Allocation references are recommended for opaque capabilities that cannot be meaningfully “split”.

**Pre:** exploration budget available; split policy defined.  
**Post:** facts may duplicate; conserved resources/caps are split or referenced to prevent double-spend; fork receipt emitted.

### 4.3 CHOOSE (Choose-as-Query)
**Pre:** candidate branches exist; invariants defined; limits/budgets defined.  
**Post:** `ChosenBranch(id)` + `Witness(...)`; other branches collapsed with reasons.

### 4.4 MERGE+NORMALIZE (Interference)
**Pre:** reconcilable conserved ledgers/caps; conflict domain declared.  
**Post:** ordinary facts may cancel/merge; receipts/evidence cannot cancel; must decrease coherence potential or spend merge budget.

### 4.5 QUORUM_COMMIT (Federation)
**Pre:** within Epoch(e); weighted votes satisfy quorum.  
**Post:** mints `Cap(ActionPermit, ...)` or `Committed(...)`; emits witness; optionally fossilizes commitment header.

### 4.6 FOSSILIZE (Finality)
**Pre:** explicit commit boundary or externalization (export) event.  
**Post:** emits `Fossil(receipt_id)`; rollback beyond boundary forbidden; only compensations allowed.

### 4.7 APPEAL / REFUTE (Court of Appeals module)
**Pre:** standing/jurisdiction receipts; evidence threshold; within grace window or pays late-appeal budget.  
**Post:** emits `Refuted(...)`; may fork rehearing; later resolved by choose/merge.

## 5. Bundle Profiles

Each “bundle” is the kernel + a small organ set.

### 5.1 Cellular Bureaucracy
Adds:
- `Treaty(cell, import_schema, export_schema)`
- `Cross(from_cell, to_cell, mol_id)`
- `Stamp(cell, mol_id, kind)`
- Optional: `Tariff(dim, amount)` (often encoded via `Res` accounts)

### 5.2 Multiverse Auditor
Adds:
- `Fork(label)`
- `Choose(criteria)`
- `Collapse(branch, reason)`

### 5.3 Grace-Period Timekeeping
Adds:
- `TTL(mol_id, expires)`
- `Commit(scope_tag)`
- `Retry(token, backoff)`

### 5.4 Interference Engine
Adds:
- `Amplitude(branch, value)`
- `Conflict(key)`
- `Merge(op)`

### 5.5 Mycelial Federation
Adds:
- `Rumor(claim, source)`
- `Vote(claim, yesno, weight)`
- `Quorum(k, trust_threshold)`

## 5.6 Treaties as Types (Normative Interpretation)

MMW treats **border treaties** as the primary “type system.” A treaty does not merely allow or deny
movement; it specifies what is *observable* across a boundary.

### Observable Schema (Projection)

For each crossable molecule kind, a treaty defines a **projection** of the payload:

- `project(payload) -> public_view`

Only the public view is permitted to cross borders in cleartext. Any non-observable fields must be:
- omitted, or
- moved into sealed receipt payloads (`Seal`), or
- transformed into redacted summaries.

This enforces “information flow typing” by customs:
- **Type error** = customs rejection at `CROSS`
- **Redaction** = customs-mandated projection
- **Capability opacity** prevents smuggling via permits

### Sensitivity Lattice (Creative, Recommended)

Treaties may annotate projected fields with a sensitivity label to drive sealing and risk classification:

- `Public` (exportable in clear)
- `Confidential` (exportable only as redacted summary)
- `Secret` (exportable only as commitment-only or opaque)
- `Sealed` (must remain sealed; only revealable via standing)

A treaty may define a mapping from sensitivity → required sealing dialect.
This functions like an information-flow lattice without a traditional type system.

### Treaty Versioning and Deprecation (Normative Guidance)

Treaties SHOULD be versioned:
- `Treaty(name, version)` is the effective contract at a border.

Border operations (`CROSS`, `GOSSIP`, `PUBLISH`) MUST record which treaty version was used for projection.
When a treaty version is deprecated:
- crossings using deprecated versions MAY be rejected, permitted under amnesty, or forced into probationary export.
- deprecation SHOULD emit migration obligations (see below).

### Treaty Migrations (Creative Pattern)

When treaty projections change, systems often need a migration path.
Recommended workflow:
1) publish new treaty version (governance)
2) emit `Obligation(MigrationDue, treaty=..., from=v_old, to=v_new, due_epoch)`
3) produce **Migration Dockets**: evidence bundles that show which exports/crossings were upgraded or grandfathered
4) optionally issue amnesty scoped to the migration window

This treats interface changes like legal reforms rather than silent breaking changes.


### Treaty Test Dockets (Creative Pattern)

Treaties act like type signatures at borders, so they should be testable.

A **treaty test docket** bundles:
- a treaty version reference,
- example inputs (often sealed or synthetic),
- expected projections (schemas + redaction behavior),
- expected risk/sensitivity classifications.

Uses:
- validating treaty implementations during ratification windows,
- proving backward compatibility (or documenting intentional breaking changes),
- adjudicating “your border mis-projected my data” disputes in court.

Treaty test dockets can be signed by notaries and may be required by meta-treaties for new treaty versions.

Treaties therefore serve three roles simultaneously:
1) module interface contract (what a cell exports/imports)
2) security boundary (what information may leave)
3) semantic type checker for inter-cell composition


## 6. Queries & Introspection (Normative)

MMW bakes in “why-based” introspection. These are not mere debugger features: they are part of the language’s
governance model.


### Treaty Fuzz Dockets (Creative Pattern)

Beyond fixed examples, treaties can be stress-tested with randomized or adversarial cases.

A **treaty fuzz docket** bundles:
- a treaty version reference,
- a seed reference (preferably a `RandomBeacon` epoch),
- a generator specification (how to synthesize edge-case payloads),
- assertions about projection behavior (schema validity, redaction invariants, hazard/risk classification).

Guidance:
- fuzz dockets SHOULD be used during ratification windows for high-impact treaties
- failures SHOULD emit `Obligation(TreatyPatchDue, ...)` or `Obligation(MigrationDue, ...)`
- fuzz payloads SHOULD default to synthetic or sealed to avoid leaking real data; headers remain honest-by-default

This treats treaty evolution like hardening a compiler: correctness is socially governed, but bugs are found mechanically.



### Treaty Withdrawal and Secession (Creative, Dangerous)

Federations need an explicit “exit hatch” to avoid pretending nobody ever leaves.

Recommended artifacts:
- `TreatyWithdrawal(treaty_ref, by=jurisdiction, effective_epoch)`
- `TreatyTermination(treaty_ref, at_epoch)` (mutual or adjudicated)
- `Secession(jurisdiction, because=..., effective_epoch)`
- `ExitSettlement(jurisdiction, obligations=[...], escrow=[...])`

Guidance:
- withdrawals/secessions SHOULD use long notice windows (timebars) and emit migration obligations
- treaties MAY forbid secession or require bicameral quorum + constitutional review
- exit processes SHOULD preserve minimum interoperability (probationary export, quarantine rules)
- dead-man escrow is recommended for protected sources during exit (anti-suppression)
- impact assessment is recommended: exit is high blast radius (ImpactBudget / LegitimacyBudget)

This is intentionally “loud and expensive”: exits are allowed, but not casual.



### Dependencies and Compatibility Proofs (Creative, Extremely Useful)

Treaties and statutes behave like packages: versions depend on other versions.
MMW supports optional explicit dependency graphs and compatibility proofs.

Recommended artifacts:
- `DependsOn(target_version, deps=[(name, version_range), ...])`
- `IncompatibleWith(target_version, other_version, because=...)`
- `CompatProof(target_version, deps, proof_id)` / `CompatFailed(target_version, because=...)`

Guidance:
- AMEND/REPEAL SHOULD update dependency declarations and emit migration obligations when ranges change
- borders MAY refuse imports whose dependency graph is unsatisfied locally (or force probationary export)
- proof-carrying governance can require `Proof(kind="deps-satisfied", ...)` for high-impact changes
- composting can preserve dependency digests even when receipts are compacted

This is supply-chain governance: you can reason about what law depends on what.


### 6.1 Core Queries

1) **WHY** is `X` present / permitted / committed?
2) **WHY NOT** did `Goal` occur?
3) **WHAT IF** policy/budget/phase were different?

Implementations may realize these as built-in queries, REPL commands, or molecules such as:

- `QueryWhy(target)`
- `QueryWhyNot(goal)`
- `QueryWhatIf(policy_delta)`

### 6.2 Expected Outputs

Query results must be representable as *first-class artifacts*, typically:

- `Witness(claim, receipt_ids)`
- `Stuck(reason, evidence)`
- minimal “blocking set” molecules (which caps/budgets/potentials prevented progress)
- optional sealed subproofs (headers public, payload sealed)

### 6.4 Honest-by-Default (Normative)

Query results MUST include header-minimum accountability metadata even when details are sealed:
- which sealing dialect(s) were applied,
- which regime/preset was active,
- aggregate budget deltas (or digests),
- whether externalization cone policy was MDS or CCF.

Queries may omit payload details, but they may not pretend actions were “free” or “unsealed” when they were not.

### 6.3 Jurisdiction & Minimality

Queries should prefer **minimal receipt chains** using Origin handles:
- evidence is cited by `ReceiptH` and origin lineage
- details may remain sealed while preserving verifiability


### Counterfactual Dockets and Dream Court (Creative, Useful)

`WHAT IF` is not just a question; it can be preserved as an artifact.

- A **counterfactual docket** bundles a hypothetical branch: inputs, assumed treaty versions, regime, and proposed actions.
- Counterfactual dockets are **non-exportable by default** (internal only) unless explicitly published (often probationary export).
- A **Dream Court** is a Claim Court configured to adjudicate counterfactual dockets, producing:
  - proposed rulings,
  - predicted obligations/costs,
  - and regret deltas (optional), without externalization.

This lets MMW do scenario planning (“what would the court do?” / “what would it cost?”) as first-class computation.


## 7. Legal Doctrines for Rules (Creative Standard Library)

MMW rules may optionally declare “doctrines” that shape behavior without changing the kernel.
These are metadata conventions intended to become a recognizable idiom.

- **Standing:** who is allowed to act (capability requirements)
- **Jurisdiction:** what receipts/origin lineage must be cited
- **Burden of Proof:** what evidence threshold is required (witness requirements)
- **Remedy:** how failures are represented (stuck, appeal, compensating transaction)
- **Sunset:** which leases/TTLs apply (grace windows)

Doctrines integrate naturally with receipts, treaties, and quorum permits, and provide an expressive way to encode
policy engines, compliance flows, and dispute resolution.


### 7.1 Canonical Appeal Pipeline (Template)

A common pattern (“case law”) for resolving disputes:

1) **Contest:** emit `Contested(claim, because=...)` (non-normative molecule) and preserve all evidence.
2) **Rehearing Fork:** `FORK("appeal")` into a branch scoped to the target jurisdiction.
3) **Admissibility Check:** admit only receipt headers/witnesses valid in that jurisdiction.
4) **Deliberation:** optionally MERGE competing rehearing branches under interference rules (e.g., cancellation of inconsistent facts).
5) **Ruling:** `CHOOSE` a ruling branch; emit `Witness("ruling: ...", ...)` in the target jurisdiction.
6) **Remedy:** either `Refuted(prior_receipt, because=...)` or `Superseded(prior_witness, new_witness)`.
7) **Finality:** externalization or explicit commit triggers fossilization under MDS/CCF policy.

This pipeline turns “debugging” and “governance” into the same mechanism.


## 7.2 Obligations (Creative Primitive)

MMW introduces **obligations** as first-class artifacts that represent required future governance actions.
Obligations are not side notes; they are enforceable “debts” in the legal/administrative sense.

Examples:
- `Obligation(PostmortemDue, override_id, due_epoch)`
- `Obligation(AuditRequired, docket_id, due_epoch)`
- `Obligation(EscrowReleaseEligible, docket_id, after_epoch)`
- `Obligation(CompensationDue, receipt_id, due_time)`

### Obligation Generation (Normative Guidance)

Obligations should be generated compositionally by key governance events:
- Treaty Override emits `Obligation(PostmortemDue, override_id, due_epoch)`.
- PUBLISH may emit `Obligation(AuditRequired, docket_id, due_epoch)` for high-risk exports.
- ESCROW_RELEASE may emit `Obligation(RevealReviewDue, docket_id, due_epoch)`.

Treaties and regimes may declare obligation templates (“if X happens, create Y debt by T”).

### Discharge and Delegation (Normative Guidance)

**Discharge** fulfills an obligation and should be represented explicitly:
- `Discharged(obligation_id, witness_id)` (non-normative helper)
- a discharge MUST emit a witness citing the evidence of fulfillment

**Delegation** assigns responsibility without erasing the debt:
- `Delegated(obligation_id, to_scope)` (non-normative helper)
- delegation MUST preserve the original obligation id and due time
- treaties may restrict delegation across borders (standing required)

Implementations MAY provide privileged helpers (`DISCHARGE`, `DELEGATE`) but the semantics are: obligations are immutable debts; only their status evolves.

### Enforcement

Unmet obligations may trigger automatic consequences by policy/regime, such as:
- legitimacy bleed per epoch,
- escalation to stricter regimes,
- quarantining of affected exports,
- emission of `Stuck("ObligationUnmet", ...)` for dependent workflows.

Obligations are a clean way to encode “paperwork due” and “governance deadlines” without hardcoding them into every rule.


## 7.3 Claim Court (Canonical Pattern)

A Claim Court is a reusable statute bundle that adjudicates claims and emits rulings with proper supersession.

### Inputs (Typical)
- `Claim(X)` or `Deny(X)` molecules
- submitted evidence references (receipt headers, dockets, witnesses)
- standing tokens for participants/judges

### Process (Typical)
1) **Intake:** verify admissibility (jurisdiction, standing, treaty constraints).
2) **Deliberation:** optionally fork rehearsals; merge/cancel inconsistent internal facts.
3) **Ruling:** choose a branch; emit `Witness("ruling: ...", ...)` in court jurisdiction.
4) **Supersession:** emit `Superseded(old, new)` or `Refuted(target, because)` as remedy.
5) **Docketing:** produce a docket bundle for portability and audit.

Claim Court makes “truth maintenance” an explicit legal workflow rather than a hidden algorithm.


### Judicial Review (Creative Pattern)

Courts may evaluate not only claims but also the validity of statutes/treaty clauses (“constitutional review”).

Recommended artifacts:
- `Challenged(rule_or_treaty_ref, because=...)`
- `Invalidated(rule_or_treaty_ref, because=..., by_witness=...)`
- `Stayed(rule_or_treaty_ref, until_epoch, ...)`

Guidance:
- invalidation requires higher-jurisdiction standing and must be witnessed + docketed
- stays provide a grace window to migrate rather than hard-breaking the system
- invalidation should emit migration obligations and may require amnesty to smooth rollout

This makes “rule changes” and “rule challenges” first-class governance, not ad-hoc admin actions.



### Constitutional Court (Creative Pattern)

A Constitutional Court is a Claim Court with elevated jurisdiction that specializes in:
- interpreting amendments (AMEND) and treaty versions,
- resolving conflicts between statutes and meta-treaties,
- issuing stays and migration obligations to avoid hard breaks.

It should default to:
- verdict sealing (public outcome, sealed reasoning),
- strict admissibility and standing,
- mandatory docketing and (often) AUDIT_PASS after major rulings.


### Amicus Briefs (Creative Pattern)

Third parties may submit evidence or arguments without being direct parties.

Recommended artifacts:
- `Amicus(case_id, docket_id, by=scope)`
- `AcceptedAmicus(case_id, docket_id)` / `RejectedAmicus(...)`

Guidance:
- acceptance requires standing of the court (or jury) and is witnessed + docketed
- abusive amicus spam can incur `PaperworkDebt` or spend `LegitimacyBudget`
- sealed amicus payloads are allowed; headers must remain visible



### Timebars and Statutes of Limitation (Optional Governance)

Courts can be overwhelmed if every ancient dispute stays litigable forever.
MMW therefore supports optional **timebars**:

Recommended artifacts:
- `Timebar(kind, scope, start_epoch, end_epoch, by=jurisdiction)`
- `Timebarred(case_id, because=...)`
- `TollingGranted(case_id, until_epoch, because=...)`

Guidance:
- timebars SHOULD be public in headers (so parties can plan)
- tolling (pausing the clock) requires standing and should be witnessed
- emergency regimes may shorten or extend timebars (with sunsets + legitimacy cost)
- whistleblower or protected-source cases may receive presumptive tolling

Timebars turn “stale case backlog” into explicit policy rather than silent neglect.



### Exhaustion Doctrine and Appeal Ladders (Creative, Useful)

To keep higher courts from being spammed, systems can require *exhaustion of remedies*.

Recommended artifacts:
- `Appealed(case_id, to_court, by=scope)`
- `ExhaustedRemedies(case_id)`
- `DeniedForNonExhaustion(case_id)`
- `FinalJudgment(case_id, at_epoch)`

Guidance:
- appeals may require bonds (CaseCredit) and must respect timebars
- constitutional review SHOULD require an exhaustion witness unless emergency standing applies
- finality should be explicit: once final, changes require supersession via AMEND/judicial review, not casual relitigation

This turns the “appeal ladder” into programmable governance.



### Jury Nullification (Creative Pattern)

Sometimes a jury believes that applying a statute would be unjust, even if the facts fit.
MMW allows an explicit (and expensive) **nullification** mechanism.

Recommended artifacts:
- `Nullified(case_id, statute_ref, by=juror_or_panel, because=...)`
- `NullificationCited(case_id, precedent_or_case)`
- `NullificationReviewed(case_id, outcome=upheld|reversed)`

Guidance:
- nullification MUST be witnessed and docketed (reason may be sealed but must have a reason summary)
- nullification SHOULD spend `LegitimacyBudget` and MAY mint `PrecedentDebt` (optional) to make it rare
- nullifications SHOULD trigger mandatory review by a higher court or en banc panel when cross-border effects exist
- treaties may declare certain classes “non-nullifiable” (e.g., quarantine/hazard constraints)

This makes “jury conscience” a first-class output without turning law into silent chaos.



### Mootness and Live Controversy (Creative Pattern)

Courts can conserve capacity by refusing to adjudicate disputes that no longer matter.
MMW supports optional **mootness** and **advisory opinion** rules.

Recommended artifacts:
- `Moot(case_id, because=...)`
- `AdvisoryOpinionRequested(issue, by=scope)`
- `AdvisoryOpinionDenied(issue, because=...)`
- `AdvisoryOpinion(issue, witness_id)`

Guidance:
- by default, courts SHOULD require a live controversy (standing + concrete effect)
- Dream Court can serve most “advisory opinion” needs without externalization
- constitutional courts may allow advisory opinions only under strict quorum and sunset constraints

This keeps courts from becoming a general Q&A backlog.



### Standards of Proof and Burden Allocation (Creative, Useful)

Not all claims require the same confidence.
MMW supports explicit **standards of proof** as doctrine, often treaty-defined.

Recommended artifacts:
- `StandardOfProof(level="preponderance"|"clear_and_convincing"|"beyond_reasonable_doubt"|custom)`
- `BurdenOfProof(issue, on=party_scope, standard=level)`
- `FailedBurden(issue, because=...)`

Guidance:
- higher standards MAY require additional proof-carrying artifacts and/or spend more `ProofBudget`
- treaties MAY map risk/hazard classes to default standards
- parties may stipulate to standards and facts via docketed `Stipulation(...)`

This makes “how sure are we?” part of the program.



### Settlements and Plea Agreements (Creative, Extremely Useful)

Not every dispute should be fully litigated. MMW supports explicit settlement and plea flows
as first-class, docketed artifacts.

Recommended artifacts:
- `SettlementProposed(case_id, terms, by=scope)`
- `SettlementAccepted(case_id, by=scope)` / `SettlementRejected(case_id, because=...)`
- `SettlementApproved(case_id, witness_id)` / `SettlementDenied(case_id, because=...)`
- `PleaEntered(case_id, counts=[...], because=...)`
- `PleaAccepted(case_id, witness_id)` / `PleaWithdrawn(case_id, because=...)`

Guidance:
- settlement/plea terms SHOULD compile to remediation orders + phased obligations + milestones (and may be underwritten)
- courts SHOULD require minimum reason summaries for approvals (even if terms are sealed)
- treaties MAY restrict “non-reviewable” pleas for hazard/quarantine violations
- abuse control: repeated bad-faith proposals may accrue `PaperworkDebt` and trigger throttling/sanctions

This enables negotiated governance outcomes without silent backroom edits.



## 7.3.1 Jury Duty and Duty Rosters (Creative Pattern)

In federated deployments, “who audits” and “who judges” can be selected via a duty roster mechanism:
- eligible nodes/agents are those holding `Cap(JuryEligible, ...)` and sufficient `TrustStake`
- selection is weighted by stake and constrained by `BandwidthCredit` / `LatencyBudget` (so duty is affordable)
- selected jurors receive `Cap(JuryDuty, case_id, nonce)` with a lease

Jurors may be compensated (or penalized) via conserved accounts, creating a verifiable incentive loop.

This pattern is intentionally weird but useful: it provides sybil-resistant, capacity-aware selection for audits and courts.


### Service Credits and Sanctions (Creative, Useful)

Jury duty creates real costs. MMW recommends an explicit service loop:

- completing duty can mint `ServiceCredit` (optional account) or replenish `TrustStake` within caps
- failing to serve without admissible recusal can incur `PaperworkDebt` or spend `LegitimacyBudget`
- repeated failure may revoke `JuryEligible` standing for a lease window

Service artifacts should be docketed so selection incentives remain auditable.




### Cooling-Off Periods (Anti-Corruption Pattern)

To reduce revolving-door corruption:
- jurors/notaries who handled a case MAY be barred from receiving related bounties or contracts for a cooling-off window
- cooling-off rules can be encoded as obligations:
  - `Obligation(CoolingOff, actor, scope, until_epoch)`

Cooling-off obligations should be enforceable (injunction/remediation) and visible in headers.


### Slashing and Misconduct (Creative, Useful)

To discourage corruption:
- jurors/notaries may stake `TrustStake` or `ServiceCredit` as a bond
- proven misconduct can slash the bond via a witnessed ruling:
  - `Slashed(actor_id, amount, because=...)`

Misconduct allegations should be docketed and may be handled by a higher-jurisdiction court.


### Random Beacons and Lotteries (Creative, Useful)

Federated selection (juries, audits, duty rosters) benefits from **unpredictable but verifiable** randomness.

Recommended artifacts:
- `RandomBeacon(epoch, commit, by=notary_or_quorum)`
- `RandomReveal(epoch, value, proves=commit)`
- `LotterySelected(kind, epoch, seed_ref, winners=[...])`

Guidance:
- beacon commits SHOULD be published before reveals to prevent biasing (“commit then reveal”)
- notaries/jurors SHOULD be selected using the beacon seed + header-visible eligibility constraints
- revealing a beacon may spend `Entropy` (or be tied to Telemetry cadence) to prevent “free grinding”
- disputes about bias become justiciable: parties can challenge beacon procedure via dockets

This gives MMW a civic-grade RNG: not magic, but governed evidence.

## 7.3.2 Recusal, Challenges, and Conflicts (Creative Pattern)

Claim Courts and audits may require recusal mechanics to avoid captured governance.

Recommended artifacts:
- `ConflictOfInterest(juror_id, case_id, because=...)`
- `Recused(juror_id, case_id)`
- `Challenge(juror_id, case_id, by=...)`

Normative-ish guidance:
- A challenge MUST be justified by header-visible evidence or an admissible sealed docket reference.
- Recusal decisions SHOULD be witnessed and docketed (no silent swapping).
- Excessive or abusive challenges MAY spend `LegitimacyBudget` or incur `PaperworkDebt` (to prevent denial-of-service against courts).



### Recusal Registry and Disclosure (Hardening)

Recusal should not be a silent side-channel. MMW recommends an auditable disclosure path.

Recommended artifacts:
- `ConflictDeclared(actor, case_id, category, because=...)`
- `Recused(actor, case_id, because=...)`
- `RecusalDenied(actor, case_id, because=...)`
- `RecusalChallenged(actor, case_id, by=scope, because=...)`
- `RecusalRegistryEntry(actor, case_id, outcome, at_epoch)`

Guidance:
- conflict declarations SHOULD be header-visible at least as a category + existence marker
- the detailed “because” may be sealed but MUST have a reason summary
- repeated conflict concealment is fraud and may trigger slashing (due process)
- treaties may require a minimum disclosure schema across borders

This keeps recusals from becoming “quiet judge shopping.”


## 7.4 Canonical Obligation Enforcers (Standard Statutes)

### Remediation Orders and Injunctions (Creative, Useful)

Not all outcomes are “pay a debt.” Sometimes the system must require *repair*.

Recommended artifacts:
- `Injunction(case_id, forbids=[...], until_epoch=...)`
- `RemediationOrder(case_id, requires=[...], due_epoch, by=jurisdiction)`
- `ComplianceReport(case_id, docket_id)`
- `Contempt(case_id, because=...)`

Guidance:
- injunctions should sunset and require renewal (SUNSET default)
- remediation orders can create structured obligations with milestones (phased)
- contempt should be expensive: spend legitimacy, may slash bonds only with strong evidence

This allows governance to order actions, not just account deltas.


### Statute Complexity and ComplexityBudget (Optional, Esoteric-Useful)

Policy can become unreadable. MMW optionally prices *complexity* itself.

- statutes may be required to declare an estimated complexity (size, branching factor, proof burden)
- enacting or amending high-complexity statutes spends `ComplexityBudget`
- audits may restore a small amount of ComplexityBudget by producing simplified, equivalent statute bundles

This turns “bureaucratic bloat” into a conserved resource problem.




### Surety and Underwriting (Creative Pattern)

Sometimes you want a guarantee: “if they don’t do the remediation, someone else will pay/do it.”
MMW supports optional **surety/underwriting** for obligations.

Recommended artifacts:
- `Underwrite(obligation_id, by=actor, collateral=TrustStake|CaseCredit, amount, expires=epoch)`
- `UnderwriteClaimed(obligation_id, by=beneficiary, because=...)`
- `UnderwritePaid(obligation_id, amount, by=underwriter)`
- `UnderwriteDefault(obligation_id, because=...)`

Guidance:
- underwriting MUST be witnessed and docketed (reason summary required)
- collateral may be slashed on default under due process (ties into Slashing / Witness Liability)
- underwriting can be funded or incentivized via `BOUNTY` / TreasuryCredit
- conflicts of interest apply (recusal/cooling-off); underwriters in a case should face stricter disclosure
- underwriting pairs well with phased obligations: milestones can auto-trigger claimed underwriting

This makes “insurance for governance outcomes” a first-class construct.


### Witness Liability (Creative, Useful)

Witnesses are powerful; reckless or malicious witnesses can corrupt the system.
MMW recommends optional liability:

- if a witness is later **refuted for fraud**, the witness author may be slashed (`Slashed(...)`) subject to due process
- if a witness is merely superseded (good-faith correction), no penalty is implied
- courts may require higher bonds for repeat bad-faith witnesses

This encourages cautious testimony without punishing honest mistakes.



#### Telemetry Misreport (Recommended)

If telemetry dockets exist, intentional misreporting SHOULD be treated as fraud:
- telemetry can be challenged via a docket and adjudicated by a court
- if a telemetry witness is refuted for fraud, slashing MAY apply under due process


### Case Market Scheduler (Optional Economics)

Courts and auditors can be overwhelmed. MMW may schedule adjudication using a market-like mechanism:

- Cases carry `Res(CaseCredit, amount)` or equivalent.
- Statutes “bid” to process cases; higher bids get priority under constrained capacity.
- Unprocessed cases accrue `PaperworkDebt` (interest) or trigger escalation obligations.
- Under Due Process, low-credit cases can still be heard via jury duty rotation (fairness floor).
- Under Emergency Powers, high-risk cases may be auto-prioritized regardless of bids (policy override with legitimacy cost).

This turns backlog into a visible economic signal without requiring ad-hoc priority hacks.




### Deliberation Markets (Optional, Extremely Weird)

Beyond adjudicating cases, systems may want to allocate scarce *thinking*:
audits, proofs, treaty fuzzing, and migration work.

A deliberation market is like the case market but for governance labor:
- tasks are issued as obligations (`ProofDue`, `AuditDue`, `TreatyPatchDue`, `MigrationDue`)
- tasks can be funded by `TreasuryCredit` bounties and prioritized with `CaseCredit`
- completion requires evidence: a docket + witness (often notary or court)

Guardrails:
- markets MUST not override due process: low-credit tasks still get minimum service under regimes
- markets SHOULD be bounded by `ComplexityBudget` and `ProofBudget` to prevent “infinite proof grinding”
- conflicts of interest are governed (cooling-off, recusals, slashing)

This is “economics of governance compute,” made explicit and auditable.


### Appeal Bonds and Filing Fees (Anti-Spam, Useful)

To reduce frivolous litigation and denial-of-service:
- filings (appeals, challenges, amicus briefs) MAY require a bond posted in `CaseCredit` and/or `PaperworkDebt` escrow
- if the filing is adjudicated as non-frivolous or succeeds, the bond may be refunded (or converted to ServiceCredit)
- abusive patterns may burn `LegitimacyBudget` or increase required bond multipliers

Bonds are especially useful for high-load federations where capacity is scarce.

### DISCHARGE (Privileged Helper)

### DELEGATE (Privileged Helper)

Implementations SHOULD provide a privileged delegation helper that:
- requires standing to delegate across borders (`Cap(DelegatePermit, ...)`),
- records delegation chains as header-visible metadata (who delegated to whom, when, and under which jurisdiction),
- preserves the original obligation id and due time,
- may require the delegatee to accept (quorum or explicit accept statute).

Delegation MUST NOT erase responsibility; it only changes who is expected to discharge the obligation.

Implementations SHOULD provide a privileged discharge helper that:
- verifies the obligation’s fulfillment criteria (policy-defined),
- emits `Witness("obligation discharged", ...)` citing evidence,
- updates (or emits) discharged status, and
- reduces `PaperworkDebt` if that optional economy is enabled.

Discharge MUST be auditable and MUST NOT be implicit.

### Interest and Paperwork Debt (Optional Economics)

MMW may model “paperwork debt” as a compounding penalty for unmet obligations.

A common implementation pattern:
- overdue obligations cause an enforcer statute to mint a `Res(PaperworkDebt, amount)` (or similar),
- the debt grows per epoch (interest),
- certain actions (publishes, overrides, reveals) may be blocked when debt exceeds policy thresholds,
- debt may be reduced only by satisfying obligations (filing postmortems, completing audits, compensations).

This turns governance latency into an explicit economic signal and makes “ignoring paperwork” semantically expensive.


To avoid bespoke “if debt unpaid then punish” rules everywhere, MMW recommends standard enforcer statutes.

Examples:
- **Legitimacy Bleed Enforcer:** if `Obligation(PostmortemDue, ..., due_epoch)` is past due, spend `LegitimacyBudget` each epoch and emit `Witness("bleed applied", ...)`.
- **Quarantine Enforcer:** if `Obligation(AuditRequired, ...)` is past due, quarantine affected exports and block dependent publishes.
- **Escrow Freeze Enforcer:** if reveal-review obligations are unmet, disable further releases for related scopes.

Enforcers are policy hooks: they make governance consequences consistent, auditable, and composable.


## 8. Account Palette (Recommended Conserved Dimensions)

### Exchange Bureau (Optional, Very Esoteric)

Sometimes a system wants to trade one conserved resource for another (e.g., spend legitimacy to accelerate audits,
or spend treasury credit to subsidize transparency). MMW allows this only via explicit, treaty-governed exchange.

Recommended artifacts:
- `ExchangeRate(from=Account, to=Account, rate, by=jurisdiction, expires=epoch)`
- `Exchanged(from, to, amount_from, amount_to)`

Guidance:
- exchanges require standing and SHOULD be limited to a small set of approved pairs
- exchanges SHOULD spend `ExchangeCredit` (or `LegitimacyBudget`) to prevent “free arbitrage”
- exchange rates MUST be witnessed and may be subject to judicial review
- cross-border exchanges require treaty compatibility (meta-treaties may forbid certain conversions)

This makes “budget laundering” explicit and auditable, while still enabling practical tradeoffs.


MMW’s “moral code” is largely determined by which accounts are conserved. This spec recommends standard
accounts that can be adopted or renamed by an implementation:

- `ExploreCredit` — branching/search budget
- `TransitCredit` — border-crossing budget per work item
- `BandwidthCredit` — gossip/propagation rate limit
- `TrustStake` — sybil resistance / voting weight
- `RiskBudget` — safety/operational risk envelope
- `Entropy` — irreversible finality / point-of-no-return spending
- `LatencyBudget` — time/effort cost envelope
- `PrivacyBudget` — information release (often tied to sealing/fossilization)

A system may add new conserved accounts freely. However:
- minting should be restricted to privileged rules or explicit governance processes
- fork/merge must preserve conservation (split or reference)


- `ProofBudget` — budget for producing/verifying proofs (optional)
- `ConfidenceBudget` — budget for statistical confidence claims (optional)
- `ImpactBudget` — bound/price for externalization blast radius (optional)
- `PatienceBudget` — bound/price for unresolved obligations over time (optional)

## 9. Surface Documents (Non-Normative Sketch)

### 9.1 Sketch Grammar (Non-Normative)

This sketch is illustrative only; implementations may diverge.

```ebnf
document      = { block } ;
block         = statute | form | treaty | docket ;

statute       = "STATUTE" name "{" { clause } "}" ;
clause        = requires | matches | guard | effects | doctrine | phase | class | sunset | forget | hold | telemetry  | prove | compost | pardon | declassify | nullify | repeal  | milestone | delegate | underwrite | impact | secede | evidence | standard | entrench | interest | restore | erratum | correct | retract | depends | merge | anon | deadlock | settle | choice | pilot | diff | throttle | sample | contradict | shadow | transition | view | habeas | palimpsest | lint | redteam | canon ;
telemetry     = "TELEMETRY" ":" telemetry_spec ;
telemetry_spec= ("public"|"internal") ("," "interval" "=" epoch_spec)? ;
forget        = "FORGET" ":" forget_spec ;
hold          = "HOLD" ":" hold_spec ;
hold_spec     = ("scope" "=" scope_tag) ("," "until" "=" epoch_spec)? ;
forget_spec   = "ephemeral" | ("scope" "=" scope_tag) | ("after" "=" epoch_spec) ;
sunset        = "SUNSET" ":" epoch_spec ;
requires      = "REQUIRES" ":" { requirement } ;
matches       = "MATCHES"  ":" { pattern } ;
effects       = "EFFECTS"  ":" { effect } ;
doctrine      = "DOCTRINE" ":" { doctrine_item } ;

treaty        = "TREATY" name "{" { projection | tariff | sealing } "}" ;
projection    = "PROJECT" kind "->" view ;
tariff        = "TARIFF" account ":" amount ;
sealing       = "SEAL" kind ":" mode ;

form          = "FORM" name "{" { field } "}" ;

docket        = "DOCKET" name "{" { receipt_ref | witness_ref | refutation_ref } "}" ;
```


MMW can be presented as “bureaucratic documents” without changing the kernel:

- **STATUTES:** rule declarations (with doctrines, budgets, potentials, phases)
- **FORMS:** structured molecules representing work items
- **TREATIES:** border contracts (schemas/projections, tariffs, sealing requirements)
- **DOCKETS:** receipts and witness bundles (audit trails)

This layer is intentionally non-normative in this draft; it exists to preserve the language’s vibe while keeping
the kernel semantics clean.


## 10. Interference & Information Flow (Normative)

Interference (MERGE+NORMALIZE) may create internal states that are **not directly exportable** across borders.
MMW resolves this by making *export* a separate, treaty-governed operation.

### 10.1 Internal vs Exportable Facts

- **Internal facts** may be produced by any legal in-scope transaction, including interference merges.
- **Exportable facts** are those that can cross a cell or node boundary after treaty projection.

A molecule’s exportability is determined by:
- its kind and treaty schema projection (Treaties-as-Types), and
- its **origin lineage** (Origin handles + receipts), which may impose sealing/redaction requirements.

### 10.2 No Taint Laundering via Merge

Interference cannot be used to “launder” restricted information by cancellation. Specifically:
- cancellation may eliminate *ordinary facts*,
- but it must not eliminate the **obligation** to redact/seal information derived from restricted origins.

Implementations may realize this as a derived attribute (informal “taint”) computed from origin lineage.
The attribute need not be a first-class molecule; it may be enforced by treaty checks at `CROSS`/`GOSSIP`/`PUBLISH`.

### 10.3 Publication and Externalization

MMW distinguishes *internal state change* from *externalization*.

An **externalization event** (e.g., publishing outputs, sending messages outside the node, writing to a real file,
or crossing a strict compliance border) must trigger:

- treaty projection/redaction (if applicable),
- optional sealing of sensitive subproofs,
- **fossilization of relevant receipts** (finality), so exported effects cannot be rolled back.

Externalization is therefore the canonical “point of no return,” priced via conserved accounts such as `Entropy` and/or `PrivacyBudget`.


## 11. Regimes (Policy Presets)

### 11.2 Regime Activation (Normative)

### 11.2.1 Emergency Sunset and Renewal (Normative)

High-power regimes MUST have a sunset:
- `RegimeActive("Emergency Powers")` MUST include an expiry epoch (lease).
- Renewal requires fresh quorum authorization and SHOULD spend additional `LegitimacyBudget`.
- If expiry passes without renewal, the system MUST revert to a lower-power regime (typically Due Process).

This prevents “permanent emergencies” from becoming the default state.


### 11.2.2 Crisis Arbitration (Creative Regime Preset)

Federations can enter “constitutional crisis” when:
- circuit splits block cross-border interoperability,
- treaties conflict with statutes across jurisdictions,
- quarantine orders or emergency actions cascade into conflicting obligations.

A **Crisis Arbitration** regime preset may:
- automatically convene an en banc panel or Constitutional Court for specified issues,
- freeze certain externalizations (probationary export only) until a crisis docket is resolved,
- require proof-carrying governance for overrides and amendments (`ProofRequired`),
- spend `LegitimacyBudget` at an accelerated rate to discourage prolonged crisis mode,
- enforce short sunsets with mandatory renewal votes.

Crisis mode is intentionally painful: it is a throttle to force convergence.



### Deadlocks and Convergence Obligations (Creative, Useful)

When circuit splits, merge conflicts, or treaty disputes persist, the federation can stall.
MMW supports explicit deadlock detection that emits obligations to converge.

Recommended artifacts:
- `DeadlockDetected(issue, because=..., at_epoch)`
- `Obligation(ConvergenceDue, issue, due_epoch)`
- `Converged(issue, witness_id)` / `ConvergenceFailed(issue, because=...)`

Guidance:
- deadlocks SHOULD be telemetry-visible (they are system risk)
- failure to converge by due epoch MAY automatically activate Crisis Arbitration (policy-defined)
- convergence work may be funded by deliberation markets and bounties, but must respect due process

This turns “governance stuck” into a first-class state with a timer.


### 11.3 Preset Binding and Deviations (Normative)

A regime SHOULD bind to a doctrine preset (Due Process / Emergency Powers / Martial Law), establishing defaults.
Deviation from the bound preset MUST be explicit:

- deviations require standing (capability) and should spend `LegitimacyBudget`
- deviations should emit a witness explaining the exception
- deviations that affect externalization MUST be recorded in dockets and may force CCF

This ensures policy remains legible: “exceptions are louder than defaults.”


A regime is not merely configuration; it may be activated and deactivated by governance events.

Implementations SHOULD support representing the active regime as a first-class artifact, e.g.:
- `RegimeActive(name)`

Normative constraints:
- Escalation to high-power regimes (e.g., Emergency Powers, Martial Law) MUST require standing, typically minted by QUORUM_COMMIT.
- Regime activation SHOULD emit a witness indicating authorization and scope.
- Regimes MAY change defaults for: cone policy (MDS/CCF), sealing, fork/merge enablement, scheduling determinism, and doctrine defaults.

This makes “policy changes” auditable and reversible within the applicable grace window (unless fossilized by PUBLISH).


MMW supports “legal regimes”: named runtime policies that alter scheduling, permissions, and defaults without changing the kernel.
Regimes can be treated as configuration, deployment mode, or as a first-class molecule (e.g., `Regime("DueProcess")`).


### Livelocks and Procedural Throttling (Creative, Useful)

Deadlock is “stuck.” Livelock is “doing lots of things, making no progress” (motion spam, endless refilings).
MMW supports optional livelock detection and throttling as explicit governance acts.

Recommended artifacts:
- `LivelockDetected(issue_or_case, because=..., at_epoch)`
- `Throttle(scope, rate, until_epoch, because=...)`
- `MotionLimit(case_id, max_per_epoch, because=...)`
- `VexatiousLitigant(scope, until_epoch)` / `VexatiousLifted(scope)`

Guidance:
- throttles MUST be witnessed and docketed (reason summary required)
- emergency regimes may apply temporary throttles but must sunset and be reviewable
- throttling SHOULD interact with PatienceBudget/PaperworkDebt (delay and spam become priced)
- high-stakes matters must still receive minimum service under regimes (no starvation)

This keeps procedure from becoming a denial-of-service vector.


### 11.1 Example Regimes

- **Due Process**
  - forks allowed (budgeted), appeals cheap within grace
  - strict jurisdiction and burden-of-proof doctrines encouraged
  - sealing used selectively; strong audit trails

- **Emergency Powers**
  - broader standing (more actions permitted), but costs `RiskBudget` and `Entropy`
  - receipts default to sealed payloads; aggressive fossilization on externalization

- **Martial Law**
  - deterministic scheduling; forks/merges disabled by default
  - fast commit cycles; minimal deliberation; high accountability

Regimes are intentionally composable: a deployment might run “Due Process” in normal conditions and escalate to
“Emergency Powers” under quorum-issued authorization.


## 12. Externalization Cones (Normative)

Externalization events (publish/send/write outside) force fossilization to prevent “export then rollback” paradoxes.
MMW defines two normative strategies. An implementation MUST choose one (or offer both as selectable policy).

### 12.1 Minimal Dependency Set (MDS)

Fossilize only the receipts required to justify the exported artifact.

- Let `Exported(m)` be a molecule leaving its originating scope.
- Compute the smallest set of receipts whose outputs (via Origin handles) are sufficient to derive `m`.
- Fossilize exactly those receipts (and their sealing obligations).

**Pros:** minimal cost, smaller fossils, better performance.  
**Cons:** subtle: requires accurate dependency tracking; can surprise users expecting “whole history” to fossilize.

### 12.2 Causal Cone Fossilization (CCF)

Fossilize the entire causal cone leading to the exported artifact.

- Fossilize all receipts reachable backward from `Exported(m)` following Origin handles and consumed-molecule links.

**Pros:** conceptually simple; strong audit guarantee (“nothing in the cone can be rolled back”).  
**Cons:** can be heavy; exports may fossilize large histories.

### 12.3 Policy Hook

An implementation may choose MDS for routine exports and switch to CCF under stricter regimes (e.g., Emergency Powers, compliance borders),
or based on treaty clauses.


## 13. PUBLISH / EXTERNALIZE (Privileged Rule)

MMW defines an explicit privileged operation for externalization. All “real world” side effects should be mediated by this rule,
or by equivalent platform-defined externalization hooks that are semantically equivalent.

### 13.X Impact Assessments and Blast Radius (Optional, Esoteric-Useful)

Some externalizations are small (publishing a harmless receipt), others are civilization-shaping.
MMW supports optional *impact accounting* to make “how much can this change the world?” explicit.

Recommended artifacts:
- `ImpactEstimate(target, class, magnitude, because=...)`
- `ImpactGuard(max_class, max_magnitude, by=jurisdiction)` (policy)
- `ImpactApproved(target, by=jurisdiction)` / `ImpactDenied(target, because=...)`

Guidance:
- PUBLISH SHOULD attach an impact estimate (at least header-visible class/magnitude)
- regimes MAY require `Proof(kind="impact-bounded", ...)` for high-impact publishes
- high-impact publishes MAY spend `ImpactBudget` (optional) and/or `LegitimacyBudget`
- impact policies are treaty-sensitive: crossings can refuse imports that exceed local impact caps
- “impact class” can be coarse (benign / significant / existential) or deployment-defined

This is a blast-radius governor for reality changes.


### 13.1 Intent

`PUBLISH` moves an exportable artifact across a boundary (cell/node/outside world), enforcing:
- treaty projection/redaction (Treaties-as-Types),
- sealing of sensitive subproofs when required,
- selection of an externalization cone (MDS or CCF),
- fossilization of receipts within the chosen cone,
- spending of appropriate conserved budgets (Entropy, PrivacyBudget, BandwidthCredit, etc.).

### 13.2 Pre-Conditions (Normative)

A PUBLISH is valid only if:
1) The artifact is **exportable** under the target treaty projection.
2) Required standing is present (e.g., `Cap(PublishPermit, target_scope, nonce)`), often minted by QUORUM_COMMIT.
3) Required tariffs/budgets are available (at minimum `Entropy` or an equivalent finality budget).
4) Jurisdiction requirements are met (evidence admissible in the target jurisdiction).

### 13.7 Compensation After Fossilization (Normative)

After fossilization, rollback is forbidden. Corrections MUST be performed via compensating transactions.

A compensating transaction:
- references the fossilized receipt(s) it compensates,
- emits `Witness("compensation", ...)` linking old and new effects,
- may generate obligations (e.g., `Obligation(CompensationDue, ...)`) for downstream audits,
- preserves evidence (no deletion; refutation/supersession only).

This provides a principled notion of “undo” compatible with externalization.

#### Compensation Normal Form (Recommended)

A compensating transaction SHOULD follow a standard structure to be easy to audit:

- **References:** list the fossilized receipt ids being compensated.
- **Replacement Effect:** describe the intended corrected effect (often as a new molecule that supersedes the old outcome).
- **Linking Witness:** emit `Witness("compensation", [old_receipts..., new_receipt])`.
- **Downstream Obligations:** optionally emit `Obligation(AuditRequired, ...)` or `Obligation(CompensationReviewDue, ...)`.
- **No Erasure:** do not delete or rewrite prior evidence; use supersession/refutation.

This “normal form” makes compensations composable and prevents stealth rollback-by-rewrite.


### 13.8 Risk Classification and Audit Triggers (Normative Guidance)

PUBLISH may be required to emit `Obligation(AuditRequired, docket_id, due_epoch)` based on a risk classification.
Risk is intentionally policy-defined but should be **derivable from header-visible metadata** (honest-by-default).

Recommended inputs:
- treaty sensitivity lattice labels for exported fields (Public/Confidential/Secret/Sealed)
- budgets spent in the causal dependency set (e.g., `RiskBudget`, `PrivacyBudget`, `Entropy`)
- lineage markers (e.g., `OverrideUsed`, sealing dialects, treaty overrides)
- destination sensitivity (treaty-defined)

Treaties and regimes may define thresholds, e.g.:
- if `PrivacyBudget` spent > 0 OR sealing dialect is Opaque → audit required
- if override used anywhere in cone → audit required + shorter due epoch
- under Emergency Powers → audit required by default for all externalizations

#### RiskClass Calculator (Recommended Statute)

To ensure consensus about risk, implementations SHOULD provide a deterministic statute that computes `RiskClass` from:
- treaty sensitivity labels (Public/Confidential/Secret/Sealed) present in projected schemas,
- sealing dialect indicators in receipt headers,
- aggregate budget deltas (PrivacyBudget/RiskBudget/Entropy), and
- lineage markers (OverrideUsed).

The calculator SHOULD emit a witness citing the inputs used, so WHY/WHY NOT queries can explain the classification.

Implementations may represent the derived result as a header-visible tag, e.g.:
- `RiskClass("low"|"med"|"high")`




### 13.9 Memetic Quarantine and Hazard Classes (Creative Pattern)

Some information is “contagious” (e.g., exploit details, coercive content, or sensitive operational procedures).
MMW supports optional hazard tagging to control propagation without pretending the data doesn’t exist.

Recommended header-visible markers:
- `HazardClass("benign"|"risky"|"toxic")`
- `Contagion(tag)`

Recommended consequences (treaty/regime-defined):
- toxic hazards force sealing dialect to commitment-only or opaque
- toxic hazards force CCF fossilization on any externalization
- crossings may emit `Obligation(QuarantineReviewDue, ...)` and quarantine exports until AUDIT_PASS
- selective reveal of toxic hazards may require elevated standing and/or constitutional court review

This turns “dangerous knowledge” into governed flow rather than an all-or-nothing ban.



#### Quarantine Orders and Challenges

Recommended artifacts:
- `QuarantineOrdered(target, hazard, by=jurisdiction)`
- `QuarantineLifted(target, by=jurisdiction)`
- `QuarantineChallenged(target, by=scope, because=...)`

Guidance:
- quarantine orders SHOULD have sunsets and review obligations
- challenges may require bonds (CaseCredit) to prevent spam
- even under quarantine, the system SHOULD preserve a reason summary (Right to Explanation) and header-minimum cost metadata


### 13.3 Post-Conditions (Normative)

A successful PUBLISH must:
- emit a receipt header indicating externalization (header-visible),
- apply treaty projection/redaction to the exported artifact,
- apply sealing where mandated by treaty or regime,
- fossilize receipts per the configured cone policy (MDS/CCF),
- produce an `Exported(...)` or equivalent artifact in the destination scope, and
- ensure that rollback cannot invalidate exported effects (compensation only).

### 13.6 GOSSIP vs PUBLISH (Normative)

MMW distinguishes node-to-node propagation from externalization:

- **GOSSIP** is *internal federation propagation*. It MUST obey treaties between nodes and spend `BandwidthCredit`.
- **PUBLISH** is *externalization* (leaving the governed system or crossing strict borders) and MUST trigger cone fossilization.

However, a deployment MAY classify certain GOSSIP channels as externalization (e.g., untrusted networks). In that case:
- GOSSIP on those channels MUST be implemented as PUBLISH (or be semantically equivalent), including fossilization.

This keeps the model honest: some networks are the outside world.

### 13.5 Probationary Export (Creative Option)

MMW may support a two-stage externalization:

1) **Probationary PUBLISH** exports only a redacted summary or commitment-only artifact.
2) **Finalize Reveal** may later disclose additional fields via selective reveal under Due Process.

Probationary export is useful when decisions must be made quickly but full disclosure is risky.
Treaties may require probationary export by default, with full reveals only after quorum review.

### 13.4 Notes

Treaties may require different cone policies (MDS vs CCF) and sealing defaults depending on molecule kind, origin lineage, or regime.



### 13.Z Proof-Carrying Governance (Optional, Insane-Useful)

Some deployments want **machine-checkable compliance**: “show me the proof you didn’t exceed the budget
and that you followed the treaty/regime rules.”

MMW supports optional proof-carrying artifacts:
- `Proof(kind, proves=[...], verifier=..., digest=...)`
- `ProofRequired(kind, scope, by=jurisdiction)` (policy)
- `ProofAccepted(proof_id)` / `ProofRejected(proof_id, because=...)`

Guidance:
- proofs SHOULD be included in dockets or referenced by witnesses for high-power actions (OVERRIDE, AMEND, high-risk PUBLISH)
- verification MAY spend `ProofBudget` (and can be audited); proofs can be sealed with header-visible digests
- failure to provide required proof can emit `Obligation(ProofDue, ..., due_epoch)` and/or block externalization

This is “proof-carrying code,” but for governance.



### 13.Y Corrections, Errata, and Retractions (Creative, Necessary)

Externalized artifacts are not immutable truth; they are governed claims about the world.
MMW supports explicit correction flow so “oops” is auditable rather than quietly edited.

Recommended artifacts:
- `Erratum(target, fixes=[...], because=..., by=scope)` — narrow, non-substantive fix (typos, formatting, metadata)
- `Correction(target, corrected_by, because=..., by=scope)` — substantive change with a new artifact
- `Retraction(target, because=..., by=jurisdiction)` — withdraw an externalization as unreliable (history remains)
- `Supersedes(old, new)` / `RetractedBy(old, retraction)` — link relations

Guidance:
- corrections MUST NOT delete history; they link to new artifacts
- retractions SHOULD be loud: spend `LegitimacyBudget` and/or require proof-carrying justification for high-impact targets
- telemetry dockets SHOULD include correction/retraction counts (governance honesty signal)
- treaties MAY require “right of reply” attachments for affected parties on significant publishes

This makes “editing reality” explicit instead of sneaky.



### 13.A Statistical Audits and Sampling (Optional, Delightfully Weird)

Full audits are expensive. MMW supports optional **sampling audits** that produce
*statistical* confidence rather than absolute certainty.

Recommended artifacts:
- `SampleAuditPlan(scope, population, method, size, seed_ref, at_epoch)`
- `Sampled(scope, sample_ids=[...], seed_ref)`
- `SampleAuditResult(scope, findings, confidence, because=...)`
- `ConfidenceClaim(scope, statement_digest, level, at_epoch)`
- `AuditEscalated(scope, because=...)` (when samples fail)

Guidance:
- sampling SHOULD be seeded by `RandomBeacon` epochs to prevent cherry-picking
- publishing confidence claims MAY spend `ConfidenceBudget` (optional) to prevent “free certainty laundering”
- treaties MAY restrict which hazard/risk classes permit sampling (e.g., toxic hazards may require full audits)
- failing samples SHOULD auto-escalate: larger samples, full audits, or court review (policy-defined)

This is “probabilistic compliance”: not perfect, but honest and scalable.


## 14. Dockets (Audit Bundles)

A **docket** is a portable bundle of governance artifacts used for audits, appeals, and postmortems.
Dockets are part of the recommended standard library; an implementation MAY treat them as data or as structured views.

### 14.1 Contents

A docket SHOULD include:
- relevant `ReceiptH` headers (always)
- optional sealed payload references (`ReceiptP` + `Seal`)
- one or more `Witness(...)` artifacts
- `Refuted(...)` and/or `Superseded(...)` relations when applicable
- cone metadata for externalizations (MDS/CCF selection and fossil set identifiers)

### 14.2 Minimality

Dockets should prefer minimal evidence sets:
- include only the receipts required to justify the claim(s) under the chosen cone policy
- use Origin handles to compute minimal dependency sets when possible

### 14.5 ESCROW_RELEASE (Privileged Rule)

Implementations SHOULD provide a privileged escrow release operation that:
- verifies escrow conditions (epoch threshold, AUDIT_PASS, or quorum witness),
- requires standing (e.g., `Cap(EscrowReleasePermit, scope_tag, nonce)`),
- emits a receipt header recording the release,
- optionally mints a `RevealPermit` scoped to the authorized reveal scope.

Escrow release MUST NOT reveal payload content by itself; it only authorizes a later selective reveal.

### 14.4 Sealed Docket Escrow (Creative Pattern)

A docket may be placed in escrow:
- payloads are sealed under a specified dialect (often commitment-only),
- the docket becomes eligible for selective reveal only after a condition holds, such as:
  - `N` epochs have passed,
  - `AUDIT_PASS` succeeds,
  - a quorum witness authorizes reveal.

Escrow is intended to support delayed transparency and safe postmortems.


### Dead-Man Escrow (Creative Pattern)

Escrows can be used for accountability: “if nobody acts, the truth auto-surfaces.”

Recommended artifacts:
- `Deadman(escrow_id, trigger_epoch, action="release"|"quarantine"|"audit")`
- `DeadmanRenewed(escrow_id, new_trigger_epoch)`
- `DeadmanFired(escrow_id, at_epoch)`

Guidance:
- deadman triggers SHOULD be treaty-defined for certain dockets (e.g., whistleblower protected sources)
- renewal SHOULD be explicit, witnessed, and may spend legitimacy (prevent indefinite suppression)
- firing a deadman trigger may automatically emit obligations (postmortem, audit, compensation review)

Dead-man escrow is the “if I disappear, publish this” feature, but governed.


### Whistleblower Dockets (Creative Pattern)

Systems need a way to surface misconduct without requiring public exposure.
A **whistleblower docket** is a sealed (often escrowed) docket submission that can trigger governance review.

Recommended artifacts:
- `Whistleblower(case_hint, docket_id, by=scope_or_anon)`
- `ProtectedSource(docket_id)` (non-normative marker)
- `RetaliationClaim(actor, because=...)`

Guidance:
- whistleblower dockets SHOULD default to commitment-only or opaque payloads with header-visible existence
- the docket SHOULD be placed in escrow by default; `ESCROW_RELEASE` authorizes limited reveals
- receipt headers MUST expose enough to route the case (jurisdiction, risk class, alleged violation class)
- courts may issue **protective orders** (standing-required) restricting who can request reveals
- false or malicious whistleblowing may be handled via slashing only under strict due process (avoid chilling effect)

This gives “anonymous reporting” a first-class, auditable path consistent with sealing and accountability.



### 14.Y Red Team Dockets and Adversarial Drills (Optional, Chaotic-Good)

Systems fail at the edges. MMW supports optional **red team drills**: governed adversarial exercises
that try to break treaties, regimes, and enforcement assumptions before attackers do.

Recommended artifacts:
- `RedTeamExercise(name, target=[treaty|statute|regime], scope, seed_ref, start_epoch, end_epoch)`
- `ExploitReport(name, finding_digest, severity, because=...)`
- `PatchProposed(name, patch_ref)` / `PatchAccepted(name, witness_id)`
- `BountyAwarded(name, to=scope, amount)` (ties to `BOUNTY` / TreasuryCredit)
- `ExerciseConcluded(name, summary_digest)`

Guardrails:
- drills MUST respect sealing: findings may be sealed, but existence + severity SHOULD be header-visible
- drills SHOULD have safe harbors: participants aren’t punished for good-faith reporting (treaty-defined)
- repeated reckless drilling can be throttled (livelock), and malicious drills are fraud/crime under regimes
- high-severity findings may automatically trigger holds, probationary exports, or crisis arbitration (policy-defined)

This is “bug bounties for governance.”


### 14.3 Portability Across Jurisdictions

When moved across cells/nodes:
- docket headers remain visible
- sensitive payloads remain sealed unless admitted by treaty and standing
- jurisdiction rules determine admissibility of cited evidence

Dockets are the canonical “paper trail” of MMW.


### 14.X Notary Nodes and Fossil Shards (Optional Scalability)

Large systems cannot ship entire causal cones everywhere. MMW recommends an optional notarization layer:

- **Notary nodes** are specialized auditors that can attest to a fossil set (MDS or CCF) without revealing payloads.
- A notarized fossil set can be represented as **Fossil Shards**:
  - compact commitments to groups of receipts (Merkle roots or equivalent),
  - plus a minimal index enabling later selective reveal of specific receipt payloads under standing.

Dockets may carry fossil shard commitments instead of full receipt payloads, improving portability while preserving verifiability.



### 14.Y Governance Telemetry Dockets (Optional)

Large federations need periodic “health reports” that are auditable but not necessarily fully public.

A **telemetry docket** is a docket produced per epoch (or per interval) that summarizes:
- aggregate budget deltas (privacy/risk/legitimacy/paperwork/etc.),
- outstanding obligations by class and jurisdiction,
- audit backlog and quarantine status,
- notable governance events (AMENDs, overrides, major rulings).

Guidance:
- telemetry SHOULD be signed/attested by notary nodes (or quorum witnesses) and may be challenged
- telemetry payload MAY be sealed; headers MUST remain honest-by-default (dialects, cone policy, aggregates/digests)
- publishing telemetry MAY spend `TelemetryBudget` to avoid “free surveillance”; treaties define what can be exported
- a public dashboard can be built by publishing redacted telemetry summaries.

Telemetry dockets make governance measurable without forcing full disclosure.



### 14.Z Composting and Compaction (Optional, Very Esoteric)

Long-lived systems accumulate receipts faster than humans can reason about them.
MMW supports optional **compaction** that preserves accountability while reducing bulk.

- `COMPOST` converts an admissible set of receipts into a smaller representation:
  - fossil shards (commitments) plus a **reason summary** and index hints.
- compaction MUST NOT change externalized truths; it changes representation, not meaning.
- compaction SHOULD produce:
  - `Composted(old_receipts=[...], new_shard=..., by=notary_or_quorum)`
  - a `Proof(kind="compaction-preserves-commitments", ...)` when proof-carrying governance is enabled.

Governance hooks:
- compaction MAY reclaim `StorageBudget` (optional) but SHOULD spend `ComplexityBudget` or `ProofBudget` (optional)
- legal holds can forbid compaction for certain scopes
- compaction artifacts are challengeable (fraud rules apply)

This is “garbage collection for governance”: you can compress history without rewriting it.




### Evidence Chain and Chain-of-Custody (Creative, Very Useful)

When disputes matter, “where did this evidence come from?” becomes the dispute.
MMW supports optional **chain-of-custody** artifacts so evidence integrity is governed, not assumed.

Recommended artifacts:
- `Evidence(item_id, kind, digest, collected_at_epoch, source=...)`
- `CustodyTransfer(item_id, from, to, at_epoch)`
- `EvidenceSealed(item_id, escrow_id)` (optional)
- `TamperClaim(item_id, because=...)` / `TamperRefuted(item_id, because=...)`

Guidance:
- evidence SHOULD have a header-visible digest (even if payload is sealed)
- custody transfers SHOULD be witnessed (notary or quorum) for high-stakes cases
- courts MAY discount or exclude evidence with broken custody chains (treaty-defined evidentiary standards)
- escrow + dead-man triggers are recommended for protected-source evidence

This makes evidence integrity an auditable program rather than vibes.


## 15. Supersession Lattice (Rulings and Evidence Evolution)

MMW treats rulings, witnesses, and refutations as evolving artifacts rather than mutable facts.
To avoid “spaghetti appeals,” this spec recommends a simple lattice of status relations.

### 15.1 Status Relations

- `Witness(claim, receipts)` — asserts claim with supporting evidence.
- `Superseded(old, new)` — indicates the old witness/ruling is replaced by the new one (same jurisdiction or higher).
- `Refuted(target, because)` — indicates the target evidence/ruling is invalid under stated reasoning.

### 15.2 Monotonicity

Within a jurisdiction:
- A witness may be **superseded** by a later witness.
- A witness or receipt may be **refuted** only by an admissible appeal (standing + jurisdiction).
- Supersession chains SHOULD be acyclic; implementations may treat cycles as `Stuck("CycleInRulings", ...)`.

Across jurisdictions:
- Higher-jurisdiction rulings may supersede lower-jurisdiction rulings when admissibility is satisfied.
- Conflicts are resolved by appeal + choose, never by silent overwrite.

### 15.3 Query Semantics

Queries (`WHY`, `WHY NOT`) should interpret the “current” ruling as:
- the latest non-refuted witness reachable via supersession chains, subject to jurisdiction admissibility.




### Stare Decisis and Precedent (Creative Pattern)

Courts can mark certain rulings as **precedent** to stabilize behavior over time.

Recommended artifacts:
- `Precedent(witness_id, level="local"|"federal"|"constitutional")`
- `Cites(new_witness, precedent_witness)`
- `Overruled(old_precedent, new_witness, because=...)`

Guidance:
- Precedent does not make rulings immutable; it makes **breaking them expensive and loud**.
- Overruling SHOULD require higher standing and spend `LegitimacyBudget` and/or mint `PrecedentDebt` (optional).
- Queries should surface whether a current ruling is precedent-backed, and whether an exception was taken.

This gives MMW “case law gravity” without mutability.


### Circuit Splits and En Banc (Creative Pattern)

In federations, different courts may form incompatible precedents (“circuit splits”). MMW makes this explicit.

Recommended artifacts:
- `CircuitSplit(issue, courts=[...], precedents=[...])`
- `EnBancRequested(issue, by=scope)`
- `EnBancConvened(issue, jurors=[...])`
- `EnBancRuling(issue, witness_id)`

Guidance:
- splits SHOULD be discoverable via queries and telemetry (they are governance debt)
- convening en banc may require higher `CaseCredit` and spend `LegitimacyBudget`
- en banc rulings can overrule lower precedents (expensive/loud) and may emit migration obligations

This makes “the law differs by circuit” a first-class reality rather than a hidden divergence.

## 16. Claims as Derived Truth (Idiom)

MMW encourages representing “facts” as **claims** whose current status is derived from governance artifacts,
rather than mutable booleans.

A typical pattern:
- `Claim(X)` is asserted as a molecule.
- Evidence is provided via `Witness("supports Claim(X)", ...)`.
- Disputes are represented by competing witnesses and refutations.
- The “current truth” of `Claim(X)` is computed by query semantics:
  - find latest admissible non-refuted witness in the supersession lattice for the relevant jurisdiction.

This supports paraconsistency: `Claim(X)` and `Deny(X)` may coexist internally, while actions require standing and an admissible ruling.


## 17. Doctrine Presets (Compilation into Constraints)

Doctrines can be used ad-hoc, but MMW also supports *preset doctrines* that compile into concrete constraints.
These presets help create recognizable “legal styles” without changing the kernel.

### 16.1 Due Process (Preset)

Compiles to defaults such as:
- require explicit jurisdiction citations for non-local actions
- require burden-of-proof witnesses for risky operations
- allow appeals within grace; default to MDS externalization cone
- sealing is selective and treaty-driven

### 16.2 Emergency Powers (Preset)

Compiles to:
- broaden standing (more actions permitted) **only if** authorized by QUORUM_COMMIT
- default to sealed receipt payloads for sensitive actions
- default to CCF externalization cone on publish
- spend `RiskBudget` and `Entropy` for extraordinary actions (see Account Palette)

### 16.3 Martial Law (Preset)

Compiles to:
- deterministic scheduling; fork/merge disabled unless explicitly permitted by standing
- fast commit cycles; aggressive fossilization on externalization
- reduced tolerance for appeals (narrow grace windows)

Presets are intended to be implemented as regime-driven defaults and validation checks.


## 18. Legitimacy and Abuse Costs (Creative Constraint)

To discourage “policy abuse” (e.g., permanent Emergency Powers), MMW introduces an optional conserved dimension:

- `LegitimacyBudget` (or `LegitimacyCredit`)

Rules that expand standing, override treaties, or accelerate finality may be required to spend legitimacy.
Legitimacy may be replenished only through governance processes (e.g., time, successful audits, quorum renewals).

This is a deliberately “political” primitive: it makes governance tradeoffs explicit and auditable.


## 19. Treaty Override (Extraordinary Mechanism)

Treaties are the type system; overriding them is equivalent to overriding types and information flow rules.
MMW permits treaty overrides only as an **extraordinary act** with explicit costs and audit guarantees.

### 18.1 Preconditions (Normative)

A treaty override is valid only if:
1) Standing is present: `Cap(OverridePermit, target_scope, nonce)`
2) Authorization is evidenced by a quorum witness (or equivalent governance rule)
3) A `RegimeActive` compatible with overrides is in force (typically Emergency Powers)
4) The action spends from `LegitimacyBudget` and `Entropy` (and often `RiskBudget`/`PrivacyBudget`)
5) A docket is created containing: authorization witness, minimal justification receipts, and projected export plan

### 18.2 Postconditions (Normative)

On override:
- all receipts in the externalization cone MUST be fossilized under **CCF** (causal cone fossilization)
- exported artifacts MUST be sealed by default unless explicitly waived by treaty clauses and standing
- a header-visible marker MUST be emitted (e.g., `OverrideUsed(...)`) to prevent “secret emergency actions”

### 18.3 Rationale

Overrides exist to model real systems (break-glass procedures), but they must be:
- expensive,
- obvious,
- accountable,
- and hard to normalize.


## 20. Amnesty and Restoration (Creative Governance)

### 19.3 AUDIT_PASS (Privileged Governance Primitive)

An implementation SHOULD support a privileged audit primitive that:
- consumes a docket of evidence,
- performs policy-defined verification steps (internal or external),
- emits a witness summarizing outcome, and
- may replenish `LegitimacyBudget` under strict rules.

Normative expectations:
- `Witness("audit passed", ...)` MUST cite the audited docket identifiers and relevant receipt headers.
- `Witness("audit failed", ...)` SHOULD cite the minimal failing evidence and trigger remedies/refutations.
- Legitimacy restoration MUST be capped and never automatic; it must be traceable to explicit audit outcomes.


MMW introduces a complementary mechanism to Legitimacy costs: **restoration**.

### 19.1 Amnesty

An amnesty is a controlled forgiveness of certain classes of violations (e.g., minor treaty deviations) that may:
- prevent endless appeals,
- permit forward progress after emergencies,
- consolidate a stable new baseline.

Amnesty MUST be authorized by quorum and MUST emit a witness describing scope and duration.

### 19.2 Restoration of Legitimacy

`LegitimacyBudget` may be replenished only through governance processes such as:
- successful audits producing `Witness("audit passed", ...)`
- time-based renewal rules (e.g., epochs without overrides)
- explicit quorum renewal votes

Restoration is intentionally slow and legible. The system should never “heal” legitimacy invisibly.


### 19.4 AMEND (Privileged Governance Primitive)

Implementations SHOULD support a privileged amendment primitive to change the system’s “constitution”:
treaties, statute bundles (including enforcers), regime presets, and court jurisdictions.

AMEND MUST:
- require quorum authorization (standing + witness),
- spend `LegitimacyBudget` (and often `Entropy`) proportional to scope,
- emit an **Amendment Docket** containing: old version refs, new version refs, rationale (possibly sealed), and migration obligations,
- avoid silent retroactivity: changes take effect at a declared epoch boundary unless explicitly emergency-authorized.

AMEND is the “law changes” operation. It is intentionally expensive and loud.


### Constitutional Layers and Meta-Treaties (Creative, Stabilizing)

As the system grows, not every rule should be equally easy to change. MMW recommends a layered constitution:

- **Layer 0 (Kernel):** receipts, conservation, fork/merge/choose, treaties-as-types (minimal, stable).
- **Layer 1 (Constitution):** amendment rules (AMEND), court jurisdictions, regime activation rules.
- **Layer 2 (Statutes):** ordinary policy rules, enforcers, court procedures.
- **Layer 3 (Customs):** local conventions, surface document styles, non-normative molecules.

**Meta-treaties** are treaties about treaties. They impose constraints like:
- all treaties MUST declare sensitivity lattice labels for exported fields,
- all treaties MUST specify default cone policy (MDS/CCF) for externalization,
- all treaties MUST specify sealing dialect mappings for each sensitivity class.

Meta-treaties reduce ambiguity and make federation interoperable: “everyone uses compatible stamps.”


### BOUNTY (Governance Primitive, Optional)

Implementations MAY support a bounty mechanism to incentivize audits, bug-finding, and governance work.

- `BOUNTY(kind, scope, amount)` earmarks `TreasuryCredit` (or another account) to reward a verified contribution.
- claiming a bounty requires evidence: a docket + witness (often `AUDIT_PASS` or a court ruling).
- bounties MUST be witnessed and docketed to prevent quiet payoffs.
- regimes may restrict bounties during emergencies to avoid perverse incentives.

This creates a public-goods loop: the system can pay for its own oversight.


#### Ratification Windows (Recommended)

AMEND can be safer when changes are staged:

- an amendment may be **proposed** and evaluated via Dream Court (counterfactual dockets)
- once approved, it enters a **ratification window** (probationary epoch range) where:
  - crossings/publishes may be forced into probationary export,
  - migration obligations are emitted and tracked,
  - judicial review stays can pause adoption if severe conflicts appear

At the end of ratification, the amendment becomes active by default unless explicitly stayed or revoked.



### Bootstrapping and Self-Hosting (Conceptual, Optional)

MMW can be *self-describing* even before any implementation exists.

Proposed model:
- A **Reference Kernel** is a statute+treaty bundle that defines how to parse and interpret the surface documents.
- The reference kernel can be externalized as a docket and governed like any other artifact (AMEND, judicial review, ratification windows).
- A deployment may “self-host” by using the reference kernel to interpret newer versions of itself, producing compatibility dockets and proof artifacts.

This does NOT require immediate implementation; it’s an architectural direction that makes “the language changes itself” a governed process.


### 19.Y REPEAL (Privileged Governance Primitive, Optional)

AMEND changes law forward; sometimes the system needs to explicitly *undo* a prior amendment.
`REPEAL` is a loud rollback mechanism that preserves history but changes what is in force.

- `REPEAL(target_amendment_ref, because=..., by=jurisdiction)`
- repeal MUST be witnessed and docketed (reason may be sealed; reason summary required)
- repeal SHOULD use ratification windows and emit migration obligations (rollbacks are still migrations)

Guidance:
- REPEAL typically requires equal-or-higher standing than the original AMEND (often bicameral quorum)
- repeals MAY incur `PrecedentDebt` or spend `LegitimacyBudget` more heavily than forward amendments
- emergency repeals should sunset quickly and trigger mandatory postmortem review

REPEAL is “we changed our mind,” but with receipts.



### 19.W Entrenchment and Unamendable Clauses (Optional, Dangerous)

Some systems want “constitutional” rules that are harder (or impossible) to change.

Recommended artifacts:
- `Entrenched(target, threshold, by=jurisdiction, until_epoch=None)`
- `Unamendable(target, by=jurisdiction)`
- `EntrenchmentChallenged(target, because=...)` / `EntrenchmentUpheld(...)`

Guidance:
- entrenchment SHOULD require bicameral quorum + constitutional court review (and often higher proof requirements)
- unamendable clauses SHOULD be extremely rare and treaty-visible across borders
- entrenchment SHOULD sunset unless explicitly renewed (avoid permanent capture)
- repeal/override actions against entrenched targets are allowed only under declared thresholds (loud, expensive)

This makes “constitutional rigidity” explicit and auditable rather than informal.



### 19.V Forks, Merges, and Governance Conflicts (Optional, Wild)

Parallel amendments can create merge conflicts: two legal branches both “won” but cannot coexist.
MMW supports an explicit fork/merge model to keep this from becoming silent chaos.

Recommended artifacts:
- `Fork(base_version, branch_a, branch_b, because=...)`
- `ConflictSet(artifacts=[...], because=...)`
- `MergeProposal(conflict_set, strategy, by=scope)`
- `MergeRuling(conflict_set, result_version, witness_id)`
- `MergeFailed(conflict_set, because=...)`

Guidance:
- conflict sets SHOULD be surfaced in telemetry (they are governance debt)
- merging SHOULD use ratification windows and may require bicameral quorum
- crisis arbitration regime may auto-trigger when unresolved conflicts block borders
- merging MAY spend `ComplexityBudget` and `LegitimacyBudget` (this is expensive work)
- proofs (optional) can attest that merges preserve certain invariants (deps satisfied, budgets bounded)

This is “git for law,” but adjudicated.



### 19.U Pilot Programs and Experimental Law (Optional, Wildly Practical)

Deployments may want “try it in a small area first” governance.
MMW supports optional pilot programs that run statutes/treaties on a constrained cohort.

Recommended artifacts:
- `Pilot(name, scope, cohort, start_epoch, end_epoch, metrics=[...])`
- `PilotGuard(max_impact_class, because=...)` (policy; pairs with ImpactBudget)
- `PilotReport(name, at_epoch, findings_digest)`
- `PilotExtended(name, new_end_epoch)` / `PilotTerminated(name, because=...)`
- `RolledOut(name, into_scope, at_epoch)`

Guidance:
- pilots SHOULD be impact-bounded (ImpactBudget) and telemetry-visible (TelemetryBudget)
- pilots MUST sunset unless explicitly extended
- crossing rules: borders may refuse imports from experimental regimes unless treaty allows probationary export
- rollouts SHOULD include migration guides and (optional) compatibility proofs

This makes “A/B testing law” explicit and accountable.



### 19.T Semantic Diffs and Migration Guides (Creative, Extremely Useful)

High-impact governance changes should ship with “what changed” and “how to migrate.”
MMW supports optional semantic diffs and migration guides as first-class artifacts.

Recommended artifacts:
- `Diff(old, new, summary, because=...)` — human-readable and machine-checkable hints
- `MigrationGuide(old, new, steps=[...], tests=[...])`
- `MigrationSatisfied(target, witness_id)` / `MigrationFailed(target, because=...)`

Guidance:
- AMEND/REPEAL/MERGE SHOULD attach a diff + guide for cross-border or high-impact changes
- treaty test/fuzz dockets SHOULD be referenced from migration guides
- proof-carrying governance MAY require `Proof(kind="migration-preserves-invariants", ...)`
- guides can be composted later, but their digests SHOULD remain in fossil shards for traceability

This is release notes + upgrade docs, but enforced by governance.


## 21. Postmortem Ritual (Creative Governance, Normative Under Emergency)

Emergency actions are legible only if they produce durable accountability artifacts.
MMW therefore defines a postmortem ritual that is REQUIRED after extraordinary mechanisms such as Treaty Override.



### 19.R Grandfathering and Transitional Rules (Creative, Necessary)

Migrations can be socially impossible if everything must switch instantly.
MMW supports explicit **transitional law**: temporary compatibility bridges with clear sunsets.

Recommended artifacts:
- `TransitionalRule(old, new, applies_to=scope, start_epoch, end_epoch, because=...)`
- `Grandfathered(scope, rule_version, until_epoch)`
- `TransitionExpired(scope, rule_version, at_epoch)`
- `TransitionViolation(scope, because=...)`

Guidance:
- transitional rules MUST sunset (end_epoch required) and should be expensive in Complexity/Legitimacy budgets
- transitional rules SHOULD be accompanied by migration guides and treaty tests/fuzz dockets
- borders MAY refuse imports relying on expired transitional rules (forced modernization)
- timebars apply: if you miss the window, you miss the window (unless tolled)

This is “compat mode,” but governed and time-bounded.



### 19.Q Statute Linting and Hygiene (Optional, Surprisingly Important)

Governance languages rot when changes are unreadable or unreviewable.
MMW supports optional **linting**: static analysis for statutes/treaties and their surface documents.

Recommended artifacts:
- `LintPolicy(required_for=[AMEND|REPEAL|MERGE|PUBLISH], severity_threshold, by=jurisdiction)`
- `LintReport(target, findings=[...], severity_counts, at_epoch)`
- `LintWaived(target, because=..., by=jurisdiction)` (witnessed; reason summary required)

Lints can check:
- complexity/branching estimates (ComplexityBudget hygiene)
- missing sunsets/holds without review hooks
- dependency graph consistency (DependsOn/CompatProof)
- contradictory clauses (Contradiction Ledger hints)
- missing diffs/migration guides for high-impact changes

Guidance:
- for high-impact changes, lint SHOULD be required and waivers SHOULD be expensive in LegitimacyBudget
- treaties MAY define shared lint schemas across borders
- lint outputs SHOULD be compostable, but digests should remain for audit trails

This is “CI for statutes”: keep the system legible.


### 19.S Shadow Execution and Replay Dockets (Optional, Very Powerful)

Before rolling out a rule, you may want to *simulate* its effects on past receipts.
MMW supports optional shadow execution: “run the new statute on old history” in a controlled sandbox.

Recommended artifacts:
- `ShadowRun(name, old_rules, proposed_rules, input_receipts_ref, at_epoch)`
- `ShadowResult(name, deltas, hazards, impact_estimate, because=...)`
- `ReplayVerified(name, witness_id)` (attest determinism / reproducibility)
- `ShadowDisputed(name, because=...)`

Guidance:
- shadow runs SHOULD be seeded and reproducible (RandomBeacon + recorded parameters)
- shadow results SHOULD feed `ImpactEstimate` and pilot guards
- treaties MAY require shadow runs for high-impact AMEND/REPEAL/MERGE proposals
- shadow execution MUST NOT substitute for due process; it is evidence, not final judgment

This is “continuous integration for governance.”


### 20.1 Requirement

If `OverrideUsed(...)` (or equivalent) occurs, then within `N` epochs (policy-defined):
- an audit docket MUST be filed, and
- a quorum witness MUST certify review outcome (pass/fail), and
- restoration/penalty rules MUST apply accordingly.

Failure to file the postmortem triggers continuing penalties:
- automatic spending (bleeding) from `LegitimacyBudget` per epoch, and/or
- forced escalation to stricter regimes, and/or
- automatic quarantine of affected exports.

### 20.2 Outcomes

- `Witness("postmortem passed", ...)` may permit legitimacy restoration.
- `Witness("postmortem failed", ...)` should trigger refutations, compensations, and stricter controls.

This creates a governance loop: **break-glass implies paperwork**.


## 22. Sealing Dialects (Normative Options)

Sealing is not binary. MMW supports multiple sealing dialects to balance privacy and accountability.
Treaties and regimes may require specific dialects per molecule kind or lineage.

Recommended dialects:

### 21.1 Selective Reveal (Normative Sketch)

Selective reveal allows sealed payload fields to be disclosed later under standing and jurisdiction rules.
A reveal MUST:
- cite the original sealed receipt header(s),
- provide standing (e.g., `Cap(RevealPermit, scope_tag, nonce)`),
- satisfy treaty and jurisdiction admissibility, and
- emit a new receipt header indicating a reveal event.

Reveals SHOULD default to disclosing the minimal field subset required by the requesting treaty/query.

### 21.2 Reveal Scopes (Normative)

Every reveal occurs *to a scope*.
A reveal MUST declare its target scope tag (cell/node/epoch constraints), and the runtime MUST enforce:
- the revealed fields are visible only within that scope unless subsequently re-published under treaty,
- propagation of revealed fields across cells/nodes requires explicit PUBLISH (or GOSSIP) with treaty checks,
- reveals do not retroactively change previously published artifacts.

This makes revealing a governed act, not an ambient leak.


- **Opaque:** payload fully hidden; only header metadata visible.
- **Redacted Summary:** payload replaced with a sanctioned projection or summary (treaty-defined).
- **Commitment Only:** payload replaced by a commitment hash; optionally revealable later via standing.
- **Selective Reveal:** payload fields tagged as revealable under specific standing/jurisdiction.

Sealing dialect choice MUST be recorded in receipt headers (so auditors can see that sealing happened),
even when payload content is opaque.



### 21.3 Quorum Reveal (Creative, Useful)

Some reveals are too sensitive to authorize by a single party, even with standing.
MMW therefore supports **quorum reveal** as an optional mode:

- a reveal request produces `RevealPetition(case_id, target_receipt, fields, scope)`
- `k-of-n` jurors/notaries (selected via duty roster) must witness approval:
  - `Witness("reveal approved", petition_id, ...)`
- the runtime mints a scoped `RevealPermit` only after threshold approval
- approvals may be sealed, but the petition and approval count SHOULD be header-visible

Quorum reveal is recommended for:
- toxic hazard classes,
- constitutional court reasoning,
- whistleblower protected-source materials.

This turns “unsealing” into a civic act.


### Transparency Budget (Optional Governance)

Systems often want a cap or target on secrecy.
`TransparencyBudget` can be modeled as a conserved account that is **spent by sealing** and **replenished by revealing** (or by time/audit).

Examples:
- Under Due Process, sealing beyond a threshold requires a court witness.
- Under Emergency Powers, sealing is cheap initially but burns transparency faster and triggers postmortem obligations.

This creates a tunable privacy/transparency dial with explicit accounting.



### 21.4 Anonymity Sets and Group Witnessing (Optional, Spicy)

Some actors must act (approve, testify) without revealing which individual did so.
MMW supports optional anonymity-set semantics for witnesses.

Recommended artifacts:
- `AnonymitySet(id, members=[...], by=jurisdiction)`
- `GroupWitness(set_id, statement_digest, threshold=k, proves=...)`
- `MemberChallenged(set_id, because=...)` / `MemberRemoved(set_id, ...)`

Guidance:
- group witnesses can satisfy witness requirements without revealing which member signed
- membership management MUST be governed (adds/removals witnessed; treaties can restrict admissible sets)
- misuse can still be punished: if a group witness is fraud-refuted, the set may be sanctioned, and members may face disclosure under quorum reveal (policy-defined)
- recommended for protected-source workflows, toxic hazard handling, and whistleblower-source shielding

This is anonymity with accountability hooks.


### Declassification and Time-Locked Sealing (Creative, Useful)

Many systems want secrecy to *expire* unless renewed. MMW supports optional **declassification policies**
that gradually relax sealing over time.

Recommended artifacts:
- `DeclassifyPolicy(scope, schedule=[(from,to,after_epochs), ...], by=jurisdiction)`
- `DeclassifyPetition(target, by=scope)` / `DeclassifyDenied(...)`
- `Declassified(target, new_label, at_epoch)`

Guidance:
- policies SHOULD be treaty-defined across borders (meta-treaties may require a declassification schedule for certain labels)
- declassification events SHOULD be docketed and may require quorum reveal for toxic hazards
- renewal of secrecy is explicit: `Hold(...)` / `RetentionPolicy(...)` can delay declassification but should have sunsets and legitimacy cost
- `TransparencyBudget` may be replenished by declassification (optional), making “sunset secrecy” part of the transparency dial

This makes “secrets become history” a governed default rather than an ad-hoc leak.



### 21.5 View Permits and Access Logs (Optional, Security-Useful)

Sealing is not enough; you often need to know *who looked*.
MMW supports optional access control and audit logs for viewing sealed payloads.

Recommended artifacts:
- `ViewPermit(target, by=jurisdiction, scope, until_epoch, limits=[...])`
- `ViewLogged(target, viewer_scope, at_epoch, permit_ref)`
- `ViewDenied(target, viewer_scope, because=...)`
- `ViewAbuseClaim(target, viewer_scope, because=...)`

Guidance:
- view logs SHOULD be header-visible as events (details may be sealed)
- treaties MAY require view logging for protected sources and toxic hazards
- viewing MAY spend `PrivacyBudget` or `PaperworkDebt` (optional) to prevent “free peeking”
- misuse can be adjudicated; view permits can be revoked and sanctions applied

This makes “access” itself part of the accountable program.


## 23. Public vs Private Ledger Split (Normative)

To preserve accountability under sealing, MMW requires a split between **public header-visible metadata** and **private payload**.

### 22.1 Public Header-Minimum

Receipt headers MUST expose at minimum:
- rule name (or an allowed alias)
- scope/jurisdiction identifiers
- time/epoch
- externalization markers (publish/override/amnesty)
- budget/account deltas in aggregate form (delta digests or summaries)
- sealing dialect indicator

### Epoch Commitments (Optional)

To reduce time ambiguity in federated systems:
- nodes may include an epoch commitment (e.g., signed epoch hash) in receipt headers,
- notaries may attest to epoch ordering for fossil sets,
- disputes about timing become justiciable via dockets and witnesses.

This keeps “when did this happen?” within the governance model.

### 22.2 Private Payload

Receipt payloads MAY include:
- sensitive data values
- detailed bindings and consumed-molecule identifiers
- full proofs and intermediate artifacts

Payloads may be sealed; headers must remain audit-usable.

This ensures “sealed governance” remains verifiable: **privacy without invisibility**.


### Verdict Sealing (Recommended)

Courts often need public accountability without exposing sensitive evidence.

Recommended convention:
- **Verdict headers are public:** outcome, jurisdiction, standing basis, budgets spent (aggregate), cone policy, and sealing dialects.
- **Verdict reasoning may be sealed:** detailed rationale and cited payloads may be Opaque/Commitment-only.
- **Selective reveal applies:** authorized parties may reveal specific reasoning fields to specific scopes via RevealPermits.

This fits the “privacy without invisibility” invariant: the world can see that a ruling happened and what it cost,
while details remain governed.



### Right to Explanation (Creative, Normative-ish)

Even when reasoning payloads are sealed, parties should be able to obtain *some* explanation.

Recommended rule:
- every ruling MUST have a treaty-projected **Reason Summary** that is exportable at least as a redacted summary.
- the reason summary MUST cite header-visible evidence and enumerate which sealed dockets were relied upon.
- a party with standing may request selective reveal of additional reasoning fields.

This prevents “black-box courts” while still allowing sensitive evidence to remain sealed.




### Dissent, Concurrence, and Minority Reports (Creative Pattern)

Multi-judge courts often produce disagreement that is still valuable.
MMW supports explicit dissent artifacts without mutating the final ruling.

Recommended artifacts:
- `Concurs(juror_id, ruling_witness)`
- `Dissent(juror_id, ruling_witness, because=...)`
- `MinorityReport(case_id, docket_id)`

Guidance:
- the ruling witness remains the binding outcome (subject to supersession)
- concurrences/dissents SHOULD be docketed and may be sealed (with reason summaries)
- dissents can become future precedent candidates or support overruling via AMEND/Judicial Review

This preserves disagreement as a first-class governance output rather than discarded commentary.

## 24. Jurisdictional Standing (Normative)

MMW makes “who may act” and “where evidence counts” explicit. Capabilities and receipts are not universally valid;
their authority is scoped.

### 13.1 Standing Tokens

A rule may require standing as:

- `Cap(Standing, scope_tag, nonce)`

Standing can be minted only by privileged processes (e.g., QUORUM_COMMIT, treaty-granted delegation, or explicit governance rules).

### 13.2 Jurisdiction of Evidence

Receipts are admissible evidence only within their jurisdiction:
- cell jurisdiction: valid only inside specified compartments
- node jurisdiction: valid only on specified nodes
- epoch jurisdiction: valid only within an epoch window (or only after finality)

Implementations may encode jurisdiction as fields in `ReceiptH` (header-visible) and enforce it during rule matching,
queries, and appeals.

### 13.3 Appeals and Transfer of Jurisdiction

An **appeal** is the canonical way to move a claim across jurisdictions:
- fork rehearing in the target jurisdiction
- cite admissible receipt headers from the origin jurisdiction
- produce a new witness that is valid in the target jurisdiction
- optionally refute or supersede prior rulings

This makes cross-border governance feel “legal” rather than ad-hoc.


### 24.X Delegated Standing and Representation (Creative, Useful)

People and services often act through representatives (lawyers, agents, bots).
MMW supports explicit delegation of standing as a governed artifact.

Recommended artifacts:
- `DelegatedStanding(from, to, scope, until_epoch, limits=[...])`
- `RevokedDelegation(from, to, scope, at_epoch)`
- `ProxyFiled(case_id, by=to, on_behalf_of=from)`

Guidance:
- delegations SHOULD be scoped, time-bounded (sunset-by-default), and revocable
- treaties MAY restrict cross-border delegation (which delegates are admissible, what scopes are delegable)
- delegated standing SHOULD inherit conflict-of-interest rules (recusal/cooling-off)
- abuse (spam filings, malicious reveals) MAY be handled via bonds and slashing under due process

This makes “acting by agent” first-class and auditable.


## 25. Canonical Invariants (Normative)

1) **No double-spend:** Fork/merge cannot duplicate conserved resources/capabilities.
2) **No silent deletion of evidence:** receipts do not cancel; they may only be refuted.
3) **Exports fossilize costs:** cross-border/cross-node externalizations fossilize relevant receipts.
4) **Monotone time/epochs:** Now/Epoch increase; rollback does not reverse them.
5) **Border crossings are explicit:** cell-to-cell movement occurs only via CROSS (treaty + stamp + tariff).
6) **Quorum-minted authority:** distributed actions require quorum-issued permits (weighted, sybil-resistant).


### 25.X Canonicalization and Normal Forms (Normative-ish, Practical)

Cross-border interoperability requires that different nodes “see the same program”.
MMW recommends a canonicalization discipline for surface documents and artifacts.

Recommended artifacts:
- `CanonicalForm(target, canonical_digest, render_version, at_epoch)`
- `CanonicalizePolicy(scope, render_version, by=jurisdiction)`
- `CanonicalMismatch(target, because=...)`

Guidance:
- canonicalization SHOULD be deterministic and content-addressed (digest defines equality)
- crossings MAY refuse imports with canonical mismatches (prevents “same text, different meaning” attacks)
- self-hosting reference kernels SHOULD publish their render versions and canonicalization rules
- corrections/errata should preserve canonical links (Supersedes keeps traceability)

This is “normal form” for governance code.


## 26. End-to-End Reference Story (Informal)

Incident response across a federated system:

1) Nodes emit `Rumor(latency_spike, source)`; votes accumulate in `Epoch(e)`.
2) `QUORUM_COMMIT` mints `Cap(ActionPermit, mitigate_latency)` and a witness.
3) Explore phase forks 10 remediation branches; budgets split.
4) Interference merges/cancels incompatible worlds; coherence potential decreases.
5) `CHOOSE` selects minimal-risk plan with proof.
6) Commit phase crosses Quarantine→Production borders with treaties/tariffs; sensitive payloads sealed.
7) Externalization fossilizes receipts; later rollback becomes compensating transaction.
8) Queries (`WHY`, `WHY NOT`, `WHAT IF`) traverse receipts/origins to explain decisions.

## 27. Tooling & Self-Hosting (Optional)

MMW does not require self-hosting to be “complete.” However, the kernel is expressive enough to support
a compiler or transpiler written in MMW, **if** it is executed under a constrained runtime policy that
prioritizes reproducibility.

A recommended approach is to define a **Compilation Profile** as a runtime policy (not a separate language):
- deterministic rule selection
- single-scope compilation (no cross-node gossip, no cross-cell borders)
- fork/merge disabled (or permitted only in explicitly budgeted search passes)
- receipts remain available for debugging/explanation but are not treated as ordinary data

This keeps the “weirdness” available for programs, while allowing “boring” tooling when desired.

## 28. Open Design Questions (Deferred)

- Exact matching/unification model for Molecules (structural? typed?).
- How “scope tags” are named and how treaties specify schemas.
- How to represent split-by-reference allocations for conserved accounts.
- Whether interference weights are probabilistic, credence-based, or policy-driven.
- Determinism controls: chaotic kinetics vs policy scheduling.
- Surface syntax: rule declarations vs “forms” vs ledger-journal style.

---

### Consent-to-Receive (ACCEPT) (Creative Pattern)

(see notes)


prove         = "PROVE" ":" prove_spec ;
prove_spec    = ("kind" "=" ident) ("," "digest" "=" ident)? ;

deadman       = "DEADMAN" ":" ("escrow" "=" ident) "," ("trigger" "=" epoch_spec) ;

compost       = "COMPOST" ":" ("scope" "=" scope_tag) ("," "set" "=" ident)? ;


### PARDON (Governance Primitive, Optional)

(placeholder)

pardon        = "PARDON" ":" ("target" "=" ident) ("," "kind" "=" ident)? ;


### Bicameral Quorum (Creative, Stabilizing)

(placeholder)
declassify    = "DECLASSIFY" ":" ("scope" "=" scope_tag) ("," "after" "=" epoch_spec)? ;
nullify       = "NULLIFY" ":" ("statute" "=" ident) ("," "case" "=" ident)? ;
milestone     = "MILESTONE" ":" ident "," "due" "=" epoch_spec ;
delegate      = "DELEGATE" ":" ("from" "=" ident) "," ("to" "=" ident) "," ("scope" "=" scope_tag) ("," "until" "=" epoch_spec)? ;

### Restorative Justice and Reconciliation Circles

(placeholder)


### Interest, Escalation, and the Time-Value of Obligations

(placeholder)
evidence      = "EVIDENCE" ":" ("id" "=" ident) ("," "digest" "=" ident)? ;
standard      = "STANDARD" ":" ident ;
entrench      = "ENTRENCH" ":" ("target" "=" ident) ("," "threshold" "=" ident)? ;
interest      = "INTEREST" ":" ("kind" "=" ident) ("," "rate" "=" ident)? ;
restore       = "RESTORE" ":" ("case" "=" ident) ;
erratum       = "ERRATUM" ":" ("target" "=" ident) ;
correct       = "CORRECT" ":" ("target" "=" ident) "," ("by" "=" ident) ;
retract       = "RETRACT" ":" ("target" "=" ident) ;
depends       = "DEPENDS" ":" ("target" "=" ident) "," ("deps" "=" ident) ;
anon          = "ANON" ":" ("set" "=" ident) "," ("threshold" "=" ident) ;
deadlock      = "DEADLOCK" ":" ident ;
settle        = "SETTLE" ":" ("case" "=" ident) ("," "terms" "=" ident)? ;
choice        = "CHOICE" ":" ("case" "=" ident) ("," "law" "=" ident)? ;
pilot         = "PILOT" ":" ident "," ("scope" "=" scope_tag) "," ("start" "=" epoch_spec) "," ("end" "=" epoch_spec) ;
diff          = "DIFF" ":" ("old" "=" ident) "," ("new" "=" ident) ;
throttle      = "THROTTLE" ":" ("scope" "=" scope_tag) ("," "until" "=" epoch_spec)? ;


### Contradiction Ledger and Paraconsistent Reasoning

(placeholder)
sample        = "SAMPLE" ":" ("scope" "=" scope_tag) ("," "size" "=" ident)? ;
contradict    = "CONTRADICT" ":" ident ;
shadow        = "SHADOW" ":" ident "," ("old" "=" ident) "," ("new" "=" ident) ;
transition    = "TRANSITION" ":" ("old" "=" ident) "," ("new" "=" ident) "," ("end" "=" epoch_spec) ;
view          = "VIEW" ":" ("target" "=" ident) ("," "permit" "=" ident)? ;


### 3.5.1 Palimpsest Forgetting (Optional, Very Esoteric)

Sometimes you want to forget the raw content but retain *structured residue*:
a summary digest, statistics, or a court-approved “what we learned” statement.
MMW supports optional **palimpsest forgetting**: deletion with a governed shadow of meaning.

Recommended artifacts:
- `Palimpsest(commit_id, summary_digest, retained_stats=[...], method, at_epoch)`
- `PalimpsestPolicy(scope, allowed_stats, by=jurisdiction)`
- `PalimpsestChallenged(commit_id, because=...)` / `PalimpsestUpheld(commit_id, witness_id)`

Guidance:
- palimpsest outputs MUST be non-reconstructive by policy (no “easy rehydration”)
- palimpsest summaries SHOULD be admissible evidence only with explicit doctrine (standards of proof may differ)
- confidence claims about palimpsests MAY spend `ConfidenceBudget` (optional)
- palimpsest is compatible with escrow/dead-man: summaries can auto-release even when payload stays sealed

This is “forget, but keep the lessons,” with receipts.

habeas       = "HABEAS" ":" ("target" "=" ident) ("," "because" "=" ident)? ;
palimpsest   = "PALIMPSEST" ":" ("commit" "=" ident) ("," "summary" "=" ident)? ;
lint         = "LINT" ":" ("target" "=" ident) ("," "policy" "=" ident)? ;
redteam      = "REDTEAM" ":" ident "," ("target" "=" ident) ;
canon        = "CANON" ":" ("target" "=" ident) ("," "render" "=" ident)? ;
