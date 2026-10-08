# Roadmap

## Phase 0 — narrow the core

Deliver:

- daemon skeleton
- local identity creation
- share/index model
- local status, event stream, and audit surface
- CLI contract draft
- daemon API contract draft
- canonical interface flows
- recovery object model
- plan/apply object model
- incoming/adoption object model
- capability introspection surface
- ignore/conflict object model
- role/preflight object model
- claim object model
- offer-artifact and claim-receipt object model
- recovery-bundle object model
- recovery-posture and recovery-receipt object model
- approval-memory object model
- local-presence-posture, arrival-default-policy, and presence-receipt object model
- placement-suggestion, placement-review, and placement-receipt object model
- path-comparison and relocate object model
- topology-exposure object model
- publication-profile, known-host-record, and route-lease object model
- contact-record, pending-peer, and introduction-policy object model
- decision-trace object model
- retirement-record object model
- filesystem-profile and filesystem-compatibility-report object model
- projection-policy object model
- projection-effect-report and projection-receipt object model
- convergence-report object model
- settlement-policy, settlement-barrier, and settlement-receipt object model
- history-entry, restore-candidate, and rollback-receipt object model
- portability-policy, fidelity-contract, fidelity-drift-case, and fidelity-receipt object model
- review-item object model
- transport-runtime object model
- transport-session object model
- transfer-policy, throughput-budget, transfer-explanation, and transfer-budget-receipt object model
- attention-policy, attention-event, and attention-receipt object model
- defaults-profile, policy-binding, effective-policy, and policy-receipt object model
- override-lease, override-receipt, and lease-conflict-report object model
- diagnostic-incident, evidence-bundle, redaction-profile, and evidence-receipt object model
- control-access-policy, control-endpoint, access-token, control-session, and access-receipt object model
- compromise-case and compromise-receipt object model
- reentry-case and reentry-receipt object model
- state-root, state-snapshot, service-profile, and state-transition-plan object model
- execution-seat, seat-switch-review, and seat-switch-receipt object model
- subject-alias-record, identity-continuity-review, and identity-label-receipt object model
- semantic-runtime-contract, semantic-optimization-review, and semantic-optimization-receipt object model
- retained-replica-posture, replica-recall-review, and replica-recall-receipt object model
- share-authority-epoch, epoch-rotation-review, and epoch-rotation-receipt object model
- observer-posture-contract, observer-rights-review, and observer-rights-receipt object model
- share-layout-contract, share-layout-review, and layout-receipt object model
- target-custody-record, binding-collision-case, and custody-receipt object model
- binding-receipt and preservation-set object model
- deviation-case and file-intent-receipt object model
- activity-phase-state and schedule-window object model
- Linux-first filesystem support-tier model
- critical-open-questions discipline

Exit criteria:

- objects and state model feel stable
- command names survive scrutiny
- event taxonomy is good enough for future UI/TUI work
- high-signal mutations can be previewed without inventing hidden side effects
- same-host path claims have a clear custody/lineage/collision story before bind or cleanup
- the interface pattern language is explicit enough that GUI, TUI, and CLI projections do not drift into different products
- proof-bearing findings share one common report language instead of dissolving into badges and special-case dialogs
- rollback and conflict resolution are auditable without hidden archive browsing or filename ritual
- filesystem semantics remain explicit after bind instead of collapsing back into stale preflight warnings or support lore
- operators can tell which report-backed conditions are merely visible in the workbench, which were delivered via external channels, and what acknowledgement changed only presentation versus real state
- operators can tell who or what can currently control the daemon, through which endpoint, and what receipt proved any exposure or revocation change
- operators can tell when a requested optimization or compatibility change would actually weaken freshness, rename continuity, diff behavior, or verification guarantees
- operators can tell which peers still retain bytes, whether those bytes still matter for recovery, and what stronger recall claim is or is not currently proven
- operators can tell which authority generation is current for a share, what older capability residue still remains, and whether the strongest honest statement is mixed-epoch migration or observed clean convergence
- operators can tell what `observer` or `read only` means for bytes, local writes, onward serving, and projection limits instead of inferring it from one mode label
- operators can tell the current share posture on one seat apart from that seat's future-arrival defaults instead of treating both as one `mode`
- operators can tell which bytes in a mounted tree are ordinary data, which are managed sync state, and what receipt proved any migration or cleanup of that boundary
- operators can tell which incident is being investigated, which evidence classes were collected, what redaction posture was applied, and what proof exists for bundle seal/export/destruction

## Phase 1 — trusted plaintext sync

This phase should already produce a minimal operator workbench, not just a daemon plus commands.
At minimum:

- high-signal status/home surface
- share detail with visibility vs mount distinction
- peer/detail trust view
- review queue for pending peers, incoming shares, and blocked actions
- proof drawers / explanation panels that keep risky actions attached to evidence
- a cross-surface report shelf / report-detail grammar for guarded, blocked, or stale decisions
- an Attention surface that makes lane placement, delivery channels, and acknowledgement posture explicit
- a Diagnostics surface that makes incidents, evidence bundles, redaction posture, and bundle custody explicit
- an Access surface that makes control endpoints, sessions, and reviewed exposure posture explicit
- a System State surface that makes active root and runtime profile explicit


Deliver:

- device add/link
- share create/grant
- full replication
- send-only / receive-only behavior
- explicit deviation-policy object and deviation-aware status/explain surfaces
- useful `status`, `doctor`, and `audit`
- named discovery / topology policies
- Tor/I2P-aware mixed transport policies with manual clearnet-direct lease semantics
- exposure-preview and effective-route-exposure surfaces
- peer-pinned known-host direct admission without ambient public-direct enablement
- byte-capped direct-speed leases for trusted bulk windows
- bundled transport provenance/verification surfaces
- explicit transport-session inspection surfaces
- basic provenance on policy and grant creation
- incoming-share visibility and adopt/reject flow
- reviewed seat-level future-arrival policy surface
- ignore-rule and drift surface
- projection-policy and projection-test surface
- compatibility warnings and least-privilege role application for link/grant/adopt flows
- explicit claim handling for invite and incoming-share acceptance
- explicit offer create/inspect/revoke/reissue surfaces that keep delivery encoding separate from authority semantics
- explicit transfer explain / policy / budget / receipt surfaces that keep route permission, route preference, and throughput budget separate
- explicit disclosure profile / report / residue / receipt surfaces that keep publication audience, fact classes, mechanism, and residue truth separate from route success
- explicit access inspect / expose-plan / token / session / receipt surfaces that keep endpoint exposure, credential issuance, and session authority separate
- explicit control-capability / control-integrity / auth-repair surfaces that keep browser quirks, trust bootstrap, and credential repair from becoming hidden semantics
- explicit channel-parity / review-handoff surfaces that keep GUI, WebUI, CLI, TUI, and API-backed control from becoming different products
- explicit mutation-gate / short-lived mutation-grant / elevation-receipt surfaces that keep inspect sessions separate from dangerous apply authority
- explicit semantic-runtime / optimization / fallback surfaces that keep meaning-changing acceleration or degraded-target acceptance from hiding behind `performance` language
- explicit retained-replica / recall / attestation surfaces that keep future authority stop, retained-copy truth, encrypted-backup usefulness, and stronger delete/recall claims visibly separate
- explicit authority-epoch / rotation / stale-capability surfaces that keep newly issued share authority, old capability residue, derivative/local-share migration, and convergence truth visibly separate
- explicit observer / read-only / local-write / serve-rights surfaces that keep byte visibility, local-write consequences, onward serving, and share-class/projection limits visibly separate
- explicit share-layout / annex / residue / cleanup surfaces that keep ordinary data trees separate from rollback, metadata-carry, and temp-transfer machinery
- explicit diagnostic incident / depth / evidence bundle / redaction / receipt surfaces that keep troubleshooting scope, debug depth, and export history separate
- explicit device-retire / ignore / revoke surfaces
- explicit grant-mutation / access-narrow / delegation-strip review surfaces
- explicit compromise open / freeze / revoke / rotate / successor-review surfaces
- explicit re-entry open / resume / quarantine / escalate surfaces for long-offline or chronology-uncertain return
- workbench `Exits & Replacement` page with fixed stop/stay/residue/follow-up review grammar
- scoped approval-memory and delegated-approver surfaces
- explicit pending-peer and contact-review surfaces
- fixed intake review-model surfaces for claims, offers, and incoming adoption so workbench and CLI render the same way-in truth
- fixed constellation-join review-model surfaces so workbench and CLI render the same identity/authority blast-radius truth before device add
- fixed approval-seat review-model surfaces so workbench and CLI render the same acting-seat / current-only-versus-future approval truth before a request is accepted
- fixed standing-approval match review-model surfaces so workbench and CLI render the same prior-trust / local-claim boundary before a later arrival becomes live here
- fixed re-entry review-model surfaces so workbench and CLI render the same dormancy/chronology/authority truth before stale return is trusted again
- bounded introduction-policy surfaces for trusted constellations
- stewardship records and handoff previews for trusted shares
- compare-before-bind and relocate-plan surfaces for populated-path adoption
- override-lease and effective-state surfaces for maintenance, drain, and temporary throttling
- filesystem preflight / explain / doctor surfaces for pathname and metadata safety
- filesystem support-tier inspection surfaces
- convergence-report and wait-for-settlement surfaces for cutover / backup / relocate readiness
- intent-aware settlement policy/barrier/receipt surfaces for proving and auditing high-signal actions
- inspect/verify/export/attach/move/switch surfaces for active state root and runtime profile
- inspect/detach/repair/preservation surfaces for local mount continuity
- inspect/preview/receipt surfaces for scope-sensitive file actions and deviation resolution
- inspect provenance/retention/receipt surfaces for file history, rollback, and conflict resolution
- inspect portability/fidelity contract, drift, and receipt surfaces for long-lived mounts
- inspect/schedule/effective-state surfaces for runtime activity control and recurring windows
- inspect/preview/receipt surfaces for namespace projection tightening and local-view cleanup
- inspect/compare/receipt surfaces for personal-constellation membership, member class, and authority-domain scope
- inspect/relabel/alias/continuity surfaces for subject naming versus authority identity
- inspect/reconcile/receipt surfaces for non-empty-target adoption, same-path divergence, and encrypted-target mismatch

Exit criteria:

- personal two-device workflow is reliable
- failures are debuggable from CLI alone
- LAN-only and trusted-WAN policies both work cleanly
- overlay-first WAN policies work cleanly without silent clearnet-direct fallback
- operators can see the difference between warm transport runtimes and active transport sessions
- operators can tell which profile or plan created the current defaults
- operators can answer what a policy publishes about reachability and whether fallback would widen metadata exposure
- operators can admit one trusted direct path without silently enabling public direct for everything else
- operators can see when a temporary speed window will expire by time or by byte budget
- operators can explain why a chosen route or approval outcome won without leaving the CLI
- operators can inspect what a portable artifact actually offers before sending or consuming it, and can later prove consumption from claim receipts
- operators can rotate or upgrade share authority without guessing whether old capability material still exists or whether the swarm actually converged to the new boundary
- operators can safely adopt into a pre-populated directory without guessing what will win
- operators can tell whether a non-empty target means same-lineage reuse, harmless merge, same-path divergence, or encrypted-target mismatch before apply
- operators can tell whether current behavior comes from durable policy or a temporary override lease, and when that lease expires
- operators can tell why a transfer is relay/direct/overlay, capped/uncapped, queued/suspended, and which policy or budget caused that outcome
- operators can tell what a route/discovery change publishes, to which audience, and whether narrowing leaves residue that still needs time or explicit clearance
- operators can tell which values are inheriting, which are pinned, which are temporarily overridden, and what a defaults/profile change would actually touch before apply
- operators can tell what “paused”, “draining”, or “metered” actually means in phase terms, including LAN-vs-Internet scope
- operators can tell when a long-offline or clock-uncertain subject is safe to resume, safe only to resume read-only, or must be quarantined/escalated before writable replay is trusted
- a small-team share can be handed off to a successor without re-sharing the whole dataset or widening everyone into owner-equivalent authority
- operators can distinguish ordinary idle status from settlement confidence degraded by missing sources, watcher fallback, clock skew, or hidden background work
- operators can move between share, peer, review, and report surfaces without relearning verb meanings or proof semantics
- operators can preview the same exit or replacement truth in workbench and CLI without semantic drift
- operators can preview the same claim/adoption truth in workbench and CLI without semantic drift
- operators can preview the same constellation-join truth in workbench and CLI without semantic drift
- operators can preview the same compromise-containment truth in workbench and CLI without semantic drift
- Linux/web workbench users do not lose safety-critical destructive-action or trust-review guardrails relative to richer projections
- operators can always tell which state root and service profile they are operating before taking high-signal actions
- operators can repair a moved or missing path without falling back to remove/re-add ritual when continuity is still provable
- operators can tell whether a file action was local-only, replicated, restorative, or deviation-resolving without reconstructing meaning from mode-specific behavior
- operators can tell whether a projection change affected peer namespace, local mount view, future announcement only, or local byte retention, and can prove it later from receipts
- operators can tell whether a high-signal action used strict or guarded readiness proof, and that answer is recoverable later from settlement receipts
- operators can inspect restore and conflict-resolution provenance without relying on hidden archive layout, short-lived activity views, or magic suffix filenames
- operators can tell what pathname, metadata, notification, and support-tier semantics a mount is actually operating under, and whether later drift has weakened that contract
- operators can tell whether control access is local-only, tunnel-reviewed, proxy-reviewed, or directly exposed, and can revoke stale sessions without resorting to config or browser folklore
- operators can diagnose a missing browser/workbench action as policy denial versus client degradation, and can repair access without deleting unrelated settings or relying on browser override ritual
- operators can tell whether a target release is merely newer or actually safe for the current daemon, runtime, and peer constellation, and can prove later what compatibility boundary they accepted at cutover time
- operators can collect reviewed evidence for a live incident without relying on hidden storage paths, sticky debug mode, or support-form ritual
- operators can keep a personal mesh convenient while still proving which members are writable, approval-capable, incoming-only, or appliance-like without ambient owner semantics
- operators can change a live member's access without falling back to folder-class switches, disconnect ritual, or remove/re-share folklore, and can prove later what authority boundary changed
- operators can fix a device or peer label without silently rotating authority, and can tell when a familiar name is actually a new trusted subject with different blast radius
- operators can tell whether a so-called read-only or observer replica really means names only, placeholders, full bytes, local-write suspension, auto-revert, or serve-clean-bytes-only without support-lore reconstruction
- operators can tell whether a visible or placeholder-backed path is actually fetchable now, backed only by this local copy, backed only by offline/guarded witnesses, or no longer honestly retrievable at all
- operators can read the same five-part availability answer in workbench and CLI without semantic drift or optimistic bulk flattening
- operators can tell when a path moved from swarm fetch into history restore, and the product changes its verb accordingly
- operators can tell when prior trust matched a new arrival, what that match actually authorized, and whether any later local bind/materialization still needs separate receipts

## Phase 2 — selective materialization

Deliver:

- detached/selective/full mount modes
- metadata-only index view
- explicit fetch/evict/pin commands
- explicit local-vs-share removal scopes
- preservation-report surface for risky file actions
- file-history listing and local/share restore surface
- conflict listing and safe resolution surface
- transfer explanations
- capability-aware placeholder strategy selection
- explicit fetchability/full-copy-witness inspection and receipts
- concrete file-availability answer strips, subtree tables, and mixed-risk batch splitting rules
- explicit availability row/action contracts so clients can render exact next-safe-action labels without inventing them locally
- explicit availability row anatomy and review-pane contract so dense tables, mobile cards, and CLI rows keep state/source/action adjacent and gate direct actions by risk class
- explicit announcement-inbox / local-claim contract so newly visible shares can stay pathless, local hide stays distinct from wider withdraw, and remembered defaults do not silently create local binds
- explicit approval-seat / horizon contract so pending requests show which reviewed member is speaking, whether the outcome is one-subject-only or future-reaching, and what narrower safer alternative exists
- explicit standing-approval / matched-arrival guardrail contract so remembered approval can recognize later arrivals without silently turning them into connected local paths
- explicit standing arrival-template / default-root governance contract so seat-level convenience remains reviewable policy rather than scattered mode/default/simple-mode behavior
- explicit standing-policy delta preview / arrival-simulation contract so future-only changes, draft refresh, and hard non-effects become reviewable before apply
- explicit standing-policy lineage / subject-attribution contract so current policy, applied older policy, grandfathering truth, and version compare remain inspectable after later edits
- explicit subject-policy drift / realignment contract so live non-current subjects classify into refresh-eligible, subset-review, grandfathered, or pinned-exception outcomes with reviewed receipts
- explicit intentional-exception aging / renewal contract so long-lived divergence carries review horizons, due-soon/overdue state, and separate reviewed outcomes for renewal, no-expiry acknowledgement, or return to current policy
- explicit remembered-approval freshness / cooling contract so long-lived trust memory carries visible freshness classes, cooling reasons, and separate reviewed outcomes for touch renewal, narrowing, freezing, fresh-next-time, or revocation
- per-device role outcomes that remain legible after selective-materialization adoption
- explicit mount-relocate workflows with compared path binding
- explicit fs-compatibility reports for adopt / relocate / restore workflows
- explicit fidelity contracts and drift detection for long-lived mounts
- review-model projection for destructive replay and delete-wave plans so rich and textual clients render the same danger sections
- review-model projection for conflict adjudication and path-collision resolution so rich and textual clients render the same candidate/loser-handling sections
- review-model projection for same-host local derivation so rich and textual clients render the same topology/lifecycle/target-tier sections
- review-model projection for authority mutation and grant-boundary changes so rich and textual clients render the same current-authority/boundary-delta/dependent-fallout sections
- review-model projection for overlap, containment, and graph topology so rich and textual clients render the same graph-subject/propagation/root-boundary sections
- review-model projection for writer contention and quiescence so rich and textual clients render the same contested-scope/writer-reality/notification-posture/quiesce-effect sections
- review-model projection for capacity fit and scale admission so rich and textual clients render the same subject-role/local-capacity/freshness-posture/path-blocker sections

Exit criteria:

- users can keep large shares visible without replicating everything
- selective mode is operationally legible
- unsupported placeholder strategies fail or degrade explicitly
- operators can always tell whether an action affected local materialization or shared state
- operators can always tell whether a share is merely visible here, already claimed here, bound here, hidden here only, or withdrawn more widely
- operators can always tell what one seat will do with the next matching arrival, whether old drafts were refreshed, and which currently bound shares stayed untouched when standing defaults changed
- operators can preview a standing-policy edit and see effect buckets, named example subjects, and explicit non-effects before any durable mutation is applied
- operators can tell which standing-policy version handled a visible draft, match, or arrival and whether it still matches current policy or is grandfathered
- operators can tell which current subjects now differ from the current standing policy, which differences are intentional, and which are actually safe to realign now
- operators can tell which intentional non-current subjects are still healthy, which are due soon or overdue for re-review, and what definitely will not happen automatically when their review horizon is reached
- operators can tell which exact remembered-trust node authorized a later low-friction arrival, which later trust mutation superseded it, and whether the same subject would still match under today's head
- operators can tell when a changed linked-device constellation forced old remembered approval to split, cool, freeze for descendants, or require fresh approval, and can review that outcome without losing historical explanation
- operators can tell whether a descendant that still belongs to remembered trust is actually live enough to count as a byte source or approval-capable seat now, or whether it is only hidden, stale, reappeared-awaiting-proof, historical only, or unknown
- operators can tell when remembered approval still exists but one governed subject still requires fresh approval because subject-level reuse policy is stricter, and can see which rule won before any action is taken
- operators can tell whether a consumed or expired invitation merely admitted one subject or also created durable remembered approval for later reuse, and can prove which outcome actually survived
- operators can see whether a destructive action still leaves any plaintext or history-backed rollback path
- operators can restore an earlier copy without hunting hidden archive directories
- operators can tell whether a path is suppressed share-wide, omitted locally, or still visible as placeholder/metadata-only state
- operators can tighten projection after indexing without pretending prior peer visibility never existed
- operators can resolve conflicts, deviation state, and rule drift without editing hidden control files
- operators can relocate a mount or rebind a path without falling back to remove/re-add folklore
- operators can see case, normalization, symlink, and metadata-fidelity risk before binding a share onto a real path
- operators can verify later that the adopted mount is still honoring the same filesystem-fidelity contract it accepted originally
- operators can preview the same destructive-replay truth in workbench and CLI without semantic drift
- operators can preview the same conflict-adjudication truth in workbench and CLI without semantic drift
- operators can preview the same same-host-derivation truth in workbench and CLI without semantic drift
- operators can preview the same contention/quiesce truth in workbench and CLI without semantic drift
- operators can preview the same authority-mutation truth in workbench and CLI without semantic drift
- operators can tell whether a contested path is just burst-save delay, active lock pressure, rescan-only freshness, or a reason to freeze propagation before sync continues
- operators can preview the same topology-review truth in workbench and CLI without semantic drift
- operators can preview the same capacity-fit truth in workbench and CLI without semantic drift
- operators can tell before adopting or rebinding a large subject whether the current host is comfortable, guarded, or blocked by RAM, watcher ceilings, indexing cost, storage headroom, or path blockers

## Phase 3 — encrypted-untrusted replicas

Deliver:

- arrival-explanation and counterfactual surfaces for incoming/matched/claimed/bound subjects
- encrypted-replica permission
- ciphertext-only peer behavior
- trusted-peer recovery via encrypted intermediary
- diagnostics for plaintext availability
- polished Tor/I2P transport health, session reuse, and bootstrap ergonomics on Linux

Exit criteria:

- operators can ask `why is this share here now?` and get one truthful causal answer without state archaeology
- “store on untrusted node, recover from trusted node” works cleanly

## Phase 4 — recovery and replacement workflows

Deliver:

- backup/export/import
- replacement-device onboarding
- identity rotation and revocation
- trust-graph reconciliation tooling
- policy provenance for auto-grants
- reviewed plan/apply for replacement and rebind work
- offline encrypted-replica recovery tooling
- recovery-bundle export and verification
- custody-grade recovery page with invalidation and continuity receipts
- successor-binding and retirement-record workflows
- explicit state-root relocation and profile-switch workflows with receipts
- reclaim plans and receipts that keep local space recovery distinct from replicated delete semantics
- exit plans and residue receipts that keep hide/revoke/decommission/erase semantics explicit across device, share, and daemon exits
- review-model projection for exit plans so rich and textual clients render the same safety-critical sections
- review-model projection for successor cutover and state re-home so rich and textual clients render the same continuity sections
- review-model projection for compromise containment and trust rotation so rich and textual clients render the same incident sections
- review-model projection for bring-up and first control entry so rich and textual clients render the same continuity and exposure sections
- review-model projection for execution-seat and runtime-profile switching so rich and textual clients render the same continuity, reachability, and freshness sections
- review-model projection for subject-label and authority-identity continuity so rich and textual clients render the same label, fingerprint, fallout, and receipt-promise sections

Exit criteria:

- operators no longer need unsupported clone-style workarounds
- operators can decommission a node or retire a replica without confusing cosmetic cleanup, authority revocation, remote residue, and preserved continuity
- Linux-first operators do not lose exit-review fidelity when they move from richer local workbench surfaces to SSH/CLI operation
- dead-device replacement is explicit and understandable
- operators can preview the same successor-cutover truth in workbench and CLI without semantic drift
- stolen-device retirement is visibly different from mere list cleanup
- suspicion, immediate freeze, revocation, rotation, and successor continuity remain visibly different under one incident-grade contract
- linked-device convenience remains auditable after recovery events
- successor carry-forward of grants and approvals remains reviewable rather than ambient
- route, exposure, and metrics surfaces are good enough for local dashboards and troubleshooting
- operators can tell whether first open is fresh, attached, recovered, successor-sensitive, or blocked without inferring it from startup flags or installer folklore
- operators can tell whether switching runtime principal or service seat preserves the same state world, target reachability, and freshness guarantees or instead requires reviewed rebind or clean-seat start
- operators can tell whether a same-person rename/replacement request is cosmetic relabeling, alias history, successor continuity, or real authority replacement before any trust shortcuts are inherited

## Phase 5 — optional richer surfaces

By this point the workbench can grow richer, but the archive should resist building a second hidden model just for GUI convenience.
Richer surfaces should mostly mean better projections of the same public objects: stronger review lanes, better share cards, clearer proof panels, and friendlier recovery views.


Possible next work:

- TUI
- local web UI
- FUSE/virtual mounts
- later Windows/macOS work only after Linux-first semantics are genuinely stable; no v1 parity promise
- platform-specific placeholder support
- private relay/discovery helpers

## What to avoid during roadmap execution

- copying every Resilio workflow before the core model is proven
- adding GUI sugar before state/diagnostics are solid
- turning the project into a generic storage platform
- hiding network policy in “advanced settings”
- merging linking and granting until trust boundaries become fuzzy

- inspect/prove/receipt surfaces for descendant capability so operators can tell whether a live linked descendant is actually eligible to act as byte source, approval seat, both, or neither for one governed subject without reconstructing it from ownership, peer presence, or remembered approval folklore

## Revision addendum — portable-offer redeemer provenance

Near-term roadmap work should now explicitly include:

- offer-recipient-intent, redeemer-identity-review, and offer-redeemer-receipt object model work so portable offers can answer `for whom`, `redeemed by whom`, and `what trust survived`
- dense/mobile projection work that keeps `For`, `Redeemed by`, and `Trust survived` adjacent instead of collapsing into vague `accepted` folklore
- lineage work linking later remembered approval back to one exact redeemer and one explicit mismatch outcome


## Revision addendum — portable-offer redemption ledgers

This revision adds the next offer-governance layer:

- redemption-ledger, redemption-attempt, budget-explanation, trust-fanout-plan, and ledger-receipt object model work so one multi-use artifact can expose ordered attempts without collapsing them into one generic audience
- UI and API work so `partially consumed`, `budget denied`, `approved subject only`, and `promoted broader` stay visibly distinct
- lineage work linking later remembered approval back to one exact successful redemption attempt rather than only to the parent artifact

## Revision addendum — redemption equivalence and slot accounting

This revision adds the next offer-governance layer:

- redemption-equivalence, slot-accounting-explanation, and slot-accounting-receipt object model work so repeated/familiar redeemers can be classified honestly instead of flattened into raw link-usage counters
- UI and API work so `replay collapse`, `same seat consumes no new slot`, `known peer new subject consumes slot`, and `require new artifact` stay visibly distinct
- compare-attempt lineage work linking later accounting decisions back to one concrete earlier redemption event


## Revision addendum — successor-artifact lineage and budget reset

This revision adds the next offer-governance layer:

- reissue-lineage, successor-boundary-explanation, and successor-boundary-receipt object model work so `require new artifact` can become one explicit predecessor/successor contract instead of a vague restart gesture
- UI and API work so `fresh budget island`, `narrowed successor`, `delivery-only copy`, and `broadened successor` stay visibly distinct
- lineage work linking replacement artifacts back to the exact predecessor posture and accounting or mismatch history that made reissue honest


## Revision addendum — delivery provenance and preview-authority boundaries

This revision adds the next portable-offer governance layer:

- delivery-event, preview-authority-explanation, and delivery-handoff-receipt object model work so browser landing pages, QR overlays, clipboard intake, and local-file import no longer collapse into one vague `opened link` story
- UI and API work so `preview only`, `landing page saw wrapper only`, `browser auto-handoff`, `locally parsed`, and `authoritative after inspect` stay visibly distinct
- lineage work linking later claim and trust consequences back to one exact delivery event instead of letting browser convenience stand in for authoritative intake truth


## Revision addendum — canonical artifact identity across carriers

This revision adds the next portable-offer governance layer:

- carrier-alias-row, canonical-identity-explanation, alias-review-plan, and carrier-alias-receipt object model work so browser wrappers, protocol rewrites, QR encodings, clipboard copies, and later file wrappers no longer collapse into one vague `same link` story
- UI and API work so `delivery wrapper`, `authority-bearing alias`, `same canonical artifact`, and `successor not alias` stay visibly distinct
- lineage work linking later claim, budget, and trust consequences back to one canonical offer identity instead of letting whichever carrier was seen last masquerade as the thing itself


## Revision addendum — preview-hint provenance and sealed-authority field partition

This revision adds the next portable-offer governance layer:

- field-provenance-row, field-partition-explanation, and field-partition-receipt object model work so landing-page hints, QR-adjacent labels, copied text, and app-parsed payloads no longer collapse into one vague `I already know this offer` story
- UI and API work so `hint only`, `sealed until parse`, `authoritative after parse`, and `not enough yet` stay visibly distinct
- lineage work linking later claim, trust, and budget consequences back to the exact field classes they relied on instead of letting preview familiarity masquerade as authority


## Revision addendum — preview sufficiency and omission-aware intake

Next portable-offer interface work should keep pushing on omission-aware intake, especially:

- decision-domain sufficiency summaries that remain stable across browser, QR, CLI, and mobile surfaces
- omission compression rules for dense rows so `recognition only` stays visible without turning every preview into a full review form
- sender policies for suppressing or minimizing preview hints when recognition benefit is outweighed by disclosure risk
- receipt tooling that lets later approval/claim decisions prove they did not rely on preview familiarity alone
