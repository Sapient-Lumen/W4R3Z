## Revision addendum — daemon API after rev0253: indirection object state must be machine-readable

The daemon now owes one more class of structured record.
Any serious path inspection result should be able to expose:

- `entry_kind` (`ordinary-file`, `ordinary-folder`, `symbolic-link`, `hard-link`, `junction`, `alias-like`, `unknown-indirection`)
- `entry_object_fate` (`preserve`, `flatten`, `block`, `unsupported-conflict-prone`, `unknown`)
- `target_scope` (`inside-subject`, `outside-subject`, `unresolved`, `none`, `unknown`)
- `target_transitivity_verdict` (`included-now`, `excluded-now`, `separate-admission-required`, `cannot-prove`, `not-applicable`)
- `graph_widening_risk` (`none`, `inside-coupling-only`, `outside-subject-widening`, `unknown`)
- `conflict_hazard` (`none-known`, `possible`, `likely`, `observed`)

This exists so local UI, CLI, and receipts do not have to infer indirection truth from unstructured warnings or troubleshooting residue.

# Daemon API spec (v1 draft)

## Purpose

This document specifies the local daemon control plane that backs the CLI and any future UI/TUI.
The goal is not “have an API somewhere”; the goal is:

- one control model
- local-first administration
- stable enough machine semantics for serious tooling
- explicit events and diagnostics
- observability and audit as first-class surfaces
- previewable, explainable mutation semantics

## Transport

### Preferred local transport

On desktop/server platforms, the daemon should expose:

- a Unix domain socket on Unix-like systems
- a named pipe on Windows

This is the default control channel for local CLI interaction.

### Optional loopback HTTP

The daemon may also expose loopback HTTP for local tooling and a future web UI.
Default bind:

- `127.0.0.1:<port>` only

It must **not** listen on non-loopback interfaces by default.

## Authentication

### Local socket/pipe

Access control is primarily OS-level.
The daemon should verify the connecting user where possible.

### Loopback HTTP

Use issued access credentials rather than ambient browser state.
Support:

- `Authorization: Bearer <token>`

Interactive browser sessions may be layered on top, but they should resolve back to first-class access-token / control-session objects.
No unauthenticated mutating endpoints.

## API versioning

Base path:

```text
/v1/
```

Rules:

- additive fields are allowed in minor revisions
- existing field meaning must not silently change
- breaking changes require `/v2/`
- event type names are append-only where possible

## Mutation semantics

### Object identity

All durable objects should include:

- stable ID
- creation timestamp
- update timestamp
- monotonic `version`

### Safe updates

`PATCH` is for bounded field changes only.
High-semantics operations should use action endpoints.

Examples:

- good `PATCH`: rename a share, change a mount mode cap, toggle relay policy
- action endpoint instead of `PATCH`: replace device, rotate identity, revoke peer, clear route cache, apply plan

### List-like policy mutation

List-like policy surfaces such as ignore rules should not rely on ambiguous whole-array replacement by default.
Where an operator means “add one rule” or “remove one rule”, the API should expose item-level resources or explicit action endpoints.
This matters because raw config-patch models in other systems often replace child arrays wholesale, which is technically simple but operator-hostile.

### Idempotency

Mutating HTTP requests should accept an optional idempotency token header for local tooling.
This matters most for retries from wrappers or UI clients.

### Preconditions

High-signal mutating requests should accept version preconditions.
At minimum the API should support one of:

- `If-Match` on the target object version
- explicit `expected_version` fields in action requests
- plan-bound preconditions when applying a previously created plan

If a precondition fails, the API should return a structured drift error rather than silently applying against new state.

---

## Core resource families

### System

```text
GET  /v1/system/info
GET  /v1/system/status
GET  /v1/system/health
GET  /v1/system/status-bridge
GET  /v1/system/logs
GET  /v1/system/paths
GET  /v1/system/capabilities
POST /v1/system/rescan
POST /v1/system/shutdown
```

`GET /v1/system/status` should report at least:

- local device identity
- daemon uptime
- storage path
- active discovery/topology policy
- online peer count
- degraded share count
- open compatibility/preflight warnings count
- subjects currently carrying mixed-family or migration-blocked release posture
- pending claims count
- degraded recovery-bundle sufficiency count
- open retirement records count
- active filesystem-compatibility warnings count
- degraded convergence-report count
- active transport-session count by engine
- filesystem paths currently in blocked or warning tier
- active storage-pressure cases count
- subjects currently blocked from new materialization because of hard pressure

`GET /v1/system/health` should classify findings as:

- `ok`
- `warning`
- `critical`

`GET /v1/system/status-bridge` should expose one lightweight proof surface for everyday operator questions and should include at least:

- `bridge_verdict` (`ready`, `not-ready`, `unavailable`, `skipped-cleanly`, `degraded`, `error`, `unknown`)
- `runtime_owner_kind`
- `strongest_blocker_class`
- `current_claim_boundary`
- `bridge_probe_rows[]` with `probe_kind`, `probe_source_kind`, and `state`
- `recommended_escalation_object_kind` nullable

### Common report envelope

Many API resources produce report-shaped objects: `preflight`, `comparison`, `preservation`, `convergence`, `exposure`, filesystem-compatibility/fidelity, and plan-drift views.
Even when they live under different endpoints, they should expose a shared operator envelope containing at least:

- `report_id`
- `report_type`
- `subject_ref`
- `generated_at`
- `freshness_state` (`fresh`, `aging`, `stale`, `drifted`, `superseded`)
- `severity` (`info`, `watch`, `guarded`, `high-risk`, `blocked`)
- `current_answer`
- `scope_summary`
- `recommended_next_action` nullable
- `unresolved_after_apply[]`

Optional convenience endpoints are acceptable for cross-type operators and workbench clients:

```text
GET  /v1/reports
GET  /v1/reports/{report_id}
POST /v1/reports/{report_id}/refresh
```

These should be projections over the underlying typed report resources, not a second hidden model.

### Constellation

```text
GET  /v1/constellations
GET  /v1/constellations/{constellation_id}
GET  /v1/constellations/{constellation_id}/members
GET  /v1/constellations/members/{member_id}
PATCH /v1/constellations/members/{member_id}
GET  /v1/constellations/authority-domains
GET  /v1/constellations/authority-domains/{authority_domain_id}
GET  /v1/constellations/receipts
GET  /v1/constellations/receipts/{constellation_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without linked-device folklore:

- which devices are members of the same reviewed convenience constellation
- what class and default visibility each member carries
- whether a member may mutate, re-share, approve, or only review/adopt on a given subject
- whether a change to visibility, disconnect, or approval scope reaches one member or the wider constellation
- which receipt proves that a class, visibility, or scope boundary changed

Constellation membership should compose with contact, approval, policy, and release resources rather than shadowing them with a second hidden model.

### Subject naming and identity continuity

```text
GET   /v1/identity/subjects/{subject_ref}/alias
PATCH /v1/identity/subjects/{subject_ref}/alias
POST  /v1/identity/subjects/{subject_ref}:prepare-continuity-review
GET   /v1/identity/continuity/reviews/{identity_continuity_review_id}
POST  /v1/identity/continuity/reviews/{identity_continuity_review_id}:apply
GET   /v1/identity/continuity/receipts
GET   /v1/identity/continuity/receipts/{identity_label_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without `rename means new certificate` folklore:

- what the current label, peer-visible label, stable subject handle, and authority fingerprint actually are
- whether a requested rename is local-only hygiene, peer-visible relabel, alias preservation, or a new-authority continuity claim
- whether the same authority remains active or the action really implies successor/replacement work
- what future approvals, constellation defaults, or grant boundaries would widen, narrow, or reset if the continuity story changes
- which receipt later proves that the action was cosmetic relabeling versus real trust fallout

A relabel response should answer at least:

- current and requested labels, with explicit visibility scope
- stable subject handle and current authority fingerprint summary
- whether the same authority remains intact
- whether previous labels remain searchable as aliases
- whether any peer observation is still pending
- which receipt will later prove the rename outcome

An identity-continuity review response should answer at least:

- current subject and candidate authority summaries
- whether the candidate is same-authority, same-person-new-authority, authority-uncertain, or authority-replacing
- whether the action can stay in this naming surface or must escalate into successor, compromise, or constellation review
- what constellation/grant/future-approval fallout would occur if accepted
- which actions remain admissible now: relabel-only, alias-only, keep separate, escalate, or block

### Target custody and exclusive binding

```text
GET  /v1/custody/records
GET  /v1/custody/records/{target_custody_record_id}
POST /v1/custody/inspect
GET  /v1/custody/cases
POST /v1/custody/cases
GET  /v1/custody/cases/{binding_collision_case_id}
POST /v1/custody/cases/{binding_collision_case_id}/apply
GET  /v1/custody/receipts
GET  /v1/custody/receipts/{custody_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without hidden-marker folklore:

- whether a local target is empty, already managed, foreign-managed, stale-managed, degraded, or ambiguous
- which daemon/state-root/service-profile appears to own the target when lineage can be proven
- whether a requested claim is same-lineage reuse, reviewed attach, successor/re-home work, inspect-only preservation, cleanup, or blocked collision
- whether removable-media reuse or same-host multi-profile behavior creates active corruption/fork risk
- which receipt proves that the target was claimed, blocked, preserved, or cleaned up

Inspection should return target-custody records even when the product refuses to bind the target.
Case creation should be preferred whenever the requested action could rewrite marker state, collide with another local universe, or destroy the easiest remaining evidence of prior ownership.
Ordinary non-empty-path comparison and reviewed target custody may reference each other, but the API should not pretend they are the same question.
Cleanup apply should fail closed if preservation is required and the required evidence has not been captured or explicitly surrendered.


### Share layout and annex separation

```text
GET  /v1/layout/contracts
GET  /v1/layout/contracts/{share_layout_contract_id}
POST /v1/layout/reviews
GET  /v1/layout/reviews/{share_layout_review_id}
POST /v1/layout/reviews/{share_layout_review_id}:apply
GET  /v1/layout/receipts
GET  /v1/layout/receipts/{layout_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without hidden-dotfolder folklore:

- whether the current live tree is clean, mixed-managed, legacy-imported, inspect-only, or blocked
- where share-control material, rollback/history bytes, metadata-carry sidecars, and temp-transfer residue live right now
- whether a requested migration would move managed bytes into an external annex, preserve them in place, or require review-sensitive cleanup first
- which residue classes are safe to clean, blocked, or preservation-sensitive

### Semantic runtime and optimization

```text
GET  /v1/semantic-runtime/contracts
GET  /v1/semantic-runtime/contracts/{semantic_runtime_contract_id}
POST /v1/semantic-runtime/reviews
GET  /v1/semantic-runtime/reviews/{semantic_optimization_review_id}
POST /v1/semantic-runtime/reviews/{semantic_optimization_review_id}/apply
GET  /v1/semantic-runtime/receipts
GET  /v1/semantic-runtime/receipts/{semantic_optimization_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without advanced-toggle folklore:

- which semantic guarantees are currently strong, weak, or uncertain for detection, rename continuity, delta-transfer behavior, verification, and conflict honesty
- whether a requested profile is harmless tuning, reviewed degraded-target acceptance, or restoration of stronger guarantees
- which target/runtime findings caused the weakness and whether they are share-, mount-, seat-, or host-scoped
- which receipt proves that the operator knowingly accepted or later reversed the semantic downgrade
- which receipt later proves that the share tree was cleaned, preserved as legacy, or explicitly kept mixed

A layout-contract response should answer at least:

- live root path and current live-namespace state
- layout class and annex location
- managed byte classes currently associated with the share
- history/temp/metadata-carry posture
- cleanup risk state and any preservation blockers
- which policy objects influence the current layout, if any

A layout-review response should answer at least:

- current versus requested layout class and visibility posture
- whether current odd bytes are live data, legacy managed state, temp residue, history bytes, or metadata-carry artifacts
- whether migration preserves continuity without exposing new in-tree managed areas
- what cleanup classes are admissible now: none, reviewed cleanup, preserve-and-inspect, or block
- which receipt will later prove the chosen layout outcome


### Replica retention and recall

```text
GET  /v1/replica-retention/postures
GET  /v1/replica-retention/postures/{retained_replica_posture_id}
POST /v1/replica-retention/reviews
GET  /v1/replica-retention/reviews/{replica_recall_review_id}
POST /v1/replica-retention/reviews/{replica_recall_review_id}/apply
GET  /v1/replica-retention/receipts
GET  /v1/replica-retention/receipts/{replica_recall_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without disconnect/remove folklore:

- which peers still retain bytes for this share and in what form
- whether future updates stopped, retained copies were merely attested, or stronger delete/recall observation actually exists
- whether an encrypted or read-only retained replica still matters for reseed or disaster recovery
- which follow-up still depends on peer observation or an explicit remote-delete request


### Share authority epochs and rotation

```text
GET  /v1/authority-epochs
GET  /v1/authority-epochs/{share_authority_epoch_id}
POST /v1/authority-rotation/reviews
GET  /v1/authority-rotation/reviews/{epoch_rotation_review_id}
POST /v1/authority-rotation/reviews/{epoch_rotation_review_id}/apply
GET  /v1/authority-rotation/receipts
GET  /v1/authority-rotation/receipts/{epoch_rotation_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without key-change/re-share folklore:

- which authority epoch is current for this share and which older epoch handles still remain in scope
- whether old capability material is artifact-only residue, still redeemable, or still backing a live older peer set
- which derivative/local-share or downstream migration obligations still block clean convergence
- whether the strongest honest statement is merely `new epoch issued` or the stronger `observed new epoch only`

### Access

```text
GET  /v1/access/policy
PATCH /v1/access/policy
GET  /v1/access/endpoints
GET  /v1/access/endpoints/{control_endpoint_id}
GET  /v1/access/capabilities
GET  /v1/access/capabilities/{control_capability_id}
GET  /v1/access/integrity
GET  /v1/access/integrity/{control_integrity_report_id}
GET  /v1/access/review-handoffs
POST /v1/access/review-handoffs
GET  /v1/access/review-handoffs/{review_handoff_id}
POST /v1/access/review-handoffs/{review_handoff_id}/consume
GET  /v1/access/mutation-gates
POST /v1/access/mutation-grants
GET  /v1/access/mutation-grants/{mutation_grant_id}
POST /v1/access/mutation-grants/{mutation_grant_id}/revoke
POST /v1/access/exposure-plans
POST /v1/access/exposure-plans/{plan_id}/apply
GET  /v1/access/tokens
POST /v1/access/tokens
GET  /v1/access/tokens/{access_token_id}
POST /v1/access/tokens/{access_token_id}/revoke
GET  /v1/access/sessions
GET  /v1/access/sessions/{control_session_id}
POST /v1/access/sessions/{control_session_id}/revoke
POST /v1/access/repair-cases
GET  /v1/access/repair-cases/{auth_repair_case_id}
POST /v1/access/repair-cases/{auth_repair_case_id}/apply
GET  /v1/access/receipts/{access_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without deployment folklore:

- which endpoints are currently local-only versus reviewed-exposed
- which token or browser/workbench session is active now and with what scope
- which attempted mutations are ready, grant-required, broader-review-required, or blocked
- which short-lived mutation grants exist now, with what scope and expiry posture
- which control actions are truly unavailable versus merely degraded in one client/channel
- how one reviewed action can safely continue in another channel without restarting the meaning from scratch
- which repair case regains control authority without touching unrelated durable state
- which receipt proves exposure, issuance, elevation, handoff, repair, rotation, or revocation happened

Exposure changes that leave localhost should be plan-bearing by default.
Browser/session repair should not require deleting unrelated daemon settings.
Trusted-proxy or hostcheck exceptions should be visible in endpoint state, not hidden in raw config.
Capability and integrity resources should let CLI, TUI, browser/workbench, and automation clients agree on whether a control action is denied by policy, blocked by trust/bootstrap posture, or merely degraded by the current client environment.
Review-handoff resources should preserve subject, review family, gate continuity, and receipt promise whenever the operator safely continues the same action in another channel, and should fail closed when channel change would alter endpoint, trust, or state-root meaning.
Mutation-gate resources should make observe-versus-mutate separation explicit and should fail closed when endpoint, state-root, or integrity posture no longer matches the reviewed apply context.
Repair-case apply should fail closed if the requested change would require broader state reset, bring-up replay, or state-root transition.


### Releases

```text
GET  /v1/releases/posture
GET  /v1/releases/posture/{release_posture_id}
POST /v1/releases/check
POST /v1/releases/compare
GET  /v1/releases/plans
POST /v1/releases/plans
GET  /v1/releases/plans/{upgrade_plan_id}
POST /v1/releases/plans/{upgrade_plan_id}/apply
GET  /v1/releases/receipts
GET  /v1/releases/receipts/{release_receipt_id}
```

These resources exist so tooling can answer one ordinary operator question without release-note archaeology:

- what version/family/channel/schema is active for this subject right now
- whether an available target is merely newer or actually safe for this constellation
- whether a mixed peer or linked-device posture remains operationally risky
- what rollback posture survives if this cutover is applied

A release posture should answer at least:

- subject kind (`daemon`, `transport-bundle`, `workbench-client`, `peer-constellation`)
- installed version and edition family
- channel and schema/API epoch
- compatibility family and peer-skew summary
- update state and downgrade posture
- linked-constellation skew state where relevant

Upgrade-plan creation should usually return or reference:

- a comparison-style report describing compatibility findings
- required cutover scope (`restart-only`, `drain-and-restart`, `state-root-verify`, etc.)
- rollback posture
- blocked/warning findings that must be accepted or resolved before apply

Release-receipt resources exist so later audit can prove which compatibility boundary was accepted, what release delta was applied, and what rollback posture was promised at cutover time.


### Policies, defaults, and precedence

```text
GET  /v1/defaults/profiles
POST /v1/defaults/profiles
GET  /v1/defaults/profiles/{defaults_profile_id}
POST /v1/defaults/profiles/{defaults_profile_id}:prepare-apply
GET  /v1/policy-bindings
GET  /v1/policy-bindings/{policy_binding_id}
POST /v1/policy-bindings
POST /v1/effective-policy:explain
GET  /v1/policy-receipts
GET  /v1/policy-receipts/{policy_receipt_id}
```

These resources exist so tooling can answer one ordinary operator question without preferences archaeology:

- what effective value is active for this subject and domain right now
- where that value came from
- whether the subject is inheriting, pinned, imported, or temporarily overridden
- what a defaults/profile change would actually touch

An effective-policy explanation should answer at least:

- subject and domain
- resolved values for important fields
- per-field origin kind and origin reference
- superseded candidate values where relevant
- whether a temporary override/schedule is affecting only current effective state
- surface gaps or unsupported-apply warnings

Defaults-profile apply preparation should usually return or reference:

- which subjects remain inheriting and are therefore eligible for change
- which subjects are pinned away from inheritance
- field-level before/after deltas
- whether the requested scope is `future-only`, `eligible-existing`, or `selected-subjects`

Policy-receipt resources exist so later audit can prove which fields were pinned, which returned to inheritance, and what defaults/profile change affected a subject set.


### Convergence

```text
GET  /v1/convergence/reports
POST /v1/convergence/reports
GET  /v1/convergence/reports/{convergence_report_id}
POST /v1/convergence/reports/{convergence_report_id}/refresh
POST /v1/convergence/wait
```

These resources exist so tooling can distinguish:

- transfer completion
- source reachability
- degraded change detection due to watcher limits or scan fallback
- clock/freshness blockers
- hidden background work that still weakens settlement confidence

A convergence report should expose at least:

- target scope and intent (`status`, `cutover`, `backup`, `relocate`, `restore`, `maintenance-drain`)
- local and remote `need*` style counts where known
- reachable versus required sources
- watcher / scan health and detection mode
- clock health and any freshness blockers
- background-work classification (`hashing`, `merging`, `dedup-copy`, etc.)
- final state (`idle`, `syncing`, `converged`, `degraded-converged`, `blocked`, `unknown`) and confidence

`POST /v1/convergence/wait` should allow a caller to block until a target satisfies a requested minimum state, or return structured blocker reasons if it cannot.

### Settlement

```text
GET  /v1/settlement/policies
POST /v1/settlement/policies
GET  /v1/settlement/policies/{settlement_policy_id}
GET  /v1/settlement/barriers
POST /v1/settlement/barriers
GET  /v1/settlement/barriers/{settlement_barrier_id}
POST /v1/settlement/barriers/{settlement_barrier_id}/refresh
POST /v1/settlement/barriers/{settlement_barrier_id}/wait
POST /v1/settlement/barriers/{settlement_barrier_id}/cancel
GET  /v1/settlement/receipts
GET  /v1/settlement/receipts/{settlement_receipt_id}
```

These resources exist so tooling can distinguish:

- current convergence evidence
- the readiness policy selected for a named action
- whether a quiet window or evidence-age clause is still pending
- which required or witness sources remain missing
- which readiness answer a plan/apply or destructive action actually used

A settlement barrier should expose at least:

- intent and policy reference
- current convergence report reference
- evidence age and quiet-window progress
- required versus present versus missing sources
- stable failed-clause codes
- current barrier state (`pending`, `satisfied`, `degraded-satisfied`, `blocked`, `stale`, `expired`, `canceled`)
- next safe actions and expiry

Settlement receipts should be queryable by subject so later audit can prove not only that an action happened, but whether it happened under strict or relaxed readiness criteria.

`GET /v1/system/capabilities` should report:

- supported placeholder strategies
- supported encryption/replica features
- supported invite kinds
- supported route/policy features
- embedded transport-engine inventory and integration kind
- Linux-first filesystem scope / support tier summaries
- explicit v1 platform-scope statement (`linux-only`, `linux-primary`, etc.)
- version/compatibility hints relevant to CLI and UI clients
- supported role templates and downgrade reasons when roles cannot apply cleanly

### Transports

```text
GET  /v1/transports
GET  /v1/transports/{engine}
GET  /v1/transports/{engine}/provenance
POST /v1/transports/{engine}/warm
POST /v1/transports/{engine}/cool
POST /v1/transports/{engine}/verify
GET  /v1/transports/sessions
GET  /v1/transports/sessions/{transport_session_id}
```

These resources exist so bundled Tor/I2P support is not a hidden side effect.
They should expose at least:

- engine name and integration kind
- whether the engine is compiled in or activated from an embedded payload
- bootstrap state and health findings
- runtime paths created locally, if any
- persistent state paths reused across restarts, if any
- whether the engine is merely cold, policy-disabled, verification-degraded, or genuinely failed
- version/build metadata that is safe to expose locally
- update mode (`daemon-release-only`, `independent-payload`, `external-managed`)
- digest/signature/provenance facts the local operator can verify

`GET /v1/transports/{engine}/provenance` should expose the stable facts behind the runtime: payload origin, version/build identifiers, digest, signer/provenance summary, persistence directory, and update mode.

`POST /v1/transports/{engine}/warm` should allow the CLI or a future UI to bring a privacy transport to ready state before a transfer without mutating durable policy.

`POST /v1/transports/{engine}/verify` should recompute or re-check locally available provenance facts without changing durable route policy.

Transport-session resources should expose at least:

- the engine and runtime in use
- whether the session is shared or dedicated
- scope (`system`, `policy`, `share`, `peer`)
- identity scope and reuse posture where that is knowable
- whether the session is overlay, LAN-direct, or WAN-direct
- route counts, last-used time, and degradation reasons
- why the daemon chose reuse versus dedicated sessioning

### Filesystems

```text
GET  /v1/filesystems/support
POST /v1/filesystems/probes
GET  /v1/filesystems/probes/{report_id}
```

These resources exist so Linux support boundaries and target-path safety are first-class inspectable state.

They should expose at least:

- detected filesystem family
- support tier
- case / normalization / xattr / ACL / symlink posture
- whether the target is local, foreign, networked, or FUSE-like
- blockers or warnings for adopt / relocate / restore / selective workflows

### Devices

```text
GET    /v1/devices
POST   /v1/devices
GET    /v1/devices/{device_id}
PATCH  /v1/devices/{device_id}
DELETE /v1/devices/{device_id}
```

Mutations must reject identity-replacement semantics by default.
A device replacement should use the recovery workflow, not a generic patch.
Device representations should also expose enough version/capability metadata for preflight reporting.

### Contacts

```text
GET    /v1/contacts
POST   /v1/contacts
GET    /v1/contacts/{contact_id}
PATCH  /v1/contacts/{contact_id}
POST   /v1/contacts/{contact_id}/trust
POST   /v1/contacts/{contact_id}/quarantine
POST   /v1/contacts/{contact_id}/ignore
```

Contact resources exist so future approval, successor continuity, and relationship memory do not hide inside raw device rows.
They should expose at least:

- relationship class
- contact state
- linked-group membership if any
- future-introduction policy summary
- approval summary and successor policy

### Pending peers

```text
GET    /v1/pending/peers
POST   /v1/pending/peers/{pending_peer_id}/accept
POST   /v1/pending/peers/{pending_peer_id}/dismiss
POST   /v1/pending/peers/{pending_peer_id}/ignore
```

Pending-peer resources exist so unknown or newly introduced devices are reviewable supported state.
They should expose at least:

- observed identity hints
- source of the contact or introduction
- candidate contact / link / claim outcomes
- durable ignore or quarantine decisions

### Review queues

```text
GET    /v1/review-items
GET    /v1/review-items/{review_item_id}
POST   /v1/review-items/{review_item_id}/dismiss
POST   /v1/review-items/{review_item_id}/snooze
```

Review items are derived attention summaries over real objects such as pending peers, incoming shares, plan drift, conflicts, degraded transports, convergence blockers, or successor reviews.
They should expose at least:

- lane (`now`, `soon`, `quiet`)
- urgency / worsen-by hints
- subject refs and proof refs
- the recommended next action
- whether dismiss/snooze affects only presentation or also requires subject resolution elsewhere

Mutating a review item must never silently perform the underlying trust, delete, or route action.

### Attention policy and events

```text
GET    /v1/attention/events
GET    /v1/attention/events/{attention_event_id}
POST   /v1/attention/events/{attention_event_id}/ack
POST   /v1/attention/events/{attention_event_id}/snooze
GET    /v1/attention/policy
POST   /v1/attention/policy
GET    /v1/attention/receipts
GET    /v1/attention/receipts/{attention_receipt_id}
```

Attention resources exist so tooling can distinguish:

- report meaning
- workbench lane placement
- delivery-channel attempts and outcomes
- operator acknowledgement or snooze posture

They should expose at least:

- active report refs and subject refs backing the event
- current lane, severity, freshness, and reason code
- chosen delivery targets and their last outcome
- whether acknowledgement changed only presentation or also references a subject workflow
- policy fallback used for headless or delivery-failure situations

### Diagnostics and evidence bundles

```text
GET    /v1/diagnostics/incidents
POST   /v1/diagnostics/incidents
GET    /v1/diagnostics/incidents/{diagnostic_incident_id}
POST   /v1/diagnostics/incidents/{diagnostic_incident_id}/depth
POST   /v1/diagnostics/incidents/{diagnostic_incident_id}/close
GET    /v1/evidence/bundles
POST   /v1/evidence/bundles
GET    /v1/evidence/bundles/{evidence_bundle_id}
POST   /v1/evidence/bundles/{evidence_bundle_id}/seal
POST   /v1/evidence/bundles/{evidence_bundle_id}/destroy
GET    /v1/evidence/receipts
GET    /v1/evidence/receipts/{evidence_receipt_id}
GET    /v1/logs
GET    /v1/log-levels
POST   /v1/log-levels
```

Diagnostic resources exist so tooling can distinguish:

- the incident being investigated
- the currently active diagnostic depth and its expiry
- the evidence classes collected for this incident
- the redaction profile and any remaining sensitivity findings
- what was sealed, exported, retained, or destroyed later

They should expose at least:

- incident subject refs, reason, and requested evidence classes
- time window and scope for collected logs/events/file diagnostics
- explicit redaction findings for paths, peer IDs, addresses, and blocked secret material
- whether crash dumps or per-file diagnostics were included
- receipt-bearing depth changes so verbose logging cannot linger invisibly after the investigation ends

### View projections

```text
GET    /v1/views/home
GET    /v1/views/shares/{share_id}
GET    /v1/views/peers/{peer_or_contact_id}
```

These endpoints are optional convenience projections for workbench clients.
They are **read-only summaries** over the same public objects, not a second hidden model.
They should expose at least:

- summary headers and high-signal chips
- current-answer text suitable for compact surfaces
- grouped primary cards or sections
- subject refs and proof refs backing each card
- recommended primary action labels without mutating state
- freshness info for any attached proof or plan

If a workbench uses these endpoints, it must still be possible to navigate from every summary card back to the underlying object resources.

### Retirements

```text
GET    /v1/retirements
POST   /v1/retirements
GET    /v1/retirements/{retirement_id}
POST   /v1/retirements/{retirement_id}/apply
POST   /v1/retirements/{retirement_id}/cancel
```

Retirement resources exist so tooling can distinguish:

- cosmetic hiding
- ignored future contact
- trust revocation
- successor replacement
- identity rotation

A retirement resource should say explicitly whether the old device may still reconnect, whether grants or approval-memory records are being revoked or rebound, and whether a successor device inherits any continuity.

### Links / linked groups

```text
GET    /v1/links
POST   /v1/links
GET    /v1/links/{linked_group_id}
PATCH  /v1/links/{linked_group_id}
POST   /v1/links/{linked_group_id}/members
DELETE /v1/links/{linked_group_id}/members/{device_id}
```

The crucial design point:

- linking is separate from granting
- linking is separate from share visibility policy
- linking is separate from identity replacement
- share visibility can produce incoming objects without creating mounts
- introduction policy must be explicit; ordinary linking does not imply ambient auto-add

Any non-trivial member-add should be previewable through a referenced claim or preflight object before mutation. Tooling must be able to ask:

- whether the candidate keeps its current identity or should instead enter a replacement/migration workflow
- which member class and defaults it would join with
- what immediate visibility delta follows from the join
- what authority or approval reach expands immediately
- which compatibility or migration warnings still block apply

### Shares

```text
GET    /v1/shares
POST   /v1/shares
GET    /v1/shares/{share_id}
PATCH  /v1/shares/{share_id}
POST   /v1/shares/{share_id}/pause
POST   /v1/shares/{share_id}/resume
POST   /v1/shares/{share_id}/rescan
```

### Grants

```text
GET    /v1/grants
POST   /v1/grants
GET    /v1/grants/{grant_id}
PATCH  /v1/grants/{grant_id}
DELETE /v1/grants/{grant_id}
POST   /v1/grants/{grant_id}/mutation-plans
GET    /v1/grants/mutation-plans/{plan_id}
POST   /v1/grants/mutation-plans/{plan_id}/apply
POST   /v1/grants/mutation-plans/{plan_id}/cancel
```

Grant objects should expose:

- subject identity
- permission
- mode cap
- origin of the grant (`manual`, `policy`, `invite`, `recovery`)
- provenance reference where available

That provenance field matters for auditability.

Non-trivial grant mutations should expose a stable `review_model` whenever changing authority is more than a cosmetic label flip.
The `review_model` should at minimum group facts into:

- `trigger_and_current_authority`
- `desired_boundary_delta`
- `active_subject_and_dependent_fallout`
- `authority_substrate_and_compatibility_effects`
- `admissible_mutations`
- `receipt_promise`

Tooling must be able to ask:

- whether the change widens only write authority or also delegation / revoke reach
- whether active local derivatives, linked members, or dependent grants narrow automatically, remain unchanged, or require follow-up review
- whether byte retention differs from authority removal
- whether the requested state can be expressed directly or requires imported/legacy authority-substrate migration before apply

### Stewardship

```text
GET    /v1/stewardship
GET    /v1/stewardship/{share_id}
PATCH  /v1/stewardship/{share_id}
POST   /v1/stewardship/{share_id}/handoff-plans
GET    /v1/stewardship/handoff-plans/{plan_id}
POST   /v1/stewardship/handoff-plans/{plan_id}/apply
POST   /v1/stewardship/handoff-plans/{plan_id}/cancel
```

Stewardship resources exist so tooling can distinguish:

- data-write rights
- grant / revoke authority
- delegation bounds
- successor nomination and handoff policy
- share governance changes caused by retirement or recovery

A handoff plan should say explicitly what authority moves, what remains with the current steward, and whether retirement / recovery state blocks safe apply.

### Incoming share visibility

```text
GET    /v1/incoming
POST   /v1/incoming/{incoming_id}/compare
GET    /v1/incoming/{incoming_id}
POST   /v1/incoming/{incoming_id}/claim-prepare
POST   /v1/incoming/{incoming_id}/adopt
POST   /v1/incoming/{incoming_id}/hide-local
POST   /v1/incoming/{incoming_id}/withdraw
POST   /v1/incoming/{incoming_id}/reject
```

These resources represent shares that are visible locally through linking, manual sharing, or recovery, but not yet adopted into a local path.
They exist specifically to avoid coupling share visibility to default-path creation.
Handling one incoming share must not depend on flipping a whole device into a different linked-folder default mode.
Incoming objects should expose whether the share is merely announced here, deferred locally, hidden locally, claim-ready, or already bound.
The wire contract should preserve the difference between `hide on this machine` and `withdraw from constellation`; clients should never have to infer that from side effects.
A `claim-prepare` response should be able to prefill suggested path, mode, and local role without pretending the claim has already been applied.
`POST /v1/incoming/{incoming_id}/hide-local` should emit a local-scope receipt and must not retract sibling visibility.
`POST /v1/incoming/{incoming_id}/withdraw` should require authority that is visibly broader than local inbox stewardship and should emit a wider-scope receipt.

### Ignore rules and drift

```text
GET    /v1/shares/{share_id}/ignore-rules
POST   /v1/shares/{share_id}/ignore-rules
GET    /v1/shares/{share_id}/ignore-rules/{rule_id}
PATCH  /v1/shares/{share_id}/ignore-rules/{rule_id}
DELETE /v1/shares/{share_id}/ignore-rules/{rule_id}
POST   /v1/shares/{share_id}/ignore-rules/test
GET    /v1/shares/{share_id}/ignore-drift
```

These resources exist so ignore behavior is a supported part of the control plane rather than an edit-this-hidden-file ritual.
The API should expose:

- the effective ordered rule set
- each rule's origin (`built-in`, `manual`, `profile`, `import`)
- drift or mismatch state where relevant
- whether the daemon considers the current rule state healthy

### Projection policies

```text
GET    /v1/projection-policies
POST   /v1/projection-policies
GET    /v1/projection-policies/{projection_policy_id}
PATCH  /v1/projection-policies/{projection_policy_id}
DELETE /v1/projection-policies/{projection_policy_id}
POST   /v1/projection-policies/{projection_policy_id}/test
POST   /v1/projection-policies/{projection_policy_id}/prepare-tighten
GET    /v1/projection-receipts
GET    /v1/projection-receipts/{projection_receipt_id}
```

These resources exist so operators can distinguish namespace suppression from local mount-view omission or placeholder projection, and so late-tightening behavior does not dissolve into hidden-file folklore.
A projection policy should expose at least:

- whether it applies to a `share` namespace or a `mount` view
- default namespace visibility / peer-announcement posture where relevant
- default local projection posture (`omit`, `placeholder`, `metadata-only`, `full`) where relevant
- ordered rules with stable IDs and provenance
- tighten behavior when rules are made stricter after paths are already indexed or materialized
- whether the daemon considers current projection state healthy, review-required, receipt-pending, or blocked

`POST .../test` should answer for a concrete path whether peers learn the path, whether the local mount shows it, whether bytes are expected locally, whether preserved-but-not-shown state exists, and whether existing indexed/materialized history creates a review requirement.

`POST .../prepare-tighten` should return either a low-risk directly applicable response or a `projection-effect` report explaining before/after namespace truth, local-view truth, and required follow-up.

Projection receipts should expose at least:

- change class (`namespace-tighten`, `namespace-widen`, `local-tighten`, `local-widen`, `detach-cleanup`, `materialization-default-change`)
- before/after effective projection state
- prior visibility/materialization history
- follow-up requirements and refs
- operator and provenance metadata

### Conflicts

```text
GET  /v1/conflicts
GET  /v1/conflicts/{conflict_id}
GET  /v1/conflicts/{conflict_id}/history
POST /v1/conflicts/{conflict_id}/resolve
POST /v1/conflicts/{conflict_id}/defer
GET  /v1/rollback-receipts
GET  /v1/rollback-receipts/{rollback_receipt_id}
```

Conflict objects should include structured candidate data, history refs where available, recommended actions, and a stable `review_model` whenever adjudication is non-trivial.
The API should not require callers to interpret magic filenames or hidden archive paths in order to resolve an ordinary sync conflict safely.
The `review_model` should at minimum group facts into:

- `trigger_and_semantic_class`
- `candidates_and_authority_posture`
- `path_materialization_and_compatibility_reality`
- `resolution_scope_and_loser_handling`
- `admissible_resolutions`
- `receipt_promise`

Completed restore or conflict-resolution actions should emit rollback receipts so later audit can answer what won, what lost, what scope changed, and how the loser was handled.


### Roles

```text
GET    /v1/roles
POST   /v1/roles
GET    /v1/roles/{role_id}
PATCH  /v1/roles/{role_id}
DELETE /v1/roles/{role_id}
```

Roles are reusable least-privilege bundles, not alternate share types.
They exist so link/grant/adopt flows can preserve convenience without collapsing everything into owner-like authority.


### Deviation policies

```text
GET    /v1/deviation-policies
POST   /v1/deviation-policies
GET    /v1/deviation-policies/{policy_id}
PATCH  /v1/deviation-policies/{policy_id}
DELETE /v1/deviation-policies/{policy_id}
```

Deviation-policy resources exist so local-remediation behavior on non-authoritative mounts is not inferred from share type or mode alone.
They should expose at least:

- which write-policy classes the policy applies to
- separate add / modify / delete handling
- whether remote progress continues, pauses, or requires review while deviation exists
- whether capability limits forced stricter remediation than the operator requested

### Deviation cases

```text
GET    /v1/deviation-cases
GET    /v1/deviation-cases/{deviation_case_id}
POST   /v1/deviation-cases/{deviation_case_id}/resolve
```

Deviation-case resources exist so concrete local drift on non-authoritative mounts is queryable as a real object.
They should expose at least:

- the affected share, mount, and path
- deviation class (`local-add`, `local-modify`, `local-delete`, `local-rename`, `path-drift`)
- current remediation state
- whether remote progress is continuing or blocked
- whether local evidence was preserved, copied aside, quarantined, or reverted
- which receipt, report, or decision trace explains the last change

### Path comparisons

```text
GET    /v1/comparisons
GET    /v1/comparisons/{comparison_id}
POST   /v1/comparisons/{comparison_id}/refresh
```

Comparison objects should summarize at least:

- target path state (`empty`, `non-empty`, `already-bound-self`, `already-bound-other`, `service-marker-conflict`)
- target-lineage posture (`same-lineage-likely`, `same-lineage-unproven`, `foreign-local-tree`, `encrypted-target-mismatch`, or similar)
- identical/local-only/remote-only/same-path-divergent/path-collision counts
- whether the compared share appears fully in sync first or not
- whether a later adopt/relocate should be blocked, allowed directly, or forced through plan/apply

The daemon should not silently resolve a non-empty-path adoption or relocation by timestamp folklore alone.
If some automatic winner rule exists, it must be surfaced explicitly in the comparison or resulting plan.

### Reconciliation cases

```text
GET    /v1/reconciliations
POST   /v1/reconciliations
GET    /v1/reconciliations/{reconciliation_case_id}
POST   /v1/reconciliations/{reconciliation_case_id}/plan
POST   /v1/reconciliations/{reconciliation_case_id}/apply
```

Reconciliation-case resources exist so non-empty-target bind work with same-path divergence or ambiguous lineage is queryable as a real object rather than a warning box.
They should expose at least:

- the triggering incoming item or mount and the requested target path
- target-lineage posture and any evidence that this is or is not same-lineage reuse
- identical/local-only/remote-only/same-path-divergent/path-collision summaries
- candidate chronology and authority confidence, including whether ranking comes only from timestamp evidence
- whether encrypted/annex target reuse is blocked, reviewed, or safe to reuse
- admissible outcomes, preservation requirements, and resulting receipt references

The daemon should fail closed when a client tries to turn a reconciliation case into plain `adopt anyway` or `repair anyway` semantics.

### Mounts

```text
GET    /v1/mounts
POST   /v1/mounts
GET    /v1/mounts/{mount_id}
PATCH  /v1/mounts/{mount_id}
DELETE /v1/mounts/{mount_id}
GET    /v1/mounts/{mount_id}/doctor
POST   /v1/mounts/{mount_id}/compare
POST   /v1/mounts/{mount_id}/repair
POST   /v1/mounts/{mount_id}/relocate
POST   /v1/mounts/{mount_id}/detach
GET    /v1/mounts/{mount_id}/preservation
POST   /v1/mounts/{mount_id}/set-deviation-policy
GET    /v1/mounts/{mount_id}/deviation-state
POST   /v1/mounts/{mount_id}/review-deviation
GET    /v1/mounts/{mount_id}/deviation-cases
```

Mount resources should expose the effective deviation policy and any active deviation state so tooling can answer whether local adds, edits, or deletes are merely flagged, auto-remediated, or currently blocking review.
Mount resources should also expose the active fidelity contract reference when filesystem portability has been explicitly negotiated.
They should also expose:

- desired path versus current bound path
- current binding-health summary
- last path-probe time
- last binding receipt
- whether detach can preserve incoming visibility

`GET /v1/mounts/{mount_id}/doctor` should explain broken-path, marker-drift, and repair posture without mutating anything.
`POST /v1/mounts/{mount_id}/repair` should normally return a plan object when continuity is non-trivial.
`POST /v1/mounts/{mount_id}/detach` should be distinct from deleting the mount or forgetting the share entirely.
`GET /v1/mounts/{mount_id}/preservation` should return the baseline preservation set most relevant to that mount.

### Preservation sets and binding receipts

```text
GET    /v1/preservation-sets
GET    /v1/preservation-sets/{preservation_set_id}
POST   /v1/preservation-sets/{preservation_set_id}/refresh
GET    /v1/binding-receipts
GET    /v1/binding-receipts/{binding_receipt_id}
```

These resources exist so clients can answer two ordinary operator questions without hidden-state archaeology:

- what rollback surface exists here right now
- what was the last bind-oriented change and what proof supported it

A preservation set is a reusable baseline, not a substitute for an action-specific preservation report.
A binding receipt is the durable audit record for adopt/repair/relocate/detach/reconnect work.

### Files and materialization

```text
POST /v1/files/fetch
POST /v1/files/evict
POST /v1/files/remove
POST /v1/files/check
POST /v1/files/pin
POST /v1/files/unpin
POST /v1/files/availability/query
GET  /v1/files/availability?share_id=...&path=...
GET  /v1/fetchability-receipts
GET  /v1/fetchability-receipts/{fetchability_receipt_id}
GET  /v1/files/state?share_id=...&path=...
GET  /v1/files/history?share_id=...&path=...
GET  /v1/files/history/{history_entry_id}
POST /v1/files/history/query
POST /v1/files/restore
GET  /v1/file-intent-receipts
GET  /v1/file-intent-receipts/{file_intent_receipt_id}
GET  /v1/rollback-receipts
GET  /v1/rollback-receipts/{rollback_receipt_id}
```

These should be task-oriented endpoints because the object being changed is usually “path within mount/share”, not a standalone durable resource.
File-intent receipts exist so later audit can explain one file action in terms of explicit intent and scope.

`POST /v1/files/remove` should require an explicit scope field such as `local` or `share`.
The API should never infer distributed-delete semantics from a generic remove request.

`POST /v1/files/check` should generate a preservation report for actions such as `evict`, `remove-local`, `remove-share`, or `restore-share`.
That report should include remaining plaintext coverage, encrypted-only coverage, history coverage, and any blockers caused by weak rollback posture.

`GET /v1/files/availability` and `POST /v1/files/availability/query` should expose namespace visibility, current local materialization, full-copy witness summary, fetchability posture, ghost/stale-announcement risk, and eviction safety for one path or a reviewed subtree.
Clients should not have to infer “available on demand” from placeholder state alone.
If the only known full copy is local, the response should say so explicitly.
If the path is announcement-visible but no peer now has the bytes, the response should classify it as `ghost-risk` or `not-fetchable`, not merely `pending`.
For reviewed subtrees, the response should support both a compact answer strip and row-level grouping such as `safe-now`, `re-witness-first`, and `stale/ghost`, so clients never flatten mixed-risk selections into one optimistic state.
Responses should include witness records or witness summaries that say whether backing is local-current, remote-confirmed, remote-last-known, history-backed, or none-known.
Responses should also be able to emit row-level action contracts and a selection summary so clients can render exact labels such as `Evict 24 safe rows`, `Create witnesses for 3 guarded rows`, or `Restore 2 history-backed rows` without inventing those verbs locally.
Responses should also be able to emit presentation hints such as `inline-direct`, `inline-review`, or `blocked`, plus a review route or review object ref, so clients do not invent their own direct-action thresholds.
History-backed-only cases should surface `restore-from-history` rather than `fetch-now`.
Dense clients may choose a smaller presentation, but the wire contract should still keep action offer, danger class, and receipt kind explicit.
If a row is not `safe-now`, the wire contract should make it possible for a client to open the right review pane directly rather than guessing whether a visible CTA should mutate or escalate.
`GET /v1/fetchability-receipts` and `GET /v1/fetchability-receipts/{fetchability_receipt_id}` should preserve later proof of the witness posture, risk class, action offer, and action taken after review.

`GET /v1/files/history` should return candidate restore points with provenance, capture cause, retention horizon, confidence, and allowed restore scopes.
`GET /v1/files/history/{history_entry_id}` should expose one durable timeline record even after the short-lived activity stream moved on.
`POST /v1/files/history/query` may support richer filters such as `path-prefix`, `entry-kind`, or `captured-from-peer` without overloading list semantics.
`POST /v1/files/restore` should require an explicit restore scope and should usually return a plan object for share-wide restore on sensitive paths. Scope-sensitive completions should emit file-intent receipts and rollback receipts.
Destructive plans should reference a fresh preservation report when rollback posture materially affects safety.

### Offers

```text
GET    /v1/offers
POST   /v1/offers
POST   /v1/offers/inspect
GET    /v1/offers/{offer_id}
POST   /v1/offers/{offer_id}/revoke
POST   /v1/offers/{offer_id}/reissue
GET    /v1/claim-receipts
GET    /v1/claim-receipts/{claim_receipt_id}
```

Offer resources make capability-bearing artifacts durable and inspectable on the sender side even after the portable payload itself has been copied elsewhere.
They should capture at least:

- normalized offer kind and delivery encoding
- offered scope and role/capabilities
- expiry, redemption budget, peer pinning, and redelegation posture
- whether claim review is mandatory
- provenance for who issued the offer and under which policy or plan
- revocation, supersession, and redemption state

`POST /v1/offers/inspect` should parse a portable artifact without applying it and return the same normalized manifest regardless of whether the input arrived as file, URI, QR payload, or clipboard text.
`POST /v1/offers/{offer_id}/reissue` should preserve semantic identity unless the caller explicitly changes scope, policy, role, or constraints.
Claim-receipt resources should remain inspectable after the original portable artifact expires or is deleted.

### Claims

```text
GET    /v1/claims
POST   /v1/claims
GET    /v1/claims/{claim_id}
POST   /v1/claims/{claim_id}/apply
POST   /v1/claims/{claim_id}/reject
```

Claim resources make invite and incoming-share acceptance durable and inspectable.
They should capture at least:

- source offer/invite or incoming reference
- intended local path / mode / role outcome
- intended linked-group / member-class outcome for link-target claims
- referenced preflight or plan IDs
- expiry, redemption-budget, peer-pinning, or drift conditions
- whether the claim widened authority, created a mount, only staged incoming visibility, or merely changed local presentation state
- resulting claim-receipt identity when applied
- a stable `review_model` grouping so clients can render the same intake sections in the same order instead of inventing their own `connect` summary grammar

The `review_model` should at minimum group facts into:

- `source_and_offer`
- `local_outcome`
- `path_and_filesystem`
- `authority_delta`
- `blockers_and_drift`
- `receipt_promise`

When `target_action=link`, the review model should additionally make these join facts explicit rather than hiding them inside generic source/outcome prose:

- `identity_and_continuity`
- `membership_and_defaults`
- `visibility_delta`
- `authority_delta`
- `compatibility_and_migration`
- `receipt_promise`

### Approval memory

```text
GET    /v1/approvals
POST   /v1/approvals
GET    /v1/approvals/{approval_id}
PATCH  /v1/approvals/{approval_id}
POST   /v1/approvals/{approval_id}/revoke
POST   /v1/approvals/test
```

Approval resources make remembered future approval explicit.
They should capture at least:

- approved subject identity or peer
- bounded scope such as one share, one tag/class of shares, or one linked group
- approver scope (`origin-only`, `linked-group`, `named-devices`)
- maximum role or permission the approval can imply
- expiry, revocation, and last-use facts
- provenance for who issued the approval and under which policy or plan

Approval objects should never by themselves imply local path creation, local claim completion, or local materialization. They only authorize reduced-review reuse within bounded scope.

`POST /v1/approvals/test` should answer whether a hypothetical future share or invite would be auto-approved, and which approval object would authorize it.

### Approval-seat review

```text
GET    /v1/approval-requests
GET    /v1/approval-requests/{approval_request_id}
POST   /v1/approval-requests/{approval_request_id}/review-prepare
GET    /v1/approval-reviews/{approval_review_id}
POST   /v1/approval-reviews/{approval_review_id}/approve
POST   /v1/approval-requests/{approval_request_id}/deny
GET    /v1/approval-receipts
GET    /v1/approval-receipts/{approval_receipt_id}
```

Approval-seat review resources exist so clients do not have to infer `which member is speaking` from the current runtime alone.
They should capture at least:

- requested peer/contact/claim subject
- requested role or permission
- candidate acting seats and why each is admissible, guarded, or blocked
- selected acting seat when a review is prepared
- approval horizon (`this-subject`, `named-members`, `reviewed-future-scope`, `none`)
- share or constellation fallout if future approval memory would be created
- policy/report references and receipt promise

`POST /v1/approval-requests/{approval_request_id}/review-prepare` must be side-effect free apart from producing the review object.
No standing approval memory should be created until the prepared review is explicitly approved.
These resources should compose with `contacts`, `approvals`, and `constellations` rather than shadowing them with a second hidden model.


### Approval-memory matches

```text
GET    /v1/approval-matches
GET    /v1/approval-matches/{approval_match_id}
POST   /v1/approval-matches/{approval_match_id}/review-prepare
GET    /v1/approval-match-reviews/{approval_match_review_id}
POST   /v1/approval-match-reviews/{approval_match_review_id}/apply
```

Approval-memory match resources exist so clients do not infer standing-trust reuse from silent arrival side effects.
They should capture at least:

- arrived subject/share/invite or pending object that matched prior trust
- matched approval object or candidate approval objects
- why the match is exact, guarded, partial, stale, or blocked
- which narrow auto-admit boundary is permitted now (`identity-only`, `queue-admitted`, `claim-suggested`, or `none`)
- whether local claim, path bind, materialization, or write enablement still remain unresolved
- whether the honest next action is reuse-as-suggestion, fresh review, tighten memory, or revoke memory
- policy/report references and receipt promise

`POST /v1/approval-matches/{approval_match_id}/review-prepare` must be side-effect free apart from producing the review object.
A remembered approval match must never silently choose a path, create a bind, or materialize bytes.
These resources should compose with `approvals`, `claims`, and `incoming` resources rather than hiding standing-trust reuse inside them.

### Policies

```text
GET    /v1/policies
POST   /v1/policies
GET    /v1/policies/{policy_id}
PATCH  /v1/policies/{policy_id}
POST   /v1/policies/{policy_id}/cache/clear
GET    /v1/policies/{policy_id}/exposure
GET    /v1/policies/{policy_id}/disclosure
```

`GET /v1/policies/{policy_id}/exposure` should summarize at least:

- what the policy publishes about this device/share reachability
- which infrastructure classes receive that publication (`lan`, `private-discovery`, `public-tracker`, `private-relay`, `public-relay`)
- whether the daemon is only dialing known targets or also accepting tracker-learned routes
- which fallback steps would widen metadata exposure compared with the preferred route

`GET /v1/policies/{policy_id}/disclosure` should summarize at least:

- which audience classes can currently learn anything about the policy subject
- which fact classes are disclosed to each audience
- which mechanisms create that disclosure
- whether any residual disclosure remains after a recent narrowing change

### Disclosure reports, exposure reports, known hosts, and route leases

```text
GET    /v1/disclosure/reports
POST   /v1/disclosure/reports
GET    /v1/disclosure/reports/{disclosure_report_id}
GET    /v1/disclosure/residue
GET    /v1/disclosure/residue/{residual_disclosure_id}
GET    /v1/disclosure/receipts
GET    /v1/disclosure/receipts/{disclosure_receipt_id}
GET    /v1/exposure/reports
POST   /v1/exposure/reports
GET    /v1/exposure/reports/{exposure_report_id}
GET    /v1/known-hosts
POST   /v1/known-hosts
GET    /v1/known-hosts/{known_host_id}
DELETE /v1/known-hosts/{known_host_id}
GET    /v1/route-leases
POST   /v1/route-leases
GET    /v1/route-leases/{route_lease_id}
DELETE /v1/route-leases/{route_lease_id}
```

These resources exist so disclosure, exposure, and temporary direct exceptions are supported state rather than preference-page folklore.
They should expose at least:

- what the baseline publication posture is
- which infrastructure classes can currently learn reachability
- which audience classes can currently learn identity, share-membership, or endpoint facts
- which peer-pinned known-host paths exist and for what scope
- which temporary route leases widen or narrow that posture right now
- whether cached endpoint state or provider retention could preserve an older wider posture until cleared or decayed

`POST /v1/disclosure/reports` should support previewing a hypothetical widening or narrowing change before mutation.
If a narrowing request still leaves residual disclosure, the resulting report should name decay or clearance steps explicitly instead of implying that “off” means invisible immediately.

`POST /v1/route-leases` should accept explicit scope, effect, TTL, reason, and optional exhaustion bounds such as byte caps.
If a lease modifies public-direct eligibility, `GET /v1/exposure/reports/...` and `GET /v1/routes/...` should both show that fact.

### Overrides and effective state

```text
GET    /v1/overrides
POST   /v1/overrides
GET    /v1/overrides/{override_id}
POST   /v1/overrides/{override_id}/review
POST   /v1/overrides/{override_id}/renew
DELETE /v1/overrides/{override_id}
GET    /v1/overrides/receipts
GET    /v1/overrides/receipts/{override_receipt_id}
GET    /v1/effective-state
GET    /v1/effective-state/{subject_type}/{subject_id}
GET    /v1/activity-state
GET    /v1/activity-state/{subject_type}/{subject_id}
GET    /v1/schedules
POST   /v1/schedules
GET    /v1/schedules/{schedule_window_id}
PATCH  /v1/schedules/{schedule_window_id}
DELETE /v1/schedules/{schedule_window_id}
```

These resources exist so maintenance intent does not masquerade as durable configuration.
They should expose at least:

- target scope, family, and mode
- explicit effects on upload, download, scanning, announcement, delete propagation, diagnostics depth, or access exposure as applicable
- creation provenance and reason
- automatic expiry time, exhaustion budget, or explicit no-expiry acknowledgement
- which underlying policies remain unchanged
- renewal/cancel history and override receipts
- the combined effective state after applying active leases

`POST /v1/overrides/{override_id}/renew` should preserve lease identity and history while changing expiry or exhaustion terms.

`GET /v1/effective-state/...` should be cheap enough that CLI and UI surfaces can show it by default whenever temporary overrides affect behavior.

`GET /v1/activity-state/...` should expose the public phase matrix directly, including which phases are active, throttled, suspended, or draining and whether the effect comes from baseline, override, or recurring schedule.
`/v1/schedules` exists so recurring windows are first-class state rather than UI-only calendar decorations.

### Routing and peer paths

```text
GET /v1/routes
GET /v1/routes/peers/{device_id}
GET /v1/routes/peers/{device_id}/decision
GET /v1/routes/shares/{share_id}
GET /v1/routes/shares/{share_id}/decision
```

These endpoints exist because transport is policy, not hidden plumbing.
They should expose at least:

- currently active route
- candidate routes
- route source (`lan`, `known-host`, `tracker`, `relay`, `tor`, `i2p`)
- transport class versus exposure class as separate fields
- whether the selected route depended on public or private infrastructure
- cached endpoint entries
- publication facts that made the route possible
- participating transport-runtime references and their current lifecycle state
- whether WAN clearnet direct required a manual override and, if so, that override's scope, expiry, and any byte/transfer exhaustion bound
- whether a direct candidate exists only because of a peer-pinned known-host record
- refusal / fallback reason when a better path was not used
- whether a cache clear is recommended after policy changes
- a structured decision trace with selected route, rejected candidates, and decisive facts when requested

### Transfers

```text
GET   /v1/transfers
GET   /v1/transfers/{transfer_id}
PATCH /v1/transfers/{transfer_id}
GET   /v1/transfers/{transfer_id}/explanation
GET   /v1/transfer-policies
POST  /v1/transfer-policies
GET   /v1/transfer-policies/{transfer_policy_id}
PATCH /v1/transfer-policies/{transfer_policy_id}
GET   /v1/throughput-budgets
POST  /v1/throughput-budgets
GET   /v1/throughput-budgets/{throughput_budget_id}
PATCH /v1/throughput-budgets/{throughput_budget_id}
GET   /v1/transfer-budget-receipts
GET   /v1/transfer-budget-receipts/{transfer_budget_receipt_id}
```

`PATCH /v1/transfers/{transfer_id}` should allow only limited, explicit actions such as lane/priority changes or cancellation.

These resources exist because raw byte counters are not enough.
A supported client should be able to inspect at least:

- selected route class and transport kind
- preferred but unavailable or rejected route classes
- active durable transfer policy and any temporary throughput budgets
- queue lane, queue state, and suspension cause
- whether relay use is merely allowed, discouraged, budgeted, or blocked by policy
- whether current slowdown is attributable to budget cap, fairness, delay profile, source absence, phase suppression, or disk backpressure
- which receipt proves a temporary cap, exemption, or scheduled budget window was active

### Filesystem profiles and compatibility

```text
GET  /v1/fs/profiles
POST /v1/fs/profiles:inspect
GET  /v1/fs/profiles/{fs_profile_id}
POST /v1/fs/compare
GET  /v1/fs/reports/{fs_compat_report_id}
GET  /v1/fs/policies
POST /v1/fs/policies
GET  /v1/fs/policies/{portability_policy_id}
POST /v1/fs/contracts:prepare
GET  /v1/fs/contracts/{fidelity_contract_id}
POST /v1/fs/contracts/{fidelity_contract_id}:verify
GET  /v1/fs/drift-cases
GET  /v1/fs/drift-cases/{fidelity_drift_case_id}
GET  /v1/fs/receipts
GET  /v1/fs/receipts/{fidelity_receipt_id}
```

These resources exist so pathname and metadata semantics are inspectable before an action commits **and** remain inspectable afterward as a durable portability/fidelity contract.
A filesystem profile should report at least:

- path inspected
- filesystem type and platform family
- case-sensitivity posture
- Unicode normalization posture
- prohibited-name / prohibited-character rules
- symlink / junction handling posture
- metadata fidelity for permissions, xattrs, ACLs, and specials
- timestamp precision and clock-safety findings

A filesystem compatibility report should report at least:

- whether pathnames are safe without rewrite
- whether normalization rewrite or case-fold protection would be required
- whether symlinks or junction-like entries will be blocked, flattened, or preserved
- whether metadata classes will be dropped or downgraded
- whether the finding is `ok`, `auto-correctable`, `warning`, or `blocked`
- which later action can reference the report as a precondition

A portability policy and fidelity contract should report at least:

- which pathname, metadata, special-file, and notification policies were intentionally chosen
- whether the active mount is local-native, network-reviewed, or outside supported posture
- what downgrades, blocked classes, or virtualization rules are currently active
- when the contract was last verified and whether it is fresh, stale, drifted, or blocked
- which receipt proves the operator knowingly accepted any warning-tier posture or downgrade

### Preflight / compatibility reports

```text
POST /v1/preflight/link
POST /v1/preflight/grant
POST /v1/preflight/adopt
GET  /v1/preflight/{report_id}
```

These resources exist so compatibility and authority consequences are inspectable **before** commitment.
A report should include:

- blockers
- warnings
- feature downgrades
- authority changes
- recommended roles or alternative actions
- referenced subject versions/capabilities used to generate the report

Preflight generation should be cheap enough to call routinely from CLI and UI clients.
If a later apply or accept step depends on preflighted assumptions, the plan or action should reference the report and fail explicitly when the report is stale.

### Plans

```text
GET    /v1/plans
POST   /v1/plans
GET    /v1/plans/{plan_id}
POST   /v1/plans/{plan_id}/apply
DELETE /v1/plans/{plan_id}
```

Plan resources are preferred for operations that:

- widen trust boundaries
- install multi-object policy bundles
- replace devices or rebind grants
- depend on exact object versions at preview time

Plan objects should include:

- intended action type
- affected objects
- preconditions
- risk flags
- provenance / initiator
- referenced preservation reports where destructive safety is relevant
- expiry if the preview becomes stale by design

### Backup / recovery

```text
GET  /v1/backups
POST /v1/backups
GET  /v1/backups/{backup_id}
GET  /v1/recovery/posture
GET  /v1/recovery-bundles
POST /v1/recovery-bundles
GET  /v1/recovery-bundles/{recovery_bundle_id}
POST /v1/recovery-bundles/{recovery_bundle_id}/verify
GET  /v1/recovery-receipts
GET  /v1/recovery-receipts/{recovery_receipt_id}
POST /v1/recover/import
POST /v1/recover/replace-device
POST /v1/recover/rotate-identity
POST /v1/recover/revoke-device
```

Recovery endpoints are intentionally explicit.
Where the real operator intent is trust retirement, the endpoint should return or reference a retirement record instead of pretending that replacement, revocation, and cosmetic cleanup are the same operation.
They should produce high-signal events and audit entries.
Where recovery mutates multiple grants or policies, returning a plan object is preferable.

Recovery-bundle resources exist so encrypted recovery posture is inspectable before failure.
Verification should answer at least:

- whether offline decrypt is presently possible
- whether a surviving daemon/database is still required
- whether metadata is complete enough for target workflow
- which secrets or provenance records are missing
- what continuity claims the bundle could later support and what it explicitly cannot restore
- whether newer rotation, retirement, or state-root changes have invalidated an older bundle

Recovery-receipt resources exist so export, verification, invalidation, and later consumption stay auditable without treating the artifact file itself as the only proof.

`POST /v1/recover/replace-device` should normally return or reference a plan with a stable cutover `review_model` whenever continuity, authority rewrite, or residue is non-trivial. That review model should at minimum group facts into:

- `predecessor_and_candidate`
- `continuity_carry_forward`
- `state_root_and_runtime_target`
- `share_grant_and_authority_rewrite`
- `residue_and_revocation`
- `receipt_promise`

Continuity-sensitive `/v1/state/roots:*` and `/v1/service-profiles/*:prepare-switch` responses may reuse the same review model when the operator is effectively performing a cutover or re-home rather than a routine low-risk move.

One important boundary: some recovery work should intentionally stay outside the daemon API.
If encrypted-replica recovery must still work after local daemon state is lost, an offline CLI path such as `recover decrypt-replica` is justified precisely because it does not depend on the daemon surviving.
The daemon-side API should still be able to export and verify the recovery material needed for that path while the system is healthy.


### Bring-up and control entry

```text
GET  /v1/bringup/cases
POST /v1/bringup/cases
GET  /v1/bringup/cases/{bringup_case_id}
POST /v1/bringup/cases/{bringup_case_id}:apply
GET  /v1/bringup/receipts
GET  /v1/bringup/receipts/{bringup_receipt_id}
```

These resources exist so first-open work does not hide behind init flows, startup flags, config files, or bind-address lore.

A bring-up case should expose at least:

- host role and runtime target
- state/continuity choice (`new-state`, `attach-known-root`, `import-state`, `recover-bundle`, `successor-sensitive`, `inspect-without-open`)
- candidate state root or artifact reference
- identity posture and any relationship consequences
- control/network posture including requested endpoints and exposure class
- blocker/dependency findings
- receipt promise and risk state

Applying a bring-up case should usually return or reference:

- a bring-up report
- a plan object where mutation is non-trivial
- a bring-up receipt if the case opens state or exposes control
- explicit answers to whether the result is fresh local state, attached prior state, recovered/imported state, successor-sensitive continuity, or rejected bring-up

### State roots and service profiles

```text
GET  /v1/state
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
POST /v1/state/import
```

These resources exist so storage-root choice, runtime-profile choice, host-local execution-seat choice, and root transition work do not hide behind launch flags, service-account changes, or installer behavior.

The `/v1/state` summary should answer at least:

- active state root ID and path
- active service profile
- active execution seat summary
- identity fingerprint summary
- last verification time
- share/mount/contact inventory counts
- current integrity state
- recent transition refs if the system just attached, moved, switched, imported, or replaced state

Attach/move/import/profile-switch endpoints should usually return or reference:

- a `state-transition` report
- a plan object where mutation is non-trivial
- before/after state snapshots when the action commits
- an explicit answer to whether the action preserves the same durable root, opens a different root, or should be treated as successor cutover instead

A state-root verification response should answer at least:

- whether the root is internally coherent enough to open
- whether identity continuity matches operator expectations
- whether another service profile currently owns the root
- whether recovery/export posture is adequate for safe transition work
- whether drift or partial-integrity findings require repair before attach or move

A profile-switch preparation response should answer at least:

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

### Space budgets, pressure, and retention

```text
GET  /v1/space/ledgers
GET  /v1/space/ledgers/{space_ledger_id}
GET  /v1/space/policies
POST /v1/space/policies
GET  /v1/space/policies/{budget_policy_id}
GET  /v1/space/pressure-cases
GET  /v1/space/pressure-cases/{pressure_case_id}
POST /v1/space/reclaim-plans
GET  /v1/space/reclaim-plans/{reclaim_plan_id}
POST /v1/space/reclaim-plans/{reclaim_plan_id}:apply
GET  /v1/space/receipts
GET  /v1/space/receipts/{reclaim_receipt_id}
```

These resources exist so tooling can distinguish:

- materialized-byte growth
- archive/history retention cost
- temp-download or remnant buildup
- daemon/state/log/runtime footprint
- reclaim actions that are local-only versus those that would weaken retention

A space ledger should expose at least:

- subject and scope
- total and free bytes
- byte classes and class totals
- active budget policy reference
- current pressure state
- last sampled time

A pressure-case response should answer at least:

- which threshold fired
- which classes dominate the problem
- whether the case is warning, guarded, high, or blocked
- which reclaim actions are safe-first
- whether new materialization or retention growth is currently blocked

A reclaim-plan creation response should answer at least:

- subject scope
- candidate class effects
- estimated freed bytes
- preserved bytes or rollback posture that would remain
- whether retention/history cost changes
- whether apply is immediately allowed or review-required

A reclaim receipt should make later audit answer not only that space was freed, but what classes changed and whether rollback/history posture weakened.

### Explain / provenance

```text
GET /v1/explain/{object_type}/{object_id}
```

This endpoint should return a structured decision trace when one exists, including selected outcome, rejected candidates, decisive facts, freshness, and provenance references.

It should answer questions such as:

- why this grant exists
- which policy or profile created this linked-group behavior
- why this route is currently active
- which route candidates were rejected and for what reason
- what exposure policy allowed this route to exist
- which recovery workflow changed this device state

### Audit

```text
GET /v1/audit
GET /v1/audit/{entry_id}
```

Audit entries should be queryable by:

- time range
- type
- subject object
- initiator
- correlation ID
- provenance reference

### Metrics

```text
GET /v1/metrics
```

Format may be JSON initially, with a Prometheus-friendly surface later.
The point is not style.
The point is that transfer, route, event, and health counters are a supported interface.

---

## Exit and decommission resources

These resources keep departure-style actions explicit.
They answer what an exit would stop, what it preserves, and what residue remains after apply.

```text
POST   /v1/exits
GET    /v1/exits/{exit_plan_id}
POST   /v1/exits/{exit_plan_id}/apply
GET    /v1/exit-residue
GET    /v1/exit-residue/{exit_residue_id}
GET    /v1/exit-receipts/{exit_receipt_id}
```

`POST /v1/exits` should accept a normalized subject ref plus an explicit `intent_class`.
The resulting plan should always include:

- authority effects
- visibility/disclosure effects
- byte-state effects
- continuity effects
- residue findings and clearability
- apply blockers or acknowledgements still required
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `intent_and_scope`
- `stops_now`
- `stays_intentionally`
- `residue_after_apply`
- `follow_up_options`
- `receipt_promise`

Domain-specific mutation endpoints may still exist, but when the operator-visible outcome is a departure, revocation, detachment, or decommission, those endpoints should reference or emit the same exit-plan / exit-receipt model.



## Compromise / containment resources

These resources keep incident-grade trust response explicit.
They answer what was merely suspected, what was frozen immediately, what was revoked or rotated, what continuity was preserved or rejected, and what residue still remains.

```text
GET    /v1/compromise-cases
POST   /v1/compromise-cases
GET    /v1/compromise-cases/{compromise_case_id}
POST   /v1/compromise-cases/{compromise_case_id}/apply
GET    /v1/compromise-receipts/{compromise_receipt_id}
```

`POST /v1/compromise-cases` should accept one or more normalized subject refs plus an explicit incident reason or posture.
The resulting case or referenced plan should always include:

- trigger facts and scope
- immediate freeze effects already possible
- proposed revocation and rotation work
- continuity/successor options if relevant
- residue findings and observation requirements
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `trigger_and_scope`
- `immediate_freeze`
- `revocation_and_rotation`
- `continuity_and_successor`
- `residue_and_observation`
- `receipt_promise`

Recovery, access, offer, and exit endpoints may still exist for narrower domain actions, but when the operator-visible outcome is incident containment, those endpoints should reference or emit the same compromise-case / compromise-receipt model.

## Re-entry / stale-return resources

These resources keep long-offline, chronology-uncertain, or otherwise stale-returning subjects explicit.
They answer whether the subject is merely visible again, whether chronology can be trusted, whether writable replay is admissible, what divergence or missing-source fallout exists, and whether the next step is resume, quarantine, merge review, successor handling, or containment escalation.

```text
GET    /v1/reentry-cases
POST   /v1/reentry-cases
GET    /v1/reentry-cases/{reentry_case_id}
POST   /v1/reentry-cases/{reentry_case_id}/apply
GET    /v1/reentry-receipts/{reentry_receipt_id}
```

`POST /v1/reentry-cases` should accept a normalized subject ref plus optional related share refs and an explicit reason such as `long-offline-return`, `clock-uncertain-return`, `ghost-announcement`, or `unexpected-reappearance`.
The resulting case or referenced plan should always include:

- subject identity and dormancy facts
- chronology confidence and evidence freshness
- proposed authority posture on return
- divergence and source-availability findings
- admissible next actions and any escalation path into compromise or successor-cutover review
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `subject_and_dormancy`
- `chronology_and_evidence`
- `authority_and_scope`
- `divergence_and_availability`
- `admissible_actions`
- `receipt_promise`

Settlement, history, compromise, and recovery endpoints may still exist for narrower domain actions, but when the operator-visible outcome is deciding what a stale-returning subject may safely do now, those endpoints should reference or emit the same reentry-case / reentry-receipt model.

## Destructive-replay / delete-wave resources

These resources keep high-signal remote delete, overwrite, and revert waves explicit.
They answer what destructive scope is being proposed, what preservation actually exists, whether source confidence is strong enough to trust the wave, and whether the right next action is apply, narrow, freeze, or escalate.

```text
GET    /v1/destructive-replay-cases
POST   /v1/destructive-replay-cases
GET    /v1/destructive-replay-cases/{destructive_replay_case_id}
POST   /v1/destructive-replay-cases/{destructive_replay_case_id}/apply
GET    /v1/destructive-replay-receipts/{destructive_replay_receipt_id}
```

`POST /v1/destructive-replay-cases` should accept a normalized share ref plus optional path set and an explicit reason such as `remote-delete-wave`, `remote-overwrite-wave`, `receive-only-revert`, `protected-scope-hit`, or `archive-weak-replay`.
The resulting case or referenced plan should always include:

- trigger facts and scope summary
- destructive effect counts, protected-path hits, and local-byte impact summary
- preservation and recoverability findings
- authority and source-confidence posture
- admissible next actions and any escalation path into compromise or re-entry review
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `trigger_and_scope`
- `destructive_effect_summary`
- `preservation_and_recoverability`
- `authority_and_source_confidence`
- `admissible_actions`
- `receipt_promise`

Activity, history, deviation, and recovery endpoints may still exist for narrower domain actions, but when the operator-visible outcome is deciding whether destructive propagation should be allowed now, those endpoints should reference or emit the same destructive-replay-case / destructive-replay-receipt model.

## Local-derivation / self-edge resources

These resources keep same-host fanout, cache branches, and self-edge topology explicit.
They answer what source and target are being coupled, whether the topology is loop-safe, what authority and lifecycle are inherited, and whether target tier or source materialization weakens the promise.

```text
GET    /v1/local-derivations
POST   /v1/local-derivations
GET    /v1/local-derivations/{local_derivation_case_id}
POST   /v1/local-derivations/{local_derivation_case_id}/apply
GET    /v1/local-derivation-receipts/{local_derivation_receipt_id}
```

`POST /v1/local-derivations` should accept a normalized source share or mount ref plus an explicit target path and derivation intent such as `read-only-derivative`, `writable-derivative`, `cache-branch`, or `export-like`.
The resulting case or referenced plan should always include:

- source and target summary
- topology relation and loop-risk posture
- authority and lifecycle coupling findings
- materialization and target-tier findings
- admissible next actions and any narrowing path
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `source_and_target`
- `topology_and_loop_risk`
- `authority_and_lifecycle_coupling`
- `materialization_and_target_tier`
- `admissible_derivations`
- `receipt_promise`

Binding, projection, fidelity, and storage endpoints may still exist for narrower domain actions, but when the operator-visible outcome is creating or changing a same-host derivative, those endpoints should reference or emit the same local-derivation-case / local-derivation-receipt model.

## Contention / quiesce resources

These resources keep locked files, burst-save delay, mixed external-writer risk, and explicit quiesce actions visible as one coordination model.
They answer what scope is contested, what writer evidence exists, whether notifications are trustworthy enough, and what propagation is being delayed, held, or frozen.

```text
GET    /v1/contention-cases
POST   /v1/contention-cases
GET    /v1/contention-cases/{contention_case_id}
POST   /v1/contention-cases/{contention_case_id}/apply
POST   /v1/contention-cases/{contention_case_id}/release
GET    /v1/contention-receipts/{contention_receipt_id}
```

`POST /v1/contention-cases` should accept one or more share/mount/path refs plus an explicit intent such as `inspect`, `delay-writes`, `quiesce-upload`, `freeze-bidirectional`, `narrow-reader`, or `escalate-fidelity`.
The resulting case or referenced plan should always include:

- trigger facts and contested-scope summary
- writer and lock evidence with confidence posture
- notification and filesystem-posture findings
- quiesce and propagation-effect summary
- admissible next actions and any escalation path into fidelity, topology, or destructive-replay review
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `trigger_and_contested_scope`
- `writer_and_lock_reality`
- `notification_and_filesystem_posture`
- `quiesce_and_propagation_effects`
- `admissible_actions`
- `receipt_promise`

Transfer, activity, fidelity, and topology endpoints may still exist for narrower domain actions, but when the operator-visible outcome is coordinating around another writer or mixed-access uncertainty, those endpoints should reference or emit the same contention-case / contention-receipt model.

## Capacity-fit / scale-admission resources

These resources keep RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers visible as one host-fit model.
They answer what subject and local role are being considered, whether this host can honestly sustain them, and whether the safe next step is full adoption, selective or metadata-only narrowing, reclaim-first staging, or rejection on the current host.

```text
GET    /v1/capacity-fit-cases
POST   /v1/capacity-fit-cases
GET    /v1/capacity-fit-cases/{capacity_fit_case_id}
POST   /v1/capacity-fit-cases/{capacity_fit_case_id}/apply
POST   /v1/capacity-fit-cases/{capacity_fit_case_id}/defer
GET    /v1/capacity-fit-receipts/{capacity_fit_receipt_id}
```

`POST /v1/capacity-fit-cases` should accept one or more share/mount/claim refs plus an explicit target path and intended local role such as `full-materialize`, `selective-materialize`, `metadata-only`, `preseeded-adopt`, or `narrow-scope`.
The resulting case or referenced plan should always include:

- subject and intended-local-role summary
- local capacity and index-cost findings
- freshness and notification-posture findings
- portability and path-blocker findings
- admissible modes / mitigations and any escalation path into topology, fidelity, or storage review
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `subject_and_intended_local_role`
- `local_capacity_and_index_cost`
- `freshness_and_notification_posture`
- `portability_and_path_blockers`
- `admissible_modes_and_mitigations`
- `receipt_promise`

Intake, storage, fidelity, and topology endpoints may still exist for narrower domain actions, but when the operator-visible outcome is deciding whether this host can honestly carry a subject and under what local mode, those endpoints should reference or emit the same capacity-fit-case / capacity-fit-receipt model.

## Semantic-runtime review resources

These resources keep speed and compatibility work honest.
They answer which guarantees are strong or weak right now, what target/runtime condition caused the weakness, and whether the safest next step is accept the degraded profile, restore a stronger profile, move to a stronger target, or block.

```text
GET    /v1/semantic-runtime/reviews
POST   /v1/semantic-runtime/reviews
GET    /v1/semantic-runtime/reviews/{semantic_optimization_review_id}
POST   /v1/semantic-runtime/reviews/{semantic_optimization_review_id}/apply
GET    /v1/semantic-runtime/receipts/{semantic_optimization_receipt_id}
```

`POST /v1/semantic-runtime/reviews` should accept one or more share/mount refs plus an explicit requested profile such as `balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, or `full-verify`.
The resulting case or referenced plan should always include:

- requested optimization or degraded-target summary
- guarantee-delta findings for detection, rename continuity, delta behavior, verification, and conflict honesty
- target/runtime findings explaining why the weaker posture exists or would exist
- admissible actions and any safer restoration path
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `requested_optimization_or_degraded_target`
- `semantic_guarantees_at_risk`
- `detection_diff_and_verification_posture`
- `target_and_runtime_findings`
- `admissible_actions`
- `receipt_promise`

Transfer, fidelity, contention, and capacity-fit endpoints may still exist for narrower domain actions, but when the operator-visible outcome is accepting or reversing a meaning-changing optimization or compatibility downgrade, those endpoints should reference or emit the same semantic-runtime-review / semantic-optimization-receipt model.

## Topology-review resources

These resources keep nested shares, overlapping graph subjects, cross-share moves, and root-boundary-sensitive path work explicit.
They answer which graph subjects are involved, how containment changes propagation, whether the path stays within allowed roots, and whether the safest next step is accept, rebind, flatten, or reject.

```text
GET    /v1/topology-cases
POST   /v1/topology-cases
GET    /v1/topology-cases/{topology_case_id}
POST   /v1/topology-cases/{topology_case_id}/apply
GET    /v1/topology-receipts/{topology_receipt_id}
```

`POST /v1/topology-cases` should accept one or more share/mount refs plus an optional candidate path and explicit intent such as `nest`, `flatten`, `rebind`, `move-across-boundary`, or `reject-overlap`.
The resulting case or referenced plan should always include:

- trigger and graph-subject summary
- containment relation and propagation-shape findings
- path continuity and root-boundary findings
- admissible topology actions and any safer narrowing path
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `trigger_and_graph_subjects`
- `containment_and_propagation_shape`
- `path_and_root_boundary_effects`
- `admissible_topology_actions`
- `receipt_promise`

Binding, derivation, claim, and filesystem endpoints may still exist for narrower domain actions, but when the operator-visible outcome is accepting or repairing a nested, overlapping, moved, or root-boundary-sensitive graph relationship, those endpoints should reference or emit the same topology-case / topology-receipt model.

### Semantic runtime and optimization reviews

```text
GET  /v1/semantic-runtime/contracts
GET  /v1/semantic-runtime/contracts/{semantic_runtime_contract_id}
POST /v1/semantic-runtime/reviews
GET  /v1/semantic-runtime/reviews/{semantic_optimization_review_id}
POST /v1/semantic-runtime/reviews/{semantic_optimization_review_id}/apply
GET  /v1/semantic-runtime/receipts
GET  /v1/semantic-runtime/receipts/{semantic_optimization_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without advanced-toggle folklore:

- which guarantees are currently strong, weak, or uncertain for detection, rename continuity, delta-transfer behavior, verification, and conflict honesty
- whether a requested profile change is harmless tuning, reviewed degraded-target acceptance, or restoration of stronger guarantees
- which target/runtime condition caused the weakness and whether it is share-, mount-, seat-, or host-scoped
- which receipt proves later that the downgrade was accepted or that the stronger posture was restored

Case creation should be preferred whenever a requested optimization weakens an operator-visible guarantee even if the request sounds like speed tuning.


### Observer posture and read-only review resources

```text
GET    /v1/observer/contracts
GET    /v1/observer/contracts/{observer_posture_contract_id}
POST   /v1/observer/reviews
GET    /v1/observer/reviews/{observer_rights_review_id}
POST   /v1/observer/reviews/{observer_rights_review_id}/apply
GET    /v1/observer/receipts/{observer_rights_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without folklore about what `read only` really means:

- whether the subject currently sees names only, placeholders, or full bytes
- whether local edits are blocked, suspend syncing for touched paths, auto-revert, or require a wider reviewed repair
- whether the subject may serve clean bytes onward, may not serve, or inherits ordinary serving rights
- which parts of that posture come from share authority versus local projection, derivative shape, selective materialization, or runtime/client limits
- which receipt later proves the exact observer bundle that was accepted, narrowed, or repaired

`POST /v1/observer/reviews` should accept one or more share/peer, replica, mount, or derivative refs plus an explicit requested posture such as `names-only-observer`, `placeholder-observer`, `full-byte-observer`, `non-serving-mirror`, or `inspect-only`.

Review creation should be preferred whenever a requested observer or read-only change affects any operator-visible fact about local write handling, onward serving, or projection limits even if the request sounds like a small permission tweak.

Every observer-rights review should be able to return:

- the current observer posture contract for the subject
- byte-visibility findings and current materialization summary
- local-write findings including repair availability or path-suspend risk
- onward-serve findings including reseed usefulness when relevant
- projection/share-class/runtime-limit findings
- a stable `review_model` grouping so clients can render the same sections in the same order without inventing their own semantics

The `review_model` should at minimum group facts into:

- `requested_posture`
- `visibility_and_materialization_reality`
- `local_write_and_repair_behavior`
- `onward_serving_and_redistribution`
- `projection_class_and_runtime_limits`
- `receipt_promise`

Grant, derivation, selective-materialization, and recall endpoints may still exist for narrower domain actions, but when the operator-visible outcome is changing or repairing observer-style behavior, those endpoints should reference or emit the same observer-posture-contract / observer-rights-review / observer-rights-receipt model.

## Event stream

## Why this matters

Syncthing's long-poll event API is a useful reference point: one stream, stable IDs, `since`, optional filtering.
AnonSync should adopt the spirit of that model while making event payloads more operator-oriented.

### Long-poll endpoint

```text
GET /v1/events?since=<event_id>&types=a,b,c&limit=100&timeout=60
```

Behavior:

- returns events after `since`
- blocks until new events are available or timeout expires
- supports filtering by event type
- returns monotonically increasing IDs

If the requested cursor is older than the retained buffer window, the API should return an explicit continuity error rather than pretending no gap exists.

### SSE endpoint

Optional but desirable:

```text
GET /v1/events/stream
```

For simple UI/TUI and dashboard consumers.

### Event envelope

```json
{
  "event_id": "evt_000123",
  "time": "2026-03-09T08:00:00-05:00",
  "type": "transfer.blocked",
  "subject_type": "transfer",
  "subject_id": "trf_01J...",
  "severity": "warning",
  "reason": "PLAINTEXT_SOURCE_UNAVAILABLE",
  "correlation_id": "corr_01J...",
  "data": {
    "share_id": "shr_01J...",
    "path": "Secrets/Taxes/report.pdf",
    "peer_candidates": 2,
    "plaintext_candidates": 0
  }
}
```

### Event classes for v1

#### Identity and trust

- `contact.created`
- `contact.trusted`
- `contact.quarantined`
- `contact.ignored`
- `pending_peer.observed`
- `pending_peer.accepted`
- `pending_peer.dismissed`
- `pending_peer.ignored`
- `device.added`
- `device.updated`
- `device.hidden`
- `device.ignored`
- `device.retirement_started`
- `device.retirement_completed`
- `device.revoked`
- `link.created`
- `link.member_added`
- `identity.rotation_started`
- `identity.rotation_completed`
- `recovery.replace_device_started`
- `recovery.replace_device_completed`
- `recovery.cutover_plan_created`
- `reentry.case_created`
- `reentry.case_applied`
- `destructive_replay.case_created`
- `destructive_replay.case_applied`
- `state.transition_prepared`
- `state.transition_applied`

#### Share and grant lifecycle

- `share.created`
- `share.updated`
- `share.paused`
- `share.resumed`
- `incoming.visible`
- `incoming.adopted`
- `incoming.rejected`
- `ignore.rule_added`
- `ignore.rule_removed`
- `ignore.drift_detected`
- `projection.updated`
- `projection.review_required`
- `grant.created`
- `grant.updated`
- `grant.revoked`
- `role.created`
- `role.updated`
- `deviation_policy.created`
- `deviation_policy.updated`
- `preflight.generated`
- `offer.created`
- `offer.revoked`
- `offer.reissued`
- `offer.inspected`
- `claim.created`
- `claim.applied`
- `claim.rejected`
- `claim.receipt_emitted`
- `recovery_bundle.exported`
- `recovery_bundle.verified`
- `recovery_bundle.invalidated`
- `recovery_receipt.emitted`
- `release.posture_changed`
- `release.update_available`
- `release.plan_created`
- `release.plan_applied`
- `release.rollback_recorded`
- `compatibility.boundary_accepted`
- `compatibility.warning`
- `policy.defaults_changed`
- `policy.binding_changed`
- `policy.inheritance_restored`
- `policy.receipt_emitted`
- `filesystem.compatibility.warning`
- `filesystem.compatibility.blocked`
- `filesystem.profile.changed`

#### Review and attention

- `review.item_promoted`
- `review.item_snoozed`
- `review.item_dismissed`
- `review.item_resolved`

#### Plans and preconditions

- `plan.created`
- `plan.applied`
- `plan.canceled`
- `precondition.failed`

#### Convergence and readiness

- `convergence.report_generated`
- `convergence.state_changed`
- `convergence.blocked`
- `convergence.degraded`
- `settlement.barrier_created`
- `settlement.barrier_state_changed`
- `settlement.barrier_stale`
- `settlement.receipt_emitted`

#### Mount and materialization

- `mount.attached`
- `mount.mode_changed`
- `mount.deviation_detected`
- `mount.deviation_cleared`
- `mount.deviation_auto_remediated`
- `file.fetch_queued`
- `file.materialized`
- `file.evicted`
- `file.check_generated`
- `file.remove_local`
- `file.remove_share`
- `file.remove_blocked`
- `file.pin_changed`
- `file.restored_local`
- `file.restored_share`
- `conflict.detected`
- `conflict.review_opened`
- `conflict.resolved`

#### Transport and transfer

- `peer.connected`
- `peer.disconnected`
- `transfer.started`
- `transfer.progress`
- `transfer.blocked`
- `transfer.completed`
- `transfer.failed`
- `route.selected`
- `route.candidate_rejected`
- `route.cache_cleared`
- `decision.trace_recorded`
- `policy.path_changed`

#### Overrides and effective state

- `override.created`
- `override.reviewed`
- `override.renewed`
- `override.expiring`
- `override.expired`
- `override.exhausted`
- `override.canceled`
- `override.receipt_recorded`
- `schedule.created`
- `schedule.updated`
- `schedule.enabled`
- `schedule.disabled`
- `schedule.activated`
- `schedule.deactivated`
- `effective-state.changed`

#### Diagnosis and recovery

- `doctor.finding`
- `backup.created`
- `backup.imported`
- `audit.entry_written`
- `exit.plan_created`
- `exit.applied`
- `exit.residue_recorded`
- `exit.residue_cleared`
- `exit.receipt_recorded`


## Share-local presence and arrival-default resources

The daemon should expose current local share posture and future-arrival defaults as related but separate resources.

### `share_presence`

Describes a specific share on a specific seat.

Suggested fields:

- `id`
- `share_id`
- `seat_id`
- `announcement_state` — `announced`, `hidden-local`, `withdrawn`, `unknown`
- `claim_state` — `not-claimed`, `claim-suggested`, `claimed`
- `bind_state` — `unbound`, `bound`, `relocate-pending`, `blocked`
- `bind_path`
- `path_provenance` — `reviewed`, `operator-picked`, `template-derived`, `collision-adjusted`, `restored`
- `byte_posture` — `names-only`, `placeholders`, `partial-local`, `full-local`
- `fetch_policy`
- `current_posture_summary`
- `updated_at`

### `arrival_default_policy`

Describes what a seat will do with later arrivals for a reviewed scope.

Suggested fields:

- `id`
- `seat_id`
- `scope`
- `default_outcome` — `announce-only`, `claim-suggested`, `review-required`, `reviewed-auto-claim`
- `path_template`
- `collision_policy`
- `initial_byte_posture`
- `review_basis`
- `receipt_id`
- `updated_at`

### `presence_review`

A reviewed mutation that changes current posture, future-arrival policy, or both.

Suggested fields:

- `id`
- `seat_id`
- `share_id`
- `change_scope` — `current-share`, `future-arrivals`, `both`
- `before`
- `after`
- `path_compare_report_id`
- `blocked_reasons`
- `receipt_promise`
- `created_at`

### `placement_suggestion`

A candidate local path for one share on one seat.

Suggested fields:

- `id`
- `share_id`
- `seat_id`
- `candidate_path`
- `suggestion_basis` — `share-name-under-reviewed-root`, `scope-template`, `remembered-seat-preference`, `manual-draft`, `restored-bind`
- `source_policy_id`
- `collision_class` — `clear`, `occupied-empty`, `occupied-nonempty-unrelated`, `occupied-same-lineage-candidate`, `managed-bind-held`, `case-fold-collision`, `portable-target-mismatch`
- `collision_evidence`
- `same_lineage_confidence`
- `future_default_impact` — `unchanged`, `template-consumed-only`, `template-update-proposed`
- `created_at`

### `placement_review`

A reviewed bind decision for one share on one seat.

Suggested fields:

- `id`
- `share_id`
- `seat_id`
- `current_bind_state`
- `suggestion_ids`
- `selected_outcome` — `bind-suggested`, `bind-alternate`, `adopt-existing`, `keep-claimed-unbound`, `keep-announced-only`, `blocked`
- `selected_path`
- `collision_class`
- `comparison_report_id`
- `future_default_change_scope` — `none`, `also-update-template`
- `receipt_promise`
- `created_at`

### Endpoints

```text
GET  /v1/shares/{share_id}/presence?seat=self
GET  /v1/presence/{presence_id}
GET  /v1/seats/{seat_id}/arrival-defaults
GET  /v1/arrival-defaults/{policy_id}
POST /v1/presence/reviews
GET  /v1/presence/reviews/{review_id}
POST /v1/presence/reviews/{review_id}/apply
GET  /v1/presence/receipts/{receipt_id}
GET  /v1/shares/{share_id}/placement-suggestions?seat=self
GET  /v1/placement-suggestions/{suggestion_id}
POST /v1/placement/reviews
GET  /v1/placement/reviews/{review_id}
POST /v1/placement/reviews/{review_id}/apply
GET  /v1/placement/receipts/{receipt_id}
```

### Event additions

- `presence.current_posture_changed`
- `presence.arrival_default_changed`
- `presence.bind_path_changed`
- `presence.path_provenance_recorded`
- `presence.collision_rule_triggered`
- `presence.receipt_emitted`
- `placement.suggestion_recorded`
- `placement.collision_classified`
- `placement.review_opened`
- `placement.receipt_emitted`

## Error model

Mutating endpoints should return structured errors.

Example:

```json
{
  "error": {
    "code": "IDENTITY_REPLACEMENT_REQUIRES_RECOVERY_FLOW",
    "message": "Linking cannot overwrite the current device identity.",
    "hint": "Use POST /v1/recover/replace-device instead."
  }
}
```

Drift example:

```json
{
  "error": {
    "code": "PRECONDITION_FAILED",
    "message": "The target share changed after the plan was created.",
    "hint": "Refresh the plan and review new effects before apply."
  }
}
```

## Compatibility contract

The daemon API should be stable enough for:

- shell tooling
- small local dashboards
- TUI/web UI clients
- backup/inspection utilities

It does **not** need to promise perfect forever stability from day one.
But it should promise that object meanings, event semantics, provenance fields, compatibility/preflight semantics, and recovery semantics do not churn casually.


## Standing arrival-template governance additions

### `arrival_template_policy`

A durable seat-scoped policy object describing how later arrivals should be admitted and drafted.

Suggested fields:

- `id`
- `seat_id`
- `governed_scope`
- `admission_posture` — `announce-only`, `review-required`, `claim-suggested`, `reviewed-auto-claim`
- `path_template`
- `collision_default` — `always-review`, `allow-same-lineage-adopt-suggestion`, `propose-alternate`
- `initial_byte_suggestion` — `names-only`, `placeholders`, `materialize-after-review`
- `origin_kind`
- `pinned_subject_count`
- `created_at`
- `updated_at`

### `arrival_template_effect_preview`

A stable preview of what a proposed standing-template change will and will not touch.

Suggested fields:

- `id`
- `policy_id`
- `future_unseen_effect`
- `unclaimed_draft_effect` — `unchanged`, `refresh-to-new-template`, `explicit-subset-only`
- `claimed_unbound_effect` — `unchanged`, `blocked`, `explicit-subset-review-required`
- `bound_share_effect` — must normally be `unchanged`
- `pinned_subject_ids[]`
- `notes[]`
- `created_at`

### `arrival_template_review`

A reviewed standing-template change for one seat and one governed scope.

Suggested fields:

- `id`
- `seat_id`
- `governed_scope`
- `current_policy_id`
- `proposed_policy_delta`
- `effect_preview_id`
- `selected_draft_refresh_mode` — `unchanged`, `refresh-unclaimed`
- `receipt_promise`
- `created_at`

### Endpoints

```text
GET  /v1/seats/{seat_id}/arrival-templates
GET  /v1/arrival-templates/{policy_id}
POST /v1/arrival-templates/reviews
GET  /v1/arrival-templates/reviews/{review_id}
POST /v1/arrival-templates/reviews/{review_id}/apply
GET  /v1/arrival-templates/receipts/{receipt_id}
```

### Event additions

- `arrival_template.policy_changed`
- `arrival_template.effect_preview_created`
- `arrival_template.review_opened`
- `arrival_template.unclaimed_drafts_refreshed`
- `arrival_template.receipt_emitted`


## Arrival explanation additions

### `arrival_explanation`

A read projection that explains why one subject currently appears in one local stage on one reviewed seat.

Suggested fields:

- `arrival_explanation_id`
- `seat_ref`
- `subject_ref`
- `current_local_stage` — `announced`, `matched`, `claim-suggested`, `claimed-unbound`, `placement-reviewed`, `bound`, `hidden-local`, `blocked`
- `primary_cause_summary`
- `causal_steps[]`
- `governing_refs[]`
- `non_causes[]`
- `counterfactuals[]`
- `next_actions[]`
- `receipt_refs[]`
- `computed_at`

### `causal_step`

Ordered explanation step for one arrival explanation.

Suggested fields:

- `ordinal`
- `step_kind` — `announcement`, `approval-match`, `seat-template`, `policy-pin`, `claim`, `placement-suggestion`, `bind`, `materialization`, `manual-hide`, `blocker`
- `effect_kind` — `explanatory-only`, `admitted-lower-friction`, `drafted`, `committed`, `prevented`, `unchanged`
- `summary`
- `source_ref`
- `receipt_ref` nullable

### `arrival_counterfactual`

Explains what stage and next action would differ under one narrower or broader governing fact.

Suggested fields:

- `counterfactual_id`
- `variant_kind` — `no-approval-memory`, `narrower-template`, `different-default-root`, `pinned-away`, `fresh-review-required`, `no-collision`, `seat-changed`
- `predicted_stage`
- `predicted_next_action`
- `difference_summary`

### Routes

```text
GET  /v1/seats/{seat_id}/arrivals/{subject_ref}/explanation
GET  /v1/arrival-explanations/{arrival_explanation_id}
GET  /v1/arrival-explanations/{arrival_explanation_id}/trace
GET  /v1/arrival-explanations/{arrival_explanation_id}/counterfactuals
GET  /v1/arrival-explanations/{arrival_explanation_id}/receipts
```

### Required answers

The explanation endpoints should be able to answer at least:

- why the subject is visible on this seat now
- whether remembered approval or standing template merely lowered friction or actually changed local state
- whether a drafted candidate path exists without a committed bind
- what one narrower governing fact would have changed
- which receipts prove the real local acts that have happened so far

### Events

- `arrival.explanation_viewed`
- `arrival.explanation_recomputed`
- `arrival.counterfactual_requested`


## Policy delta preview additions

### `policy_delta_preview`

A read projection describing the practical effect of one proposed standing-policy change for one seat and governed scope.

Suggested fields:

- `policy_delta_preview_id`
- `seat_ref`
- `governed_scope`
- `current_policy_refs[]`
- `proposed_policy_delta`
- `effect_buckets[]`
- `example_subjects[]`
- `non_effect_guarantees[]`
- `risk_flags[]`
- `computed_at`

### `policy_delta_effect_bucket`

Stable preview bucket for one subject class.

Suggested fields:

- `bucket_kind` — `future-unseen-arrivals`, `announced-unclaimed`, `claimed-unbound`, `bound`, `materialized-bytes`, `approval-memory-and-matches`
- `effect_kind` — `unchanged`, `new-default`, `refresh-optional`, `refresh-required`, `blocked`, `subset-review-required`
- `summary`
- `subject_count` nullable
- `requires_explicit_subject_list`
- `example_subject_refs[]`

### `policy_delta_example_subject`

Concrete named subject used to ground the preview.

Suggested fields:

- `subject_ref`
- `current_stage`
- `predicted_stage_after_apply`
- `change_class` — `unchanged`, `draft-updated`, `needs-manual-review`, `future-only`
- `difference_summary`

### `policy_delta_non_effect_guarantee`

Durable statement of something the proposed standing-policy change definitely does not do.

Suggested fields:

- `guarantee_kind` — `no-rebind`, `no-evict`, `no-auto-claim`, `no-memory-widen`, `no-sibling-withdraw`, `no-current-byte-change`
- `summary`
- `confidence`

### Routes

```text
POST /v1/policy-deltas/previews
GET  /v1/policy-deltas/previews/{policy_delta_preview_id}
GET  /v1/policy-deltas/previews/{policy_delta_preview_id}/effect-buckets
GET  /v1/policy-deltas/previews/{policy_delta_preview_id}/example-subjects
GET  /v1/policy-deltas/previews/{policy_delta_preview_id}/non-effects
GET  /v1/policy-deltas/previews/{policy_delta_preview_id}/simulate/{subject_ref}
POST /v1/policy-deltas/previews/{policy_delta_preview_id}/apply
GET  /v1/policy-deltas/receipts/{receipt_id}
```

### Required answers

The preview endpoints should be able to answer at least:

- what future unseen arrivals will do after the policy change
- whether announced-but-unclaimed drafts remain unchanged or refresh
- whether claimed-but-unbound subjects require stronger subset review
- whether bound shares and current bytes stay untouched
- whether remembered approval scope changes, stays unchanged, or blocks the delta
- which named example subjects illustrate those answers

### Events

- `policy_delta.preview_created`
- `policy_delta.simulation_requested`
- `policy_delta.review_opened`
- `policy_delta.applied`
- `policy_delta.receipt_emitted`



## Standing-policy lineage resources

### Standing policy version

Represents one effective standing-policy snapshot for one reviewed seat/scope.

Suggested fields:

- `standing_policy_version_id`
- `seat_ref`
- `governed_scope`
- `policy_family`
- `version_seq`
- `effective_from`
- `superseded_at` nullable
- `policy_fields`
- `created_by_receipt_ref`
- `superseded_by_version_ref` nullable

### Subject policy attribution

Represents which standing-policy version handled one subject and how it relates to current policy now.

Suggested fields:

- `subject_policy_attribution_id`
- `subject_ref`
- `seat_ref`
- `current_subject_stage`
- `applied_policy_version_ref`
- `current_policy_version_ref`
- `attribution_class`
- `difference_from_current_summary`
- `supporting_receipt_refs[]`

### Policy compare projection

Represents a semantic compare between an applied older version and the current effective version.

Suggested fields:

- `policy_compare_projection_id`
- `older_version_ref`
- `current_version_ref`
- `field_diffs[]`
- `semantic_diffs[]`
- `subject_effect_summary`
- `non_effect_summary`

### Suggested endpoints

- `GET /v1/policy/lineage/{seat_ref}/{scope}`
- `GET /v1/policy/version/{standing_policy_version_id}`
- `GET /v1/policy/attribution/{subject_ref}?seat_ref=...`
- `POST /v1/policy/compare`

### Events

- `policy.version_created`
- `policy.version_superseded`
- `policy.lineage_inspected`
- `policy.attribution_computed`
- `policy.compare_requested`



## Standing-policy drift and realignment resources

### Policy drift row

Represents one current subject's relation to the current effective standing policy.

Suggested fields:

- `policy_drift_row_id`
- `subject_ref`
- `seat_ref`
- `governed_scope`
- `current_subject_stage`
- `current_policy_version_ref`
- `applied_policy_version_ref`
- `drift_class`
- `difference_summary`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Policy drift population

Represents the current divergence population for one seat/scope against one current policy version.

Suggested fields:

- `policy_drift_population_id`
- `seat_ref`
- `governed_scope`
- `current_policy_version_ref`
- `summary_counts`
- `drift_rows[]`
- `generated_at`
- `generation_basis`

### Realignment review plan

Represents one prepared reviewed attempt to refresh or pin a selected drift subset.

Suggested fields:

- `realignment_review_plan_id`
- `seat_ref`
- `governed_scope`
- `target_policy_version_ref`
- `selected_subject_refs[]`
- `selection_classes`
- `requested_outcome`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Subject exception pin

Represents a durable reviewed decision to keep one subject intentionally divergent from current policy.

Suggested fields:

- `subject_exception_pin_id`
- `subject_ref`
- `seat_ref`
- `current_policy_version_ref`
- `kept_applied_policy_version_ref`
- `pin_reason`
- `review_receipt_ref`
- `review_expires_at` nullable

### Suggested endpoints

- `GET /v1/policy/drift/{seat_ref}/{scope}`
- `GET /v1/policy/drift/subjects/{subject_ref}`
- `POST /v1/policy/realignment/review-plans`
- `POST /v1/policy/realignment/review-plans/{realignment_review_plan_id}/apply`
- `POST /v1/policy/exceptions`

### Events

- `policy_drift.population_generated`
- `policy_drift.subject_inspected`
- `policy_realignment.review_plan_created`
- `policy_realignment.applied`
- `policy_exception.pinned`
- `policy_exception.released`


## Exception-aging and re-review resources

### Exception aging row

Represents one intentional non-current subject's current review-horizon posture.

Suggested fields:

- `exception_aging_row_id`
- `subject_ref`
- `seat_ref`
- `governed_scope`
- `current_policy_version_ref`
- `kept_applied_policy_version_ref`
- `exception_kind` (`grandfathered-keep`, `pinned-exception`)
- `aging_class` (`healthy`, `due-soon`, `overdue`, `blocked`, `no-expiry-acknowledged`)
- `review_horizon_at` nullable
- `last_review_receipt_ref`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Exception review population

Represents the current aging queue for one seat/scope.

Suggested fields:

- `exception_review_population_id`
- `seat_ref`
- `governed_scope`
- `summary_counts`
- `aging_rows[]`
- `generated_at`
- `generation_basis`

### Exception renewal review plan

Represents one prepared reviewed attempt to renew, retire, or widen acknowledgement for an intentional exception.

Suggested fields:

- `exception_renewal_review_plan_id`
- `subject_ref`
- `seat_ref`
- `current_policy_version_ref`
- `existing_exception_ref`
- `requested_outcome` (`renew-same-exception`, `return-to-current-policy`, `keep-without-expiry`, `open-stronger-review`)
- `new_review_horizon_at` nullable
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Exception review receipt

Represents the durable result of one renewal or reconsideration review.

Suggested fields:

- `exception_review_receipt_id`
- `subject_ref`
- `seat_ref`
- `previous_exception_ref`
- `outcome`
- `reviewed_at`
- `next_review_horizon_at` nullable
- `no_expiry_acknowledged` boolean
- `proof_refs[]`

### Suggested endpoints

- `GET /v1/policy/exceptions/review/{seat_ref}/{scope}`
- `GET /v1/policy/exceptions/review/subjects/{subject_ref}`
- `POST /v1/policy/exceptions/review-plans`
- `POST /v1/policy/exceptions/review-plans/{exception_renewal_review_plan_id}/apply`
- `POST /v1/policy/exceptions/{subject_exception_pin_id}/acknowledge-no-expiry`

### Events

- `policy_exception.review_population_generated`
- `policy_exception.review_required`
- `policy_exception.renewal_plan_created`
- `policy_exception.renewed`
- `policy_exception.returned_to_current_policy`
- `policy_exception.no_expiry_acknowledged`

## Approval-memory freshness resources

### Approval-memory freshness row

Represents one remembered approval's current trust-freshness posture.

Suggested fields:

- `approval_memory_freshness_row_id`
- `approval_memory_ref`
- `seat_ref`
- `governed_scope`
- `granted_scope_summary`
- `last_explicit_review_at` nullable
- `last_exercised_at` nullable
- `freshness_class`
- `cooling_reasons[]`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Approval-memory freshness population

Represents the current remembered-trust freshness queue for one seat/scope.

Suggested fields:

- `approval_memory_freshness_population_id`
- `seat_ref`
- `governed_scope`
- `summary_counts`
- `freshness_rows[]`
- `generated_at`
- `generation_basis`

### Approval-memory touch-renewal plan

Represents one prepared reviewed attempt to refresh, narrow, freeze, or retire remembered approval.

Suggested fields:

- `approval_memory_touch_renewal_plan_id`
- `approval_memory_ref`
- `seat_ref`
- `governed_scope`
- `current_freshness_class`
- `requested_outcome`
- `proposed_scope_delta` nullable
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Approval-memory freshness receipt

Represents the durable result of one remembered-trust freshness review.

Suggested fields:

- `approval_memory_freshness_receipt_id`
- `approval_memory_ref`
- `seat_ref`
- `previous_freshness_class`
- `outcome`
- `reviewed_at`
- `next_expected_review_at` nullable
- `result_scope_summary`
- `proof_refs[]`

### Suggested endpoints

- `GET /v1/approval/memory/freshness/{seat_ref}/{scope}`
- `GET /v1/approval/memory/freshness/{approval_memory_ref}`
- `POST /v1/approval/memory/touch-renewal-plans`
- `POST /v1/approval/memory/touch-renewal-plans/{approval_memory_touch_renewal_plan_id}/apply`
- `POST /v1/approval/memory/{approval_memory_ref}/freeze`
- `POST /v1/approval/memory/{approval_memory_ref}/require-fresh-next-time`
- `POST /v1/approval/memory/{approval_memory_ref}/revoke`

### Events

- `approval_memory.freshness_population_generated`
- `approval_memory.freshness_inspected`
- `approval_memory.touch_renewal_plan_created`
- `approval_memory.touch_renewed`
- `approval_memory.scope_narrowed`
- `approval_memory.reuse_frozen`
- `approval_memory.fresh_next_time_required`
- `approval_memory.revoked`


## Approval-memory lineage and authorization-trace resources

### Approval-memory trace row

Represents one remembered approval family together with its current effective lineage head.

Suggested fields:

- `approval_memory_trace_row_id`
- `approval_memory_ref`
- `governed_scope`
- `current_lineage_node_ref`
- `origin_receipt_ref`
- `origin_seat_ref`
- `current_freshness_class`
- `current_scope_summary`
- `last_mutation_summary`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Approval-memory lineage node

Represents one reviewed authorization event in remembered-trust history.

Suggested fields:

- `approval_memory_lineage_node_id`
- `approval_memory_ref`
- `predecessor_node_ref` nullable
- `event_kind`
- `acting_seat_ref`
- `acting_identity_epoch_ref`
- `governed_horizon`
- `result_scope_summary`
- `result_freshness_class`
- `receipt_ref`
- `effective_from`

### Approval-memory lineage timeline

Represents the ordered lineage of trust mutations for one remembered-approval family.

Suggested fields:

- `approval_memory_lineage_timeline_id`
- `approval_memory_ref`
- `current_head_ref`
- `nodes[]`
- `generated_at`
- `generation_basis`

### Approval-memory authorization trace explanation

Represents the proof-bearing answer to which lineage node authorized one specific later subject or match.

Suggested fields:

- `approval_memory_authorization_trace_explanation_id`
- `approval_memory_ref`
- `subject_ref`
- `matched_lineage_node_ref`
- `current_head_ref`
- `subject_event_at`
- `authorization_posture_at_match`
- `difference_from_current_head`
- `counterfactual_under_current_head`
- `proof_refs[]`

### Suggested endpoints

- `GET /v1/approval/memory/trace/{seat_ref}/{scope}`
- `GET /v1/approval/memory/trace/{approval_memory_ref}`
- `GET /v1/approval/memory/trace/{approval_memory_ref}/lineage`
- `GET /v1/approval/memory/trace/{approval_memory_ref}/subjects/{subject_ref}`

### Events

- `approval_memory.trace_population_generated`
- `approval_memory.lineage_inspected`
- `approval_memory.authorization_trace_resolved`
- `approval_memory.authorization_trace_unknown`

## Approval-memory constellation-mutation and family-rebase resources

### Approval-memory rebase row

Represents one remembered-approval family whose safe reuse is affected by constellation or identity mutation.

Suggested fields:

- `approval_memory_rebase_row_id`
- `approval_memory_ref`
- `seat_ref`
- `current_head_ref`
- `triggering_mutation_ref`
- `mutation_class`
- `current_family_posture`
- `affected_descendant_count`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Constellation-mutation impact explanation

Represents why one remembered-approval family can no longer be reused as a monolithic trust family without review.

Suggested fields:

- `approval_memory_mutation_impact_explanation_id`
- `approval_memory_ref`
- `triggering_mutation_ref`
- `previous_constellation_summary`
- `current_constellation_summary`
- `identity_epoch_compare`
- `descendant_postures[]`
- `non_effect_summary`
- `proof_refs[]`

### Approval-memory descendant posture

Represents how one descendant seat/member/device currently relates to a remembered-approval family after mutation.

Suggested fields:

- `approval_memory_descendant_posture_id`
- `approval_memory_ref`
- `descendant_ref`
- `descendant_kind`
- `inheritance_posture`
- `why`
- `last_observed_at`
- `proof_refs[]`

### Approval-memory rebase plan

Represents one prepared reviewed attempt to carry forward, split, freeze, or fresh-gate a remembered-approval family after mutation.

Suggested fields:

- `approval_memory_rebase_plan_id`
- `approval_memory_ref`
- `seat_ref`
- `triggering_mutation_ref`
- `requested_outcome`
- `selected_descendant_outcomes[]`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Approval-memory rebase receipt

Represents the durable result of one remembered-trust rebase review.

Suggested fields:

- `approval_memory_rebase_receipt_id`
- `approval_memory_ref`
- `triggering_mutation_ref`
- `outcome`
- `reviewed_at`
- `resulting_family_refs[]`
- `descendant_outcomes[]`
- `proof_refs[]`

### Suggested endpoints

- `GET /v1/approval/memory/rebase/{seat_ref}/{scope}`
- `GET /v1/approval/memory/rebase/{approval_memory_ref}`
- `POST /v1/approval/memory/rebase-plans`
- `POST /v1/approval/memory/rebase-plans/{approval_memory_rebase_plan_id}/apply`

### Events

- `approval_memory.rebase_population_generated`
- `approval_memory.rebase_inspected`
- `approval_memory.rebase_plan_created`
- `approval_memory.family_split_reviewed`
- `approval_memory.descendant_reuse_frozen`
- `approval_memory.descendant_fresh_required`
- `approval_memory.family_revoked`

## Approval-memory descendant-liveness resources

### Approval-memory descendant liveness row

Represents one descendant's current liveness and confidence posture relative to a remembered-approval family.

Suggested fields:

- `approval_memory_descendant_liveness_row_id`
- `approval_memory_ref`
- `seat_ref`
- `descendant_ref`
- `descendant_kind`
- `inheritance_posture`
- `liveness_class`
- `last_live_observed_at`
- `last_byte_source_observed_at`
- `confidence_class`
- `current_expected_role`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Descendant-liveness explanation

Represents why one descendant currently carries a particular liveness/confidence posture.

Suggested fields:

- `approval_memory_descendant_liveness_explanation_id`
- `approval_memory_ref`
- `descendant_ref`
- `liveness_class`
- `confidence_class`
- `evidence_basis`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Descendant-liveness refresh plan

Represents one prepared reviewed attempt to refresh stale descendant knowledge without silently renewing trust scope.

Suggested fields:

- `approval_memory_descendant_liveness_refresh_plan_id`
- `approval_memory_ref`
- `seat_ref`
- `descendant_ref`
- `current_liveness_class`
- `requested_outcome`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Descendant-liveness receipt

Represents the durable result of one reviewed descendant-liveness decision.

Suggested fields:

- `approval_memory_descendant_liveness_receipt_id`
- `approval_memory_ref`
- `descendant_ref`
- `previous_liveness_class`
- `outcome`
- `reviewed_at`
- `resulting_liveness_class`
- `resulting_confidence_class`
- `proof_refs[]`

### Suggested endpoints

- `GET /v1/approval/memory/descendants/{seat_ref}/{scope}`
- `GET /v1/approval/memory/descendants/{approval_memory_ref}`
- `GET /v1/approval/memory/descendants/{approval_memory_ref}/{descendant_ref}`
- `POST /v1/approval/memory/descendant-liveness-plans`
- `POST /v1/approval/memory/descendant-liveness-plans/{approval_memory_descendant_liveness_refresh_plan_id}/apply`

### Events

- `approval_memory.descendant_liveness_population_generated`
- `approval_memory.descendant_liveness_inspected`
- `approval_memory.live_observation_recorded`
- `approval_memory.descendant_marked_historical_only`
- `approval_memory.descendant_reuse_frozen_until_live`
- `approval_memory.descendant_false_reappearance_dismissed`

## Approval-memory descendant-capability resources

### Approval-memory descendant capability row

Represents one descendant's current per-subject role eligibility.

Suggested fields:

- `approval_memory_descendant_capability_row_id`
- `approval_memory_ref`
- `seat_ref`
- `subject_ref`
- `descendant_ref`
- `descendant_kind`
- `liveness_class`
- `candidate_role`
- `eligibility_class`
- `proof_basis`
- `blocking_reason`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Descendant capability explanation

Represents why one descendant currently carries a particular role-eligibility posture for one subject.

Suggested fields:

- `approval_memory_descendant_capability_explanation_id`
- `approval_memory_ref`
- `subject_ref`
- `descendant_ref`
- `candidate_role`
- `eligibility_class`
- `proof_basis`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Descendant capability review plan

Represents one prepared reviewed attempt to tighten or correct descendant capability claims without silently widening trust or materializing bytes.

Suggested fields:

- `approval_memory_descendant_capability_plan_id`
- `approval_memory_ref`
- `seat_ref`
- `subject_ref`
- `descendant_ref`
- `current_candidate_role`
- `current_eligibility_class`
- `requested_outcome`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Descendant capability receipt

Represents the durable result of one reviewed descendant-capability decision.

Suggested fields:

- `approval_memory_descendant_capability_receipt_id`
- `approval_memory_ref`
- `subject_ref`
- `descendant_ref`
- `previous_candidate_role`
- `previous_eligibility_class`
- `outcome`
- `reviewed_at`
- `resulting_candidate_role`
- `resulting_eligibility_class`
- `proof_refs[]`

### Suggested endpoints

- `GET /v1/approval/memory/capability/{seat_ref}/{scope}`
- `GET /v1/approval/memory/capability/{approval_memory_ref}/{subject_ref}`
- `GET /v1/approval/memory/capability/{approval_memory_ref}/{subject_ref}/{descendant_ref}`
- `POST /v1/approval/memory/capability-plans`
- `POST /v1/approval/memory/capability-plans/{approval_memory_descendant_capability_plan_id}/apply`

### Events

- `approval_memory.descendant_capability_population_generated`
- `approval_memory.descendant_capability_inspected`
- `approval_memory.byte_source_proof_recorded`
- `approval_memory.approval_seat_proof_recorded`
- `approval_memory.descendant_marked_explanation_only`
- `approval_memory.subject_reuse_frozen`
- `approval_memory.fresh_approval_required_for_subject`


## Approval-memory reuse-policy precedence resources

### Approval-memory reuse policy row

Represents one governed subject's current relationship to remembered approval reuse.

Suggested fields:

- `approval_memory_reuse_policy_row_id`
- `approval_memory_ref` nullable
- `seat_ref`
- `subject_ref`
- `subject_kind`
- `standing_reuse_candidate`
- `subject_reuse_policy`
- `precedence_outcome`
- `winning_rule_basis`
- `blocking_reason` nullable
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Approval-memory reuse policy explanation

Represents the current explanation for why a governed subject did or did not inherit remembered approval reuse.

Suggested fields:

- `approval_memory_reuse_policy_explanation_id`
- `approval_memory_ref` nullable
- `subject_ref`
- `standing_reuse_candidate`
- `subject_reuse_policy`
- `precedence_outcome`
- `winning_rule_basis`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Approval-memory reuse policy plan

Represents one prepared reviewed attempt to keep, narrow, or override remembered approval reuse for one governed subject.

Suggested fields:

- `approval_memory_reuse_policy_plan_id`
- `approval_memory_ref` nullable
- `seat_ref`
- `subject_ref`
- `current_subject_reuse_policy`
- `current_precedence_outcome`
- `requested_outcome`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Approval-memory reuse policy receipt

Represents the durable result of one reviewed reuse-policy precedence decision.

Suggested fields:

- `approval_memory_reuse_policy_receipt_id`
- `approval_memory_ref` nullable
- `subject_ref`
- `previous_subject_reuse_policy`
- `previous_precedence_outcome`
- `outcome`
- `reviewed_at`
- `resulting_subject_reuse_policy`
- `resulting_precedence_outcome`
- `proof_refs[]`

### Suggested endpoints

- `GET /v1/approval/memory/reuse-policy/{seat_ref}/{scope}`
- `GET /v1/approval/memory/reuse-policy/{approval_memory_ref}/{subject_ref}`
- `POST /v1/approval/memory/reuse-policy-plans`
- `POST /v1/approval/memory/reuse-policy-plans/{approval_memory_reuse_policy_plan_id}/apply`

### Events

- `approval_memory.reuse_policy_population_generated`
- `approval_memory.reuse_policy_inspected`
- `approval_memory.reuse_authorized_for_subject`
- `approval_memory.fresh_approval_required_by_subject_policy`
- `approval_memory.reuse_narrowed_to_reviewed_seat`
- `approval_memory.reuse_marked_explanation_only`


## Offer-artifact trust-promotion resources

### Offer trust-promotion row

Represents what durable trust, if any, survived after one offer artifact was claimed, consumed, expired, or exhausted.

Suggested fields:

- `offer_trust_promotion_row_id`
- `offer_ref`
- `seat_ref`
- `subject_ref`
- `artifact_terminal_posture`
- `claim_outcome`
- `promotion_posture`
- `promotion_scope_basis`
- `later_reuse_posture`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Offer trust-promotion explanation

Represents the current explanation for what durable trust survived after the offer artifact's own redemption lifetime ended.

Suggested fields:

- `offer_trust_promotion_explanation_id`
- `offer_ref`
- `subject_ref`
- `artifact_terminal_posture`
- `claim_outcome`
- `promotion_posture`
- `promotion_scope_basis`
- `later_reuse_posture`
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Offer trust-promotion plan

Represents one prepared reviewed attempt to keep one accepted offer artifact as `subject only`, promote it into broader remembered approval, or freeze it at explanation only.

Suggested fields:

- `offer_trust_promotion_plan_id`
- `offer_ref`
- `seat_ref`
- `subject_ref`
- `current_artifact_terminal_posture`
- `current_promotion_posture`
- `requested_outcome`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Offer trust-promotion receipt

Represents the durable result of one reviewed decision about what long-lived trust survived after one offer artifact was used or expired.

Suggested fields:

- `offer_trust_promotion_receipt_id`
- `offer_ref`
- `subject_ref`
- `previous_artifact_terminal_posture`
- `previous_promotion_posture`
- `outcome`
- `reviewed_at`
- `resulting_promotion_posture`
- `resulting_later_reuse_posture`
- `proof_refs[]`

### Suggested endpoints

- `GET /v1/offers/trust-promotion/{seat_ref}/{scope}`
- `GET /v1/offers/trust-promotion/{offer_ref}/{subject_ref}`
- `POST /v1/offers/trust-promotion-plans`
- `POST /v1/offers/trust-promotion-plans/{offer_trust_promotion_plan_id}/apply`

### Events

- `offer.trust_promotion_population_generated`
- `offer.trust_promotion_inspected`
- `offer.claim_kept_subject_only`
- `offer.claim_promoted_to_reviewed_seat_only`
- `offer.claim_promoted_to_family_reuse_candidate`
- `offer.claim_frozen_explanation_only`
- `offer.fresh_approval_required_next_time`

## Offer recipient-intent and redeemer-identity API contract

Portable-offer inspection is incomplete until the daemon can answer both `what did the sender mean?` and `who actually redeemed this?`.
The API should therefore expose recipient-intent and redeemer-identity resources separately from bare claim status.

Suggested endpoints:

```text
GET  /v1/offers/{offer_id}/recipient-intent
GET  /v1/offers/{offer_id}/recipient-intent/{claim_id}
POST /v1/offers/{offer_id}/recipient-intent/prepare
POST /v1/offers/recipient-intent-plans/{plan_id}/apply
GET  /v1/offer-redeemer-receipts
GET  /v1/offer-redeemer-receipts/{offer_redeemer_receipt_id}
```

Minimum read shape:

- `offer_id`
- `subject_id`
- `recipient_intent_posture`
- `intended_recipient_label`
- `actual_redeemer_ref`
- `actual_redeemer_proof_basis`
- `intent_match_class`
- `mismatch_outcome`
- `resulting_promotion_posture`
- `non_effect_summary`
- `receipt_refs[]`

Rules:

- the daemon must allow clients to inspect recipient-intent state without applying any trust-promotion or mismatch outcome
- a successful claim receipt and a redeemer-intent receipt must remain distinct durable objects even when they were created in one operator session
- API responses must preserve explicit `unknown` values instead of collapsing incomplete provenance into `matched` or `accepted`
- apply must fail loudly if the underlying claim, approval proof, or offer-lifetime posture drifted after the plan was prepared


## Offer redemption-ledger and multi-redeemer trust-fanout API contract

The API should expose artifact-budget state and per-attempt trust consequence separately from bare offer state.

Minimum endpoints:

GET  /v1/offer-redemption-ledgers
GET  /v1/offer-redemption-ledgers/{offer_redemption_ledger_row_id}
GET  /v1/offers/{offer_id}/redemption-attempts
GET  /v1/offer-redemption-attempts/{offer_redemption_attempt_id}
GET  /v1/offer-redemption-budget-explanations/{offer_redemption_budget_explanation_id}
POST /v1/offer-trust-fanout-plans
GET  /v1/offer-trust-fanout-plans/{offer_trust_fanout_plan_id}
POST /v1/offer-trust-fanout-plans/{offer_trust_fanout_plan_id}/apply
GET  /v1/offer-redemption-ledger-receipts
GET  /v1/offer-redemption-ledger-receipts/{offer_redemption_ledger_receipt_id}

Minimum fields across these resources:

- `offer_ref`
- `artifact_budget_class`
- `redemption_limit_total`
- `redemption_count_consumed`
- `redemption_count_remaining`
- `artifact_terminal_posture`
- `actual_redeemer_ref`
- `actual_redeemer_proof_basis`
- `attempt_outcome_class`
- `budget_effect`
- `resulting_trust_posture`
- `recommended_next_action`
- `receipt_refs[]`

Rules:

- the ledger row and each attempt entry must remain separately addressable resources
- a budget explanation must be able to point to the last budget-consuming attempt
- a successful claim receipt and a later trust-fanout receipt must remain distinct durable objects even when they were created in one review session
- later remembered approval lineage must be able to reference one exact `offer_redemption_attempt_id`, not only the parent `offer_id`

## Offer redemption-equivalence and slot-accounting API contract

The API should expose equivalence judgment and slot treatment separately from raw redemption attempts.

Minimum endpoints:

GET  /v1/offer-redemption-equivalence-rows
GET  /v1/offer-redemption-equivalence-rows/{offer_redemption_equivalence_row_id}
GET  /v1/offer-redemption-equivalence-explanations/{offer_redemption_equivalence_explanation_id}
POST /v1/offer-slot-accounting-plans
GET  /v1/offer-slot-accounting-plans/{offer_slot_accounting_plan_id}
POST /v1/offer-slot-accounting-plans/{offer_slot_accounting_plan_id}/apply
GET  /v1/offer-slot-accounting-receipts
GET  /v1/offer-slot-accounting-receipts/{offer_slot_accounting_receipt_id}

Minimum fields across these resources:

- `offer_ref`
- `subject_ref`
- `current_attempt_ref`
- `comparison_attempt_ref`
- `equivalence_class`
- `budget_accounting_policy`
- `slot_effect`
- `resulting_trust_posture`
- `recommended_next_action`
- `receipt_refs[]`

Rules:

- the equivalence row must stay separately addressable from the raw redemption-attempt entry
- one slot-accounting receipt may reference both the current attempt and the comparison attempt, but must not overwrite either attempt object
- clients must be able to render `same reviewed seat -> collapse` and `same known peer, new subject -> consume new slot` without inventing local heuristics
- later trust lineage must be able to reference one exact slot-accounting receipt when budget treatment matters to explanation


## Offer reissue-lineage and successor-boundary API contract

```text
GET  /v1/offer-reissue-lineage-rows
GET  /v1/offer-reissue-lineage-rows/{offer_reissue_lineage_row_id}
GET  /v1/offer-reissue-boundary-explanations/{offer_reissue_boundary_explanation_id}
POST /v1/offer-reissue-plans
GET  /v1/offer-reissue-plans/{offer_reissue_plan_id}
POST /v1/offer-reissue-plans/{offer_reissue_plan_id}/apply
GET  /v1/offer-successor-boundary-receipts/{offer_successor_boundary_receipt_id}
```

Rules:

- `offer-reissue-lineage-rows` must make predecessor posture, successor relation, budget reset posture, and recommended next action available without forcing clients to diff two raw offer manifests manually
- `offer-reissue-boundary-explanations` must say what carried forward and what definitely did not
- `offer-reissue-plans` must reject ambiguous `delivery-only` requests when scope, budget, or policy drift means the successor is actually semantically new
- successor-boundary receipts must remain readable even if both predecessor and successor later expire, are revoked, or disappear from default active lists


## Revision addendum — delivery events and preview-authority surfaces

Portable-offer intake now needs one additional public surface before claim or approval objects take over.
The daemon/API should therefore expose delivery events as first-class read objects.

Minimum additions:

```text
GET    /v1/offer-delivery-events
GET    /v1/offer-delivery-events/{delivery_event_id}
GET    /v1/offer-delivery-events/{delivery_event_id}/explain
POST   /v1/offer-delivery-events/{delivery_event_id}/inspect
POST   /v1/offer-delivery-events/{delivery_event_id}/prepare-review
GET    /v1/offer-delivery-handoff-receipts
GET    /v1/offer-delivery-handoff-receipts/{receipt_id}
```

A delivery event object should at minimum name:

- delivery channel
- preview surface
- preview fields
- external-touch posture
- handoff posture
- preview-authority posture
- authoritative offer reference if local parsing already succeeded

Event stream additions:

- `offer.delivery_event_observed`
- `offer.delivery_preview_recorded`
- `offer.delivery_handoff_completed`
- `offer.delivery_authority_posture_changed`
- `offer.delivery_handoff_receipt_issued`


## Revision addendum — carrier alias and canonical-artifact resources

Portable-offer intake now needs one additional public surface after delivery provenance but before later budget/trust reasoning fully makes sense.
The daemon/API should therefore expose carrier aliases and canonical artifact identity as first-class read objects.

Minimum additions:

```text
GET    /v1/offer-carrier-aliases
GET    /v1/offer-carrier-aliases/{carrier_alias_id}
GET    /v1/offers/{offer_id}/carrier-aliases
GET    /v1/offers/{offer_id}/canonical-identity-explain
POST   /v1/offer-carrier-alias-plans
GET    /v1/offer-carrier-alias-plans/{plan_id}
POST   /v1/offer-carrier-alias-plans/{plan_id}/apply
GET    /v1/offer-carrier-alias-receipts
GET    /v1/offer-carrier-alias-receipts/{receipt_id}
```

A carrier-alias object should at minimum name:

- canonical offer reference when known
- carrier kind
- carrier authority posture
- equivalence posture
- normalization basis
- related delivery event reference when present

Event stream additions:

- `offer.carrier_alias_observed`
- `offer.canonical_identity_compared`
- `offer.delivery_wrapper_collapsed_into_canonical`
- `offer.authority_bearing_alias_recorded`
- `offer.alias_treated_as_successor`
- `offer.carrier_alias_receipt_issued`


## Revision addendum — field-provenance and field-partition resources

Portable-offer intake now needs one additional public surface after carrier-alias identity but before later governance reasoning is honest enough.
The daemon/API should therefore expose preview-hint provenance and sealed-authority field partition as first-class read objects.

Minimum additions:

```text
GET    /v1/offer-field-provenance-rows
GET    /v1/offer-field-provenance-rows/{row_id}
GET    /v1/offers/{offer_id}/field-provenance
GET    /v1/offers/{offer_id}/field-partition-explain
POST   /v1/offer-field-partition-plans
GET    /v1/offer-field-partition-plans/{plan_id}
POST   /v1/offer-field-partition-plans/{plan_id}/apply
GET    /v1/offer-field-partition-receipts
GET    /v1/offer-field-partition-receipts/{receipt_id}
```

A field-provenance row should at minimum name:

- canonical offer reference when known
- carrier alias reference when relevant
- field semantic role
- field exposure posture
- field authority posture
- seen-on surfaces
- eligible and ineligible later inferences

Event stream additions:

- `offer.preview_hint_field_observed`
- `offer.sealed_field_declared`
- `offer.local_parse_promoted_field_authority`
- `offer.field_partition_compared`
- `offer.preview_hint_marked_non_authoritative`
- `offer.field_partition_receipt_issued`


## Revision addendum — preview-sufficiency and omission-aware intake objects

Portable-offer intake APIs should now expose a dedicated preview-sufficiency layer in addition to delivery provenance and field-partition truth.

Suggested read models:

- `offer_preview_sufficiency_row`
- `offer_preview_omission_explanation`
- `offer_preview_sufficiency_plan`
- `offer_preview_sufficiency_receipt`

Minimum fields should include:

- preview fields shown
- omitted governance fields
- sufficiency by decision domain (`recognition`, `routing`, `governance`, `trust`)
- unsafe inferences refused
- next honest action

CLI and API clients must be able to render `recognition sufficient but governance insufficient` without inventing their own policy heuristics.
## Offer decision-ladder and card projections

The daemon/API should expose first-class read models for portable-offer decision ladders and dense/full projections so lightweight clients do not reconstruct them ad hoc.

Suggested read models:

### `offer_decision_ladder_row`

Fields should include at least:

- `delivery_event_ref`
- `offer_ref` nullable
- `claim_ref` nullable
- `current_rung`
- `previous_rung` nullable
- `newly_available_facts[]`
- `still_blocked_facts[]`
- `enough_for[]`
- `not_enough_for[]`
- `recommended_next_action`
- `receipt_refs[]`

### `portable_offer_card_projection`

Fields should include at least:

- `identity_summary`
- `visibility_summary`
- `missing_summary`
- `enough_for_summary`
- `not_enough_for_summary`
- `next_action_summary`
- `receipt_summary`
- `urgency_class`
- `batch_class`

### `portable_offer_detail_projection`

Fields should include at least:

- `what_arrived`
- `what_was_visible_by_stage[]`
- `what_is_missing[]`
- `current_decision_scope`
- `blocked_decision_scope`
- `current_ladder_rung`
- `next_honest_action`
- `proof_refs[]`

API rule:

- clients may render these objects with different density
- clients may not omit `missing`, `not enough for`, or `next honest action` while still claiming parity for portable-offer surfaces


## Offer-composer and issuance resources

### `offer_composer_draft`

A mutable sender-side object for composing a portable offer before review and issue.
It should expose audience scope, preview-field policy, sealed-field policy, offered role, approval policy, expiry policy, and redemption budget.

### `offer_issuance_review`

A review object projecting the exact issuance meaning before an artifact is emitted.
It should distinguish effect from non-effect and promise the later issuance receipt.

### `offer_issuance_receipt`

A durable proof of what artifact was issued, to what audience posture, under which preview/governance/redemption contract.

### Suggested endpoints

```text
GET    /v1/offers/drafts
POST   /v1/offers/drafts
GET    /v1/offers/drafts/{draft_id}
PATCH  /v1/offers/drafts/{draft_id}
POST   /v1/offers/drafts/{draft_id}:review
POST   /v1/offers/drafts/{draft_id}:issue
GET    /v1/offers/issuance-reviews/{review_id}
GET    /v1/offers/issuance-receipts/{receipt_id}
```

## Constellation-publication resources

### `publication_row`

A per-subject/per-target summary of who can currently see a subject through reviewed publication and with what arrival posture.

### `publication_review_plan`

A reviewed change object for widening, narrowing, or withdrawing publication scope on one subject.

### `publication_receipt`

A durable receipt proving that one subject was published to one member, member class, or named set with one declared arrival posture and authority summary.

### Suggested endpoints

```text
GET    /v1/publications
GET    /v1/publications/{subject_id}
POST   /v1/publications:review
GET    /v1/publication-plans/{plan_id}
POST   /v1/publication-plans/{plan_id}:apply
GET    /v1/publication-receipts/{receipt_id}
```

### Event additions

- `offer.draft.created`
- `offer.issuance.reviewed`
- `offer.issued`
- `publication.reviewed`
- `publication.applied`
- `publication.withdrawn`


## Publication-matrix resources

### `publication_matrix_view`

A read projection over current publication truth across some subject/member scope.
It should be explainable enough that clients do not need to reconstruct the matrix from historical receipts.

### `publication_matrix_cell`

A compact explanation of one `(subject, member)` cell, including current state, provenance kind, authority effect, unresolved local work, and latest establishing receipt.

### `publication_override_review`

A reviewed change object for overriding or reverting one cell without pretending to rewrite the whole matrix.

### Suggested endpoints

```text
GET    /v1/publications/matrix
GET    /v1/publications/matrix/cells/{cell_id}
POST   /v1/publications/matrix/cells:review-override
GET    /v1/publication-overrides/{review_id}
GET    /v1/publication-override-receipts/{receipt_id}
```

## Role-first arrival resources

### `arrival_role_sheet`

A review object that states the admissible roles for one subject on one member before path or materialization choice occurs.

### `path_materialization_review_plan`

A plan object prepared only after role selection.
It keeps role, path, and byte posture separate while still letting clients render them together.

### `arrival_adoption_receipt`

A durable proof of the role chosen and the later local path/materialization posture that followed from it.

### Suggested endpoints

```text
GET    /v1/arrivals/rolesheets/{sheet_id}
POST   /v1/arrivals:review-role
POST   /v1/arrivals:prepare-adoption
POST   /v1/arrival-plans/{plan_id}:apply
GET    /v1/arrival-receipts/{receipt_id}
```

### Event additions

- `publication.matrix.generated`
- `publication.cell.overridden`
- `arrival.role.reviewed`
- `arrival.adoption.prepared`
- `arrival.adopted`


## Publication-delta preview resources

### `publication_delta_preview`

A counterfactual projection over the exact `(subject, member)` cells that would change if one publication, template, or related policy edit were applied.

### `affected_cell_delta_row`

A compact row describing one changed or explicitly unchanged cell, including before/after posture, authority delta, local-work delta, and provenance notes.

### Suggested endpoints

```text
POST   /v1/publications:preview-delta
GET    /v1/publication-deltas/{delta_id}
GET    /v1/publication-deltas/{delta_id}/cells
POST   /v1/publication-deltas/{delta_id}:apply
GET    /v1/publication-delta-receipts/{receipt_id}
```

## Member-policy resources

### `member_policy_card`

A read projection over one member's future-arrival defaults, default roots, admissible auto-staging posture, exception lineage, and latest receipts.

### `member_policy_review`

A reviewed object for changing one member's defaults without pretending to rewrite current publication state.

### Suggested endpoints

```text
GET    /v1/members/{member_id}/policy
POST   /v1/members/{member_id}/policy:review
GET    /v1/member-policy-reviews/{review_id}
POST   /v1/member-policy-reviews/{review_id}:apply
GET    /v1/member-policy-receipts/{receipt_id}
```

### Event additions

- `publication.delta.previewed`
- `publication.delta.applied`
- `member.policy.reviewed`
- `member.policy.updated`


## Approval reapproval resources

### `approval_memory_material_change_row`

A compact row describing one remembered approval, one material trigger or due clock, and the current reuse posture.

### `approval_memory_reapproval_review`

A reviewed object for deciding whether one trigger leads to same-scope reapproval, narrowed reapproval, reuse freeze, revocation, or reviewed non-material carry-forward.

### Suggested endpoints

```text
GET    /v1/approval-memories/{memory_id}/reapproval
POST   /v1/approval-memories/{memory_id}:prepare-reapproval
GET    /v1/approval-reviews/{review_id}
POST   /v1/approval-reviews/{review_id}:apply
GET    /v1/approval-reapproval-receipts/{receipt_id}
```

## Shareable-artifact head-register resources

### `shareable_artifact_head_row`

A compact row describing one retained artifact family together with its operational head, shareable head, and blocking warnings.

### `shareable_artifact_head_register`

A register summarizing current heads for one scope such as outgoing packets or active portable artifacts.

### Suggested endpoints

```text
GET    /v1/artifact-heads
GET    /v1/artifact-heads/{family_id}
POST   /v1/artifact-heads/{family_id}:freeze-current
GET    /v1/shareable-head-receipts/{receipt_id}
```


## Approval coordination resources

### `approval_seat_roster_row`

A compact row describing one seat that remains relevant to a current approval together with current eligibility and request state.

### `approval_active_request_row`

A compact row describing one explicit live request (or rerequest-needed state) for one seat against one current basis.

### Suggested endpoints

```text
GET    /v1/approvals/{approval_request_id}/coordination
GET    /v1/approvals/{approval_request_id}/roster
POST   /v1/approvals/{approval_request_id}/requests:open
POST   /v1/approvals/{approval_request_id}/requests:rerequest
POST   /v1/approvals/{approval_request_id}/requests:clear
GET    /v1/approval-coordination-receipts/{receipt_id}
```


## External-guidance frozen-basis resources

### `external_guidance_source_row`

A compact row describing one live outside source locator together with current authority posture, fetch-path class, and current live-source state.

### `guidance_fetch_snapshot`

A durable locally retained copy of what the product actually fetched or ingested at one moment.

### `frozen_guidance_basis_row`

A compact row describing one exact excerpt or clause set from a specific snapshot that local translation may rely on.

### Suggested endpoints

```text
GET    /v1/guidance/{guidance_id}/sources
POST   /v1/guidance/{guidance_id}/snapshots:fetch
GET    /v1/guidance-snapshots/{snapshot_id}
POST   /v1/guidance/{guidance_id}/basis:freeze
GET    /v1/guidance-basis/{basis_id}
POST   /v1/guidance/{guidance_id}:check-drift
GET    /v1/guidance-drift-checks/{check_id}
GET    /v1/guidance-basis-receipts/{receipt_id}
```


## Runtime-status bridge resources

### `runtime_status_bridge`

A lightweight proof surface joining current seat readiness, runtime health, control-entry posture, strongest blocker, and explicit escalation boundary.

### `bridge_probe_row`

A compact machine-readable fact row describing one probe family that contributed to a bridge verdict.

### Suggested endpoints

```text
GET    /v1/system/status-bridge
GET    /v1/seats/{seat_id}/status-bridge
GET    /v1/subjects/{subject_id}/status-bridge
POST   /v1/status-bridges/{bridge_id}:refresh
GET    /v1/status-bridge-receipts/{receipt_id}
```


## Follow-through coverage resources

### `followthrough_case`

A durable object describing one requested repair or unblock path whose completion may stop at request-only, source-only, or partial-effect truth.

### `fix_claim_boundary_row`

A compact row stating what the product may honestly claim now and which required steps remain before a stronger claim is allowed.

### Suggested endpoints

```text
GET    /v1/followthrough/{case_id}
GET    /v1/followthrough/{case_id}/requested-steps
GET    /v1/followthrough/{case_id}/source-execution
GET    /v1/followthrough/{case_id}/effect-observations
POST   /v1/followthrough/{case_id}:refresh-effect
GET    /v1/followthrough-receipts/{receipt_id}
```

## Outbound channel execution resources

### `outbound_channel_execution`

A durable object describing one reviewed attempt to move one frozen shareable artifact through one channel while preserving the current claim ceiling.

### `delivery_witness_row`

A compact row describing the strongest currently known evidence beyond local channel completion.

### Suggested endpoints

```text
GET    /v1/outbound-executions/{execution_id}
GET    /v1/outbound-executions/{execution_id}/witnesses
POST   /v1/artifacts/{artifact_id}/outbound-executions:prepare
POST   /v1/outbound-executions/{execution_id}:record-local-completion
POST   /v1/outbound-executions/{execution_id}:import-witness
GET    /v1/outbound-execution-receipts/{receipt_id}
```

## Imported recipient-acknowledgment binding resources

### `recipient_ack_binding_row`

A durable object describing one imported acknowledgment against one artifact family and one target scope, including sender match, conversation continuity, acknowledged object kind, binding exactness, and current claim ceiling.

### `ack_binding_receipt`

A durable receipt describing one classification or upgrade of imported acknowledgment exactness for one artifact family / target scope pair.

### Suggested endpoints

```text
GET    /v1/artifact-acks/{family_id}
GET    /v1/artifact-acks/{family_id}?target={target_scope}
POST   /v1/artifact-acks/{family_id}:import
POST   /v1/artifact-acks/{family_id}:classify
GET    /v1/ack-binding-receipts/{receipt_id}
```


## Imported acknowledgment scope/delegation resources

### `recipient_ack_scope_row`

A durable object describing one imported acknowledgment against one expected target scope, including raw actor, visible reply lane, relation to target, delegation evidence, represented scope, and current audience ceiling.

### `ack_scope_receipt`

A durable receipt describing one classification or upgrade of imported acknowledgment actor-scope/delegation truth for one artifact family / target scope pair.

### Suggested endpoints

```text
GET    /v1/artifact-ack-scopes/{family_id}
GET    /v1/artifact-ack-scopes/{family_id}?target={target_scope}
POST   /v1/artifact-ack-scopes/{family_id}:import
POST   /v1/artifact-ack-scopes/{family_id}:classify
GET    /v1/ack-scope-receipts/{receipt_id}
```


## Imported acknowledgment authorship / automation resources

### `recipient_ack_authorship_row`

A durable object describing one imported acknowledgment against one expected target scope, including authorship class, automation kind, human-material presence, human-proof strength, and current authorship claim ceiling.

### `ack_authorship_receipt`

A durable receipt describing one classification or upgrade of imported acknowledgment authorship / automation truth for one artifact family / target scope pair.

### Suggested endpoints

```text
GET    /v1/artifact-ack-authorship/{family_id}
GET    /v1/artifact-ack-authorship/{family_id}?target={target_scope}
POST   /v1/artifact-ack-authorship/{family_id}:import
POST   /v1/artifact-ack-authorship/{family_id}:classify
GET    /v1/ack-authorship-receipts/{receipt_id}
```

## Imported reply-stance / follow-up resources

### `recipient_reply_stance_row`

A durable object describing the current semantic stance of one imported reply against one artifact family and one target scope, including clarification/request-changes/redirect/conditional/decline posture plus smallest honest follow-up class.

### `reply_stance_receipt`

A durable receipt describing one classification or upgrade of imported reply stance / follow-up truth for one artifact family / target scope pair.

### Suggested endpoints

```text
GET    /v1/artifact-reply-stances/{family_id}
GET    /v1/artifact-reply-stances/{family_id}?target={target_scope}
POST   /v1/artifact-reply-stances/{family_id}:import
POST   /v1/artifact-reply-stances/{family_id}:classify
GET    /v1/reply-stance-receipts/{receipt_id}
```

## Imported reply referent-slice / coverage resources

### `recipient_reply_referent_slice_row`

A durable object describing what portion of one outward artifact family an imported reply actually referred to, including quoted-excerpt scope, named subobject scope, request-coverage ceiling, and remainder posture.

### `reply_referent_slice_receipt`

A durable receipt describing one classification or upgrade of imported reply referent-slice / request-coverage truth for one artifact family / target scope pair.

### Suggested endpoints

```text
GET    /v1/artifact-reply-referents/{family_id}
GET    /v1/artifact-reply-referents/{family_id}?target={target_scope}
POST   /v1/artifact-reply-referents/{family_id}:import
POST   /v1/artifact-reply-referents/{family_id}:classify
GET    /v1/reply-referent-receipts/{receipt_id}
```

## Imported reply-series head resources

### `recipient_reply_series_row`

A durable object describing the current operative reply state for one artifact family / target scope partition, including latest arrival, current whole-artifact head, current subset heads, superseded replies, and contradiction warnings.

### `reply_series_head_receipt`

A durable receipt describing one rebuild or reclassification of imported reply-series currentness for one artifact family / target scope partition.

### Suggested endpoints

```text
GET    /v1/artifact-reply-series/{family_id}
GET    /v1/artifact-reply-series/{family_id}?target={target_scope}
POST   /v1/artifact-reply-series/{family_id}:rebuild
POST   /v1/artifact-reply-series/{family_id}:classify-head
GET    /v1/reply-series-head-receipts/{receipt_id}
```

## Artifact carryforward and refresh-notice resources

### `shareable_artifact_carryforward_profile`

A compact comparison object describing whether one earlier shared artifact still stands, refreshes in place, must be replaced, or must be reopened against the current family head.

### `shareable_artifact_delta_ledger`

A durable ledger of changed and explicitly unchanged field families for one comparison basis and one candidate/current shareable head.

### `artifact_refresh_notice`

A reviewed audience-safe visible wrapper summarizing what changed since the comparison basis without replacing the deeper delta or lineage surfaces.

### Suggested endpoints

```text
GET    /v1/artifact-carryforward/{family_id}
GET    /v1/artifact-carryforward/{family_id}?compared_to={artifact_id}
GET    /v1/artifact-carryforward/{family_id}/delta-ledger
POST   /v1/artifact-carryforward/{family_id}:prepare-refresh-notice
GET    /v1/artifact-refresh-notices/{notice_id}
POST   /v1/artifact-refresh-notices/{notice_id}:issue
GET    /v1/artifact-refresh-notice-receipts/{receipt_id}
```


## Startup-owner resources

### `startup_owner_snapshot`

A durable object describing the currently reviewed startup-owner truth for one node, including candidate owner lanes, effective-owner verdict, runtime correlation, and recent drift state.

### `startup_owner_receipt`

A durable receipt describing one observed or reviewed change in startup ownership, including duplicate introduction/clearance, owner loss/restoration, or runtime-correlation recovery.

### Suggested endpoints

```text
GET    /v1/startup-owner
GET    /v1/startup-owner/history
POST   /v1/startup-owner:refresh
POST   /v1/startup-owner:review
GET    /v1/startup-owner-receipts/{receipt_id}
```


## Reviewed-action basis-guard resources

### `reviewed_action_basis_guard`

A durable object describing the expected-versus-current basis for one reviewed action together with the current execution verdict.

### `stale_action_attempt_receipt`

A durable receipt proving that one attempted issue/apply/enqueue/disclose action was refused or downgraded because its reviewed basis no longer matched current state.

### `reissue_receipt`

A durable receipt proving that one newer reviewed action explicitly replaced an older stale one on a newer basis.

### Suggested endpoints

```text
GET    /v1/reviewed-actions/{action_id}/basis-guard
POST   /v1/reviewed-actions/{action_id}/basis-guard:refresh
POST   /v1/reviewed-actions/{action_id}:reissue
GET    /v1/stale-action-attempt-receipts/{receipt_id}
GET    /v1/reissue-receipts/{receipt_id}
```


## Reviewed recipient-target guard resources

### `reviewed_action_target_guard`

A durable object describing the expected-versus-current recipient or disclosure target for one reviewed action together with the current retarget verdict.

### `stale_target_attempt_receipt`

A durable receipt proving that one attempted send / issue / disclose action was refused or downgraded because its reviewed target no longer matched current destination state.

### `retarget_reissue_receipt`

A durable receipt proving that one newer reviewed action explicitly replaced an older stale-target action on a different recipient or audience target.

### Suggested endpoints

```text
GET    /v1/reviewed-actions/{action_id}/target-guard
POST   /v1/reviewed-actions/{action_id}/target-guard:refresh
POST   /v1/reviewed-actions/{action_id}:retarget-reissue
GET    /v1/stale-target-attempt-receipts/{receipt_id}
GET    /v1/retarget-reissue-receipts/{receipt_id}
```


## Issued-artifact correction resources

### `issued_artifact_correction_register`

A durable object describing one already-issued outward artifact family for one recipient or audience together with the active correction notice, any replacement already issued, and the current residual-reliance posture.

### `artifact_correction_notice`

A frozen outward-facing notice telling one recipient or audience how to interpret one older issued artifact now.

### `correction_transition_receipt`

A durable receipt describing one change in outward correction posture, such as notice issue, replacement issue, or recipient acknowledgment import.

### Suggested endpoints

```text
GET    /v1/artifact-corrections/{family_id}
GET    /v1/artifact-corrections/{family_id}?target={target_id}
POST   /v1/artifact-corrections/{family_id}:prepare-notice
GET    /v1/artifact-correction-notices/{notice_id}
POST   /v1/artifact-correction-notices/{notice_id}:issue
POST   /v1/artifact-corrections/{family_id}:import-ack
GET    /v1/artifact-correction-transition-receipts/{receipt_id}
```

## Artifact disclosure-register resources

### `artifact_disclosure_register`

A durable object describing one retained artifact family for one recipient or audience together with the current shareable head, any queued issue item, the latest executed issue event, and the current issued/disclosed head now outwardly in force.

### `artifact_issue_queue_item`

A prepared or queued outward-action object describing which frozen head is intended for which target, under which basis and target guards, before execution actually occurs.

### `issued_surface_snapshot`

A frozen recipient-facing or public-facing wrapper proving what surface became current for one target or audience after one executed issue event.

### Suggested endpoints

```text
GET    /v1/artifact-disclosure/{family_id}
GET    /v1/artifact-disclosure/{family_id}?target={target_id}
POST   /v1/artifact-disclosure/{family_id}:prepare-issue
GET    /v1/artifact-issue-queue/{queue_item_id}
POST   /v1/artifact-issue-queue/{queue_item_id}:record-execution
GET    /v1/issued-surface-snapshots/{snapshot_id}
GET    /v1/artifact-disclosure-transition-receipts/{receipt_id}
```

