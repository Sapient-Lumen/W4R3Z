# Architecture overview

Helm is a desktop shell/compositor product built around one idea:

the desktop has a real object model, and that model should be visible and programmable.

The shell/compositor therefore owns desktop truth for:

- surfaces/windows
- focus and activation
- workspaces and placement
- visibility and reveal/select
- continuity posture and reentry
- transfer routing and exactness
- shell-object identity
- base automation entrypoints

Around that truth Helm ships seven first-party shell pillars plus a native terminal/capshell front-end family:

- **Tiling Shell** — keyboard-first, hybrid-capable presentation and layout
- **Omnibox** — launch, search, switch, route, and act over shell-owned objects
- **Object Browser** — query views, reveal, preview, selection, and durable object workflows
- **Operations Center** — windows, jobs, background presence, resource use, grants, failures, automation sessions, transfers, and receipts
- **Desktop Flow** — visible graph control over the desktop
- **Recall** — continuity, reentry, exact reopen/reveal, activity trail, and restored-vs-live honesty
- **Exchange** — typed ingress, transfer offers, selection packets, transfer routing, attach/share/forward workflows, route witnesses, materialization witnesses, effect receipts, and continuation handles
- **Terminal/Capshell** — a native shell-facing front-end family for explicit shell tooling that does not smuggle ambient authority back in

These are not eight adjacent apps. They are seven pillars plus one native shell-facing front-end family over one control plane.

Helm preserves raw reach through an explicit control-tier model:

1. shell graph
2. structural UI graph
3. raw automation lane

The exemplar lineage now translates like this:

- i3 → deterministic tiling discipline
- AHK → low-latency desktop programmability with a visible raw lane
- Rofi → unified summon/search/switch/dispatch over shell objects
- Dolphin → strong object/document browsing with query views and exact reveal
- “god-tier task manager” → an Operations Center that explains the desktop honestly

SlopOS and Schell now add two promoted product pressures that became pillars rather than hidden subsystems:
- exact continuity, explicit restore/reentry honesty, and durable activity truth
- typed transfer, explicit ingress/selection packets, transfer offers, exact route witnesses, and post-route materialization truth

Schell changed one major thing in recent revisions:
Helm no longer treats terminal work as a generic future placeholder.
Instead it names a provisional shell-facing treaty around:
- session lineage
- reviewed actions and receipts
- ingress packets
- execution-ground witnesses
- restoration honesty
- attach/forward route honesty

The product thesis is not “ban hacks.” It is “make the shell graph strong enough that hacks become the exception rather than the substrate.”

Helm's datacube stance is now much clearer: **do not build one giant cube.**
Build a shell-owned family of saved view objects, basis stamps, change cursors, resync reset cards, action warrants, revalidation checkpoints, drift gates, retry keys, effect receipts, slot verdict ledgers, rerun lineage links, quiesce rails, drain witnesses, grace-budget chips, cut-through receipts, intent sparks, direct-gesture gates, gesture runways, helper escorts, work claims, transfer offers, take cards, route witnesses, materialization witnesses, quarantine ribbons, endorsement receipts, shadow work lanes, adoption harbors, landing trains, reversal warrants, repair ladders, teardown rails, claim envelopes, reliance ladders, freshness windows, authority windows, elevation tickets, grant-rung ladders, revoke handles, de-elevation rails, active-borrow beacons, brake rails, freshness-horizon chips, decay rails, access verdict cards, least-widening previews, condition strips, state tuples, grounding witnesses, why rails, **delta briefs**, **since cards**, **footing marks**, **renewal beacons, overlap handoffs, footing death cards**, **residue ladders**, **salience lenses**, **quiet witnesses**, **change classes**, **re-review gates**, **semantic recipe cards**, **serve-path strips**, **`as-of` footing markers**, **validator rails**, **replay capsules**, **variance cards**, **compare lanes**, **epoch stamps**, **stale-fence strips**, **reset witnesses**, **coverage witnesses**, **blindspot rails**, **delivery witnesses**, **disposition witnesses**, **revisit witnesses**, **commitment witnesses**, **exception witnesses**, **waiver leases**, **breakglass beacons**, **resolution witnesses**, **retreat witnesses**, **succession witnesses**, observed-basis chips, trusted chrome lanes, host-effect witnesses, reveal windows, audience ladders, cohort windows, minimization ladders, reach previews, affected-set witnesses, glance derivations, glance windows, watchpoints, patrol routes, evidence briefs, response kits, timeline markers, bounded view subscriptions, derivative view decks, activity front doors, current-live beacons, pinned and floating handles, generation cards, rollback rails, attenuated reveal links, capability recipes, capability budgets, lease windows, renewal rails, promotion rails, semantic command landmarks, scoped accelerators, humane facet-conflict cards, weak Overview landings, bounded compare surfaces, caveat sheets, delegation subtrees, reality strips, **notice cards**, **triage cards**, **wake cards**, **promise cards**, **waiver cards**, **closure cards**, **refuge cards**, **baton cards**, **ceiling cards**, **commit cards**, and explicit publication/adoption/promotion/reveal/materialize/rollback/renew/revalidate/widen/narrow/remove/retire/endorse/safe-open/accept/decline/delegate/duplicate/queue/snooze/unsubscribe/promise/rescope/handoff/mark-met/reopen/archive/retreat/make-durable/revert-dependents moves over stronger shell truth.

While the companion cubes are still in design phase, Helm should freeze **cross-pillar verbs and proof slices** more confidently than it freezes **cross-pillar mega-objects**.

A wider product judgment now looks ready too: Helm's next delight/proof cluster should still be **humane return loops** rather than another new noun family. The first narrowing was **landmarks**: exact object/view return points, front doors, action templates, and compare entry points that stay stronger than recents but weaker than current-live proof. The next narrowing was the **reality strip** plus **continuity postcards**: a tiny always-near face for return and live-adjacent truth without a giant home plane. The next pull-trigger now looks even better: Helm should admit **grounding witnesses + why rails** beside **state tuples** so compact chrome can say not just what state is being claimed, but what exact witness, reason, message, freshness relation, and withheld-support posture stand behind the claim. After **footing marks** and typed **delta ladders**, the next narrow honesty seam should be **footing death cards + residue ladders** so serious surfaces can say whether older footing still survives, what exact class of break killed it when it does not, what weaker residue still remains, and whether the strongest next verb is continue, latest-only, rebuild, continue-as-new, or history-only. After that, the next humane return ratchet should be **delta briefs** and **since cards**: compact compared-basis answers to what changed since last-confirmed, since the landmark footing, since the reviewed basis, or since the last visit. Around them Helm should keep one explicit **salience lens**, one optional **quiet witness** when nothing qualifying moved, **typed action mode**, a **pilot-light Overview landing**, **object timelines** inside Recall, and **session-attention lights** beside helper/adoption truth before the archive freezes any giant cross-pillar home/workspace/memory machinery. In practice that means pull the trigger on delight proofs like parameterized front doors, exact action keys, promoted landmarks, grouped landmark shelves, one tiny current-live slot, one borrowed-now brake path, postcard-backed return truth, live-to-last-confirmed decay, one optional session-attention ember, pilot-light landing cues, peek → promote, productive restricted preview, glance windows with explicit promote ladders, exact-scope grants, exact remembered handles, constrained helper lanes, helper/session rosters, session-attention lights, named protection gates, pinned-versus-floating handle badges, compare / review / promote lanes, rehearsal → compare → promote rails, facet-conflict cards, generation cards, attenuated reveal links, capability budgets, borrowed-now lease windows, renewal rails, elevation tickets, de-elevation rails, effect receipts, slot verdict ledgers, rerun lineage links, quiesce rails, drain witnesses, grace-budget chips, cut-through receipts, intent sparks, direct-gesture gates, gesture runways, helper escorts, work claims, transfer offers, take cards, route witnesses, materialization witnesses, semantic command landmarks, selection-scoped action sparks, scoped accelerators, condition strips, **state tuples**, observed-basis chips, trusted chrome lanes, host-effect witnesses, active-borrow beacons, brake rails, freshness-horizon chips, decay rails, triage lanes, quarantine ribbons, endorsement receipts, continuity postcards, and reality strips before expanding family machinery any further.

## Cross-cutting moves currently pressuring the architecture

These are not promoted pillars, but they are increasingly important.
Many of them should now be read through one shared law: **projection surfaces are bounded, typed, source-witnessed, and non-authoritative by default.**
A second shared law is now warming in earnest: **preview, warrant/review, effect/receipt, rehearse/compare, materialize/adopt, reversal/repair, claim/reliance, freshness/revalidation, authority/eligibility/grant/de-elevation/revoke, helper-delegation/escort posture, work-claim/authority/task-result posture, intent/directness/runway posture, verdict/least-widening preview, reveal/audience, last-seen/change-cursor, retry/same-act identity, teardown/requested-vs-complete, live truth, and live-truth decay are different strengths, not one mushy convenience state.**
A third shared law now looks worth naming explicitly: **status should be multi-axis and basis-honest — phase, typed conditions, freshness, basis, and last outcome are different claims, and visible status should admit what exact mutable basis it was observed against.** This now looks less like a warm metaphor and more like a concrete shell-wide candidate grammar: **state tuples**.
A fourth shared law now looks ready beside it: **older trust should bind to exact footing, not float free of it — desired footing, observed footing, unsynced posture, reset-class change, reconsent, and retirement are different truths, not one inherited green state.**
A fifth shared law now looks ready beside that: **compact shell status should be revealably grounded — every humane tiny surface should be able to answer what class of witness produced the claim, what short reason/message explains it, and where stronger detail lives without turning into log theater.** This now looks like a concrete shell-wide companion grammar: **grounding witnesses + why rails**.
A fifth shared law now looks ready beside that pair: **bounded change should be basis-aware — users need a compact answer to what changed since the last trustworthy footing, not just a timestamp, a why rail, or a giant timeline.** This now looks like a concrete shell-wide companion object: **delta briefs**, with **since cards** as one likely tiny rendering.
A sixth shared law now looks ready beside delta briefs: **the shell should name what kind of earlier footing it means when it says “since” — last-visited, last-confirmed, last-reviewed, last-adopted, shared-base, and receipt-backed are different comparison baselines.** This now looks like a concrete shell-wide companion object: **footing marks**.
A seventh shared law now looks ready beside footing marks: **once the shell can say what changed since an exact reviewed footing, it should also say what strength of re-review that change deserves — some drift only reopens inspect posture, some reopens a latest-push recheck, some demands full re-review, and some is reset-class or reacquire-class rather than ordinary review.** This now looks like a concrete shell-wide companion seam: **change classes** plus **re-review gates**, with later maybe bounded **carry-forward rails**.
A seventh shared law now looks ready beside footing marks: **a compact change answer should say what kinds of change counted and whether the compared answer was quiet or partial.** This now looks like a concrete shell-wide companion bundle: **salience lenses** plus **quiet witnesses**.
A sixth shared law now looks ready beside revisit truth too: **assignment, target date, reminder, service-level timer, work occupancy, and actual promise are different truths, and compact surfaces should admit which one they are showing.** This now looks like a concrete shell-wide companion object: **commitment witnesses**, with **promise cards** as one likely tiny rendering.
A seventh shared law now looks warm enough to prove: **authority-bearing review should live in shell-owned trusted chrome, while weaker-origin content can only request shell-side effects through witnessed seams.**
A seventh shared law now looks worth warming: **foreign arrival, quarantine/risk state, safe-open posture, explicit endorsement, derivative-vs-source distinction, and live authority are different strengths, not one flattering open/import state.**
An eighth shared law now looks worth warming: **original cohort, observed affected set, exact unfinished remainder, live continuation, and humane repair scope are different truths, not one vague partial/retry state.**
A ninth shared law now looks worth warming beside the deck/branch/freshness cluster: **overlay, checked slice, lineage explanation, frozen share, bounded brief workbench, and current-live source truth are different strengths, not one clever collaborative surface.**


A tenth shared law now looks worth warming beside the overlay/check/lineage cluster: **summary health, downstream use, draft/live publication posture, and migration windows are different truths, not one operational badge.** A compact health tile may combine freshness, latest-run, and checks; a use rail may show references and affected dependents; a publish preview may compare draft to live; and a version window may keep latest and pinned consumers legible. None of those should outrank the exact reviewed slice or live shell truth underneath them.
A nearby product judgment now looks ready too: the shell should not stop at saved-versus-live and branch-versus-main honesty. It should also get better at **explainable decks**. In practice that means warming deck overlays, reviewed target-set promotion, attached checks, lineage rails, snapshot-share objects, and richer evidence-brief workbenches so Helm can support annotation, explanation, and curation without regressing into a giant BI dashboard center, a giant notebook suite, or a giant lineage wall.
A second adjacent product judgment now looks worth warming right beside that cluster: the shell should get better at **operationally trustworthy decks** too. In practice that means compact health tiles, downstream-use rails, compare-before-publish previews, and strict draft-versus-live posture so Helm can say not just what a slice shows, but whether it is healthy, who depends on it, and what exact live thing would change if the current draft were promoted.
An eighth shared law now looks ready to warm beside it: **historical effect, exact remainder, reviewed basis, present-time drift verdict, fresh reconsent, and renewed artifact are different truths, not one flattering resume/retry story.**

- **Three-form law** — recipes/definitions, tickets/snapshots/stable review slices, and live instances/current lanes should stay visibly different forms even when the shell makes them easy to move between

## New pressure from rev0140: quorum witnesses after succession witnesses

After **succession witnesses** and **baton cards**,
Helm can explain who currently has the baton,
how it moved,
and whether the stronger lane survived the relay.
What it still lacks is a shell-owned signoff seam for `what exact quorum still stands between candidate work and an authoritative move, whose signoffs count, and does the current basis still bind them?`

The current pressure is unusually crisp:
- GitHub branch protection keeps required approval counts, code-owner requirements, stale-dismissal, and merge-base drift invalidation explicit
- GitLab approval rules keep required-versus-optional rules, multiple simultaneous rules, eligible approvers, and counted approvals explicit
- LaunchDarkly approval settings keep approvals-required, self-approval, consensus, and bypass posture explicit
- Jira Service Management keeps approver sets and blocked workflow movement explicit
- Figma keeps review state visible while still separating approval from actual merge authority

### New shared law warming beside succession witnesses

A new shared law now looks ready to warm beside baton truth too: **holder truth, signoff-threshold truth, basis-validity truth, veto/consensus truth, bypass truth, and final outcome truth are different truths, and compact surfaces should admit which one they are showing.** This now looks like a concrete shell-wide companion object: **quorum witnesses**, with **signoff cards** as one likely tiny rendering.


## New pressure from rev0141: headroom witnesses after quorum witnesses

After **quorum witnesses** and **signoff cards**,
Helm can explain what threshold still stands between candidate work and an authoritative move.
What it still lacks is a shell-owned ceiling seam for `even if this is allowed and approved, how much headroom remains under the relevant budget / quota / burst / seat / rate family, and what exact recovery move is honest when that ceiling is hot?`

The current pressure is unusually crisp:
- Kubernetes ResourceQuota keeps `used` and `hard` ceiling math explicit
- GitHub REST rate limits keep remaining budget, reset horizon, and retry posture explicit
- Google Cloud separates adjustable quotas from fixed system limits and supports usage monitoring plus alerts
- AWS Service Quotas keeps adjustable increase workflow explicit
- Slack keeps tiered burst ceilings and special-scope limits explicit

### New shared law warming beside quorum witnesses

A new shared law now looks ready to warm beside signoff truth too: **authority truth, signoff-threshold truth, headroom truth, reset/refill truth, burst-versus-sustained truth, adjustable-versus-fixed truth, and final outcome truth are different truths, and compact surfaces should admit which one they are showing.** This now looks like a concrete shell-wide companion object: **headroom witnesses**, with **ceiling cards** as one likely tiny rendering.

### New shared law warming beside headroom witnesses

A new shared law now looks ready to warm beside headroom truth too: **authority truth, signoff truth, headroom truth, request acceptance, local durability, quorum / replication posture, receiver-visible settlement, and final outcome truth are different truths, and compact surfaces should admit which one they are showing.** This now looks like a concrete shell-wide companion object: **settlement witnesses**, with **commit cards** as one likely tiny rendering.
- **Review tickets** — compact shell-owned stable-enough review slices for compare, paging, route inspection, checkpoint review, and handoff without pretending current liveness
- **Activity spines** — shell-owned scoped work frames that can gather saved views, checkpoints, quick actions, launch/layout starters, review tickets, and one current-live beacon without collapsing into a giant workspace religion
- **Current-live beacons** — compact shell-owned exact current-lane cues that stay stronger than recents, entry kits, checkpoints, or grouped resource sets
- **Reality strips** — tiny shell-owned always-near projection surfaces that can compose current-live beacons, active-borrow beacons, continuity postcards, freshness-horizon chips, and condition strips without becoming a dashboard or a hidden authority plane
- **State tuples** — compact shell-owned multi-axis state grammars over one exact subject that keep phase, typed conditions, freshness / live-until posture, basis class, and last durable outcome visibly different even when compressed into tiny chrome
- **Work claims** — compact shell-owned live coordination objects over one exact subject that keep holder, mode, freshness, queue/handback posture, and historical residue visibly different from broader authority, assignments, or task/result truth
- **Commitment witnesses** — compact shell-owned obligation objects over one exact subject or relation that keep promisor, promisee, target window or condition, footing/dependency posture, miss/rescope/handoff law, and historical promise residue visibly different from assignee badges, reminders, SLA timers, live work occupancy, or final outcome truth
- **Succession witnesses** — compact shell-owned baton / holder-transition objects over one exact subject or relation that keep previous holder, current holder, relay class, policy continuity, shared-vs-exclusive posture, acceptance state, expiry / return posture, and historical relay residue visibly different from assignment badges, live work occupancy, promises, or final outcome truth
- **Quorum witnesses** — compact shell-owned signoff-threshold / approval-gate objects over one exact subject or relation that keep rule identity, required count, counted count, eligible signer class, optional-versus-required posture, stale-basis posture, veto / consensus posture, and bypass-versus-satisfaction truth visibly different from holder badges, promises, waivers, or final outcome truth
- **Headroom witnesses** — compact shell-owned remaining-budget / quota / rate / burst / seat / capacity objects over one exact subject or relation that keep used-versus-limit math, remaining headroom, reset / refill law, burst-versus-sustained posture, adjustable-versus-fixed posture, payer relation, and historical-success humility visibly different from authority badges, signoff badges, or final outcome truth
- **Settlement witnesses** — compact shell-owned post-act durability / replication / receiver-visibility objects over one exact effect, receipt, route, or publication step that keep accepted, local-durable, quorum-durable, cross-target-settled, receiver-visible, pending-settlement, and historical-only postures visibly different from headroom, promise, or final outcome truth
- **Exception witnesses** — compact shell-owned exception objects over one exact rule, gate, promise, or condition that keep bypass, waiver, pause, silence, expiry, revoke, reason, requester, granter, and scope visibly different from healthy compliance, quiet, resolution, or current-live success
- **Transfer offers** — compact shell-owned offered-material objects that keep exact source, representation menu, preview / promise posture, advisory receiver hints, and later take truth visibly different from chosen route, import/open/attach/publish, or receipt truth
- **Materialization witnesses** — compact shell-owned post-handoff acquisition objects that keep exact retrieved representation, materialization class, retrieval-proof source, lifetime / closure posture, and downstream-unknown humility visibly different from chosen route, current-live receiver state, or durable effect truth
- **Pinned and floating handles** — compact shell-owned handle posture objects that keep exact reviewed / exact historical / exact commit-like reentry visibly different from intentionally latest-following entry points
- **Generation cards** — compact shell-owned exact-history objects that keep current generation, prior generations, compare posture, rollback posture, and retention class visible for materially changing saved shell surfaces
- **Attenuated reveal links** — compact shell-owned travel/share objects that keep one exact subject or cohort, one reveal shape, one audience class, one expiry posture, and one revoke path visibly different from broad durable access
- **Capability recipes** — compact shell-owned portable starter objects that preserve helpful preferred setup, likely reacquisition paths, generation lineage, and declared future-ask posture without impersonating current-live grants or current-live state
- **Capability budgets** — compact shell-owned upper-bound ask objects that say what a front door, recipe, flow fragment, or helper lane may later request without pretending those asks are already granted
- **Helper escorts** — compact shell-owned downscoped helper-delegation objects that keep exact helper identity, exact subject or cohort, narrower-than-parent scope, expiry / uses, blocked stronger families, and unsatisfied human seams visible without becoming a giant token console
- **Lease windows** — compact shell-owned current-live borrowing objects that say what exact authority is actually held now, by whom, on what subject, on what rung, for how long, and with what nearby revoke/narrow moves
- **Renewal rails** — compact shell-owned next-step rails that keep renew-same, renew-narrower, move-to-isolated-lane, widen-with-fresh-ask, and let-expire visibly different when old borrowing is revisited
- **Promotion rails** — compact shell-owned paths that keep rehearsal, compare, gates, promote, refusal, and aftermath visibly different when side work or preview becomes strong enough to land
- **Retry keys** — compact shell-owned same-act witnesses that keep safe retries visibly different from second attempts or silent duplicate effects when stronger acts cross unreliable boundaries
- **Teardown rails** — compact shell-owned pending-removal objects that keep teardown requested, blockers, cleanup progress, force posture, and teardown complete visibly different
- **Facet ownership cards** — compact shell-owned conflict surfaces that say which authored, imported, derived, helper, or default actor currently owns one facet/slot of a composite shell surface and what explicit takeover or keep-local moves exist
- **Activity memory seeds** — compact shell-owned remembered facts, warnings, instructions, or object/view pointers that stay explicit, scoped, source-witnessed, and weaker than live truth
- **Context loadouts** — compact shell-owned current bundles of selected tabs/files/views/seeds/tools/instructions for one ask, compare, route, or action
- **Contribution witnesses** — compact shell-owned after-surfaces that say what was selected, what was actually used, and what stayed merely nearby or available
- **Claim envelopes** — compact shell-owned output objects that separate observed, sourced, derived, remembered, proposed, and unresolved claim classes; can reveal grounding witness, freshness, locality, and redaction posture; and stop mixed-result surfaces from flattening everything into one answer box
- **Reliance ladders** — compact shell-owned next-step ladders that keep inspect basis, inspect sources, inspect helper-session witness, double-check, save weakly, quote/share, adopt, and apply visibly different strengths next to a claim envelope
- **Freshness windows** — compact shell-owned decay/revalidation posture objects that say how fresh one bounded saved, derived, watched, remembered, or traveling shell object still is; what weaker stale class if any still applies; and what exact revalidation rails remain available
- **Change cursors** — compact shell-owned last-seen / caught-up-through / resume-from witnesses that keep “what I last saw,” “where a stream can resume,” “what exact start semantics apply,” and “has this changed since then?” visibly different from current-live truth
- **Resync reset cards** — compact shell-owned dead-bookmark witnesses that keep cursor expiry, history pruning, source replacement, and exact reset scope visibly different from live source health, watchpoint state, and silent jump-to-latest repair
- **Authority windows** — compact shell-owned bounded grant objects that say what exact authority family exists or recently existed, for whom, on what subject, on what rung, with what live-vs-historical posture, and with what revoke/narrow next moves
- **Elevation tickets** — compact shell-owned temporary-power tickets that keep eligible, requested, pending approval, active, and historical temporary stronger power visibly different while preserving reason, duration, reduced-scope, and extra-check posture
- **De-elevation rails** — compact shell-owned nearby rails that keep end-now, narrow-now, drop-back-to-eligible, and inspect-history visibly different once temporary stronger power exists
- **Grant-rung ladders** — compact shell-owned humane choosers that keep inspect, exact once, this ask, this activity, isolated-lane only, and persistent scope visibly different instead of collapsing everything into one Allow button
- **Revoke handles** — compact shell-owned nearby live controls that keep revoke, suspend, narrow, and move-to-isolated-lane visibly different after a grant exists
- **Reveal windows** — compact shell-owned bounded visibility objects that say what exact audience relation exists or recently existed, by what route, in what reveal shape, under what expiry/policy posture, and with what current-live versus historical truth
- **Audience ladders** — compact shell-owned humane choosers that keep local-only, named, org/workspace, guarded-link, and public/time-boxed reveal visibly different instead of collapsing everything into one Share state
- **Action warrants** — compact shell-owned exact proposed-change objects that say what strong effect is being asked for, on what reviewed basis, with what affected-set and next-step posture
- **Reach previews** — compact shell-owned pre-act expected-reach surfaces that say what a stronger reveal/export/mute/apply/rerun act would currently include, whether that reach is static or dynamically rule-derived, and where the inspect/narrow/broaden path lives
- **Affected-set witnesses** — compact shell-owned exact-or-counted witnesses for predicted or observed touched sets so previews, warrants, windows, receipts, and repair surfaces can carry inspectable “who was in scope” truth
- **Drift gates** — compact shell-owned gates that compare a warrant's reviewed basis against current mutable basis so stronger rungs can downgrade honestly when the target drifted
- **Effect receipts** — compact shell-owned durable aftermath witnesses that say what exact effect actually happened after a stronger act without impersonating current-live truth
- **Slot verdict ledgers** — compact shell-owned slotwise aftermath ledgers that keep partial landing, rebind, default-fill, pending, and refusal outcomes inspectable after the act
- **Quiesce rails** — compact shell-owned cooperative maintenance controls that keep no-new-work, drain-versus-cancel mode, visible blockers, resume, and cut-through posture visibly different without turning the shell into a giant orchestrator
- **Drain witnesses** — compact shell-owned maintenance-phase witnesses that keep running, quiescing, quiescent, resumed, cut-through, and completed-historical posture visibly different while carrying blocker and freshness truth
- **Landing trains** — compact shell-owned ordered promotion objects that keep queue order, exact target lane, rebuild/invalidation truth, and optional guarded-promotion ladders visible when several candidates aim at one authoritative lane
- **Reversal warrants** — compact shell-owned exact reverse/recover proposal objects that bind one historical effect, checkpoint, or reviewed change before a stronger reversal or compensating act happens
- **Repair ladders** — compact shell-owned bounded next-step ladders that keep undo, redo, rerun-failed-subset, replay-on-fresh-basis, reopen-unresolved, branch-and-fix, and hold visibly different after a partial or regretted effect
- **Remainder witnesses** — compact shell-owned unfinished-slice witnesses that keep remaining ranges, failed indexes, unresolved slots, pending recipients, and partially unknown leftover sets visibly different from original cohorts, affected-set memory, live continuation handles, and current-live truth
- **Aftermath decks** — bounded shell-owned post-act workspaces that gather settlement, effect, continuation, remainder, repair, and later calibration around one exact story family while staying weaker than current-live truth
- **Recovery maps** — compact shell-owned next-rung maps inside or beside aftermath decks that keep continue, rerun-failed-subset, redrive, replay-on-fresh-basis, compensate, widen, and hold visibly different
- **Revalidation checkpoints** — compact shell-owned review-again / reconsent cards that keep reviewed basis, current-basis relation, fresh-step posture, and renewed-artifact humility visibly different from historical receipts, live continuation, or current-live authority
- **Gesture runways** — compact shell-owned prepared final-step lanes that preserve exact subject, prepared parameters, and reviewed basis while stopping at fresh-spark or direct-gesture seams instead of laundering stale intent into later authority
- **Context recipes** — still-warm tiny ordered bundles of memory seeds, instructions, and starter hints that can steer return/planning surfaces without becoming a second hidden control plane

- **Projection surfaces** — compact shell-owned derivative surfaces such as docks, rails, strips, lenses, cockpit cards, decks, bays, and exact trails that project already-legible shell truth without becoming new authority domains
- **Preview** — a shell-wide inspect-before-commit surface that should appear across Object Browser, Omnibox, Recall, Exchange, and Operations Center
- **Preview-promotion ladders** — a shell-wide grammar where preview may carry bounded actions and then explicitly promote into open, reveal, split, import, adopt, compare, or branch without pretending those stronger moves already happened
- **Glance windows** — temporary weak windows that keep place, preserve source posture, and decay or auto-archive unless explicitly promoted into stronger open, split, shelf, route, or adopt posture
- **Open-versus-stronger-act honesty** — generic open/summon should remain weaker than current-live reentry, durable save, materialization/adoption, publication/promotion, and branch/fork acts
- **Workspace/activity capsules** — continuity objects that capture and reenter meaningful project state with exact/repaired/partial/unavailable honesty
- **Scoped activity memory** — a spine or shared activity should be explicit about what memories, views, receipts, and resources are in scope and what remains deliberately out of scope
- **Imported-surface trust posture** — a reusable weaker starting posture for inbound/shared/rebound shell surfaces, ideally with explicit restricted-mode cues and named blocked powers, so imported things can be useful before they are fully adopted as local truth
- **Overview** — a spatial companion to Omnibox that shows windows, workspaces, continuity cues, and quick moves at a glance
- **Visual layout/template editing** — a Tiling Shell surface for spatial templates without regressing into separate zone-manager culture
- **Activity cockpit cards** — shell-owned activity front doors that combine live status, continuity relation, layout relation, and next actions without becoming a new pillar
- **Activity entry kits / front doors** — shell-owned saved starter objects that sit on top of activity spines and resource shelves, point at one preferred way in, can expose one triage lane and one compare/change path nearby, carry explicit profile/provider affinity without silently choosing it, and keep inspect / attach / restore / relaunch / fresh-start choices explicit without pretending to be live state
- **Exact front-door handles** — tiny shell-owned summonable entry objects that point at one preferred way back in without pretending they are current-live proof
- **View subscriptions** — shell-owned bounded attention relations attached to one exact saved view object so a view can notify without becoming a hidden daemon or giant timeline
- **Glance derivations** — tiny shell-owned derived summary objects over one exact saved view or review ticket so Overview and subscriptions can stay glanceable without pretending summary cards are live truth
- **Watchpoints** — shell-owned evaluated-state objects over one exact saved view so Overview and Operations can show durable watch state without confusing notification history for current evaluated truth
- **Attention windows** — shell-owned quiet / active / maintenance / critical-only posture objects over exact subscriptions, watchpoints, patrol routes, or digest lanes so interruption law stays inspectable and weaker than watched truth
- **Quiet witnesses** — shell-owned bounded stillness objects that keep no-material-change-observed, no-signal-yet, stale-last-known calm, coverage-incomplete calm, and evaluation-suppressed calm visibly different over one exact footing/lens/coverage bundle
- **Stillness cards** — tiny shell-owned derivative renders for quiet witnesses so Overview, Recall, watchpoints, and reality strips can show scoped calm without pretending universal all-clear
- **Delivery witnesses** — compact shell-owned attention-truth objects that say whether an event or subject was suppressed, queued, delivered, presented, read, cleared, snoozed, saved, or acknowledged for one exact audience scope without laundering that into source truth
- **Notice cards** — tiny shell-owned derivative renders for delivery witnesses so Overview, Recall, watchpoints, subscriptions, and reality strips can show attention-layer truth without becoming a giant inbox or notification center
- **Revisit witnesses** — compact shell-owned return-law objects that say when or why something should come back: remind-at-time, snoozed-until, time-or-new-activity, due-soon, ack-timeout return, or review-on-drift, without laundering that into source outcome truth
- **Wake cards** — tiny shell-owned derivative renders for revisit witnesses so Overview, Recall, watchpoints, subscriptions, and reality strips can show return law without becoming a giant reminders app
- **Basis stamps** — compact shell-owned exact-basis witnesses that let traveling, derived, reviewed, or published shell luxuries say what exact source, revision, checkpoint, query, or prior reviewed state they reflect without bluffing latestness
- **Patrol routes** — shell-owned bounded revisit circuits over linked views, watchpoints, compare tickets, and exact front-door handles so the rounds people actually make stop depending on memory, recents, or giant dashboards
- **Evidence briefs** — shell-owned bounded curated-investigation objects over exact views, watchpoints, glances, tickets, receipts, and handles so people can gather and explain why something matters without turning the shell into a giant notebook or case engine
- **Response kits** — shell-owned bounded guided-response objects over exact source refs, instructional and automated steps, action affordances, preconditions, and visible outputs so people can see what to do next without turning the shell into a giant workflow engine
- **Live lenses** — bounded shell-owned derivative watch/compare surfaces that keep source witness and modest action strength explicit
- **Drift beacons** — compact shell-owned change-aware surfaces that compare one exact current subject against one exact reviewed or remembered basis without becoming giant timeline theater
- **Basis contrast cards** — bounded shell-owned current-vs-basis compare surfaces that sit one rung above drift beacons and one rung below giant history/diff products
- **View decks** — small shell-owned named sets of explicit views over one subject family, activity relation, or query basis, often including triage/compare/work members, without collapsing into dashboard folklore
- **Linked views** — borrowed by-reference appearances of saved view objects inside other shell surfaces, keeping source and basis witness instead of becoming copied authority
- **Deck recipes** — shell-owned typed saved starters that can materialize a view deck or deck-like cluster without letting the recipe itself impersonate live continuity
- **Derivation strips** — tiny shell-owned witness strips/headers that keep a compact derived surface honest about its exact source, basis, recipe, and locality tier
- **Publication ladders** — compact shell-owned ladders for promoting a surface across locality tiers without ambient sync or fake shared liveness
- **Handoff packets** — portable shell-owned travel forms that let a derived or saved surface cross tiers with exact source, basis, and locality witness without pretending the receiver already has live local state
- **Receiver-fit cards** — compact receiver-side landing cards that say what matched locally, what was intentionally omitted because it is receiver-local, and what explicit choices still remain before rebind, materialize, or adopt
- **Promotion receipts** — compact shell-owned durable witnesses for publication/share/export moves, including tier change, audience delta, and receiver-side expectations
- **Materialization bays** — explicit shell-owned places or workflows where a preview, view, import, trail, recipe, or candidate can become a stronger local or live thing without smuggling that stronger workflow through the weaker one
- **Landing rehearsals** — compact receiver-local try-before-adopt surfaces where an imported or derived shell object can be rendered provisionally before it becomes adopted local truth
- **Review strips** — tiny shell-owned preflight strips/cards that can show subject, route, basis, and readiness without forcing giant review UI
- **Launch ladders** — small shell-owned next-step ladders that distinguish inspect, fresh launch, attach, reuse, repaired return, historical replay, and hold instead of flattering everything into “open”
- **Sticky context strips** — tiny shell-owned anchors that keep long-lived output, receipts, status lanes, or result panes attached to their source/action/subject posture
- **Preview rails** — compact bounded next-step rails next to shell-owned preview so inspect and stronger action stay adjacent but distinct
- **Facet strips** — compact typed pivot rows for objects, actions, routes, receipts, and transfers so summon/recency surfaces avoid one mushy mixed list
- **Exact-object recency** — Recall cues centered on exact objects, reviewed actions, route receipts, and clear source labels rather than vague recent-items folklore
- **Current-live reentry cues** — one shell-owned obvious return path for the real active live lane, typically carried by a current-live beacon and kept visibly stronger than generic history or recent/opened hints
- **Authority windows** — shell-owned bounded grant objects that say what authority is live or historical for one act, lane, activity, or source, with expiry/revoke posture and explicit separation between issuance evidence and current-live truth
- **Grant-rung ladders** — small shell-owned choosers that keep inspect / once / this-time / ask-scoped / activity-scoped / isolated-lane / persistent grants visibly different instead of flattening them into one Allow button
- **Revoke handles** — compact shell-owned current-control objects that keep exact revoke, suspend, or narrow acts nearby for live grants instead of burying them in provider folklore
- **Attenuation ladders** — small shell-owned de-escalation choosers that keep drop-to-inspect, this-ask-only, activity-only, isolated-lane-only, subfamily-only, and full revoke visibly different after a grant is already live
- **Reusable flow fragments** — reusable status-bearing graph units so Desktop Flow can absorb subflow/prefab lessons without becoming opaque
- **Binding witness cards** — shell-owned continuity cards that explain exact / repaired / ambiguous / unavailable joins across saved or planned structure and current live targets
- **Activity scope witnesses** — small shell-owned strips/cards that say which axes counted for same-activity continuity and which nearby ambient context stayed out
- **Continuity choice witnesses** — small shell-owned strips/cards that say who proposed, chose, or executed a repaired, widened, switched, reused, or delegated continuity path
- **Basis packets** — small shell-owned strips/cards that say what exact reviewed basis a stronger action still depends on, whether it still matches, and which honest next ladder remains
- **Shadow work lanes** — small shell-owned isolated mutable side lanes with exact live-subject links, authorship posture, basis posture, and drift visibility for delegated or background work
- **Adoption harbors** — compact shell-owned inspect/apply surfaces where candidate side work can be previewed, selectively adopted, held, or rejected without pretending it is already live truth
- **Arrival overlays** — compact shell-owned compare surfaces that show one arriving subject against one exact basis or one explicit local candidate before adoption
- **Adoption slices** — bounded shell-owned partial-adoption acts that let receivers accept one admitted slice of a landing while keeping the remainder explicit
- **Lineage modes** — compact shell-owned cross-boundary identity choices that distinguish preserve-lineage, fork-as-copy, and fresh starter-instantiation before stronger publish/import/materialization acts
- **Fork receipts** — compact shell-owned durable ancestry witnesses that explain when a new surface was born from another one without pretending same-object continuity survived

Twelve narrower moves are now frozen rather than merely implied:

- **typed Omnibox providers** — the action-surface breadth is welcome, but the extensibility model is typed-provider-first rather than ambient shell-string plugin culture
- **Flow observability/reuse** — Desktop Flow now explicitly requires debug/event surfaces, graph secondary views, and reusable inspectable fragments
- **request-vs-live truth** — rich cards, routes, restores, and status surfaces must not flatten proposal, admission, live observation, and historical receipt truth into one flattering success story
- **entry-artifact truth** — saved task-entry objects must not flatten selected plan/history/guidance into current live state merely because they are convenient to summon
- **binding witness posture** — non-exact joins from saved/planned structure to current live targets must stay witnessable rather than silently counting as ordinary success
- **activity-scope truth** — same-activity claims must not silently inherit nearby workspace/profile/account/browser/remote/provider context by convenience or glow
- **continuity-switch authorship truth** — repaired, widened, switched, reused, or delegated continuity must not hide who proposed, chose, or executed the move
- **reviewed-basis truth** — strong shell-facing actions should not silently follow newer mutable basis just because the shell still remembers the task, card, or prior review
- **delegated-adoption truth** — delegated, background, or repair-produced mutable candidate work should not silently mutate the operator's authoritative live lane before explicit adoption
- **ordered-promotion truth** — when several candidates aim at one authoritative lane, queue order, rebuilds, invalidations, pauses, and partial guarded promotion should stay visible instead of collapsing into isolated green-check folklore
- **approval-on-reviewed-basis truth** — strong shell-facing apply/adopt/run acts should bind one exact reviewed basis and downgrade honestly when that basis drifted instead of silently following the newest mutable state
- **quorum truth** — required counts, eligible signer classes, stale signoffs, optional rules, consensus/veto posture, and bypasses should stay visibly separate instead of collapsing into one reassuring approved badge
- **headroom truth** — permission, signoff, remaining budget, burst allowance, reset/refill law, adjustable-versus-fixed ceilings, and payer posture should stay visibly separate instead of collapsing into one reassuring ready or exhausted badge
- **recovery truth** — generic undo/retry language should not flatten exact reversal, redo, subset rerun, replay-on-fresh-basis, compensating reverse, and hold into one flattering recovery story
- **authority-duration truth** — temporary approval or grant should not silently widen, float onto a drifted basis, or outlive its explicit rung just because the shell remembers that it was granted once
- **eligibility-versus-activity truth** — being eligible to request stronger power, having a pending request, holding a temporary grant, and being hot now are different claims and should not collapse into one flattering allowed state
- **post-grant control truth** — revocation, suspension, de-elevation, and narrowing should stay exact about what ended and what remains rather than hiding in provider-specific settings or overclaiming total erasure
- **reveal-route truth** — named invite, org-only, guarded link, public link, and bearer/signed route should stay visibly different instead of flattening into one flattering shared badge
- **historical-share truth** — promotion receipts and old publish/share events should not impersonate current audience truth unless a stronger live reveal witness confirms the surface is still open now


Additional narrower moves frozen by this revision:

- **linked-view provenance truth** — borrowed views must keep source, basis, locality tier, and degradation posture inspectable instead of pretending wrapper-local ownership
- **front-door handle truth** — tiny summonable entry handles should stay exact and useful without impersonating current-live beacons or silent strongest-act launch
- **profile-affinity truth** — preferred profile/account/provider/space hints should stay explicit witnesses or choices rather than ambiently selecting live scope
- **suggestion-first triage truth** — AI triage help should begin as explainable suggest/accept/decline posture before any stronger auto-apply rung becomes admissible


New narrower moves frozen by this revision:

- **view-subscription truth** — a saved view may carry bounded attention, but the subscription remains shell-owned, revocable, inspectable, and weaker than current-live or workflow-authority truth
- **overview-landing truth** — Overview should be assembled from linked views, handles, watchpoints, beacons, nearby briefs, nearby kits, and bounded ops slices rather than becoming a second authority plane or giant home dashboard
- **watch-state honesty** — saved view, watchpoint, and delivery event should remain distinct forms, and muted delivery must not impersonate healthy evaluation
- **attention-window honesty** — quiet / maintenance / active-only delivery windows should remain distinct from source truth and watch state, and silence must not impersonate recovery
- **brief-versus-source honesty** — a brief should stay a bounded curated derivative object whose notes, summaries, and imported posture remain weaker than the exact source views, tickets, receipts, and current-live evidence it gathers


Additional narrower move frozen by this revision:

- **marker-time truth** — point/range markers, imported change events, and recent-change breadcrumbs should help correlate time and context without impersonating current-live proof, causal certainty, or giant event-bus authority


## New cross-cutting pressure: least-reach cohorts

Helm now has enough saved, derived, authority, reveal, and recovery objects that one additional law becomes useful across the whole shell:

- a **loadout** says what ingredients are intentionally available
- a **cohort window** says what exact subset a bounded act is actually about
- a **minimization ladder** says how much wider the shell is asking to go
- a **reach preview** says what the stronger move would actually include right now
- an **affected-set witness** keeps predicted and observed touched-set truth inspectable nearby

That distinction keeps Exchange, Recall, Omnibox, and Operations Center from quietly widening from one selected slice into one whole provider or workspace family, and from collapsing predicted blast radius into live aftermath folklore.

## Current ratchets from rev0085

This revision adds three especially strong design-phase ratchets that should now inform most pillar work:

- **restricted-first adoption posture** — imported, rebound, borrowed, or helper-generated structures should begin inspectable and weaker than ordinary local truth until an explicit adopt step upgrades them
- **saved-plan / reviewed-basis posture** — stronger acts should be able to carry exact subject, exact scope, exact basis, drift status, and inspect-before-apply review rather than collapsing immediately into fire-and-forget mutation
- **exposure ladders** — local preview/open, named/private cohort, org/tailnet, guarded-link, and public should remain visibly different reveal/exposure classes rather than one generic open/share state
- **exact remembered handles** — wherever the host allows it, Helm should carry exact reopen/rebind access as remembered handles/bookmarks with visible current / stale / re-requestable posture rather than path/title nostalgia
- **constrained helper lanes** — helper, delegated, or repair work should run inside visible file/object and network bounds with allow / ask / deny posture rather than ambient shell reach
- **named protection gates** — strong publish/apply/expose acts may need visible reviewer / delay / policy / custom-check gates that stay distinct from both the proposal and the final effect receipt

A fourth ergonomic ratchet is warming into likely law:
**adopt the narrowest safe rung** should be an ordinary fast path across pillars.

These are not arguments for a bigger cross-pillar constitution.
They are arguments for a tighter shell-owned verb grammar over the same seven pillars.


- **typed action mode** — Omnibox should be able to switch from search/browse posture into a typed shell action posture with named arguments, inspectable provider identity, and honest review/effect ladders
- **promoted exact landmarks** — bookmarks, quicklinks, front doors, saved layouts, and exact action keys should stay exact handles rather than recency mush
- **helper/session rosters** — background or delegated work should have an exact roster with live footing, lane identity, and adoption posture instead of living only as logs or notifications


- **Landmarks** — shell-owned promoted return points for exact objects, front doors, typed actions, and compare entry paths that stay stronger than recents but weaker than current-live proof
- **Session-attention lights** — compact shell-owned cues that background or helper work is running, adoption-ready, drifted, or attention-worthy without pretending the live lane already changed


## New pressure from rev0127

Helm should now increasingly treat **footing** as a first-class shell question.
Delta briefs helped clarify what changed, but they also exposed the missing seam: the shell still needs one compact object that says **which earlier footing counts here**.
That is the job of **footing marks**.

A new shared law now looks ready beneath resumption briefs too: **when the shell can name the earlier footing, it should also keep the next-round grammar explicit — finishing the current page or batch, adopting the next durable baseline, waiting on a wake signal, rebuilding the same scope, and reacquiring after reset are different next moves.** This now looks like a concrete shell-wide companion seam: **delta ladders**.

A footing mark is weaker than a delta brief and weaker than a receipt.
It does not explain the change or prove the result.
It simply prevents compact shell surfaces from saying “since last time” without saying whether the baseline is personal, shared, reviewed, adopted, lane-relative, or receipt-backed.


## New pressure from rev0128: salience lenses after footing marks

After **footing marks**,
Helm's next small honest move is not another pillar.
It is one shell-owned **salience lens** family.

Footing marks answer **since what kind of earlier footing?**
Salience lenses answer **what kinds of change counted,
what was grouped or suppressed,
and whose perspective made the change matter?**

That is now the clean follow-on because current tools keep proving the same ordering law:
first name the baseline,
then name what counts.
Without that,
compact chrome still lies by acting as though every observed change matters equally once a footing exists.


A seventh shared law now looks ready beside footing marks and salience lenses: **compact surfaces should admit their inspected coverage — named baseline and named materiality are still not enough unless the shell can also say what exact source/lane/window/account space it actually looked at, what remained stale or unauthorized, and what the cheapest honest widen / resync / inspect move is.** This now looks like a concrete shell-wide companion pair: **coverage witnesses + blindspot rails**.

## New pressure from rev0130: quiet witnesses after coverage witnesses

After **coverage witnesses** and **blindspot rails**,
Helm's next small honest move is not another pillar.
It is one shell-owned **quiet witness** family with tiny **stillness cards**.

Coverage witnesses answer **what exact space was inspected?**
Quiet witnesses answer **what kind of nothing happened there — and how trustworthy is that calm?**

That is now the clean follow-on because current tools keep proving the same ordering law:
first name the baseline,
then name what counts,
then name what you inspected,
and only then are you allowed to say *nothing important changed*.
Without that,
compact chrome still lies by letting silence impersonate health,
completeness,
or universal calm.

## New pressure from rev0131: delivery witnesses after quiet witnesses

After **quiet witnesses** and **stillness cards**,
Helm's next small honest move is not another pillar.
It is one shell-owned **delivery witness** family with tiny **notice cards**.

Quiet witnesses answer **what kind of calm or change can be claimed here?**
Delivery witnesses answer **what happened in the attention layer about that claim?**

That is now the clean follow-on because current tools keep proving the same ordering law:
first separate source truth from attention policy,
then separate posted from presented,
then separate read from cleared,
then separate snoozed or saved from acknowledged,
and never let any of those pretend to be the underlying fix, adoption, or current-live truth.
Without that,
compact chrome still lies by treating a shown or read cue as though the important thing was handled.


### New shared law warming beside delivery witnesses

A compact shell surface increasingly needs to answer five different questions without flattening them together:
- **what kind of subject truth is being claimed?**
- **what happened in the attention layer about it?**
- **what stance was chosen afterward?**
- **when or why should it come back?**
- **what stronger work/outcome truth exists, if any?**

That means Helm should increasingly keep apart:
- source outcome truth
- delivery truth
- disposition truth
- revisit truth
- live work truth
- and historical residue

This now looks less like a metaphor and more like a shell-wide ratchet: **revisit witnesses**, with **wake cards** as one likely tiny rendering.


## New pressure from rev0135: exception witnesses after commitment witnesses

After **commitment witnesses** and **promise cards**,
Helm's next small honest move is not another pillar.
It is one shell-owned **exception witness** family with tiny **waiver cards**.

Commitment witnesses answer **what was promised here?**
Exception witnesses answer **is the requirement actually being met,
or are we proceeding under an explicit bypass,
waiver,
pause,
or downtime?**

That is now the clean follow-on because current tools keep proving the same ordering law:
first separate assignment from promise,
then separate promise from compliance,
then separate silenced enforcement from healed state,
and never let an approved exception quietly repaint the world as healthy.
Without that,
compact chrome still lies by treating bypass,
downtime,
pause,
or acknowledgement as though the underlying gate was genuinely satisfied.


## New pressure from rev0136: resolution witnesses after exception witnesses

After **exception witnesses** and **waiver cards**,
Helm's next small honest move is not another pillar.
It is one shell-owned **resolution witness** family with tiny **closure cards**.

Exception witnesses answer **are we moving under a bypass, waiver, pause, or downtime instead of genuine satisfaction?**
Resolution witnesses answer **how did this tracked thing actually end?**

That is now the clean follow-on because current tools keep proving the same ordering law:
first separate promise from compliance,
then separate compliance from explicit exception,
then separate exception from typed ending class,
and never let `closed`, `archived`, `resolved`, or `duplicate` quietly collapse into one universal done badge.
Without that,
compact chrome still lies by treating one old ending record as though the subject is fixed forever, globally clean, or impossible to return.

### New shared law warming beside resolution witnesses

A compact shell surface increasingly needs to keep apart:
- source outcome truth
- attention truth
- chosen stance truth
- revisit truth
- commitment truth
- exception truth
- resolution truth
- and current-live truth

That is the practical reason to keep **resolution witnesses** and tiny **closure cards** nearby instead of laundering `closed`, `fixed`, `duplicate`, `not planned`, `archived`, `resolved in next release`, `reopened`, and `regressed` into one final badge.

## New cross-pillar ratchet after retreat witnesses

The next pressure point now looks like **succession truth**.
Helm has grown better at saying what changed, what counted, what was covered, what stayed quiet, what was delivered, what stance was chosen, when it should come back, what was promised, what was excepted, how it ended, what exact smaller slice remains, what local residue did not travel, and what kind of retreat happened.

What it still needs more clearly is one shell-owned way to say:
- who currently has the baton
- how the baton moved
- whether the stronger lane or policy survived the relay
- whether the baton is shared, queued, pending acceptance, returned, or expired
- and what exact next renew / reclaim / wait / override path is honest

That is why `succession witnesses` and `baton cards` now look like the next cross-pillar ratchet worth warming into proof slices.
They make Helm more humane without adding another pillar or another assignment dashboard.

## New pressure from rev0143: branch decks, freshness lamps, and live inspectors after settlement witnesses

The next high-value harvest now looks less like a new witness family and more like a **cross-pillar cluster**.
Helm should increasingly cultivate:
- **query witnesses** so saved search/view posture stays explicit
- **smart decks** so saved criteria and frozen result sets stop hiding inside generic views
- **live inspector decks** so observe-versus-act posture stays honest
- **checkpoint branches** so exploration can stay real without mutating mainline truth in place
- **freshness lamps** so compact surfaces confess stale, lagged, snapshot-only, or recheck-required posture
- **local analytics sidecars** so Helm can answer rich recall/ops questions quickly without pretending derived analysis is canonical live truth

The practical law is simple:
Helm should get more luxurious by separating **saved**,
**live**,
**branch**,
**historical**,
**derived**,
and **adopted-mainline** posture more clearly,
not by hiding them inside one giant deck/search/history center.


A wider product judgment now looks ready after the health/use/publish and contract passes too: Helm should keep warming one adjacent **semantic + serving honesty** cluster beside the deck/brief work. The key luxury is not another giant semantic center. It is the ability for a shell-owned reviewed slice or smart deck to reveal one semantic recipe card, one serve-path strip, one explicit `as-of` footing marker, and one bounded validator rail so recipe truth, served-answer truth, validation truth, and current live source truth stay visibly different.
## New pressure from rev0148

Helm now benefits from one compact **replay capsule / variance card / compare-lane** layer beside semantic recipe cards, serve-path strips, and validator rails so the shell can keep these truths separate:
- the exact source slice or brief being compared,
- the exact replay request and alternate footing,
- the current compare lane or branch,
- the resulting compared answer,
- and the later adopt / publish / merge / discard decision.

That should make reviewed slices and smart decks much more trustworthy without letting `refresh`, `rerun`, `fork`, `current inputs`, `version pin`, or `collaborative session` quietly impersonate current live shell truth.


## New pressure from rev0151

Helm now benefits from one compact **action-fit / fresh-intent** layer beside semantic recipe cards, serve-path strips, replay capsules, watch posture, and owner/coverage truth so the shell can keep these truths separate:
- this slice is fit to inspect, brief, or triage,
- this stronger publish or act rung still needs fresher footing,
- this stronger move is blocked or narrowed by an access verdict,
- this stronger move still needs recent local intent,
- and this visible answer came from live-direct, cached, precomputed, frozen, or replayed footing.

That should make reviewed slices and smart decks much more usable without letting verified, official, reviewed, or certified chrome quietly impersonate operator-grade truth.

## New pressure from rev0162: basis explorers, rule-insight cards, guarded promotion ladders, and patrol decks

The next cross-pillar luxury cluster now looks more concrete after the calibration pass.
Helm does not need another pillar.
It increasingly needs four tiny linked answers:
- what exact footing is this surface standing on?
- why would the stronger move pass or fail on that footing?
- what promotion rung are we on right now?
- what bounded patrol route should carry the revisit through compare and settlement later?

That is why **basis explorers**,
**rule-insight cards**,
**guarded promotion ladders**,
and **patrol decks** now look like the brightest near-term harvest.
They make the pillars feel more amazing without collapsing preview into authority,
without inventing one giant workflow center,
and without turning a deck or summary into a second truth system.
