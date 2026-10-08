# Changelog — MMW Spec

## 2026-01-04 v0.1
- Created initial spec draft consolidating kernel, primitives, invariants, and bundle profiles.
- Added scratch notes doc to preserve exploratory modules and failure-mode patches.

## 2026-01-04 v0.2
- Added optional Tooling & Self-Hosting section and “Compilation Profile” concept (policy, not a separate language).
- Added Self-Hosting Thoughts and bootstrap notes to scratchpad.

## 2026-01-04 v0.3
- Added Treaties-as-Types interpretation (observable schema projections) and formalized WHY/WHY NOT/WHAT IF queries.
- Added “Legal Doctrines” metadata layer for rules, plus an account palette for conserved dimensions.
- Added a non-normative “Surface Documents” sketch (Statutes/Forms/Treaties/Dockets) to preserve vibe without polluting kernel semantics.
- Expanded scratch notes with doctrine presets and treaty/type implications.

## 2026-01-04 v0.4
- Added normative Interference & Information Flow section (no taint laundering; exportability via treaty projection; externalization fossilizes receipts).
- Added Regimes (policy presets) with examples: Due Process, Emergency Powers, Martial Law.
- Added a non-normative EBNF sketch for Surface Documents (Statutes/Forms/Treaties/Dockets).
- Expanded scratch notes on interference-export interactions, regimes as policy, and publication points.

## 2026-01-04 v0.5
- Added Externalization Cones (Minimal Dependency Set vs Causal Cone Fossilization) with policy hooks.
- Added Jurisdictional Standing (scoped admissibility of receipts and standing tokens) and linked appeals to jurisdiction transfer.
- Added a canonical Appeal Pipeline template under doctrines.
- Expanded notes with non-normative helper molecules for disputes/supersession.

## 2026-01-04 v0.6
- Added privileged PUBLISH/EXTERNALIZE rule with normative pre/postconditions tying treaties, sealing, cone fossilization, and budgets.
- Added normative Allocation References strategy for fork-safe conserved resources/capabilities (Alloc/Spent semantics).
- Updated notes with PUBLISH and allocation reference rationale.

## 2026-01-04 v0.7
- Defined normative merge reconciliation for allocation references, including double-spend conflict handling (stuck vs appeal by regime).
- Added normative regime activation mechanism (RegimeActive, quorum authorization, auditable witnesses).
- Added Dockets section describing portable audit bundles with minimality and jurisdiction portability rules.
- Updated notes with docket and executable regime ideas.

## 2026-01-04 v0.8
- Added Supersession Lattice for rulings/evidence (Witness, Superseded, Refuted) and query semantics for “current ruling.”
- Added Doctrine Presets that compile into concrete constraints (Due Process, Emergency Powers, Martial Law).
- Added optional LegitimacyBudget account as an explicit cost for governance overrides and policy abuse.
- Updated account palette and notes accordingly.

## 2026-01-04 v0.9
- Added Treaty Override extraordinary mechanism with strict standing, cost, docketing, and forced CCF fossilization.
- Added Amnesty and Restoration governance mechanisms (auditable amnesty; slow, legible legitimacy replenishment).
- Clarified RegimeActive + doctrine preset binding with explicit deviation rules (exceptions require standing + legitimacy spend).

## 2026-01-04 v1.0
- Added Postmortem Ritual: overrides require audited docket + quorum witness within N epochs or legitimacy bleeds.
- Added Sealing Dialects: multiple sealing modes (opaque, redacted summary, commitment only, selective reveal) recorded in headers.
- Added Public vs Private Ledger Split: header-minimum metadata is mandatory for accountability under sealing.
- Extended canonical invariants with paperwork and privacy-without-invisibility rules.

## 2026-01-04 v1.1
- Added Selective Reveal sketch under Sealing Dialects (reveal events require standing, admissibility, and emit receipts).
- Added Probationary Export option under PUBLISH (two-stage externalization: summary/commitment first, later reveal via due process).
- Added AUDIT_PASS privileged governance primitive enabling explicit, capped legitimacy restoration via audit witnesses.

## 2026-01-04 v1.2
- Added Reveal Scopes: reveals target a scope; propagation of revealed fields requires explicit publish/gossip and treaty checks.
- Added Sealed Docket Escrow pattern (delayed transparency after epochs/audit/quorum).
- Added Honest-by-Default query policy requiring header-minimum accountability metadata in query outputs.

## 2026-01-04 v1.3
- Added ESCROW_RELEASE privileged rule (authorizes selective reveal after escrow conditions; does not reveal content itself).
- Clarified GOSSIP vs PUBLISH: gossip is internal propagation unless a channel is classified as externalization (then fossilization applies).
- Added Claims as Derived Truth idiom (truth maintained via supersession lattice and jurisdiction admissibility rather than mutable booleans).

## 2026-01-04 v1.4
- Added Obligations as first-class governance debts with enforceable consequences (legitimacy bleed, escalation, quarantine, stuckness).
- Added Claim Court canonical pattern for adjudicating claims and producing rulings with supersession/refutation and docketing.
- Added regime effects guidance on phase machine behavior (Due Process vs Emergency Powers vs Martial Law) and obligation emission.

## 2026-01-04 v1.5
- Added compositional obligation generation guidance (overrides/publish/escrow release can auto-emit obligations via treaty/regime templates).
- Added normative compensation after fossilization: corrections via compensating transactions with explicit witnesses and references.
- Added Canonical Obligation Enforcers (standard statutes) for consistent auditable consequences (bleed/quarantine/freeze).

## 2026-01-04 v1.6
- Added Risk Classification and Audit Triggers guidance for PUBLISH (header-visible derivation; treaty/regime thresholds).
- Added Compensation Normal Form recommendation to standardize compensating transactions for auditability.
- Added optional PaperworkDebt economics (interest/compounding penalties for unmet obligations) and extended account palette.

## 2026-01-04 v1.7
- Added treaty sensitivity lattice (Public/Confidential/Secret/Sealed) to drive sealing dialect requirements and risk classification.
- Added obligations discharge/delegation guidance (obligations are immutable debts; discharge emits witnesses; delegation preserves ids/due times).
- Added DISCHARGE privileged helper sketch and connected discharge to optional PaperworkDebt reduction.

## 2026-01-04 v1.8
- Added DELEGATE privileged helper with delegation chains and cross-border standing requirements.
- Added deterministic RiskClass Calculator statute recommendation emitting witnesses for explainable risk classification.
- Added Jury Duty / Duty Rosters pattern for sybil-resistant, capacity-aware selection of auditors and courts.

## 2026-01-04 v1.9
- Added Recusal/Challenge/Conflict patterns for Jury Duty and courts (witnessed, docketed; abuse can cost legitimacy/debt).
- Added optional Case Market Scheduler for adjudication/audit capacity (CaseCredit bids, backlog signals, fairness floor).
- Added Verdict Sealing convention (public headers, sealed reasoning, selective reveal under standing).
- Extended account palette with optional CaseCredit.

## 2026-01-04 v2.0
- Added treaty versioning/deprecation guidance and migration obligations + migration dockets pattern.
- Added AMEND privileged governance primitive for loud, expensive constitutional changes (epoch-boundary, docketed, migration obligations).
- Added jury service credits/sanctions pattern (optional ServiceCredit) to make duty sustainable and auditable.
- Added judicial review pattern (challenge/invalidated/stayed) with stays, docketing, and migration obligations.

## 2026-01-04 v2.1
- Added constitutional layering and Meta-Treaties to stabilize treaty interoperability (required sensitivityu sensitivity lattice, cone defaults, sealing mappings).
- Added Emergency Sunset and Renewal rules for high-power regimes (leased activation; renewal costs legitimacy; auto-revert).
- Added optional Notary Nodes and Fossil Shards pattern for scalable fossilization and portable dockets.
- Added Constitutional Court pattern as an elevated Claim Court for AMEND/treaty/meta-treaty conflicts.

## 2026-01-04 v2.2
- Added precedent/stare decisis pattern (Precedent/Cites/Overruled) and optional PrecedentDebt; extended account palette with RegretBudget.
- Added SUNSET clause sketch (surface docs) and generalized sunset governance guidance beyond regimes.
- Added Amicus Briefs pattern for third-party evidence submissions with anti-spam costs.
- Added Counterfactual Dockets + Dream Court pattern for scenario planning via WHAT IF without externalization.

## 2026-01-04 v2.3
- Added Right to Explanation pattern (reason summaries are exportable redactions; sealed reliance is listed; selective reveal available).
- Added slashing/misconduct pattern for jurors/notaries with bonded stake/credits and witnessed Slashed artifacts.
- Added optional TransparencyBudget account and governance guidance (sealing spends, revealing replenishes).
- Added optional epoch commitments in receipt headers for federated time-order accountability.

## 2026-01-04 v2.4
- Added Whistleblower Dockets pattern (sealed/escrowed reporting, protective orders, controlled reveals).
- Added Appeal Bonds and Filing Fees guidance for anti-spam filings (CaseCredit/PaperworkDebt escrow with refunds).
- Added optional TreasuryCredit and BOUNTY governance primitive for public-goods funding of audits/juries/bug-finding.
- Added Witness Liability pattern (fraud-refuted witnesses may be slashed under due process; supersession is not penalized).

## 2026-01-04 v2.5
- Added dissent/concurrence/minority report artifacts as first-class court outputs (docketable, sealable, future precedent influence).
- Added optional ComplexityBudget and statute complexity pricing guidance to make bureaucratic bloat an explicit resource.
- Added optional identity layer (pseudonyms, optional proof-of-personhood attestations, trust stake) consistent with capability-first semantics.
- Added ratification windows for staged AMEND adoption (Dream Court simulation, probationary epoch range, migration obligations, stays).

## 2026-01-04 v2.6
- Added Ephemeral Deliberation + FORGET semantics (explicit forgetting for deliberation exhaust; never for fossilized or published artifacts).
- Added Memetic Quarantine / Hazard Classes pattern to govern “contagious” knowledge with sealing, CCF defaults, and quarantine-review obligations.
- Added optional Exchange Bureau (ExchangeRate/Exchanged) and ExchangeCredit to support explicit treaty-governed cross-account conversions.
- Extended surface language grammar with FORGET clause.

## 2026-01-04 v2.7
- Added Legal Holds and Retention Policies to complement FORGET (holds block forgetting; retention is treaty/governance-defined; sunsets and witnessed release).
- Added optional StorageBudget to price retention/storage costs.
- Added Quorum Reveal mode (k-of-n approvals via duty roster to mint RevealPermit) for highly sensitive unsealing.
- Extended Memetic Quarantine with QuarantineOrdered/Lifted/Challenged artifacts, review/sunset guidance, and reason-summary expectations.
- Extended surface language grammar sketch with HOLD clause.

## 2026-01-04 v2.8
- Added Oblivion Receipts / Forget Proofs pattern (OblivionProof attestations for forgotten ephemeral payload commitments; holds block proofs).
- Added optional Governance Telemetry Dockets (signed epoch summaries of budgets/obligations/backlog) and TelemetryBudget account.
- Added Telemetry Misreport guidance (fraud-refuted telemetry witnesses may be slashed under due process).
- Extended surface language grammar sketch with TELEMETRY clause.

## 2026-01-04 v2.9
- Added Random Beacons and Lotteries pattern (commit-then-reveal civic RNG for jury/audit selection; justiciable bias disputes).
- Added Treaty Test Dockets pattern to validate treaty projections/redactions/risk labels (supports ratification and disputes).
- Added optional Timebars / Statute of Limitations pattern for courts (Timebarred/TollingGranted; protected-source-friendly).
- Added Consent-to-Receive (ACCEPT) import handshake pattern for CROSS, especially for hazards/quarantine.
- Extended surface language grammar sketch with ACCEPT and TIMEBAR clauses (best-effort).

## 2026-01-04 v3.0
- Added Proof-Carrying Governance pattern and optional ProofBudget (proof artifacts for OVERRIDE/AMEND/high-risk PUBLISH; proofs can be sealed with digests; missing proofs can block or emit ProofDue obligations).
- Added Circuit Splits and En Banc pattern to make divergent precedents explicit and governable.
- Added Dead-Man Escrow pattern (triggered escrow release/quarantine/audit with explicit renewal and obligations on fire).
- Added Bootstrapping and Self-Hosting conceptual direction (Reference Kernel as governable statute+treaty bundle).
- Extended surface language grammar sketch with PROVE and DEADMAN (best-effort).

## 2026-01-04 v3.1
- Added Treaty Fuzz Dockets pattern (RandomBeacon-seeded adversarial tests; ratification hardening; patch/migration obligations on failures).
- Added Crisis Arbitration regime preset to force convergence during constitutional crisis (auto en banc/constitutional court; probationary exports; proof requirements; accelerated legitimacy burn; short sunsets).
- Added Composting/Compaction pattern (COMPOST as governance garbage collection: shard commitments + reason summaries; notary/quorum + optional proofs; holds can forbid).
- Added PARDON governance primitive (loud debt/obligation discharge with legitimacy cost; treaty-defined unpardonable classes).
- Added Exhaustion Doctrine / Appeal Ladders pattern (ExhaustedRemedies, DeniedForNonExhaustion, FinalJudgment).
- Extended surface language grammar sketch with COMPOST and PARDON (best-effort).

## 2026-01-04 v3.2
- Added Declassification / Time-Locked Sealing pattern (DeclassifyPolicy, declass petitions, declassification events; integrates with holds/retention and optional TransparencyBudget replenishment).
- Added Jury Nullification pattern (explicit nullification artifacts; expensive, witnessed, docketed; higher-court review; non-nullifiable classes possible).
- Added Bicameral Quorum pattern (two-chamber approval for constitutional actions; ChamberVote + BicameralPassed/Failed).
- Added REPEAL privileged primitive (loud rollback of prior AMEND with ratification + migration guidance).
- Extended surface language grammar sketch with DECLASSIFY, NULLIFY, and REPEAL clauses (best-effort).

## 2026-01-04 v3.3
- Added Mootness and Advisory Opinion patterns (live controversy requirement; Dream Court for most hypotheticals).
- Added Remediation Orders and Injunctions pattern (structured repair actions, compliance reports, contempt).
- Added Phased Obligations and Milestones model integrated with the Phase Machine; added MILESTONE clause sketch.
- Added Cooling-Off Periods anti-corruption pattern (obligations preventing revolving-door incentives).
- Added Deliberation Markets pattern to allocate governance labor (audits/proofs/fuzzing/migrations) with budget guardrails.

## 2026-01-04 v3.4
- Added Impact Assessments and Blast Radius pattern for PUBLISH (ImpactEstimate/Guard/Approved; optional ImpactBudget; proofs for high-impact publishes).
- Added Delegated Standing and Representation pattern (DelegatedStanding/RevokedDelegation/ProxyFiled; scoped, sunset, treaty-restricted; abuse via bonds/slashing).
- Added Surety and Underwriting pattern for obligations (Underwrite + claim/pay/default; collateral + due-process slashing; pairs with milestones).
- Hardened Recusal with Recusal Registry and Disclosure artifacts (ConflictDeclared/Recused/Denied/Challenged/RegistryEntry; concealment fraud).
- Added Treaty Withdrawal and Secession pattern (loud exit hatch with notice windows, migration + settlement, constitutional constraints, impact accounting).
- Extended surface language grammar sketch with DELEGATE/UNDERWRITE/IMPACT/SECEDE clauses (best-effort).

## 2026-01-04 v3.5
- Added Evidence Chain / Chain-of-Custody pattern (Evidence, CustodyTransfer, tamper claims; escrow + protected-source compatibility).
- Added Standards of Proof and Burden Allocation pattern (StandardOfProof, BurdenOfProof; treaty-mapped defaults; stipulations).
- Added Restorative Justice / Reconciliation Circles track (RestorationPlan compiles to phased obligations + milestones; consent-based; failure returns to adversarial).
- Added Entrenchment and Unamendable Clauses pattern (Entrenched/Unamendable + challenge; bicameral + constitutional review; sunset-by-default).
- Added Interest/Escalation model for time-value of obligations (InterestRate/Accrued/Escalated; optional PatienceBudget).
- Extended surface language grammar sketch with EVIDENCE/STANDARD/ENTRENCH/INTEREST/RESTORE (best-effort).

## 2026-01-04 v3.6
- Added Corrections/Errata/Retractions pattern for PUBLISH (explicit edit links; loud retractions; optional right-of-reply; telemetry honesty signal).
- Added Dependencies and Compatibility Proofs pattern (DependsOn/CompatProof; border refusal/forced probation when deps unsatisfied; proofs for deps-satisfied invariants).
- Added Forks/Merges and Governance Conflicts pattern (“git for law”: ConflictSet/MergeProposal/MergeRuling; telemetry-visible debt; ratification + bicameral; crisis arbitration tie-in).
- Added Anonymity Sets and Group Witnessing pattern (threshold group witnesses with governed membership; accountability hooks via sanctions/quorum reveal).
- Added Deadlocks and Convergence Obligations pattern (DeadlockDetected -> ConvergenceDue; failure can trigger crisis arbitration; convergence funded via deliberation markets).
- Extended surface language grammar sketch with ERRATUM/CORRECT/RETRACT/DEPENDS/MERGE/ANON/DEADLOCK (best-effort).

## 2026-01-04 v3.7
- Added Settlements and Plea Agreements pattern (negotiated outcomes as docketed artifacts; compile to remediation/milestones; minimum reason summaries; abuse controls).
- Added Choice-of-Law / Conflict-of-Laws pattern (explicit bundle selection for cross-border disputes; treaty defaults; deadlock/crisis arbitration tie-in).
- Added Pilot Programs / Experimental Law pattern (impact-bounded, telemetry-visible A/B governance with sunsets; probationary border behavior; rollout guidance).
- Added Semantic Diffs and Migration Guides pattern (Diff + MigrationGuide + satisfied/failed; ties to treaty tests/fuzz and optional proofs).
- Added Livelocks and Procedural Throttling pattern (Throttle/MotionLimit/VexatiousLitigant; witnessed, reviewable; non-starvation; priced delay/spam).
- Extended surface language grammar sketch with SETTLE/CHOICE/PILOT/DIFF/THROTTLE (best-effort).

## 2026-01-04 v3.8
- Added Statistical Audits and Sampling pattern (RandomBeacon-seeded sampling audits; ConfidenceClaim; optional ConfidenceBudget; automatic escalation on failed samples).
- Added Contradiction Ledger / Paraconsistent Reasoning pattern (ContradictionDetected, InferenceSuspended, resolution; telemetry-visible debt; externalization constraints from contradictory bases).
- Added Shadow Execution and Replay Dockets pattern (simulate proposed rules on past receipts; ReplayVerified; feeds impact estimates and pilots; evidence-not-judgment).
- Added Grandfathering and Transitional Rules pattern (time-bounded compat mode with explicit end epochs; border refusal of expired transitions; ties to migration guides/tests).
- Added View Permits and Access Logs pattern (ViewPermit/ViewLogged; treaty-required logging for sensitive classes; misuse adjudication).
- Extended surface language grammar sketch with SAMPLE/CONTRADICT/SHADOW/TRANSITION/VIEW (best-effort).

## 2026-01-04 v3.9
- Added Hold Review and Habeas Petitions pattern (challengeable holds/quarantines/seals; scheduled review; uphold/modify/lift; emergency narrowing must sunset + postmortem).
- Added Palimpsest Forgetting pattern (forget payload but retain governed summaries/stats; non-reconstructive policy; admissibility doctrine; optional ConfidenceBudget for claims).
- Added Statute Linting and Hygiene pattern (LintPolicy/LintReport/LintWaived; CI checks for complexity, sunsets, deps, contradictions, missing migration guides; expensive waivers).
- Added Red Team Dockets / Adversarial Drills pattern (RedTeamExercise/ExploitReport/PatchAccepted/BountyAwarded; safe harbor; sealing-respecting severity; auto-trigger holds/probation/crisis on high severity).
- Added Canonicalization and Normal Forms pattern in Canonical Invariants (CanonicalForm/Policy/Mismatch; border refusal on mismatch; ties to self-hosting render versions and correction traceability).
- Extended surface language grammar sketch with HABEAS/PALIMPSEST/LINT/REDTEAM/CANON (best-effort).
