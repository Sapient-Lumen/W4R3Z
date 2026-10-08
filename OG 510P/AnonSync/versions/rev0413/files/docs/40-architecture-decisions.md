## Revision addendum — architecture decisions from nested overlap and bridge-host work

1. Overlap is a first-class topology object.
2. Parent and child subjects retain separate membership graphs even when one path contains the other.
3. Bridge-host carriage is modeled explicitly whenever one host belongs to both subjects.
4. Duplicate indexing / rescanning cost is part of overlap state, not derived only at runtime.
5. Overlap may be blocked by posture incompatibility such as placeholder/selective weakness.
6. Receipts preserve the blocked audience-isolation overstatement.

## Revision addendum — architecture decisions from resource-budget and starvation work

1. Resource budget is a first-class domain object with typed lanes.
2. Every meaningful rate, floor, or priority must carry provenance.
3. Scheduler pauses, fairness bias, hard caps, and runtime pressure are separate mechanisms.
4. Queue ordering shown to humans is not trusted as scheduler truth unless explicitly proven.
5. Starvation and preemption are reviewable hazards, not incidental side effects.
6. Bottleneck diagnosis must emit a claim ceiling and rejected alternatives.

## Revision addendum — architecture decisions for raw-state clone boundaries and successor import

New decisions locked here:

1. the system models **state adoption source class** as first-class state
2. the system models **seat lineage** and **subject-state carry-forward** as separate axes
3. reviewed replacement uses a first-class **successor capsule** object rather than opaque state copying
4. **concurrent duplicate-seat risk** is a blocking architectural class, not merely a warning tier
5. receipts preserve the **blocked same-seat-overstatement** whenever raw copies or stale backups are involved

**Why:** Current official Resilio docs are candid that cloning is unsupported, that storage contains real configuration/database state, and that each installation has its own certificate-backed identity. Those truths are valuable; the operator contract is still too blunt.

## Revision addendum — architecture decisions for invocation profile

New decisions locked here:

1. the system models **invocation profile** as first-class state
2. the system models **world lineage**, **visibility posture**, and **control-exposure posture** as separate launch-time axes
3. state-root selection compiles to an explicit **world-authority class** rather than an incidental path string
4. hidden/minimized/service/headless starts are architecturally valid but must not weaken stop-proof semantics
5. receipts preserve the **actual world opened**, the **requested intent**, and the **stronger rejected sentence**

**Why:** Current Resilio docs are candid that launch flags, storage roots, loopback-vs-LAN WebUI, service accounts, and same-parameter relaunch discipline materially change runtime truth. Those distinctions are valuable; the scattered explanation path is not.

## Revision addendum — architecture decisions after rev0308: requester identity model

This pass locks in the following architecture decisions:

1. the requester model must contain distinct fields for **human label**, **device label**, **canonical proof handle**, and **family association**
2. trust memory must key off a reviewed handle bundle, not any display label alone
3. family association may support widening decisions, but may not collapse seat-specific proof into family-wide proof
4. receipts and approval-memory records must preserve both the trusted scope and the stronger rejected sentence

These are not just copy or UI decisions; they affect data model, approval cache design, receipt schema, and every future arrival/claim/review flow.

## Revision addendum — architecture decisions for time authority

New decisions locked here:

1. the system models **time authority** as first-class state
2. the system models **disk-visible timestamp** and **ledger-authoritative timestamp** as separate axes when needed
3. every chronology-sensitive workflow stores a **skew budget** and **confidence class** snapshot
4. replay / restore flows depend on explicit **winner forecasts** rather than implicit file-copy semantics
5. receipts preserve the **trusted time basis**, **divergence snapshot**, and **stronger rejected sentence**

**Why:** Current Resilio docs are candid that file ordering depends on GMT-normalized `mtime`, that skew is budgeted, that disk `mtime` can be wrong while the database carries the correct time, and that archive replay can fail if chronology is wrong. Those truths are valuable; the scattered explanation path is not.

## Revision addendum — architecture decisions for completion/freshness truth

New decisions locked here:

1. the system models **completion horizon** as first-class state
2. the system models **freshness proof** separately from transfer quiet or UI success state
3. **offline debt**, **peer aging**, and **hidden-work debt** are stored as first-class proof weakeners
4. observational aids such as `last transferred` remain **evidence inputs**, not final truth classes
5. receipts preserve the **horizon snapshot**, **proof ceiling**, and **stronger rejected sentence**

**Why:** Current Resilio docs are candid that green state is relative to connected peers, that peer aging changes visible membership, that hidden work can continue, and that detection latency matters. Those truths are valuable; the scattered explanation path is not.

## Revision addendum — architecture decisions for permission metadata

New decisions locked here:

1. the system models **byte truth** and **metadata truth** as separate but related state axes
2. metadata policy compiles to an explicit **metadata authority class** rather than one boolean flag
3. **runtime principal** and **identity mapping mode** are stored as first-class proof objects when metadata is in scope
4. non-native targets may publish **preserve-only** without overclaiming **native apply**
5. receipts preserve the **metadata apply ceiling** and the **stronger rejected sentence**

**Why:** Current Resilio docs are candid that permission metadata is real, that runtime principal and target mapping determine what can actually be applied, and that some targets preserve metadata without native enforcement. Those truths are valuable; the scattered explanation path is not.

## Revision addendum — architecture decisions for typed removal

New decisions locked here:

1. the system models **removal verb family** as first-class state
2. remove-like actions declare their **mutation planes** explicitly
3. every removal stores **survivor and residue truth**
4. reconnect, reappearance, and reinstall are modeled as **reopen triggers**, not accidental side stories
5. receipts preserve both the **strongest safe sentence** and the **stronger rejected sentence**

## Revision addendum — architecture decisions for transfer eligibility

New decisions locked here:

1. the system models **eligibility lanes** separately from runtime state
2. transfer-related gates are typed as either **policy** or **context**
3. every blocked or reduced state carries an optional **wake witness**
4. receipts preserve both the **strongest safe sentence** and the **stronger rejected sentence**
5. mixed states are architecturally valid and must be representable without status abuse

## Revision addendum — shared-substrate architecture after rev0296

**Decision:** represent storage substrate, runtime identity, path namespace, notification grade, and write-lane boundary as one first-class substrate object.

**Why:** Current Resilio docs are candid that SMB shares, service-visible UNC paths, mapped-drive aliases, lock contention, and missing notifications materially change what the product can promise. Those truths are valuable; the article archaeology is not.

**Therefore:**
- the state model separates `storage_class`, `runtime_identity`, `authoritative_path_namespace`, and `notification_floor`
- write-lane authority is declared explicitly rather than inferred from the last used path alias
- lock contention is modeled as a first-class blockage object
- mixed direct-plus-mediated writer topologies can be blocked as invalid, not merely warned after the fact
- receipts preserve degraded detection truth and forbidden stronger claims

## Revision addendum — activation-class and proof-of-effect architecture after rev0294

**Decision:** represent every meaningful settings or policy mutation as a first-class activation object with explicit route, trigger, proof class, and retroactivity boundary.

**Why:** Current Resilio docs are candid that some changes become real only after reread, rescan, restart, or later observation, and that some rules are future-only rather than retroactive. Those truths are valuable; the article archaeology is not.

**Therefore:**
- the state model separates `saved`, `live`, and `proven`
- each mutation carries `activation_class`
- verification stores `proof_class` and `coverage`
- future-only / non-retroactive scope is public
- supersession does not erase earlier receipts


## Revision addendum — architecture decisions after rev0293: edge-mutation state is modeled, not implied

Architecture decision added by this tranche:

### ADDED — automatic ingress mutation and lease truth are first-class state objects

AnonSync will model, persist, and expose at least:

- requested edge-mutation posture
- effective listening-port basis
- last observed mapping status
- freshness / staleness of mapping evidence
- accepted infrastructure-risk acknowledgement
- receipt supersession triggers

Rationale:
Current Resilio docs are candid that auto-mapping exists, that it can matter materially for directness, and that it can even affect other network equipment; the missing piece is not substance but owned state.
AnonSync therefore treats router-mutation truth as modeled product state rather than checkbox implication.

## Revision addendum — architecture decision after rev0287: compile authority artifacts and rotation forks into first-class objects

Decision:

- portable authority artifacts and their successor forks must compile into first-class inspected objects rather than raw opaque strings plus help-article lore

Why:

- current official Resilio material still shows that token family, approval path, and continuity consequences are real but partially hidden inside key prefixes, hash fragments, and separate flow articles
- carrier changes should not change semantics, which means semantics need an object separate from carrier
- rotation can leave old cohorts live, so successor issuance is continuity governance rather than mere regeneration

Implications:

- create a `capability_artifact` object
- create an `artifact_issuance_preview` object and `artifact_issuance_receipt` object
- create an `incoming_artifact_intake` object
- create an `artifact_rotation_fork_review` object preserving old cohort evidence, successor epoch, and retirement order
- require all projections to render artifact family, ceiling, approval path, and fork-risk explicitly rather than reconstructing them from token text

Rejected alternative:

- treat links/keys/QR as mostly equivalent carriers, keep semantics implicit, and handle rotation as a background refresh

Reason rejected:

- that would recreate exactly the token-opacity and silent-fork contract the archive is explicitly refusing to clone


## Revision addendum — architecture decision after rev0285: compile dangerous-session continuity, salvage export, and destructive tickets into first-class objects

Decision:

- dangerous browser/service workflows must compile into first-class context, preservation, and execution objects rather than page-local state

Why:

- current official Resilio material still shows that dangerous-control meaning can depend on install path, service/browser route, product line, trust bootstrap, and per-surface destructive controls
- dangerous meaning collapses if context must be reconstructed from browser tabs or remembered earlier review
- final destructive authority becomes too durable if it is stored only as barrier acceptance rather than a freshness-bound execution object

Implications:

- create a `danger_session_capsule` and `danger_review_context_rail` object
- create a `salvage_export` object and `salvage_export_receipt` object
- create a `destructive_execution_ticket` object that binds endpoint, seat, trust grade, reviewed loss basis, salvage basis, and invalidators
- require destructive commit to consume the ticket instead of reusing ambient browser/session continuity

Rejected alternative:

- keep dangerous-session continuity in the client, let export remain a side action, and treat barrier approval as enough until the page is refreshed

Reason rejected:

- that would recreate exactly the sticky-danger folklore and remembered-browser-consent contract the archive is explicitly refusing to clone


## Revision addendum — architecture decision after rev0284: compile destructive approvals into first-class review and receipt objects

Decision:

- serious destructive actions must compile into first-class server-side review, approval, and receipt objects rather than UI-local toggles or remembered warning acknowledgements

Why:

- current official Resilio material still shows that one destructive-heal answer can depend on product line, deployment mode, endpoint exposure, archive-bearing locality, and loss/salvage classes
- destructive meaning collapses if endpoint authority, loss preview, salvage viability, and approval text are not preserved together
- later `nothing important was lost` folklore becomes too easy if the authoritative record is only a setting flip or transient dialog acceptance

Implications:

- create a `destructive_review_shell` object with endpoint, seat, action, loss classes, salvage ladder, and safe-language ceiling
- create a `destructive_approval_barrier` object with explicit approval sentence, blocking checks, waiver rows, and commit lineage
- create a `destructive_action_receipt` object with execution facts, preserved remnants, waived loss, and supersession boundary
- require every projection to render these compiled objects rather than reconstruct them from ambient state

Rejected alternative:

- keep destructive actions as page-local preferences plus warning modals and let receipts be inferred from later history rows

Reason rejected:

- that would recreate exactly the destructive-toggle folklore and cross-page archaeology the archive is explicitly refusing to clone

## Revision addendum — architecture decision after rev0276: quiet-cohort coverage is a first-class object

The archive now needs one more explicit architecture rule:

- quiet-dependent operations must compile into a cohort-coverage object, not just a local pause state

At minimum the system should preserve:

- target subject and operation intent
- target seat cohort and seat relevance basis
- per-seat requested stop class
- matched / unresolved / excluded seat status
- residual mover classes still outside coverage
- strongest allowed sentence and stronger rejected sentence
- reopen triggers for the quiet claim

A local pause may still be useful, but it must not silently widen into shared stillness without a first-class quiet-cohort object.
## Revision addendum — architecture decision after rev0275: stale return must compile into a first-class re-entry case

Decision:

- serious post-dormancy return must be represented as an explicit re-entry case, not as a loose combination of presence badges, peer-aging state, warning rows, and remembered history

Why:

- current official Resilio docs still show that one honest return answer can depend on restart/reopen chronology effects, peer-expiration policy, hidden-device behavior, clock validity, and live source reality
- stale-return meaning collapses if dormancy facts, roster-return class, chronology confidence, and source-reality verdict are not preserved together
- normality language collapses if a seat can look visible again before it has earned ordinary trust again

Implications:

- create a `reentry_case` object with dormancy interval, return class, roster state, chronology confidence, and source-reality verdict
- create a `dormancy_timeline` object with last-good witness, hide/expiry rows, return events, and current interpretation
- create a `stale_return_review` object with chronology-risk rows, source/announcement rows, safe action ladder, and rejected stronger sentence
- create a `reentry_receipt` object with safe current sentence and reopen triggers

Rejected alternative:

- keep visibility, peer aging, clock warnings, and no-source symptoms as separate surfaces and let operators synthesize re-entry truth mentally

Reason rejected:

- that would recreate exactly the stale-return folklore and accidental overtrust this archive is explicitly trying not to clone

## Revision addendum — architecture decision after rev0269: compile speed investigations into explicit experiment objects

Decision:

- serious performance diagnosis must be represented as explicit experiment objects, not as a loose mix of telemetry views, external commands, and remembered tuning attempts

Why:

- current official Resilio docs still show that one honest speed answer can depend on live Sync telemetry, hidden internal-task state, power-user configuration, and an external iperf3 run with Sync shut down
- benchmark meaning collapses if quiescence, direction coverage, and baseline comparison are not preserved
- intervention safety collapses if topology/security-affecting changes are proposed without an explicit hypothesis review

Implications:

- create a `measurement_plan` object with question class, baseline observation, peer pair, quiescence requirements, and comparison rules
- create a `benchmark_run` object with row ledger, commands or helper actions, outputs, anomalies, and validity verdict
- create a `performance_hypothesis_review` object with supported interventions, cost classes, and revert plans
- create a `measurement_receipt` object with supported capacity/bottleneck statement, next safe step, and reopen triggers

Rejected alternative:

- keep live graphs in-product but leave network-isolation benchmarking and tuning interpretation to help-center articles or support ritual

Reason rejected:

- that would recreate the same benchmark folklore and tuning folklore this archive is explicitly trying not to clone

## Revision addendum — architecture decision after rev0268: keep a diagnostic-posture ledger separate from evidence packets

### Decision

AnonSync should model temporary diagnostic posture in a dedicated ledger that is separate from, but linkable to, evidence packets and export receipts.

### Why

Current Resilio docs make clear that capture quality can depend on runtime deltas such as enabled debug logging, enlarged log buffers, profiler activation, restart completion, and retention rules.
Those facts belong to system state, not merely to support prose.

### Architectural consequences

- evidence packets should reference the posture receipt active during their capture window
- hidden and advanced activation routes must still emit the same state-change events as visible controls
- baseline values and restored values must be preserved, not overwritten by the latest state snapshot
- residue and cleanup facts must survive even after settings return to baseline
- a packet may be complete while restoration remains incomplete; architecture must keep those truths separate

### Anti-clone rule

Do not let packet manifests impersonate instrumentation truth.
The product needs one explicit posture chain: plan -> change review -> restore review -> posture receipt.

## Revision addendum — architecture decision after rev0266: compile recipient asks and fulfillment verdicts server-side

Architecture should now treat **recipient asks** as first-class server-side objects rather than inferred reply-thread annotations.

Inputs to the compiled ask verdict should include at least:

- incident identifier
- requester lane and audience class
- ask clauses and required/optional posture
- binding token candidates
- allowed return lanes
- candidate manifest version
- clause coverage verdicts
- excess-disclosure findings

The client may render this verdict in different ways, but it should never have to reconstruct ask meaning from freeform reply prose, ticket numbers, or portal habits.

## Revision addendum — architecture decision after rev0265: persist companion-case identity separately from lane receipts

Architecture should now treat **companion-case identity** as a first-class object, not just a pair of loosely related lane receipts.

Inputs to the compiled companion verdict should include at least:

- incident identifier
- public artifact reference if any
- private artifact reference if any
- audience class for each artifact
- withheld-detail categories
- linkage basis and confidence
- continuation lane and reopen triggers

The client may render this verdict in different ways, but it should never have to reconstruct the relationship from ticket numbers, pasted URLs, or remembered prose.

## ADR addendum after rev0264 — compile escalation-lane truth server-side

**Decision:** Architecture will compile every outbound-help route from an explicit lane object rather than infer it from a button or page family.

**Why:** Current official Resilio docs still show that route validity depends on product line, entitlement, issue class, and audience, while visible surfaces can still suggest `Submit Customer Service Request`, forum/help-center self-service, billing/licensing web forms, and in-app `Contact support` at the same time. A trustworthy product should not let the client guess whether `send` means public summary, private ticket, billing request, peer handoff, or local-only save.

**Consequence:** clients may render lane pickers differently, but they must all bind to the same server-side lane record with entitlement basis, audience class, package-fit verdict, response ceiling, and redirect/reopen boundary.


## Revision addendum — architecture decision after rev0263: compile evidence plans and manifests server-side

Decision:

- diagnostic incidents must own a reviewed **evidence plan** and a versioned **evidence manifest** before outbound package export is considered complete

Why:

- current support articles already show that artifact family, platform route, and capture precondition materially change package meaning
- delivery state is weaker than package interpretation
- later operators need one durable object that says what the package was meant to answer and what actually traveled

Implications:

- exported packages must record the evidence plan version and manifest version they used
- capture rows must preserve route, prerequisite, disruption level, and return state
- delivery receipts must never be allowed to stand in for diagnostic sufficiency on their own

## Revision addendum — architecture decision after rev0262: capture runs must bind to structured briefs and event anchors

Decision:

- every serious evidence run must bind to a versioned **incident brief** and may optionally bind to a versioned **symptom bookmark**

Why:

- support articles already show that role, timestamp, and affected-subject context are required to interpret artifacts
- capture dwell and send completion do not prove that the target symptom was actually caught
- later operators need one durable object that says what event the packet was meant to represent

Implications:

- exported packets must record which brief version and which bookmark they inherited
- run receipts must preserve `caught`, `partial`, `no-repro`, and `capture-failed` as distinct states
- evidence interpretation must never assume that a packet explains the leading symptom unless the run receipt says the window was usable for that symptom

## Revision addendum — architecture decision after rev0261: incidents own participant scope and evidence duty

Decision:

- diagnostic incidents must own a reviewed **witness set** object whenever the current question depends on more than one participant

Why:

- troubleshooting articles already show that some incident classes are pairwise while others are share-wide
- returned packets are weaker without explicit participant roles
- completeness and contradiction math require a declared participant set, not just artifact blobs

Implications:

- evidence bundles must record which participant each artifact came from
- completeness review must compare returns against required witnesses, not merely count files
- escalation packets must be able to say whether current witness coverage is complete, partial, or intentionally narrow

## ADR addendum after rev0260 — compile diagnostic incident continuity server-side

**Decision:** Architecture will compile every serious investigation into a first-class diagnostic-incident object with stable identity, entry point, ranked explanations, evidence references, unresolved gaps, and conclusion receipts.

**Why:** Current official Resilio docs still show diagnosis spread across row clicks, history search, peer/queue inspection, and later log-gathering rituals. A trustworthy product should not require the client or the operator to reconstruct the investigation narrative from disparate surfaces.

**Consequence:** clients may render different workbench or receipt layouts, but they must all bind to the same server-side incident, timeline, sufficiency verdict, and conclusion record.

## ADR addendum after rev0257 — visible state tokens must compile from origin plus matrix, not from label alone

**Decision:** Architecture will compile every durable visible state token from an explicit origin record plus an explicit signal matrix, and will reject reuse of one token across different matrices unless the rendered token is qualified or the semantic-stability verdict is `true`.

**Why:** Current official Resilio docs still let `Paused` mean a selective manual matrix in one place and a scheduler-origin matrix with different documented outbound semantics in another, while deletions and indexing continue under the same friendly word. An inspectable product should not let label text outrun the active lanes.

## ADR addendum after rev0256 — replay class deserves explicit architecture status

**Decision:** Persist replay class as a first-class computed object, not an inferred transport footnote.

**Why:** Current Resilio docs still show that changed-file replay meaning varies across piecewise resend, piece-shift whole-file fallback, stronger diff-delta lanes, and policy-driven full resend. One performance adjective is therefore not enough.

**Consequence:** any surface that claims `incremental`, `delta`, or `changed parts only` must bind to a replay-class record with fallback ceiling, evidence strength, and unavailable-stronger-class explanation.

## Revision addendum — architecture decision after rev0250: compile permission-plane authority and apply truth server-side

Architecture should now treat **permission-plane truth** as a compiled server-side fact, not a client-side inference.

Inputs to the compiled verdict should include at least:

- subject and epoch
- configured permission mode
- authority basis and reference-seat lineage if any
- seat-local substrate compatibility
- seat-local privilege grade and missing rights
- local re-inheritance basis if used
- deferred-apply basis if used
- compare-participation rule
- strongest safe sentence and stronger forbidden sentence

The client may render this verdict in different ways, but it should never have to derive `are permissions really being preserved here, and by whose authority?` from raw job-profile flags, runtime account hints, and pre-seeded-folder caveats on its own.

## Revision addendum — architecture decision after rev0238: compile bind-right and adoption verdict server-side

Architecture should now treat **arrival bind truth** as a compiled server-side fact, not a client-side inference.

Inputs to the compiled verdict should include at least:

- seat-wide future-arrival scope
- default root/template and provenance
- current share continuity class
- suggested path and suggestion source
- current target occupancy
- lineage/adoption evidence grade
- duplicate-namespace risk
- whether standing defaults were mutated during review

The client may render this verdict in different ways, but it should never have to derive `can I safely bind this share here?` from raw mode bits, folder names, and warning strings on its own.

## Revision addendum — architecture decision after rev0237: sync mode is a composite object, not one field

Decision:

- represent sync mode as a first-class composite object keyed by seat, subject-or-scope, and review surface
- record **current-share posture**, **future-arrival default**, **byte posture**, **path basis**, and **return contract** separately rather than flattening them into one `mode` field
- bind receipts and claim ceilings to mode events so later surfaces can explain aftermath without re-parsing mobile, linked-device, and reconnect state

Rationale:

Current Resilio docs still show that `Disconnected`, `Selective Sync`, `Synced`, placeholder conversion, default connect mode, and reconnect path proposal all change different truths. AnonSync should therefore not encode mode as an overloaded label.

## Revision addendum — architecture decision after rev0235: status claims must compile from windowed evidence

Another cross-cutting decision now belongs in the archive:

- status-bearing UI values are not raw presentation garnish; they are compiled claims whose metric family, time window, and scope must be explicit in the product model

Consequences:

- a status row must be decomposable into live, historical, and threshold-driven fields
- timestamps must declare their event family rather than reusing one generic time slot
- safe language generation must read claim ceilings from metric objects, not from row styling alone
- receipts must preserve reviewed interpretation when a row participates in a consequential decision

## Revision addendum — architecture decision after rev0231: compile control-endpoint attestation server-side

Architecture should now treat **control-endpoint attestation** as a compiled server-side fact, not a browser-only inference.

Inputs to the compiled verdict should include at least:

- runtime identifier
- storage root identifier
- config path identifier if any
- endpoint bind / listen tuple
- audience/auth/transport grade
- seat-lineage verdict
- browser residue findings when known
- recent endpoint-switch or recovery mutations
- control-target confidence and strongest safe sentence

The client may render this verdict in different ways, but it should never have to derive endpoint identity from raw ports, URLs, or cookie state on its own.

## Revision addendum — architecture decision after rev0229: compile winning-rule provenance server-side

Architecture should now treat **policy provenance** as a compiled server-side fact, not a browser-only inference.

Inputs to the compiled verdict should include at least:

- subject and scope
- effective rule value
- origin surface
- ordered override chain
- shadow residue
- authoritative edit surface
- required apply boundaries (restart / reconnect / reload / relaunch)
- future-only versus immediate effect scope

The client may render this verdict in different ways, but it should never have to derive rule authority from scattered raw flags on its own.

## Revision addendum — architecture decision after rev0228: compute control grade server-side

Architecture should now treat **control-surface grade** as a compiled server-side fact, not a browser-only interpretation.

Inputs to the compiled verdict should include at least:

- current listener scope
- active control modality
- auth source and floor
- transport posture
- certificate origin / trust class
- browser residue findings when known
- fallback control route availability
- collateral class of the last recovery mutation

The client may render this verdict in different ways, but it should never have to derive it from raw flags on its own.

## ADR addendum after rev0222 — recovery durability is a typed horizon, not a support-side retention caveat

Architecture should now treat recovery durability as a structured object.

**Decision:** Persist typed horizon fields for byte witnesses, event witnesses, access reach, capture exclusions, and next expiry cliffs; emit horizon receipts for reviewed cleanup, preservation, and retention mutations.

**Why:** Current official Resilio docs still split recovery durability across Archive TTL, History window, platform access, hidden `.sync` placement, and uninstall cleanup caveats. An inspectable product should not make operators reconstruct that half-life from scattered settings and support prose.

## ADR addendum after rev0221 — recovery witness locality must stay separate from restore intent

**Decision:** Keep witness-seat location, executed recovery host, actor evidence source, and recovery shape as separate public objects.

**Why:** Current Resilio docs still make operators combine Archive notes, rename behavior, History UI, and runtime timing caveats to understand one ordinary recovery story. AnonSync should publish that story directly.

The architecture should now treat four distinctions as non-negotiable:

1. **prior bytes exist somewhere** is not the same object as **this acting seat can recover them**
2. **witness seat** is not the same object as **executed recovery host**
3. **archive byte evidence** is not the same object as **history actor evidence**
4. **exporting recovered bytes** is not the same object as **replaying them into live distributed state**

If the object model fuses these distinctions, the interface will drift back toward the exact Resilio-style archaeology the archive is trying to avoid.

## Revision addendum — architecture decision after rev0220: quiescence is a first-class typed state

Architecture should now treat quiescence as a structured object rather than a boolean toggle.

Minimum fields:

- target object
- requested phrase
- effective stop class
- per-phase verdicts
- strongest safe sentence
- forbidden stronger sentence
- stronger next action ladder
- receipt/audit linkage

This prevents GUI, local-web, TUI, and CLI projections from inventing their own incompatible meanings for `paused`.

## Revision addendum — opaque custody, recovery proof, and encrypted history ceilings must stay separate after rev0211

The architecture should now treat four distinctions as non-negotiable:

1. **target path exists** is not the same object as **target is safe for ciphertext admission**
2. **ciphertext bytes present** is not the same object as **plaintext can be produced on this node**
3. **saved RW secret exists** is not the same object as **database continuity still makes recovery honest**
4. **encrypted Archive contains history** is not the same object as **this node can replay deletion back into the live subject**

If the object model fuses these distinctions, the interface will drift back toward the exact Resilio-style caveat archaeology the archive is trying to avoid.

## Revision addendum — target volume capability and metadata fallback must stay separate after rev0210

The architecture should now treat four distinctions as non-negotiable:

1. **target is writable** is not the same object as **target can natively carry required primitives**
2. **metadata appears preserved** is not the same object as **metadata is stored natively rather than by fallback stubs**
3. **action is absent** is not the same object as **client unhealthy**
4. **repair target selected** is not the same object as **postcondition proof completed**

If the object model fuses these distinctions, the interface will drift back toward the exact Resilio-style archaeology the archive is trying to avoid.

## Revision addendum — architecture pressure after rev0201: synthetic freshness is a reviewed chronology claim

The architecture should now preserve another line explicitly:

- synthetic freshness signals such as `touch` are not neutral repairs; they are chronology-bearing actions
- publication readiness must be typed state derived from evidence, not merely `changed recently`
- authoring delay and inbound priority need explicit provenance because inheritance and local freeze are materially different states
- visible browse order must never be treated as authoritative execution order when the scheduler knows otherwise

These are product-shape constraints, not merely UI copy decisions.

## ADR addendum after rev0199 — capability availability, entitlement basis, and loss state must stay separate

**Decision:** Keep capability availability, entitlement provenance, missing-action gating, and post-loss capability floor as separate public objects.

**Why:** Current Resilio docs still make operators combine feature-availability footnotes, folder-class comparisons, owner/seat licensing notes, lost-license troubleshooting, and FAQ prose to understand one ordinary capability story. AnonSync should publish that story directly.

The architecture should now treat four distinctions as non-negotiable:

1. **action is visible** is not the same object as **action is actually available**
2. **seat currently has capability** is not the same object as **why that entitlement basis is true**
3. **control absent on this surface** is not the same object as **capability impossible on this seat**
4. **entitlement changed** is not the same object as **current degraded floor and subject impact**

If the object model fuses these distinctions, the interface will drift back toward the exact Resilio-style archaeology the archive is trying to avoid.


## ADR addendum after rev0192 — byte-presence verbs and history replay need first-class pages

**Decision:** Keep fetch scope, local eviction, delete consequence, and retained-history replay visible as first-class public interface objects.

**Why:** Current Resilio docs still make operators combine synchronization modes, Selective Sync, RSLS instructions, disconnect behavior, Archive notes, and overwrite FAQs to understand one ordinary byte-presence story. AnonSync should publish that story directly.

## Revision addendum — seat lineage, roster residue, and reset impact must stay separate after rev0191

The architecture should now treat four distinctions as non-negotiable:

1. **seat display label** is not the same object as **seat identity proof**
2. **linked relationship** is not the same object as **identity replacement or certificate takeover**
3. **hidden roster row** is not the same object as **unlinked / retired seat**
4. **credential reset in same storage world** is not the same object as **clean install or storage-root rehome**

If the object model fuses these distinctions, the interface will drift back toward the exact Resilio-style archaeology the archive is trying to avoid.

## Revision addendum — pending claim, approver locus, and remembered trust must stay separate after rev0190

The architecture should now treat four distinctions as non-negotiable:

1. **claim exists** is not the same object as **approving seat has currently received / observed the claim**
2. **claimant identity proof** is not the same object as **resulting right if approved**
3. **seat is linked** is not the same object as **seat is currently eligible to approve for this subject**
4. **remembered trust record** is not the same object as **current reprompt policy for this claim lane**

If the object model fuses these distinctions, the interface will drift back toward the exact Resilio-style archaeology the archive is trying to avoid.

## Revision addendum — grant, artifact, revoke, and successor epoch must stay separate after rev0189

The architecture should now treat four distinctions as non-negotiable:

1. **current member right** is not the same object as **requested grant delta**
2. **live access-bearing artifact** is not the same object as **current governance intent**
3. **future-update revocation** is not the same object as **landed-byte cleanup or recall**
4. **successor grant epoch** is not the same object as **in-place mutation of the existing grant**

If the object model fuses these distinctions, the interface will drift back toward the exact Resilio-style archaeology the archive is trying to avoid.

## Revision addendum — relationship, subject class, and carrier must stay separate after rev0188

The architecture should now treat three distinctions as non-negotiable:

1. **linked relationship** is not the same object as **resulting seat right**
2. **subject class** is not the same object as **current-seat shareability verdict**
3. **carrier or intake lane** is not the same object as **canonical authority artifact**

If the object model fuses these distinctions, the interface will drift back toward the exact Resilio-style archaeology the archive is trying to avoid.

## ADR-000 — Current-surface capability is product state, not browser folklore

**Decision:** Whether an action is fully supported, inspect-only, handoffable, or blocked on the current surface must be published as product state.

**Why:** Current Resilio docs still show that browser prompts, WebUI exceptions, browser incompatibility, ad-block interference, and role ceilings can all influence the practical answer to `can I do this here?`.

**Implications:**

- one action-availability object per serious action family
- one surface-mismatch diagnosis object when accelerator failure and policy denial would otherwise blur together
- one reviewed handoff object when the safest path is another channel
- one resume receipt proving whether the target channel preserved or reopened review

# Architecture decisions

## ADR-001 — Open, inspectable behavior beats opaque convenience

**Decision:** Design for inspectability first.

**Why:** The strongest non-Resilio reason to build AnonSync is to make peer-to-peer sync more auditable and controllable.

**Implications:**

- documented protocol and schemas
- stable machine-readable state
- explicit diagnostics
- fewer hidden heuristics

## ADR-002 — Device identities are durable; linking never overwrites them

**Decision:** A device keeps its identity unless the local operator explicitly rotates or replaces it through recovery workflows.

**Why:** Resilio's documented linking behavior shows that certificate takeover can be destructive and confusing.

**Implications:**

- linking creates relationships, not mergers
- conflict resolution must be explicit
- share state cannot be silently rebound to a new certificate

## ADR-003 — Materialization state is first-class

**Decision:** Every mount/share pairing exposes a materialization mode.

**Modes:**

- `detached`
- `selective`
- `full`

**Why:** This is one of Resilio's genuinely strong product insights and should be preserved.

## ADR-004 — Encrypted-untrusted replicas are a v1 feature, not a someday add-on

**Decision:** Support encrypted-replica peers early.

**Why:** This is strategically differentiating, operationally useful, and aligned with the product thesis.

**Implications:**

- permissions must include `encrypted-replica`
- status tooling must distinguish plaintext and ciphertext holders
- fetch logic must explain when only encrypted copies exist

## ADR-005 — Placeholder semantics are optional, not foundational

**Decision:** Do not make cross-platform placeholder files the basis of v1.

**Why:** Placeholder implementation details can consume disproportionate complexity and obscure the real product value.

**Implications:**

- support virtual and sidecar strategies first
- add native placeholder integrations later where they are robust

## ADR-006 — Start with personal/small-team scope

**Decision:** Ignore enterprise fleet scope for now.

**Why:** Wide deployment support and central management can easily dominate the roadmap and bury the core product insight.

**Implications:**

- no centralized multi-tenant admin plane in v1
- no huge-job distribution story yet
- better local operator experience first

## ADR-007 — Strong diagnostics are part of the product, not support work

**Decision:** `status`, `events`, and `doctor` are first-class surfaces.

**Why:** Sync products fail hardest when users cannot tell what is happening.

**Implications:**

- the daemon tracks explanation-rich transfer states
- every blocked sync has a reason string
- the UI/TUI can be built atop the same event stream

## ADR-008 — Discovery/relay behavior is policy, not a hidden advanced setting

**Decision:** Tracker, relay, LAN discovery, known-host controls, and endpoint cache management are explicit policy objects.

**Why:** Resilio's official docs show that transport behavior materially changes privacy, reachability, and operator expectations.

**Implications:**

- shares can bind to named discovery policies
- status must show the effective path used
- LAN-only operation becomes a normal supported workflow

## ADR-009 — Linked devices do not imply owner authority by default

**Decision:** Device linking and share ownership are separate concepts.

**Why:** Resilio's linked-device model is convenient, but too broad for a system that wants auditable trust boundaries.

**Implications:**

- share grants remain explicit objects
- linked-device auto-grants are opt-in policy
- admin authority can be reviewed independently of personal-device membership

## ADR-010 — Recovery must be explicit; cloning is not the workflow

**Decision:** Support backup/export/import/replacement flows, but do not rely on opaque disk cloning.

**Why:** Operators still need hardware replacement and disaster-recovery workflows, and unsupported cloning is an unsatisfying answer.

**Implications:**

- explicit backup and recover commands
- trust reconciliation paths
- auditable identity rotation and replacement events

## ADR-011 — API and CLI are two views of one object model

**Decision:** The local daemon API is a first-class surface, not a private implementation detail.

**Why:** Resilio's split across UI/config/startup flags is precisely the kind of fragmentation AnonSync should avoid.

**Implications:**

- future UI/TUI must consume the same events and objects
- config import/export maps to the same schema family
- machine users are not second-class users

## ADR-012 — “Easy mode” behaviors must decompose into explicit policies

**Decision:** Convenience features such as linking, auto-grants, or default selective mounts must compile to inspectable policy objects.

**Why:** Hidden convenience is where trust expansion becomes hard to audit.

**Implications:**

- every auto-grant has provenance
- users can list and revoke policy-derived grants
- defaults are explainable and reversible

## ADR-013 — Observability and audit are part of the control plane

**Decision:** Expose metrics, audit, route selection, and health summaries through supported CLI/API surfaces.

**Why:** A sync product that only exposes raw logs leaves operators reconstructing the system model by hand.

**Implications:**

- `status`, `doctor`, `audit`, and `metrics` are supported interfaces
- route/cache state must be inspectable without debug builds
- security-relevant changes must leave machine-readable audit entries

## ADR-014 — High-signal mutations use plan/apply with drift detection

**Decision:** Trust-expanding, recovery-rebinding, or multi-object mutations should prefer explicit plan objects that are reviewed and then applied against checked preconditions.

**Why:** A plain `dry-run` is useful, but not strong enough when the world may change between preview and execution.

**Implications:**

- plan objects become part of the public object model
- applies can fail safely on drift instead of guessing intent
- audit can record both reviewed intent and executed change

## ADR-015 — Capability differences must be explicit and queryable

**Decision:** Local and remote capability differences should be inspectable through supported CLI/API surfaces.

**Why:** Partial feature support is inevitable across platforms, but silent degradation recreates the same black-box feeling this project is meant to avoid.

**Implications:**

- daemon exposes capability sets
- operators can tell why a requested strategy is unavailable
- CLI and future UI use the same capability facts when offering or rejecting actions


## ADR-016 — Newly visible shares are staged before local path adoption

**Decision:** Shares made visible through linking, policy, invite acceptance, or recovery should first appear as incoming objects unless the operator or policy explicitly chooses auto-adoption.

**Why:** Resilio's docs show that linked-device convenience can couple visibility, default mode, and default path placement tightly enough to create duplicate folders or require reconnect rituals.

**Implications:**

- incoming visibility becomes part of the public object model
- path choice is explicit and auditable
- visibility and mount existence are no longer conflated

## ADR-017 — Local eviction and share-wide delete use distinct verbs and scopes

**Decision:** The interface must separate local materialization actions from replicated delete actions.

**Why:** Selective-sync systems naturally sit close to a dangerous ambiguity: freeing local space and deleting shared state can look similar unless the contract is explicit.

**Implications:**

- CLI/API require explicit scope on remove actions where ambiguity exists
- plan/apply is preferred for share-wide delete on sensitive paths
- audit and events distinguish local eviction from replicated delete


## ADR-018 — File history and restore are supported surfaces, not hidden archive rituals

**Decision:** The product must expose file history and restore through supported CLI/API objects and actions.

**Why:** Resilio's Archive feature is valuable, but its documented restore path still depends on hidden directories, desktop-only affordances, and timing-sensitive manual steps.

**Implications:**

- restore candidates have stable IDs and provenance
- restore requires explicit scope (`local` vs `share`)
- share-wide restore can use plan/apply when risk warrants it
- audit and events cover restore actions like any other high-signal mutation


## ADR-019 — Ignore, conflict, and service-metadata state are supported surfaces

**Decision:** Ignore rules, conflict cases, and service-metadata health are part of the public control model.

**Why:** Resilio's docs show too much important operator state leaking through hidden `.sync` files, magic conflict filenames, and support-article warnings about what not to delete.

**Implications:**

- ignore rules become inspectable objects with provenance and drift state
- conflicts become structured records with safe resolution actions
- damaged service metadata is surfaced through health/doctor, not discovered only after breakage

## ADR-020 — Incremental rule mutation beats whole-array replacement

**Decision:** List-like policy surfaces should prefer item-level resources or explicit add/remove actions over generic whole-array replacement.

**Why:** Operators frequently mean “change one rule”, and array-replacement patch semantics are too easy to misuse when the blast radius is broader than it looks.

**Implications:**

- ignore rules get add/remove/test style operations
- CLI/API avoid accidental deletion of neighboring rules during routine edits
- future UI/TUI can use the same safe mutation model instead of inventing client-side merge logic


## ADR-021 — Compatibility and authority consequences are preflight objects

**Decision:** Link, invite-accept, grant, and adoption workflows should expose supported preflight reports with blockers, warnings, downgrade notes, and authority changes.

**Why:** Resilio's docs are clear enough that mixed-version linking and linked-device convenience can have real configuration or authority consequences, but too much of that knowledge still lives in FAQs and support notes.

**Implications:**

- preflight becomes part of the public object model
- plans may reference a preflight report and fail if it becomes stale
- UI/CLI can share one compatibility-warning vocabulary

## ADR-022 — Least privilege must survive convenient linking

**Decision:** Personal-device linking should support explicit per-device/per-share roles without requiring a separate weaker share type.

**Why:** Resilio's documented path to read-only behavior across linked devices pushes users toward Standard-folder key rituals and away from the stronger Advanced-folder model.

**Implications:**

- role templates become first-class resources
- linked-group membership never implies owner-like authority by itself
- share/grant semantics stay coherent even when one personal device is read-only, receive-only, or encrypted-only

## ADR-023 — Offers and invites require explicit claims before non-trivial local mutation

**Decision:** Visible shares and capability-bearing invites should pass through a durable claim/acceptance object before they create mounts, grants, or linked-group effects when the outcome is non-trivial.

**Why:** Resilio's current product shows that awareness, access, path choice, and authority expansion are easy to blur. AnonSync should keep “what was offered” distinct from “what this machine accepted.”

**Implications:**

- claims become part of the public object model
- invite inspection is side-effect free
- claim review can reference preflight and plan objects
- audit records can distinguish offered capability, claimed outcome, rejection, and expiry

## ADR-024 — Recovery-material sufficiency is supported state, not folklore

**Decision:** Recovery prerequisites for encrypted offline decrypt and similar workflows should be exportable, inspectable, and verifiable through supported recovery-bundle objects.

**Why:** Recovery that depends on remembered hidden database paths, debug logs, or lucky retained local state is too fragile for the product AnonSync aims to be.

**Implications:**

- recovery bundles become part of the supported surface
- doctor/status can report degraded recovery posture
- offline recovery aims to minimize database dependency where design permits
- rotation or replacement can explicitly invalidate stale recovery material


## ADR-025 — Approval memory is explicit, scoped, and revocable

**Decision:** Any remembered future-approval convenience must compile to a first-class approval object with bounded scope, approver scope, expiry, maximum role, and auditability.

**Why:** Resilio's docs make it clear that “approved before” and “can approve from any linked device” are real product concepts, but they remain too implicit for the trust model AnonSync wants.

**Implications:**

- there is no hidden ambient approval state outside the supported approval surface
- future-share convenience can be tested and reviewed before it is exercised
- linked devices may approve on one another's behalf only when explicit approver scope says so
- audit and events can explain why a later share or invite auto-approved


## ADR-026 — Path binding and relocation are explicit compared actions

**Decision:** Adopting a share into a populated path or relocating an existing mount must generate a comparison object and should usually go through plan/apply.

**Why:** Resilio's docs show permissive reconnect and pre-populated-folder workflows where default paths, duplicate-index folders, and timestamp-win replacement can decide outcomes, while Syncthing's docs react by warning that move/rename is dangerous unless the folder is already fully in sync. AnonSync should surface that risk instead of inheriting either folklore-driven extreme.

**Implications:**

- share identity and local path binding remain separate concepts
- non-empty target paths produce explicit identical/local-only/remote-only/collision findings
- service-marker or foreign-binding conflicts become health/preflight findings, not surprise later errors
- relocation is auditable as local path rebinding rather than hidden filesystem drift


## ADR-027 — Publication scope and route selection are distinct policy surfaces

**Decision:** Discovery policy must distinguish what the daemon publishes about reachability from how it later dials or relays traffic.

**Why:** Current Resilio docs make the network model reconstructable, but still mostly in the language of transport success: tracker, relay, LAN search, predefined hosts. A product centered on inspectable trust needs the language of exposure as well: who can learn that this device/share relationship exists, and through which service.

**Implications:**

- policy objects expose announce scope, dial methods, relay pool choice, and fallback order separately
- route/exposure summaries explain both the active path and the metadata disclosure that enabled it
- future UI/TUI cannot reduce topology policy back into a few unlabeled checkboxes


## ADR-028 — Decision traces are public contract, not debug garnish

**Decision:** High-signal outcomes should expose structured decision traces through supported CLI/API surfaces.

**Why:** Resilio's current docs are good enough to reconstruct route behavior, but too much explanation still arrives as a mix of peer-list symptoms, icon hints, and troubleshooting lore. A product built around inspectability should expose the decision path directly.

**Implications:**

- routes, claims, approval consumption, restore scope, and recovery rebinds can expose selected outcome plus rejected alternatives
- traces carry stable reason codes and freshness so automation can trust them
- future UI/TUI should consume the same trace objects instead of inventing its own inference layer


## ADR-029 — Temporary runtime overrides are explicit leases, not silent policy edits

Sync operators often need short-lived changes: pause during a metered connection, drain before shutdown, or temporary throttling during maintenance.
If those changes silently rewrite durable share or route policy, the product accumulates invisible drift and later surprises.

Decision:

- represent short-lived operational changes as first-class override leases
- require explicit target, effect, provenance, and expiry
- expose effective-state views that combine durable policy with active leases
- keep lease expiry reversible without manual cleanup

Consequence:

AnonSync can offer convenient maintenance controls without inheriting overloaded pause semantics or burying temporary intent inside long-lived configuration.


## ADR-030 — Destructive file mutations carry preservation reports

**Decision:** Share-wide delete, local remove, eviction, and share-scope restore should expose preservation evidence when rollback posture materially affects safety.

**Why:** Resilio's docs make destructive consequences depend too much on placeholder state, exact invocation path, hidden preferences, and Archive assumptions. AnonSync should not ask operators to reconstruct that safety model by memory.

**Implications:**

- the control plane can generate preservation reports for risky file actions
- plans for destructive mutations can reference fresh preservation evidence
- remaining plaintext replicas, encrypted-only remnants, and history gaps become visible state instead of folklore
- future UI/TUI integrations must preserve the same blast-radius model as CLI/API surfaces

## ADR-031 — Retirement, ignore, revoke, replace, and rotate are distinct public actions

**Decision:** Introduce a first-class retirement record so device exit semantics are explicit instead of inferred from disappearance, unlinking, or list hygiene.

**Why:** Current sync products too easily blur cosmetic cleanup, ignored future contact, trust revocation, hardware replacement, and identity rotation. Those intents have different security and continuity consequences and should not be bundled into one overloaded “remove device” gesture.

**Consequences:**

- CLI and API gain retirement resources and explicit intent values
- recovery workflows can reference retirement records when replacement or revocation is the real action
- audit and event streams can explain whether an old device was hidden, ignored, revoked, or replaced
- remote-lag / not-yet-observed retirement becomes supported status instead of ghost-device folklore

## ADR-032 — Share stewardship and handoff are first-class state

**Decision:** Introduce a first-class stewardship record so share governance is explicit instead of inferred from one permission bit or from share-type-specific rituals.

**Why:** Current sync products make authority either too broad (all linked devices act as owners) or too mode-dependent (Standard vs Advanced vs local-share behavior). AnonSync should keep data mutation rights, grant power, delegation, and succession visible as separate public concepts.

**Consequences:**

- CLI and API gain stewardship resources and handoff-plan workflows
- recovery and retirement workflows can say how stewardship changes, instead of leaving authority transfer implicit
- audit and event streams can explain who handed off what authority and under which review policy
- future UI/TUI layers must preserve the same separation between data rights and governance rights


## ADR-033 — Permission, propagation, and local-deviation remediation are distinct public state

Resilio's current read-only guidance still spreads a critical operator question across permission type, selective-sync caveats, overwrite toggles, and encrypted-folder special cases.
That is enough evidence that “can this target write?”, “will local changes propagate?”, and “what happens when someone edits it anyway?” should not live in one overloaded concept.

Therefore AnonSync should expose deviation policy as a first-class supported object.
Roles and mounts may reference it, plans and explain surfaces must show it, and events must report when local deviation is detected or auto-remediated.
That keeps one-way / mirror behavior inspectable without forcing operators to memorize share-type folklore.


## ADR-034 — Filesystem compatibility is first-class state, not conflict folklore

**Decision:** Case rules, Unicode normalization, prohibited names, symlink handling, metadata fidelity, and timestamp/clock safety must be exposed through supported filesystem-profile and compatibility-report surfaces.

**Why:** Resilio's docs still teach too much of this boundary through conflict examples and power-user toggles, while Syncthing's docs point toward a cleaner model of explicit capability and safety settings. AnonSync should not make operators discover pathname or metadata incompatibility only after bind or pull has already started.

**Consequences:**

- CLI and API gain filesystem-profile and filesystem-compatibility resources
- adopt / relocate / restore workflows can require a fresh fs compatibility report as a precondition
- doctor / explain surfaces can say whether the system is operating under reduced pathname or metadata fidelity
- normalization rewrites and metadata stripping become explicit policy choices instead of magic fallout


## ADR-035 — Namespace projection is first-class state, not ignore folklore

**Decision:** Introduce explicit projection-policy objects so share namespace announcement and local mount-view projection are supported state rather than inferred from hidden ignore files or placeholder timing.

**Why:** Resilio's docs make clear that `IgnoreList` edits do not retroactively hide already-synced files, that once a tree is indexed its structure continues to be passed to peers until disconnect, and that Selective Sync separately controls placeholder-visible local projection. Those are individually understandable behaviors, but they still leave operators reconstructing “who sees the name?” from folklore.

**Consequences:**

- CLI and API gain projection-policy and path-test surfaces
- share-level namespace suppression and mount-level omission/placeholder behavior become separate supported concepts
- tighten behavior for already-indexed or already-materialized paths becomes explicit reviewable state
- future UI/TUI layers must preserve the same distinction between namespace announcement, local projection, and byte materialization


## ADR-036 — Settlement confidence is first-class state, not status folklore

**Decision:** Introduce explicit convergence-report and convergence-wait surfaces so the product can distinguish idle status from trustworthy settlement confidence.

**Why:** Resilio's current docs still ask operators to combine peer counts, status warnings, excessive time-difference errors, watcher-exhaustion warnings, and hidden internal-task caveats to decide whether a share is really safe to treat as settled. That is too much inference for a product centered on inspectable control.

**Consequences:**

- CLI and API gain convergence-report and wait-for-settlement resources
- status, doctor, and explain surfaces can report `degraded-converged` instead of pretending every idle share is equally trustworthy
- cutover / backup / relocate workflows can depend on explicit readiness evidence instead of ad hoc polling
- future UI/TUI layers must preserve the same distinction between completion, health, and settlement confidence

## ADR-037 — Tor and I2P are first-class transport engines

**Decision:** Treat Tor and I2P as supported transport engines and route classes, not merely external proxy compatibility modes.

**Why:** If AnonSync wants privacy-routed operation to be central, the route model cannot remain clearnet-first with anonymity added later as an option. Tor's Arti project is explicitly embeddable and production-quality for client use, while I2P's own application guidance encourages bundling a router and using SAM for non-Java applications.

**Implications:**

- route policies can express `tor` and `i2p` directly
- bundled transport runtimes get explicit health/inspection surfaces
- CLI/API can explain when a privacy route failed because the engine was cold, unhealthy, or policy-disabled

## ADR-038 — WAN clearnet direct is a manual override, not a default

**Decision:** Keep faster WAN clearnet direct available, but require manual enablement or explicit policy opt-in.

**Why:** Direct IP-to-IP can materially improve speed, but making it the default would quietly re-center the product on the clearnet-first transport hierarchy it is trying not to inherit.

**Implications:**

- default privacy-oriented policies use Tor/I2P before public direct paths
- route/explain surfaces must say when manual speed override is active
- temporary direct enablement should expire cleanly without rewriting durable baseline policy

## ADR-039 — Linux-first quality bar beats early cross-platform parity

**Decision:** Optimize v1 design quality for Linux and common Linux filesystems before treating Windows/macOS as equal design centers.

**Why:** The archive is already deep in daemon semantics, watcher behavior, path binding, and filesystem compatibility. Spreading that effort too early across every desktop platform would dilute correctness and observability where the project most wants to be strong.

**Implications:**

- roadmap and testing center on Linux-first headless operation
- filesystem-compatibility work starts with common Linux semantics
- other platforms remain future work unless they can fit without bending the primary model



## ADR-040 — Privacy-transport session lifecycle must be explicit

Transport engines, transport runtimes, transport sessions, and route outcomes are related but not identical.
The product should expose all four.

Why:

- bundled runtimes otherwise become magical
- route debugging becomes guesswork
- I2P in particular should usually avoid per-transfer session churn
- a future UI should consume the same public transport/session model as the CLI

Consequence:

- the interface and API expose transport-session objects
- I2P defaults toward a very small number of long-lived shared sessions
- manual clearnet speed overrides create visible temporary route state rather than silently widening the base policy

## ADR-041 — Linux-first support requires explicit filesystem tiers

“Linux-first” is not a complete decision until the project publishes which filesystem environments it supports strongly.

Why:

- operators need a correctness contract before adoption or relocation
- xattr/ACL/symlink/network-filesystem behavior is part of the trust boundary
- warning-tier and blocked environments should be visible before data lands there

Consequence:

- the archive names first-class Linux filesystems for v1
- filesystem support tier is exposed as public state
- adopt / relocate / restore / selective workflows can depend on filesystem-probe results

## ADR-042 — Peer-pinned direct paths and route-speed windows are first-class state

**Decision:** Introduce first-class known-host records and route leases for transport exceptions.

**Why:** Resilio's documented `known_hosts`, tracker/relay toggles, and LAN-only cache-clearing rituals show that operators really do need fine-grained route control. But hiding that control inside preference pages and remembered endpoint state makes exposure hard to reason about.

**Consequences:**

- peer-pinned direct admission becomes distinct from ambient public direct
- temporary speed windows become auditable route leases with scope, reason, expiry, and optional byte caps
- exposure reports can explain who currently learns reachability and why a direct candidate exists at all


## ADR-043 — Contacts and pending peers are first-class state, not side effects of linking

**Decision:** Introduce explicit contact and pending-peer surfaces in the public control model.

**Why:** Resilio's linked-device behavior shows that convenience can easily smear together relationship memory, future approval, and ambient visibility. Syncthing's explicit pending-device queue validates that unknown-peer admission is a real product seam worth modeling directly.

**Consequences:**

- unknown or newly introduced peers land in a queue before trust
- ignore and quarantine become durable supported states
- future UI/TUI work gets a supported admission queue instead of inventing one from logs

## ADR-044 — Successor continuity is reviewed state, not ambient inheritance

**Decision:** Treat device succession as an explicit reviewed continuity plan.

**Why:** Linking and replacement solve different problems. The project should not recreate Resilio-style certificate takeover or ambient owner-like carry-forward just because replacing hardware needs to stay practical.

**Consequences:**

- replacement plans show which grants, approvals, contacts, and known-hosts carry forward
- some continuity may be preserved without pretending the successor is literally the same authority
- recovery, retirement, and stewardship surfaces converge on one explicit successor contract


## ADR-045 — State roots and service profiles are first-class operator state

**Decision:** Expose durable state roots, identity-root continuity, and runtime/service profiles as public objects with verification, attach, move, export, import, and profile-switch workflows.

**Why:** Resilio's docs show too much important behavior hiding in storage paths, service-account choices, migrated-versus-clean installs, and unsupported cloning warnings. A product built around inspectability should never leave the operator guessing which control universe is active.

**Consequences:**

- CLI and API gain explicit state-root and service-profile surfaces
- attach/move/profile-switch work uses reports, plans, and before/after snapshots instead of launch-time magic
- workbench gains a System State page
- “missing shares after mode switch” becomes a blocked or explained transition, not normal folklore


## ADR-046 — File intent and local deviation are first-class operator state

**Decision:** Expose explicit file-intent scope, deviation-case objects, and file-intent receipts so destructive or restorative file actions do not depend on mode-specific folklore.

**Why:** Resilio's docs still spread important file semantics across Selective Sync placeholder behavior, `Remove from this device` versus `Remove from all devices`, read-only `Overwrite any changed files`, and manual Archive restore. An inspectable product should not force operators to reconstruct that model from scattered caveats.

**Consequences:**

- CLI and API gain deviation-case and file-intent-receipt surfaces
- workbench gains a dedicated file-actions/deviation panel
- future GUI/TUI affordances must preserve the same distinction between local eviction, replicated delete, local restore, share restore, and deviation resolution


## ADR-047 — Runtime control is a phase matrix, not an overloaded pause state

**Decision:** Introduce first-class activity-phase-state and schedule-window surfaces so one-shot overrides and recurring windows render through the same public phase model.

**Why:** Resilio's current docs still show pause, scheduler, and bandwidth controls that are useful but semantically overloaded: paused states can still allow rescans and delete propagation, scheduler effects can be asymmetric, and LAN throttling can depend on a separate advanced switch. AnonSync should not clone that ambiguity.

**Consequence:**

- `activity show` and workbench activity cards expose scan/index, ingress, egress, delete propagation, announcement, and dialing separately
- recurring windows become first-class inspectable objects rather than UI-only calendar state
- stronger freezes that suspend delete propagation or announcement can require plan/apply instead of masquerading as ordinary pause
- route-class scope for throttling remains explicit so LAN, Internet, overlay, and direct-path behavior do not blur together

## ADR-048 — Projection tightening emits receipts, not folklore

**Decision:** Introduce projection-effect reports and projection receipts for high-signal namespace / local-view changes, especially when rules tighten after paths were already indexed or materialized.

**Why:** Resilio's docs say `IgnoreList` lives in hidden `.sync`, does not affect files that already synced, and still leaves indexed structure passed to peers until disconnect. Separate docs say placeholders / `.rsls` are a local-view mechanism, disconnecting a selective-sync share removes placeholders from the device, nested subfolder shares disable Selective Sync while double-indexing, and xattrs use a separate `StreamsList` control path. Those are workable behaviors, but they leave operators inferring past and future visibility from side effects instead of one public model.

**Consequences:**

- any projection-tightening action that touches already indexed or materialized state can require a projection-effect report before apply
- applied high-signal changes emit receipts explaining peer namespace change, local-view change, local-byte effect, and remaining follow-up
- detach cleanup cannot masquerade as share-wide suppression
- GUI/TUI/CLI layers must preserve the distinction between peer namespace, local view, and local byte state


## ADR-049 — Settlement readiness is a policy/barrier/receipt layer, not just one convergence report

**Decision:** Introduce first-class settlement-policy, settlement-barrier, and settlement-receipt surfaces above the existing convergence report.

**Why:** Resilio's current docs still make operators combine `X of Y peers`, sync-history clues, time-difference warnings, watcher fallback, background-task caveats, and ghost-file/source-absence warnings to judge whether a share is *actually* safe for cutover or restore. A product centered on inspectable control should not leave that translation step outside the public model.

**Consequences:**

- convergence evidence remains first-class, but no longer carries the whole readiness burden alone
- intent-specific witness/source rules, quiet windows, evidence-age limits, and degraded allowances become public policy state
- high-signal actions can require or emit settlement barriers and receipts
- later audit can prove what readiness standard an action actually used instead of only that it happened


## ADR-050 — Rollback provenance and conflict resolution are timeline objects, not support ritual

**Decision:** Introduce first-class history-entry, restore-candidate, conflict-case linkage, and rollback-receipt surfaces so rollback and conflict resolution are one public timeline model.

**Why:** Resilio's current docs still split the story across a generic 30-day History view, hidden/manual Archive restore, offline-wins overwrite behavior, `.Conflict` filename ritual, and a power-user switch that can suppress conflict-file creation while leaving syncing unpredictable. An inspectable product should not make operators reconstruct rollback truth from those fragments.

**Consequences:**

- history entries carry provenance, capture cause, retention horizon, allowed scopes, and confidence
- restore and conflict-resolution actions emit rollback receipts in addition to ordinary file-intent or audit records
- workbench gains a combined history/conflict/rollback surface rather than separate “history” and “mystery conflict” mini-products
- future GUI/TUI/CLI projections must preserve the same winner/loser/scope semantics without falling back to magic filenames or hidden archive browsing

## ADR-051 — Filesystem portability is a durable fidelity contract, not a one-time preflight

**Decision:** Introduce first-class portability-policy, fidelity-contract, drift-case, and fidelity-receipt objects so filesystem semantics remain explicit after bind and after later runtime drift.

**Why:** Resilio's current docs still distribute this boundary across SMB caveats, symlink platform rules, hidden `.sync` / `StreamsList` service files, troubleshooting for UTF-8/path-length/permission failures, and remove/re-add repair ritual after service-marker corruption. That is workable support knowledge. It is not a durable operator contract.

**Consequences:**

- the public model distinguishes previewed compatibility from the active semantics a mount is currently promising
- network-share posture and degraded notifications become explicit support-tier facts, not background folklore
- accepted downgrade becomes auditable through fidelity receipts
- later drift in permissions, notifications, or filesystem backing becomes a first-class warning object instead of a mysterious sync regression


## ADR-052 — Storage pressure is a budget/reclaim/receipt layer, not a troubleshooting afterthought

### Decision

AnonSync will model storage as first-class public state through space ledgers, budget policies, pressure cases, reclaim plans, and reclaim receipts.

### Why

Current sync products often expose useful space-saving features while still leaving the operator to reconstruct one storage story from placeholders, hidden archives, power-user thresholds, service-state paths, and manual temp-remnant cleanup. That is good troubleshooting; it is not an honest storage contract.

### Consequences

- low-space conditions can be explained by byte class rather than by generic warning strings
- reclaim can stay visibly distinct from replicated delete semantics
- retention and rollback posture can remain visible when space-saving actions would weaken them
- workbench, CLI, API, and audit can all answer what was reclaimed and what tradeoff was accepted


## ADR-053 — capability-bearing offers use one artifact grammar regardless of delivery encoding

**Decision:** AnonSync will model portable authority through first-class offer artifacts, offer policy, and claim receipts. File, URI, QR, clipboard, and local-handoff delivery are encodings of the same semantic object, not different trust systems.

**Why:** Resilio's current docs still make operators combine key-vs-link behavior, approval posture, expiry/use-count link settings, Standard-vs-Advanced re-sharing semantics, and local-share permission ritual to answer what authority an artifact really carries.

**Consequences:**

- sender-side surfaces can revoke or reissue offers without confusing that with applied local authority
- receiver-side intake can normalize portable artifacts before any local mutation
- delivery widgets stop becoming hidden semantic control surfaces
- later audit can prove offer consumption through claim receipts even after one-time artifacts expire


## ADR-054 — Transfer speed is governed by explicit policy, budget, and explanation objects

**Decision:** AnonSync will model transfer behavior through first-class transfer-policy, throughput-budget, transfer-explanation, and transfer-budget-receipt objects rather than leaving throughput truth to icons, graphs, and advanced settings.

**Why:** Resilio's current docs still spread important transfer behavior across relay/direct articles, Internet-vs-LAN bandwidth caveats, protocol and encryption knobs, queue priority semantics, per-extension delay config, and performance graphs. That is useful tuning guidance. It is not one operator-facing transfer contract.

**Consequences:**

- CLI and API gain explicit transfer-policy, throughput-budget, and transfer-explanation surfaces
- workbench transfer cards must explain queue, route, and bottleneck truth rather than only progress
- temporary metered or bulk windows emit receipts instead of disappearing into scheduler folklore
- future GUI/TUI/CLI projections must preserve the same distinction between route permission, route preference, and throughput budget


## ADR-055 — Attention is a durable policy/event/receipt layer, not a scatter of badges and notifications

**Decision:** AnonSync will model operator attention through first-class attention-policy, attention-event, and attention-receipt objects that sit above reports and review items without replacing them.

**Why:** Resilio's current docs still make operators triangulate status-column warnings, separate core-warning pages, history search, queue inspection, Linux UI-only notifications, and browser trust prompts to answer one simple question: what needs action now, and what did my acknowledgement actually change? That is workable support knowledge. It is not one trustworthy attention contract.

**Consequences:**

- workbench, CLI, and headless clients preserve the same semantic urgency even when they render through different delivery channels
- acknowledgements and snoozes become receipt-bearing public state rather than implicit local UI behavior
- delivery failure is visible and auditable instead of disappearing into best-effort notification plumbing
- future GUI/TUI/CLI projections must preserve the same distinction between report meaning, lane placement, delivery channel, and operator acknowledgement


## ADR-056 — Control access is an endpoint/session/receipt layer, not WebUI password lore

**Decision:** AnonSync will model control access through first-class control-access-policy, control-endpoint, access-token, control-session, and access-receipt objects.

**Why:** Resilio's current docs still make operators combine localhost-vs-LAN WebUI listen state, optional workstation passwords, session cookies, self-signed HTTPS trust warnings, config-file login injection, password-reset side effects, and service-profile storage-folder changes to answer one simple question: who can control this daemon right now, and what changed when I exposed or repaired that access? That is workable support knowledge. It is not one trustworthy control-access contract.

**Consequences:**

- leaving localhost becomes a reviewed exposure change rather than a casual bind tweak
- browser/workbench sessions, CLI sessions, and automation tokens remain visibly distinct
- trusted-proxy and hostcheck posture become explicit endpoint state instead of deployment folklore
- access repair and revocation emit receipts instead of mutating unrelated daemon state behind the operator's back


## ADR-057 — Recovery material is a custody/continuity/receipt contract, not just an export command

**Decision:** AnonSync will model recovery through first-class recovery posture, workflow-scoped bundles, and recovery receipts that explicitly name custody class, hidden dependencies, continuity claims, and invalidation causes.

**Why:** Resilio's current docs still spread recovery truth across unsupported cloning warnings, storage-folder lore, saved-key requirements, database continuity requirements for encrypted recovery, config-mode guidance, and password-reset or service-profile actions that mutate state roots. That is workable support knowledge. It is not one durable recovery-material contract.

**Consequences:**

- bundle export no longer implies sufficiency by itself
- device replacement, encrypted-byte recovery, and grant/identity continuity stay visibly distinct
- rotation, retirement, and state-root changes can invalidate older recovery bundles explicitly
- workbench, CLI, API, and audit can all answer which recovery artifact was current and what it could actually preserve

## ADR-058 — Release posture is a version/channel/schema/rollback contract, not package-manager folklore

**Decision:** AnonSync should expose release posture, reviewed upgrade plans, and release receipts as first-class operator state.

**Why:** Current Resilio docs still spread upgrade truth across update settings, platform-specific install pages, v2/v3 and Home/Business caveats, mixed-version linking warnings, and changelog archaeology. That is useful support material, but it is not one trustworthy operator contract.

**Consequences:**

- update availability and upgrade readiness remain visibly distinct
- edition family, release channel, schema epoch, and peer-constellation skew stay separate public facts
- cutover scope and rollback posture become part of reviewed upgrade plans rather than post-hoc support lore
- later audit can prove which compatibility boundary was accepted when a guarded or mixed release posture remained in force



## ADR-059 — Effective policy is a per-field origin/precedence contract, not settings-layer folklore

**Decision:** AnonSync will model defaults profiles, policy bindings, effective-policy explanation, and policy receipts as first-class operator state.

**Why:** Current Resilio docs still spread effective behavior across global preferences, per-folder preferences, power-user keys, config-mode injection, Linux-WebUI gaps, and manual-detach-from-default lore. That is useful support material, but it is not one trustworthy precedence contract.

**Consequences:**

- effective value and origin chain stay separate public facts
- `inherit`, `disable`, `clear`, and `pin to none` remain distinct actions rather than one ambiguous reset gesture
- defaults/profile changes become previewable by subject set instead of silently rewriting every eligible object
- later audit can prove which field was pinned, which returned to inheritance, and which defaults/profile change touched existing subjects


## ADR-060 — Diagnostics are an incident/evidence/redaction contract, not hidden-log support ritual

**Decision:** AnonSync will model troubleshooting through first-class diagnostic incidents, reviewed evidence bundles, redaction profiles, and evidence receipts.

**Why:** Current Resilio docs still spread serious diagnostics across hidden storage-folder lore, manual debug-file toggles, log-size tweaks, platform-specific dump collection, and support-form ritual. That is useful support material. It is not one trustworthy operator contract.

**Consequences:**

- diagnostic depth becomes explicit, temporary, and receipt-bearing instead of sticky hidden state
- support bundles can be previewed, redaction-reviewed, sealed, exported, and destroyed through one public model
- crashes, per-file diagnostics, recent logs, and event windows stay incident-scoped instead of becoming orphaned filesystem artifacts
- future GUI/TUI/CLI projections must preserve the same distinction between incident scope, collected evidence, redaction posture, and bundle custody


## ADR-061 — Temporary exceptions share one lease lifecycle across domains

**Decision:** AnonSync will treat temporary exceptions as first-class override leases with one shared lifecycle, even when route, activity, diagnostics, access, or other domains keep specialized fields.

**Why:** Current Resilio docs still solve several short-lived operator needs through scattered scheduler cells, power-user keys, config edits, debug toggles, and cleanup memory. That is workable, but it is not one trustworthy exception contract.

**Implications:**

- specialized temporary controls can cross-link through one `Exceptions` surface
- every lease can show baseline-versus-effective state, end condition, and receipt history
- `renew` preserves continuity instead of replacing history with a fresh opaque object
- converting a temporary exception into durable policy becomes an explicit, receipted mutation rather than hidden drift


## ADR-062 — Personal-device convenience is a constellation/authority-domain contract, not ambient owner identity

Resilio's linked-device model remains a useful warning: it is highly convenient, but it still makes ambient same-identity status do too much authority work.
AnonSync should instead model convenience-linked devices through explicit constellation records, member classes, visibility defaults, approval-scope limits, and share-scoped authority-domain explanations.

Consequences:

- “my devices” remains useful without silently implying owner merge
- phones, appliances, untrusted-storage nodes, and recovery-only members can stay inside one reviewed constellation without pretending they are equivalent
- disconnect/remove/approval actions can explain constellation-wide blast radius before apply
- later audit can prove when membership, member class, or scope boundaries changed


## ADR-063 — Discovery publication is an audience/fact/residue contract, not tracker-toggle folklore

**Decision:** AnonSync will model discovery publication through first-class disclosure profiles, disclosure reports, residual-disclosure findings, and disclosure receipts.

**Why:** Current Resilio docs still spread disclosure truth across tracker behavior, LAN announcements, predefined hosts, ports/protocols notes, and cache-clearing lore. That is useful support material. It is not one trustworthy operator contract for what audiences learn which facts and what remains after narrowing.

**Consequences:**

- route success and disclosure truth remain related but separate public state
- local discovery, named endpoints, private infrastructure, and public infrastructure all render as audience classes with fact matrices
- narrowing a policy can stop future publication without falsely claiming residue is gone
- later audit can prove both publication change and any acknowledged or cleared residual disclosure


## ADR-064 — Exit intent must be a first-class contract

**Decision:** Departure-style actions should compile to a shared exit-plan / exit-receipt model instead of relying on overloaded remove/uninstall vocabulary.

**Why:** Current sync-product support lore often makes operators infer too much from verbs like hide, disconnect, remove, unlink, or uninstall. A privacy-respecting product should be at least as explicit on the way out as it is on the way in.

**Implications:**

- exit intent stays explicit (`hide`, `detach-local`, `revoke-authority`, `replace-with-successor`, `decommission`, `erase-local-residue`)
- exit plans always show what stops, what stays, and what residue remains
- domain-specific verbs may stay for ergonomics, but their outcomes should compile to one shared receipt model


## ADR-065 — Safety-critical destructive controls need channel parity

**Decision:** Any exit, replacement, revocation, detach, or destructive file action that is considered safety-critical must preserve the same semantic review model across GUI, WebUI, TUI, CLI, and API-backed automation.

**Why:** Current Resilio docs make it unusually visible that Linux/WebUI/config-heavy operation can differ meaningfully from richer desktop paths, including destructive-action affordances and feature envelopes. A Linux-first product cannot treat that as implementation trivia.

**Implications:**

- dangerous actions get one stable review grammar (`intent`, `stops`, `stays`, `residue`, `follow-up`, `receipt`)
- channel-specific clients may change layout, but not scope truth or acknowledgement requirements
- the daemon/API contract must expose a review-ready projection rather than forcing each client to summarize raw effects ad hoc


## ADR-066 — Device joining must be a reviewed blast-radius decision, not a pairing ritual

**Decision:** Any non-trivial device join into a personal constellation must expose a fixed review model before apply.

**Why:** Current Resilio docs still make one `link device` step carry identity continuity, immediate share visibility, future approval reach, compatibility risk, and path-placement consequences. A Linux-first product should not hide that blast radius behind convenience language.

**Implications:**

- reviewed joins answer whether the action is join, migration, or replacement
- member class and default visibility posture are explicit before apply
- immediate visibility and authority deltas are explicit before apply
- GUI, WebUI, TUI, CLI, and automation all render the same join sections in the same order
- future GUI convenience work cannot silently outrun what headless or textual operators are allowed to understand before apply

## ADR-067 — Non-trivial claims and adoptions need one fixed intake grammar

**Decision:** Portable-offer acceptance, linked incoming-share adoption, and other non-trivial way-in flows must preserve the same semantic review model across GUI, WebUI, TUI, CLI, and API-backed automation.

**Why:** Current Resilio docs show that linked visibility, default-path placement, reconnect behavior, and non-empty-folder acceptance can still depend on device-wide mode switches and `Connect` ritual. A Linux-first product should not let one channel show rich intake meaning while another collapses it into a path picker.

**Implications:**

- non-trivial claims get one stable review grammar (`source`, `local outcome`, `path/filesystem`, `authority delta`, `blockers`, `receipt`)
- incoming visibility, portable offers, and prepared claims can render through the same supported intake model
- channel-specific clients may change layout, but not acceptance meaning or acknowledgement requirements
- future GUI convenience work cannot silently outrun what headless or textual operators are allowed to understand before apply



## ADR-068 — Successor cutover and state re-home need one fixed review grammar

**Decision:** Non-trivial device replacement and continuity-sensitive state-root/runtime transitions should expose one shared cutover review model before apply.

**Why:** Current Resilio docs still spread continuity meaning across unsupported cloning, service installer choices, service-account storage-root shifts, link-time certificate takeover, uninstall residue, and stolen-device ritual. A Linux-first product should not make operators reconstruct cutover truth from that archaeology.

**Implications:**

- successor replacement and same-root re-home can share one stable review order without pretending they are always the same action
- GUI, WebUI, TUI, CLI, and automation all have to render predecessor/candidate, carry-forward, target, rewrite, residue, and receipt truth in the same order
- installer or profile-switch convenience work cannot silently outrun what headless or textual operators are allowed to understand before apply
- later audit can prove which continuity claims were actually made, what authority rewrites occurred, and what residue remained unresolved


## ADR-069 — Compromise response is an incident-grade containment/rotation contract, not unlink/uninstall ritual

**Decision:** AnonSync will model trust incidents through first-class compromise cases and compromise receipts that normalize immediate freeze, later revocation, rotation, continuity choice, and residue findings into one reviewed contract.

**Why:** Current Resilio docs still spread compromise meaning across hide-offline-device behavior that does not unlink anything, local-only unlink limits, uninstall/storage cleanup notes, stolen-device reset ritual, and manual reshare memory. That is workable emergency lore. It is not one trustworthy containment contract.

**Implications:**

- freeze, revoke, rotate, replace, and clean-break decisions remain visibly distinct even when one incident touches all of them
- access tokens, portable offers, route publication, grants, and approval memory can participate in one case without collapsing into one overloaded verb
- successor preparation can remain continuity-preserving without falsely claiming compromise was fully cleared
- later audit can prove what was contained immediately, what still required observation, and what residue remained unresolved


## ADR-070 — Dormant-peer return is a reviewed state-replay decision, not ordinary online status

**Decision:** AnonSync will model long-offline or chronology-uncertain return through first-class re-entry cases and re-entry receipts that normalize dormancy facts, chronology confidence, replay authority, divergence/source reality, and escalation options into one reviewed contract.

**Why:** Current Resilio docs still spread stale return meaning across hide-only offline-device cleanup, offline-peer counters, configurable disconnect thresholds, offline-wins overwrite rules, time-difference warnings, and ghost-file/source-absence messages. Those are useful clues. They are not one trustworthy re-entry contract.

**Implications:**

- “online again” remains visibly separate from “safe to resume writable replay”
- chronology confidence and source reality stay public facts instead of archive/conflict folklore
- stale return can escalate cleanly into compromise or successor-cutover review without pretending it was benign status all along
- later audit can prove whether the subject resumed, stayed quarantined, downgraded to read-only, or was blocked/escalated


## ADR-071 — Destructive replay needs one reviewed pre-apply contract, not pause/archive folklore

**Decision:** Any non-trivial remote delete, overwrite, or receive-only revert wave should expose one shared destructive-replay review model before apply.

**Why:** Current Resilio docs still make operators combine pause-except-delete semantics, optional archive retention, potentially destructive `Overwrite any changed files` behavior, and manual restore lore to understand whether the next accepted cluster action will destroy or replace local state. That is useful support information. It is not one trustworthy consent contract.

**Implications:**

- pause, preservation, and destructive consent remain visibly separate public state
- delete, overwrite, and revert scope stay explicit before apply rather than being inferred from mode or aftermath
- archive/versioning weakness becomes a recoverability finding, not a hidden preference footnote
- GUI, WebUI, TUI, CLI, and automation all have to render the same trigger/effect/recoverability/confidence sections in the same order
- destructive waves can escalate into re-entry or compromise review without pretending they were routine sync progress all along

## ADR-072 — Conflict adjudication needs one reviewed contract, not suffix folklore

**Decision:** Any non-trivial conflict should expose one shared adjudication review model before winner selection or destructive loser handling proceeds.

**Why:** Current Resilio docs still make operators combine `.Conflict` suffix warnings, manual healthy-file dance, re-add collision examples, and power-user path toggles such as `fix_conflicting_paths` to understand what is actually colliding and what happens if they “clean it up”. That is useful support information. It is not one trustworthy adjudication contract.

**Implications:**

- conflicts keep semantic class distinct from filename artifact
- reviewed conflict pages always expose candidate posture, compatibility reality, propagation scope, and loser handling before resolution
- rollback receipts prove winner, loser handling, and unresolved caveats after the visible badge is gone
- workbench, CLI, and API-backed automation must render the same adjudication sections in the same order


## ADR-073 — Same-host derivation needs one reviewed contract, not local-share convenience

### Status
Accepted

### Context

Current Resilio docs show same-host `local share` support is useful, but it still spreads important meaning across one convenience action: target path choice, loop warnings, inherited permissions, source-coupled removal, re-share ritual, and placeholder dependence.
That is enough to build real workflows, but it is too compressed for AnonSync's thesis.

### Decision

AnonSync will treat non-trivial same-host derivation as a first-class reviewed case with one fixed grammar for source/target, topology risk, authority+lifecycle coupling, materialization+target-tier reality, admissible derivations, and receipt promise.
No channel may reduce that meaning to a path picker plus `Create local copy` semantics.

### Consequences

- same-host fanout becomes explicitly distinguishable from remote adoption, export, or cache-only branching
- loop risk and target-tier weakness are previewed before apply rather than left to warnings or failure
- lifecycle coupling to the source remains inspectable later from receipts
- Linux/WebUI/CLI parity becomes part of the safety model for same-host derivation

## ADR-074 — Live authority mutation needs one reviewed contract, not folder-class ritual

**Decision:** Non-trivial access changes should compile to one reviewed authority-mutation model rather than depending on share class, owner folklore, disconnect semantics, or remove/re-share ritual.

**Why:** Resilio's current docs still spread live permission meaning across Standard-vs-Advanced folder class, same-identity owner broadening, local-share caveats, and config-mode surface loss. AnonSync should keep write authority, delegation reach, revoke power, dependent fallout, and byte-retention consequences visible in one place.

**Consequences:**
- grant mutation gains a stable review grammar and durable mutation receipts
- workbench and CLI both need explicit current-authority and desired-boundary sections
- narrowing authority can preserve bytes without pretending revoke means erase
- imported or legacy authority representations may require visible migration rather than silent coercion


## ADR-075 — Graph overlap and containment need one reviewed contract, not nested-share folklore

**Decision:** Non-trivial nested, overlapping, moved, or root-boundary-sensitive graph relationships should compile to one reviewed topology model rather than depending on separate-share caveats, local loop warnings, reconnect ritual, or config-root restrictions.

**Why:** Resilio's current docs still spread topology meaning across nested-child limitations, double indexing, child-via-parent propagation, same-host parent/subdirectory loop warnings, move/rename limits, and `directory_root_policy` / `dir_whitelist` path rules. AnonSync should keep graph relation, propagation shape, path continuity, and root-boundary truth visible in one place.

**Consequences:**
- topology work gains a stable review grammar and durable topology receipts
- workbench and CLI both need explicit graph-subject and propagation-shape sections
- nested-share acceptance stays visibly distinct from same-host derivation, cross-share move, or root escape
- imported or policy-root path constraints may require visible rebind or root-review rather than silent coercion


## ADR-076 — Writer contention needs one reviewed coordination contract, not badges and hidden delay lore

**Decision:** Non-trivial lock pressure, burst-save delay, mixed external-writer risk, and explicit quiesce actions should compile to one reviewed contention model rather than living as separate status badges, hidden delay files, retry knobs, and SMB caveats.

**Why:** Current Resilio docs still spread coordination meaning across `Locked files`, storage-folder `FileDelayConfig`, `recheck_locked_files_interval`, and SMB warning pages about notification loss, broken locks, and mixed access outside Samba. AnonSync should keep contested scope, writer reality, filesystem posture, quiesce effect, and safe resume conditions visible in one place.

**Consequences:**
- contention work gains a stable review grammar and durable contention receipts
- workbench and CLI both need explicit contested-scope, writer-reality, notification-posture, and quiesce-effect sections
- delay profiles, upload holds, bidirectional freezes, and reader-only guards remain visibly distinct public actions
- degraded notification or mixed-access evidence can escalate visibly into fidelity, topology, or destructive-replay review instead of hiding behind retries

## ADR-077 — Host fit and scale admission need one reviewed contract, not warnings and re-add folklore

**Decision:** Non-trivial RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers should compile to one reviewed capacity-fit model rather than living as separate warnings, advanced toggles, and re-add/reindex ritual.

**Why:** Current Resilio docs still spread host-fit meaning across `Out of memory`, watcher-exhaustion warnings, generic internal-task slowdown notes, huge-folder indexing preferences, free-space reserve knobs, and troubleshooting advice that can end in restart, `touch`, or remove-and-re-add. AnonSync should keep subject role, host resource posture, freshness guarantees, path blockers, and admissible local modes visible in one place.

**Consequences:**
- host-fit work gains a stable review grammar and durable fit receipts
- workbench and CLI both need explicit subject-role, local-capacity/index-cost, freshness-posture, and path-blocker sections
- full adoption, selective/materialized narrowing, metadata-only visibility, reclaim-first staging, and reject-on-this-host outcomes remain visibly distinct public actions
- intake, topology, fidelity, and storage surfaces can escalate into host-fit review instead of hiding scale pain behind generic add/connect flows


## ADR-078 — Bring-up and first control entry need one reviewed contract, not installer and config ritual

**Decision:** Non-trivial first-open work should compile to one reviewed bring-up model rather than living as separate init flows, startup flags, config files, activation steps, and bind-address lore.

**Why:** Current Resilio docs still spread bring-up meaning across v3 activation/edition notes, config-mode and Linux startup flags (`--storage`, `--identity`, `--license`, `--webui.listen`), headless license-apply ritual, local-versus-LAN WebUI choices, and unsupported clone warnings. AnonSync should keep host role, continuity choice, identity posture, control exposure, and startup blockers visible in one place.

**Consequences:**
- bring-up work gains a stable review grammar and durable bring-up receipts
- workbench and CLI both need explicit host-role, continuity-choice, identity-posture, control-posture, and blocker sections
- fresh local-only start, attach existing state, recover/import, successor-sensitive continuity, and blocked bring-up remain visibly distinct public actions
- state-root, recovery, release, and access surfaces can escalate into bring-up review instead of hiding first-open meaning behind startup convenience


## ADR-079 — Browser-mediated control must degrade into explicit capability, integrity, and repair state

**Decision:** Missing browser/workbench controls, trust/bootstrap problems, and auth-repair work should compile to explicit public capability, integrity, and repair objects rather than disappearing buttons, unsafe browser ritual, or settings-file surgery.

**Why:** Current Resilio docs still spread Linux/WebUI control truth across browser compatibility notes, ad-block caveats, self-signed warning pages, manual link-paste fallback, and password-reset paths that can reset preferences or duplicate devices. AnonSync should keep control availability, client degradation, fallback channels, and auth repair visible in one place.

**Consequences:**
- browser-rendered control becomes one projection of server-declared capability state rather than the origin of semantics
- workbench and CLI both need explicit capability-availability, integrity-finding, and auth-repair sections
- ordinary control repair must preserve the difference between access-state change and broader reviewed bring-up/state-root transition
- Linux/headless deployments gain a clearer guarantee that browser failure cannot erase the only honest path to inspect or perform high-signal control actions


## ADR-080 — High-signal mutation needs one explicit reviewed authority object, not ambient browser/session continuity

**Status:** Accepted

**Why:** Current Resilio docs still blur mutation authority across optional workstation passwords, browser-session cookies, config-defined credentials, Linux/headless startup flags, localhost/LAN bind changes, and even service-account switches that can reopen a different storage root. AnonSync should keep inspectability and mutation authority visibly distinct.

**Decision:** Browser/workbench sessions are inspect-oriented by default. Non-trivial mutation requires either a short-lived reviewed mutation grant bound to subject scope, channel, endpoint, and state root, or a separately issued explicit mutate/admin credential object whose scope is already public enough to satisfy the same gate.

**Consequences:**

- dangerous apply paths must expose gate state rather than generic confirmation ritual
- mutation grants become receipt-bearing public objects with expiry and invalidation semantics
- endpoint, integrity, or state-root drift can invalidate reviewed elevation even if the browser session itself still exists
- CLI, TUI, browser/workbench, and API-backed automation need one shared mutation-authority truth


## ADR-081 — Local target ownership needs one reviewed custody contract, not hidden-marker folklore

**Decision:** AnonSync will model host-local target ownership through first-class target-custody records, binding-collision cases, and custody receipts rather than treating hidden internal markers or non-empty-path checks as the whole contract.

**Why:** Current Resilio docs still make `.sync` markers, `already added` checks, same-folder multi-instance collision, removable-disk reuse, and delete-and-re-add repair ritual carry too much ownership meaning. AnonSync should not let same-lineage reuse, foreign-marker inspection, successor claim, and blocked collision collapse into one path picker.

**Implications:**

- risky local target claims must be reviewable before marker rewrite or cleanup
- daemon/API must expose target ownership and lineage confidence directly where it can be inferred
- preservation requirements must be explicit before cleanup destroys easy ownership evidence
- GUI, CLI, TUI, and automation clients must share one fixed custody-review grammar



## ADR-082 — Safety-critical actions need one channel-parity contract, not surface-specific semantics

**Decision:** Safety-critical actions must keep one server-declared capability identity and one stable review grammar across browser/workbench, CLI, TUI, and API-backed control, with explicit handoff objects when a degraded channel cannot continue the action honestly.

**Why:** Current Resilio docs still spread action meaning across Linux/WebUI-only control, config-mode feature loss, disappearing share controls, manual link-paste fallback, and Linux WebUI preferences that ignore one destructive-action guard. AnonSync should not let channel choice decide whether a dangerous action exists or how it is reviewed.

**Consequences:**

- degraded channels must expose capability/degradation/handoff state rather than weaker local substitutes
- review handoffs become durable public objects with auditable continuity semantics
- workbench and CLI both need the same fixed channel-parity section order for safety-critical actions
- channel change can reopen broader review when endpoint, trust, or state-root meaning changes, but it must say so explicitly


## ADR-083 — Runtime-principal and service-seat changes need one reviewed continuity/reachability contract, not install-mode folklore

**Decision:** Non-trivial execution-seat changes should compile to one reviewed continuity/reachability model rather than depending on installer choices, service-account switching, mapped-drive caveats, UNC workarounds, or re-add/re-share ritual.

**Why:** Current Resilio docs still spread same-host runtime truth across current-user vs Local System / Local Service service modes, migrated-state vs clean install choices, mapped-drive invisibility for services, UNC fallback with degraded notifications, and storage roots that vary by service account. AnonSync should keep state continuity, reachable-target delta, notification/freshness posture, and clean-seat-versus-migrated outcome visible in one place.

**Consequences:**

- execution-seat work gains a stable review grammar and durable seat-switch receipts
- workbench and CLI both need explicit continuity, reachability, freshness, and fallout sections for runtime-seat changes
- service installs or principal switches can no longer masquerade as harmless backgrounding when they actually alter the host-local world
- degraded workaround posture such as rescan-only rebinds remains visibly distinct from true same-seat continuity

## ADR-084 — Human-facing labels must stay separate from authority identity and same-person continuity

**Decision:** Non-trivial naming work should compile to one reviewed label/identity continuity model rather than depending on unlink/new-certificate ritual, convenience linking, or remembered fingerprint lore.

**Why:** Current Resilio docs still spread naming/continuity meaning across identity-name-generated certificates, rename-via-unlink behavior, linked-device auto-approval reach, configured-device takeover during linking, mixed-version linking warnings, and local-only unlink limits. AnonSync should keep mutable labels, stable subject handles, cryptographic authority, alias history, and same-person continuity visibly distinct.

**Consequences:**

- naming work gains a stable review grammar and durable identity-label receipts
- workbench and CLI both need explicit current-label/authority, peer-visible fallout, and grant/constellation-fallout sections
- harmless relabel, alias preservation, successor continuity, and authority replacement remain visibly different public actions
- convenience linking can no longer masquerade as safe continuity proof when the real effect is trust or approval blast-radius change



## ADR-085 — Live namespace and managed sync state need one reviewed share-layout contract, not hidden-dotfolder folklore

**Decision:** Non-trivial share-layout work should compile to one reviewed live-namespace/annex/residue model rather than depending on hidden `.sync` state, `Archive` browsing, xattr stub files, or temp-suffix cleanup ritual as the operator contract.

**Why:** Current Resilio docs still place share identity markers, ignore policy, rollback/history storage, xattr carry-forward state, and in-flight residue directly in or beside the live tree through `.sync`, `.sync/Archive`, `.sync/StreamsList`, `.sync/Streams`, and `.!sync` conventions. AnonSync should keep ordinary user content, managed control bytes, rollback state, portability sidecars, and cleanup fallout visibly separate.

**Consequences:**

- share-layout work gains a stable review grammar and durable layout receipts
- workbench and CLI both need explicit live-namespace, annex-placement, and residue/cleanup sections
- annex migration and legacy cleanup can no longer masquerade as harmless hidden-file deletion
- storage, rollback, fidelity, and custody surfaces gain one shared place to say where the daemon's own bytes actually live for a share


## ADR-086 — Performance and compatibility changes need one reviewed semantic-fallback contract, not power-user-toggle folklore

**Decision:** Non-trivial optimization or degraded-target work should compile to one reviewed semantic-runtime model rather than depending on advanced settings, SMB caveats, watcher warnings, or rename folklore as the operator contract.

**Why:** Current Resilio docs still let lazy indexing, whole-file fallback, direct fast paths, notification loss, and degraded network-share posture quietly alter rename continuity, detection freshness, resumability, verification timing, or conflict honesty. AnonSync should keep those guarantee changes explicit.

**Consequences:**

- semantic runtime state gains a stable contract and receipt model
- workbench and CLI both need explicit guarantee-delta sections before meaning-changing optimization can apply
- degraded-target acceptance can no longer masquerade as harmless speed tuning
- future performance work must distinguish semantic-neutral tuning from reviewed semantic downgrade



## ADR-087 — Revoke/remove language needs one reviewed retained-copy and recall contract, not disconnect folklore

**Decision:** Non-trivial access narrowing, replica retirement, or share-removal work should compile to one reviewed retained-replica/recall model rather than depending on disconnect notes, linked-device scope, or encrypted-backup caveats as the operator contract.

**Why:** Current Resilio docs still let `Disconnect` mean `future updates stop while bytes remain`, let linked-device removal say nothing about non-linked peers that already have the share, and let encrypted backup usefulness depend on saved keys and database continuity while ordinary read-only/archive behavior tells a different story. AnonSync should keep future authority, retained bytes, recovery usefulness, and stronger recall claims explicit.

**Consequences:**

- retained-copy truth gains a stable review grammar and receipt model
- workbench and CLI both need explicit byte-retention and recall-verdict sections before revoke/remove-style actions can apply honestly
- linked-surface cleanup can no longer masquerade as universal recall
- future access, exit, and backup-preservation work must distinguish future-stop, retained-copy attestation, delete request, and observed stronger recall


## ADR-088 — Share-authority change needs one reviewed epoch-rotation contract, not key/re-share folklore

**Decision:** Non-trivial share-authority changes should compile to one reviewed authority-epoch model rather than depending on folder-class caveats, key-change notes, or derivative/local-share re-share ritual as the operator contract.

**Why:** Current Resilio docs still let Standard/key-backed and Advanced/certificate-backed shares behave materially differently for permission mutation and reissue, still say key changes do not propagate automatically, and still require remove-and-re-share in some derivative/local-share cases. AnonSync should keep new authority issuance, stale capability residue, derivative migration, and mixed-epoch convergence explicit.

**Implications:**

- share authority gains stable epoch objects, rotation reviews, and rotation receipts
- workbench and CLI both need explicit epoch maps, stale-capability findings, and convergence verdicts before rotation-style actions can apply honestly
- derivative/local-share fallout can no longer masquerade as implementation trivia when it changes what must be rebuilt or reissued
- future compromise, recall, and share-class work must distinguish new-epoch issuance from observed clean retirement of old authority


## ADR-089 — Observer/read-only posture needs one reviewed contract, not permission-label folklore

**Decision:** Non-trivial observer, read-only, viewer, or receive-only semantics should compile to one reviewed observer-posture model rather than depending on permission labels, overwrite-changed-files notes, linked-device workarounds, or local-share caveats as the operator contract.

**Why:** Current Resilio docs still let `read only` mean `local edits suspend sync`, optionally `local edits are overwritten`, unavailable for some linked-device/Advanced-folder combinations, and inherited differently by local shares. AnonSync should keep byte visibility, local-write behavior, onward serving, and projection/class limits explicit.

**Implications:**

- observer posture gains stable contracts, reviews, and receipts
- workbench and CLI both need explicit visibility/write/serve/limit sections before observer-style changes can apply honestly
- local repair helpers can no longer masquerade as universal behavior when projection mode disables them
- future grant, derivation, selective-materialization, and recall work must distinguish non-authoritative writing from non-serving and from byte invisibility


## ADR-090 — Non-empty target bind work needs one reviewed reconciliation contract, not `Folder not empty` folklore

**Decision:** Adopting, repairing, or relocating a share into a populated target must expose one reviewed reconciliation contract whenever same-path divergence, ambiguous lineage, or encrypted-target mismatch is present.

**Why:** Current Resilio docs say reconnect can reuse an old directory by ignoring the non-empty warning, that pre-populated folders are hashed and merged while same-named divergent files let the latest timestamp win, and that encrypted-folder intake into a non-empty target can ignore existing plaintext bytes or archive previously encrypted ones. AnonSync should not inherit one small confirmation box as the operator contract for those materially different outcomes.

**Implications:**

- compare counts alone are not the full contract once same-path divergence exists
- timestamp freshness may contribute evidence, but it is not a hidden trustworthy winner rule
- same-lineage reuse, harmless merge, reviewed replacement, and encrypted-target mismatch remain visibly distinct outcomes
- apply emits a reconciliation receipt that proves the chosen lineage and candidate-handling result later


## ADR-091 — Visibility and retrievability are separate public contracts

**Decision:** Introduce explicit fetchability/full-copy-witness objects so placeholder visibility, names-only visibility, and durable byte retrievability never collapse into one casual `available on demand` claim.

**Why:** Current Resilio docs say Selective Sync can expose placeholders without full bytes, reverting files to placeholders can leave nobody with a real file if every peer does it, `Clear synced files` can dematerialize an entire local share, and ghost announcements can persist after no peer still has the bytes. AnonSync should not force operators to reconstruct whether a visible path is actually fetchable from placeholder state plus troubleshooting warnings.

**Consequences:**

- fetchability, full-copy witnesses, local-last-copy risk, and ghost-announcement posture become explicit reviewed state
- evict/clear/pin/fetch actions can fail closed when they would remove the last known full copy or rely on stale announcement-only visibility
- workbench, CLI, and API can render the same honest answer to `can I still get the bytes later?` without support-article archaeology



## ADR-092 — File availability must be a concrete interface contract, not only a conceptual truth

**Decision:** Every serious file/subtree availability surface must render one compact answer strip, one reviewed detail grammar, and one mixed-risk batch model rather than leaving clients to improvise around placeholder state.

**Why:** `rev0078` established that visibility, local residency, full-copy witnesses, and fetchability are different truths. Without a concrete interface contract, clients can still collapse those truths back into one optimistic `available on demand` label or one misleading bulk action.

**Consequences:**

- workbench, CLI, and API-backed clients inherit one stable availability reading order
- mixed-risk subtree actions split by witness/fetchability class before apply
- receipts can later prove not just that an action happened, but which availability truth justified it

## ADR-093 — Availability surfaces need an explicit action matrix, not just state chips

**Decision:** Availability reports must carry explicit per-row and per-selection action offers so the primary verb changes with the risk class instead of being invented independently by each client.

**Why:** `rev0079` made file availability a concrete interface contract, but an honest answer strip still leaves one dangerous gap if clients can keep rendering the same optimistic `Fetch` or `Evict` button after the posture has already changed to local-last-copy, history-backed-only, or stale visibility. The product needs an explicit action contract, not just posture chips.

**Consequences:**

- clients receive row-level action offers such as `fetch-now`, `pin-locally`, `restore-from-history`, or `retire-stale-announcement`
- mixed-selection bars may only label the safe subset they can mutate honestly
- history-backed-only rows no longer masquerade as ordinary on-demand fetch cases


## ADR-094 — Availability rows must keep state, source, and verb adjacent, and direct action must be gated by risk class

**Decision:** Availability rows and cards must expose local truth, source/recovery truth, and next honest action in one adjacent presentation contract, and only clearly safe rows may offer one-click mutation without opening review.

**Why:** `rev0080` made the action matrix explicit, but a safer model can still regress if a dense table hides source posture in one column, action in another menu, and review state somewhere else. The operator needs to see the honest verb near the row it belongs to, and the UI needs one cross-client rule for when inline action is allowed versus when review is required.

**Consequences:**

- row/action contracts gain presentation hints such as `inline-direct`, `inline-review`, and `blocked`
- workbench, CLI, and compact/mobile clients inherit the same direct-action threshold instead of inventing their own
- guarded/history-backed/stale rows pivot naturally into review instead of pretending to support the same one-click action shell as safe rows



## ADR-095 — Share announcement, local claim, and local bind must be separate durable objects

Resilio's current linked-device docs still show a useful but too-entangled convenience model:
shares become visible everywhere across the linked set, careful custom placement often routes through `Disconnected`, duplicate-index directories can appear from default-location behavior, and removing a disconnected item can affect all linked devices.
Those are not fatal flaws.
They are evidence that announcement, claim, bind, and wider withdraw still live too close together.

AnonSync therefore chooses a stricter contract:

- a share may become visible on a machine without creating a local path
- a machine may defer or hide that visibility locally without pretending wider authority changed
- claiming a share is a durable local decision object
- binding a claim into a path is a distinct act with its own compare/preflight/reconciliation hooks
- wider withdrawal must stay visibly different from local hide

Consequence:
incoming objects, claims, receipts, and workbench surfaces must preserve these distinctions explicitly, even on dense/mobile/textual surfaces.

## ADR-096 — Approval convenience must expose acting seat and horizon, not just a generic `Approve` button

Resilio's current docs still show a useful but too-entangled approval model:
linked devices act as Owners for the user's own shares, a request can be approved from any linked device where the folder is active, and a remote user can choose to auto-approve all linked devices for future sharing after approving one.
Those are not fatal flaws.
They are evidence that acting seat, current-subject approval, and future approval memory still live too close together.

AnonSync therefore chooses a stricter contract:

- every approval-worthy request names the acting seat explicitly
- `approve once` and `approve for reviewed scope` are different durable actions
- seat changes may alter admissible horizon and must render that delta explicitly
- future approval memory may never be created by implication from a generic `Approve` action
- approval receipts must later prove which seat spoke and what horizon was accepted

Consequence:
approval queues, review panes, CLI verbs, API objects, and receipts must preserve seat/horizon truth explicitly, even on dense/mobile/textual surfaces.


## ADR-097 — Remembered approval must match explicitly and admit narrowly, not silently complete later local acts

### Status

Accepted

### Context

The archive already says that acting seat and approval horizon must be explicit at the live approval moment.
What still remained too easy to blur was what happens later when a new arrival matches prior trust.
Current Resilio docs still say prior approval can make later pending folders auto-connect, prior approval may be retained with identity/certificate for later sharing, and approval can be widened to linked devices for future sharing.
That is useful convenience, but it leaves too much room for remembered trust to silently explain later local state changes.

### Decision

AnonSync will model remembered-trust reuse through explicit approval-match objects and review surfaces.
A match may authorize only narrow outcomes such as `identity-only`, `queue-admitted`, or `claim-suggested`.
A match will not, by itself, choose a path, create a bind, materialize bytes, or widen rights.
Those later local acts remain separate reviewed outcomes with their own receipts.

### Consequences

Positive:

- remembered trust remains useful without becoming magical
- incoming-share convenience stays compatible with least privilege and truthful local-claim semantics
- later audit can prove whether the product merely recognized prior trust or actually changed local state

Negative:

- some flows will feel less magical than auto-connect products
- the model adds approval-match objects and receipts that simpler products hide
- operators may sometimes feel they are doing one extra explicit claim step after a helpful match


## ADR-098 — local share posture and future-arrival policy must be decomposed, not flattened into one mode field

**Decision:** AnonSync will expose current local share posture and future-arrival policy as separate durable objects and review surfaces instead of using one monolithic mode label.

**Why:** Current Resilio docs still show `Disconnected`, `Selective Sync`, and `Synced` as useful convenience labels, but those same docs also keep using them to imply future-arrival handling, default-location behavior, custom-location workflow, and collision fallback. An inspectable product should not force operators to infer whether they changed the current share, later arrivals, or both from one `change mode` action.

**Consequences:**

- current share posture, future-arrival defaults, and path provenance become first-class public model elements
- seat-level convenience can still exist, but it must state whether it affects current subjects, future arrivals, or both
- workbench, CLI, and API can all render `change current share here` separately from `change what happens next time here`


## ADR-099 — path suggestion and collision fallback need one reviewed placement contract, not `Connect` folklore or silent duplicate suffixes

**Decision:** Treat candidate placement as an explicit suggestion/review/receipt pipeline.

**Why:** Current Resilio docs still show default roots, `Disconnected`/`Connect`, and duplicate `(1)` folders doing too much work in the operator story. AnonSync should preserve helpful path suggestions without letting suggestion, commitment, and collision fallback blur together.

**Implications:**

- candidate paths are explicit objects with suggestion basis and collision class
- same-lineage adoption and alternate-path choice are explicit reviewed outcomes
- a one-share alternate path does not silently rewrite future templates/defaults
- placement receipts must prove which candidate won, which candidates were rejected, and whether defaults changed


## ADR-100 — standing future-arrival defaults need one reviewed template-governance contract, not scattered mode/default/simple-mode folklore

### Status
Accepted

### Context

The archive already separates current share posture from future-arrival policy and one-share placement review from broader defaults.
Current Resilio docs still show standing future-arrival behavior spread across linked-device modes, default-folder settings, custom-location reconnect ritual, and Android `Simple mode`.
That is practical convenience, but it still leaves operators reconstructing one seat's future behavior from several scattered knobs.

### Decision

AnonSync will model standing future-arrival behavior as an explicit seat-template policy with explicit governance review, explicit effect buckets, explicit pinned exceptions, and explicit receipts.
Changing this template will never silently relocate already bound shares.
Refreshing existing unclaimed drafts will require its own explicit choice.

### Consequences

- clients gain one public object for standing convenience instead of inferring it from current-share actions
- policy changes can preview future unseen arrivals separately from open drafts and bound shares
- mobile/dense clients may compress wording, but they must still preserve governed scope and unchanged-subject guarantees
- the product avoids recreating `change mode` / `default folder` folklore as a hidden control plane for future arrivals


## ADR-101 — later-arrival convenience must compile to one explicit explanation surface

### Status
Accepted

### Context

The archive now separates announcement, approval memory, standing seat templates, claim, placement, and bind.
What still remained too easy to hide was the operator question that comes after those decisions already exist: why is this subject in this stage on this machine right now?
Current Resilio docs still answer that question only indirectly through linked-device visibility, remembered approvals, pending-folder auto-connect behavior, standing modes, default roots, and later `Connect` ritual.

### Decision

AnonSync will require one first-class arrival-explanation surface for later-arrival subjects.
That surface must render current stage, causal chain, governing standing state, explicit non-causes, counterfactuals, next honest verbs, and proof links in one place.
Remembered approval and standing template may explain lower friction or drafted candidates, but they must explicitly say whether they changed local state or merely influenced review posture.

### Consequences

Positive:

- later-arrival convenience becomes auditable rather than magical
- support burden falls because `why here now` has one public answer surface
- richer and denser clients can share one explanation contract without inventing new semantics

Negative:

- the model adds one more read projection family and counterfactual machinery
- some compact surfaces will need to spend space on non-causes and counterfactual entry points
- implementers have to keep explanation recomputation aligned with the underlying state graph so stale summaries do not mislead


## ADR-102 — standing-policy edits need one explicit retroactivity preview contract

### Status
Accepted

### Context

The archive now separates standing templates, remembered approval, current share posture, path bind, and later-arrival explanation.
What still remained too easy to blur was the mutation boundary when one of those standing defaults changes.
Current Resilio docs still answer that boundary only indirectly through linked-device modes, default roots, remembered approval, pending-folder auto-connect, and Android `Simple mode`, while also noting that selected mode changes apply to newly added folders and current ones remain as they are.

### Decision

AnonSync will require one first-class policy-delta preview surface for meaningful standing-policy edits.
That surface must render governed scope, proposed delta, effect buckets, named example subjects, explicit non-effects, honest apply labels, and proof links in one place.
A standing-policy mutation may alter future unseen arrivals immediately, may optionally refresh some open drafts, and may require subset review for some claimed subjects, but it must explicitly prove when bound subjects and current bytes stay untouched.

### Consequences

Positive:

- operators can review retroactivity directly instead of inferring it from folklore
- safer `future only` versus `refresh drafts` versus `subset review` labels become portable across GUI, CLI, and mobile
- the non-clone case against Resilio stays focused on contract shape rather than pretending the product lacks convenience

Negative:

- the model adds one more preview family and simulation/projection cost
- compact clients must spend space on explicit non-effects and named examples
- implementers must keep effect buckets aligned with live subject state so previews do not go stale or misleading



## ADR-103 — standing-policy families need explicit version lineage and per-subject attribution

### Status
Accepted

### Context

The archive now previews standing-policy edits before apply and explains why later-arrival subjects are here now.
What still remained too easy to lose was the link between those two surfaces after time passes.
Current Resilio docs still make this seam concrete by describing standing modes, remembered approval, later auto-connect behavior, and default-root/mobile placement semantics in ways that are useful in the moment but still leave older subjects explained mostly by reconstruction.

### Decision

AnonSync will model every meaningful standing-policy family as a versioned lineage with explicit supersession and explicit per-subject attribution.
A client must be able to show the current effective version, the applied version that handled one subject, the semantic difference between them, and the receipts that prove both the policy transition and the subject stage.

### Consequences

Positive:

- operators can tell whether a subject matches current policy or is truthfully grandfathered
- later support and audit work no longer depend on comparing current settings with memory
- policy-delta preview and arrival explanation now connect through one durable version model

Negative:

- the model adds one more read family and more historical indexing
- compact clients must spend some space on version and attribution chips
- implementers must keep lineage/attribution recomputation aligned with mutations so stale compare projections do not mislead



## ADR-104 — standing-policy families need explicit drift classification and reviewed realignment

### Status
Accepted

### Context

The archive now previews standing-policy edits, explains why subjects are here now, and preserves version lineage after policy changes.
What still remained too easy to lose was the operational step after that: deciding which current differences are intentional, which are safe to refresh, and which need stronger review.
Current Resilio docs still make this seam concrete by saying new folders follow the chosen linked-device mode while current ones remain as they are, while later auto-connect, universal visibility, and default-placement ritual can keep the estate heterogeneous over time.

### Decision

AnonSync will model post-lineage operational drift explicitly.
Every meaningful standing-policy family must expose a drift-population view, per-subject drift classes, reviewed realignment plans, and durable exception-pin receipts where intentional divergence is kept.

### Consequences

Positive:

- operators can tell whether a non-current subject is refreshable, intentionally grandfathered, pinned as an exception, or blocked
- policy lineage becomes operationally useful instead of purely historical
- mixed realignment batches no longer need one misleading umbrella action

Negative:

- the model adds another read/mutation family and more classification work
- compact clients must spend some space on drift classes and split action bars
- implementers must keep drift classification aligned with lineage, current state, and exception pins so stale rows do not mislead



## ADR-105 — intentional exceptions need explicit aging, renewal, and re-review

### Status
Accepted

### Context

The archive now previews standing-policy edits, preserves lineage, and classifies live drift with reviewed realignment.
What still remained too easy to lose was the lifecycle after an operator intentionally keeps an older outcome.
Current Resilio docs still make this seam concrete by retaining person-approval memory, allowing later auto-connect after prior approval, and allowing future linked-device approval widening, but without one explicit review-horizon contract for those remembered conveniences.

### Decision

AnonSync will model intentional non-current outcomes as aging reviewed state.
Every meaningful standing-policy family that permits `keep grandfathered` or `pin exception` must expose exception-aging rows, review horizons or explicit no-expiry acknowledgements, renewal/reconsideration review plans, and durable exception-review receipts.
Reaching a review horizon may raise urgency or queue review, but it must not silently mutate binds, bytes, or authority.

### Consequences

Positive:

- operators can tell whether an intentional exception is healthy, due soon, overdue, or explicitly acknowledged as no-expiry
- pinned exceptions stop behaving like immortal background clutter
- remembered convenience stays auditable over time instead of turning into silent forever-policy

Negative:

- the model adds another review family and more queue pressure
- compact clients must spend some space on aging class and horizon facts
- implementers must keep review-horizon computation aligned with drift, lineage, and current state so stale due-soon signals do not mislead

## ADR-106 — remembered approval needs explicit freshness, cooling, and touch-renewal

### Status

Accepted

### Context

The archive already had first-approval review, later matched-arrival guardrails, policy lineage, drift classification, and exception aging.
What still remained under-specified was remembered approval itself.
Without one explicit freshness lifecycle, old approval would keep behaving like timeless convenience memory, especially after dormancy, linked-device growth, or scope change.

Current Resilio docs still make that seam concrete in a useful way: approve-once identity retention, future auto-approval across linked devices, and later auto-connect after prior approval all remain convenient, but they still lack one first-class surface for cooling, freezing, or reviewed touch renewal of remembered trust itself.

### Decision

Every meaningful remembered-approval family that can influence later arrivals must expose approval-memory freshness rows, cooling reasons, reviewed touch-renewal or narrowing plans, and durable freshness receipts.

Freshness is not the same thing as arrival claim.
Touch renewal must therefore remain a trust-memory mutation only; it may not silently claim, bind, materialize, or widen scope.

### Consequences

- remembered approval is now a lifecycle object rather than immortal background memory
- later-arrival explanation must include the freshness posture of the matched trust, not merely the existence of a match
- dense/mobile clients must keep `fresh`, `warm`, `cooling`, `stale`, `frozen`, `revoked`, and `unknown` visibly distinct
- any batch trust-refresh surface must split rows by truthful reviewed outcome rather than flattening them into `keep approved`


## ADR-107 — remembered approval needs explicit lineage and subject-level authorization trace

### Status

Accepted

### Context

The archive already had first-approval review, later matched-arrival guardrails, approval-memory freshness, and touch renewal.
What still remained under-specified was attribution.
Without one explicit lineage and authorization-trace model, the operator could know that trust was still fresh enough to matter while still not knowing which exact old approval act or later trust mutation actually authorized the current convenience.

Current Resilio docs still make that seam concrete in a useful way: approval can be retained with identity, approvals can be issued from any linked device, future linked devices can be auto-approved after one approval, later pending folders can auto-connect after prior approval, and approval-time details are visible at request review time. That is useful provenance material, but it is still not one first-class later trace surface.

### Decision

Every meaningful remembered-approval family that can influence later arrivals must expose explicit lineage nodes, ordered authorization history, and per-subject authorization-trace explanations.
Later trust mutations must supersede by adding lineage, not by overwriting origin history.
A later subject that cites remembered trust must be able to point to one explicit authorization node or else surface `unknown` attribution posture.

### Consequences

- remembered approval is now an attributable lineage rather than only a freshness-colored memory
- later-arrival explanation must include which trust node authorized the subject, not merely that prior approval existed
- dense/mobile clients must preserve origin-versus-current-head distinctions even when they compress wording
- missing trust provenance becomes an explicit proof problem rather than a guessed success story

## ADR-108 — remembered approval must support family split/rebase after constellation mutation

### Status
Accepted

### Context

The archive now preserves approval freshness, lineage, authorization trace, and current-vs-historical trust comparison.
What still remained too easy to lose was the effect of identity/constellation mutation on old remembered approval itself.
Current Resilio docs still make this seam concrete by saying all linked devices act as Owners, approvals can be issued from any linked device, one approval can expand to all linked devices for future sharing, hidden offline devices can later reappear without having been unlinked, linking already-initialized devices can cause certificate takeover, and remote unlink is not available.

### Decision

AnonSync will model remembered approval as a family that may need reviewed rebase after constellation mutation.
Every meaningful remembered-approval family affected by identity/constellation change must expose a triggering mutation, descendant postures, reviewed rebase plans, and durable rebase receipts proving whether the family stayed intact, split into child families, froze descendants, or now requires fresh approval for selected descendants.

### Consequences

Positive:

- operators can tell whether hidden-device return or certificate takeover changed future trust reuse without losing historical explanation
- trust continuity becomes reviewable rather than ambient when the device set behind an identity changes
- future reuse and historical explanation stay separate after constellation mutation

Negative:

- the model adds another trust-lifecycle family and more descendant bookkeeping
- compact clients must spend some space on mutation triggers and descendant outcomes
- implementers must keep rebase logic aligned with freshness, lineage, identity epochs, and constellation membership so stale descendant posture does not mislead

## ADR-109 — remembered-trust descendants must expose liveness and confidence separately from family membership

### Status
Accepted

### Context

The archive now preserves approval freshness, lineage, authorization trace, family rebase, and descendant postures after constellation mutation.
What still remained too easy to overstate was present-tense descendant reality.
Current Resilio docs still make this seam concrete by saying selective-sync fetch requires at least one online peer with the files, peer lists distinguish online peers from peers ever seen, hidden offline devices may later reappear, and ghost-file guidance shows that visible names can outlive current byte sources.

### Decision

AnonSync will model descendant liveness as a first-class layer separate from remembered-family membership.
Every meaningful remembered-trust descendant must expose a liveness class, confidence class, evidence basis, current honest role, reviewed liveness-refresh outcomes, and durable receipts proving whether the descendant is live observed, recently live, reachable but unproven, hidden awaiting return, reappeared awaiting proof, historical only, or unknown.

### Consequences

Positive:

- operators can tell when remembered-trust family membership is historical explanation rather than current operational convenience
- byte-source and approval-seat claims become evidence-backed instead of implied by lineage or placeholder presence
- reappeared descendants can remain visible without silently regaining strong convenience rights

Negative:

- the model adds another per-descendant posture family and more witness bookkeeping
- compact clients must spend some space on liveness/confidence rather than only inheritance posture
- implementers must keep liveness evidence aligned with fetchability, dormant-return, and trust-lineage receipts so present-tense claims do not outrun proof

## ADR-110 — descendant liveness must stay separate from per-subject role eligibility

### Status
Accepted

### Context

The archive now preserves approval freshness, lineage, authorization trace, family rebase, descendant liveness, and reachability confidence.
What still remained too easy to over-claim was present-tense subject capability.
Current Resilio docs still make this seam concrete by saying approvals can be issued from any linked device where the folder is active, all linked devices act as Owners, later pending folders can auto-connect after prior approval, and selective-sync fetch still requires at least one online peer with the bytes.

### Decision

AnonSync will model descendant role eligibility as a first-class layer separate from family membership and separate from liveness.
Every meaningful remembered-trust descendant considered for a governed subject must expose a candidate role, an eligibility class, a proof basis, reviewed capability outcomes, and durable receipts proving whether that descendant may honestly count as a byte source, an approval seat, both, or neither for the subject now.

### Consequences

Positive:

- operators can tell when a live linked descendant is still not actually eligible to approve or serve the governed subject
- byte-source and approval-seat claims become explicitly per-subject instead of ambient device folklore
- remembered approval, linked ownership, and live presence remain useful evidence without silently becoming the verdict

Negative:

- the model adds another per-descendant/per-subject posture family and more proof bookkeeping
- compact clients must spend some space on candidate-role and eligibility language instead of a vague `available` badge
- implementers must keep capability proofs aligned with liveness, approval-seat review, fetchability, and policy narrowing so subject-specific claims do not outrun evidence


## ADR-111 — remembered approval reuse must stay separate from subject-level fresh-approval override policy

### Status
Accepted

### Context

The archive now preserves approval freshness, lineage, authorization trace, family rebase, descendant liveness, descendant capability, and per-subject role eligibility.
What still remained too easy to over-claim was approval reuse itself.
Current Resilio docs still make this seam concrete by saying later pending folders can auto-connect after prior approval, approval can be retained with a person's identity, linked devices can broaden future approval reach, and the share dialog can separately require approval from `all peers` even when they were approved before.

### Decision

AnonSync will model subject-level approval-reuse precedence as a first-class layer separate from standing remembered approval and separate from descendant capability.
Every meaningful governed subject that might inherit old approval convenience must expose a standing reuse candidate, a subject reuse policy, a precedence outcome, a winning-rule explanation, reviewed override outcomes, and durable receipts proving whether remembered approval may or may not be reused for that subject.

### Consequences

Positive:

- operators can tell when old approval still exists but this subject intentionally requires fresh approval anyway
- share/offer security policy stops being hidden folklore and becomes an inspectable part of the approval surface
- descendant eligibility remains useful evidence without silently becoming permission to skip review

Negative:

- the model adds another subject-level policy layer and more precedence bookkeeping
- compact clients must spend some space on subject-policy and winning-rule language instead of a vague `already approved` badge
- implementers must keep reuse-policy precedence aligned with freshness, lineage, capability, and actual approval actions so lower-friction paths do not outrun the governing subject policy


## ADR-112 — portable invitation lifetime must stay separate from durable trust promotion

### Status
Accepted

### Context

The archive now preserves offer-artifact semantics, approval freshness, authorization lineage, descendant capability, and subject-level reuse-policy precedence.
What still remained too easy to over-claim was the afterlife of a successful invitation.
Current Resilio docs still make this seam concrete by saying share links can expire after `N` days or `N` uses while other current docs still say approval is retained with a person's identity for later sharing and that approval mints certificate-backed access.

### Decision

AnonSync will model offer-artifact trust promotion as a first-class layer separate from artifact redemption lifetime and separate from later subject-level reuse-policy precedence.
Every meaningful portable invitation that can survive its own redemption as durable remembered approval must expose artifact terminal posture, claim outcome, promotion posture, promotion-scope basis, later-reuse posture, reviewed promotion outcomes, and durable receipts proving what trust survived the invitation and what did not.

### Consequences

Positive:

- operators can tell when a single-use or expiring invitation admitted one subject without silently creating broad remembered approval
- offer-artifact controls remain useful without having to carry all later trust semantics by implication
- later approval reuse can still exist, but only after explicit promotion and later reuse-policy checks

Negative:

- the model adds another after-claim posture family and more receipt bookkeeping
- compact clients must spend some space on artifact-lifetime versus trust-lifetime language instead of a vague `invite used` badge
- implementers must keep promotion outcomes aligned with offer policy, approval actions, subject reuse policy, and approval-memory lineage so later convenience does not outrun reviewed scope

## ADR-113 — sender intent, actual redeemer identity, and durable trust must stay separate for portable offers

### Status
Accepted

### Context

The archive now preserves portable-offer lifetime, trust-promotion boundary, approval freshness, authorization lineage, descendant capability, and subject-level reuse precedence.
What still remained too easy to over-claim was *who the offer was really redeemed by*.
Current Resilio docs still make this seam concrete by saying share links can be copied into messenger or e-mail, any peer with the link can auto-connect when approval is disabled, and approval review plus link flow identify the actual requester by name/fingerprint/public key and then mint certificate-backed access.

### Decision

AnonSync will model recipient intent and actual redeemer identity as a first-class layer separate from portable-offer lifetime and separate from durable trust promotion.
Every meaningful portable offer that can travel by possession must expose sender-intent posture, actual redeemer proof, match class, reviewed mismatch outcomes, and durable receipts proving what trust boundary followed from that exact redeemer.

### Consequences

Positive:

- operators can tell whether the person/device who redeemed the offer is actually the one the sender meant it for
- portable-offer convenience remains useful without pretending successful redemption automatically satisfied sender intent
- later remembered approval can be traced back to one exact redeemer and one explicit mismatch decision

Negative:

- the model adds another offer-side provenance layer and more receipt bookkeeping
- compact clients must spend some space on `for` versus `redeemed by` language instead of a vague `accepted` badge
- implementers must keep mismatch outcomes aligned with claim receipts, trust-promotion outcomes, and later reuse policy so broad convenience does not outrun reviewed intent


## ADR-114 — portable-offer budget and per-redemption trust must stay separate

**Status:** Accepted

**Context:** Current Resilio docs still combine useful but separable ideas: a link may be used only `N` times by whoever, some peers may auto-connect based on prior approval, and successful approval generates certificate-backed access for the actual requester. Once more than one redeemer hits the same artifact, operators otherwise have to reconstruct from use-counts, approval dialogs, and later remembered approval which identities consumed which budget and what trust survived.

**Decision:** AnonSync will model multi-use offer history through first-class redemption-ledger rows, ordered attempt entries, budget explanations, and trust-fanout receipts instead of leaving that story inside raw offer history.

**Consequences:**

- artifact budget becomes a first-class surface distinct from per-redeemer trust meaning
- `partially consumed` becomes its own stable public state
- later remembered approval can trace back to one exact successful redemption attempt rather than only to the parent artifact
- UI/API must support `reissue new artifact` as a first-class safe action when mixed attempt history exists

## ADR-115 — redemption equivalence and slot treatment must be first-class

**Status:** Accepted

**Context:** Current Resilio docs still combine bounded-use links, prior-approval reuse, and per-requester approval identity in a way that leaves one remaining accounting seam: once a familiar redeemer hits the same artifact again, operators otherwise have to reconstruct whether the later event was a replay, the same reviewed seat on the same subject, the same known peer on a new subject, or a genuinely distinct redeemer that deserves a fresh slot.

**Decision:** AnonSync will model redemption equivalence and slot treatment as a first-class layer with explicit equivalence rows, accounting explanations, reviewed outcomes, and receipts instead of leaving slot consumption to raw attempt order or vague `already approved` language.

**Consequences:**

- remaining budget becomes a first-class fact but not the only fact
- familiar redeemers still need explicit equivalence class and slot-effect language
- replay collapse, fresh-slot consumption, and `require new artifact` become distinct reviewed outcomes
- UI/API must support comparison-attempt links and accounting receipts whenever portable-offer history matters


## ADR-116 — successor artifacts must have explicit predecessor lineage and budget-reset truth

**Status:** Accepted

**Context:** Current Resilio docs still say expired links require a new link from the owner, bounded-use links fail at `N+1`, and remembered approval can still survive separately across later sharing. Once the product already knows the right answer is `require new artifact`, operators otherwise still have to reconstruct whether the replacement is just another wrapper for the same invitation story or a genuinely fresh boundary with narrower policy and reset budget.

**Decision:** AnonSync will model reissue lineage and successor-boundary review as a first-class layer with predecessor posture, successor relation, budget-reset posture, explicit carry-forward summaries, non-carry summaries, and durable successor-boundary receipts.

**Consequences:**

- `reissue new artifact` becomes a reviewable governance act rather than a shallow convenience verb
- successor artifacts can honestly say whether they are same-scope, narrowed, broadened, fresh-scope, or delivery-only
- delivery-only copies stop masquerading as fresh budget islands
- UI/API must support predecessor/successor receipts so later audit can tell what really changed at reissue time


## ADR-117 — delivery preview must stay separate from authoritative local intake

### Status

Accepted

### Context

Portable offers now have first-class objects for sender intent, actual redeemer identity, budget, multi-redemption history, slot treatment, and successor lineage.
One remaining seam still risked collapsing too much into one vague story: browser landing pages, QR overlays, clipboard intake, and external-app handoff can show useful preview information before the local app has actually performed authoritative inspection.

Current Resilio docs make that seam real in a useful way: links open a landing page that shows basic folder info, may immediately transfer into the app if protocol launch is already trusted, and keep the `#` fragment out of the landing-page request.
That is useful convenience and useful privacy posture, but it still leaves too much room for an operator surface to blur `previewed outside the app` with `authoritative inside the app`.

### Decision

AnonSync will model **delivery events** separately from offer artifacts, claim preparation, and later trust consequences.
Every portable-offer intake path must preserve at least these distinct public facts:

- delivery channel
- preview surface
- external-touch posture
- handoff posture
- preview-authority posture
- authoritative offer reference once local parsing succeeds

The interface must keep preview hints, local parse results, and authoritative review truth visibly separate.
`Opened in browser`, `auto-launched app`, or `previewed folder name` can never stand in for trust, byte availability, claim readiness, or remembered approval.

### Consequences

Positive:

- browser/app convenience remains usable without becoming trust folklore
- external-touch privacy posture becomes inspectable public state
- later audit/support work can reason from delivery receipts instead of browser-memory guesswork

Costs:

- intake surfaces gain one more layer of row/detail state
- APIs and logs need a delivery-event object family in addition to offer and claim objects
- lightweight clients must compress the story carefully without hiding the preview-versus-authority boundary

### Alternatives rejected

- treat browser landing-page preview as just another offer inspect result
- bury delivery provenance only in debug logs
- collapse `auto-opened successfully` into a generic success badge


## ADR-118 — carrier aliases must collapse into canonical artifact identity before later semantics are inferred

### Status

Accepted

### Context

Portable offers now have first-class objects for sender intent, redeemer identity, artifact budget, repeated-attempt equivalence, successor lineage, and delivery/handoff provenance.
One remaining seam still risked collapsing too much into one vague story: the same offer may appear through browser wrapper URLs, protocol rewrites, QR encodings, clipboard copies, or later file wrappers.

Current Resilio docs make that seam real in a useful way: links use an `https://link.resilio.com/...#...` wrapper, the landing page may rewrite that wrapper to `btsync://` for the app, the `#` fragment is not sent to the server, and the same share can also be delivered as copied text or QR.
That is useful convenience, but it still leaves too much room for a surface to blur carrier convenience with artifact identity.

### Decision

AnonSync will model **carrier aliases** separately from canonical offer identity, delivery events, claim objects, and successor artifacts.
Every meaningful portable-offer surface must preserve at least these distinct public facts:

- canonical artifact reference
- carrier kind
- carrier authority posture
- equivalence posture
- normalization basis
- explicit non-effects on budget/trust/lineage

Budget, trust consequence, successor lineage, and later audit attach to the canonical artifact identity, not to whichever carrier happened to be observed last.

### Consequences

Positive:

- browser wrapper, protocol handoff, QR, and copied text can all stay convenient without forking hidden artifact stories
- delivery-only re-encoding stops masquerading as reissue
- later audit/support work can reason from canonical artifact receipts instead of browser-history guesswork

Costs:

- intake surfaces gain one more layer of alias/detail state
- APIs and logs need a carrier-alias object family in addition to offer and delivery-event objects
- lightweight clients must compress the story carefully without hiding whether the current carrier is authority-bearing or merely a wrapper

### Alternatives rejected

- treat whichever carrier last reached the seat as the artifact identity
- bury alias normalization only in debug logs
- infer `same offer` from folder-name hints or familiar wrapper shape alone


## ADR-119 — preview-visible hints must remain separate from sealed and authoritative offer fields

### Status

Accepted

### Context

Portable offers now have first-class objects for delivery provenance, canonical artifact identity, carrier aliases, redemption accounting, and successor lineage.
One remaining seam still risked collapsing too much into one vague story: some surfaces may show recognition hints before local parse, while authority-bearing or policy-bearing fields stay sealed until the app ingests them.

Current Resilio docs make that seam real in a useful way: the landing page can show basic folder info, the wrapper may hand off into the app, and the `#` fragment is not sent to the server.
That is useful convenience, but it still leaves too much room for a surface to blur preview familiarity with authoritative field truth.

### Decision

AnonSync will model **offer field provenance and field partition** separately from carrier alias identity, delivery events, claim objects, and later approval artifacts.
Every meaningful portable-offer surface must preserve at least these distinct public facts:

- field semantic role
- field exposure posture
- field authority posture
- which later actions may rely on the field
- which later actions explicitly may not rely on the field
- receipts proving that partition

Alias collapse, local parse, claim review, and trust review must not erase the earlier fact that some fields were only hints while others stayed sealed until parse.

### Consequences

Positive:

- preview convenience remains useful without becoming authority folklore
- sealed authority-bearing material becomes explainable rather than mysterious
- later governance decisions can cite exact field classes instead of over-reading preview familiarity

Costs:

- intake surfaces gain one more compact strip or drawer of state
- APIs and logs need a field-provenance object family in addition to offer, delivery-event, and carrier-alias objects
- lightweight clients must compress the story carefully without hiding non-inference boundaries

### Alternatives rejected

- treat any previewed field as authoritative enough for later claim or trust steps
- bury field partition only in debug logs
- let alias collapse erase field-exposure history


## ADR-120 — preview usefulness must publish decision sufficiency and omission truth

### Status

Accepted

### Context

The archive already distinguishes delivery provenance, canonical artifact identity, and field-partition truth for portable offers.
However, one gap remained: a preview can show enough to make a human feel comfortable without actually showing the governance-bearing fields that should decide permissions, approval posture, expiry, use-count, or later trust consequences.
Current Resilio docs still make this gap concrete by showing a landing page with basic folder info while separate sharing surfaces govern permission, approval, expiration, and use-count behavior.

### Decision

AnonSync will treat preview sufficiency as a first-class public property.
Every portable-offer preview surface must be able to say:

- what it showed
- what governance-bearing fields it omitted
- what decision domains it is sufficient for
- what decision domains remain blocked
- what unsafe inferences are being refused
- what the next honest action is

The product will therefore add dedicated preview-sufficiency rows, omission explanations, review plans, and receipts.
`Recognition sufficient` must never imply `governance sufficient`.

### Consequences

Benefits:

- minimal previews can stay useful without becoming stealth governance surfaces
- omitted fields become explicit product truth rather than invisible absence
- later approval/claim receipts can prove they did not rely on preview familiarity alone

Costs:

- dense intake cards need one more compact summary strip
- APIs and CLI need one more explicit decision-domain model
- operators will see a little more `not enough yet` language during safe intake

### Rejected alternative

Treat `preview hint` versus `authoritative field` as sufficient and leave decision sufficiency implicit.
That was rejected because a user can still over-read a perfectly honest hint surface unless the product also says what the hint is *not enough* to decide.
## ADR-121 — preview, local parse, claim review, and apply must remain explicit ladder rungs

**Decision:** Portable-offer handling must expose preview, local parse, claim preparation, and apply as separate public rungs rather than one convenience sequence.

**Why:** The archive already separates preview hints, sealed fields, and omission truth. Without a visible ladder, operators still compress those truths back into `I opened it, so I basically accepted it`.

**Implications:**

- daemon/API expose decision-ladder read models and receipts
- GUI/TUI/CLI must render current rung and next honest action explicitly
- local parse is visible as a meaningful state transition, not silent background work
- apply cannot erase the earlier ladder story

## ADR-122 — portable-offer rows and panes are governance surfaces, not cosmetic projections

**Decision:** Dense rows and full panes for portable offers must preserve one fixed adjacency contract for `what arrived`, `what is missing`, `what this is enough for`, `what it is not enough for`, and `what next`.

**Why:** Operators most often over-read convenience on the dense surface, not the most detailed one. If the row drops omission or decision-scope truth, the layout itself recreates ambiguity.

**Implications:**

- card/detail projections become first-class daemon/UI contract
- mobile compaction may stack content but may not separate missing truth from next action too aggressively
- batch actions depend on explicit ladder and decision-scope fields rather than inferred readiness


## Revision addendum — ADR: explicit issuance and publication over ambient member defaults

### Decision

Treat outbound offer issuance and constellation publication as separate receipted review acts.

### Why

Current Resilio docs remain strong enough to prove the convenience value of linked devices and share dialogs, but they also show that ambient visibility, device-wide mode ritual, and identity-replacement-like linking flows are still easy to trigger or misread.
AnonSync therefore chooses more explicit public objects rather than more magical defaults.

### Consequence

The product will carry more explicit draft/review/receipt state on the sender and publication side, but it will be easier to explain, safer to automate, and much harder to misread.


## ADR-123 — living publication truth must be inspectable as subject × member matrix state

**Decision:** Publication state must be renderable as explicit `(subject, member)` cells with provenance, unresolved-local-work truth, and receipt lineage.

**Why:** Per-subject publication reviews are not enough once the operator is living with dozens of subjects and members. Without a matrix view, current publication truth quickly decays back into remembered defaults and device folklore.

**Implications:**

- matrix views and cell-detail projections are first-class, not optional dashboards
- inherited template state must stay visibly inherited
- one-cell overrides must remain narrow and receipted
- stale-drift cells must stay visible instead of bluffing certainty

## ADR-124 — arrival role selection precedes path and materialization

**Decision:** For non-trivial arrivals, the interface must choose the member's admissible role before it chooses path or byte posture.

**Why:** Resilio's current read-only and custom-placement guidance shows how quickly least-privilege goals get translated into path ritual when role, path, and mode are entangled.

**Implications:**

- directory pickers cannot be the first meaningful control on a fresh arrival review
- placeholder/full/encrypted byte posture is subordinate to role, not synonymous with it
- reconnect and re-adoption flows must compare prior role and new role explicitly
- role promotion requires fresh reviewed plans even if the path stays unchanged


## ADR-125 — publication edits must render counterfactual affected-cell previews before apply

**Decision:** Any publication/template/default edit that can change multiple `(subject, member)` outcomes must render an affected-cell delta preview before apply.

**Why:** Operators should learn the consequences of policy changes prospectively, not only from later appearances, missing folders, duplicate paths, or widened visibility.

**Implications:**

- delta previews are first-class reviewed objects, not optional simulation sugar
- unchanged but in-scope cells must stay countable and inspectable
- authority widening and visibility-only widening must be called out separately
- apply receipts should cite the reviewed delta set

## ADR-126 — member-wide future-arrival defaults need their own public policy card

**Decision:** Each member must have one inspectable policy card for future-arrival defaults, default roots, auto-staging posture, exceptions, and receipts.

**Why:** Current publication truth and future-arrival defaults are related but different. If defaults remain hidden in one settings page or one compressed mode label, the product will recreate Resilio-style member lore.

**Implications:**

- member policy changes must publish explicit non-effects on current state
- if a member policy change would alter existing cells, delta preview must open automatically
- current claimed role/state and future default posture must stay visually distinct
- global settings alone are not an acceptable explanation surface


## ADR-127 — publication mutations need durable ledgers distinct from observation and recall

**Decision:** Every meaningful publication mutation must persist as a first-class ledger entry with review lineage, local apply proof, per-member observation state, supersession state, and non-effects.

**Why:** A reviewed change is not fully explained by a current matrix cell alone. Operators also need to know what changed recently, who has observed it, and which stronger claims still depend on recall or later observation.

**Implications:**

- ledger entries and matrix cells are complementary, not interchangeable
- local apply cannot masquerade as remote observation
- mutation history must remain inspectable even after supersession
- recall and retained-copy truth remain separate follow-on surfaces

## ADR-128 — member-policy edits must be draft-first and precedence-explicit

**Decision:** Semantic member-policy changes must commit only from a reviewed edit plan that shows inheritance mode, precedence ladder, simulations, non-effects, and whether a wider delta preview is required.

**Why:** A visible member policy card is not enough if the edit path still collapses `inherit`, `clear`, `pin empty`, `pin value`, and `future-only` into one inline save gesture.

**Implications:**

- inline card controls may draft changes, but may not silently commit semantic defaults
- compact review is allowed only for provably future-only edits with zero current-cell impact and no precedence conflicts
- precedence conflicts escalate to the full editor
- every applied member-policy edit emits one durable receipt that cites any required delta preview


## ADR-021 — Every visible subject/member cell must be causally explainable

**Decision:** If the product renders a `(subject, member)` cell, it must be able to render one supported explanation object for why that cell exists with its current role, bind posture, and materialization state.

**Why:** A major non-clone reason versus Resilio is that operators should not have to reconstruct arrival meaning from linked-device defaults, reconnect outcomes, and scattered settings pages.

**Implications:**

- per-cell explanation becomes part of the public object model
- publication truth, acceptance truth, role truth, path truth, and byte-posture truth stay adjacent
- support articles become reinforcement, not the only place where causality can be learned

## ADR-022 — Standing member-policy edits must preview representative future arrivals

**Decision:** Semantic member-policy drafts must expose a future-arrival simulation surface before apply.

**Why:** Preventing semantics-by-defaults requires showing not only what current cells change, but also how representative future arrivals would differ.

**Implications:**

- impact proof and future simulation sit in the same review flow
- scenario classes become explicit and queryable
- widening future behavior gets louder review treatment than cosmetic or presentational change


## ADR-023 — unresolved post-change gaps need explicit convergence-window truth

**Decision:** Any unresolved `(subject, member)` gap after publication, arrival, withdrawal, or standing-policy change must render through one explicit convergence-window object with stable verdict classes and explicit non-claims.

**Why:** Preventing semantics-by-folklore requires not only explaining why state exists, but also classifying honestly whether unsettled state is still expected, blocked, overdue, impossible, or superseded.

**Implications:**

- `pending` alone is never enough for meaningful distributed-state review
- convergence windows must publish fresh evidence, missing evidence, blocked claims, and supersession truth without promising fake ETAs
- mutation ledgers, matrix cells, and arrival surfaces may open the same convergence object rather than inventing separate local meanings

## ADR-024 — next actions for unsettled gaps must compile into one reviewed wait-vs-intervene verdict

**Decision:** When an unresolved gap has multiple materially different possible next moves, the product must render one wait-vs-intervene decision sheet with a single strongest recommendation, explicit non-recommended alternatives, and blocked unsafe actions.

**Why:** A major non-clone reason versus Resilio is that operators should not have to improvise reconnect, republish, route repair, or policy edits from scattered support cues and remembered ritual.

**Implications:**

- `wait` becomes a first-class positive recommendation when evidence still supports ordinary convergence
- route, source, local-prerequisite, supersession, and policy causes must stay distinct in recommendation logic
- decision receipts record the recommendation from current evidence without pretending it remains eternally correct


## Revision addendum — evidence bundles and intervention receipts are primary objects

The archive now commits to two more architectural choices:

1. unresolved convergence gaps may require first-class **evidence bundle** objects rather than ad hoc derived panels assembled transiently from logs and status rows
2. non-trivial remediation or re-check work must create first-class **intervention attempt** objects with mandatory after-action recompute receipts

Why this matters:

- it prevents diagnosis from collapsing back into support-lore reconstruction
- it lets CLI, API, and graphical surfaces share the same evidence and action semantics
- it preserves later auditability for repeated retries, superseded attempts, and action-effect comparison


## Revision addendum — probe plans and disclosure packets are separate from evidence bundles

This revision makes two additional architectural decisions:

1. a sealed evidence bundle is **not** itself permission to start higher-intrusion capture; deeper diagnostics require a separate reviewed probe plan
2. a sealed evidence bundle is **not** itself permission to disclose material externally; outbound sharing requires a recipient-specific escalation packet with its own manifest and receipt


## Revision addendum — frozen packets and outside-step return proof are separate architectural objects

This revision makes two additional architectural decisions:

1. sealed local evidence, reviewed packet composition, and actual disclosure are three different lifecycle stages and must remain queryable as separate objects with separate receipts
2. any blocker whose next honest resolution step leaves the product surface must become an external-handoff object with typed target class, follow-up state, expiry/staleness posture, and explicit return proof


## ADR-023 — Effective values must expose origin and rejoin posture

**Decision:** Non-trivial effective values should surface source state, source reference, baseline-change effect, and rejoin posture as public model data.

**Why:** Current sync-product evidence shows that the visible value alone is not enough; operators also need to know whether it is inheriting, pinned, excepted, leased, copied static, computed, unsupported, or drifting.

**Implications:**

- UI/TUI/CLI can render one consistent value-row grammar
- baseline edits can preview real blast radius instead of guessed blast radius
- exception and rejoin workflows become easier to explain and audit

## ADR-024 — The persistent shell is a safety-relevant interface contract

**Decision:** Subject context, proof context, queue context, and action context should persist through one stable shell grammar across projections.

**Why:** Losing or scattering that context changes operator judgment and recreates settings folklore.

**Implications:**

- GUI/local-web/TUI/CLI summaries share one conceptual page frame
- proof drawers and action trays are first-class, not optional embellishment
- navigation shortcuts cannot silently bypass subject context for risky actions

## ADR-025 — Batch power must split on semantic outliers

**Decision:** Bulk actions may optimize repetitive work, but they must split when risk class, proof freshness, or action scope materially differs.

**Why:** Bulk convenience is one of the fastest ways for a careful interface to regress into hidden scope expansion.

**Implications:**

- batch preview shows outlier counts and split reasons explicitly
- mixed-risk actions fall back to draft/review instead of direct apply
- receipts can preserve which subjects were batched together and which were forced apart


## Revision addendum — mutation instruments and projection parity are architectural choices

This revision makes two additional architectural decisions:

1. non-trivial value mutation must be modeled as an **instrument choice** before field editing, because `baseline edit`, `local pin`, `temporary override`, `durable exception`, and `restore inheritance` are not interchangeable state transitions
2. projection parity is architectural, not cosmetic; GUI, local web, TUI, and CLI must share the same capability classes and deep-linkable draft handles even when they render them differently

Why this matters:

- it prevents state mutation from smuggling governance changes through generic settings edits
- it keeps Linux-first local web from becoming a semantically second-class control surface
- it gives automation, CLI, and graphical projections one shared draft/apply/handoff model instead of frontend-specific folklore

## ADR-129 — Reviewed mutation requires a fixed commit barrier

**Decision:** Non-trivial mutation flows must expose a stable last-step commit barrier between reviewed draft and apply.

**Why:** A good preview is not enough if the final click still hides irreversible scope, continuity claims, or expected receipts.

**Implications:**

- draft review and commit review are separate semantic stages
- generic confirmation modals are insufficient for high-signal apply paths
- receipts must be linked directly from the barrier outcome

## ADR-130 — Reconnect and path repair are continuity workflows

**Decision:** Reconnect, rebind, adopt, and pre-existing-path repair belong to one compared-workflow family.

**Why:** Current sync tooling too often teaches path continuity through duplicate-folder creation, reconnect ritual, or remove/re-add support lore.

**Implications:**

- remembered path becomes a first-class comparison input
- duplicate-risk and divergence class are proof-bearing findings
- the product avoids defaulting to `make a new folder and let the operator sort it out later`

## ADR-131 — Local web is a primary Linux/service projection

**Decision:** Local web is a first-class projection for Linux-first and service-first operation.

**Why:** If the comparison product uses WebUI as the default Linux/service path, AnonSync cannot let browser access be semantically thinner than desktop access.

**Implications:**

- first-run auth and empty states are product-critical, not peripheral
- ordinary read/explain/draft/review/apply capability must exist there
- projection handoff remains explicit when some action truly requires other custody

## ADR-132 — Layout compression must preserve provenance and consequence

**Decision:** Dense and narrow layouts may compress chrome and history before they compress provenance, scope, or apply consequence.

**Why:** Once meaning is already spread across several object families, hiding the remaining proof-bearing cues on small screens would recreate folklore.

**Implications:**

- responsive design must be semantics-first, not ornament-first
- source, blocker, future effect, and consequence remain visible in compressed form
- mobile/narrow surfaces cannot be excused from the same truth contract


## Revision addendum — comparative imports after rev0144

This pass adopts four tighter architecture requirements from comparative reading across the uploaded archives.

1. **Diagnostic arbitration is now a first-class review object.**  
   When several hypotheses or repair recipes remain simultaneously eligible, the system must preserve a compact tie set, the arbitration rule that currently recommends one branch, the nearby fallback/abstention baseline, and the instability budget that would revoke confidence.

2. **Fact authorship is now explicit in the public model.**  
   Every visible fact that matters to trust, route, readiness, adoption, or repair must say whether it is local-observed, peer-declared, sender-declared, operator-entered, config-declared, browser-observed, or derived. Stronger buckets may not be inferred silently from weaker ones.

3. **Local-web history behavior is now part of projection parity.**  
   Browser `push` versus `replace`, back/forward continuity, refresh behavior, and typed fragment/deep-link miss handling must be deliberate projection rules for the local-web surface, not incidental consequences of whichever frontend stack is used.

4. **Transient message delivery is now subordinate to durable outcome state.**  
   Any consequential result, blocker, warning, or next-step recommendation must remain visible in durable inline state and receipt continuity even if a toast, badge, live-region announcement, or OS notification also fires.


## Revision addendum — reapproval clocks and compact shareable-head registers

This pass adds two more architectural requirements.

1. **Material-change reapproval is a first-class trust object.**  
   Remembered approval cannot be governed only by age classes. The system needs explicit trigger rows, periodic review clocks, reapproval reviews, and receipts that can freeze reuse, reapprove same scope, reapprove narrowed scope, or record a reviewed `non-material` judgment.

2. **Retained shareable artifacts need a compact current-head register.**  
   Offer families, escalation packets, continuity bundles, and similar portable artifacts must expose one register that distinguishes operational head from frozen shareable head and preserves warnings when the current-shareable answer is blocked by branching, missing freeze proof, expiry, recipient mismatch, or supersession.


## ADR-133 — Approval coordination splits seat roster from active request state

**Decision:** The approval object model must expose eligible-seat continuity separately from current approval-request state.

**Why:** Multi-seat products repeatedly blur `who could act`, `who is being asked now`, `who already reviewed this basis`, and `who must be re-asked after drift`. That flattening creates false queue states and hides when no current ask actually exists.

**Implications:**

- seat roster rows and active request rows are distinct objects
- completed review may clear live request without erasing seat continuity
- later basis drift yields `rerequest-needed`, not silent auto-rerequest
- UI, CLI, and API may not claim `waiting on review` when only eligibility remains

## Revision addendum — comparative import after rev0148

This pass adopts one tighter architecture requirement from comparative reading across the uploaded archives.

1. **Approval coordination now distinguishes roster continuity from live request truth.** The system must preserve which seats remain eligible to act, which seat is currently requested on the present basis, which seat merely reviewed an older basis, and when explicit rerequest is required, instead of letting one approver/reviewer badge stand in for all of that state.


## ADR-134 — Live external sources do not substitute for frozen review basis

**Decision:** Keep live source locator, fetched local snapshot, exact reviewed basis excerpts, and later drift checks as separate objects.

**Why:** External guidance frequently arrives through mutable help-center pages, forum posts, ticket replies, and copied command blocks. Treating a live locator as the exact reviewed instruction basis lets redirects, edits, or disappearance silently rewrite the meaning of older approvals.

**Implications:**

- translated recipes, probes, and packets must point to explicit frozen basis rows
- host / source authority posture must remain separate from exact reviewed snapshot/excerpt truth
- later drift checks may demand follow-up without mutating earlier receipts
- copy-pasted commands and quoted snippets need the same snapshot/basis discipline as URLs

## Revision addendum — status-bridge and follow-through claim truth after rev0150

This pass adds two adjacent architecture decisions.

1. **Everyday status and full incident capture are now explicitly different proof scales.** A compact runtime-status bridge should exist for ordinary seat/runtime questions, but it must publish its claim ceiling and escalation boundary instead of pretending to replace the richer dossier lane.
2. **Outside progress and whole-fix claims are now explicitly different coverage states.** Requested step, source-side execution, product-side effect, and claim-ready repair should remain separate public truths so that partial outside progress cannot silently inherit stronger product meaning than the reread evidence supports.

## Revision addendum — outbound channel execution and delivery claim ceiling

**Why:** The archive already separated delivery encoding from artifact meaning, frozen packets from disclosure, and current shareable head from working tips. What was still missing was the truth boundary of the channel action itself: clipboard completion, browser download, web-share resolution, and later recipient evidence are not the same proof.

**Decision:** Outbound artifact movement now uses one explicit channel-execution contract with a current claim ceiling. Clients should preserve at least these distinct answers:

- exact frozen artifact head
- chosen channel and surface
- observed local completion
- strongest later witness beyond local completion
- strongest currently allowed delivery label

**Consequences:**

- `copied`, `saved locally`, `share invoked`, `passed to target`, and `receipt imported` become legitimate stable labels instead of awkward intermediate states
- current shareable head and latest channel execution remain different objects
- later stronger witness import may raise the current claim ceiling without rewriting what an earlier execution actually proved
- browser-local surfaces must preserve platform variance where channel APIs resolve at different points in the user journey


## Revision addendum — artifact carryforward verdicts and refresh notices after rev0151

**Why:** The archive now had current-head registers and outbound delivery claim ceilings, but it still lacked one compact answer to `what changed since the last artifact we already shared?` Without that surface, operators either over-compress meaning into `updated` or reopen lineage manually for every reissue.

**Decision:** Retained shareable-artifact families now get one explicit carryforward profile, one delta ledger, and one audience-safe refresh-notice surface. Clients should preserve at least these distinct answers:

- prior comparison basis
- current carryforward verdict
- changed field families
- explicitly unchanged guarantees
- smallest honest visible refresh note
- stronger follow-up boundary when terse carryforward is forbidden

**Consequences:**

- current shareable head no longer has to explain semantic change by itself
- version/hash drift can help prove non-identity but cannot replace the delta ledger or visible refresh note
- recipients can get one compact honest continuity note without losing access to deeper lineage and proof
- widened audience, changed authority scope, or contradictory basis can cleanly force `reopen-required` instead of being squeezed into one misleading update sentence


## ADR-135 — Startup ownership is distinct from install readiness and service continuity

**Decision:** The object model must expose startup ownership as its own reviewed runtime-return surface, with candidate owner lanes, one effective-owner verdict, runtime correlation, and drift history.

**Why:** Install attestation, bring-up, and service promotion already answer adjacent questions, but none of them alone answers `who will actually start this same node again later?` Current Linux startup reality reinforces the need for a separate object: unit-file states are not one boolean, generated/transient lanes do not mean the same thing as ordinary enablement, and desktop-autostart entries can be conditionally suppressed or ignored. Flattening all of that into `launch at login` or `service enabled` makes duplicate or missing startup ownership invisible until after a reboot.

**Implications:**

- startup-owner snapshots and receipts become first-class objects
- `singular`, `duplicate`, `missing`, `ambiguous`, and `manual-only-by-choice` become legitimate stable verdicts
- current runtime may be healthy while still classified `manual-outside-owner`
- install and service-promotion receipts may point to startup-owner review, but may not impersonate it
- local web, CLI, and status surfaces may not claim automatic return unless a reviewed effective owner actually exists

## Revision addendum — startup owner, duplicate-launch risk, and drift truth after rev0152

**Why:** The archive already had install attestation, service-promotion continuity, and lightweight runtime status, but it still lacked one compact answer to `who actually owns automatic return on this host, and has that truth drifted recently?` Without that surface, operators would still reconstruct startup truth from service-manager state, desktop-startup files, and lucky current runtime.

**Decision:** Startup ownership now uses one explicit owner-snapshot contract with candidate owner rows, effective-owner verdict, runtime correlation, and drift-history receipts. Clients should preserve at least these distinct answers:

- requested startup posture
- candidate owner lanes
- effective owner verdict
- duplicate or missing owner risk
- current runtime correlation
- recent drift class

**Consequences:**

- `installed`, `service promoted`, `running now`, and `will return automatically later` remain different operator truths
- duplicate startup owners can be surfaced before they cause wrong-node or double-start confusion
- generated / conditional owner lanes can stay visible without being flattened into ordinary enablement
- drift history can say `stable`, `recovered`, `duplicate introduced`, `owner lost`, or `flapping` from one ordinary status surface


## ADR-136 — Reviewed actions are scoped to expected basis, not ambient latestness

**Decision:** Reviewed drafts, packets, queue-worthy actions, and apply-ready mutations must preserve an explicit expected-basis guard with stale-attempt and reissue receipts.

**Why:** Cross-reading the comparison archives showed the same seam in several domains: approvals, merge requests, queue entry, publication, and frozen public surfaces all become dishonest if an older reviewed action silently jumps onto whatever later became current. AnonSync already had adjacent objects for current heads, approval reapproval, carryforward, and follow-through, but it still lacked one compact contract for the action itself.

**Implications:**

- reviewed action presence and current-basis validity are distinct truths
- stale clicks must emit durable stale-attempt receipts rather than disappearing or silently rebinding
- reissue must be explicit even when prose or recipients are conveniently carried forward
- authority guard and basis guard stay separate so one failure cannot hide the other
- queued or deferred actions keep the same compare-and-set discipline as immediate actions

## Revision addendum — reviewed-action basis guard after rev0153

**Why:** The archive already knew how to say what is current, what changed, and when trust or carryforward reopens. What it still did not say cleanly was whether an already reviewed action still binds right now. That missing seam is where sticky inheritance and silent no-op failure usually leak in.

**Decision:** Add one explicit reviewed-action basis-guard contract with expected-basis rows, current comparison, stale-attempt receipts, and explicit reissue. Clients should preserve at least these distinct answers:

- which action was reviewed
- which basis rows it expected
- which rows still match and which drifted
- whether a stale click was refused
- which newer action explicitly replaced it, if any


## ADR-137 — Recipient-scoped reviewed actions are scoped to expected target, not ambient retargeting

**Decision:** Recipient-specific or target-scoped reviewed actions must preserve an explicit expected-target guard with stale-target and retarget-reissue receipts.

**Why:** Cross-reading the comparison archives showed a second seam adjacent to basis drift: an object may keep family continuity while the target it was meant to hit changes. AnonSync already had recipient-specific packets, carryforward notes, and channel claim ceilings, but it still lacked one compact contract for whether an older reviewed action still points at the same destination.

**Implications:**

- action continuity and target continuity are distinct truths
- widening recipient or audience scope always reopens through explicit reissue
- narrowing or alias-equivalent targets still require an explicit visible verdict rather than silent send
- old channel-execution history remains attached to the old target even after retarget review
- basis guard and target guard should remain separate so one failure cannot hide the other

## Revision addendum — recipient-target guard after rev0154

**Why:** The archive already knew how to say what basis was reviewed and what channel later executed. What it still did not say cleanly was whether the reviewed action still pointed at the same recipient or disclosure target. That missing seam is where sticky retargeting and silent audience widening usually leak in.

**Decision:** Add one explicit reviewed recipient-target guard contract with expected-target rows, current comparison, stale-target receipts, and explicit retarget reissue. Clients should preserve at least these distinct answers:

- which action was reviewed
- which target rows it expected
- which rows still match and which changed
- whether a stale retarget was refused
- which newer action explicitly replaced it, if any

## ADR-138 — Current shareable head and current issued outward surface are distinct target-scoped truths

**Decision:** Retained outward artifact families must preserve an explicit disclosure register that distinguishes current shareable head, queued issue item, executed issue event, current issued head, and later delivery witness.

**Why:** Cross-reading the comparison archives showed one more seam that adjacent AnonSync objects still did not fully close. Head registers answer what is current for reuse, carryforward notes answer what changed since an older disclosed artifact, target guards answer whether the reviewed destination still matches, and channel ceilings answer what one local send or witness proved. None of those objects alone answers `what artifact is currently outwardly in force for this recipient or audience now, given that a newer frozen head or queued send also exists?`

**Implications:**

- freezing a newer head does not, by itself, rewrite the current issued head
- queueing or scheduling an outward act does not, by itself, rewrite the current outward surface
- an executed issue event may advance current issued head for one target even while another target still remains on an older head
- delivery witness remains separate from issued-head transition and may still lag after execution
- carryforward and refresh-note surfaces may compare against the prior disclosed head without auto-promoting the newer one before execution

## Revision addendum — disclosure register and current issued-surface truth after rev0155

**Why:** The archive already knew how to say what artifact is current for reuse, what changed since an older disclosed artifact, what a channel action locally completed, and whether a reviewed destination still matched. What it still did not say cleanly was which artifact is currently outwardly in force for one recipient or audience when a newer head is merely frozen or queued.

**Decision:** Add one explicit disclosure-register contract with current shareable head, queued issue item, executed issue event, current issued head, and outward-surface snapshot. Clients should preserve at least these distinct answers:

- which head is current for new reuse
- whether a newer issue is only queued or scheduled
- which issue event actually executed most recently
- which head is currently outwardly in force for one target or audience
- whether any stronger recipient receipt exists beyond that issued-surface transition


## ADR-139 — Outward correction, supersession notice, and residual reliance are distinct from current issued state

**Decision:** Already-issued outward artifact families must preserve an explicit correction register that distinguishes the older issued artifact being corrected, the active correction notice if any, any replacement already issued, and the current residual-reliance posture.

**Why:** Cross-reading the comparison archives showed one more seam that adjacent AnonSync objects still did not fully close. Disclosure registers answer what is outwardly current now. Carryforward notes answer what changed between retained artifacts. Channel ceilings answer what one send or witness proved. None of those objects alone answers `which notice now controls interpretation of an already-issued older artifact, and what stale-copy or acknowledgment risk still remains?`

**Implications:**

- a local decision or newer replacement artifact does not, by itself, prove recipient interpretation changed
- withdrawal without replacement remains a first-class outward state rather than collapsing into `nothing current`
- correction notice issue, replacement issue, and recipient acknowledgment stay separate receipts and separate claim ceilings
- residual stale-copy posture remains visible after correction instead of disappearing behind `superseded`
- correction history explains new interpretation without erasing the earlier issue event

## ADR-140 — Imported acknowledgment exactness is separate from conversation continuity

**Decision:** Already-issued outward artifact families must preserve an explicit imported-acknowledgment binding surface that distinguishes sender match, conversation continuity, exact bound object, and acknowledgment claim ceiling.

**Why:** Cross-reading the comparison archives showed one more seam that adjacent AnonSync objects still did not fully close. Delivery witnesses answer what transport or local handoff proved. Disclosure registers answer what is currently outwardly in force. Correction registers answer what notice now controls interpretation of an older artifact. None of those objects alone answers `what exact thing did this imported reply or acknowledgment bind to, and how exact is that binding really?`

**Implications:**

- same-thread or same-ticket continuity does not, by itself, prove exact artifact acknowledgment
- generic reply text and read/open receipts remain useful but weaker than exact object-binding proof
- same-product successor observation may be stronger than message-thread folklore and may upgrade claim ceiling explicitly
- correction and disclosure surfaces may consume stronger acknowledgment exactness without flattening older issue history
- ambiguity should remain visible until the binding object is exact or explicitly classified

## Revision addendum — acknowledgment binding exactness after rev0158

**Why:** The archive already knew how to say what was issued, what notice later corrected it, and what transport/delivery witnesses existed. What it still did not say cleanly was whether an imported acknowledgment bound to the family generically, one exact correction notice, or one exact replacement artifact.

**Decision:** Add one explicit acknowledgment-binding contract with sender-match, conversation-continuity, exact-bound-object, and claim-ceiling answers. Clients should preserve at least these distinct truths:

- who replied and how exact the sender match is
- whether continuity exists only by thread/ticket lane
- what exact object kind, if any, the acknowledgment binds to
- what claim ceiling is justified now
- what stronger proof would upgrade the ceiling

## Revision addendum — outward correction and residual reliance truth after rev0156

**Why:** The archive already knew how to say what artifact is outwardly current, what changed since an older disclosed artifact, and what local send or later witness proved. What it still did not say cleanly was which notice now controls interpretation of an older already-issued artifact once the operator decides it should be superseded or withdrawn.

**Decision:** Add one explicit outward-correction contract with older issued artifact, active correction notice, replacement-issued state, residual-reliance posture, and stronger acknowledgment ceiling. Clients should preserve at least these distinct answers:

- which older issued artifact is being corrected
- whether a correction notice is drafted, issued, or acknowledged
- whether a replacement artifact merely exists or was actually issued
- why stale-copy risk still remains
- what stronger proof would justify saying the recipient now understands the correction


## ADR-141 — Imported acknowledgment actor scope is separate from object exactness

**Decision:** Already-issued outward artifact families must preserve an explicit imported-acknowledgment scope surface that distinguishes raw actor, visible reply lane, relation to expected target, delegation evidence, and current audience/scope ceiling.

**Why:** Cross-reading the comparison archives showed one more seam that adjacent AnonSync objects still did not fully close. `259` now answers what exact object a reply acknowledged. Delivery witnesses answer what transport proved. Disclosure registers answer what is currently outwardly in force. Correction registers answer what notice controls interpretation of older outward artifacts. None of those objects alone answers `who can this exact reply honestly speak for?`

Concretely:

- one actor inside a broader mailbox/group/support lane may reply exactly without proving that the whole target audience acknowledged
- delegated or shared-mailbox response can be stronger than same-domain folklore without automatically becoming whole-organization proof
- exact object binding and exact target-scope coverage are orthogonal and must not silently overwrite each other
- manual scope promotion must preserve weaker raw actor/lane facts rather than rewriting history

## Revision addendum — acknowledgment actor scope after rev0159

**Why:** The archive already knew how to say what was issued, which correction or replacement object a reply bound to, and what transport/delivery witnesses existed. What it still did not say cleanly was whether that reply spoke only for one actor, one target lane, one audience member, or the whole intended audience.

**Decision:** Add one explicit acknowledgment actor-scope contract with raw-actor, visible-lane, target-relation, delegation-evidence, and audience-ceiling answers. Clients should preserve at least these distinct truths:

- who concretely produced the reply
- what visible mailbox/group/ticket lane the reply arrived through
- how that actor relates to the expected target scope
- what current scope ceiling is justified
- what stronger proof would justify promoting that ceiling



## ADR-142 — Human-proof and reply stance are distinct imported-reply truths

**Decision:** Already-issued outward artifact families must preserve an explicit imported-reply stance surface that distinguishes semantic stance, blocking effect, smallest honest follow-up, and current acceptance ceiling from object exactness, represented scope, and human-proof.

**Why:** Cross-reading the comparison archives showed one more seam that adjacent AnonSync objects still did not fully close. Binding exactness answers what exact object the reply spoke about. Audience scope answers who the reply can honestly speak for. Authorship answers whether any human likely replied at all. None of those objects alone answers `did that human reply accept the current request, ask for clarification, redirect the lane, conditionally accept pending one more step, or decline outright?`

**Consequences:**

- one human reply may still remain clarification-only, redirect-only, or decline-only
- redirect to a new lane does not prove that the new lane already accepted or received the artifact
- disclosure, correction, and acknowledgment surfaces may consume stronger reply stance without flattening the older clarification / redirect / decline history

## ADR-143 — Exact reply object and covered portion are distinct imported-reply truths

**Decision:** Already-issued outward artifact families must preserve an explicit imported-reply referent-slice surface that distinguishes whole-artifact binding from quoted-excerpt, line-range, attachment-only, request-item-only, and named-subset coverage.

**Why:** Cross-reading the comparison archives showed one more seam that adjacent AnonSync objects still did not fully close. Binding exactness answers what artifact family or outward object the reply spoke about. Reply stance answers whether the reply understood, redirected, requested changes, or conditionally accepted. Neither object alone answers whether the reply actually covered the whole packet or only one cited/requested slice inside it.

**Consequences:**

- exact quoted feedback may remain useful without promoting whole-artifact acceptance
- attachment-only or request-item-only approval can coexist with an open remainder posture
- disclosure, correction, and acknowledgment surfaces may consume stronger subset truth without flattening the unmentioned remainder

## ADR-144 — Imported reply chronology is separate from current operative head

**Decision:** Already-issued outward artifact families must preserve an explicit imported-reply series head register that distinguishes latest arrival, current whole-artifact head, current subset heads, superseded older replies, and contradiction warnings.

**Why:** Cross-reading the comparison archives showed one more seam that adjacent AnonSync objects still did not fully close. Binding exactness answers what object the reply spoke about. Audience scope answers who it can speak for. Authorship answers whether any human likely replied. Reply stance answers what it meant. Referent coverage answers what slice it covered. None of those objects alone answers `which reply is currently operative now, and does the newest reply actually replace older blockers or merely add one narrower subset head?`

**Consequences:**

- latest thread position does not, by itself, define current reply truth
- subset-safe later approvals may coexist with older whole-artifact blockers
- contradiction warnings remain visible when one unique current head does not yet exist

## Revision addendum — imported reply series heads after rev0163

**Why:** The archive could already say what exact outward artifact a reply bound to, who it could speak for, whether any human likely replied, what stance that reply took, and what portion of the larger packet it covered. What it still could not say cleanly was which imported reply was currently operative now once several replies accumulated in the same lane.

**Decision:** Add one explicit reply-series head-register contract with latest-arrival, current-whole-head, current-subset-heads, superseded-replies, and contradiction-warning answers. Clients should preserve at least these distinct truths:

- newest imported reply in chronology
- current whole-artifact operative head
- current slice-specific operative heads
- older replies that were genuinely superseded
- older blockers that remain live because later replies were narrower or differently scoped

## Revision addendum — imported reply referent slices after rev0162

**Why:** The archive could already say what exact outward artifact a reply bound to, who it could speak for, whether any human likely replied, and what stance that reply took. What it still could not say cleanly was what portion of the larger packet or request that reply actually covered.

**Decision:** Add one explicit referent-slice contract with referent-scope, coverage-ceiling, remainder-posture, and promotion-requirement answers. Clients should preserve at least these distinct truths:

- reply bound to the correct outward artifact
- reply only addressed one quoted excerpt, line range, attachment, or named request item
- reply addressed a visible subset but left a remainder open
- reply explicitly covered all request items
- reply explicitly accepted the whole outward artifact

## Revision addendum — imported reply stance after rev0161

**Why:** The archive could already say what exact object a reply bound to, who it could speak for, and whether any human likely replied. What it still could not say cleanly was what that reply *meant* in operational terms.

**Decision:** Add one explicit reply-stance contract with semantic-stance, blocking-effect, smallest-follow-up, and acceptance-ceiling answers. Clients should preserve at least these distinct truths:

- human reply happened
- reply only acknowledged receipt
- reply asked for clarification or artifact change
- reply redirected the operator to a different lane
- reply conditionally accepted pending one further step
- reply declined or rejected the request

## Revision addendum — imported acknowledgment authorship after rev0160

- imported acknowledgment truth now separates object exactness, represented scope, and authorship class
- machine-authored mailbox/ticket reactions remain useful weaker truths instead of being discarded or promoted into human review
- auto-replies, ticket auto-create notices, rule-authored comments, and receipt-like signals cannot silently claim `human acknowledged` without explicit stronger proof

## ADR-019 — Convenience selectors must compile to orthogonal public objects

**Decision:** Keep useful convenience selectors only when their consequences remain separately inspectable.

**Why:** Current Resilio evidence keeps showing that the painful part is often not the convenience itself, but the way one selector silently decides several truths at once.

**Implications:**

- visibility, adoption, materialization, authority, and future defaults should stay queryable as separate answers
- no selector may be the only semantic home of a high-signal consequence
- review surfaces must be able to explain the consequence chain after the fact

## ADR-020 — Operational lists are first-class decision surfaces

**Decision:** Treat share list, Transfers, History / Restore, and Conflict inbox surfaces as part of the semantic control plane.

**Why:** Most operators spend more time in lists than in deep detail pages, so list rows that hide risk/proof/action truth recreate black-box behavior even when the underlying object model is excellent.

**Implications:**

- row anatomy is part of the public interface contract
- dense/narrow views may compress wording but may not drop next-action or blocker truth
- list rows must carry stable jumps into proof/review rather than hiding them behind ornamental status

## ADR-145 — Every non-clone boundary must name a page-shaped replacement

**Decision:** Refuse aesthetic divergence.
Whenever the archive says `do not clone` for an operator-facing seam, it should name the replacement page contract that will answer the same ordinary question better.

**Why:** Otherwise `do not clone` degrades into taste, and the archive becomes stronger at critique than product design.

**Implications:**

- anti-clone arguments should point at replacement pages, not only abstract doctrine
- control trust, import artifact, rate policy, and finish setup now count as required replacement surfaces
- roadmap progress should track whether those pages exist, not merely whether critique exists

## ADR-146 — Degraded operational states must publish upgrade ladders

**Decision:** Treat degraded states as reviewed transitions, not static badges.

**Why:** Browser warnings, failed handoffs, scheduled throttles, and installed-but-not-ready states only become operator-usable when the product names the next stronger reachable state and what mutation gets there.

**Implications:**

- degraded states should name reachable stronger states explicitly
- the UI should prefer `current grade` plus `next safer upgrade` over generic `warning` chips
- receipts should say whether the operator accepted degradation temporarily or actually upgraded the state

## ADR-147 — Byte posture deserves its own page, not one fused mode selector

**Decision:** Treat current visibility, current bind, current byte materialization, and future-arrival default as separate public answers that may be rendered together on one Byte posture page but may not collapse into one mode label.

**Why:** Current Resilio evidence still shows how useful the posture language is and how easy it is for the same selector to quietly speak for later defaults and path behavior too.

**Implications:**

- `mode` may remain useful shorthand but cannot be the only semantic home of the answer
- current-share truth and later-default truth must remain independently queryable
- receipts must say whether the mutation touched `current`, `future`, or `both`

## ADR-148 — Ciphertext-only custody must publish restoreability, not only possession

**Decision:** Any encrypted-only or ciphertext-only seat must expose one restoreability ladder showing the current strongest honest recovery path and the missing prerequisites for a stronger one.

**Why:** Current Resilio evidence still shows that encrypted custody is valuable while the recovery path depends on key continuity, database continuity, and seat capability ceilings that are too important to leave implicit.

**Implications:**

- ciphertext presence is not sufficient proof of practical recovery
- saved-capability and continuity proofs belong to the ordinary product model
- encrypted Archive and live-share restore remain separate truths

## ADR-149 — Same-host derivation is lineage, not a trick share subtype

**Decision:** Same-host source→child families must be modeled as lineage families with explicit rights ceilings, topology verdicts, and reattach states.

**Why:** Current Resilio evidence still shows a real same-host workflow, but continuity remains too easy to lose inside remove/re-share and reconnect caveats.

**Implications:**

- reattach should be a first-class reviewed action when continuity honestly survives
- recreate must remain visibly different from reattach
- loop safety and source dependence must be rendered as lineage truth, not only blocked controls

## ADR-150 — Safe eviction must cite last-full-copy risk explicitly

**Decision:** Any action that materially reduces local byte presence must pass through a fetchability surface whenever it may remove the last well-evidenced full copy or the last easy recovery route.

**Why:** Current Resilio evidence still shows how placeholders and Archive help, but also how easy it is for `remove from this device` or manual restore folklore to hide who still really has the bytes.

**Implications:**

- placeholder visibility never counts as enough recovery proof by itself
- Archive route truth and live-peer witness truth must remain separate rows
- bulk clear/evict operations need the same semantic discipline as single-path operations when risk is material


## ADR-151 — Identity joins must classify safe join, successor import, and takeover separately

**Decision:** Treat identity-family joins as a first-class reviewed page that distinguishes empty-seat safe join from successor import and takeover risk.

**Why:** Current Resilio evidence still shows that `link device` convenience can conceal control-plane displacement even when local bytes survive on disk.

**Implications:**

- empty-seat proof becomes a public prerequisite for compact join flows
- local-byte survival and local-app continuity remain separate truths
- mixed-cohort or mixed-license joins escalate before any local control plane is displaced

## ADR-152 — Non-empty target intake must publish reuse, merge, and duplicate-risk truth

**Decision:** Any attach or reconnect against an existing directory must expose one typed intake page that classifies empty target, intended continuation, merge candidate, deliberate sibling copy, or blocked mixed material.

**Why:** Current Resilio evidence still shows how easy it is for path continuity and duplicate repair to collapse into disconnect/connect ritual and indexed-folder folklore.

**Implications:**

- default-path suggestion does not outrank intended continuity silently
- strongest available reuse proof becomes public before commit
- deliberate sibling creation remains visibly different from repairing the original bind

## ADR-153 — Delegation must publish rights ceiling and local-drift truth together

**Decision:** Every non-trivial member-rights surface must show current effective right, strongest admissible ceiling, onward-share power, and local-drift consequences together.

**Why:** Current Resilio evidence still shows rights ceilings split across folder type, peer relation, local-child caveats, and read-only overwrite/suspension behavior.

**Implications:**

- disabled stronger rights need product-language explanations
- onward delegation and byte mutation stay separate truths
- read-only local edits cannot remain invisible just because they do not propagate upstream

## ADR-154 — Stable title, local label, disk basename, and outward artifact label are separate name planes

**Decision:** Treat naming as a multi-plane public object rather than one generic `folder name` field.

**Why:** Current Resilio evidence still shows useful divergence between local UI name, disk name, and outbound artifact labels, but not one ordinary page that keeps their scope honest.

**Implications:**

- local relabel, path rename, and artifact relabel become different reviewed actions
- outward artifacts keep their historical labels unless explicitly reissued
- aligned name planes may be rendered calmly, but divergent planes may not be hidden


## ADR-155 — Hidden runtime service material must have a first-class integrity page

**Decision:** Treat continuity-bearing runtime material as a public product object with typed integrity, ownership, and repair outcomes rather than a hidden implementation detail.

**Why:** Current Resilio evidence still shows that hidden service material is real and load-bearing, but also that operators encounter it too often only through corruption or missing-file warnings.

**Implications:**

- service material may remain hidden on disk without being hidden semantically
- continuity-preserving repair must remain visibly different from clean rebind
- duplicate-runtime or foreign-ownership conflicts need product-language explanations and receipts

## ADR-156 — Exclusion policy is governance, not advanced syntax

**Decision:** Treat exclusion rules as first-class policy with scope, matching, and accounting semantics instead of leaving them primarily in raw rule files.

**Why:** Current Resilio evidence still shows that `not indexed` and `not counted` are meaningful product outcomes, but the ordinary answer remains too dependent on hidden case-sensitive text syntax.

**Implications:**

- the product should simulate rule impact before commit
- shipped defaults and local overrides remain separate policy origins
- peer divergence in exclusion policy must stay visible rather than surfacing later as mysterious size mismatch

## ADR-157 — File-class delay windows are chronology policy, not merely config knobs

**Decision:** Treat mutation-delay policy as a reviewed chronology surface with live pending rows, rationale, and safe release actions.

**Why:** Current Resilio evidence still shows that delay windows are useful for unstable editor workflows while the current contract still routes ordinary users through storage-folder JSON and restart ritual.

**Implications:**

- healthy batching windows must remain visibly different from suspected lock/conflict symptoms
- manual release actions need explicit chronology-risk language
- baseline delay policy and temporary holds remain separate origins

## ADR-158 — Visible transfer order must name its authoritative execution source

**Decision:** Any surface that displays inbound work order must identify whether it is showing authoritative execution order or a non-authoritative browse/list order.

**Why:** Current Resilio evidence still shows that queue prioritization is valuable while UI-visible order and actual priority execution can still diverge.

**Implications:**

- inherited global priority and frozen local override must remain distinct states
- exceptions and non-splittable transfers require typed explanations
- queue-policy mutations must leave receipts stating whether inheritance changed


## ADR-159 — Shell integration is acceleration, not semantic authority

**Decision:** Shell/file-manager integration may accelerate actions but must never be the only semantic home of materialization, evict, share, or restore truth.

**Why:** Current Resilio evidence still shows useful shell convenience coupled to extension health, platform ritual, and filesystem-class limits.

**Implications:**

- every shell-accelerated action needs a product-native parity path
- shell health and semantic availability remain separate facts
- shell-repair and product-bypass decisions leave different receipts

## ADR-160 — Byte-presence mutation and object destruction must never share one unlabeled remove path

**Decision:** Distinguish local byte eviction, local presence drop, and global destruction as separate reviewed action families.

**Why:** Current Resilio evidence still shows placeholder convenience while read-write placeholder deletion can still imply share-wide destruction.

**Implications:**

- last-copy proof is mandatory before dangerous action families
- after-state preview must show local visibility and remote existence separately
- dense surfaces may compress labels but may not collapse the action families

## ADR-161 — History retention needs one product-owned access and restore page

**Decision:** Retained versions/deletions must compile to one history-access page with seat parity, candidate ordering, and restore consequences.

**Why:** Current Resilio evidence still shows useful Archive retention while access and restore truth remain split across desktop UI, hidden folders, and platform-specific omissions.

**Implications:**

- candidate ordering must stay explicit
- restore-in-place, restore-as-branch, and export-only remain distinct actions
- history access and restore capability remain separate facts

## ADR-162 — Filesystem-shape fidelity needs one rollup audit before specialist drill-ins

**Decision:** Provide one ordinary rollup page for link-node, metadata-channel, invalid-name, and bundle-cohesion risk before sending the operator into specialist pages.

**Why:** Current Resilio evidence still shows serious treatment of these risks while the ordinary answer remains fragmented across hidden policy files and multiple support articles.

**Implications:**

- one rollup verdict names the current target-profile fidelity class
- deeper alias-edge and metadata pages remain available without being the first required stop
- reduced-fidelity acceptance and validation horizon remain explicit receipts


## ADR-163 — External infrastructure roles are first-class visibility objects

**Decision:** Tracker/discovery, relay, landing-page, update-check, telemetry, and account-related services must be modeled as explicit observer/service-role objects with fact ceilings and hard non-capabilities.

**Why:** Current Resilio docs are usefully honest about what these services can and cannot see, but the answer still lives across multiple security/help pages. AnonSync should expose one ordinary matrix instead of relying on reassurance prose.

**Implications:**

- visibility pages distinguish observer classes, fact classes, and plaintext ceilings
- service-role pages distinguish observation from operational influence
- disablement/replacement review becomes explicit and receipt-bearing

## ADR-164 — State-root attachment is a reviewed continuity boundary

**Decision:** Existing local state must be attached, imported, quarantined, or blocked through reviewed continuity classification rather than implicit path discovery.

**Why:** Current Resilio docs show that storage-path changes, service-user changes, and unsupported cloning can land operators in a different local world or in clone-risk ambiguity without one ordinary page owning the answer.

**Implications:**

- state-root pages publish active world identity and clone/shadow risk
- attach/import flows classify same-world attach, successor import, stale backup, clean branch, foreign world, and clone risk explicitly
- apparently empty state is treated as a continuity question before it is treated as ordinary absence



## ADR-165 — Helper use is one policy stack, not scattered preference folklore

**Decision:** Treat tracker, relay, LAN discovery, pinned hosts, proxy posture, and temporary overrides as one reviewed helper-policy stack with explicit scope and precedence.

**Why:** Current Resilio docs still show real helper control, but the effective answer remains too distributed across folder preferences, global preferences, configuration mode, and troubleshooting notes.

**Implications:**

- helper policy pages publish per-layer precedence and effective verdicts
- route previews must name which layer made a helper required or merely allowed
- helper narrowing and widening become receipt-bearing policy actions

## ADR-166 — Bootstrap provenance and learned route residue are public state

**Decision:** Treat helper-catalog source, learned helper coordinates, cached endpoints, and stale route residue as public provenance objects rather than hidden network trivia.

**Why:** Current Resilio docs still make vendor bootstrap, manual host overrides, and cache-clearing steps operationally important, yet the product-level answer remains article-shaped.

**Implications:**

- bootstrap-source pages show provenance, freshness, and residue explicitly
- route narrowing is not considered complete until residual widening facts are reviewed
- private or manual bootstrap replacement must state its trust and failure domain

## ADR-167 — Host cadence is a reviewable freshness-versus-wakefulness contract

**Decision:** Treat notifications, periodic rescans, helper refresh, settings-save cadence, logging/profiling, and quiet-host posture as one reviewed cadence model.

**Why:** Current Resilio docs still show that wakefulness and freshness tradeoffs are real, but the ordinary answer still lives across watcher warnings, rescan docs, NAS-sleep guidance, and advanced settings.

**Implications:**

- host-cadence pages show current loops and their costs in one place
- quiet-host changes must preview freshness loss and diagnostic loss before commit
- watcher exhaustion, disabled rescans, and aggressive quieting remain distinct explanatory states

## ADR-168 — Capability is a provenance stack, not a flat entitlement badge

**Decision:** Capability surfaces must publish which source rows grant or withhold power, whether remote dependence exists, and what survives expiry or offline operation.

**Why:** Current Resilio docs show useful capability families, but the ordinary right-to-run answer still depends on licensing, FAQ, update, and platform notes.

**Implications:**

- capability source becomes a first-class page and object family
- remote/account dependence must be explicit when it exists
- expiry or downgrade cannot silently remove verbs without cited source failure

## ADR-169 — Compatibility must distinguish data-safe, join-safe, and blocked outcomes

**Decision:** Compatibility review must separate wire/data compatibility, identity/join compatibility, and capability/edition fences instead of flattening them into one green or red label.

**Why:** Current Resilio docs keep those truths real, but still spread them across FAQ, update, and licensing articles.

**Implications:**

- compatibility gate becomes a first-class review page
- blocked or risky mixes must cite the winning boundary
- storage continuity and subject risk must remain adjacent to the verdict

## ADR-170 — Alert delivery is a carrier/gate pipeline, not a notification toggle

**Decision:** The product must model event origin, carrier, permission gates, suppression, and missed-event recovery explicitly.

**Why:** Current Resilio docs are candid about platform and permission asymmetry, but still force the operator to reconstruct one answer from several places.

**Implications:**

- alert delivery becomes a first-class page and receipt family
- `notifications enabled` cannot imply reliable delivery by itself
- missed-event recovery must stay near the carrier verdict

## ADR-171 — Creation verbs must compile to explicit subject kinds

**Decision:** `sync`, `backup`, `send`, `ciphertext custody`, and `same-host derivation` must remain explicit kind choices with published contract differences.

**Why:** Current Resilio docs expose these kinds usefully, but still scatter the meaning across `+` menus, share dialogs, and platform-specific articles.

**Implications:**

- subject kind chooser becomes a first-class page
- creation surfaces must compare authority, retention, deletion, and continuity consequences before commit
- blocked kinds must publish why they are unavailable here and which stronger surface can admit them

## ADR-172 — Issue diagnosis begins with one family verdict and first safe action

**Decision:** Every materially broken-looking state must compile to one ordinary issue-home verdict before the product offers deeper repair or diagnostic moves.

**Why:** Current Resilio docs still make operators combine status rows, peer columns, warnings, and troubleshooting articles just to learn the first safe action.

**Implications:**

- issue-home becomes a first-class page and object family
- first actions must remain less destructive than later repair rungs when evidence allows
- `unknown` remains allowed only with explicit missing-evidence rows

## ADR-173 — Environment conflict must separate locks, weak detection, and unsafe mixed access

**Decision:** Model local-lock pressure, deliberate delay windows, weak notification confidence, and foreign-writer topology risk as separate but combinable conflict classes.

**Why:** Current Resilio docs are candid about all of them, but still spread the truth across lock pages, delay files, SMB caveats, and detection guidance.

**Implications:**

- environment-conflict becomes a first-class page
- unsafe mixed access may block blind retry or repair
- weak change detection cannot masquerade as normal settled state

## ADR-174 — Repair must stay an ordered copy-safe ladder with explicit preconditions

**Decision:** Heavier recovery work must render as an ordered repair plan whose rungs are gated by preservation proof and environment preconditions.

**Why:** Current Resilio repair advice is practical, but the ordinary answer still lives across several articles and hidden-file rituals.

**Implications:**

- repair-plan becomes a first-class page and receipt family
- remove/re-add or service-material reset cannot lead the ladder while lighter truthful rungs remain
- environment conflict remains adjacent to repair eligibility

## ADR-175 — Crash capture must publish artifact origin, runtime provenance, and disclosure state

**Decision:** Crash/evidence capture must expose existing artifacts, capture prerequisites, runtime/state-root origin, freeze manifests, and disclosure state explicitly.

**Why:** Current Resilio docs still send operators into hidden storage and service-account paths, restart ritual, and self-serve support boundaries to answer ordinary crash questions.

**Implications:**

- crash-capture becomes a first-class page
- evidence collection stays separate from disclosure
- artifact provenance must cite runtime principal and state-root origin when known


## ADR-176 — Active bind path is first-class custody, not a column

**Decision:** Every locally present subject must have a first-class page that publishes current bind path, bind root, storage/volume facts, and relocation eligibility.

**Why:** Current Resilio docs are honest about move limits and local-only rename, but still leave too much of the operator answer implicit until later errors or support reading.

**Implications:**

- share-path becomes a first-class page
- storage/volume facts stay adjacent to move eligibility
- broken binds remain inspectable instead of becoming generic missing-path errors

## ADR-177 — Non-trivial relocation must compile to one review grammar

**Decision:** Cross-domain moves, missing-path repair, and deliberate rebinds must use one relocate-review grammar with explicit continuity class and peer fallout.

**Why:** Current Resilio docs are practical, but still split relocation truth across move FAQs, duplicate-folder workarounds, and folder-not-found repair.

**Implications:**

- relocate-review becomes a first-class page and receipt family
- `remove and re-add` cannot hide severed peer continuity
- missing-path repair and deliberate move remain comparable operations

## ADR-178 — Pathless disconnected presence is a real subject state

**Decision:** A known subject without a local path must remain a first-class page with remembered-bind, reconnect, and removal-scope truth.

**Why:** Current Resilio docs make disconnected folders real but still semantically overloaded.

**Implications:**

- disconnected-share becomes a first-class page
- reconnect is a reviewed choice, not a magical row action
- removal scope must be visible before apply

## ADR-179 — Rename/move actions must publish remote replay expectations

**Decision:** Any rename or move with remote consequences must publish local meaning, remote expectation, replay basis, and fallback near the action and receipt.

**Why:** Current Resilio docs honestly explain archive/hash replay, but only in a separate article rather than where the action semantics naturally belong.

**Implications:**

- rename/move explanation becomes a first-class page or drawer
- relabel and disk-path rename stay separate
- history/archive dependence must be explicit whenever replay quality depends on it


## ADR-180 — Surface parity must be reason-coded, not inferred from missing controls

**Decision:** Every seat/surface pair must publish a reason-coded capability matrix showing what verbs are available here, what verbs are unavailable, and which stronger surface can complete them.

**Why:** Current Resilio docs are candid that desktop, Linux/WebUI, Android, and iOS differ materially, but the ordinary answer still lives in separate platform articles rather than one stable page.

**Implications:**

- surface-capability becomes a first-class page and receipt family
- absent buttons no longer count as sufficient explanation
- fallback surfaces must remain semantically honest about what is lost here

## ADR-181 — External edit must declare copy-versus-live-bind before launch

**Decision:** Any cross-app edit flow must state whether the target app receives a live writable bind, a local materialization, or an exported copy, together with the exact save-back contract.

**Why:** Current Resilio docs honestly describe iOS copy-based editing, but only in a platform tutorial instead of next to the action itself.

**Implications:**

- external-edit-review becomes a first-class page
- save-back becomes an explicit step when required
- replacement, sibling-create, and detached-copy outcomes remain distinct

## ADR-182 — Background freshness must publish suspend gates and catch-up risk

**Decision:** Background delivery must model platform eligibility, current suspend gates, unattended freshness floor, and post-resume catch-up risk explicitly.

**Why:** Current Resilio docs are candid about desktop, Linux, Android, and iOS differences, but still spread the answer across background, battery, task-killer, network, and platform notes.

**Implications:**

- background-delivery becomes a first-class page and receipt family
- `online` is no longer treated as an adequate unattended-delivery answer
- stale-edit and resume risk remain adjacent to catch-up actions

## ADR-183 — Mobile storage is custody, not merely quota

**Decision:** Constrained or sandboxed seats must publish app/runtime data, synced user data, downloads, cleanup scope, and reacquireability on one ordinary page.

**Why:** Current Resilio docs still split mobile storage truth across share details, downloads, shared links, and storage settings.

**Implications:**

- mobile-storage becomes a first-class page
- cleanup verbs must publish local/remote/history scope before apply
- sandbox/container facts become public state rather than hidden implementation detail

## Revision addendum — capture ingest is a first-class relationship, not a backup special-case after rev0176

Architecture should now assume:

- capture-only ingest is a first-class relationship with its own source-domain object, sink-assignment object, landed-proof object, and cleanup-review object
- a source-domain grant and a sink durability class are different architectural facts and must be modeled separately
- `landed under policy` is a computed state over evidence, not a synonym for `queued`, `progress visible`, or `one sink has a copy`
- source cleanup receipts must preserve the difference between freeing source storage, pausing future ingest, and disconnecting the relationship entirely


## ADR-184 — Runtime authorship must publish the acting OS principal

**Decision:** Every seat must expose the exact OS principal and launch mode that act on disk, together with the storage root that belongs to that authority world.

**Why:** Current Resilio docs are candid that Windows service, Linux package, NAS package, and headless macOS runs use materially different principals, but the ordinary answer still lives across host-specific articles instead of one stable page.

**Implications:**

- execution-principal becomes a first-class page
- service-versus-user semantics stop hiding behind the product brand
- storage-root custody stays adjacent to runtime authorship

## ADR-185 — Filesystem grant proof must name the grant family and covered operations

**Decision:** Path writability must publish its grant family and the operations currently proven, rather than collapsing into `accessible` or `permission denied`.

**Why:** Current Resilio docs still spread owner/group/ACL/internal-user/provider truths across Linux, NAS, macOS, and troubleshooting pages.

**Implications:**

- filesystem-grant becomes a first-class page
- file versus directory proof remain distinct
- sampled or inherited proof stays labeled as such

## ADR-186 — Principal or storage-root change is a continuity review, not a toggle

**Decision:** Any change to runtime principal, service mode, package mode, or storage root must open a reviewed same-world versus successor-world decision before apply.

**Why:** Current Resilio docs still show that changing service user or storage location can yield a different storage root and an empty-looking inventory that must be re-added or reconnected.

**Implications:**

- principal-switch-review becomes a first-class page
- empty-inventory surprises after a host-mode change become a pre-apply warning rather than a post-apply mystery
- authority gain and world continuity stay separate truths

## ADR-187 — Blocked-path repair must prefer in-place grant repair over world replacement

**Decision:** Permission-repair flows must order their ladder from least world-disruptive grant repair toward stronger principal/world changes, with operation-specific retests after each rung.

**Why:** Current Resilio docs give practical repair advice, but it is still scattered across host-specific troubleshooting and permission pages instead of one reviewed ladder.

**Implications:**

- blocked-path-repair becomes a first-class page
- retests must prove the specific operations restored
- successor-world escalation remains explicit when it is the only remaining fix


## ADR-095 — Reachability truth is a first-class contract, not a side effect of helper toggles

**Decision:** Model listener endpoints, advertised endpoint claims, pairwise route verdicts, and reachability repair ladders as first-class product objects with receipts.

**Why:** Current Resilio docs are candid that directness depends on listening ports, NAT/firewall/proxy posture, LAN discovery, relay fallback, and manual endpoint pins. They still spread the ordinary answer across Preferences, Folder Preferences, mobile helper settings, ports/protocols notes, and troubleshooting pages.

**Implications:**

- every seat can render one listener endpoint page with bind facts, advertised claims, and ingress-proof grade
- every peer pair can render one route-proof page with winning path, losing candidates, blockers, and counterfactuals
- degraded reachability always has one least-destructive repair ladder with widening cost, retest, and rollback
- manual endpoint pins and learned endpoints keep provenance, freshness, and scope instead of collapsing into raw `IP:port` folklore

## ADR-096 — Chronology authority must publish confidence, winner rule, and timestamp source

**Decision:** Model clock validity, chronology-confidence grade, offline-return authority, mtime-source truth, and restore replay timing as first-class product objects with receipts.

**Why:** Current Resilio docs are candid that time skew blocks transfer, that offline return can outrank later online edits, that mtime truth can fall back to database-only, and that restore can re-archive itself if runtime timing is wrong. They still spread the ordinary answer across warnings, power-user tables, FAQ prose, and Archive instructions instead of one stable page family.

**Implications:**

- every seat can render one clock-authority page with peer skew, policy window, consequences, and retest proof
- every surprising returning-offline overwrite can render one offline-replay review before apply
- every timestamp-fidelity problem can render one mtime-integrity page that separates disk truth from database truth
- every restore can render one restore-replay review that names scope, runtime preconditions, and re-archive risk


## ADR-097 — Semantic tradeoffs from convenience or optimization need first-class pages

**Decision:** Model read-only overwrite behavior, placeholder-removal scope, hash/index readiness, and transfer-method recovery cost as first-class product objects with receipts.

**Why:** Current Resilio docs still spread these truths across the read-only FAQ, Folder Preferences, the RSLS article, the power-user table, and the internal-tasks warning page. That is candid support knowledge. It is not one durable operator contract.

**Consequences:**

- read-only drift can publish exact class fate before any destructive overwrite is armed
- placeholder removal can separate local eviction, global delete, and guardrail remap explicitly
- readiness can separate scanned names from semantically trustworthy operations like placeholder rename or preseed release
- fast transfer can publish interruption and restart cost alongside speed claims


## Revision addendum — ADR: list metrics are contracts, not ornaments

**Decision:** Any displayed size/count metric must have a named contract, and any subject cleanup claim must disclose hidden managed residue.

**Why:** Current Resilio docs are candid that ignored files are not counted, placeholders are 0-byte stand-ins, `.sync` and `.!sync` are real managed byte families, and rescans/hashing can make views provisional. Those truths are valuable; the scattered explanation path is not. AnonSync therefore treats metric meaning and cleanup residue as first-class design objects rather than support notes.

## Revision addendum — target topology and provider grants are architectural state, not UI trivia

The archive now records a stronger design decision:

- graph relation (`disjoint`, `child`, `duplicate bind`, `self-route edge`) is architectural state
- provider-root grant proof is architectural state
- entitlement dependence of same-host edges is architectural state
- return continuity grade for removable targets is architectural state

Any implementation that hides these as mere warnings or platform quirks would violate the product model.


## ADR-098 — Capability artifacts, requester review, and grant mutation need first-class pages

**Decision:** Model share-capability family, incoming requester review, member-grant mutability, and manual-claim semantics as first-class product objects with receipts.

**Why:** Current Resilio docs are candid that keys, links, QR carriers, requester approval, mutable grants, and revocation are all real. They still spread the ordinary answer across share-dialog docs, key/link architecture docs, user-management docs, and mobile sharing guides instead of one stable page family.

**Consequences:**

- every subject can render one share-capability page with artifact family, carrier equivalence, approval posture, and rights ceiling
- every live incoming claimant can render one requester-review page with proof, policy basis, and durable consequence preview
- every member grant can render one access page with origin, editability ceiling, and future-update revocation scope
- every paste / scan / browser handoff can render one manual-claim page that distinguishes raw capability material from reviewed claim artifacts


## ADR addendum after rev0184 — class cliffs deserve public pages

**Decision:** Keep governed subject class, class-upgrade cutover, linked-seat breakout, and peer-row grouping basis visible as first-class public interface objects.

**Why:** Current Resilio docs still make operators combine Standard-vs-Advanced architecture, upgrade how-to, linked read-only workaround, and peer-list screenshots to understand one ordinary authority story. AnonSync should publish that story directly.

## ADR addendum after rev0185 — performance visibility needs causal pages, not decorative telemetry

**Decision:** Keep graph window meaning, per-peer route/RTT attribution, disk-pressure truth, and workload-shaped throughput expectations visible as first-class public interface objects.

**Why:** Current Resilio docs still make operators combine the Performance Overview article, slow-speed troubleshooting, and scattered preference notes to understand one ordinary performance story. AnonSync should publish that story directly.


## ADR addendum after rev0186 — evidence custody needs first-class pages, not support rituals

**Decision:** Keep telemetry families, profiler enablement, outbound diagnostic sends, and local evidence retention visible as first-class public interface objects.

**Why:** Current Resilio docs still make operators combine power-user settings, debug-log collection articles, hidden storage paths, and crash-log guides to understand one ordinary diagnostics story. AnonSync should publish that story directly.



## ADR addendum after rev0187 — control surfaces need first-class pages, not browser and filesystem rituals

**Decision:** Keep control-surface kind, listener audience, browser distrust state, and access-recovery preservation grade visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that WebUI is the default path on Linux and Windows service installs, that listeners are loopback-only by default until deliberately widened, that browser warnings have both temporary and durable repair paths, and that one password-reset ritual can duplicate the device row and reset preferences. Those truths are valuable; the scattered explanation path is not. AnonSync should publish that story directly.

## ADR addendum after rev0193 — namespace blockage and portability repair deserve public pages

**Decision:** Keep namespace blockage, conflict-artifact counterpart proof, unsupported-entry consequence, and portability-repair scope visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that path portability differs across seats, `.Conflict` artifacts still correspond to real remote data, Windows link classes are unsupported, Unix symlink targets are not implicitly included, and path-handling toggles can change whether the share emits conflicts or simply stops syncing. Those truths are valuable; the scattered explanation path is not. AnonSync should publish that story directly.
## ADR addendum after rev0194 — freshness claims and rescans deserve public pages

**Decision:** Keep freshness basis, detection downgrade, rescan scope/non-effects, and changed-object publication stage visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that notifications can fail, rescans are periodic/startup/manual, watcher exhaustion and service-path workarounds can degrade freshness, and internal background work can still be recoverable. Those truths are valuable; the scattered explanation path is not. AnonSync should publish that story directly.
## ADR addendum after rev0195 — discovery basis and route widening deserve public pages

**Decision:** Keep discovery basis, pairwise route truth, least-widening connectivity repair, and observer-delta review visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that peers may be found through tracker, LAN discovery, or predefined hosts; that direct is preferred while relay is a slower fallback; that trackers and discovery lanes learn concrete share/endpoint facts; and that `LAN only` tightening can still leave remembered public endpoints active until cache is cleared. Those truths are valuable; the scattered explanation path is not. AnonSync should publish that story directly.

## ADR addendum after rev0196 — quiet posture and motion cause deserve public pages

**Decision:** Keep motion basis, quiet-window semantics, bottleneck cause, and resume catch-up truth visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that scheduled `Paused` still permits some semantic effects, that runtime/power policy can intentionally take a seat offline, that hidden work can consume time before visible transfer, and that slowness can be caused by relay, small files, remote-upload ceiling, disk, or host interference. Those truths are valuable; the scattered explanation path is not. AnonSync should publish that story directly.


## ADR addendum after rev0197 — hidden subject spine and sidecar policy deserve public pages

The architecture should now treat hidden subject namespace as first-class model state, not incidental filesystem litter.

That implies:

- subject objects should enumerate payload, continuity spine, sidecar policy, history, and transient hidden-byte families explicitly
- sidecar-policy objects should encode locality and peer-agreement rather than only storing raw pattern text
- repair plans must distinguish preserved continuity from recreated successor epochs
- browse surfaces should expose safe observation contracts for managed hidden bytes without endorsing raw manual mutation

## ADR addendum after rev0198 — install eligibility and cohort cutover deserve public pages

**Decision:** Keep install-target eligibility, linked-cohort uniformity, upgrade-boundary continuity, and package-lane ownership visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that v3 is personal-only, Business stays on v2, Windows Server is unsupported for v3, mixed v2/v3 linked cohorts can lose UI/share configuration, and update rituals differ by install lane. Those truths are valuable; the scattered explanation path is not. AnonSync should publish that story directly.


## ADR addendum after rev0200 — advanced overrides and precedence deserve public pages

**Decision:** Keep advanced-override inventory, hidden safety posture, peer-memory retention / clearance, and runtime-bias disclosure visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that hidden advanced settings and config files can materially change destructive behavior, retention, discovery cadence, route memory, and resource bias, and that some of these changes require restart or explicit clearance. Those truths are valuable; the scattered explanation path is not. AnonSync should publish that story directly.


## ADR addendum after rev0202 — external recipe provenance and postcondition proof deserve public pages

**Decision:** Keep external-recipe provenance, command-step exactness, off-product lane witness, and postcondition verification visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that some repairs happen through commands, hidden-file operations, browser trust workarounds, config edits, and service restarts. Those truths are valuable; the scattered explanation path is not. AnonSync should publish those truths directly and require a reread proof after execution.

## ADR addendum after rev0203 — warnings deserve public ownership pages

**Decision:** Keep warning kind, blast radius, safest next rung, and acknowledgment / residue history visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that tracker loss, hidden-work backlog, watcher exhaustion, ghost-file warnings, database corruption, service-file loss, path-loss prompts, merge-risk prompts, and time-difference failures are materially different realities. Those truths are valuable; the scattered explanation path is not. AnonSync should publish those truths directly and keep dismissal separate from proof-backed repair.

## ADR addendum after rev0204 — mobile source classes and path classes deserve public pages

**Decision:** Keep mobile source-class truth, path-class admission, durable-sink authority, and local-clear reacquireability visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that Camera Backup, Android Backup, Simple Mode, SD-card authority, sandboxed iOS storage, copied-out iOS edits, download history, and autosleep/battery gating all materially change the contract. Those truths are valuable; the scattered explanation path is not. AnonSync should publish those truths directly.

## ADR addendum after rev0205 — compromised seats and residual authority deserve public pages

**Decision:** Keep compromised-seat posture, containment-lane choice, rotation-rebuild sequence, and residual-authority truth visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that disk encryption changes stolen-seat danger, that linked seats act as Owners, that remote unlink is unavailable, that subject-local disconnect is future-facing only, and that broader rotation may be required. Those truths are valuable; the scattered explanation path is not. AnonSync should publish those truths directly.

## ADR addendum after rev0206 — bounded handoff and residue deserve public pages

**Decision:** Keep bounded-handoff posture, redemption-lane truth, receive-inbox ownership, and transfer-history residue visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that file send is one-way, that open-link audience is broad, that desktop and mobile receive lanes differ materially, and that history cleanup is not the same thing as byte cleanup. Those truths are valuable; the scattered explanation path is not. AnonSync should publish those truths directly.


## ADR addendum — support lane, capture depth, and crash-custody must be first-class after rev0207

**Decision:** Support entitlement, diagnostic capture depth, outbound report route, and crash-artifact residue must remain explicit first-class state.

**Why:** Current Resilio docs are candid that v3 self-serve and Business support differ, that debug logging, profiler capture, and crash artifacts are distinct families, that restart and hold time matter, that send routes have different ceilings, and that dump files live in platform/service-specific locations. Those truths are valuable; the scattered explanation path is not.

**Implications:**

- send buttons must compile to reviewed recipient lanes and packet routes
- capture toggles must publish restart/sufficiency/residue state
- crash artifacts must expose class, locality, export status, and cleanup proof
- audit must be able to answer not just what left the machine, but what remained afterward


## ADR addendum after rev0208 — storage floors, byte classes, and reclaim proof deserve public pages

**Decision:** Keep space-pressure floors, byte-class inventory, reclaim previews, and reclaim receipts visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that stop floors, placeholders, Archive retention, mobile storage classes, residual files, and storage-root state all matter. Those truths are valuable; the scattered explanation path is not. AnonSync should publish those truths directly.

**Implications:**

- low-space warnings must resolve to one reviewed floor basis
- byte classes must stay public across clients and cleanup flows
- reclaim actions must preview non-effects and retention cost before apply
- receipts must prove what changed and what remained intact afterward


## ADR addendum after rev0209 — network-path truth deserves first-class pages

**Decision:** Keep network path class, protocol discipline, detection grade, and network-subject admission visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that SMB/network paths differ materially from local folders, that notification support can disappear on certain shares or service workarounds, that mixed direct-plus-Samba mutation can corrupt or roll back files, and that runtime identity can change both access and storage-root consequences. Those truths are valuable; the scattered explanation path is not. AnonSync should publish those truths directly.

**Implications:**

- every remote bind must surface path class and watcher grade before it looks ordinary
- authoritative mutation lane must be explicit whenever alternate lanes exist
- freshness claims must carry detection-grade provenance
- admission flows must be willing to reject an unfit remote path instead of merely working around it



## ADR addendum after rev0212 — encrypted-custody workflow truth deserves first-class pages

**Decision:** Keep encrypted-custody lane classification, opaque-seat posture, recovery-material attestation, and shareable dossier truth visible as first-class public interface objects.

**Why:** Current Resilio docs are candid that encrypted custody is real, that linked seats may need `Disconnected` posture, that non-empty ordinary merge and encrypted landing are materially different branches, and that later recovery depends on saved keys and continuity. Those truths are valuable; the scattered explanation path is not. AnonSync should publish those truths directly.

**Implications:**

- encrypted custody cannot be committed from a generic connect dialog alone
- capability ceiling and recoverability posture must remain adjacent in everyday seat views
- recovery confidence must decay when continuity proof or rehearsal freshness decays
- handoff bundles must export reviewed facts without exporting secrets


## Architecture-decision addendum — typed bootstrap artifacts and intake-route proof after rev0213

The archive should now treat the following as architecture-level decisions:

- artifact parsing produces a typed family verdict, not only carrier-level decode success
- route selection is a first-class decision object that can be reviewed, switched, or abandoned
- intake receipts are distinct objects from join/claim/custody receipts
- exported intake receipts must preserve route truth without becoming live bearer artifacts


## Architecture-decision addendum — destination-world proof after rev0214

The archive should now treat the following as architecture-level decisions:

- every typed artifact can enumerate admissible destination worlds before deeper bind/custody work begins
- standing arrival posture and root policy produce a drafted world, not an unreviewable final world
- rerouting away from a drafted auto-land world is a first-class reviewed mutation
- destination-world receipts are distinct bridge objects between intake receipts and later bind/custody receipts

## Architecture-decision addendum — bind-outcome proof after rev0215

The archive should now treat the following as architecture-level decisions:

- every typed artifact plus destination-world pair can derive one explicit branch-outcome review before non-trivial target commitment
- existing-tree evidence is a first-class object that can carry hard same-ID proof, softer lineage hints, and collision classes separately
- branch-consequence compare is a first-class counterfactual object, not ad hoc UI glue
- bind-outcome receipts are distinct bridge objects between destination-world receipts and later merge/reuse/custody/repair receipts

## Architecture-decision addendum — effective seat posture proof after rev0216

The archive should now treat the following as architecture-level decisions:

- effective seat posture is a first-class derived object, not only a restatement of requested policy
- local mutation handling on narrowed seats is a first-class event object, not only a status symptom
- downward rights inheritance is a first-class graph object, not hidden derivative lore
- seat-posture receipts are distinct proof objects from join, bind, or custody receipts

## Architecture-decision addendum — seat posture change mechanism after rev0217

The archive should now treat the following as architecture-level decisions:

- posture-change mechanism class is a first-class derived object, not only UI glue around grant edits
- transition forecasts are first-class objects carrying byte/path and residue effects, not just rights deltas
- cascade graphs are first-class adjacency objects for posture mutation, not inferred only from current-state derivation graphs
- seat-posture change receipts are distinct proof objects from both grant receipts and steady-state posture receipts


## Revision addendum — model row visibility separately from severance scope

Another architecture decision now becomes explicit:

- **row visibility is not authority state**
- **authority state is not byte retention**
- **byte retention is not returnability**
- **returnability is not severance completion**

Implementation should therefore model at least four separate state planes:

1. visibility plane
2. relation / future-sync plane
3. byte-retention plane
4. retainer / reappearance plane

This avoids reusing one overloaded enum for hidden, disconnected, removed, deleted, and rotated-away objects.


## Architecture-decision addendum — model claim objects separately from action objects

The archive should now treat the following as architecture-level decisions:

- approved post-action statements are first-class derived objects, not only strings attached to receipts
- forbidden stronger phrases are first-class contradiction objects, not help-text prose
- residue planes can support or contradict claims independently of action success
- statement receipts are distinct proof objects from action receipts, even when emitted together


## Revision addendum — cleanup must preserve proof floors explicitly after rev0223

Current Resilio docs still make this seam concrete by saying disconnect, linked remove, local placeholder reversion, Selective-Sync share removal, iOS storage clear, uninstall, and hidden archive cleanup all have different effects on local bytes, visibility, and later recovery.

AnonSync will therefore model consequential cleanup as a typed workflow that can optionally require preservation before apply.
Every cleanup decision must produce a durable receipt describing effective family, surviving witness classes, practical reachability, and the strongest honest post-cleanup claim.


## Revision addendum — architecture must preserve witness visibility metadata

Architecture decision tightened in this pass:

- witness inventory must carry **surface visibility metadata** in addition to existence metadata
- hidden service-state and Archive candidates must be classifiable without forcing unsafe mutation
- receipts must preserve the reviewed surface, not just the reviewed subject
- handoff bundles must carry `exists / inspectable-here / route-required / unavailable-here` as first-class fields


## Revision addendum — model artifact class separately from path, bytes, and scope

Another architecture decision now becomes explicit:

- artifact class is not path class
- path class is not byte presence
- byte presence is not action scope
- action scope is not claim scope

Implementation should therefore model at least four separate fields for acted-on rows:

1. artifact class
2. canonical subject / counterpart reference
3. byte-presence class on current seat
4. effective action scope

This avoids overloading one `file row` object with assumptions that only hold for plain local material.


## Revision addendum — model subject non-arrival verdict separately from warnings and repair actions

Another architecture decision now becomes explicit:

- subject non-arrival verdict is not warning kind
- warning kind is not remedy class
- remedy class is not continuity outcome
- continuity outcome is not post-action claim scope

Implementation should therefore model at least four separate fields for a missing or stalled subject:

1. subject delivery verdict
2. evidence-plane summary
3. least-strong justified intervention
4. continuity outcome if intervention broadens

This avoids overloading one `error` or `status` object with assumptions that only hold for one layer of truth.


## Revision addendum — architecture decision after rev0227: runtime profiles are typed continuity-bearing objects

Decision:

- represent runtime profiles as first-class objects keyed by host, execution principal, storage root, and control-surface configuration
- derive a profile-lineage relation between them rather than assuming one host implies one effective seat
- make share catalogs, identity surfaces, logs, and receipts bind to runtime profile as well as host seat

Rationale:

Current Resilio docs still show that service account, storage path, and control reach changes can materialize as a fresh active profile. AnonSync should therefore not encode runtime envelope as a bag of process flags.


## Revision addendum — architecture decision after rev0232: platform permissions are typed provenance objects

Decision:

- represent platform permission families as first-class typed objects keyed by seat, platform family, and capability family
- record both transition requested and transition observed rather than assuming OS prompt outcome
- bind receipts and claim ceilings to permission events so later surfaces can explain aftermath without re-parsing native state

Rationale:

Current Resilio docs still show that camera, storage, startup, wake, notification, network, and account permissions change different capability families. AnonSync should therefore not encode platform permission as an untyped boolean bag.


## Revision addendum — architecture decision after rev0234: presence proof is multi-plane

Decision:

- represent presence proof as first-class typed objects keyed by seat, peer, share, and optional subject
- record listedness, route witness, eligibility witness, and source witness separately rather than collapsing them into one `online` field
- bind receipts and claim ceilings to presence events so later surfaces can explain aftermath without reconstructing several help-page semantics

Rationale:

Current Resilio docs still show that historical roster presence, current connection, current eligibility, and full-byte source availability can diverge materially. AnonSync should therefore not encode presence as a flat status badge.

## Revision addendum — architecture decision after rev0259: diagnostic route is a first-class object

The archive now needs one more explicit architecture rule:

- diagnostic navigation from a live row must compile into a durable object, not only transient view state

At minimum the system should preserve:

- original entry token/row identity
- current subject scope
- candidate next routes and their expected proof gain
- affected-item slice identity when present
- issued route receipt and freshness state

External help may still exist, but it should be downstream of the owned diagnostic route, not the first-class replacement for it.


## Revision addendum — architecture decision after rev0270: representative-pair judgment is a first-class object

The archive now needs one more explicit architecture rule:

- pairwise performance evidence must compile into a topology-slice object with an explicit generalization ceiling, not just a benchmark result or peer-row annotation

At minimum the system should preserve:

- covered peer pairs or cohorts
- covered directions and route classes
- representative-pair verdict and similarity basis
- plausible counterexample seats
- strongest allowed sentence and stronger rejected sentence
- reopen triggers when topology or evidence changes

A pairwise result may still be useful locally, but it must not silently widen into mesh-wide truth without a first-class representativeness object.


## Revision addendum — architecture decision after rev0272: change-detection coverage is a first-class object

The archive now needs one more explicit architecture rule:

- change discovery must compile into a first-class coverage object with declared blind windows, not just background worker state or a stale `watching` badge

At minimum the system should preserve:

- subject scope and storage class assumptions
- active notification/rescan/manual-probe posture
- expected latency budget and whether it is default, widened, or disabled
- blind-window basis such as watcher exhaustion or unsupported notifications
- cheapest honest intervention rung
- strongest allowed sentence and stronger rejected sentence

A late-appearance story may still be benign, but it must not silently depend on hidden observation gaps without a first-class detection-coverage object.

## Revision addendum — architecture decision after rev0273: freshness-receipt invalidation is a first-class object

The archive now needs one more explicit architecture rule:

- freshness receipts must compile into a lineage object that can be weakened, expired, revalidated, or superseded by later posture drift

At minimum the system should preserve:

- prior receipt identity and covered scope
- later invalidator event and its source
- drift-impact verdict (`unchanged`, `weakened`, `expired`, `superseded`, `unknown`)
- new proof threshold required for revalidation
- supersession boundary between old and new claim
- reopen triggers for the newer claim

A freshness judgment may still be useful later, but it must not silently survive watcher, path, runtime, power, or network changes without a first-class invalidation and rollover object.

## Revision addendum — architecture decision after rev0288: authority policy is a first-class object

The archive now needs one more explicit architecture rule:

- live authority must compile into a first-class policy object rather than being reconstructed from artifact family, seat origin, and help-text caveats

At minimum the system should preserve:

- affected principal or seat family
- resulting authority floor
- delegation ceiling
- mechanism class (`live edit`, `derivative narrowing`, `revocation`, `successor reissue`)
- retained-material truth after cutoff or downgrade
- source-dependence and auto-lowering triggers for derivatives
- receipt lineage and supersession boundary

A seat may still arrive through many carriers, but its ongoing policy must not be trapped inside the carrier family once accepted.

## Revision addendum — architecture decision after rev0289: compile effective policy with provenance and precedence

The archive now needs one more explicit architecture rule:

- every serious policy field must compile into a provenance-bearing effective-state object, not just a resolved value cached on the client

At minimum the system should preserve:

- subject or cohort scope
- field family
- winning effective value
- winning source plane
- losing competing plane when relevant
- precedence reason
- blast radius of edits on that plane
- exception / drift status
- superseded receipt or assumption
- reopen triggers

A visible value may still be enough for quick scanning, but it must not silently stand in for source-of-truth ownership or inheritance state.

## Revision addendum — architecture decision after rev0290: visible names compile into provenance-bearing render objects

The archive now needs one more explicit architecture rule:

- every serious rendered label must compile into a provenance-bearing naming object rather than a single cached display string

At minimum the system should preserve:

- subject scope
- naming plane
- rendered label
- intended audience
- origin event or receipt
- live-versus-residue status
- any linked artifact-family attribution
- later supersession or reset boundary
- strongest allowed sentence and stronger rejected sentence

A string may still be enough for quick scanning, but it must not silently stand in for canonical subject identity, recipient-facing issuance wording, or stale local residue.

## Revision addendum — architecture decision after rev0291: action verbs compile into projection-bearing semantic objects

The archive now needs one more explicit architecture rule:

- every serious rename-like action must compile into a projection-bearing semantic object rather than a button label plus local UI implementation detail

At minimum the system should preserve:

- resolved verb family
- executing projection
- editable plane set on that projection
- changed planes
- untouched neighboring planes
- audience reached
- stronger rejected reading
- supersession boundary to later rename/reset actions

A familiar control may still be enough for quick scanning, but it must not silently stand in for canonical retitle, local alias edit, disk path rename, or artifact relabel.



## Revision addendum — architecture decision after rev0292: reachability compiles into exposure-budget and claim-ceiling objects

The archive now needs one more explicit architecture rule:

- every serious route-policy state must compile into an exposure-budget object and a claim-ceiling object rather than a pile of helper booleans

At minimum the system should preserve:

- target scope
- helper family states
- winning source planes
- discovery lanes in force
- transfer lanes in force
- widest exposure ceiling
- public-route residue or proof gaps
- strongest safe sentence
- stronger rejected sentence
- supersession boundary to later route witnesses or helper changes

Raw toggles may still be enough for quick scanning, but they must not silently stand in for proven LAN-only truth.

## Revision addendum — architecture decision after rev0295: contested subjects compile into repair-bearing contest objects

The archive now needs one more explicit architecture rule:

- every serious contested file or subtree must compile into a repair-bearing contest object rather than a filename badge plus scattered history rows

At minimum the system should preserve:

- contested subject ref
- contest class
- participant set
- live-line verdict
- survivor classes already present
- available repair paths
- runtime prerequisites
- strongest safe sentence
- stronger rejected sentence
- supersession boundary to later repairs or reopened evidence

A warning badge may still be enough for quick scanning, but it must not silently stand in for blocked intake, archive-backed loser fate, or live-repair scope.

## Revision addendum — stop truth, hidden runtime, and restart-boundary architecture decisions

This pass locks the following architecture decisions:

1. **Stop is a first-class contract object.** The model must distinguish `projection-closed`, `background-active`, `service-active`, `pause-requested`, `stop-requested`, `draining`, `stopped-unproven`, and `stopped-proven`.
2. **Projection disappearance does not imply runtime stop.** Any UI shell, browser tab, tray surface, or mobile foreground projection may vanish while the runtime continues; the architecture must never flatten those states.
3. **Drain truth is separate from stop intent.** The system must model pending outbound publication, active transfers, queued index writes, and receipt emission before it can claim a drained stop.
4. **No-further-publication is a proof-bearing ceiling, not a convenience sentence.** The product may only say the stronger sentence after the runtime and its publication lanes have witnessable stop state.
5. **Restart posture is part of stop truth.** Startup-on-boot, service installation, mobile background privilege, and external watchdog relaunch must be represented in the contract.
6. **Restart provenance remains durable.** Reopen or restart cause must remain inspectable because a stop/start boundary can affect indexing chronology and later overwrite interpretation.
7. **Every consequential stop mutation emits a receipt.** The receipt must preserve targeted runtime, drain verdict, proof ceiling, restart posture, and invalidators.


## Revision addendum — architecture decision after rev0299: identity linking compiles into adoption-bearing seat objects

The archive now needs one more explicit architecture rule:

- every serious seat-link operation must compile into an adoption-bearing identity object rather than a QR/paste affordance plus silent side effects

At minimum the system should preserve:

- source seat lineage
- target seat lineage
- direction of adoption
- certificate fate
- subject inheritance set
- subject eviction set
- filesystem-risk class
- version-compatibility posture
- unlink boundary
- latent hidden-member residue
- supersession boundary to later detach/replace actions

A linking control may still be enough for quick scanning, but it must not silently stand in for certificate takeover, inherited authority, or reappearing hidden members.


## Revision addendum — architecture decision after rev0301: birth commitments compile into mutability-bearing objects

The archive now needs one more explicit architecture rule:

- every consequential settings family must compile into a mutability-bearing object rather than a raw key/value editor plus scattered migration lore

At minimum the system should preserve:

- field family
- current effective value
- mutability class
- effect timing
- birth-time preconditions
- successor-required boundary
- carryforward candidates
- strongest safe sentence
- stronger rejected sentence
- supersession boundary to later successor or rollback work

A settings panel may still be enough for quick tweaks, but it must not silently stand in for birth-locked assumptions, successor-required migration, or carryforward loss.


## Revision addendum — architecture decision after rev0303: disclosure truth compiles into observer/fact/carrier objects

The archive now needs one more explicit architecture rule:

- every serious sharing, browser-open, helper, and telemetry action must compile into a disclosure-bearing object rather than a badge plus FAQ prose

At minimum the system should preserve:

- action lineage
- carrier set
- observer roster
- fact-family visibility matrix
- payload-readability class
- strongest safe sentence
- blocked stronger sentence
- proof basis class
- stale-after triggers
- supersession boundary to later carrier or telemetry changes

A lock icon or `private` badge may still be enough for quick scanning, but it must not silently stand in for relay blindness, tracker visibility, browser-service preview, or telemetry export posture.

## Revision addendum — architecture decision after rev0305: event evidence truth compiles into family/horizon/proof objects

The archive now needs one more explicit architecture rule:

- every serious event, rollback, notification, or transfer-history surface must compile into an evidence-bearing object rather than a timestamp row plus folklore

At minimum the system should preserve:

- evidence family
- source locator
- durability class
- retention horizon
- actor-attribution class
- byte-witness class
- chronology-authority class
- strongest safe sentence
- blocked stronger sentence
- invalidators and expiry triggers
- supersession boundary to later stronger or weaker evidence joins

A bell, history list, or timestamp column may still be enough for quick scanning, but it must not silently stand in for durable authorship proof, recoverable bytes, or exportable incident evidence.


## Revision addendum — architecture decision after rev0307: control substrate truth compiles into capsule/sidecar/residue objects

The archive now needs one more explicit architecture rule:

- every serious subject, import, repair, cleanup, and rebind action must compile into a control-substrate-bearing object rather than a path plus hidden-file folklore

At minimum the system should preserve:

- subject identity
- capsule state
- capsule owner / authority class
- sidecar family roster
- editability class per sidecar family
- activation / retroactivity class per sidecar family
- residue classes present
- dual-owner evidence state
- strongest safe sentence
- blocked stronger sentence
- invalidators / reopen triggers
- supersession boundary to later regenerate, fork, or successor work

A file browser may still be enough for quick scanning, but it must not silently stand in for fragile control substrate, editable policy sidecars, or dual-runtime collision risk.

## Revision addendum — architecture decision after rev0309: mutation state compiles into live/persisted/boot-authority objects

The archive now needs one more explicit architecture rule:

- every serious mutation must compile into a durability-bearing object rather than a raw value plus UI optimism

At minimum the system should preserve:

- object / field mutated
- live verdict
- persisted verdict
- boot-authoritative verdict
- storage-home identifier
- runtime principal
- stronger authority plane roster
- next-boot world verdict
- strongest safe sentence
- blocked stronger sentence
- invalidators / reopen triggers
- supersession boundary to later stronger proof

A settings panel may still be enough for quick scanning, but it must not silently stand in for crash durability, boot authority, or storage-world continuity.



## Revision addendum — architecture decision from rev0311

Decision: **Path identity is modeled explicitly, not inferred only from conflict aftermath.**

Implications:

- subject identity must retain rendered name, raw form witness, and canonical comparison basis where relevant
- peer-horizon portability is part of rename/adoption planning
- receipts and audit surfaces must preserve the exact comparison basis used at decision time


## Revision addendum — architecture decision from rev0315

Decision: **Special object fidelity is modeled explicitly, not inferred only from later conflicts or degraded renders.**

Implications:

- subject state must retain object kind, reference-target boundary, and metadata dependency where relevant
- compatibility residue may be lineage-relevant and therefore belongs in receipts and audits
- portability planning must preserve the reviewed fidelity ceiling rather than only raw byte success
