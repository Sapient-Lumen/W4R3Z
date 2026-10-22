# ViewFS core schema v0

Revision 155 introduced this file as a compression point for ViewFS. Revision 156 extended it from “authority carriers only” into lifecycle lanes for mutable commits, revocation, retention, action plans, and portal replay. Revision 157 added adversarial resolver nodes, delegated authority chains, shell-card honesty, and copy-inventory cleanup. Revision 158 added quarantine capsules, trust transitions, authority diffs, export plans, and generated conformance reporting. Revision 159 added policy bundles, policy decisions, witness bundles, replay scenarios, override warrants, and a policy-trace report. Revision 160 added distributed freshness, leases, offline branches, merge plans, remote attestations, and checkpoints. Revision 161 added disclosure and observation lanes. Revision 162 adds shared rooms, mount edges, group memberships, label overlays, handoff packets, collaboration cards, and a collaboration trace report. Revision 163 adds GC, snapshot, archive-hold, backup, restore, deletion-claim, and sanitization-proof lanes. Revision 164 adds package envelopes, dependency pins, provenance attestations, transparency entries, verifier roots, extension manifests, tool schemas, tool bindings, install plans, sandbox profiles, and supply-chain trace reporting. The goal is still not a final ABI. The goal is a small vocabulary that can be checked by fixtures before ViewFS grows more nouns.

## Design posture

ViewFS is a capability graph with projections. Paths, search results, shell cards, prompts, receipts, indexes, and recents are projections over authority. They may guide selection, explanation, rendering, or replay, but they are not the authority substrate.

A fixture should make every authority transition explicit:

1. what object or work surface is being addressed;
2. what current authority carrier is being used;
3. what cut, if any, approves the effect;
4. what record remains afterward;
5. what non-authority artifacts are visible but inert.

## Record families

| Record | Minimum fields | Authority role | Non-collapse rule |
|---|---|---|---|
| `ObjCore` | `id`, `kind`, `digest`, optional `shape` | Names committed object identity. | An object core is not a live open, not a view placement, and not proof of possession. |
| `ObjRef` | `id`, `object`, `ref_class`, optional `issuer`, `status` | Durable, descriptive, or restore-style reference to an object core. | A ref is not a handle and cannot read, write, export, execute, retain, or publish by itself. |
| `Handle` | `id`, `object`, `rights`, `status`, optional `caveats` | The primary current authority carrier. | Duplication may preserve or narrow rights; attenuation must never widen rights. Revoked handles remain inspectable but inert. |
| `LiveFacet` | `id`, `handle`, `facet`, `status` | Operation-shaped live access derived from a handle. | A facet dies with the handle or with its own status/caveat expiry. |
| `ViewRoot` | `id`, `owner`, `binds` | A per-process synthetic namespace assembled from explicit binds. | A view is not global filesystem truth and cannot invent authority absent from its binds. |
| `Bind` | `path`, `handle`, optional `mount_flags` | Places a live handle inside one view. | A bind path is not object identity and does not travel to another view unless explicitly copied. |
| `PortalGrant` | `id`, `issuer`, `subject`, `rights`, `lifetime`, `status`, `result_handle` | Mediated import/export/adoption boundary. | A portal request, preview, old grant, or receipt is not a current grant; replay and spent states must fail closed. |
| `Delegation` | `id`, `source_handle`, `child_handle`, `attenuation_envelope`, `lease`, `status` | Current or historical handoff of narrowed authority through a membrane. | Delegation intent, delegated handle, lease status, revocation wavefront, and history receipt are distinct; delegation never widens rights. |
| `CompatPathwalk` | `view`, `root`, `path`, `flags`, `verdict` | Compatibility membrane over held view authority. | Path text may select a bound handle, but it cannot escape the view or fall back to host ambient root. |
| `PathNode` | `id`, `view`, `path`, `kind`, optional `target` | Resolver witness for symlink, magic/synthetic, mount, blocked, or ordinary path nodes inside one view. | A path node is not a bind and not authority; it only records why a pathwalk may fail or continue. |
| `DerivedArtifact` | `id`, `source`, `artifact_class`, `scope`, `retention`, optional `current_handle` | Search/index/summary/OCR/answer material. | A derived artifact is not source authority, not a retention root unless pinned, and not future agent memory by default. |
| `CopyInventory` | `id`, `source`, `entries` | Cleanup/minimization ledger for derived artifacts, embeddings, answer caches, excerpts, thumbnails, and exported copies. | Forgetting a source is not complete merely because the source object is gone; derived rows need their own cleanup state. |
| `InstructionFrame` | `id`, `source`, `priority`, `scope`, `content_digest` | Prompt/context/tool-description provenance. | Instruction-like text may propose; it is not policy, approval, current fact, or tool authority. |
| `ActionPlan` | `id`, `typed`, `effect`, `target`, `approval_cut` | Prepared effectful operation. | A model proposal or prompt sentence is not an action plan; an action plan still needs approval and current authority. |
| `ConsentChain` | `candidate`, `summary`, `presentation`, `trusted_path`, `gesture`, `volition`, `approval_cut` | Human approval ceremony evidence. | Gesture evidence, focus state, prompt replies, and receipts cannot substitute for an approval cut over the exact candidate. |
| `MutableSession` | `id`, `base_object`, `current_head`, `write_handle`, `journal`, `commit_cut` | Writable work-in-progress lane. | A journal, buffer, repair plan, or local overlay is not committed object identity. Commit requires current-base validation. |
| `RevocationEvent` | `id`, `target`, `class`, `restore_allowed`, `time` | Authority death/stale-brake evidence. | Revocation blocks current or future use; it does not erase past receipts or pretend past reads did not happen. |
| `RetentionRoot` | `id`, `object`, `root_class`, `status`, `issuer` | Explicit reason an object survives sweep. | Receipts, answer cards, derived-only indexes, and old grants are not roots unless promoted by policy. |
| `ShellCard` | `id`, `subject`, `subject_class`, `authority_badge`, optional `authority_slot`, optional `retention_badge` | Human-facing projection of authority/retention posture. | A card can render or select; it cannot make receipt history live or hide missing backing authority. |
| `OriginEvidence` | `id`, `source`, `evidence_class`, `status`, optional `locator`, optional `signature` | Evidence about where a foreign object came from and what was verified. | Origin evidence can support a trust transition; a locator, summary, receipt, or signature-shaped string is not clearance by itself. |
| `QuarantineCapsule` | `id`, `source`, `origin_evidence`, `status`, optional `safe_viewer_handle`, optional `result_handle` | Isolation envelope for imported/foreign content before trust transition. | Quarantine can allow safe viewing without live export/execute authority; direct open waits for explicit clearance. |
| `TrustTransition` | `id`, `capsule`, `origin_evidence`, `scanner_verdict`, `policy_cut`, optional `result_handle` | Cut from quarantined or reviewed content to normal live access. | Trust transition requires verifying evidence, clean/admitted verdicts, and approved policy cut; old receipts and summaries do not clear quarantine. |
| `AuthorityDiff` | `id`, `subject`, `before_rights`, `after_rights`, `declared_added`, `declared_removed`, optional `widening_badge` | Shell/audit projection of a proposed or completed rights change. | Diffs must account for every gained and lost right; hidden widening is a denial case. |
| `ExportPlan` | `id`, `typed`, `source`, `sink`, `authority_handle`, `approval_cut`, optional `quarantine_clearance` | Prepared egress operation. | Export requires live export authority and sink-specific approval; old export receipts, quarantined sources, or generic share labels are not authority. |
| `PolicyBundle` | `id`, `issuer`, `status`, `digest`, optional `version` | Active rule/data package used to evaluate a policy decision. | A bundle is not authority; stale, advisory, or digest-mismatched bundles cannot authorize effects. |
| `PolicyDecision` | `id`, `bundle`, `policy_digest`, `decision_class`, `effect`, `principal`, `action`, `resource`, optional `authority_handle` | A verdict over structured request facts. | A policy allow explains eligibility only; the effect still needs current live authority and exact scope. |
| `WitnessBundle` | `id`, `status`, `decision`, `policy_bundle`, `policy_digest`, `input_digest`, `subject`, `evidence_digest`, `evaluator`, `includes` | Audit and replay evidence for why a decision was reached. | A witness is not an approval, not a handle, and not a replay token. |
| `ScenarioReplay` | `id`, `status`, `scenario_class`, `steps` | Sealed conformance story composed from positive and negative witnessed steps. | A happy-path-only story is not conformance evidence; denial specimens must remain visible. |
| `OverrideWarrant` | `id`, `status`, `scope`, `right`, `authority_handle`, `steward_signature`, `audit_sink`, `expires_at` | Breakglass/steward-mediated exception lane. | Override is not a magic bypass; it still needs verified stewardship, live authority, exact scope, expiry, and audit. |
| `RedactionView` | `id`, `source`, `status`, `allowed_fields`, `redacted_fields`, optional `authority_handle` | Narrowing lens over source fields or classes. | A redaction view is not authority and not proof of safe disclosure; it only narrows output when paired with current authority. |
| `AuditProjection` | `id`, `status`, `projection_class`, `included_fields`, optional `redaction_view`, optional `observer_handle`, optional `raw_handle` | Human/reviewer-facing projection of audit or event history. | An audit projection explains events; raw projection, live badges, and underlying object access require separate authority. |
| `DisclosurePackage` | `id`, `status`, `source`, `subject`, `sink`, `payload_class`, `fields`, `redaction_view`, `redaction_applied`, `authority_handle`, `approval_cut` | Prepared egress packet. | A package is not a replayable export; it still requires approval, exact scope, redaction posture, sink, and live authority. |
| `SubscriptionCursor` | `id`, `status`, `subjects`, `authority_handle`, optional `expires_at`, optional `redaction_view` | Bounded observation stream cursor. | A subscription cursor may deliver event envelopes; it is not read authority and expires like other currentness evidence. |
| `NotificationEnvelope` | `id`, `status`, `subject`, `event_type`, `payload_class`, `fields`, optional `redaction_applied` | Event notification prepared for delivery. | A notification can describe a change without opening the changed object or revealing redacted payload fields. |
| `SubjectAccessRequest` | `id`, `status`, `subject`, `scope_objects`, `disclosure_package`, `redaction_view`, `authority_handle`, `review_cut` | Reviewed subject-facing export lane. | Subject access requires review, exact subject/scope, redaction, package readiness, and live authority; receipts do not replay it. |
| `SharedRoom` | `id`, `status`, `participants`, `state_epoch`, optional `roles` | Collaboration namespace membership and role state. | A room name, invite, timeline, presence advert, or collaborator badge is not object authority. |
| `MountEdge` | `id`, `status`, `target_room`, `source_handle`, `rights`, `propagation`, optional `propagation_gate` | Candidate projection of a source handle/view into a shared room path. | A mount edge must be rights-bounded by the source handle and propagation-gated when shared. |
| `GroupMembership` | `id`, `status`, `epoch`, `members`, optional `denied_members`, optional `scope`, optional `authority_handle` | Current principal/group fact set for group-bound authorization. | Membership is eligibility evidence, not authority; stale epochs, principal mismatches, labels, and missing handles deny. |
| `LabelOverlay` | `id`, `status`, `object`, `labels`, optional `conflicts`, optional `resolution_cut`, optional `authority_handle` | Classification/sharing/policy label projection over an object. | Labels are advisory or explanatory unless backed by current authority; unresolved conflicts deny settled presentation. |
| `HandoffPacket` | `id`, `status`, `source_principal`, `target_principal`, `delegation`, `child_handle`, `acceptance_cut` | Target-bound acceptance record for delegated authority handoff. | Handoff proposals and receipts do not transfer authority; accepted handoffs still need valid delegation and live child handle. |
| `CollaborationCard` | `id`, `status`, `room`, `principal`, `authority_badge`, optional `authority_slot`, optional `visible_rights`, optional `claimed_role` | Shell-facing summary of collaboration state. | The card must not fake roles, hide rights, or claim live authority without a backing handle. |
| `Receipt` | `id`, `event`, `subject`, `outcome`, `time`, optional `basis` | Durable history and explanation. | Receipts are historical evidence; they never reopen, reapprove, regrant, rehydrate, retain, or revive by themselves. |

The fixture runner currently serializes these families under plural snake-case names: `objects`, `refs`, `handles`, `views`, `portal_grants`, `derived_artifacts`, `consent_chains`, `receipts`, `mutable_sessions`, `retention_roots`, `action_plans`, `revocations`, `path_nodes`, `delegations`, `shell_cards`, `copy_inventories`, `origin_evidence`, `quarantine_capsules`, `trust_transitions`, `authority_diffs`, `export_plans`, `policy_bundles`, `policy_decisions`, `witness_bundles`, `scenario_replays`, `override_warrants`, `authority_leases`, `offline_branches`, `merge_plans`, `remote_attestations`, `freshness_fences`, `journal_checkpoints`, `redaction_views`, `audit_projections`, `disclosure_packages`, `subscription_cursors`, `notification_envelopes`, and `subject_access_requests`.

## Minimal operations

The fixture corpus exercises only the following operations. A real implementation may add richer operations, but the first checker must stay small enough to audit by inspection.

| Operation | Inputs | Allowed only when | First fixture lane |
|---|---|---|---|
| `read_handle` | handle id or non-authority carrier | handle exists, is live, and has the requested right | direct authority and revoked-handle checks |
| `attenuate_handle` | source handle id, result handle id | source and result are live, target the same object, and result rights are a subset of source rights | handle narrowing / no-widen checks |
| `compat_pathwalk` | view id, root, relative path, flags | normalized path stays under root, no blocked resolver witness is crossed, and the path resolves to a bound live handle with matching rights | path escape, symlink, magic-link, and mount-crossing checks |
| `portal_redeem` | portal grant id | grant is accepted/unspent/unexpired and result handle is live with requested rights | portal replay checks |
| `semantic_open` | answer/result artifact id | artifact carries a current live handle or prompts a fresh grant; artifact text alone is denied | semantic non-authority checks |
| `consent_export` | consent chain id | approval cut exists, summary digest matches candidate, and approved authority slots name live handles with export rights | trusted-path/approval checks |
| `retain_source_via_index` | derived artifact id | derived artifact is explicitly marked as retention root under a live policy cut | derived-artifact retention checks |
| `commit_mutable_session` | mutable session id | live write handle exists, commit cut is approved, observed base equals current head, and new object exists | mutable stale-base checks |
| `reacquire_from_restore_token` | restore-token ref id | restore token is live, has no death/stale-brake revocation, and names a live result handle | revocation/stale-brake checks |
| `sweep_decision` | object id | object has a live-handle root or explicit active retention root | GC/retention-root checks |
| `tool_invocation` | action-plan id or prompt text | typed action plan has approved cut and live authority slot with requested right | prompt/proposal/toolcall checks |
| `delegate_handle` | delegation id | delegation is issued, lease is live, source and child handles are live, target object matches, and child rights are within the attenuation envelope and source rights | delegation chain checks |
| `render_shell_card` | shell-card id | authority/retention badges match backing live handles or active roots; receipt-history cards are inert | shell-card honesty checks |
| `forget_source` | source object id | every derived artifact/copy inventory entry for that source is deleted, minimized, tombstoned, or not materialized | derived-artifact cleanup checks |
| `quarantine_open` | quarantine capsule id, mode | direct open requires cleared status and live result handle; safe-viewer open requires a live read/inspect-only viewer handle | quarantine direct-open and safe-viewer checks |
| `trust_transition_release` | trust transition id | verifying origin evidence, clean scanner/admission verdict, approved policy cut, and live result handle are all present | quarantine release checks |
| `render_authority_diff` | authority diff id | actual added/removed rights match declared added/removed rights, and widening is visibly badged | authority-diff honesty checks |
| `export_plan` | export plan id or receipt decoy | typed plan has approved cut, live export authority, sink, and required quarantine clearance; receipt replay is denied | export-plan checks |
| `policy_decision` | policy-decision id | decision is enforced, bundle is active, digests match, effect is allow, resource scope matches, and a live handle supplies the requested right | policy decision / no-policy-laundering checks |
| `witness_bundle_verify` | witness-bundle id | witness is complete and binds policy digest, decision id, input digest, subject, evaluator, and required evidence facts; replay attempts are denied | witness-bundle checks |
| `scenario_replay` | scenario-replay id | scenario is sealed, every step is well formed and witnessed, and negative evidence is present when required | replay/conformance-story checks |
| `override_grant` | override-warrant id | warrant is approved, steward-verified, scoped, unexpired, audited, and backed by a live handle with the requested right | breakglass/steward override checks |
| `redaction_view_read` | redaction-view id, fields | fields are admitted by the view and a current live read/inspect handle backs the source | redaction leak and redaction-view-not-authority checks |
| `render_audit_projection` | audit-projection id | sealed projection has observe authority; raw projection has raw-audit authority; redaction and authority badges are honest | audit projection and raw-audit checks |
| `disclose_package` | disclosure-package id | package is ready, approved, source/sink scoped, redaction applied when needed, and backed by live export/disclosure authority | disclosure package and receipt-replay checks |
| `deliver_notification` | subscription-cursor id, notification-envelope id | cursor is live/unexpired/scoped, backed by observe authority, and payload redaction is safe | subscription and notification checks |
| `subject_access_export` | subject-access-request id | request is approved, subject/scope match, package is ready, redaction blocks third-party/internal fields, and live subject-access/export authority exists | subject-access checks |
| `compose_shared_view` | shared-room id, mount-edge id, principal, epoch | room is active/current, principal is a member, mount edge is live, propagation is approved when shared, and projected rights are within source handle rights | shared-room and mount-edge checks |
| `group_bound_authority` | group id, principal, epoch, requested right | membership epoch is current, principal is a member, exact scope matches, and a live handle supplies the requested right | group membership / group-label non-authority checks |
| `resolve_label_overlay` | label-overlay id, object | overlay is active, object matches, conflicts are resolved, and live badges are backed by scoped handles | label conflict and badge checks |
| `handoff_packet` | handoff-packet id, target principal | packet is accepted by the target, delegation is valid, child handle is live, and delegated rights do not widen | handoff and receipt-replay checks |
| `render_collaboration_card` | collaboration-card id | card is sealed, room state is active, claimed role matches room state, visible rights match live slot rights, and live badges are backed | collaboration-card honesty checks |

## Fixture shape

A fixture is one JSON document with a closed top-level shape:

```json
{
  "schema": "viewfs-core-fixture-v0",
  "name": "short stable name",
  "mode": "positive-or-negative",
  "covers": ["PO-VIEWFS-AUTH-001"],
  "records": {
    "objects": [],
    "refs": [],
    "handles": [],
    "views": [],
    "portal_grants": [],
    "derived_artifacts": [],
    "consent_chains": [],
    "receipts": [],
    "mutable_sessions": [],
    "retention_roots": [],
    "action_plans": [],
    "revocations": [],
    "path_nodes": [],
    "delegations": [],
    "shell_cards": [],
    "copy_inventories": [],
    "origin_evidence": [],
    "quarantine_capsules": [],
    "trust_transitions": [],
    "authority_diffs": [],
    "export_plans": [],
    "policy_bundles": [],
    "policy_decisions": [],
    "witness_bundles": [],
    "scenario_replays": [],
    "override_warrants": [],
    "authority_leases": [],
    "offline_branches": [],
    "merge_plans": [],
    "remote_attestations": [],
    "freshness_fences": [],
    "journal_checkpoints": [],
    "redaction_views": [],
    "audit_projections": [],
    "disclosure_packages": [],
    "subscription_cursors": [],
    "notification_envelopes": [],
    "subject_access_requests": [],
    "shared_rooms": [],
    "mount_edges": [],
    "group_memberships": [],
    "label_overlays": [],
    "handoff_packets": [],
    "collaboration_cards": []
  },
  "operation": {"op": "compat_pathwalk"},
  "expect": {"result": "allow-or-deny", "reason": "stable reason"}
}
```

The checker intentionally rejects unknown top-level keys and unknown record families. That makes ambient state visible: if a future fixture wants a helper cache, shell preference, policy override, external provider, compatibility backstop, copied vector row, delegated membrane, or host fallback, the fixture must name it rather than hiding it in prose.

Every fixture also names proof obligations in `covers`. The coverage gate fails if a fixture points at an unknown obligation or if fixture-coverable obligations are left untested.


## Policy, witness, and replay discipline

Revision 159 adds the first policy-evaluation lane to the v0 checker. The shape is deliberately small:

```text
PolicyBundle
  -> PolicyDecision
  -> WitnessBundle
  -> ScenarioReplay / Shell why-panel
```

A policy decision is a verdict, not a handle. It can say that a request is eligible, but the effect still needs current authority. A witness bundle explains which bundle, input digest, evaluator, subject, and authority facts supported the decision; it cannot replay the read, write, export, or mutation. A scenario replay is not mature if it contains only happy-path successes. It must include denial specimens and witnesses so conformance does not become a screenshot of a green path.

## Override and breakglass discipline

Breakglass lanes are modeled as `OverrideWarrant` records rather than as hidden administrative bypasses. An override must be steward-verified, audit-bound, scoped, unexpired, and backed by a live authority handle. This keeps Ward-style human accountability visible while preserving ViewFS's rule that explanations, labels, and emergency prose are not object authority.

## Commit-cut discipline

Mutable work is allowed to exist, but it must not masquerade as committed object identity. The minimum commit-cut story is:

```text
Committed object
  -> MutableSession(base_object, current_head, write_handle, journal)
  -> CommitCut(observed_base, new_object, approved)
  -> new ObjCore + receipt, only if observed_base == current_head
```

This makes stale-base denial a first-class behavior rather than a later merge surprise. Conflict artifacts, rebase proposals, and repair plans can be added later, but none should be allowed to publish without passing the same current-base cut or an explicit takeover/merge cut.

## Revocation and stale-brake discipline

Revocation is not deletion and not forgetting. The v0 checker recognizes enough vocabulary to block accidental resurrection:

- a revoked handle remains visible but is not live authority;
- a restore token under a death verdict cannot reacquire authority;
- a stale brake leaves explanation behind without becoming a live grant;
- receipts survive to explain what happened but do not regrant.

The future implementation can add revocation wavefronts, issuer callbacks, recall races, offline windows, and distributed leases. The core invariant stays the same: **death evidence may preserve history while cutting future use**.

## Retention-root discipline

GC and forgetting cannot be inferred from search/index/shell convenience. The v0 rules are deliberately sparse:

- live handles retain while live;
- explicit active `RetentionRoot` records retain;
- derived-only artifacts do not retain;
- receipts do not retain;
- old portal grants do not retain unless an explicit retention root says so.

This is Schell pressure imported into ViewFS: `why retained?` and `sweep --dry-run` must be explainable without quietly turning every helpful cache into a root.

## Quarantine and egress discipline

Revision 158 adds the first foreign-origin lane to the executable core. The model is intentionally narrow:

```text
OriginEvidence
  -> QuarantineCapsule
  -> SafeViewerHandle or TrustTransition
  -> Live handle / ExportPlan
  -> Receipt
```

Safe viewing is allowed only through read/inspect-only handles. A direct open or export waits for a trust transition or an explicit quarantine clearance. A receipt that content was downloaded, scanned, viewed, or exported remains useful history, but it never clears quarantine or replays export authority.

## Authority-diff discipline

Shell surfaces are treated as attack surfaces. An authority diff is honest only when it shows every gained and lost right. Narrowing can be ordinary. Widening may be allowed in some policies, but it must be declared and visibly badged. Hidden widening is a fixture-covered denial because it would let a projection launder a rights expansion into a harmless-looking card.

## Conformance-report discipline

The generated `out/conformance_report.md` is a drift map over the fixture corpus. It is not a proof and not a filesystem implementation result. It exists so a reviewer can answer: which operations are exercised, which fixtures are positive or negative, which stable denial reasons exist, and which proof obligations have specimen pressure.

## Promotion rule for new nouns

A new ViewFS noun remains provisional until it has all of the following:

1. one positive specimen;
2. one negative specimen;
3. a shell representation or card label;
4. at least one claim or invariant entry;
5. at least one proof-obligation row or explicit non-claim;
6. a companion-seam note explaining which SlopOS/Schell/Harbor/Steward/Ward/Helm/Foundry pressure it imports and which collapse it refuses.

This rule is deliberately stricter than earlier revisions. ViewFS already has enough anti-collapse vocabulary; the next growth step is checked specimens.

## Open choices

- Exact object digest profile remains open.
- Handle table storage, slot lifetime, and kernel/runtime ABI remain open.
- Portal grant serialization remains open.
- Quarantine release policy, scanner trust, and origin-evidence verification profiles remain open beyond v0 fixture gates.
- Policy language, entity graph shape, rule precedence, and obligation syntax remain open beyond v0 policy-decision checks.
- Witness bundle envelope format, signing profile, and transparency publication remain open beyond v0 witness checks.
- Replay scenario packaging, corpus slicing, and CI result retention remain open beyond v0 scenario checks.
- Breakglass quorum rules, steward delegation, and incident closure remain open beyond v0 override-warrant checks.
- Export sink taxonomy, quotas, and multi-party review remain open beyond v0 export-plan checks.
- The shell card grammar remains open.
- Full revocation wavefront mechanics remain open beyond delegated-handle stale-brake fixtures.
- Shell card grammar remains open, but badge honesty is now fixture-covered.
- Resolver policy beyond symlink/magic/mount/escape denial remains open.
- Derived-artifact deletion, unlearning, and index compaction remain open beyond copy-inventory cleanup accounting.
- Mutable directory transaction semantics remain open beyond stale-base commit cuts.
- Multi-user, distributed, provider-backed, and federated-room semantics remain open beyond the v0 collaboration fixtures.

The v0 schema exists so those choices can be explored without allowing receipts, paths, digests, summaries, prompts, search hits, stale bases, restore tokens, clicks, origin summaries, quarantine marks, authority cards, export receipts, policy decisions, witness bundles, replay stories, or override labels, room badges, group labels, mount edges, handoff receipts, or collaboration cards to impersonate live authority.


## Revision 160 distributed-state additions

The v0 executable schema now includes six distributed-state record families:

- `AuthorityLease` — current lease over a handle/right, with epoch, expiry, renewal cut, and revocation posture.
- `OfflineBranch` — local branch state with base, local head, observed remote head, current remote head, revalidation cut, and publish authority.
- `MergePlan` — base/ours/theirs reconciliation record with conflicts, resolution cut, witnesses, write authority, and result posture.
- `RemoteAttestation` — issuer/subject/statement evidence with signature status, revocation status, expiry, and evidence-only posture.
- `FreshnessFence` — bounded freshness evidence with subject, epoch, observed time, valid-until horizon, and uncertainty state.
- `JournalCheckpoint` — checkpoint candidate with journal status, target object, flush proof, finalizer authority, and receipt separation.

The associated operations are `renew_lease`, `publish_offline_branch`, `reconcile_merge`, `verify_remote_attestation`, `check_freshness_fence`, and `checkpoint_journal`.


## Revision 161 disclosure and observation additions

The v0 executable schema now includes six disclosure/observation record families:

- `RedactionView` — a field/class/path lens that blocks or admits output but never supplies authority.
- `AuditProjection` — a sealed audit rendering that may be redacted or raw, with separate observe/raw authority and badge honesty.
- `DisclosurePackage` — a prepared egress packet with source, sink, payload class, redaction state, approval cut, and live authority.
- `SubscriptionCursor` — a bounded observation cursor with scope, expiry, and observe authority.
- `NotificationEnvelope` — a metadata or payload event envelope that cannot open the object it describes.
- `SubjectAccessRequest` — a reviewed subject-facing export lane with exact subject, scope, package, redaction, and live authority.

The associated operations are `redaction_view_read`, `render_audit_projection`, `disclose_package`, `deliver_notification`, and `subject_access_export`.

The key anti-collapse rule is that observation and disclosure surfaces are authority-adjacent, not authority. A log row, notification, redaction label, prepared package, subject-access receipt, or audit projection can explain what might be shown or what happened, but cannot replace live authority, approval/review cuts, exact scope, redaction, and freshness.


## Revision 162 collaboration and namespace-composition additions

The v0 executable schema now includes six collaboration/namespace-composition record families:

- `SharedRoom` — room/workspace/collaboration state with participants, roles, status, and state epoch.
- `MountEdge` — a rights-bounded projection of a source handle/view into a target room path, including propagation posture.
- `GroupMembership` — a current membership fact set with exact principal, epoch, denied-member, scope, and optional authority-handle posture.
- `LabelOverlay` — classification/sharing/policy labels with conflict state and optional live-badge backing.
- `HandoffPacket` — target-principal acceptance record for delegated authority transfer.
- `CollaborationCard` — shell summary of room, role, label, visible rights, and live/inert authority posture.

The associated operations are `compose_shared_view`, `group_bound_authority`, `resolve_label_overlay`, `handoff_packet`, and `render_collaboration_card`.

The key anti-collapse rule is that social/collaboration surfaces are authority-adjacent, not authority. A room membership, group label, mounted-path label, handoff receipt, or collaboration card can explain why an operation may be eligible or visible, but cannot replace live authority, exact scope, current membership epoch, accepted delegation, and honest rights rendering.

## Revision 163 GC/archive/deletion extension

| Record family | Purpose | Non-authority warning |
|---|---|---|
| `GcCandidate` | Local sweep candidate with tombstone, sweep cut, collector authority, and copy-inventory requirements. | Not proof of secure erasure or global disappearance. |
| `SnapshotPin` | Point-in-time retention edge that blocks collection or backup pruning. | Not a live object handle. |
| `ArchiveHold` | Legal/compliance/stewardship blocker with release posture. | Not read authority and not deletion evidence. |
| `BackupSet` | Inventory of protected backup copies and snapshot pins. | Not restore authority by itself. |
| `RestorePlan` | Approved plan to restore from a verified backup into a target scope. | Not valid without live restore/write authority. |
| `DeletionClaim` | Evidence envelope describing what deletion/sanitization level is claimed. | Not object authority and not proof when contradicted by retained copies. |
| `SanitizationProof` | Verified proof row for tombstone/clear/crypto-erase/purge/destroy posture. | Not global erasure proof unless scope says so. |

New checked operations: `collect_gc_candidate`, `prune_snapshot`, `release_archive_hold`, `restore_from_backup`, and `verify_deletion_claim`.


## Revision 164 supply-chain and plugin/tool-boundary extension

The v0 executable schema now includes ten supply-chain and extension-boundary record families:

| Record family | Purpose | Non-authority warning |
|---|---|---|
| `PackageEnvelope` | Signed package/admission candidate with digest, version, requested effects, and origin posture. | Not install authority and not proof that its code should run. |
| `DependencyPin` | Exact dependency source, version, digest, resolved digest, and advisory posture. | Names and version ranges are not pins; pins do not grant runtime rights. |
| `ProvenanceAttestation` | Build/subject/builder evidence for a package or extension artifact. | Provenance explains how bytes were built; it is not admission or execution authority. |
| `TransparencyEntry` | Inclusion proof row for a package/provenance/signature event. | Transparency history is evidence, not authorization. |
| `VerifierRoot` | Trust root or log-root admission state with purpose, expiry, and threshold-rotation warrant. | Root claims and old entries cannot silently update verifier trust. |
| `ExtensionManifest` | Installed extension declaration with schema digest, declared rights, sandbox, and install plan. | A manifest or installed badge cannot bind or invoke tools by itself. |
| `ToolSchema` | Typed tool effect/argument/right contract with digest and status. | A schema describes an effect; it is not effect authority. |
| `ToolBinding` | Current binding between extension manifest, tool schema, sandbox, and binding authority. | A palette-visible or installed tool is not invocable without plan approval and target authority. |
| `InstallPlan` | Approved package/extension admission plan binding provenance, transparency, pins, scanner verdict, sandbox, and live install authority. | SBOM/provenance/transparency/package metadata cannot install by themselves. |
| `SandboxProfile` | Allowed effect set for install and tool runtime lanes. | A sandbox label is not a substitute for exact authority; it only blocks effects outside its envelope. |

New checked operations: `verify_package_install`, `resolve_dependency_pin`, `verify_transparency_entry`, `admit_verifier_root`, `bind_extension_tool`, and `invoke_extension_tool`.

The key anti-collapse rule is that supply-chain evidence supports admission decisions but does not become authority. Package metadata, SBOM rows, dependency pins, provenance attestations, transparency inclusion, verifier-root claims, extension manifests, tool schemas, installed-tool badges, and sandbox labels must all remain distinguishable from live install/bind/invoke authority.


## Revision 165 resource, side-effect, cache, capacity, and metering extension

The v0 executable schema now includes seven resource/side-effect record families:

| Record family | Purpose | Non-authority warning |
|---|---|---|
| `ResourceBudget` | Period-bounded resource spend envelope for a scope. | A quota/budget card is not payer authority and does not reserve capacity. |
| `SpendReservation` | Pending or reserved slice of budget for a named effect. | A reservation row does not supply object authority for the effect. |
| `RateLimiter` | Windowed token/admission state for invocations or scheduled work. | A token count, limiter row, or old rate receipt cannot mint authority. |
| `BackgroundJob` | Deferred work unit with plan, queue lease, reservation, rate, and live-authority requirements. | A queued job is inert and must revalidate at start. |
| `CacheEntry` | Local residency row binding source epoch, pressure posture, pin state, and source handle. | Cache warmth is not read authority and stale/evicted entries cannot revive bytes. |
| `CapacitySignal` | Coarse approved observation about capacity or pressure. | Capacity hints are side-channel surfaces and must not reveal exact membership. |
| `MeteringReceipt` | Evidence that measured work is ready to settle against a reservation. | A metering receipt is not new spend/charge authority and cannot overcharge. |

New checked operations: `reserve_budget`, `admit_rate_limit`, `start_background_job`, `hydrate_cache_entry`, `emit_capacity_signal`, and `settle_metering_receipt`.

The key anti-collapse rule is that resource state can block, bound, or explain effects but cannot authorize them. A budget, reservation, rate token, queue row, cache hit, capacity hint, or metering row must remain visibly separate from typed plans, approval cuts, and current live handles.

## Revision 166 identity, credential, encryption, secret, and escrow extension

The v0 executable schema now includes ten identity/secret-custody record families:

| Record family | Purpose | Non-authority warning |
|---|---|---|
| `IdentityAssertion` | Verified or unverified subject claim from an issuer with assurance posture. | Not file, secret, or tool authority by itself. |
| `SessionBinding` | Current session state binding subject, assertion, assurance, expiry, and authority handle. | Login state and session cards expire and do not outlive currentness checks. |
| `CredentialToken` | Scope-bound external credential or token with sender constraint, expiry, and proof key posture. | Bearer strings, refresh receipts, and token metadata are not authority. |
| `EncryptionEnvelope` | Sealed object metadata binding ciphertext to key version and algorithm posture. | Ciphertext, envelope headers, and digests do not authorize cleartext. |
| `KeyVersion` | Key lifecycle row with active/revoked/decrypt-only/primary posture and algorithm status. | A key id is not decryption authority, and revoked/deprecated keys cannot clear data. |
| `KeyRotationPlan` | Approved rotation and rewrap plan binding old/new keys and live key-admin authority. | Rotation receipts and key labels cannot rotate keys again. |
| `SecretLease` | Dynamic or leased secret-use grant with scope, TTL, and authority handle. | Vault rows, secret names, and descriptors are not secret-use authority. |
| `SecretInjectionPlan` | Approved delivery plan for a leased secret into a workload/tool/shell slot. | Injection must recheck lease, delivery slot, redaction, target fit, and live authority. |
| `EscrowRecoveryWarrant` | Scoped recovery warrant with quorum evidence, subject session, expiry, and authority handle. | Escrow tickets, recovery labels, and past receipts are inert evidence only. |
| `SecretCard` | Shell projection of secret custody posture. | Secret cards must be sealed/redacted and cannot display secret material. |

New checked operations: `verify_identity_session`, `redeem_credential_token`, `open_encryption_envelope`, `rotate_key_version`, `lease_secret`, `inject_secret`, `recover_escrow`, and `render_secret_card`.

The key anti-collapse rule is that identity and cryptographic custody surfaces are authority-adjacent, not authority. An authenticated account, bearer token, passkey credential id, sealed object, key id, vault row, secret lease receipt, injection plan, escrow ticket, or shell card can explain eligibility, but cannot replace current handles, scope checks, key lifecycle, delivery-slot safety, approval cuts, and expiry/freshness fences.

## Revision 167 boundary-reality extension records

Revision 167 extends the executable core with boundary records for host/runtime, network, clipboard, drag/drop, peripheral, and sensor surfaces. These records intentionally model facts that feel close to authority but are not authority without a current handle and policy/freshness/trusted-path join.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `runtime_postures` | `id`, `status`, `attestation_status`, `epoch`, `debug_enabled` | runtime posture is not object/tool authority |
| `network_connectors` | `id`, `status`, `policy_status`, `dns_proof`, `endpoint`, `allowed_effects` | connector metadata is not egress authority |
| `clipboard_parcels` | `id`, `status`, `classification`, `contains_secret`, `redacted`, `source_epoch`, `expires_at` | copied bytes are not read/paste/secret authority |
| `dragdrop_parcels` | `id`, `status`, `trusted_path`, `overlay_suspected`, `gesture_status`, `expires_at` | drag/drop gesture rows are not import approval |
| `device_attestations` | `id`, `status`, `revoked`, `device_class` | device identity/descriptor is not authority |
| `peripheral_grants` | `id`, `status`, `device_attestation`, `device_class`, `sandbox_fit` | connected hardware is not usable hardware |
| `sensor_observations` | `id`, `status`, `consent_status`, `precision`, `includes_identifier`, `allowed_purposes`, `over_rate` | sensor facts are not disclosure authority |

The checker operations are `verify_runtime_posture`, `admit_network_connector`, `redeem_clipboard_parcel`, `redeem_dragdrop_parcel`, `bind_peripheral_device`, and `observe_sensor_sample`.

## Revision 168 transform, codec, migration, annotation, lineage, preview, and canonicalization extension records

Revision 168 extends the executable core with transform/interpretation records. These records model artifacts that often feel like the object itself: converted files, OCR text, previews, rendered pages, schema-upgraded payloads, patch summaries, annotations, provenance chains, and normalized/canonical byte views.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `transform_plans` | `id`, `status`, `approved_cut`, `source_handle`, `source_object`, `output_object`, `lossy`, `loss_disclosed`, `result_handle` | transform recipe/output is not source authority |
| `codec_profiles` | `id`, `status`, `handler_pinned`, `accepted_media_types`, `allow_active_content` | media labels and decoder profiles are not safe execution or read authority |
| `schema_migrations` | `id`, `status`, `source_schema`, `target_schema`, `current_validator`, `lossy`, `loss_disclosed`, `result_handle` | migrated payload is not original payload unless equivalence is proved |
| `patch_sets` | `id`, `status`, `observed_base`, `current_base`, `expands_authority`, `summary_only`, `result_handle` | patch summaries and stale diffs are not writes |
| `annotation_layers` | `id`, `status`, `target_object`, `selector_status`, `sensitive_selector`, `label_claims_policy`, `authority` | annotations and tags are not policy labels or authority classes |
| `lineage_links` | `id`, `status`, `complete`, `source_hashes_match`, `ambiguous_transform`, `claims_authority` | provenance explains production history but does not grant access |
| `preview_artifacts` | `id`, `status`, `source_object`, `fields`, `requires_redaction`, `redaction_view`, `claims_source_authority` | previews and render caches are not source objects |
| `canonicalization_profiles` | `id`, `status`, `confusable_collision`, `equivalence_witness`, `claims_original_digest` | normalized bytes and canonical digests are not original-byte identity |

The checker operations are `apply_transform_plan`, `decode_codec_payload`, `apply_schema_migration`, `apply_patch_set`, `attach_annotation_layer`, `verify_lineage_link`, `render_preview_artifact`, and `admit_canonicalization_claim`.

The key anti-collapse rule is that interpretive products can be useful, inspectable, and even authorized as new objects, but they must not silently inherit original authority or canonical truth. A transform recipe, decoded rendering, migration result, patch explanation, annotation label, lineage chain, preview cache, OCR text, or normalized digest needs explicit handles, proof posture, redaction/field checks, current bases, and degradation/equivalence witnesses before it can support any operation.

## Revision 169 classification, licensing, jurisdiction, purpose, and release extension records

Revision 169 extends the executable core with compliance-facing records. These records are intentionally not a legal engine; they are anti-collapse specimens for labels, license terms, obligations, jurisdiction facts, purpose statements, public-release reviews, and shell cards.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `classification_marks` | `id`, `status`, `subject`, `classifier_status`, `conflict`, `authority` | classification/public/safe/export labels are not authority |
| `license_terms` | `id`, `status`, `subject`, `permitted_uses`, `prohibited_uses`, `accepted_terms`, `required_obligations`, `satisfied_obligations`, `authority`, `required_right` | license strings and SPDX ids are not use authority |
| `jurisdiction_fences` | `id`, `status`, `source_realm`, `allowed_destinations`, `route_status`, `route_epoch`, `current_epoch`, `export_controlled`, `license_required`, `license_granted`, `authority` | region/residency labels are not egress clearance |
| `compliance_obligations` | `id`, `status`, `required_artifacts`, `satisfied_artifacts`, `authority`, `required_right` | receipts/checklists do not discharge current obligations |
| `public_release_reviews` | `id`, `status`, `reviewer_verified`, `review_epoch`, `current_epoch`, `classification`, `requires_redaction`, `redaction_view`, `fields`, `obligations_satisfied`, `authority` | public labels and old release receipts are not release cuts |
| `purpose_bindings` | `id`, `status`, `allowed_purposes`, `secondary_approved`, `retention_budget_status`, `authority`, `required_right` | purpose statements are not processing authority |
| `compliance_cards` | `id`, `status`, `claims_live_authority`, `claims_clear_to_export`, `release_review`, `exposes_blocked_fields` | shell compliance cards are explanations, not authority |

The checker operations are `evaluate_classification_mark`, `authorize_license_use`, `check_jurisdiction_fence`, `enforce_compliance_obligation`, `approve_public_release`, `bind_purpose_use`, and `render_compliance_card`.

## Revision 170 query, planning, result, evaluation, scoring, and model-selection extension records

Revision 170 extends the executable core with query/evaluation records. These records model a dangerous agentic seam: saved queries, planner traces, ranked results, aggregates, eval sets, benchmark runs, scoring rubrics, and leaderboards often look like decisions. In ViewFS they are evidence, selectors, summaries, or assessment artifacts. They are not authority.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `query_specs` | `id`, `status`, `allowed_sources`, `allowed_fields`, `requires_current_index`, `authority` | query text and saved queries are not read/search authority |
| `planner_traces` | `id`, `status`, `approved_cut`, `proposed_rights`, `allowed_rights`, `scope_widened`, `hidden_effects`, `authority` | model/planner proposals are not executable plans |
| `result_sets` | `id`, `status`, `summary_only`, `claims_raw_access`, `members` | ranked hits, ids, and snippets are not object authority |
| `aggregation_views` | `id`, `status`, `cohort_count`, `k_threshold`, `raw_rows_exposed`, `claims_exact_membership`, `authority` | aggregate cells are not raw rows or membership oracles |
| `evaluation_sets` | `id`, `status`, `holdout_sealed`, `contamination_status`, `license_ok`, `purpose_ok`, `authority` | eval-set labels are not production/deploy authority |
| `benchmark_runs` | `id`, `status`, `run_epoch`, `current_epoch`, `reproducible`, `eval_set_status`, `rubric_status`, `authority` | benchmark scores and leaderboards are not deploy authority |
| `scoring_rubrics` | `id`, `status`, `calibrated`, `metric_gaming_detected`, `rubric_epoch`, `current_epoch`, `authority` | rubrics and metric names are not policy authority |
| `model_selection_cards` | `id`, `status`, `claims_deploy_authority`, `claims_production_ready`, `approval_cut`, `hides_tradeoffs`, `single_score_only` | dashboards must not hide tradeoffs or claim production authority without evidence |

The checker operations are `admit_query_scope`, `admit_planner_trace`, `open_result_member`, `render_aggregation_view`, `admit_evaluation_set`, `record_benchmark_run`, `apply_scoring_rubric`, and `render_model_selection_card`.

The key anti-collapse rule is that assessment and retrieval artifacts can guide humans and agents, but they do not replace live handles, current scopes, approval cuts, contamination checks, reproducibility evidence, and deployment authority.


## Revision 171 incident-response extensions

Revision 171 extends the v0 executable schema with incident-response record families. These records are intentionally operational and evidentiary; none of them is a shortcut to object authority, disclosure authority, containment authority, remediation authority, or proof of closure.

| Record family | Checked operation pressure |
|---|---|
| `AlertSignal` | `admit_alert_signal` must reject stale alerts, alerts that claim authority, subject mismatch, and missing observe/security authority. |
| `IncidentCase` | `open_incident_case` must reject case rows that lack active alert context, claim remediation authority, are closed, or lack case authority. |
| `TriageVerdict` | `apply_triage_verdict` must reject stale/low-confidence verdicts, execution claims, and missing triage authority. |
| `ForensicSnapshot` | `capture_forensic_snapshot` must reject live-access claims, unsealed captures, redaction leaks, and missing capture authority. |
| `EvidenceChain` | `verify_evidence_chain` must reject incomplete chains, digest mismatch, truth/causality claims, and missing verification authority. |
| `ContainmentPlan` | `approve_containment_plan` must reject unapproved plans, scope widening, missing blast-radius review, and missing containment authority. |
| `RemediationPlan` | `execute_remediation_plan` must reject receipt replay, unapproved repair, missing preconditions, closure claims, and missing remediation authority. |
| `RecoveryRollback` | `execute_recovery_rollback` must reject unapproved rollback, stale base epochs, erasure claims, and missing rollback authority. |
| `PostmortemRecord` | `render_postmortem_record` must reject live-authority claims, no-recurrence/closure claims, redaction leaks, and unbacked public-release claims. |

The incident-response lane also added positive specimens for formerly negative-only operations so the executable corpus now shows both the allowed cut and at least one denied collapse for every operation.

## Revision 172 governance and change-management extension records

Revision 172 extends the executable core with governance/change-management records. These records are not a replacement for Ward stewardship or SlopOS policy; they are the ViewFS-local anti-collapse specimens for change records that would otherwise look like authority.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `change_proposals` | `id`, `status`, `subject`, `digest`, `basis_epoch`, `current_epoch`, `authority` | proposals are not execution, migration, rollout, or disclosure authority |
| `decision_records` | `id`, `status`, `proposal`, `proposal_digest`, `decision`, `authority` | decision rows do not execute effects |
| `approval_quorums` | `id`, `status`, `required`, `approvals`, `eligible`, `steward_required`, `steward_present`, `authority` | quorum facts are not approval authority by themselves |
| `rollout_plans` | `id`, `status`, `approval_cut`, `guardrails_ok`, `blast_radius_reviewed`, `allowed_rings`, `authority` | rollout plans do not prove completion or safety |
| `feature_flags` | `id`, `status`, `allowed_scopes`, `policy_epoch`, `current_epoch`, `authority` | flag/cohort membership is not object or tool authority |
| `deprecation_notices` | `id`, `status`, `effective_after`, `now`, `migration_path`, `authority` | notices are not removal proof or revocation authority |
| `compatibility_contracts` | `id`, `status`, `from_version`, `to_version`, `breaking_change`, `waiver`, `authority` | compatibility promises are not compatibility proof |
| `migration_runs` | `id`, `status`, `approval_cut`, `source_schema`, `target_schema`, `current_schema`, `precheck_ok`, `rollback_plan`, `authority` | migration plans/runs are not success proof |
| `governance_cards` | `id`, `status`, `subject`, `quorum`, `claims_live_authority`, `exposes_private_votes`, `claims_unanimity` | dashboards/cards explain; they do not grant authority |

The checker operations are `admit_change_proposal`, `record_decision`, `verify_approval_quorum`, `start_rollout_plan`, `evaluate_feature_flag`, `enforce_deprecation_notice`, `check_compatibility_contract`, `execute_migration_run`, and `render_governance_card`.

Revision 172 also adds fixture-catalog discipline: fixture numeric prefixes must be contiguous, positive fixtures must end in `-allow.json`, negative fixtures must end in `-denied.json`, fixture names must be unique, and every fixture must identify operation and proof-obligation coverage.


## Revision 173 workflow, automation, idempotency, retry, and human-task extension records

Revision 173 extends the executable core with automation-custody records. These records are deliberately not a workflow engine. They are the minimal fixtures needed to keep event, trigger, schedule, run, step, idempotency, retry, compensation, human-task, and card state from collapsing into authority.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `event_envelopes` | `id`, `status`, `type`, `source`, `subject`, `source_trusted`, `schema_valid`, `authority` | event delivery is not object or workflow authority |
| `trigger_rules` | `id`, `status`, `event_type`, `rule_epoch`, `current_epoch`, `authority` | rule matches are not effect cuts |
| `schedule_windows` | `id`, `status`, `not_before`, `not_after`, `now`, `approval_cut`, `authority` | scheduled eligibility is not approval or authority |
| `workflow_runs` | `id`, `status`, `approval_cut`, `lease_valid`, `basis_epoch`, `current_epoch`, `authority` | queued/run state does not serialize live authority |
| `step_invocations` | `id`, `status`, `workflow`, `approval_cut`, `target_handle`, `required_right`, `authority` | step rows do not widen target rights or prove completion |
| `idempotency_keys` | `id`, `status`, `request_fingerprint`, `authority` | dedupe keys are not effect replay authority |
| `retry_policies` | `id`, `status`, `attempt`, `max_attempts`, `backoff_until`, `now`, `budget_ok`, `authority` | retry policy is not hidden retry authority |
| `compensation_plans` | `id`, `status`, `approval_cut`, `reversible`, `target_step`, `authority` | compensation does not erase history/evidence |
| `human_tasks` | `id`, `status`, `assignee`, `trusted_path`, `approval_cut`, `authority` | task rows and clicks are not consent by themselves |
| `workflow_cards` | `id`, `status`, `workflow`, `claims_live_authority`, `leaks_hidden_steps`, `claims_completion` | cards explain workflow state but do not grant authority |

The checker operations are `admit_event_envelope`, `evaluate_trigger_rule`, `fire_schedule_window`, `start_workflow_run`, `execute_workflow_step`, `apply_idempotency_key`, `apply_retry_policy`, `execute_compensation_plan`, `complete_human_task`, and `render_workflow_card`.

The key anti-collapse rule is that automation can prepare, narrow, and explain work. It cannot execute ViewFS object effects unless the exact operation revalidates current basis, approval, lease, policy, and live handle authority.

## Revision 174 personalization, recommendation, shortcut, and feedback extension records

Revision 174 extends the executable core with personalization/convenience records. These records deliberately separate adaptation from authority.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `user_profiles` | `id`, `status`, `subject`, `identity`, `session`, `policy_epoch`, `current_epoch`, `authority` | profiles are not identity proof or object authority |
| `preference_sets` | `id`, `status`, `profile`, `scope`, `allowed_scopes`, `policy_epoch`, `current_epoch`, `authority` | preferences are not policy, consent, or tool authority |
| `personalization_models` | `id`, `status`, `model_epoch`, `current_epoch`, `training_purpose_ok`, `source_minimized`, `authority` | models/scores are not source authority or training consent |
| `recommendation_sets` | `id`, `status`, `source_model`, `scoped`, `authority` | recommendations are not object opens or proof of intent |
| `shortcut_bindings` | `id`, `status`, `action`, `target_handle`, `required_right`, `approval_cut`, `authority` | shortcuts are not macro authority without target rights and approval |
| `autofill_proposals` | `id`, `status`, `target_handle`, `required_right`, `secret_fields`, `redacted`, `approval_cut`, `authority` | autofill suggestions are not write authority or secret disclosure |
| `experiment_assignments` | `id`, `status`, `subject`, `experiment`, `scope`, `allowed_scopes`, `policy_epoch`, `current_epoch`, `authority` | cohorts are not policy overrides |
| `feedback_signals` | `id`, `status`, `source`, `purpose`, `allowed_purposes`, `consent_for_training`, `authority` | feedback is not training consent or a retention root |
| `personalization_cards` | `id`, `status`, `profile`, `preference_set`, `claims_live_authority`, `exposes_sensitive_features`, `claims_deterministic` | cards explain adaptation but do not grant authority or expose sensitive features |

The checker operations are `verify_user_profile`, `apply_preference_set`, `admit_personalization_model`, `render_recommendation_set`, `execute_shortcut_binding`, `accept_autofill_proposal`, `apply_experiment_assignment`, `record_feedback_signal`, and `render_personalization_card`.

## Revision 175 schema, ontology, reference, crosswalk, and catalog extension records

Revision 175 extends the executable core with interoperability records. These records make schema translation and external reference work explicit while preventing namespace, URI, term, crosswalk, validation, ontology, catalog, and card surfaces from becoming authority.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `namespace_bindings` | `id`, `status`, `prefix`, `allowed_prefixes`, `context_digest`, `policy_epoch`, `current_epoch`, `authority` | namespace contexts and prefixes are not object authority or policy |
| `external_references` | `id`, `status`, `scheme`, `allowed_schemes`, `resolver_epoch`, `current_epoch`, `target_digest`, `authority` | URIs, IRIs, and external references identify; they do not open or disclose |
| `vocabulary_terms` | `id`, `status`, `term`, `namespace`, `deprecated`, `authority` | vocabulary terms are labels, not classification, policy, or rights |
| `crosswalk_mappings` | `id`, `status`, `source_term`, `target_term`, `reviewed`, `confidence`, `mapping_kind`, `authority` | crosswalks translate; they do not prove exact equivalence by default |
| `shape_constraints` | `id`, `status`, `shape_epoch`, `current_epoch`, `validation_passed`, `target_handle`, `authority` | shape validation is not approval, safety, or object authority |
| `ontology_alignments` | `id`, `status`, `relation`, `confidence`, `alignment_epoch`, `current_epoch`, `reviewed`, `authority` | ontology inference and alignment cannot inherit authority automatically |
| `catalog_entries` | `id`, `status`, `catalog_epoch`, `current_epoch`, `public_release_approved`, `redacted`, `source_handle`, `authority` | catalog metadata is not raw payload disclosure or release authority |
| `interop_cards` | `id`, `status`, `claims_live_authority`, `overstates_equivalence`, `leaks_hidden_identifier` | interop cards explain translation state; they do not certify safety or grant authority |

The checker operations are `bind_namespace_context`, `resolve_external_reference`, `admit_vocabulary_term`, `apply_crosswalk_mapping`, `validate_shape_constraint`, `verify_ontology_alignment`, `publish_catalog_entry`, and `render_interop_card`.

The key anti-collapse rule is that interoperability artifacts may connect schemas and improve review, but they must not silently become live handles, policy, classification, disclosure approval, equivalence proof, or canonical truth. Any effect still needs current ViewFS authority, exact scope, policy epoch, approval cut where relevant, and receipt separation.


## Revision 176 host-adapter compatibility extension records

Revision 176 extends the executable core with host-adapter compatibility records. These records are deliberately projection records, not a commitment to one host filesystem API.

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `adapter_mounts` | `id`, `status`, `provider`, `policy_epoch`, `current_epoch`, `sandbox_ok`, `authority` | mount rows and provider labels are not ambient/root authority |
| `stat_projections` | `id`, `status`, `source_handle`, `fields`, `hidden_fields`, `authority` | stat metadata is not read authority or full object truth |
| `inode_aliases` | `id`, `status`, `alias_epoch`, `current_epoch`, `target_handle`, `collision`, `authority` | inode-like aliases are not object identity by themselves |
| `xattr_parcels` | `id`, `status`, `name`, `allowed_names`, `sensitive_names`, `redacted`, `source_handle`, `authority` | xattrs are not policy, classification, or disclosure authority |
| `watcher_subscriptions` | `id`, `status`, `event_epoch`, `current_epoch`, `cursor_state`, `allowed_events`, `authority` | watcher events are notifications, not opens or authority refreshes |
| `lock_tokens` | `id`, `status`, `mode`, `target_handle`, `required_right`, `range_conflict`, `authority` | advisory locks coordinate; they do not grant write authority |
| `rename_plans` | `id`, `status`, `approval_cut`, `source_handle`, `target_parent_handle`, `cross_mount`, `authority` | rename plans are not completion proof and cannot bypass mount boundaries |
| `tempfile_leases` | `id`, `status`, `flush_proof`, `approval_cut`, `target_handle`, `authority` | staged tempfiles are not committed objects |
| `hydration_tickets` | `id`, `status`, `placeholder_epoch`, `current_epoch`, `network_verified`, `source_handle`, `result_handle`, `authority` | hydration tickets are not read authority or network trust |
| `external_app_handoffs` | `id`, `status`, `portal_approved`, `redacted`, `target_handle`, `authority` | handoff receipts are not persistent grants |

The checker operations are `admit_adapter_mount`, `render_stat_projection`, `resolve_inode_alias`, `read_xattr_parcel`, `deliver_watcher_event`, `acquire_lock_token`, `execute_rename_plan`, `promote_tempfile_lease`, `hydrate_placeholder`, and `handoff_external_app`.
