# MMW Scratch Notes (Draft v3.9)

**Goal:** keep exploratory ideas without bloating the main spec.

## Bundles (Active)
- Cellular Bureaucracy (membranes + stamps + tariffs + custody)
- Multiverse Auditor (fork/choose with proof)
- Grace-Period Timekeeping (leased undo; TTL; soft commits; backoff)
- Interference Engine (merge algebra; cancellation without laundering evidence)
- Mycelial Federation (gossip + weighted quorum; epochs)

## Module Grafts (Optional)
### Market Scheduler (Debt/Interest + Bidding)
- Rules bid with scarce credits; debt accrues with interest.
- Runtime policy becomes “economic tuning”.
- Useful for backpressure and fairness.

### Thermodynamic Finality (Entropy Tax)
- Fossilization is entropy sink; can fossilize early by paying Entropy.
- Multiple entropies: IOEntropy, PrivacyEntropy, LatencyEntropy.

### Paraconsistent Court / Court of Appeals
- Contradictions allowed: Claim(X) and Deny(X) coexist.
- Action requires standing + evidence thresholds.
- Appeals = fork rehearing + choose + refute.

### Equilibrium Mode
- Run until stable residue rather than halt.
- Halting notions:
  - all work items Committed or Stuck-with-witness
  - no potential decreases possible
  - quorum commitments concluded per epoch

## Failure Modes & Patches (kept)
- Smuggling: make Cap opaque; split receipts into header/payload; treaty-check observable fields.
- Fork budget farming: split conserved resources/caps on fork; allocation references.
- Infinite grace: monotone time; renewal cost curve; fossils cannot be re-leased.
- Evidence laundering via cancellation: protect evidence; refutation only.
- Sybil quorum / rumor flooding: weighted quorum; bandwidth budgets; quarantine.

## Livelock Controls
- Border bounce: TransitCredit per form; escalation or Stuck.
- Search explosion: ExploreCredit budget; anytime choose.
- Retry storms: enforced increasing backoff; time credit burn.
- Merge chatter: coherence potential must decrease; hysteresis threshold.
- Consensus churn: epoch rounds; monotone commitments; appeal to overturn.

## UX Queries (unified)
- WHY is X present/allowed? -> minimal receipt chain (possibly sealed).
- WHY NOT did Goal happen? -> blockers + budgets/potentials + phase state.
- WHAT IF change budgets/policy/phase? -> controlled branch + witness diff.

## Self-Hosting Thoughts

**Craziness scale (informal):**
- Full kitchen-sink chimera self-hosting: **9/10** (possible in principle, brutal in practice).
- A deterministic “Compilation Profile” hosting a compiler that lowers surface syntax → kernel IR: **6/10**.

### Why it’s hard
- nondeterminism (chemical choice, kinetics, branch/merge) fights reproducibility
- receipts/leases can balloon runtime state if treated as normal data
- scopes (branch/cell/node/epoch) add dimensions a compiler usually doesn’t want

### Why it’s plausible
- compilation is naturally expressed as rewrite passes over AST molecules
- receipts provide built-in debugging/provenance for compiler passes
- budgets/potentials/phases can enforce termination and bounded search

### Plausible bootstrap path
1) host a minimal kernel runner in another language
2) write an MMW compiler that lowers a surface syntax to kernel IR (rules + molecules)
3) use the host runner to compile the compiler (self-apply)
4) iterate toward more “native” tooling if desired

## Treaties as Types

Treaties are elevated to the primary type/interface system:
- each treaty defines an **observable projection** per molecule kind
- crossing a border is the typecheck + redaction step
- sealing/headers/payloads are the standard method to move “private parts” safely

Implication: compositional safety via customs. “Type errors” manifest as `CROSS` rejection artifacts.

## Doctrine Library Ideas

A “doctrine” is rule metadata that changes social meaning without changing kernel semantics:
- Standing / Jurisdiction / Burden / Remedy / Sunset
- Useful as an idiomatic layer for policy engines and compliance flows.

Possible doctrine presets:
- **Emergency Powers**: standing broadened, but costs RiskBudget+Entropy and auto-seals receipts.
- **Due Process**: strict jurisdiction and burden; more forks allowed; appeals cheap inside grace.
- **Martial Law**: deterministic scheduling; forks disabled; rapid fossilization.

## Surface Documents (Sketch)

Non-normative vibe layer that could still compile down cleanly:
- STATUTE blocks define rules with clauses (requires/matches/effects)
- FORM blocks define structured payload schemas
- TREATY blocks define projections + tariffs + sealing requirements
- DOCKET blocks are bundles of receipts/witnesses used for audits/appeals

## Interference & Treaties

Key decision: **exportability is treaty-governed**, and interference cannot “wash” restricted origins.
Even if internal cancellation eliminates a sensitive fact, any derived obligations to seal/redact survive via origin lineage.

Implementation hint: compute a derived “taint class” from Origin handles/receipts; enforce at CROSS/GOSSIP/PUBLISH.
This taint need not be a molecule; it can be runtime metadata, keeping the language minimal.

## Regimes as Semantics-Adjacent Policy

Regimes are policy presets over:
- deterministic vs kinetic scheduling
- fork/merge enablement and budgets
- default sealing and fossilization thresholds
- doctrine defaults (standing/jurisdiction/burden/remedy/sunset)

Idea: regimes can be escalated only via quorum-issued permits (Emergency Powers requires Witness + costs).

## Publication Points

Define explicit *externalization events* (PUBLISH, SEND_OUT, WRITE_REALFILE) that:
- force treaty projection
- default seal sensitive payloads
- fossilize all receipts in the causal cone (or at least the minimal dependency set)

## Appeal Pipeline

Non-normative helper molecules:
- `Contested(claim, because)` — marks a dispute without deleting evidence.
- `Superseded(old, new)` — indicates an older witness/ruling is superseded by a newer one.

These are not kernel requirements; they are surface-language conveniences that compile down to receipts/witness/refutations.

## PUBLISH Primitive

Hard decision: externalization is explicit via `PUBLISH` (or equivalent platform hook).
This concentrates:
- treaty projection/redaction
- sealing requirements
- cone fossilization policy (MDS/CCF)
- spending of Entropy/Privacy/Bandwidth budgets
- jurisdiction admissibility checks

This makes “real effects” legible and auditable, and prevents export/rollback paradoxes.

## Allocation References

Preferred mechanism for conserved non-splittable items (opaque capabilities):
- `Alloc(id, amount)` can be spent once; spending yields `Spent(id)`.
- Works across forks/merges by treating spent status as global truth (within governance policy).

## Dockets

Dockets are the portable “paper trail” artifact:
- headers always visible
- payloads may remain sealed
- includes witnesses, refutations, and cone metadata
- used as the unit of audit/appeal/postmortem

This is a natural fit for the surface-document vibe: DOCKET blocks compile into docket artifacts.

## Executable Regimes

Regimes can be activated via governance:
- represent active regime as `RegimeActive(name)`
- escalation requires quorum-issued standing
- regime changes emit witnesses and are subject to grace/appeal unless fossilized by PUBLISH

## Supersession Lattice

Need a clean semantics for “current ruling”:
- model witnesses as immutable artifacts
- relate them via Superseded/Refuted
- queries compute effective truth by finding latest admissible non-refuted witness

Potential pitfall: cycles; treat as Stuck or require explicit refutation to break.

## Legitimacy Budget

Make “abuse” semantically expensive:
- emergency powers or treaty overrides burn LegitimacyBudget
- replenishment requires governance (quorum renewal, audits, or time-based rules)
This is a fun political/thermodynamic hybrid: legitimacy is a conserved moral resource.

## Treaty Override

Break-glass mechanism must be expensive and obvious:
- requires OverridePermit + quorum witness + Emergency Powers regime
- burns LegitimacyBudget + Entropy (and likely Privacy/Risk)
- forces CCF fossilization and default sealing
- emits header-visible marker (no secret emergencies)

## Amnesty / Restoration

Counterweight to legitimacy burn:
- amnesty consolidates after emergencies to prevent endless appeal churn
- legitimacy replenishes via audits, time, or quorum renewals (never silently)

## Postmortem Ritual

After OverrideUsed, require a postmortem docket within N epochs or legitimacy bleeds.
This makes emergency action self-limiting and forces a governance feedback loop.

## Sealing Dialects

Sealing modes beyond binary:
- opaque
- redacted summary
- commitment only (hash)
- selective reveal under standing/jurisdiction

## Public/Private Split

Even sealed receipts must expose header-minimum metadata so auditors can see *that* something happened and what it cost.

## Selective Reveal

A reveal event:
- cites original sealed receipt headers
- requires RevealPermit standing + admissible jurisdiction
- emits a reveal receipt header
- reveals minimal field subset required (default)

This keeps sealing reversible in controlled ways without destroying auditability.

## Probationary Export

Two-stage publish:
- export only redacted summary or commitment-only artifact first
- later reveal more under due process
Nice for rapid response workflows.

## AUDIT_PASS Primitive

Privileged audit that can replenish legitimacy (capped) only via explicit audit witnesses.

## Reveal Scopes

A reveal is always *to a scope*:
- enforce visibility boundaries for revealed fields
- propagation requires explicit publish/gossip with treaty checks
- no retroactive alteration of past published artifacts

## Sealed Docket Escrow

Pattern: docket sealed now (commitment-only), eligible for reveal after condition:
- N epochs, audit pass, or quorum witness.

## Honest-by-Default Queries

WHY/WHY NOT/WHAT IF must surface header-minimum costs:
- sealing dialects, regime, cone policy, budget delta summaries
Even if payload sealed, the system stays accountable.

## Claims as Derived Truth

Instead of mutating booleans, store Claim/Deny molecules and let “truth” be a derived property:
- computed from supersession lattice + jurisdiction admissibility
- actions require standing + admissible witness
Allows paraconsistency without chaos.

## Obligations

Make governance deadlines explicit via obligation artifacts:
- PostmortemDue, AuditRequired, CompensationDue, EscrowReleaseEligible
Unmet obligations can trigger legitimacy bleed, escalation, quarantine, or stuckness.

This is a nice “administrative debt” analogue to resource budgets.

## Claim Court

Reusable statute bundle for adjudicating claims:
- admissibility checks
- rehearing forks and merges
- ruling witness in court jurisdiction
- supersession/refutation emitted as remedy
- docketed outputs for portability

## Compensation Calculus

After fossilization, “undo” becomes compensating transactions:
- must reference the fossilized receipt(s) they compensate
- must emit a witness linking old and new effects
- often generates obligations (audit required, compensation due)
This keeps externalized history immutable while still allowing correction.

## Obligation Enforcers

Standard statutes that turn debts into consistent consequences:
- legitimacy bleed
- quarantine
- escrow freeze
Avoids bespoke punishment logic in every workflow.

## Risk Classification

Externalizations can auto-trigger `AuditRequired` based on header-visible signals:
- PrivacyBudget / RiskBudget / Entropy spent
- OverrideUsed in cone
- sealing dialects used
- destination treaty sensitivity

Nice property: auditors can see why audit was required without unsealing payloads.

## Compensation Normal Form

Make compensations auditable by structure:
- references fossil receipts compensated
- replacement effect molecule(s)
- linking compensation witness
- optional review obligations
- never erases evidence (supersede/refute)

## Paperwork Debt (Optional)

Compounding penalty for unmet obligations:
- enforcers mint PaperworkDebt and apply interest per epoch
- high debt can block publish/override/reveal
- debt reduced only by satisfying obligations

This makes governance latency a first-class economic signal.

## Sensitivity Lattice (Treaties)

Add an info-flow lattice at the treaty layer:
- Public / Confidential / Secret / Sealed
- maps to sealing dialect requirements
- feeds RiskClass and audit triggers
This is “types by customs stamp” with a security vibe.

## Obligation Discharge & Delegation

Obligations are immutable debts; status evolves:
- discharge emits witness and can reduce PaperworkDebt
- delegation preserves obligation id/due time, may be treaty-restricted
Suggest privileged helpers: DISCHARGE / DELEGATE.

## DELEGATE Helper

Privileged delegation that records delegation chains visibly:
- preserves obligation id + due time
- requires standing across borders
- may require acceptance by delegatee
Prevents “responsibility laundering.”

## RiskClass Calculator

Deterministic statute that computes RiskClass from header-visible inputs:
- treaty sensitivity labels
- sealing dialects
- budget delta summaries
- override lineage markers
Emits a witness so queries can explain “why this is high risk.”

## Jury Duty / Duty Rosters

Sybil-resistant selection of auditors/judges:
- weighted by TrustStake
- constrained by Bandwidth/Latency budgets
- issues leased JuryDuty caps
Weird but genuinely practical for federated governance.

## Recusal & Conflicts

Add court/audit mechanics to prevent capture:
- ConflictOfInterest, Challenge, Recused artifacts
- challenges must be justified; outcomes witnessed/docketed
- abusive challenges can cost legitimacy or accrue paperwork debt

## Case Market Scheduler

Optional economics for court/audit capacity:
- cases carry CaseCredit; statutes bid to process
- backlog becomes PaperworkDebt/obligations
- fairness floor via jury duty rotation

## Verdict Sealing

Public verdict headers + sealed reasoning payloads + selective reveal for authorized scopes.
Perfectly aligned with privacy-without-invisibility.

## Treaty Versioning & Migrations

Treaties are interfaces: version them.
- CROSS/GOSSIP/PUBLISH record treaty version used
- deprecation emits MigrationDue obligations
- migration dockets document upgrades/grandfathering
- amnesty can scope a transition window

## AMEND Primitive

Privileged operation to change treaties/statutes/regimes/courts.
- quorum + legitimacy cost
- amendment dockets + migration obligations
- epoch-boundary effect unless emergency-authorized

## Jury Service Economics

Close the loop:
- mint ServiceCredit (or adjust TrustStake) for completed duty
- penalties for non-service without admissible recusal
Keeps jury duty sustainable and auditable.

## Judicial Review

Courts can invalidate or stay statutes/treaty clauses:
- challenged/invalidated/stayed artifacts
- higher-jurisdiction standing + docketing
- stays + migration obligations avoid hard breaks

## Meta-Treaties and Constitutional Layers

Add a layered constitution and meta-treaties to enforce interoperability:
- sensitivity lattice required
- default cone policy declared
- sealing dialect mappings declared
Keeps federation consistent and makes “treaties as types” less ambiguous.

## Emergency Sunset

Emergency Powers must expire unless renewed by quorum.
Renewal costs legitimacy. Auto-revert to Due Process.
Prevents permanent emergencies.

## Notary Nodes / Fossil Shards

Scalability pattern:
- notaries attest to fossil sets without revealing payloads
- dockets carry shard commitments + minimal indices
- selective reveal still possible under standing

## Constitutional Court

Specialized elevated Claim Court for AMEND/treaty versions/meta-treaty conflicts.
Defaults: strict standing, docketing, verdict sealing, often audit after major rulings.

## Precedent / Stare Decisis

Mark some rulings as precedent:
- Precedent(witness_id, level)
- Cites(new, old)
- Overruled(old, new)
Breaking precedent should be expensive + loud (legitimacy spend or PrecedentDebt).

## Amicus Briefs

Third parties can submit dockets/arguments:
- acceptance witnessed + docketed
- spam can cost legitimacy or accrue paperwork debt

## Counterfactual Dockets / Dream Court

Preserve WHAT IF branches as artifacts (internal by default).
Dream Court adjudicates hypotheticals to output predicted rulings/costs/obligations without externalization.
Nice for planning and policy simulation.

## Sunsets Everywhere

Generalize sunsets beyond regimes:
- extraordinary permissions should expire by default
- continuations emit renewal obligations
- non-renewal can bleed legitimacy or accrue paperwork debt

## Right to Explanation

Even with verdict sealing:
- require a treaty-projected reason summary (redacted)
- cite header-visible evidence and list sealed dockets relied on
- selective reveal can disclose more under standing
Prevents black-box courts.

## Slashing / Misconduct

Jurors/notaries can bond stake/credits.
Proven misconduct triggers Slashed(...) via witnessed ruling.
Allegations docketed; handled by higher-jurisdiction courts.

## TransparencyBudget

Optional dial: sealing spends transparency; revealing/audit replenishes.
Lets policies cap secrecy and make prolonged opacity explicitly costly.

## Epoch Commitments

Optional signed epoch hashes in headers (and notary attestations) to make timing disputes justiciable.

## Whistleblower Dockets

First-class sealed/escrowed reporting channel:
- Whistleblower(...) references a docket
- default commitment-only/opaque + header-visible routing metadata
- escrow + controlled reveals, protective orders
- false reports handled carefully to avoid chilling effect

## Appeal Bonds / Filing Fees

Anti-spam: filings may require bonds in CaseCredit/PaperworkDebt escrow.
Refund on non-frivolous/success; abuse increases multipliers or burns legitimacy.

## TreasuryCredit and Bounties

Optional public-goods loop:
- TreasuryCredit funds audits/juries/bounties
- BOUNTY primitive rewards verified governance work (docketed, witnessed)

## Witness Liability

Optional: fraud-refuted witnesses can trigger slashing (due process), while supersession isn't punished.
Encourages careful testimony without punishing honest corrections.

## Dissent / Minority Reports

Courts can emit concurrences and dissents as docketed artifacts:
- Concurs(...), Dissent(...), MinorityReport(...)
Dissents can become future precedent candidates or support overruling.

## ComplexityBudget

Price “bureaucratic bloat”:
- statutes declare complexity
- high complexity spends ComplexityBudget
- audits can restore some by simplifying equivalent statute bundles

## Identity Layer (Optional)

Capability-first by default, but allow pseudonyms + optional proof-of-personhood + trust stake for sybil resistance.
Treat identity attestations as witnesses/evidence.

## Ratification Windows

Stage AMEND changes:
- propose + simulate in Dream Court
- probationary adoption window with forced probationary exports + migration obligations
- stays can pause rollout

## Ephemeral Deliberation / FORGET

Allow ephemeral artifacts in Explore/counterfactual dockets.
FORGET is explicit: drops retrievability (possibly destroys keys) but emits a header-visible receipt with scope/epoch/counts.
Never applies to fossilized receipts or published artifacts.

## Memetic Quarantine

Optional hazard tagging (HazardClass, Contagion):
- forces sealing + CCF fossilization for toxic info
- triggers quarantine-review obligations and possible audit gating
Govern “dangerous knowledge” without pretending it never existed.

## Exchange Bureau

Optional treaty-governed account conversion:
- ExchangeRate + Exchanged receipts
- requires standing + spends ExchangeCredit/Legitimacy
Prevents silent budget laundering while allowing explicit tradeoffs.

## Legal Holds / Retention Policies

If FORGET exists, also support DO-NOT-FORGET:
- RetentionPolicy(scope, kind, keep_epochs)
- Hold(...)/HoldReleased(...) with sunsets
- holds block FORGET for affected scope/kind
Releasing holds is witnessed; disputes can go to court.

## Quorum Reveal

For highly sensitive reveals:
- reveal petitions require k-of-n approvals via jury duty/notaries
- approvals mint scoped RevealPermit
- petition + approval count should be header-visible
Good for toxic hazards, constitutional reasoning, protected sources.

## StorageBudget

Optional conserved account to price retention/storage.
Retention policies and holds can spend StorageBudget so “keep everything forever” becomes expensive and explicit.

## Quarantine Orders and Challenges

Formalize quarantine governance:
- QuarantineOrdered/Lifted/Challenged
- sunsets + review obligations
- challenges may require bonds to prevent spam
Even quarantined actions keep reason summaries + header-minimum costs.

## Oblivion Proofs

Optional verifiable forgetting:
- ephemeral sealed payloads can have commitment ids
- FORGET may emit OblivionProof(commit_id, scope, epoch, method)
- proofs must not enable recovery; holds block oblivion proofs
Gives “right to be forgotten” a verifiable footprint.

## Governance Telemetry Dockets

Periodic signed/attested dockets summarizing:
- aggregate budget deltas
- obligations outstanding
- audit/quarantine backlog
- major governance events
Publishing can spend TelemetryBudget; payload may be sealed; headers stay honest-by-default.

## TelemetryBudget

Optional cap/dial for governance observability.
Prevents “free surveillance dashboards”; treaties define exportability of telemetry summaries.

## Random Beacons and Lotteries

Commit-then-reveal randomness for civic selection:
- RandomBeacon(epoch, commit), RandomReveal(epoch, value)
- drives jury/audit selection; disputes are justiciable
Reduces bias/grinding in duty rosters.

## Treaty Test Dockets

Treaties are border types; test them:
- bundle example inputs + expected projections/redactions + expected risk/sensitivity
- required during ratification windows; used for compatibility disputes

## Timebars / Statute of Limitations

Optional timebars for courts to prevent infinite backlog:
- Timebar + Timebarred + TollingGranted
- tolling requires standing; protected sources may get presumptive tolling

## Consent-to-Receive (ACCEPT)

Optional import handshake:
- CROSS -> ImportOffer
- receiver must Accept/Reject (standing/treaty-controlled)
Quarantine/hazards can require explicit accept and trigger review obligations.

## Proof-Carrying Governance

Optional “proof-carrying” dockets/witnesses:
- Proof / ProofRequired / ProofAccepted / ProofRejected artifacts
- used for OVERRIDE/AMEND/high-risk PUBLISH
- verification can spend ProofBudget; missing proofs can block or create ProofDue obligations

## Circuit Splits / En Banc

Make divergent precedents explicit:
- CircuitSplit(issue,...)
- EnBancRequested/Convened/Ruling
Splits become governance debt surfaced in queries/telemetry; en banc unifies at legitimacy/case-credit cost.

## Dead-Man Escrow

Escrow with a trigger epoch:
- Deadman(... trigger_epoch, action=release/quarantine/audit)
- renewals are explicit + costly; firing emits obligations
Great for protected sources and anti-suppression accountability.

## Bootstrapping / Self-Hosting (Conceptual)

Reference Kernel as statute+treaty bundle:
- governs parsing/interpretation of surface docs
- externalized and amended like other artifacts
- enables staged self-hosting later via compatibility/proof dockets

## Treaty Fuzz Dockets

Randomized/adversarial treaty tests:
- seed from RandomBeacon
- generator spec + assertions about redaction/risk/hazard invariants
Used during ratification; failures emit patch/migration obligations.

## Crisis Arbitration Regime

A painful “constitutional crisis” preset:
- auto-convene en banc / constitutional court
- freeze externalizations to probationary export
- require proofs for overrides/amends
- accelerated legitimacy burn + short sunsets
Forces convergence during governance deadlock.

## Composting / Compaction

“Garbage collection for governance”:
- COMPOST converts receipt sets into fossil shards + reason summaries + index hints
- should be notary/quorum attested; optionally proof-carrying
- may reclaim StorageBudget but spend Proof/Complexity budgets
Challengeable; holds can forbid compaction.

## PARDON (Optional)

Mercy/cleanup without erasure:
- discharges certain obligations/debts, loudly and docketed
- costs legitimacy (and maybe treasury)
- some classes may be unpardonable (hazards/constitutional violations)

## Exhaustion Doctrine / Appeal Ladders

Programmable appeals:
- require ExhaustedRemedies before higher courts/constitutional review (unless emergency standing)
- explicit FinalJudgment for finality
- appeals respect timebars and may require bonds

## Declassification / Time-Locked Sealing

Optional declassification policies make secrecy expire unless renewed:
- DeclassifyPolicy schedules label relaxation over epochs
- Declassified events docketed; quorum reveal for toxic hazards if needed
- holds/retention can delay but should sunset + cost legitimacy
Can optionally replenish TransparencyBudget.

## Jury Nullification

Explicit (expensive) nullification artifact:
- Nullified(case_id, statute_ref, ...)
- witnessed + docketed; reason summary required
- costs legitimacy / precedent debt; often triggers higher-court review
Treaties can declare non-nullifiable classes (hazards/quarantine).

## Bicameral Quorum

Two chambers must approve high-impact changes:
- ChamberVote + BicameralPassed/Failed
Reduces capture by a single constituency; can be required by meta-treaties for cross-border constitutional moves.

## REPEAL

Loud rollback of prior AMEND:
- preserves history but changes what is in force
- witnessed/docketed; ratification windows + migration obligations recommended
Typically requires equal-or-higher standing (often bicameral).

## Mootness / Advisory Opinions

Capacity saver:
- Moot(case_id) dismisses no-longer-live controversies
- advisory opinions are constrained; Dream Court covers most hypotheticals without externalization

## Remediation Orders / Injunctions

Outcomes beyond account deltas:
- Injunction(forbids..., until_epoch) with sunsets
- RemediationOrder(requires..., milestones)
- ComplianceReport + Contempt

## Phased Obligations / Milestones

Multi-step obligations:
- Milestone(... due_epoch), MilestoneMet/Missed
- missed milestones can escalate to audits/court under policy
Makes long-running governance work programmable.

## Cooling-Off Periods

Anti-corruption:
- cooling-off obligations bar jurors/notaries from related bounties/contracts for a window
- enforced via injunction/remediation

## Deliberation Markets

Allocate scarce governance labor (audits/proofs/fuzzing/migrations):
- tasks as obligations, funded by treasury bounties, prioritized by case credit
- bounded by Proof/Complexity budgets; conflict-of-interest guardrails

## Impact Assessments / Blast Radius

Optional impact accounting for PUBLISH:
- ImpactEstimate + ImpactGuard + ImpactApproved/Denied
- high-impact publishes can spend ImpactBudget/Legitimacy and require proofs
Crossings can refuse imports that exceed local impact caps.

## Delegated Standing

Representation as a governed artifact:
- DelegatedStanding(... scope, until_epoch, limits)
- RevokedDelegation + ProxyFiled
Scoped, time-bounded, treaty-restricted; abuse handled via bonds/slashing.

## Surety / Underwriting

Insurance for obligations:
- Underwrite(obligation_id, collateral, amount)
- claims/pay/default artifacts
Collateral slashing under due process; pairs with milestones; conflicts-of-interest apply.

## Recusal Registry

Auditable disclosure:
- ConflictDeclared + Recused/Denied + RecusalChallenged + RecusalRegistryEntry
Prevents silent judge-shopping; concealment is fraud (due process/slashing).

## Treaty Withdrawal / Secession

Loud exit hatch:
- TreatyWithdrawal / TreatyTermination / Secession / ExitSettlement
Long notice windows + migration obligations; may require bicameral quorum + constitutional review; impact assessment recommended.

## Evidence Chain / Chain-of-Custody

Evidence is governed, not assumed:
- Evidence(item_id, digest, source, collected_at_epoch)
- CustodyTransfer witnessed for high-stakes cases
- broken chains can discount/exclude evidence
Escrow + dead-man triggers pair well with protected sources.

## Standards of Proof / Burdens

Doctrine for confidence:
- StandardOfProof + BurdenOfProof + FailedBurden
- higher standards can require more proofs and spend ProofBudget
- treaties can map risk/hazard to default standards; stipulations are docketed

## Restorative Justice / Reconciliation Circles

Consent-based repair track:
- CircleConvened + RestorationPlan + Accepted/Rejected + Restored
- plans compile to phased obligations + milestones (and can be underwritten)
- failure returns to adversarial track; never erases receipts (pairs with PARDON without erasure)

## Entrenchment / Unamendable Clauses

Explicit constitutional rigidity:
- Entrenched / Unamendable + challenge/upheld artifacts
- should require bicameral + constitutional review and sunset unless renewed
- very rare; treaty-visible across borders

## Interest / Escalation (Time-Value of Obligations)

Optional “delay costs money” model:
- InterestRate + InterestAccrued + Escalated
- outstanding obligations can accrue PaperworkDebt or spend PatienceBudget
- delinquency can auto-trigger audits/bond increases/stricter proof standards; emergency freezes must sunset

## Corrections / Errata / Retractions

Externalizations are governed claims; edits must be explicit:
- Erratum (narrow fixes), Correction (new artifact + link), Retraction (withdraw reliability)
- links: Supersedes / RetractedBy
Loud retractions cost legitimacy; telemetry can surface correction counts; right-of-reply possible.

## Dependencies / Compatibility Proofs

Treaties/statutes as packages:
- DependsOn + CompatProof/CompatFailed + IncompatibleWith
Borders can refuse imports with unsatisfied dependency graphs; proofs can attest deps satisfied.

## Forks / Merges (Git for Law)

Parallel AMENDs can conflict:
- Fork + ConflictSet + MergeProposal + MergeRuling/MergeFailed
Conflicts are telemetry-visible governance debt; merging uses ratification windows + bicameral often; crisis arbitration can auto-trigger.

## Anonymity Sets / Group Witnessing

Witness without revealing which member:
- AnonymitySet + GroupWitness(threshold)
Membership is governed; fraud-refuted group witnesses can sanction sets; disclosure may be forced under quorum reveal by policy.

## Deadlocks / ConvergenceDue

Make “governance stuck” explicit:
- DeadlockDetected -> Obligation(ConvergenceDue) with due_epoch
- failure can auto-activate Crisis Arbitration under policy
Convergence work can be funded via deliberation markets/bounties.

## Settlements / Plea Agreements

Negotiated outcomes as docketed artifacts:
- SettlementProposed/Accepted/Approved (+ rejections)
- PleaEntered/Accepted/Withdrawn
Terms compile to remediation + phased obligations + milestones; minimum reason summaries required; abuse accrues paperwork debt and can trigger throttling.

## Choice-of-Law / Conflict-of-Laws

Make border “which law applies?” explicit:
- ChoiceOfLaw + ConflictOfLaws + ChoiceResolved
Treaty-defined defaults; header-visible bundle refs; unresolved conflicts can trigger deadlock/crisis arbitration.

## Pilot Programs / Experimental Law

A/B test statutes/treaties on constrained cohorts:
- Pilot + PilotGuard + PilotReport + Extended/Terminated + RolledOut
Impact-bounded + telemetry-visible; must sunset; borders can treat pilots as probationary by default.

## Semantic Diffs / Migration Guides

Upgrade docs as governed artifacts:
- Diff(old,new) + MigrationGuide(steps, tests)
- MigrationSatisfied/Failed
Hook into treaty tests/fuzz; optional proofs for invariants; digests preserved in fossils after compaction.

## Statistical Audits / Sampling

Optional sampling audits:
- SampleAuditPlan seeded by RandomBeacon to prevent cherry-picking
- SampleAuditResult + ConfidenceClaim(level)
Confidence claims can spend ConfidenceBudget; failures auto-escalate to larger samples/full audits/court review.

## Contradiction Ledger / Paraconsistent Reasoning

Govern inconsistent states instead of exploding:
- ContradictionDetected + InconsistencyTolerated + InferenceSuspended + ResolvedContradiction
Contradictions are telemetry-visible debt; externalization from contradictory bases may be barred unless resolved/proven.

## Shadow Execution / Replay Dockets

Simulate proposed rules on past receipts:
- ShadowRun + ShadowResult + ReplayVerified/Disputed
Feeds ImpactEstimate and pilots; can be treaty-required for high-impact changes. Evidence, not judgment.

## Grandfathering / Transitional Rules

Governed compat mode:
- TransitionalRule + Grandfathered + TransitionExpired/Violation
Must sunset; expensive in complexity/legitimacy; borders can refuse expired transitional dependencies.

## View Permits / Access Logs

Accountable viewing of sealed payloads:
- ViewPermit + ViewLogged + ViewDenied + ViewAbuseClaim
View logs header-visible as events; treaties may require for protected sources/toxic hazards; misuse is justiciable.

## Hold Review / Habeas Petitions

Challenge indefinite holds/quarantines:
- HabeasPetition + HoldReviewScheduled + HoldReviewed (upheld/modified/lifted)
- review rights can narrow under emergency regimes but must sunset + postmortem
Prevents “hold forever” as covert veto; integrates with throttling for bad-faith petitions.

## Palimpsest Forgetting

Forget raw payload, retain governed residue:
- Palimpsest(commit_id, summary_digest, retained_stats, method)
- policy ensures non-reconstructive summaries
- summaries admissible only under explicit doctrine; confidence claims can spend ConfidenceBudget

## Statute Linting / Hygiene

CI for governance:
- LintPolicy + LintReport + LintWaived (witnessed)
Checks complexity hygiene, sunsets/review hooks, dependency consistency, contradiction hints, missing migration guides.
Waivers cost legitimacy for high-impact changes; treaty-shared lint schemas possible.

## Red Team Dockets / Adversarial Drills

Governed bug-bounty exercises:
- RedTeamExercise + ExploitReport + PatchProposed/Accepted + BountyAwarded + ExerciseConcluded
Must respect sealing; severity header-visible; safe-harbor policies; high severity can trigger holds/probation/crisis arbitration.

## Canonicalization / Normal Forms

Deterministic rendering + content-addressed equality:
- CanonicalForm + CanonicalizePolicy + CanonicalMismatch
Crossings can refuse mismatches; render versions published by self-hosting kernels; preserves traceability across corrections.
