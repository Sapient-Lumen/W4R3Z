# Ministry of Many Worlds

## Explore several plans without multiplying the right to act

Ministry of Many Worlds imagines a programming language for work that must explore alternatives, spend limited resources, cross boundaries and explain its decisions. A plan may be useful without being authorized. A simulation may be reversible while a message sent outside it is not. Two branches may share information without each acquiring a fresh copy of the same spending power.

The draft makes those distinctions part of execution rather than comments beside a program. Its “ministry” is an elaborate language of forms, treaties, courts and receipts, but the underlying proposal is concrete: scoped rewriting, conserved resources, explicit effects and inspectable histories. The bureaucratic vocabulary gives branching computation an institutional imagination, including disagreement, appeals, emergency powers and the cost of maintaining the machinery itself.

The supplied [v3.9 specification](versions/v3.9/files/SPEC.md) is dated 4 January 2026. It is a substantial language-design work, accompanied by [exploratory notes](versions/v3.9/files/NOTES.md) and a [revision account](versions/v3.9/files/CHANGELOG.md), not a delivered interpreter. Read the core first; the many optional institutions are extensions of it, not prerequisites for every useful program.

## A rule changes a world and accounts for the change

The [core model and transactional rewrite](versions/v3.9/files/SPEC.md#1-core-model) treat state as a multiset of immutable “molecules”: facts, work items and messages located within branch, cell, node and epoch scopes. A rule matches some molecules and produces others. Unlike an unconstrained rewrite, its firing must also balance designated conserved accounts, emit a receipt and attach an undo lease.

Ordinary data and authority are different kinds of things. Copying a form describing a restart does not mint permission to restart a service. Capabilities are opaque permits; resource tokens represent quantities the chosen policy conserves. The ledger is therefore not merely a log written after the action. Its balance is a condition of a valid transition.

Outputs may carry origin handles pointing to the receipt and output slot that produced them. That makes a later question about a result traceable to the steps it depends on. A header can travel while sensitive payload remains sealed. The program can expose that a decision occurred, the rule and scope involved, and the budget changes without exposing every input.

Each step must also decrease a well-founded potential, spend a finite budget, or produce a terminal committed/stuck artifact. This is the draft's progress discipline: a busy computation should have to account for what its activity accomplishes or consumes. A full termination argument would still need the selected scheduling and budget rules; naming a potential does not supply that proof.

## Branch facts, not unlimited resources

The [fork and merge rules](versions/v3.9/files/SPEC.md#42-fork-branching-search) give “many worlds” its practical meaning. A program can explore competing plans, but it cannot make each plan independently rich by copying the same authority or budget.

A divisible resource can be split between branches. An indivisible permit can instead be represented by an allocation reference whose use produces a spent marker. Merge must reconcile those markers: if one branch spent the allocation, the merged state records that expenditure; if both spent it, the draft requires an explicit double-spend conflict, either a stuck result or an adjudication with a witness and refutation of the losing spend. Silent reconciliation is not allowed.

Ordinary facts may merge or cancel under the chosen interference rules. Evidence and receipts do not disappear merely because their branches lose. Nor may cancellation remove an inherited obligation to redact information derived from a restricted source. The distinction lets alternatives be simplified without making their inconvenient history vanish.

This is not quantum execution. The draft leaves the interpretation of interference weights open: probability, credence and policy-driven weights are among its unresolved choices. Its concrete contribution here is the obligation to say what can be combined, what can be spent, and what a conflict requires.

## A border specifies what becomes visible

[“Treaties as types”](versions/v3.9/files/SPEC.md#56-treaties-as-types-normative-interpretation) recasts an interface as a controlled projection. For each kind of molecule, a treaty specifies which fields may cross in clear form and which must be omitted, summarized or sealed. Crossing a boundary is therefore not just moving the same object to a new address: it checks what the recipient may receive and produces a stamp and receipt.

This makes interface design and information flow meet. A result derived from restricted inputs cannot become freely exportable just by changing its label or merging it with another result. Its origin lineage still matters. Treaty versions, migration obligations and test dockets extend that idea to changing interfaces: an export should identify the contract under which it was projected.

The notes make the analogy explicit: a type error becomes a customs rejection. That is a proposed discipline for an implementation, not a proof that the sketch already prevents every information leak. Its usefulness is in forcing the interface to describe observation as well as structure.

## Undo ends where another participant can rely on the effect

[Externalization](versions/v3.9/files/SPEC.md#12-externalization-cones-normative) is the decisive boundary. An unfossilized internal experiment can be undone within its lease. Publishing an artifact, sending outside the governed system or writing a real file commits relevant history so a local rollback cannot pretend the external effect never happened.

The draft offers two policies. A minimal dependency set fossilizes the receipts sufficient to justify the exported artifact. A causal cone fossilizes the entire backwards-reachable history through origins and consumed molecules. The first aims to preserve more room for revision; the second freezes more history at potentially much greater cost. Accurate dependency tracking is essential to either policy's meaning.

After fossilization, correction becomes a new compensating transaction linked to the old receipts. It records a replacement effect and a witness rather than erasing the earlier event. This is a model of accountable correction, not a promise to reverse physical consequences.

Time itself does not roll back. That choice prevents a branch from restoring an old clock merely to recover an expired undo window. Federation gossip is distinguished from external publication, but a deployment that treats a gossip channel as external must apply the stronger publication semantics there too.

## Follow one incident through the language

The specification's [reference story](versions/v3.9/files/SPEC.md#26-end-to-end-reference-story-informal) begins with reports of a latency spike. Nodes accumulate votes; a quorum issues a mitigation permit. Exploration forks remediation plans with divided budgets. A choice selects a plan with a witness, and the commit phase crosses from quarantine toward production under the applicable border rules.

That example joins the design's pieces. Observing a problem is not permission to change production. Exploring ten responses is not ten times the authorized budget. Choosing a response is not yet an external effect. Once the response is published, a later correction must acknowledge what already happened.

The [query interface](versions/v3.9/files/SPEC.md#61-core-queries) then asks three different questions. WHY follows the evidence for a result or permission. WHY NOT identifies blocking capabilities, budgets or phase conditions. WHAT IF opens a controlled alternative under changed assumptions. Answers are intended to be reusable artifacts, not only console prose. Counterfactual dockets can preserve the assumptions and predicted obligations of a hypothetical without turning it into an instruction to act.

These are promising ingredients for a workflow engine, incident-response simulator or experimental policy language. The incident is a design walkthrough, not a report of a deployed federation.

## Obligations survive handoff, and disagreement survives a verdict

The [obligation model](versions/v3.9/files/SPEC.md#72-obligations-creative-primitive) makes future work part of current state. An emergency override can create a postmortem due at a specified epoch. Publication can create an audit obligation. Delegating that work preserves its identifier and deadline; discharge requires evidence rather than merely changing the assignee.

The [supersession account](versions/v3.9/files/SPEC.md#15-supersession-lattice-rulings-and-evidence-evolution) similarly preserves changes of judgment. Witnesses can be superseded or refuted through explicit relations. A query determines the current admissible ruling instead of overwriting a Boolean and losing the disagreement. Claims and denials may coexist while the rules constrain which ruling can support an action.

“Current truth” in this idiom means the status derived under a jurisdiction's admissibility and supersession rules. It does not make an authorized ruling true of the world. Dissent, minority reports and later challenges remain useful precisely because a binding decision and a justified belief can come apart.

## Keep the lessons without keeping everything

The work does not simply demand an ever-growing archive. [Ephemeral deliberation and FORGET](versions/v3.9/files/SPEC.md#33-ephemeral-deliberation-and-forget-creative-useful) distinguish exploratory residue from evidence required to justify a published result. Forgetting may remove ephemeral content or its local keys while retaining a header-visible account of what was forgotten; it must not rewrite fossilized or published history.

Holds constrain forgetting, but v3.9 adds procedures to challenge holds, quarantines and seals rather than treating indefinite retention as automatically justified. Its final palimpsest-forgetting proposal keeps a governed summary or selected statistics after raw material is discarded. Whether that residue is non-reconstructive, and what claims it can support, remain obligations for the chosen method and evidentiary policy, not properties obtained by calling it a palimpsest.

The [changelog](versions/v3.9/files/CHANGELOG.md) makes this expansion legible: the early rewriting kernel acquires externalization rules, obligations, institutional disputes, forgetting and finally review, linting and canonical forms. These are the document's recorded revisions, not separately supplied running releases.

## The cost of making every exception explicit

The optional institutions are more than decorative names. An emergency regime changes deliberation and finality; an override spends named budgets and generates review work; an amendment creates migration obligations. High-power regimes must expire unless renewed with fresh quorum authorization; an expired regime must revert to a lower-power one. The design tries to prevent extraordinary power from becoming an invisible shortcut. It also recognizes procedural overload through complexity budgets, throttling and minimum-service requirements.

There is a serious tension here. A language can record that an override consumed “legitimacy” without establishing that the override was legitimate. Charging for an appeal can limit spam and also exclude someone who needs review. A minimum-service clause needs an allocation mechanism that actually delivers service. These questions concern the substance of the rules, not merely their successful execution.

The [open design questions](versions/v3.9/files/SPEC.md#28-open-design-questions-deferred) still include molecule matching, scope naming, allocation representation, interference weights, scheduling and surface syntax. Some later sections remain placeholders or grammar additions. A productive continuation could implement and test a small kernel plus one worked workflow before adopting the whole institutional vocabulary. The notes propose a host-language runner and a deterministic compilation profile for that reason: ordinary reproducible tooling should not require every exotic feature at once.

Read beside [Lacuna](../Lacuna/README.md) for the different problem of keeping fictional possibilities and accepted history distinct, [Radical Governance](../Radical-Governance/README.md) for contestable institutions, and [Micromax](../Micromax/README.md) for a language/editor project with a different implemented surface. MMW's particular invitation is to imagine computation in which alternatives, permissions and obligations remain visible together.

## Version shelf and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [v3.9](versions/v3.9/README.md): 3 preserved members; `mmw_spec_2026-01-04_v3.9.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
