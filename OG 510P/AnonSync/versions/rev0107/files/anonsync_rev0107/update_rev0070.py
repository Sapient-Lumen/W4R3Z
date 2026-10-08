from pathlib import Path
import re

root = Path('/tmp/anonsync_rev')

def read(rel):
    return (root / rel).read_text()

def write(rel, text):
    (root / rel).write_text(text)

# README
p = root / 'README.md'
text = p.read_text()
text = text.replace('- Revision: `rev0069`\n- Timestamp: `2026.03.17.17.10` (America/New_York)\n- Codename: `parityproofsurfaceanchor`\n',
                    '- Revision: `rev0070`\n- Timestamp: `2026.03.17.17.27` (America/New_York)\n- Codename: `seatproofreachharbor`\n')
text = re.sub(r"## What changed in this revision\n\n.*?\n## Current conclusion",
"""## What changed in this revision

This revision continues directly from `rev0069` and does seven things:

1. Re-checks **Resilio Sync** again with extra emphasis on runtime seat drift: current docs still let current-user, Local System, Local Service, service/config mode, and Linux headless operation open materially different path/state worlds.
2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let a profile or principal switch silently change which state root is active, which targets are reachable, or whether freshness falls back to rescan-only on a workaround path.
3. Adds a dedicated **execution-seat and runtime-profile reachability review spec** so the archive now says what a real operator surface must literally show before switching runtime principal, service seat, or host-local path view.
4. Extends the **interface and daemon/API contract** with explicit execution-seat objects and reviewed seat-switch cases rather than treating service-account and install-mode changes as launch trivia.
5. Extends the **workbench/interface pattern language** so current seat, target seat, path reachability, and notification/freshness downgrade are visible before apply.
6. Adds additional **canonical interface flows** for switching from an interactive user seat to a service-style seat without silently losing inventory, path reachability, or freshness truth.
7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep runtime-seat continuity explicit.

## Current conclusion""", text, count=1, flags=re.S)
anchor = '- a fixed channel-parity review pane that renders requested action, semantic parity, channel degradation, safe handoff, apply continuity, and receipt promise in the same order across GUI, TUI, CLI, and API-backed automation\n'
insert = anchor + '- a first-class execution-seat object so the product can distinguish service profile, runtime principal, visible path world, and freshness/notification posture on one host\n- a fixed execution-seat review pane that renders requested seat switch, root/identity continuity, reachability delta, freshness/substrate delta, fallout/actions, and receipt promise in the same order across GUI, TUI, CLI, and API-backed automation\n'
text = text.replace(anchor, insert)
text = text.replace('- `docs/82-safety-critical-channel-parity-and-surface-capability-spec.md` — fixed channel-parity review anatomy for requested action, semantic parity, current-channel degradation, safe handoff, and durable handoff receipts\n',
                    '- `docs/82-safety-critical-channel-parity-and-surface-capability-spec.md` — fixed channel-parity review anatomy for requested action, semantic parity, current-channel degradation, safe handoff, and durable handoff receipts\n- `docs/83-execution-seat-and-runtime-profile-reachability-spec.md` — fixed execution-seat review anatomy for runtime-principal/service-seat switch, state continuity, reachable-target delta, notification/freshness downgrade, and seat-switch receipts\n')
text = text.replace('then `81-target-custody-and-exclusive-bind-review-spec.md`, then `82-safety-critical-channel-parity-and-surface-capability-spec.md`, then `41-report-and-intervention-language.md`',
                    'then `81-target-custody-and-exclusive-bind-review-spec.md`, then `82-safety-critical-channel-parity-and-surface-capability-spec.md`, then `83-execution-seat-and-runtime-profile-reachability-spec.md`, then `41-report-and-intervention-language.md`')
p.write_text(text)

# Status rewrite
status = """# Status

## Scope of this revision

This revision is an in-place continuation of `rev0069`, driven by the current request:

- continue research and tighten the archive without letting it sprawl
- evaluate Resilio Sync further with enough care that the non-clone case stays evidence-based
- spend more time on interface specs rather than letting runtime-seat truth hide inside install modes, service accounts, or startup flags
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless evidence truly breaks them
- keep turning support-lore seams into explicit product contracts
- make sure the archive has a better reason not to clone current-user/service/Local-System/config-mode drift as though the same host necessarily remains the same control world
- make sure state-root continuity, visible path reachability, and notification/freshness downgrade survive profile/principal switches as first-class review state instead of troubleshooting ritual

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a deeper Resilio-derived warning that service-account and install-mode changes still blur together state continuity, path reachability, notification quality, and clean-versus-migrated runtime worlds
- a dedicated **execution-seat and runtime-profile reachability spec** that says what a real operator surface must show before switching runtime principal, service seat, or path world
- stronger interface and daemon/API requirements so execution seats and seat-switch reviews become explicit public objects rather than launch trivia
- stronger workbench and pattern-language rules so operators can see current seat, target seat, path-loss risk, freshness downgrade, and fallout before apply
- additional canonical flows for switching from an interactive seat to a service-style seat without silently losing state, inventory, or freshness truth
- roadmap, ADR, status, open-question, and README updates so future revisions keep runtime-seat continuity explicit

## The main shift

`rev0069` proved that channel changes needed one explicit capability/handoff contract rather than degraded-client folklore.

`rev0070` applies the same discipline one layer deeper inside the same host:

> a serious Linux-first workbench still is not specified tightly enough if the archive can define state roots, service profiles, bring-up review, mutation gates, and channel parity, yet still leave the next hard question loose: whether switching runtime principal or service seat preserves the same state world, the same path reachability, and the same freshness guarantees.

That changes the archive in six specific ways:

- runtime/service-seat switching is now treated as explicit continuity and reachability review rather than background execution detail
- current-user, Local System, Local Service, maintenance, and similar seats can no longer be presented as the same host truth without proof
- path visibility and write reachability are now separated from mere path strings that happen to look reusable in another seat
- notification/freshness downgrade such as UNC or rescan-only posture must now be visible before apply rather than discovered later through support lore
- the Resilio comparison now lands a sharper non-clone argument: the weak seam is not merely browser brittleness, but the lack of one honest reviewed boundary between profile/principal change and host-local world change
- future interface work now has a narrower quality bar for service installs, maintenance shells, local web workbenches, and Linux/headless control

## What still remains unresolved

This revision intentionally does **not** overclaim closure on several important questions:

- how much of transport identity and overlay publication should be device-wide, share-scoped, or policy-scoped
- how strong disclosure-narrowing guarantees should be before the product becomes noisy or dishonest about residue
- how aggressive the default review queue should be before it becomes noisy
- how much UI simplification is safe without recreating the hidden coupling the archive is trying to escape
- how much one-click automation an exit surface should allow before it starts hiding scope, residue, or follow-up obligations
- how aggressive default compromise freezes should be before the product starts turning suspicion into disruptive magic
- when long-offline or clock-uncertain peers should be allowed to resume writable participation without first-class re-entry review
- when remote delete or overwrite waves should always force destructive-replay review instead of ordinary sync progress
- when non-trivial conflicts should always force full reviewed adjudication instead of a safely compressed resolution path
- when same-host derivations should always force full local-derivation review instead of a safely compressed path
- when live authority changes should always force full authority-mutation review instead of a safely compressed access-change path
- when nested, overlapping, or root-boundary-sensitive topology changes should always force full topology review instead of a safely compressed path
- when writer contention, burst-save delay, or mixed external-writer risk should always force full contention review instead of a safely compressed path
- when RAM pressure, watcher ceilings, indexing cost, or path blockers should always force full capacity-fit review instead of a safely compressed path
- when discovered state, recovery material, or reviewed control exposure should always force full bring-up review instead of a safely compressed startup path
- how broad one reviewed mutation grant may be in v1 before explicit authority becomes either too reusable or too noisy
- when an obviously same-lineage local target may use a safely compressed custody review versus always opening the full ownership-and-lineage sheet
- how much low-risk cross-channel continuation may stay compressed before channel-parity honesty becomes either noisy or too magical
- how much low-risk runtime-seat switching may stay compressed before state continuity, path reachability, and freshness honesty become either noisy or too magical

## Files added in this revision

- `docs/83-execution-seat-and-runtime-profile-reachability-spec.md`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/30-interface-spec.md`
- `docs/31-daemon-api-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/64-critical-open-questions.md`
"""
write('docs/00-status.md', status)

# Evaluation insert
p = root / 'docs/10-resilio-sync-evaluation.md'
text = p.read_text()
insert = """
### 16ab) Runtime-seat changes still depend too much on install mode, service account, and mapped-path folklore

One more Resilio pass exposes a distinct same-host seam.

`Running Sync as a service on Windows` says the service can run as current user, `Local System`, or `Local Service`, and that install choices split into migrated state versus clean installation.
`Sync Service Troubleshooting on Windows` says mapped drive letters are unavailable to the service because services do not receive interactive logon mapping, that the UNC workaround loses file-update notifications and falls back to full rescan or restart, and that switching the service to `Local System` opens a different storage folder with no prior shares visible until the operator re-adds and re-shares them.
`Sync Storage folder` separately says the storage path changes again by service account.
`Guide to Linux, and Sync peculiarities` adds that Linux has no OS integration and requires more manual configuration than desktop seats.

That combination is revealing.
The same machine can still present materially different control worlds depending on which runtime seat is active:

- whether the same durable state root is still open or a different storage root silently became active
- whether the same target paths are even reachable from this seat
- whether path access now depends on degraded UNC or similar workaround rather than native local semantics
- whether change detection remains continuous or has silently degraded to rescan-only best effort
- whether the honest next step is preserve same state, migrate with reviewed rebind, or admit that this is really a clean-seat start

AnonSync should not clone that shape.
A serious operator surface should instead publish one execution-seat and seat-switch model with:

- one explicit execution-seat object describing service profile, runtime principal, visible path world, and notification/freshness posture
- one reviewed seat-switch case describing requested continuity intent, reachable-target delta, freshness/substrate downgrade, and fallout
- explicit difference between `same root / same seat-class`, `same root / new principal`, `same state but rebind required`, and `clean-seat start`
- explicit receipts proving whether a switch preserved inventory truth or deliberately opened a different runtime world

### Requirement 66 — runtime-principal and service-seat changes must share one reviewed continuity/reachability contract

If the operator still has to combine install-mode choices, service-account changes, missing mapped drives, UNC workarounds, storage-folder lore, and re-add/re-share ritual to answer “am I still operating the same state world, what paths did I lose, and did freshness degrade?”, the product has not actually exposed its execution-seat contract.

AnonSync should instead publish one public model with explicit execution-seat objects, explicit seat-switch reviews, explicit path-reachability and notification/freshness deltas, explicit migrated-state versus clean-seat outcomes, and durable seat-switch receipts that preserve the difference between continuity-preserving runtime change, reviewed rebind, and honest fresh runtime world.

## Where Resilio is still probably the better choice
"""
text = text.replace('## Where Resilio is still probably the better choice\n', insert)
p.write_text(text)

# Interface spec insert
p = root / 'docs/30-interface-spec.md'
text = p.read_text()
text = text.replace("""### Service profile

A named runtime context that opens or manages a state root.
This exists so background service, local web workbench, recovery CLI, and workstation invocation can differ in runtime posture without silently differing in semantics.

Fields:

- `service_profile_id`
- `name`
- `mode` (`workstation`, `background-service`, `local-web`, `maintenance`, `recovery-cli`)
- `user_context`
- `listen_policy`
- `mutation_capabilities[]`
- `state_root_policy` (`must-attach-explicitly`, `may-create-empty`, `read-only-only`, `single-known-root`)
- `created_at`
- `last_used_at` nullable
- `provenance_ref` nullable


### Bring-up case""",
"""### Service profile

A named runtime context that opens or manages a state root.
This exists so background service, local web workbench, recovery CLI, and workstation invocation can differ in runtime posture without silently differing in semantics.

Fields:

- `service_profile_id`
- `name`
- `mode` (`workstation`, `background-service`, `local-web`, `maintenance`, `recovery-cli`)
- `user_context`
- `listen_policy`
- `mutation_capabilities[]`
- `state_root_policy` (`must-attach-explicitly`, `may-create-empty`, `read-only-only`, `single-known-root`)
- `created_at`
- `last_used_at` nullable
- `provenance_ref` nullable

### Execution seat

A concrete host-local runtime seat combining service profile, principal context, path world, and notification substrate.
This exists so switching between current-user, service-style, maintenance, or recovery seats cannot silently change what the operator is actually touching.

Fields:

- `execution_seat_id`
- `service_profile_ref`
- `principal_class` (`interactive-user`, `named-service-user`, `local-system`, `local-service`, `maintenance-shell`, `recovery-shell`, `container-service`, `unknown`)
- `principal_label`
- `state_root_ref` nullable
- `reachable_mount_roots[]`
- `path_resolution_mode` (`interactive-mapped`, `direct-local`, `unc-reviewed`, `namespace-scoped`, `container-mapped`, `unknown`)
- `notification_posture` (`native`, `degraded`, `rescan-only`, `none`, `unknown`)
- `control_channel_set[]`
- `mutation_capabilities[]`
- `last_verified_at` nullable
- `provenance_ref` nullable

### Bring-up case""")
text = text.replace("""### State transition plan

A reviewed mutation covering root attach/move/export/import/profile-switch or identity-root replacement.
This exists so those transitions are not implicit process behavior.

Fields:

- `state_transition_plan_id`
- `transition_type` (`attach`, `move-root`, `switch-profile`, `replace-identity-root`, `export-state`, `import-state`)
- `source_state_root_ref` nullable
- `target_state_root_ref` nullable
- `source_service_profile_ref` nullable
- `target_service_profile_ref` nullable
- `state_transition_report_ref`
- `preflight_report_ref` nullable
- `preservation_report_ref` nullable
- `quiesce_required`
- `rollback_strategy`
- `generated_at`
- `expires_at` nullable

### Plan""",
"""### State transition plan

A reviewed mutation covering root attach/move/export/import/profile-switch or identity-root replacement.
This exists so those transitions are not implicit process behavior.

Fields:

- `state_transition_plan_id`
- `transition_type` (`attach`, `move-root`, `switch-profile`, `replace-identity-root`, `export-state`, `import-state`)
- `source_state_root_ref` nullable
- `target_state_root_ref` nullable
- `source_service_profile_ref` nullable
- `target_service_profile_ref` nullable
- `state_transition_report_ref`
- `preflight_report_ref` nullable
- `preservation_report_ref` nullable
- `quiesce_required`
- `rollback_strategy`
- `generated_at`
- `expires_at` nullable

### Execution-seat review

A durable, reviewed case for switching runtime principal or service seat without guessing whether the same host still means the same state/path world.

Fields:

- `execution_seat_review_id`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `requested_intent` (`preserve-state-and-reachability`, `preserve-state-accept-path-loss`, `migrate-with-rebind`, `clean-seat-start`, `inspect-target-seat`)
- `continuity_expectation` (`same-root-same-identity`, `same-root-new-principal`, `same-root-rebind-required`, `new-root-clean-seat`, `inspect-only`)
- `reachability_findings[]`
- `freshness_findings[]`
- `fallout_findings[]`
- `action_options[]`
- `seat_transition_report_ref`
- `generated_at`
- `expires_at` nullable

### Execution-seat receipt

A durable record proving whether a reviewed runtime-seat change preserved state continuity, degraded reachability/freshness, required rebind, or opened a clean runtime world.

Fields:

- `execution_seat_receipt_id`
- `review_ref`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `continuity_summary`
- `reachability_summary`
- `freshness_summary`
- `outcome_summary`
- `actor_ref`
- `created_at`

### Plan""")
p.write_text(text)

# API spec updates
p = root / 'docs/31-daemon-api-spec.md'
text = p.read_text()
text = text.replace("""GET  /v1/state
GET  /v1/state/roots
GET  /v1/state/roots/{state_root_id}
POST /v1/state/roots:verify
POST /v1/state/roots:attach
POST /v1/state/roots:move
GET  /v1/service-profiles
GET  /v1/service-profiles/{service_profile_id}
POST /v1/service-profiles/{service_profile_id}:prepare-switch
POST /v1/state/export
POST /v1/state/import""",
"""GET  /v1/state
GET  /v1/state/roots
GET  /v1/state/roots/{state_root_id}
POST /v1/state/roots:verify
POST /v1/state/roots:attach
POST /v1/state/roots:move
GET  /v1/service-profiles
GET  /v1/service-profiles/{service_profile_id}
POST /v1/service-profiles/{service_profile_id}:prepare-switch
GET  /v1/execution-seats
GET  /v1/execution-seats/{execution_seat_id}
POST /v1/execution-seats/{execution_seat_id}:prepare-switch
POST /v1/state/export
POST /v1/state/import""")
text = text.replace('These resources exist so storage-root choice, runtime-profile choice, and root transition work do not hide behind launch flags or installer behavior.',
                    'These resources exist so storage-root choice, runtime-profile choice, host-local execution-seat choice, and root transition work do not hide behind launch flags, service-account changes, or installer behavior.')
text = text.replace("""- active service profile
- identity fingerprint summary
- last verification time""",
"""- active service profile
- active execution seat summary
- identity fingerprint summary
- last verification time""")
text = text.replace("""A profile-switch preparation response should answer at least:

- whether the target profile would open the same active root
- whether the target profile has enough privileges to manage that root
- whether local control-surface listen posture would change
- whether mutation capabilities narrow or widen
- whether quiesce/restart is required
""",
"""A profile-switch preparation response should answer at least:

- whether the target profile would open the same active root
- whether the target profile has enough privileges to manage that root
- whether local control-surface listen posture would change
- whether mutation capabilities narrow or widen
- whether path reachability or path-resolution mode would change
- whether notification/freshness posture would degrade, for example to rescan-only
- whether the result still counts as migrated state or really becomes a clean-seat start
- whether quiesce/restart is required

An execution-seat switch response should answer at least:

- the current seat and target seat, including principal class and service-profile relation
- whether the same state root and identity stay active, become inspect-only, or require explicit rebind
- which currently known targets become unreachable, remapped, or downgraded to reviewed workaround posture
- whether notification/freshness posture stays native, degrades, or becomes unknown
- what fallout is expected next: none, rebind, narrow-to-inspect, or clean-seat start
- which receipt will later prove the chosen outcome
""")
p.write_text(text)

# Flows append
p = root / 'docs/32-interface-flows.md'
text = p.read_text()
append = """

## Flow 121 — review switching from an interactive seat to a service-style seat without pretending the same host is the same world

Problem: an operator wants to move an existing workstation-managed node into a background-service seat so it survives logout. The product must explain whether the same state root stays active, whether previously visible paths remain reachable, and whether any path now falls back to degraded notification or rescan-only posture.

Goal:

- prove that service-account or runtime-seat switching is a reviewed continuity/reachability decision, not install folklore
- keep state continuity, path loss, and freshness downgrade visible before apply

Workbench expectations:

- choosing `Run as background service` from the System State page first opens `Review execution seat`
- the page renders sections in this order:
  1. requested seat switch and continuity intent
  2. state root and identity continuity
  3. reachable-target delta
  4. freshness and substrate delta
  5. fallout and admissible actions
  6. receipt promise
- if some targets would only survive through degraded workaround posture, the primary action becomes `Prepare reviewed rebind` or `Keep current seat`, not a generic `Install service`

CLI expectations:

```text
$ anonsync state seat show esr_01J... --view review
Execution-seat review
---------------------
1. Requested seat switch and continuity intent
   Source seat: workstation / interactive-user
   Target seat: background-service / local-system
   Requested intent: preserve-state-and-reachability

2. State root and identity continuity
   Active state root: /home/jane/.config/anonsync/root-a
   Continuity expectation: same-root-new-principal
   Result if applied now: guarded — target seat would not reopen this root without explicit attach

3. Reachable-target delta
   Lost path: Z:\\team-share\\ledger
   Reason: mapped drive exists only in interactive seat
   Reviewed fallback: UNC path \\\\nas\\team-share\\ledger requires explicit rebind

4. Freshness and substrate delta
   Current posture: native notifications
   Target posture for fallback path: rescan-only
   Reason: target seat cannot rely on direct change notifications for reviewed workaround path

5. Fallout and admissible actions
   Safe actions: keep current seat / prepare rebind / create clean service seat
   Blocked shortcut: switch seats and preserve all current targets automatically

6. Receipt promise
   Receipt will prove continuity choice, lost or rebound targets, freshness downgrade, and final seat outcome.
```

Expected operator answers from CLI alone:

- whether the target seat really preserves the same state root or needs explicit attach/rebind
- which current targets vanish or degrade under the new seat
- whether freshness remains native or falls back to reviewed rescan-only posture
- whether the honest next step is keep current seat, rebind carefully, or start a clean service seat

## Flow 122 — render the same execution-seat review in CLI and workbench without semantic drift

Problem: a browser/workbench operator previews a switch into a service-style seat; later a headless operator inspects the same review over SSH before applying it. Both surfaces must show the same continuity, reachability, freshness, fallout, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed execution-seat case
- make service-seat switching read like one product instead of one installer path plus one pile of troubleshooting lore

Cross-surface success criteria:

- both surfaces answer the same question: **if I change runtime seat on this host, am I still operating the same state world, which targets or guarantees change, and what reviewed fallout follows?**
- neither surface falls back to generic `run as service`, `switch account`, or `re-share folders` language when the real decision is a reviewed continuity/reachability change
"""
text += append
p.write_text(text)

# Workbench spec updates
p = root / 'docs/38-operator-workbench-interface-spec.md'
text = p.read_text()
text = text.replace('- active service profile and user context\n', '- active service profile, execution seat, and user/principal context\n- current path-reachability and notification posture summary\n')
text = text.replace('- prepare profile switch\n', '- prepare profile switch\n- prepare reviewed execution-seat switch\n')
anchor = """No mutation on this page should bypass a report or plan.


## Target-custody and exclusive-bind surface"""
insert = """No mutation on this page should bypass a report or plan.

## Execution-seat and runtime-profile switch surface

The workbench should expose one dedicated surface whenever a runtime/service-seat change could alter what the same host can actually see or manage: current-user to background service, named-service user to Local System, maintenance or recovery seat, containerized seat, or any switch that weakens notification quality or path reachability.
This page is not installer garnish.
It is where the product proves that `same state, same world`, `same state, rebind required`, `same state but degraded freshness`, and `clean-seat start` are different outcomes.

The page should show at least:

- source seat and target seat with service-profile and principal class
- current state-root/identity continuity expectation
- reachable-target delta and any path-resolution workaround posture
- notification/freshness delta and any rescan-only downgrade
- admissible actions and recent seat-switch receipts

Its primary actions should be:

- keep current seat
- prepare reviewed same-root switch
- prepare reviewed rebind for affected targets
- open a clean-seat start intentionally
- inspect why the switch is blocked or guarded

No mutation on this page should bypass a report, plan, or receipt.

## Target-custody and exclusive-bind surface"""
text = text.replace(anchor, insert)
p.write_text(text)

# Pattern language insert
p = root / 'docs/39-interface-pattern-language.md'
text = p.read_text()
anchor = """If a profile switch, attach, or move can make shares appear or disappear without an explicit receipt, the interface has failed this pattern.


## Pattern 17 — transfer cards must answer route, budget, and queue truth"""
insert = """If a profile switch, attach, or move can make shares appear or disappear without an explicit receipt, the interface has failed this pattern.

## Pattern 16a — execution-seat switches must show reachability and freshness delta before apply

A service-account or runtime-seat change on one host is not merely a startup convenience.
It can change which state root opens, which paths remain reachable, and whether notifications stay native.

Required rules:

- switching user, service seat, maintenance seat, or container seat must say whether the same state root and identity remain active
- any target that becomes unreachable, remapped, or downgraded to reviewed workaround posture must be visible before apply
- freshness/notification downgrade such as `native -> rescan-only` must be shown as semantic fallout, not hidden inside later troubleshooting
- `migrated state`, `same state with rebind`, and `clean-seat start` must remain visibly different outcomes

This matters because a product can define good state-root and service-profile objects on paper and still regress in practice if `run as service`, `switch account`, or `open as system` silently changes the host-local world.

## Pattern 17 — transfer cards must answer route, budget, and queue truth"""
text = text.replace(anchor, insert)
p.write_text(text)

# ADR append
p = root / 'docs/40-architecture-decisions.md'
text = p.read_text()
text += """

## ADR-083 — Runtime-principal and service-seat changes need one reviewed continuity/reachability contract, not install-mode folklore

**Decision:** Non-trivial execution-seat changes should compile to one reviewed continuity/reachability model rather than depending on installer choices, service-account switching, mapped-drive caveats, UNC workarounds, or re-add/re-share ritual.

**Why:** Current Resilio docs still spread same-host runtime truth across current-user vs Local System / Local Service service modes, migrated-state vs clean install choices, mapped-drive invisibility for services, UNC fallback with degraded notifications, and storage roots that vary by service account. AnonSync should keep state continuity, reachable-target delta, notification/freshness posture, and clean-seat-versus-migrated outcome visible in one place.

**Consequences:**

- execution-seat work gains a stable review grammar and durable seat-switch receipts
- workbench and CLI both need explicit continuity, reachability, freshness, and fallout sections for runtime-seat changes
- service installs or principal switches can no longer masquerade as harmless backgrounding when they actually alter the host-local world
- degraded workaround posture such as rescan-only rebinds remains visibly distinct from true same-seat continuity
"""
p.write_text(text)

# Roadmap updates
p = root / 'docs/50-roadmap.md'
text = p.read_text()
text = text.replace('- state-root, state-snapshot, service-profile, and state-transition-plan object model\n',
                    '- state-root, state-snapshot, service-profile, and state-transition-plan object model\n- execution-seat, seat-switch-review, and seat-switch-receipt object model\n')
text = text.replace('- operators can tell whether first open is fresh, attached, recovered, successor-sensitive, or blocked without inferring it from startup flags or installer folklore\n',
                    '- operators can tell whether first open is fresh, attached, recovered, successor-sensitive, or blocked without inferring it from startup flags or installer folklore\n- operators can tell whether switching runtime principal or service seat preserves the same state world, target reachability, and freshness guarantees or instead requires reviewed rebind or clean-seat start\n')
text = text.replace('- review-model projection for bring-up and first control entry so rich and textual clients render the same continuity and exposure sections\n',
                    '- review-model projection for bring-up and first control entry so rich and textual clients render the same continuity and exposure sections\n- review-model projection for execution-seat and runtime-profile switching so rich and textual clients render the same continuity, reachability, and freshness sections\n')
p.write_text(text)

# Open questions append
p = root / 'docs/64-critical-open-questions.md'
text = p.read_text()
text += """

## 51) How much low-risk runtime-seat switching can stay compressed before continuity/reachability honesty becomes either noisy or too magical?

The archive is now clearer that current-user, service-style, Local System, maintenance, and similar execution seats should use first-class reviewed seat-switch cases and receipts, but one policy seam remains open:

- when should a same-root runtime switch be allowed to stay compressed because no reachable targets or freshness guarantees change
- whether any target loss should always force full seat-switch review instead of a lighter acknowledgement
- when rescan-only or other degraded workaround posture is acceptable versus always blocked for the requested intent
- how much automatic rebind help is safe before the product starts hiding the difference between continuity and a different host-local world

This matters because weak defaults recreate service-account, mapped-drive, and UNC folklore, while overly strict defaults could make harmless backgrounding or maintenance-seat changes feel ceremonial instead of trustworthy.
"""
p.write_text(text)

# New spec
newdoc = """# Execution-seat and runtime-profile reachability spec

The archive already has state roots, service profiles, bring-up review, mutation gates, target custody, and channel parity.
This document answers the narrower practical question those abstractions still left open:

> what must a real operator surface literally show when the same host changes runtime principal or service seat, so AnonSync does not drift back into current-user vs service-account folklore, mapped-drive surprises, UNC workaround magic, or `my shares disappeared` archaeology?

This is the execution-seat companion to `42-state-root-and-service-profile-spec.md`, the runtime-world companion to `78-bringup-and-control-entry-interface-spec.md`, and the host-local continuity companion to `82-safety-critical-channel-parity-and-surface-capability-spec.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Running Sync as a service on Windows` says the service can run as current user, `Local System`, or `Local Service`, and that installation can migrate existing state or create a clean service install.
`Sync Service Troubleshooting on Windows` says mapped drive letters are unavailable to the service because services do not receive interactive logon mapping, that the UNC workaround loses immediate file-update notifications and falls back to rescan or restart, and that switching the service to `Local System` opens a different storage folder with no old shares visible until the operator re-adds and re-shares them.
`Sync Storage folder` separately says the storage path differs by service account.
`Guide to Linux, and Sync peculiarities` adds that Linux has no OS integration and needs more manual runtime setup.

The lesson is not merely that services are annoying.
The lesson is that a useful product can still leave one of the most dangerous host-local questions under-specified:

- am I still opening the same durable state, or did a different storage root silently become active?
- can this runtime seat still reach the same targets, or do some paths exist only in the previous seat?
- did a workaround preserve the same local semantics, or did freshness quietly degrade to rescan-only best effort?
- is this really `background the same node`, or is it `start a different local world and reconnect it by hand`?

AnonSync should not clone that shape.

## Core rule

Every runtime/service-seat change should have one server-declared continuity identity and one review identity.
A switch may be:

- same root / same reachable world
- same root / reachable world narrowed
- same root / reviewed rebind required
- clean-seat start
- inspect-only / blocked

A switch may not silently redefine the active state universe, hide path loss behind a successful service start, or claim continuity when freshness guarantees materially degraded.

## Which actions are in scope

This spec is primarily about host-local runtime changes whose meaning cannot be allowed to hide in launch ritual.
That includes at least:

- workstation -> background service
- current-user service -> `Local System` or `Local Service`
- named service user -> another named service user
- maintenance or recovery seat entry that opens or inspects current state
- containerized / namespace-scoped seat changes
- any switch where target reachability, root visibility, or notification posture changes

Low-risk same-seat restart can stay lighter.
High-signal seat changes cannot.

## Vocabulary

### Execution seat

An execution seat is the concrete host-local runtime seat through which the daemon operates.
It combines:

- service profile
- runtime principal / user or service account
- path world and mount namespace
- notification substrate and freshness posture
- control-surface set and mutation capability posture

The point of the seat is not branding.
It is to make the practical host-local world inspectable.

### Seat-switch review

A reviewed case that answers whether changing execution seat preserves the same durable state, the same reachable targets, and the same freshness guarantees.

### Seat-switch receipt

A durable record proving what runtime seat change was actually applied, what continuity was preserved, and what fallout remained.

## Fixed review order

Every non-trivial execution-seat review should render the same sections in the same order:

1. **Requested seat switch and continuity intent**
2. **State root and identity continuity**
3. **Reachable-target delta**
4. **Freshness and substrate delta**
5. **Fallout and admissible actions**
6. **Receipt promise**

### 1) Requested seat switch and continuity intent

This section should show:

- source seat and target seat
- requested intent (`preserve same node`, `background it`, `inspect only`, `clean service start`, `migrate with rebind`)
- whether the action is low-risk restart, guarded switch, or high-signal local-world change
- which review family owns the action (`seat-switch`, `bringup`, `successor`, `other`)

The operator must be able to answer: **what runtime world am I leaving, what one am I trying to enter, and what continuity story am I asking the product to preserve?**

### 2) State root and identity continuity

This section should show:

- whether the same state root remains open, needs explicit attach, or would be replaced
- whether identity continuity remains intact, becomes inspect-only, or would require successor/recovery handling
- whether the target seat widens or narrows mutation capability compared with the source seat
- whether the action is still `same node under a new seat` or really `new node / new root`

The operator must be able to answer: **am I still operating the same durable node, or did the runtime change cross into a different state universe?**

### 3) Reachable-target delta

This section should show:

- which currently known targets remain reachable from the target seat
- which paths become unreachable, remapped, or require reviewed workaround posture
- whether path strings are merely visible versus writable and watchable from the target seat
- whether any existing bind or target-custody assumption must be reopened

The operator must be able to answer: **what local targets, mounts, or path classes change meaning under the new seat?**

### 4) Freshness and substrate delta

This section should show:

- whether notification posture stays native, becomes degraded, or falls to rescan-only
- whether the path-resolution mode changes (`direct-local`, `mapped`, `UNC`, `namespace-scoped`, other)
- whether any workaround weakens settlement, readiness, or writer-contention truth
- whether the requested action still satisfies the original freshness promise

The operator must be able to answer: **did continuity preserve only bytes, or did it also preserve the quality of local truth?**

### 5) Fallout and admissible actions

This section should show:

- whether the honest next step is switch now, prepare rebind, narrow to inspect-only, or open a clean-seat start
- whether target-custody, bring-up, or capacity/fidelity review must reopen
- whether some targets must be deliberately dropped or converted before the switch can remain honest
- what shortcuts are blocked because they would hide state/path/freshness loss

The operator must be able to answer: **what must I do next to keep this runtime change truthful?**

### 6) Receipt promise

This section should show:

- which seat-switch receipt will exist after apply, defer, or refusal
- what it will later prove about source seat, target seat, continuity outcome, reachability delta, freshness delta, and follow-up obligations
- whether the receipt remains provisional because rebind or later verification is still pending
- where later audit survives if the switch is resumed from another channel

The operator must be able to answer: **what later evidence will prove that this runtime change preserved continuity honestly — or that it did not?**

## Public objects

### Execution seat

Fields:

- `execution_seat_id`
- `service_profile_ref`
- `principal_class`
- `principal_label`
- `state_root_ref` nullable
- `reachable_mount_roots[]`
- `path_resolution_mode`
- `notification_posture`
- `control_channel_set[]`
- `mutation_capabilities[]`
- `last_verified_at` nullable
- `provenance_ref` nullable

### Seat-switch review

Fields:

- `execution_seat_review_id`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `requested_intent`
- `continuity_expectation`
- `reachability_findings[]`
- `freshness_findings[]`
- `fallout_findings[]`
- `action_options[]`
- `seat_transition_report_ref`
- `generated_at`
- `expires_at` nullable

### Seat-switch receipt

Fields:

- `execution_seat_receipt_id`
- `review_ref`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `continuity_summary`
- `reachability_summary`
- `freshness_summary`
- `outcome_summary`
- `actor_ref`
- `created_at`

## What the surface must never imply

The execution-seat surface must never imply that these are the same thing:

- a successful service start versus preserving the same state root
- seeing a familiar path string versus being able to write and watch that target honestly
- a UNC or namespace workaround versus the same native local semantics
- backgrounding the same node versus starting a clean seat that later reconnects manually
- principal change versus ordinary channel handoff
- missing inventory because of seat drift versus explicit reviewed detach or exit

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/headless parity rule

A Linux-first product has to assume that runtime-seat changes will be entered from SSH, service managers, maintenance shells, browser workbenches, and recovery environments.
So execution-seat truth must survive across those surfaces.
It is not acceptable for one richer surface to show continuity, reachability, and freshness delta while headless control falls back to installer choice, `systemctl` success, or path-lookup troubleshooting.

## Relationship to nearby specs

Execution-seat review should often hand off to nearby review families, but it should not dissolve into them.

- **State-root and service-profile work** explains the durable state and runtime objects.
  Execution-seat review explains whether switching seat preserves the same practical host-local world.
- **Bring-up review** explains whether first open is fresh, attached, recovered, or blocked.
  Execution-seat review explains whether a runtime change is still continuity-preserving or really a new-world bring-up.
- **Target-custody review** explains who already owns one path.
  Execution-seat review explains whether that path remains reachable or honest under the new seat.
- **Channel-parity review** explains how one reviewed action survives client changes.
  Execution-seat review explains how the host-local world itself changes under the daemon.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync state seat show <execution_seat_review_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether the new seat preserves the same state, loses targets, degrades freshness, or really becomes a clean runtime world.

## Why this is worth the trouble

AnonSync only justifies its extra interface complexity if runtime changes also become easier to trust.
A fixed execution-seat grammar is how the archive avoids rebuilding a system where service-account choices, mapped-drive disappearance, UNC fallback, changed storage roots, and re-add/re-share instructions are all individually documented, yet the full meaning of `is this still the same node, and what host-local truth changed when I switched runtime seat?` still depends on which support article the operator happened to remember first.
"""
write('docs/83-execution-seat-and-runtime-profile-reachability-spec.md', newdoc)

print('update_rev0070 complete')
