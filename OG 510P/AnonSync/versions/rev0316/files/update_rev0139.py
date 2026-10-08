from pathlib import Path
import shutil

BASE = Path('/mnt/data/anonsync_work')
SRC = BASE / 'anonsync_rev0138'
DST = BASE / 'anonsync_rev0139'
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)

ROOT = DST
DOCS = ROOT / 'docs'

rev = 'rev0139'
timestamp = '2026.03.19.18.50'
codename = 'catalogrelaybudgetwayfinder'

# --- new interface specs ---
(DOCS / '217-discovery-bootstrap-catalog-outage-and-fallback-authority-interface-spec.md').write_text('''# Discovery bootstrap, catalog outage, and fallback-authority interface spec

## Purpose

The archive already has discovery disclosure, route exposure, and route-narrowing residue language.
What it still lacked was one explicit contract for a narrower but very real dependency seam:

> before a node can even apply its declared discovery posture, **who tells it where discovery infrastructure exists at all**, what happens when that bootstrap authority is missing or stale, and which fallback scope is still honest?

Current official Resilio docs make this seam unusually explicit.
They still say Sync learns tracker and relay addresses from `https://config.resilio.com/sync.conf`, that `Cannot get the list of trackers` means the app cannot fetch that configuration file, and that the troubleshooting path is to check browser reachability to that URL, firewall rules, and port access.
A companion connectivity page still says an unreachable catalog blocks tracker/relay learning before the product ever gets to ordinary peer matching.

That is not just networking trivia.
It is a control-plane dependency.

AnonSync should therefore treat discovery bootstrap as one first-class authority object with health, scope, fallback, and receipts.

## Core decision

Every seat must have one explicit **discovery bootstrap authority** record that answers four questions together:

1. where discovery and rendezvous endpoint knowledge came from
2. whether that knowledge is still fresh enough to trust
3. what reduced connectivity envelope remains if bootstrap is unavailable
4. what receipt proves a bootstrap source changed, narrowed, or failed over

The product must never compress this into generic states like `tracker unavailable` or `trying to connect`.
If the node does not currently know where to find discovery infrastructure, that is a different truth from `knows but cannot reach`, and both are different from `intentionally not using centralized discovery at all`.

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- central catalog availability decides whether tracker/relay addresses are known at all
- outage diagnosis begins outside the app, with browser or `wget` checks against the catalog URL
- tracker failure and tracker-list failure are distinct, but easy to collapse into one `cannot connect` story
- manual/predefined-host fallback is documented as a separate troubleshooting move instead of one bounded fallback envelope rendered from the current node state

AnonSync should therefore keep one harder rule:

> bootstrap authority is part of route truth, not a hidden prerequisite that only support pages mention.

## Fixed review order

Every non-trivial discovery-bootstrap surface should render the same sections in the same order:

1. **Bootstrap authority now**
2. **Fetch and freshness health**
3. **Fallback connectivity envelope**
4. **Dependency-change receipt**

### 1) Bootstrap authority now

This section should show:

- source class (`embedded-default`, `fetched-catalog`, `pinned-private-catalog`, `manual-static`, `none`)
- source identifier
- who approved that source
- what endpoint classes it may define (`tracker`, `relay`, `directory`, `rendezvous`, `other`)
- current effective authority rank

The operator must be able to answer: **who currently tells this node where discovery infrastructure exists?**

### 2) Fetch and freshness health

This section should show:

- last successful refresh
- last failed refresh
- whether the current catalog is fresh, stale-but-usable, expired, or absent
- whether transport reachability, TLS validation, signature validation, or content parsing failed
- which currently active endpoints were learned from this authority versus preserved from earlier state

The operator must be able to answer: **is the problem that the catalog is missing, stale, unreachable, or no longer trusted?**

### 3) Fallback connectivity envelope

This section should show one honest answer for what still works if bootstrap authority is degraded:

- `no ambient discovery remains`
- `known-peer direct only`
- `local discovery only`
- `cached private infra only`
- `manual artifact claims only`
- `full discovery envelope retained`

The operator must also see what facts are now uncertain:

- new tracker learning blocked
- relay pool growth blocked
- old cached endpoints may still dial
- peer discovery narrowed to pinned/manual knowledge
- connectivity may remain for existing peers while new joins fail

The operator must be able to answer: **what exact connectivity envelope remains right now, and what did we lose?**

### 4) Dependency-change receipt

This section should show:

- previous bootstrap authority
- resulting bootstrap authority
- freshness before/after
- effective fallback envelope before/after
- any residual endpoint cache that survived the change

The operator must be able to answer: **what later proves whether we changed, lost, or intentionally narrowed discovery bootstrap?**

## Public objects

### `discovery_bootstrap_authority`

Fields:

- `discovery_bootstrap_authority_id`
- `seat_ref`
- `source_class`
- `source_locator`
- `authority_rank`
- `declared_endpoint_classes[]`
- `signature_posture`
- `freshness_state`
- `last_success_at` nullable
- `last_failure_at` nullable
- `active_failure_class` nullable
- `fallback_envelope`
- `created_at`
- `updated_at`

### `discovery_bootstrap_report`

Fields:

- `discovery_bootstrap_report_id`
- `seat_ref`
- `effective_authority_ref` nullable
- `candidate_authority_refs[]`
- `catalog_health_findings[]`
- `fallback_envelope`
- `residual_cached_endpoint_findings[]`
- `next_actions[]`
- `generated_at`

### `discovery_bootstrap_receipt`

Fields:

- `discovery_bootstrap_receipt_id`
- `seat_ref`
- `action` (`fetch-refresh`, `failover`, `pin-private-authority`, `disable-authority`, `clear-cached-bootstrap-state`)
- `before_summary`
- `after_summary`
- `fallback_delta_summary`
- `created_at`

## Main surface

A compact row should read like one of these, not just `tracker unreachable`:

- `bootstrap authority healthy · fetched catalog · refreshed 4m ago`
- `bootstrap catalog stale · cached rendezvous only`
- `bootstrap absent by policy · manual/pinned discovery only`
- `catalog unreachable · new public discovery blocked`

## CLI shape

```text
anonsync discovery bootstrap show
anonsync discovery bootstrap refresh
anonsync discovery bootstrap pin --source private-catalog
anonsync discovery bootstrap explain
anonsync discovery bootstrap receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- a node can lose catalog reachability and still only show `peers aren't connecting`
- the operator must test the catalog URL in a browser just to know whether endpoint authority exists
- cached endpoint reuse survives a bootstrap outage without being visible in route/disclosure reports
- a manual or pinned fallback behaves like an implementation accident instead of a rendered fallback envelope

## Non-clone reason

Resilio's current docs still make discovery bootstrap feel like support lore around one remote `sync.conf` fetch and later tracker troubleshooting.
AnonSync should instead publish discovery bootstrap authority, freshness, fallback envelope, and receipts as first-class state.
''')

(DOCS / '218-egress-only-proxy-and-relay-inevitability-interface-spec.md').write_text('''# Egress-only proxy and relay-inevitability interface spec

## Purpose

The archive already has route classes, transfer budgets, and disclosure policy.
What it still lacked was one explicit contract for a very particular transport posture:

> when a seat is placed behind an egress-only proxy, what changes about direct reachability, inbound expectations, and relay inevitability, and how does the product keep that from masquerading as ordinary degraded networking?

Current official Resilio docs make this seam explicit.
They still say proxy servers prohibit incoming connections and allow only outgoing ones, and that if two Sync instances are both behind a proxy they will be able to talk only via relay; only when one side is behind a proxy can that proxied side still connect directly to the other side.
A connectivity troubleshooting page still folds proxy cases into the same tracker/relay story unless the operator manually reconstructs what that means.

That is not just a settings detail.
It is an asymmetric reachability contract.

AnonSync should therefore treat egress-only proxy posture as one first-class seat property with route consequences rendered up front.

## Core decision

Any seat whose transport is mediated by an egress-only proxy must declare a first-class **reachability asymmetry posture**.
That posture must compile into route explanations, peer compatibility, expected bottlenecks, and honest next steps.

The product must never let `proxy enabled` behave like a harmless transport preference.
For sync semantics it means:

- inbound direct path classes are narrowed or gone
- direct success becomes topology-dependent and asymmetric
- some peer pairings become relay-inevitable unless other explicit private infrastructure exists
- transfer performance and disclosure trade-offs change accordingly

## Fixed review order

Every proxy-mediated transport review should render the same sections in the same order:

1. **Seat reachability posture**
2. **Peer-pair compatibility**
3. **Relay inevitability and cost**
4. **Receipt and reversal**

### 1) Seat reachability posture

This section should show:

- whether the seat is `direct-capable`, `egress-only`, `egress-only-with-overlay`, or `unknown`
- which dial classes remain allowed
- which accept/inbound classes are no longer possible
- whether the posture comes from reviewed policy, ambient environment detection, or both

The operator must be able to answer: **is this seat still directly reachable, only able to dial out, or fully asymmetrical?**

### 2) Peer-pair compatibility

This section should show, for any selected peer pair:

- direct possible
- direct possible only one way
- relay required
- overlay/private-rendezvous required
- blocked by policy

The operator must be able to answer: **for this exact pair, is relay merely allowed, or inevitable?**

### 3) Relay inevitability and cost

This section should show:

- whether relay is optional, preferred, or unavoidable
- whether any relay/private-overlay budget applies
- expected throughput penalty class
- any widened disclosure or infrastructure dependence that follows from the posture

The operator must be able to answer: **what cost and dependency did the proxy posture just buy me?**

### 4) Receipt and reversal

This section should show:

- posture before/after
- whether the seat became egress-only by policy or by detected environment
- which peer-pair route classes changed
- what is required to restore inbound/direct capability

The operator must be able to answer: **what later proves that the seat became relay-bound, and what would undo that?**

## Public objects

### `seat_reachability_posture`

Fields:

- `seat_reachability_posture_id`
- `seat_ref`
- `posture_class` (`direct-capable`, `egress-only`, `egress-only-with-overlay`, `relay-bound`, `unknown`)
- `origin` (`policy`, `detected`, `policy-and-detected`)
- `allowed_dial_classes[]`
- `allowed_accept_classes[]`
- `proxy_ref` nullable
- `updated_at`

### `peer_pair_route_compatibility`

Fields:

- `peer_pair_route_compatibility_id`
- `seat_a_ref`
- `seat_b_ref`
- `direct_posture`
- `relay_requirement` (`not-needed`, `possible`, `inevitable`, `blocked`)
- `best_available_route_class`
- `cost_notes[]`
- `generated_at`

### `reachability_posture_receipt`

Fields:

- `reachability_posture_receipt_id`
- `seat_ref`
- `before_summary`
- `after_summary`
- `pairwise_delta_summary`
- `created_at`

## Main surface

A compact row should read like one of these:

- `direct-capable seat`
- `egress-only seat · inbound direct unavailable`
- `egress-only seat · relay inevitable with 3 peers`
- `egress-only via reviewed proxy · private overlay available`

## CLI shape

```text
anonsync route posture show --seat self
anonsync route posture explain --peer tablet-citrine
anonsync route posture review --proxy corp-egress
anonsync route posture receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- a proxied seat still appears merely `online` or `healthy` without saying it cannot accept inbound direct paths
- relay inevitability is reconstructed only after slow transfers start
- pairwise asymmetry stays hidden behind one generic route icon
- turning on a proxy silently changes route cost and disclosure posture without a receipt

## Non-clone reason

Resilio's current docs still make proxy behavior feel like one preference line and later troubleshooting notes, even though it changes directness asymmetrically and can make relay unavoidable for some peer pairs.
AnonSync should instead make egress-only posture and relay inevitability explicit.
''')

(DOCS / '219-runtime-memory-pressure-subject-budget-and-relief-interface-spec.md').write_text('''# Runtime memory pressure, subject budget, and relief interface spec

## Purpose

The archive already has space pressure, work-phase visibility, and capacity-fit language.
What it still lacked was one explicit contract for another resource truth:

> when the runtime is short on memory, which subjects are causing it, what softer relief remains, and how does the product avoid turning one resource incident into full subject deletion and re-add ritual?

Current official Resilio docs make this seam painfully clear.
They still say the only way to make Sync use less RAM is to remove the biggest folders from Sync from all peers and share the folder again; that removal also deletes the database; and re-adding creates a new database and re-indexes the files while keeping only the current set of files.

That is practical support advice.
It is still not a good resource-relief contract.
Memory pressure is not the same thing as subject retirement.

AnonSync should therefore treat runtime memory pressure as one first-class budget surface with non-destructive relief before destructive subject reset.

## Core decision

Every seat must expose one **memory pressure ledger** that ties runtime memory consumption to concrete subject/index classes and to ordered relief options.
The product must separate at least five answers:

1. memory pressure source
2. current risk to the seat
3. reversible relief options
4. destructive relief options
5. continuity cost of each step

The product must never jump from `out of memory` to `remove the share and add it back` without first rendering what continuity is being thrown away.

## Fixed review order

Every memory-pressure case should render the same sections in the same order:

1. **Current memory pressure now**
2. **Top contributing subjects**
3. **Ordered relief ladder**
4. **Continuity receipt**

### 1) Current memory pressure now

This section should show:

- current memory pressure state (`healthy`, `elevated`, `critical`, `thrashing`, `recovering`)
- current pressure budget and observed usage
- whether the bottleneck is indexing, live transfer, metadata retention, or mixed work
- whether the seat is merely slow, at risk of crash, or already refusing new work

The operator must be able to answer: **how bad is it right now, and what class of work is causing it?**

### 2) Top contributing subjects

This section should rank the top subjects by live memory cost and show:

- subject label
- index/working-set contribution
- whether the load is durable or bursty
- whether the subject is currently active, idle-but-indexed, or partially detachable
- what local continuity artifacts depend on the current state

The operator must be able to answer: **which subjects are expensive, and what would be lost if I relieved them?**

### 3) Ordered relief ladder

The product should always present a relief ladder from least to most destructive, for example:

- slow scan or hashing concurrency
- suspend non-urgent subjects
- narrow local materialization or caches
- postpone history/verification classes
- split future intake across seats
- prepare subject sharding or migration
- rebuild local indexes only
- full subject detach/re-add

Every step must show:

- expected memory delta
- reversibility
- time cost
- continuity cost

The operator must be able to answer: **which softer moves remain before we cross into subject recreation?**

### 4) Continuity receipt

This section should show:

- action chosen
- memory delta target
- before/after continuity class
- whether any index lineage, history, or local proofs were intentionally discarded
- follow-up review references

The operator must be able to answer: **what later proves whether we relieved pressure safely or paid for it by resetting subject state?**

## Public objects

### `memory_pressure_ledger`

Fields:

- `memory_pressure_ledger_id`
- `seat_ref`
- `pressure_state`
- `budget_bytes`
- `observed_bytes`
- `pressure_classes[]`
- `top_subject_refs[]`
- `updated_at`

### `subject_memory_contribution`

Fields:

- `subject_memory_contribution_id`
- `subject_ref`
- `seat_ref`
- `estimated_bytes`
- `contribution_class` (`index`, `active-transfer`, `verification`, `history`, `mixed`)
- `burstiness`
- `reversible_relief_refs[]`
- `destructive_relief_refs[]`
- `generated_at`

### `memory_relief_plan`

Fields:

- `memory_relief_plan_id`
- `seat_ref`
- `target_delta_bytes`
- `ordered_steps[]`
- `strongest_step_class`
- `continuity_cost_summary`
- `created_at`

### `memory_relief_receipt`

Fields:

- `memory_relief_receipt_id`
- `seat_ref`
- `plan_ref`
- `applied_steps[]`
- `before_summary`
- `after_summary`
- `continuity_delta_summary`
- `created_at`

## Main surface

A compact row should read like one of these:

- `memory healthy`
- `memory elevated · 2 subject indexes dominate`
- `memory critical · reversible relief still available`
- `memory critical · destructive subject reset would discard local index lineage`

## CLI shape

```text
anonsync memory status
anonsync memory top-subjects
anonsync memory relief plan --target 2GiB
anonsync memory relief apply <plan>
anonsync memory relief receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator gets an out-of-memory warning without seeing which subjects dominate working set
- the first honest step still looks like `remove and share again`
- destructive reset can happen without continuity cost and evidence loss being shown in the same review
- the product has space-pressure visibility but not memory-pressure visibility

## Non-clone reason

Resilio's current docs still route memory relief through full subject removal and re-add, with database deletion and re-index cost folded into the remedy.
AnonSync should instead publish subject memory budgets and an ordered relief ladder before any destructive reset.
''')

(DOCS / '220-linked-seat-rights-narrowing-and-owner-domain-separation-interface-spec.md').write_text('''# Linked-seat rights narrowing and owner-domain separation interface spec

## Purpose

The archive already has observer-rights decomposition, topology-aware rights editing, and future-arrival posture language.
What it still lacked was one explicit contract for a subtler but important seam:

> when several seats belong to the same person or owner-domain, how does the product let one of those seats become intentionally narrower without pretending it is a different subject, a different owner, or a reconnect-by-key ritual?

Current official Resilio docs make this seam vivid.
They still say all devices linked to one identity act as Owners, and a separate current help page for making one linked device read-only still tells the operator to use a Standard folder with a Read Only key, disconnect the already-connected folder, open `+ -> Enter a key or link`, paste the key, and choose a path manually.

That is not just a workaround.
It means self-owned seat posture and subject identity are still tangled together.

AnonSync should therefore treat per-seat narrowing inside one owner-domain as a first-class rights change, not as share replacement folklore.

## Core decision

A subject should keep one stable subject identity even when seats inside the same owner-domain hold different postures.
The product must let the operator narrow one seat to a less powerful posture without forcing any of these hidden substitutions:

- new artifact family
- new subject class
- disconnect/reconnect ritual
- silent path re-adoption
- new owner-domain meaning

In other words:

> seat posture may narrow without pretending the seat left and rejoined a different subject.

## Fixed review order

Every same-owner seat-narrowing review should render the same sections in the same order:

1. **Owner-domain and seat in scope**
2. **Current versus requested seat posture**
3. **Subject-identity continuity**
4. **Dependent consequences and reversal**
5. **Seat-narrowing receipt**

### 1) Owner-domain and seat in scope

This section should show:

- owner-domain / constellation in scope
- subject in scope
- seat selected for narrowing
- other seats that retain broader posture

The operator must be able to answer: **which one of my seats am I narrowing, and who else stays broad?**

### 2) Current versus requested seat posture

This section should show:

- current effective posture on the seat
- requested posture (`observe`, `receive-only`, `write-blocked`, `names-only`, `other`)
- whether the narrowing changes materialization, writeback, delegation, or future-arrival defaults
- whether the seat already carries local bytes that need separate treatment

The operator must be able to answer: **what exactly becomes narrower on this seat?**

### 3) Subject-identity continuity

This section should show:

- that the subject identity stays the same
- whether any delivery artifact or local bind would change
- whether the seat remains a remembered member of the same owner-domain
- whether reversal later is a posture change, not a rejoin

The operator must be able to answer: **am I narrowing one seat inside the same subject, or creating a second subject in disguise?**

### 4) Dependent consequences and reversal

This section should show:

- effects on local materialization
n- effects on local write attempts
- effects on future arrivals on this seat
- whether reversal is immediate, reviewed, or blocked by policy
- whether any older stronger rights artifacts remain and need retirement

The operator must be able to answer: **what stays local, what becomes inert, and how would I widen this seat later?**

### 5) Seat-narrowing receipt

This section should show:

- subject identity before/after
- seat posture before/after
- owner-domain continuity proof
- artifact rotation or retirement if any
- reversal conditions

The operator must be able to answer: **what later proves that I narrowed a seat, not that I disconnected and joined something else?**

## Public objects

### `linked_seat_narrowing_review`

Fields:

- `linked_seat_narrowing_review_id`
- `owner_domain_ref`
- `subject_ref`
- `seat_ref`
- `current_posture`
- `requested_posture`
- `subject_identity_continuity_class`
- `artifact_delta_summary`
- `dependent_effects[]`
- `generated_at`

### `linked_seat_posture_receipt`

Fields:

- `linked_seat_posture_receipt_id`
- `review_ref`
- `subject_ref`
- `seat_ref`
- `before_summary`
- `after_summary`
- `owner_domain_continuity_summary`
- `artifact_retirement_refs[]`
- `created_at`

## Main surface

A compact row should read like one of these:

- `seat narrowed inside same subject`
- `seat observe-only · subject identity preserved`
- `seat narrowing blocked · old broad artifact still active`
- `seat posture widened back by review`

## CLI shape

```text
anonsync seat posture review --seat tablet-citrine --subject photos --to observe
anonsync seat posture apply <review>
anonsync seat posture receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- narrowing one self-owned seat still requires disconnect-and-rejoin ritual
- subject identity changes just to express a weaker seat posture
- seat reversal later behaves like a fresh join instead of a posture widening
- the operator must infer from keys, path prompts, or new rows that this was really a self-seat rights edit

## Non-clone reason

Resilio's current docs still treat linked devices as one owner-like domain and then fall back to disconnect-plus-read-only-key ritual when one of those seats should become narrower.
AnonSync should instead make same-owner seat narrowing a first-class, in-place rights change with explicit continuity receipts.
''')

# fix accidental typo in doc 220
p = DOCS / '220-linked-seat-rights-narrowing-and-owner-domain-separation-interface-spec.md'
p.write_text(p.read_text().replace('\nn- effects on local write attempts', '\n- effects on local write attempts'))

# --- README ---
readme = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{timestamp}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `rev0138` and does twelve specific things:

1. Pushes the **Resilio Sync** evaluation further with current official evidence about discovery bootstrap dependence on a fetched tracker/relay catalog, proxy-driven egress-only asymmetry, destructive memory-pressure relief, and same-owner seat narrowing that still falls back to disconnect-plus-key ritual.
2. Sharpens the non-clone reason again: the remaining problem is not missing capability but too much operator-meaningful truth spread across remote bootstrap files, proxy caveats, out-of-memory advice, and owner-domain workarounds.
3. Adds a new **discovery bootstrap / catalog outage / fallback authority** interface spec so rendezvous/tracker knowledge becomes an explicit dependency record instead of support lore around one remote `sync.conf` file.
4. Adds a new **egress-only proxy / relay inevitability** interface spec so proxied seats publish their asymmetry and pairwise directness limits instead of looking like ordinary healthy nodes.
5. Adds a new **runtime memory pressure / subject budget / relief ladder** interface spec so memory crises stop collapsing into remove-and-readd ritual.
6. Adds a new **linked-seat rights narrowing / owner-domain separation** interface spec so one self-owned seat can become intentionally narrower without pretending it joined a different subject.
7. Refreshes the **Resilio evaluation** so the comparison now also covers tracker/relay bootstrap via `config.resilio.com/sync.conf`, proxy servers as outgoing-only transport, both-proxied peers becoming relay-only, and the current `Out of memory` remedy that deletes databases by removing and re-sharing subjects.
8. Refreshes the **product direction** so bootstrap authority, reachability asymmetry, memory-relief ordering, and same-owner seat posture become doctrine rather than troubleshooting folklore.
9. Refreshes the **roadmap** so the next tranche now explicitly includes discovery-bootstrap health, egress-only seat posture, memory-relief ladders, and in-place seat narrowing.
10. Refreshes the **source notes** so the official evidence set now explicitly includes `Peers aren't connecting`, `Cannot connect to trackers`, `Sync Preferences` proxy behavior, `Out of memory`, `User Management`, and `How to create a Read Only folder while syncing across linked devices?`.
11. Keeps the archive tight by extending existing discovery, route, rights, observer, repair, and work-ledger grammar instead of inventing unrelated subsystems.
12. Preserves the earlier service-world, path-class, declaration-branch, closure, power-cadence, transfer-ledger, shell-equivalence, repair-ladder, route, restore, naming, and topology decisions while giving them stronger bootstrap, asymmetry, memory-budget, and owner-domain companions.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The reason is sharper again and still evidence-based.
Current official docs still show a maintained Sync v3 line through `3.1.2.1076` in late 2025, practical linked-device and selective-materialization workflows, and a large body of operational guidance.
That is why Resilio remains worth studying rather than dismissing.

But the better non-clone reason is now this:

> Resilio still solves many real operator problems while leaving too much meaning about **who currently authorizes discovery infrastructure**, **which seats are only egress-capable and therefore relay-bound for some peers**, **which subjects are exhausting memory and what continuity would be lost by relieving them**, and **whether a weaker posture on one self-owned seat is really a rights change or a disguised rejoin** distributed across remote bootstrap files, proxy notes, out-of-memory advice, and read-only-key ritual where AnonSync wants one bootstrap-authority receipt, one reachability-asymmetry contract, one memory-relief ladder, and one in-place seat-posture receipt.

That stronger conclusion is what this revision tries to preserve.

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/217-discovery-bootstrap-catalog-outage-and-fallback-authority-interface-spec.md`
4. `docs/218-egress-only-proxy-and-relay-inevitability-interface-spec.md`
5. `docs/219-runtime-memory-pressure-subject-budget-and-relief-interface-spec.md`
6. `docs/220-linked-seat-rights-narrowing-and-owner-domain-separation-interface-spec.md`
7. `docs/213-service-promotion-migrate-clean-and-principal-continuity-interface-spec.md`
8. `docs/214-remote-volume-path-class-and-notification-confidence-interface-spec.md`
9. `docs/215-declared-config-subject-set-and-interactive-control-boundary-interface-spec.md`
10. `docs/216-uninstall-offboard-peer-tombstone-and-hidden-residue-attestation-interface-spec.md`
11. `docs/170-topology-aware-rights-editor-and-propagation-ceiling-interface-spec.md`
12. `docs/89-observer-readonly-local-write-and-serve-rights-spec.md`
13. `docs/62-discovery-publication-and-identity-disclosure-spec.md`
14. `docs/36-route-exposure-known-host-and-lease-spec.md`
15. `docs/38-operator-workbench-interface-spec.md`
16. `docs/39-interface-pattern-language.md`
17. `docs/30-interface-spec.md`

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and interface doctrine
- `docs/217-discovery-bootstrap-catalog-outage-and-fallback-authority-interface-spec.md` — reviewed bootstrap-authority contract for fetched catalogs, stale endpoint knowledge, and bounded fallback envelopes
- `docs/218-egress-only-proxy-and-relay-inevitability-interface-spec.md` — reviewed reachability-asymmetry contract for outbound-only proxy posture and pairwise relay inevitability
- `docs/219-runtime-memory-pressure-subject-budget-and-relief-interface-spec.md` — reviewed resource-relief contract for per-subject memory budgets, ordered relief steps, and continuity cost
- `docs/220-linked-seat-rights-narrowing-and-owner-domain-separation-interface-spec.md` — reviewed same-owner seat-posture contract for in-place narrowing without subject replacement ritual
- `docs/50-roadmap.md` — near-term phases and exit criteria
- `docs/sources.md` — current external source notes for this revision
'''
(ROOT / 'README.md').write_text(readme)

# --- 00-status ---
status = f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0138`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based, current, and specific not only about service-world continuity, path-class truth, declaration authority, and closure receipts, but now also about **discovery bootstrap authority**, **proxy-driven reachability asymmetry**, **memory-pressure relief**, and **same-owner seat narrowing**
- spend more time on **interface specs**, especially where current sync products still ask the operator to infer discovery dependency, egress-only posture, destructive relief cost, or self-seat rights narrowing from remote config fetches, proxy notes, resource warnings, and manual key rituals
- preserve the shell/workspace, route, disclosure, repair, rights, and service-world decisions already made unless fresh evidence actually breaks them
- make a better explicit case for why AnonSync should not inherit Resilio's catalog-bootstrap opacity, proxied-seat asymmetry opacity, memory-relief destructiveness, or self-device read-only workaround model

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: {rev}
- Timestamp: {timestamp} America/New_York
- Codename: {codename}

- a further-tightened **Resilio evaluation** that now treats discovery bootstrap, egress-only proxy posture, out-of-memory relief, and same-owner seat narrowing as additional non-clone reasons
- a new **discovery bootstrap / catalog outage / fallback authority** interface spec so rendezvous/tracker knowledge becomes an explicit dependency record instead of support lore around one remote file
- a new **egress-only proxy / relay inevitability** interface spec so proxied seats publish pairwise directness limits instead of looking like ordinary healthy nodes
- a new **runtime memory pressure / subject budget / relief ladder** interface spec so memory crises stop collapsing into subject deletion and re-add ritual
- a new **linked-seat rights narrowing / owner-domain separation** interface spec so one self-owned seat can become intentionally narrower without pretending it joined a different subject
- updated top-level docs so the archive now makes firmer choices about bootstrap authority, reachability asymmetry, memory-relief ordering, and in-place seat-posture receipts

## The main shift

`rev0139` closes the next seam:

> it is not enough to have strong route, disclosure, repair, and rights language if the operator still has to reconstruct **who currently authorizes discovery infrastructure**, **which seats can only dial out and therefore force relay for some peers**, **which subjects are exhausting memory and what continuity would be sacrificed to relieve them**, and **whether a weaker posture on one self-owned seat is really a rights edit or a disguised rejoin** from remote `sync.conf` dependencies, proxy notes, out-of-memory advice, and read-only-key rituals.

That changes the archive in eight specific ways:

- discovery bootstrap is now a first-class authority object with freshness, failure class, fallback envelope, and receipts
- proxied seats now publish direct-capable versus egress-only posture instead of hiding asymmetry behind generic connectivity status
- pairwise route explanations can now say when relay is inevitable rather than merely observed
- memory pressure now compiles into one per-subject budget ledger instead of generic distress
- relief planning now orders reversible and destructive steps with explicit continuity cost
- same-owner seat narrowing now preserves subject identity and owner-domain continuity explicitly
- wider and narrower self-seat postures can now reverse as posture changes rather than as full rejoins
- new receipts can now prove bootstrap changes, reachability asymmetry, memory-relief cost, and self-seat posture changes directly

## Files added in this revision

- `docs/217-discovery-bootstrap-catalog-outage-and-fallback-authority-interface-spec.md`
- `docs/218-egress-only-proxy-and-relay-inevitability-interface-spec.md`
- `docs/219-runtime-memory-pressure-subject-budget-and-relief-interface-spec.md`
- `docs/220-linked-seat-rights-narrowing-and-owner-domain-separation-interface-spec.md`
- `update_rev0139.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/20-product-direction.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## The current stance in one paragraph

Resilio remains worth studying because current official docs still show a maintained Sync v3 line, practical linked-device and selective-materialization workflows, and extensive operational guidance.
But those same docs still show discovery bootstrap meaning hidden across a fetched `sync.conf` catalog and tracker troubleshooting, proxied-seat directness hidden across one outgoing-only preference line, memory relief hidden across remove-and-readd advice that deletes databases, and self-seat narrowing hidden across disconnect-plus-read-only-key ritual.
That is enough reason for AnonSync to prefer one bootstrap-authority receipt, one reachability-asymmetry contract, one memory-relief ladder, and one in-place seat-posture receipt instead of cloning Resilio's support-lore-driven contract.
'''
(DOCS / '00-status.md').write_text(status)

# --- append evaluation/product/roadmap/sources addenda ---
eval_addendum = '''

## Revision addendum — bootstrap authority, egress asymmetry, memory pressure, and self-seat narrowing

This pass found another current Resilio cluster worth treating as a first-class non-clone reason.
The strongest new seams are no longer only about service worlds, closure, or restore ritual.
They are now also about how a modern sync product explains **who authorizes discovery infrastructure**, **which seats are only outbound-capable**, **what resource relief discards continuity**, and **how one self-owned seat becomes intentionally narrower**.

## AZ. Discovery bootstrap still depends on a fetched catalog instead of one rendered authority object

Current official Resilio docs still say peers may fail before tracker matching even begins because Sync cannot reach `https://config.resilio.com/sync.conf`, the file from which it learns tracker and relay addresses. The current troubleshooting path still starts by checking that URL in a browser or with `wget`, and a separate tracker article still distinguishes `cannot get the list of trackers` from failing to reach the trackers themselves.

That is practical. It is still not a good bootstrap contract. `Cannot connect` is not one truth if the node does not yet know where rendezvous infrastructure lives, knows but cannot fetch fresh definitions, or knows enough cached state to limp along for existing peers only.

AnonSync should therefore keep another stronger rule:

- discovery bootstrap authority must be a first-class rendered object
- catalog freshness and endpoint-authority failure must be distinct from ordinary route failure
- fallback envelope after bootstrap loss must be visible and receipt-bearing

## BA. Proxy posture still changes directness asymmetrically without one reachability contract

Current official Resilio docs still say proxy servers prohibit incoming connections and allow only outgoing ones, which means two peers both behind a proxy will be able to talk only via relay, while only one proxied peer can still connect directly to an unproxied counterpart. Connectivity troubleshooting still treats `using proxy` as one line in a wider connection checklist.

That is useful. It is still not a good route contract. A proxied seat is not just `online with extra latency`; it is often a fundamentally different reachability class whose pairwise behavior changes by peer topology.

AnonSync should therefore keep another stronger rule:

- egress-only posture must be rendered as a first-class seat property
- pairwise route explain must say when relay is inevitable, not merely observed
- direct-capable and egress-only seats must never share the same health language

## BB. Memory relief still falls too quickly into remove-and-readd ritual

Current official Resilio docs still say that to use less RAM the only way is to remove the biggest folders from Sync from all peers and share the folder again, which deletes the database and later rebuilds it on re-add and re-index.

This is practical support advice. It is still not a good resource-relief contract. Memory pressure is a runtime budget incident, not proof that the subject itself should be discarded and recreated.

AnonSync should therefore keep another stronger rule:

- memory pressure must identify top contributing subjects explicitly
- reversible relief must be shown before destructive relief
- destructive relief must publish continuity cost in the same review as the proposed memory gain

## BC. Linked-device narrowing still falls back to disconnect-plus-key ritual

Current official Resilio docs still say all linked devices under one identity act as Owners, while a separate help page for creating a read-only linked device still tells the operator to use a Standard folder with a Read Only key, disconnect the already connected folder on the target seat, and then re-enter the key manually at `+ -> Enter a key or link`.

That is exactly the kind of seat-posture story AnonSync should not clone. A weaker posture on one self-owned seat should not require a new artifact family and a gesture that looks indistinguishable from leaving one subject and joining another.

AnonSync should therefore keep another stronger rule:

- same-owner seat narrowing must preserve subject identity explicitly
- posture narrowing and posture widening must behave like rights edits, not rejoins
- any artifact retirement involved in self-seat narrowing must be secondary to one stable subject row and one receipt

## The interface consequences for AnonSync in this revision

This pass adds four more direct interface consequences:

### 37) Discovery bootstrap needs one authority and fallback surface

Because current docs still rely on a fetched `sync.conf` catalog and browser-side reachability checks to explain tracker/relay authority, AnonSync now requires one bootstrap-authority surface that publishes source class, freshness, failure class, and reduced connectivity envelope.

### 38) Proxied seats need one reachability-asymmetry surface

Because current docs still hide outgoing-only proxy semantics behind one preference line and later troubleshooting prose, AnonSync now requires one seat-posture surface that says whether inbound/direct paths still exist and for which peer pairings relay is inevitable.

### 39) Memory pressure needs one subject-budget relief ladder

Because current docs still route RAM relief through subject removal and re-share ritual, AnonSync now requires one memory-pressure surface that ranks top subject contributions and orders reversible relief before destructive reset.

### 40) Self-owned seat narrowing needs one in-place posture review

Because current docs still require disconnect-plus-read-only-key ritual to make one linked seat narrower, AnonSync now requires one seat-posture review that preserves subject identity and owner-domain continuity while narrowing one seat.
'''
(DOCS / '10-resilio-sync-evaluation.md').write_text((DOCS / '10-resilio-sync-evaluation.md').read_text() + eval_addendum)

product_addendum = '''

## Revision addendum — doctrine after rev0139

The next doctrinal hardening after this pass is now clearer:

1. discovery bootstrap is not implementation scaffolding; it is an operator-visible authority chain with freshness, fallback, and receipts
2. egress-only seats are not merely slower seats; they are a separate reachability class that must change pairwise route expectations explicitly
3. runtime memory pressure is not permission to discard subject continuity casually; it must route through one ordered relief ladder
4. weaker posture on one self-owned seat is still one subject inside one owner-domain and should therefore behave like an in-place rights edit, not a disguised rejoin
'''
(DOCS / '20-product-direction.md').write_text((DOCS / '20-product-direction.md').read_text() + product_addendum)

roadmap_addendum = '''

## Revision addendum — next tranche after rev0139

Add to Phase 0 deliverables:

- explicit discovery-bootstrap authority / freshness / fallback-envelope surfaces
- explicit egress-only seat / pairwise relay-inevitability / directness-asymmetry surfaces
- explicit memory-pressure / top-subject-budget / ordered-relief-ladder surfaces
- explicit same-owner seat-posture / subject-identity-preserving narrowing surfaces

Add to Phase 0 exit criteria:

- operators can tell whether discovery failure is catalog-authority loss, tracker reachability loss, or ordinary peer-path failure
- operators can tell which seats are egress-only and for which peer pairings relay is inevitable
- operators can relieve memory pressure without guessing which continuity proofs or indexes would be discarded
- operators can narrow one self-owned seat without creating a second disguised subject or relying on rejoin ritual
'''
(DOCS / '50-roadmap.md').write_text((DOCS / '50-roadmap.md').read_text() + roadmap_addendum)

sources_addendum = '''

## Revision addendum — bootstrap authority, proxy asymmetry, memory relief, and self-seat narrowing

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier service, route, and restore passes.
The new questions were:

> where do current official docs prove that **discovery bootstrap authority** still lives in a fetched remote catalog and support-page reachability checks rather than one rendered dependency object?

> where do current docs show that **proxy posture** still changes directness asymmetrically and can make relay inevitable for some peer pairs?

> what current evidence most clearly shows that **memory relief** still broadens too quickly into remove-and-readd ritual with database loss?

> how do current docs prove that **narrowing one linked self-owned seat** still falls back to disconnect-plus-read-only-key ritual instead of one in-place rights edit?

The most load-bearing source set for this pass was the maintained v3 line together with docs on tracker/bootstrap failures, proxy behavior in preferences, linked-device ownership, read-only creation across linked devices, and out-of-memory guidance.

### Additional Resilio official sources emphasized in rev0139

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Cannot connect to trackers  
  https://help.resilio.com/hc/en-us/articles/210587126-Cannot-connect-to-trackers

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Out of memory  
  https://help.resilio.com/hc/en-us/articles/209724663-Out-of-memory

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices
'''
(DOCS / 'sources.md').write_text((DOCS / 'sources.md').read_text() + sources_addendum)

# update script record inside repo
(ROOT / 'update_rev0139.py').write_text(Path('/mnt/data/anonsync_work/update_rev0139.py').read_text())
