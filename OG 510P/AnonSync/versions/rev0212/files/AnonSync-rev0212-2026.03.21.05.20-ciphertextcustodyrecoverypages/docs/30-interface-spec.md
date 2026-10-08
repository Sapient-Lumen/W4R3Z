## Revision addendum — opaque custody needs four fixed pages after rev0211

The main interface spec should now treat ciphertext-only custody as another fixed page family rather than a special-case article sink.

Required stable pages:

- **Encrypted target admission**
- **Ciphertext custody**
- **Decrypt recovery**
- **Encrypted Archive limit**

The shell must be able to enter those pages from any serious encrypted-node row, warning, restore candidate, or custody report without changing vocabulary or collapsing hard ceilings into friendly-but-false verbs.

## Revision addendum — interface grammar after rev0210: target rows need capability class, fidelity, and repair truth

Every interface projection that shows a subject root or storage target should now keep five truths adjacent in the same row or review pane:

- current volume capability verdict
- strongest native primitive ceiling
- metadata fidelity verdict (`native`, `stub-backed`, `narrowed`, `unknown`)
- strongest missing action cause (`posture`, `client health`, `volume prerequisite`)
- nearest honest repair lane

The product must never let `connected`, `writable`, or `mounted` stand in for the real answer about what this target can carry.

## Revision addendum — interface grammar after rev0201: readiness, repair, and urgency need adjacent basis and risk

Every interface projection that shows changed or inbound artifacts should now keep five truths adjacent in the same row or review pane:

- current readiness or urgency verdict
- strongest basis for that verdict
- strongest blocker or exception now in charge
- nearest honest action
- chronology or fairness risk if the operator overrides it

The product must never let `syncing`, `waiting`, or alphabetical listing stand in for the real answer about readiness or queue order.
Any manual freshness repair must also surface whether it asserts newer chronology before the user leaves the pane.

## Revision addendum — interface grammar after rev0199: capability posture needs adjacent basis, blocker, and recovery

Every interface projection that shows a serious action or feature family should now keep four truths adjacent in the same row or review pane:

- current capability verdict
- entitlement basis or provenance
- strongest blocker if unavailable
- nearest honest enable or recovery path

The product must never let a missing action rely on the operator to remember whether the blocker was release line, subject class, surface, host role, or entitlement provenance.
Any downgrade or loss state must also surface which live subjects are affected before the user leaves the pane.


## Revision addendum — interface grammar after rev0192: byte-presence rows need typed verbs and scope chips

Every interface projection that shows a materializable subject should now keep five truths adjacent in the same row or review pane:

- current byte posture
- next fetch scope
- later-arrival policy
- strongest local-only reclaim verb
- strongest global-delete consequence chip

The product must never let a row rely on the operator to remember that the same Delete key can mean different things for a placeholder, a full local copy, or a subject with wider write authority.
Any restore entry point must also surface chronology authority and replay risk before the user leaves history.

## Revision addendum — seat continuity and reset-impact grammar after rev0191

The core interface grammar should now explicitly preserve another adjacency rule:

- whenever seat identity is in question, every serious surface must keep **identity proof**, **lineage verdict**, and **continuity-survival summary** adjacent
- whenever an operation might replace identity, every serious surface must keep **takeover verdict**, **subject-loss preview**, and **safe alternative** adjacent
- whenever a roster row looks confusing, every serious surface must keep **row classification**, **linkage state**, and **return / retirement consequence** adjacent
- whenever reset or rehome is proposed, every serious surface must keep **preservation verdict**, **storage-root verdict**, and **follow-up work** adjacent

The product should not let row labels, path reuse, or reset verbs silently stand in for the whole continuity story.

## Revision addendum — approval-state grammar after rev0190

The core interface grammar should now explicitly preserve another adjacency rule:

- whenever a request is pending, every serious surface must keep **request state**, **approver locus**, and **route-visibility verdict** adjacent
- whenever approval is proposed, every serious surface must keep **identity proof**, **fingerprint / receipt evidence**, and **resulting authority** adjacent
- whenever remembered trust suppresses or fails to suppress a prompt, every serious surface must keep **memory scope**, **reprompt trigger**, and **tightening / broadening action** adjacent

The product should not let a pending icon, an absent prompt, or a remembered certificate silently stand in for the whole approval story.

## Revision addendum — grant lifecycle grammar after rev0189

The core interface grammar should now explicitly preserve another adjacency rule:

- whenever a member right might change, every serious surface must keep **requested delta**, **live-mutation verdict**, and **epoch boundary** adjacent
- whenever access-bearing artifacts remain live, every serious surface must keep **canonical artifact identity**, **grant epoch**, and **governance drift** adjacent
- whenever revoke is proposed, every serious surface must keep **direct effect**, **descendant blast radius**, and **landed-byte boundary** adjacent
- whenever reissue is required, every serious surface must keep **in-place impossibility reason**, **successor artifact**, and **retirement plan** adjacent

The product should not let a role dropdown, a Disconnect button, or an old share dialog stand in for the whole lifecycle story.

## Revision addendum — join authority and lane comparison grammar after rev0188

The core interface grammar should now explicitly preserve another adjacency rule:

- whenever a seat might join, every serious surface must keep **entry lane**, **approval basis**, **resulting rights**, and **future scope** adjacent
- whenever a seat might share onward, every serious surface must keep **shareability verdict**, **ceiling source**, and **downstream envelope** adjacent
- whenever several claim lanes are offered, every serious surface must keep **canonical artifact truth**, **approval/budget deltas**, and **browser/scanner dependence** adjacent

The product should not let any projection force the operator to infer authority from carrier labels alone.

# Interface spec (v1 draft, operator surface)

## Design principles

1. **One daemon, one shared model.**
   CLI, API, UI, and TUI are clients of the same object graph.

2. **Everything important is addressable.**
   Devices, shares, grants, mounts, policies, invites, claims, transfers, backups, recovery bundles, plans, and events all have stable IDs.

3. **Human by default, machine on demand.**
   Read commands support `--json`; watch commands support stream output.

4. **States describe local reality.**
   Prefer `detached`, `selective`, `full`, `metadata-only`, `partial`, `complete`, `encrypted-only`.

5. **Linking is not replacement.**
   Linking can create relationships and install policies; it never overwrites local identity.

6. **Transport and publication are visible policy.**
   Relay, tracker, LAN discovery, known-host pinning, address publication, and endpoint cache are first-class configuration.

7. **Recovery is part of the primary surface.**
   Backup, import, replacement, rotation, and revocation are not “support-only” edge cases.

8. **Convenience must compile to explicit policy.**
   Profile-driven flows may exist, but their effects must be inspectable and reversible.

9. **High-signal mutations should be previewable and replay-safe.**
   When an operation can widen trust, rebind identity, or change recovery posture, the interface should prefer `plan -> review -> apply` over blind fire-and-forget mutation.

10. **Visibility is staged before local path adoption.**
   A share becoming visible through linking or policy should not silently create a path. Incoming visibility is an explicit object that can later be adopted.

11. **File scope must be explicit.**
   Fetching, evicting local bytes, and deleting replicated data are separate operations with separate verbs.

12. **Restore must be first-class.**
   Version history and restoration should be exposed through normal commands, not hidden archive spelunking.

13. **Hidden service files are implementation detail.**
   Ignore rules, conflict cases, and service metadata should be inspectable through supported surfaces rather than ad hoc filesystem rituals.

14. **Compatibility and privilege consequences should be previewable.**
   Linking, adoption, and role changes should expose blockers, downgrade warnings, and authority consequences before commitment.

15. **Offers and recovery material should be inspectable.**
   Invites, visible share offers, and recovery prerequisites should be supported objects rather than hidden side effects or log archaeology.

16. **Path binding is a compared action.**
   Adopting a share into a path or relocating an existing mount into a non-empty path should expose comparison results, collision classes, and explicit winner policy before commit.

17. **Destructive actions need preservation evidence.**
   Eviction, local remove, share-wide delete, and share-scope restore should expose replica/history coverage before apply.

18. **Retirement intent must be explicit.**
   Hiding an offline device, ignoring future contact, revoking trust, replacing hardware, and rotating identity are distinct operations with distinct audit and continuity consequences.

19. **Filesystem compatibility is supported state.**
   Case rules, Unicode normalization, symlink handling, metadata fidelity, and path-safety blockers should be inspectable before and after adoption.

20. **Namespace projection is explicit.**
   Share-wide namespace suppression, local mount-view omission, placeholder-visible projection, and byte materialization should not be inferred from one overloaded ignore rule.

21. **Unknown peers are staged before trust.**
   New or newly introduced peers should first land in contact or pending state; linking, granting, and future approval should remain separate decisions.

22. **Attention is a first-class resource.**
   The interface should explicitly summarize what needs review now, what can wait, and what is merely informative background state.

23. **Derived summaries are not hidden authority.**
   Review queues, dashboard cards, and workbench groupings may compress the object model for humans, but they must point back to the real underlying objects rather than inventing secret side effects.

24. **Risk must travel with proof.**
   Destructive, trust-expanding, compatibility-sensitive, or exposure-widening actions should surface the relevant preservation, preflight, convergence, or exposure report where the action is taken.

25. **Warnings should converge to one report language.**
   Different report families may exist internally, but operators should be able to inspect them through one shared read/projection surface rather than learning a separate mini-product for every risk class.

26. **Path repair is not share re-creation.**
   Missing paths, reconnects, marker drift, and moved local directories should lead to inspect/compare/repair workflows before any remove/re-add style reset is suggested.

27. **Binding and preservation stay legible together.**
   The surface answering “where is this share bound?” should also be able to answer “what survives if I detach, clean up, or restore it?”

28. **Runtime control must be phase-specific.**
   Transfer stops, drains, throttles, maintenance freezes, and recurring windows should say exactly which phases stay active.

29. **Rollback provenance must be queryable.**
   History, restore, and conflict resolution should expose durable timeline objects with provenance and receipts rather than hidden archive paths, generic activity scraps, or magic filenames.

30. **Filesystem fidelity must stay legible after bind.**
   Portability policy, active pathname/metadata semantics, degraded notification posture, and later drift should remain inspectable as durable mount state rather than dissolving back into one stale preflight warning.

31. **Later-arrival causality must be explorable.**
   A subject that appears, matches prior trust, drafts a candidate path, or stalls before bind should expose one truthful `why here now` explanation surface with causes, non-causes, counterfactuals, and proof links.


32. **Mutation instrument choice comes before field editing.**
   The operator must choose baseline edit, local pin, temporary override, durable exception, or inheritance restore before a value editor pretends scope is obvious.

33. **Reviewed drafts end in a fixed commit barrier.**
   The last step before apply must restate irreversible scope, continuity claim, expected receipts, and any stronger acknowledgement required for authority widening or destructive outcomes.

34. **Reconnect is a continuity problem, not a default-path problem.**
   Reconnect, rebind, adopt, and repair should compare remembered path, proposed path, existing bytes, and duplicate risk before any new namespace is created.

35. **Local web is a primary projection.**
   Linux-first and service-first operators must be able to read, explain, draft, review, and ordinarily apply from the local web surface without semantic downgrade.

36. **Narrow surfaces preserve proof-bearing meaning.**
   Small screens and dense tables may stack, fold, or defer, but they may not omit source, blast radius, future effect, blocker reason, or apply consequence.

37. **Delivery encoding is not authority semantics.**
   File, URI, QR, clipboard, and local handoff are wrappers around one offered capability; changing wrapper must not silently change what authority is on offer.

38. **Portable preview is not local acceptance.**
   Browser and import surfaces may inspect an artifact and then hand off explicitly, but only a local claim/apply path may state what this machine accepted.

39. **One property gets one effective-truth stack.**
   A value influenced by several layers must still be explainable from one property surface, including current winner, shadowed layers, future-parent effect, and rejoin path.

40. **Standing arrival defaults do not replace per-share bind review.**
   Machine- or seat-level future-arrival defaults may suggest visibility, materialization, or path roots, but they may not stand in for one-share compare/bind truth.

41. **Current artifact and change explanation are separate surfaces.**
   When one retained shareable artifact supersedes or refreshes another, the interface should expose both the current head and a compact carryforward/delta/refresh surface; operators should not have to infer semantic continuity from revision markers alone.

42. **Startup ownership is not a checkbox.**
   Install success, service continuity, and current runtime health should not be allowed to impersonate who actually owns automatic return on this host; candidate startup lanes, effective owner, runtime correlation, and recent drift should remain inspectable as their own object.

43. **Same-thread reply is not exact acknowledgment.**
   Imported recipient response may prove conversational continuity without proving which exact issued artifact, correction notice, or replacement object was acknowledged; sender match, continuity lane, bound object, and claim ceiling should remain separate.

44. **Exact acknowledged object is not the same thing as exact target scope.**
   One actor's reply may be exact about the object while still being only actor-scoped, one-member-scoped, or delegate-scoped relative to a broader mailbox, group, or support lane; raw actor, visible lane, delegation evidence, and audience ceiling should remain separate.

45. **Reply-shaped traffic is not automatically human acknowledgment.**
   A same-thread message, shared-mailbox response, ticket auto-create note, rule-authored comment, out-of-office response, or receipt-like signal may still be machine-authored; authorship class, automation kind, and human-proof ceiling should remain separate from both object exactness and target scope.

46. **Human reply is not automatic acceptance.**
   A real human reply may still be only a comment, clarification request, redirect, request-changes posture, conditional acceptance, or decline; reply stance, blocking effect, and smallest honest follow-up should remain separate from object exactness, target scope, and human-proof.

47. **Exact reply object is not whole-packet coverage.**
   A reply can bind exactly to the right outward artifact yet still address only one quoted paragraph, one diff range, one attachment, or one named request item; referent slice, coverage ceiling, and remainder posture should remain separate from object exactness, target scope, human-proof, and stance.

48. **Latest imported reply is not automatically the current operative answer.**
   Several imported replies in the same lane may coexist as whole-packet blockers, whole-packet approvals, slice-specific approvals, redirects, or conditional heads; clients should preserve latest arrival, current operative head, superseded replies, and contradiction warnings instead of flattening the bottom-most message into current truth.

---

## Command-language rules

### Naming

Binary name:

```text
anonsync
```

Resource names should be stable, lower-case, and shell-friendly where possible.
User-facing labels can be richer, but selectors should prefer simple handles.

### Selectors

Every object should be addressable by one of:

- stable ID
- unique local handle/label
- path, where path is the natural selector
- local token file or bundle path, where the object naturally originates from an artifact

If a selector is ambiguous, the command must fail with an ambiguity error rather than guessing.

Examples:

```text
anonsync share show workdocs
anonsync share show shr_01J...
anonsync mount show ~/Sync/workdocs
```

### Read vs mutate

Read commands:

- default to human-readable output
- support `--json`
- never have side effects

Mutating commands:

- support `--json`
- support `--yes` for non-interactive mode
- should support `--reason <text>` for auditability on sensitive operations
- should support `--profile <name>` when invoking convenience presets
- should support `--plan` when the command class is high-signal

### Preview levels

Three preview forms are useful:

```text
--dry-run
--plan
anonsync plan show <plan_id>
```

Semantics:

- `--dry-run` is an inline preview for simple local changes
- `--plan` creates a durable plan object for review and later apply
- `plan show` renders the same intent as a first-class object with preconditions and drift boundaries

The preview output must explain:

- which objects would change
- which policies would be created or updated
- whether trust scope would expand
- whether route/cache state is affected
- whether any action becomes hard to undo without recovery or revoke
- for destructive file actions, what preservation evidence exists or is missing after the action

### Preconditions and drift

High-signal apply paths should support precondition checks.
At minimum the contract should include:

- expected object version
- expected identity status where relevant
- expected policy revision where relevant

If the world changed after the preview was generated, apply must fail loudly rather than silently reinterpret the request.

### Explainability

For important objects, the CLI should support at least one of:

```text
--explain
--show-provenance
anonsync audit --subject <id>
```

The goal is that an operator can answer:

- why this grant exists
- why this route is active
- which serious route candidates were rejected and why
- what this policy currently publishes about reachability
- which profile created this policy
- which recovery step rebound this device or share state
- which standing template, approval memory, or placement suggestion influenced this arrival
- which tempting story is false because no local claim or bind has happened yet

### Exit status

A minimal exit-code contract:

- `0` success
- `1` generic failure
- `2` usage / selector ambiguity / invalid flags
- `3` policy violation / trust boundary rejection
- `4` remote or peer state prevents completion
- `5` recovery flow required
- `6` precondition failed / plan drifted

The richer machine contract is the structured error code emitted under `--json`.

---

## Concept model

### Device

A locally controlled node with its own keypair and daemon state.

Fields:

- `device_id`
- `display_name`
- `trust_class` (`trusted`, `untrusted`, `relay`)
- `identity_status` (`normal`, `rotating`, `revoked`, `replaced`)
- `addresses[]`
- `capabilities[]`
- `software_version`
- `protocol_family`
- `compatibility_status` (`unknown`, `ok`, `warning`, `blocked`)
- `last_seen`
- `linked_group_id` nullable
- `retirement_status` (`active`, `hidden`, `ignored`, `revoking`, `replaced`, `retired`)

### Contact record

A durable relationship-memory object for a peer or potential peer.
This exists so “someone I know”, “someone I linked”, “someone currently pending”, and “someone explicitly ignored” are not collapsed into one overloaded device row.

Fields:

- `contact_id`
- `primary_device_id` nullable
- `display_name`
- `relationship_class` (`self-device`, `known-peer`, `collaborator`, `unknown`)
- `contact_state` (`pending`, `trusted`, `quarantined`, `ignored`, `revoked`)
- `linked_group_id` nullable
- `future_introduction_policy` (`disabled`, `share-scoped`, `bounded`, `review-required`)
- `approval_summary`
- `last_seen_identity_refs[]`
- `successor_policy` (`none`, `manual-review`, `carry-limited`, `carry-all-with-review`)
- `provenance_ref` nullable

### Pending peer

A first-class queue record for an unknown or newly introduced peer that has tried to contact this node or announce a share relationship.

Fields:

- `pending_peer_id`
- `observed_device_id` nullable
- `observed_name` nullable
- `source` (`manual-invite`, `share-announcement`, `linked-introduction`, `recovery`, `direct-contact`)
- `linked_group_hint` nullable
- `candidate_contact_id` nullable
- `offered_actions[]` (`trust-contact`, `link`, `claim-share`, `ignore`, `quarantine`)
- `expires_at` nullable
- `decision_status` (`pending`, `accepted`, `dismissed`, `ignored`, `quarantined`)
- `provenance_ref` nullable

### Introduction policy

A bounded policy describing when one trusted device or linked group may surface additional peers without silently turning those peers into full trust.

Fields:

- `introduction_policy_id`
- `scope_type` (`link`, `share`, `tag`)
- `scope_id`
- `mode` (`disabled`, `pending-only`, `share-scoped`, `bounded-auto-link`)
- `max_permission` (`none`, `ro`, `rw`)
- `requires_claim` boolean
- `requires_preflight` boolean
- `auto_visible_share_limit` (`none`, `matched-only`)
- `provenance_ref` nullable

### Share

A logical synchronized dataset.

Fields:

- `share_id`
- `label`
- `origin_device`
- `default_mode` (`detached`, `selective`, `full`)
- `write_policy` (`send-receive`, `send-only`, `receive-only`)
- `encryption_policy` (`plaintext`, `encrypted-at-rest-on-untrusted-peers`)
- `discovery_policy_id`
- `conflict_policy`
- `versioning_policy`
- `ignore_policy_id`
- `projection_policy_id` nullable

### Grant

A permission relationship between a share and a device or policy group.

Fields:

- `grant_id`
- `share_id`
- `subject_type` (`device`, `linked-group`, `tag`)
- `subject_id`
- `permission` (`ro`, `rw`, `owner`, `encrypted-replica`)
- `reshare_capability` (`none`, `delegate`, `admin`)
- `mount_mode_cap` (`detached`, `selective`, `full`)
- `role_id` nullable
- `created_by`
- `created_at`
- `origin` (`manual`, `policy`, `invite`, `recovery`)
- `provenance_ref` nullable


### Role profile

A reusable least-privilege bundle for grants and local adoption.
The point is to keep one coherent share/grant model while still supporting roles like read-only viewer, receive-only mirror, or encrypted cache.

Fields:

- `role_id`
- `label`
- `permission`
- `write_policy_cap` (`send-receive`, `send-only`, `receive-only`)
- `mount_mode_cap` (`detached`, `selective`, `full`)
- `plaintext_access` (`allowed`, `forbidden`)
- `reshare_capability` (`none`, `delegate`, `admin`)
- `deviation_policy_cap[]`
- `provenance_ref` nullable

### Deviation policy

A first-class policy describing what happens when a non-authoritative local target is changed anyway.
This exists so read-only, receive-only, mirror, and encrypted-replica behavior is not inferred from a fragile mix of role, mode, and share type.

Fields:

- `deviation_policy_id`
- `label`
- `allowed_write_policy[]` (`send-only`, `receive-only`, `encrypted-replica`)
- `on_local_add` (`preserve-and-flag`, `quarantine`, `auto-revert`, `block-pending-review`)
- `on_local_modify` (`preserve-and-flag`, `conflict-copy`, `auto-revert`, `block-pending-review`)
- `on_local_delete` (`preserve-and-flag`, `re-fetch`, `auto-revert`, `block-pending-review`)
- `remote_progress_when_deviated` (`continue-with-warning`, `pause-path`, `review-required`)
- `forced_by_capability` boolean
- `provenance_ref` nullable

### Deviation case

A first-class record describing one locally observed deviation on a non-authoritative mount.

Fields:

- `deviation_case_id`
- `share_ref`
- `mount_ref`
- `path`
- `class` (`local-add`, `local-modify`, `local-delete`, `local-rename`, `path-drift`)
- `policy_ref`
- `current_state` (`detected`, `preserved`, `auto-remediated`, `quarantined`, `blocked`, `resolved`)
- `remediation_mode` (`preserve-and-flag`, `re-fetch`, `auto-revert`, `conflict-copy`, `block-pending-review`)
- `remote_progress` (`continue-with-warning`, `paused-for-path`, `blocked-for-mount`)
- `local_artifact_state` (`preserved`, `copied-aside`, `quarantined`, `reverted`, `none`)
- `detected_at`
- `last_transition_at`
- `report_ref` nullable
- `decision_trace_ref` nullable
- `provenance_ref` nullable

### Stewardship record

A first-class record describing who governs a share and how authority can be handed off.
This exists so write access, grant power, and succession are not inferred from one coarse Owner bit.

Fields:

- `stewardship_id`
- `share_id`
- `steward_set[]`
- `grantor_set[]`
- `delegation_policy` (`none`, `bounded`, `open-with-cap`)
- `max_delegable_role` nullable
- `handoff_policy` (`single-steward-approval`, `dual-review`, `quorum`, `recovery-gated`)
- `candidate_successors[]`
- `departure_behavior` (`freeze-grants`, `retain-existing`, `rebind-to-successor`, `require-review`)
- `active_handoff_plan_id` nullable
- `created_at`
- `updated_at`
- `provenance_ref` nullable

### Mount

A local attachment of a share into a filesystem path. Adoption into a mount is a separate step from merely learning that the share exists.

Fields:

- `mount_id`
- `share_id`
- `path`
- `materialization_mode` (`detached`, `selective`, `full`)
- `placeholder_strategy` (`none`, `virtual`, `sidecar`)
- `pin_policy` (`manual`, `sticky`, `always-full`)
- `binding_status` (`bound`, `relocating`, `drifted`, `blocked`)
- `desired_path` nullable
- `binding_health` (`ok`, `missing-path`, `marker-drift`, `needs-compare`, `repair-required`, `blocked`)
- `last_path_probe_at` nullable
- `last_binding_receipt_ref` nullable
- `preservation_set_ref` nullable
- `visible_if_detached` boolean
- `deviation_policy_id` nullable
- `projection_policy_id` nullable
- `fidelity_contract_ref` nullable
- `path_binding_provenance_ref` nullable


### Incoming share

A share exposure that is visible locally but not yet adopted into a path.
The lifecycle is intentionally staged:

- `visible` — the share is known through linking, manual share, or recovery policy
- `incoming` — the operator can inspect and decide what to do locally
- `adopted` — the share is attached to a local path as a mount

This separates discovery from acceptance and path placement.

Fields:

- `incoming_id`
- `share_id`
- `source_device`
- `visibility_origin` (`manual-share`, `linked-policy`, `recovery`)
- `suggested_label`
- `suggested_path` nullable
- `default_mode_offer` (`detached`, `selective`, `full`)
- `adoption_status` (`pending`, `adopted`, `rejected`, `deferred`)
- `local_claim_state` (`announced-only`, `deferred-local`, `claim-in-review`, `claimed-and-bound`, `hidden-local`)
- `requires_path_choice`
- `hide_local_supported` boolean
- `wider_withdraw_supported` boolean
- `review_route` nullable
- `provenance_ref` nullable


### Path comparison

A durable comparison report for adopting or relocating a share into a target path.
This exists so non-empty-path binding is reviewable instead of guessed from later file outcomes.

Fields:

- `comparison_id`
- `share_id`
- `target_path`
- `source_ref` (`incoming`, `mount`)
- `source_id`
- `path_state` (`missing`, `empty`, `non-empty`, `already-bound-self`, `already-bound-other`, `service-marker-conflict`)
- `identical_count`
- `local_only_count`
- `remote_only_count`
- `collision_count`
- `marker_status` (`ok`, `missing`, `foreign`, `conflicting`)
- `recommended_action` (`safe-bind`, `plan-required`, `blocked`)
- `generated_at`
- `presentation_kind` nullable (`inline-direct`, `inline-review`, `drawer-required`, `blocked`)
- `review_route` nullable
- `provenance_ref` nullable


### Filesystem profile

A machine-readable summary of a local mount target's path and metadata semantics.
The point is to stop treating case collisions, normalization drift, symlink behavior, and metadata loss as after-the-fact surprises.

Fields:

- `fs_profile_id`
- `path`
- `platform_family`
- `filesystem_type`
- `case_sensitivity` (`sensitive`, `insensitive`, `unknown`)
- `unicode_normalization` (`none`, `nfc`, `nfd`, `mixed`, `unknown`)
- `utf8_requirement` (`required`, `best-effort`, `unknown`)
- `prohibited_name_rules[]`
- `prohibited_character_rules[]`
- `symlink_support` (`preserve`, `ignore`, `blocked`, `unknown`)
- `junction_support` (`preserve`, `flatten`, `blocked`, `unknown`)
- `xattr_support` (`full`, `partial`, `none`, `unknown`)
- `acl_support` (`full`, `partial`, `none`, `unknown`)
- `permission_fidelity` (`full`, `partial`, `minimal`, `unknown`)
- `timestamp_precision` (`ns`, `us`, `ms`, `s`, `unknown`)
- `clock_status` (`ok`, `warning`, `blocked`, `unknown`)
- `special_file_policy` (`ignore`, `preserve-subset`, `blocked`)
- `observed_at`
- `provenance_ref` nullable

### Filesystem compatibility report

A durable report comparing one or more filesystem profiles against the pathname and metadata demands of a share or mount action.
This exists so operators can see whether path semantics are safe before bind, adopt, restore, or role changes commit.

Fields:

- `fs_compat_report_id`
- `target_action` (`incoming-adopt`, `mount-relocate`, `grant`, `restore`, `share-set`)
- `share_id` nullable
- `subject_refs[]`
- `fs_profile_refs[]`
- `status` (`ok`, `auto-correctable`, `warning`, `blocked`)
- `path_findings[]`
- `metadata_findings[]`
- `normalization_actions[]`
- `blocked_patterns[]`
- `recommended_policy_changes[]`
- `generated_at`
- `provenance_ref` nullable

### Portability policy

A durable operator-visible policy describing how pathname, metadata, link, and notification differences should be handled for a mount or adoption workflow.

Fields:

- `portability_policy_id`
- `name`
- `scope` (`share-default`, `mount-default`, `mount-specific`, `system`)
- `path_policy` (`strict-native`, `portable-rewrite`, `portable-block`, `review-required`)
- `case_policy` (`native`, `portable-fold-safe`, `block-collision`)
- `normalization_policy` (`native`, `rewrite-nfc`, `rewrite-nfd`, `portable-utf8`, `block-mismatch`)
- `symlink_policy` (`preserve-link`, `omit`, `block`)
- `junction_policy` (`preserve`, `flatten`, `block`)
- `xattr_policy` (`preserve-full`, `portable-subset`, `copy-aside-when-unsupported`, `drop-with-receipt`)
- `acl_policy` (`preserve-full`, `portable-subset`, `drop-with-receipt`, `block`)
- `special_file_policy` (`block`, `preserve-subset`, `omit-with-receipt`)
- `notification_requirement` (`continuous-required`, `continuous-preferred`, `periodic-ok`)
- `network_share_posture` (`forbid`, `warn`, `allow-reviewed`)
- `created_at`
- `provenance_ref` nullable

### Fidelity contract

A durable mount-scoped contract describing what filesystem semantics the daemon currently promises on the chosen path.

Fields:

- `fidelity_contract_id`
- `mount_ref`
- `share_ref`
- `fs_profile_ref`
- `fs_compat_report_ref`
- `portability_policy_ref`
- `support_tier` (`linux-first`, `best-effort`, `warning-tier`, `blocked`)
- `path_semantics` (`native`, `rewritten`, `mixed`, `blocked`)
- `metadata_semantics` (`full`, `portable-subset`, `best-effort`, `none`)
- `notification_semantics` (`continuous`, `periodic-rescan`, `mixed`, `unknown`)
- `network_path_state` (`local-native`, `network-reviewed`, `network-unreviewed`, `unknown`)
- `active_downgrades[]`
- `blocked_classes[]`
- `virtualized_classes[]`
- `last_verified_at`
- `verification_state` (`fresh`, `stale`, `drifted`, `blocked`)
- `provenance_ref` nullable

### Fidelity receipt

A durable record proving which filesystem-fidelity tradeoffs were accepted or applied.

Fields:

- `fidelity_receipt_id`
- `mount_ref`
- `share_ref`
- `action_kind` (`adopt`, `relocate`, `repair`, `policy-change`, `drift-accept`)
- `portability_policy_ref`
- `fidelity_contract_ref`
- `accepted_downgrades[]`
- `blocked_classes[]`
- `network_share_acknowledged` boolean
- `notification_posture_acknowledged` boolean
- `decision_trace_ref` nullable
- `completed_at`
- `provenance_ref` nullable

### Convergence report

A durable report describing whether current share state is merely idle, transfer-complete, or trustworthy enough to treat as settled for a specific purpose.
This exists so operators do not infer cutover safety from peer counts and warning badges alone.

Fields:

- `convergence_report_id`
- `target_scope` (`share`, `mount`, `device`, `system`)
- `target_ref`
- `intent` (`status`, `cutover`, `backup`, `relocate`, `restore`, `maintenance-drain`)
- `state` (`idle`, `syncing`, `converged`, `degraded-converged`, `blocked`, `unknown`)
- `local_need_bytes`
- `local_need_items`
- `remote_need_bytes` nullable
- `remote_need_items` nullable
- `reachable_sources`
- `required_sources`
- `watcher_health` (`ok`, `degraded`, `unknown`)
- `clock_health` (`ok`, `warning`, `blocked`, `unknown`)
- `background_work` (`none`, `hashing`, `merging`, `dedup-copy`, `mixed`, `unknown`)
- `detection_mode` (`continuous`, `periodic-rescan`, `mixed`, `unknown`)
- `blocking_findings[]`
- `confidence` (`high`, `medium`, `low`, `none`)
- `recommended_wait` nullable
- `generated_at`
- `provenance_ref` nullable

### Settlement policy

A durable operator-visible rule describing what convergence evidence is required before an action may claim the target is settled enough.

Fields:

- `settlement_policy_id`
- `name`
- `intent` (`status`, `cutover`, `backup`, `relocate`, `restore`, `maintenance-drain`, `custom`)
- `required_confidence` (`high`, `medium`, `low`)
- `required_state` (`converged`, `degraded-converged`)
- `required_source_mode` (`all-reachable`, `all-required`, `all-writable`, `witness-set`, `minimum-count`)
- `required_source_refs[]` nullable
- `minimum_source_count` nullable
- `require_continuous_detection` boolean
- `allow_periodic_rescan` boolean
- `allow_background_work` (`none`, `safe-read-only`, `non-mutating`, `any`)
- `allow_clock_warnings` boolean
- `max_report_age`
- `quiet_window`
- `stale_after`
- `created_by`
- `created_at`
- `provenance_ref` nullable

### Settlement barrier

A refreshable readiness gate for one target and one intent.

Fields:

- `settlement_barrier_id`
- `target_type` (`share`, `mount`, `device`, `system`, `plan`)
- `target_id`
- `intent` (`status`, `cutover`, `backup`, `relocate`, `restore`, `maintenance-drain`, `custom`)
- `policy_ref`
- `current_convergence_report_ref`
- `current_state` (`pending`, `satisfied`, `degraded-satisfied`, `blocked`, `stale`, `expired`, `canceled`)
- `evidence_age`
- `quiet_window_elapsed`
- `required_sources[]`
- `present_sources[]`
- `missing_sources[]`
- `failed_clauses[]`
- `next_safe_actions[]`
- `created_by`
- `created_at`
- `last_evaluated_at`
- `satisfied_at` nullable
- `expires_at` nullable

### Settlement receipt

A durable receipt proving which readiness bar an action crossed.

Fields:

- `settlement_receipt_id`
- `subject_type` (`plan`, `cutover`, `backup`, `restore`, `relocate`, `delete`, `maintenance-freeze`, `custom`)
- `subject_id`
- `target_refs[]`
- `intent`
- `policy_ref`
- `barrier_ref` nullable
- `accepted_convergence_report_ref`
- `accepted_state` (`satisfied`, `degraded-satisfied`)
- `accepted_confidence`
- `accepted_sources[]`
- `accepted_missing_sources[]`
- `accepted_detection_mode`
- `accepted_background_work`
- `accepted_clock_health`
- `accepted_at`
- `expires_at` nullable
- `operator_ref`
- `notes` nullable
- `provenance_ref` nullable

### Ignore policy

A supported rule set that controls what the local daemon ignores for a share.
The point is not only filtering.
The point is that ignore behavior should be inspectable and mutable without editing hidden dotfiles.

Fields:

- `ignore_policy_id`
- `projection_policy_id` nullable
- `share_id`
- `consistency_mode` (`local-ok`, `warn-on-drift`, `require-match`)
- `rules[]` (stable rule objects)
- `default_rule_source` (`built-in`, `profile`, `import`)
- `drift_status` (`unknown`, `in-sync`, `drifted`)
- `provenance_ref` nullable

### Projection policy

A first-class rule set that controls share-wide namespace announcement or local mount-view projection.
This exists so operators can tell the difference between:

- suppressing a path from the share namespace peers learn about
- hiding a path only on one local mount
- showing a path as placeholder/metadata-only instead of fully materialized bytes
- tightening a rule after structure or bytes already exist

Fields:

- `projection_policy_id`
- `subject_type` (`share`, `mount`)
- `subject_id`
- `rule_ordering` (`first-match`)
- `default_namespace_visibility` (`visible`, `hidden`) nullable
- `default_remote_announcement` (`announce`, `suppress`) nullable
- `default_local_projection` (`omit`, `placeholder`, `metadata-only`, `full`) nullable
- `tighten_behavior` (`no-retrochange`, `review-existing`, `evict-existing-safe`, `block-until-reviewed`)
- `rules[]` (stable rule objects with match, namespace_visibility, remote_announcement, local_projection)
- `drift_status` (`unknown`, `in-sync`, `drifted`)
- `provenance_ref` nullable

### Share layout contract

A durable contract describing where a share's ordinary live namespace ends and where managed sync state lives.
This exists so operators do not have to infer from hidden folders or odd suffixes whether a byte is user content, rollback/history state, temp-transfer residue, or metadata-carry machinery.

Fields:

- `share_layout_contract_id`
- `share_ref`
- `mount_ref` nullable
- `live_root_path`
- `live_namespace_state` (`clean`, `mixed-managed`, `legacy-import`, `inspect-only`, `blocked`)
- `layout_class` (`external-annex`, `adjacent-managed`, `in-tree-explicit`, `legacy-imported`, `unknown`)
- `annex_path` nullable
- `annex_visibility` (`not-mounted`, `managed-visible`, `in-tree-explicit`, `unknown`)
- `managed_byte_classes[]`
- `history_storage_class` (`external-annex`, `adjacent-managed`, `in-tree-explicit`, `disabled`, `legacy-import`)
- `temp_residue_policy` (`external-only`, `adjacent-managed`, `in-tree-explicit`, `mixed`, `unknown`)
- `metadata_carry_mode` (`native-only`, `annex-sidecar`, `in-tree-sidecar-explicit`, `drop-with-receipt`, `unknown`)
- `ignore_policy_ref` nullable
- `projection_policy_ref` nullable
- `cleanup_risk_state` (`none`, `review-required`, `preservation-required`, `blocked`, `unknown`)
- `last_verified_at`
- `provenance_ref` nullable

### Share layout review

A reviewed case for inspecting or changing how managed sync bytes relate to the ordinary live tree.
This exists so annex migration, legacy-import cleanup, metadata-carry sidecars, and history/temp residue do not collapse into `show hidden files` and `delete weird directory` ritual.

Fields:

- `share_layout_review_id`
- `share_ref`
- `mount_ref` nullable
- `current_layout_contract_ref`
- `requested_layout_class` (`external-annex`, `adjacent-managed`, `in-tree-explicit`, `inspect-only`, `cleanup-only`)
- `requested_visibility_posture` (`external-only`, `adjacent-managed`, `in-tree-explicit`, `inspect-only`)
- `live_namespace_findings[]`
- `annex_findings[]`
- `residue_findings[]`
- `cleanup_requirements[]`
- `action_options[]`
- `share_layout_report_ref`
- `generated_at`
- `expires_at` nullable

### Layout receipt

A durable record proving what share layout was accepted, migrated, cleaned, or preserved.

Fields:

- `layout_receipt_id`
- `review_ref`
- `share_ref`
- `live_namespace_summary`
- `annex_summary`
- `residue_summary`
- `cleanup_summary`
- `actor_ref`
- `created_at`
- `provenance_ref` nullable

### Semantic runtime contract

A durable contract describing what semantic guarantees the daemon currently makes for a subject under the current runtime/target posture.
This exists so operators do not have to guess whether an `optimization` really preserved freshness, rename continuity, diff behavior, verification, and conflict honesty.

Fields:

- `semantic_runtime_contract_id`
- `subject_ref`
- `mount_ref` nullable
- `runtime_seat_ref` nullable
- `optimization_profile` (`balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, `full-verify`, `custom`)
- `detection_posture` (`notifications-primary`, `notifications-plus-rescan`, `rescan-biased`, `rescan-only`, `unknown`)
- `rename_continuity_posture` (`preserved`, `preserved-with-history`, `uncertain`, `degraded-to-recopy`, `blocked`, `unknown`)
- `delta_transfer_posture` (`diff-preferred`, `whole-file-fallback`, `whole-file-only`, `direct-nonresumable-fastpath`, `unknown`)
- `verification_posture` (`eager`, `lazy`, `post-write-verify`, `database-only-for-some-fields`, `unknown`)
- `conflict_honesty_posture` (`normal`, `suppressed-but-blocking`, `degraded`, `unknown`)
- `target_degradation_class` (`none`, `network-share`, `watcher-exhausted`, `mixed-access-risk`, `path-semantics-risk`, `unknown`)
- `guarantee_warnings[]`
- `last_verified_at`
- `provenance_ref` nullable

### Semantic optimization review

A reviewed case for changing runtime behavior that may weaken meaning while improving speed or compatibility.
This exists so lazy proof, rescan-only detection, whole-file fallback, or degraded-target acceptance do not collapse into reassuring speed language.

Fields:

- `semantic_optimization_review_id`
- `subject_ref`
- `mount_ref` nullable
- `current_semantic_runtime_contract_ref`
- `requested_profile` (`balanced`, `large-preseeded-intake`, `degraded-network-share`, `lazy-proof`, `full-verify`, `custom`)
- `requested_change_class` (`profile-switch`, `degraded-target-acceptance`, `one-off-mitigation`, `restore-stronger-guarantees`, `inspect-only`)
- `guarantee_deltas[]`
- `detection_findings[]`
- `verification_findings[]`
- `target_findings[]`
- `action_options[]`
- `semantic_runtime_report_ref`
- `generated_at`
- `expires_at` nullable

### Semantic optimization receipt

A durable record proving which guarantees were preserved, weakened, or later restored by a reviewed optimization change.

Fields:

- `semantic_optimization_receipt_id`
- `review_ref`
- `subject_ref`
- `profile_summary`
- `guarantees_preserved[]`
- `guarantees_weakened[]`
- `restoration_requirements[]`
- `actor_ref`
- `created_at`
- `provenance_ref` nullable


### Retained replica posture

A durable statement of what a peer currently retains for a share and what that peer can still do with those bytes.
This exists so operators do not have to guess whether `revoked`, `removed`, and `recalled` meant the same thing.

Fields:

- `retained_replica_posture_id`
- `share_ref`
- `peer_ref` nullable
- `replica_scope` (`linked-constellation`, `direct-grantee`, `encrypted-backup`, `local-derivation`, `unknown-offline`)
- `authority_posture` (`owner`, `write`, `read-only`, `encrypted-readonly`, `revoked-future`, `unknown`)
- `byte_presence_posture` (`materialized`, `metadata-only`, `encrypted-materialized`, `unknown`)
- `future_update_posture` (`active`, `frozen`, `revoked-pending-observation`, `revoked-observed`, `unknown`)
- `recovery_contribution_posture` (`can-upload`, `can-reseed-with-continuity-material`, `retained-storage-only`, `cannot-contribute`, `unknown`)
- `recall_verdict` (`not-requested`, `retained-copy-confirmed`, `future-updates-stopped`, `remote-delete-requested`, `remote-delete-observed`, `unknown-offline`)
- `residue_findings[]`
- `last_verified_at`
- `provenance_ref` nullable

### Replica recall review

A reviewed case for changing future authority while staying honest about already-retained bytes.
This exists so disconnect, revoke, remove, encrypted-backup preservation, and remote-delete requests do not collapse into one comforting but misleading `remove` story.

Fields:

- `replica_recall_review_id`
- `share_ref`
- `peer_refs[]`
- `current_retained_replica_posture_refs[]`
- `requested_boundary_change` (`revoke-future-updates`, `narrow-authority`, `retire-linked-presence`, `request-copy-recall`, `inspect-only`)
- `requested_byte_outcome` (`retain-existing-copies`, `attest-existing-copies`, `request-remote-delete`, `future-stop-only`, `unknown`)
- `authority_findings[]`
- `retention_findings[]`
- `recovery_findings[]`
- `observation_requirements[]`
- `action_options[]`
- `replica_recall_report_ref`
- `generated_at`
- `expires_at` nullable

### Replica recall receipt

A durable record proving what future authority changed and what retained-copy claim was honestly supported.

Fields:

- `replica_recall_receipt_id`
- `review_ref`
- `share_ref`
- `peer_summary`
- `future_update_summary`
- `retained_copy_summary`
- `recovery_dependency_summary`
- `observation_summary`
- `actor_ref`
- `created_at`
- `provenance_ref` nullable


### Share authority epoch

A durable record of one generation of share authority material.
This exists so operators do not have to guess whether `rotated`, `re-shared`, `upgraded`, and `changed permissions` all describe the same trust reality.

Fields:

- `share_authority_epoch_id`
- `share_ref`
- `epoch_handle`
- `authority_class` (`key-backed`, `certificate-backed`, `derived-local`, `encrypted-derivative`, `unknown-legacy`)
- `status` (`current`, `superseded`, `quarantined`, `retired-observed`, `unknown-offline`)
- `issued_from_epoch_ref` nullable
- `peer_refs[]`
- `offer_refs[]`
- `derivative_refs[]`
- `grant_refs[]`
- `stale_capability_posture` (`none-known`, `artifact-only`, `still-redeemable`, `live-peer-set`, `unknown-offline`)
- `convergence_verdict` (`not-started`, `new-epoch-issued`, `mixed-epoch`, `old-epoch-quarantined`, `observed-new-epoch-only`, `unknown-offline`)
- `issued_at`
- `last_observed_at` nullable
- `provenance_ref` nullable

### Epoch rotation review

A reviewed case for changing share authority material or share class without lying about old capability residue or mixed-epoch drift.
This exists so `rotate`, `re-share`, and `upgrade share` do not collapse into a reassuring but incomplete one-liner.

Fields:

- `epoch_rotation_review_id`
- `share_ref`
- `current_epoch_ref`
- `prior_epoch_refs[]`
- `requested_change_class` (`rotate-authority-material`, `narrow-share-authority`, `upgrade-share-class`, `reissue-derived-scope`, `inspect-only`)
- `requested_outcome` (`issue-new-epoch`, `retire-old-epoch`, `quarantine-old-epoch`, `upgrade-authority-class`, `inspect-only`)
- `stale_capability_findings[]`
- `derivative_migration_findings[]`
- `convergence_requirements[]`
- `follow_on_review_refs[]`
- `action_options[]`
- `epoch_rotation_report_ref`
- `generated_at`
- `expires_at` nullable

### Epoch rotation receipt

A durable record proving which authority epoch became current, what older capability residue remained, and what convergence was actually observed.

Fields:

- `epoch_rotation_receipt_id`
- `review_ref`
- `share_ref`
- `current_epoch_summary`
- `superseded_epoch_summary`
- `stale_capability_summary`
- `derivative_migration_summary`
- `convergence_summary`
- `actor_ref`
- `created_at`
- `provenance_ref` nullable

### Conflict item

A structured record of a detected conflict or path collision.
Conflicts are first-class cases, not just filenames with a suffix.

Fields:

- `conflict_id`
- `share_id`
- `path`
- `kind` (`content`, `case`, `delete-vs-modify`, `path-mapping`, `capability`)
- `semantic_class` (`content-concurrency`, `delete-vs-modify`, `case-collision`, `unicode-collision`, `path-mapping`, `materialization-mismatch`, `capability-mismatch`)
- `status` (`open`, `resolved`, `deferred`)
- `candidates[]`
- `propagation_scope_hint` (`local-only`, `replicated`, `mixed`, `blocked`)
- `loser_handling_options[]`
- `recommended_actions[]`
- `review_model` nullable
- `detected_at`
- `history_refs[]`
- `provenance_ref` nullable

### History entry

A durable timeline record for a prior file state or rollback-relevant event.
This exists so operators can ask what changed, where the prior bytes came from, and what confidence the product has in that answer without opening hidden archive state.

Fields:

- `history_entry_id`
- `share_id`
- `path`
- `entry_kind` (`remote-replaced`, `remote-deleted`, `local-rollback-candidate`, `conflict-candidate`, `deviation-artifact`, `restored`, `resolved-conflict`)
- `capture_reason` (`remote-update`, `remote-delete`, `conflict-detected`, `deviation-preserved`, `operator-restore`, `operator-resolution`)
- `captured_from_peer_ref` nullable
- `captured_at`
- `retention_horizon` nullable
- `storage_class` (`history-store`, `preservation-copy`, `derived-remote`, `mixed`)
- `scope_allowances[]` (`mount-local`, `device-local`, `share-plan`)
- `confidence` (`high`, `guarded`, `low`)
- `provenance_ref` nullable

### Rollback receipt

A durable explanation record proving how a restore or conflict-resolution action actually completed.

Fields:

- `rollback_receipt_id`
- `share_ref`
- `path`
- `source_type` (`history-entry`, `conflict-case`, `deviation-artifact`, `manual-import`)
- `source_ref`
- `action_kind` (`restore-local`, `restore-share`, `resolve-conflict`, `copy-aside-and-restore`, `quarantine-and-continue`)
- `scope` (`mount-local`, `device-local`, `share-plan`)
- `loser_handling` (`left-intact`, `copied-aside`, `quarantined`, `deleted-sharewide`, `deleted-local`, `unknown`)
- `settlement_receipt_ref` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `blocked`, `cancelled`, `reverted`)
- `provenance_ref` nullable

### Invite

A capability-bearing token or file used to add a device to a share or constellation.
The invite is the offered capability, not the acceptance itself.

Fields:

- `invite_id`
- `target_scope` (`device-link`, `share-access`)
- `permissions`
- `expiry`
- `one_time`
- `peer_pinning`
- `transport_hints[]`
- `offered_role_id` nullable
- `claim_required` (`true`, `false`)

### Claim

A durable acceptance record prepared from an invite or incoming share before it mutates local state.
Claims exist so operators can inspect the difference between “this was offered” and “this machine accepted it this way.”

Fields:

- `claim_id`
- `source_type` (`invite`, `incoming`)
- `source_ref`
- `target_action` (`link`, `grant`, `incoming-adopt`)
- `requested_role_id` nullable
- `requested_linked_group_id` nullable
- `requested_member_class` nullable
- `requested_path` nullable
- `requested_mode` nullable
- `claim_effect_scope` (`local-only`, `local-bind`, `authority-widening`, `authority-withdrawal`)
- `status` (`draft`, `preflighted`, `planned`, `applied`, `rejected`, `expired`)
- `compatibility_report_id` nullable
- `provenance_ref` nullable
- `review_model` nullable

### Local derivation case

A durable plan-bearing record for creating or changing a same-host derivative of an existing share or mount.
This exists so operators can inspect the difference between “pick another local path” and “create a new self-edge with specific topology, authority, lifecycle, and target-tier consequences.”

Fields:

- `local_derivation_case_id`
- `source_share_ref`
- `source_mount_ref` nullable
- `target_path`
- `target_profile_ref` nullable
- `target_tier` (`local-native`, `removable-reviewed`, `network-reviewed`, `warning`, `blocked`)
- `derivation_kind` (`read-only-derivative`, `writable-derivative`, `cache-branch`, `export-like`, `blocked-self-edge`)
- `topology_relation` (`disjoint`, `sibling`, `child`, `parent`, `overlap`, `ambiguous`)
- `loop_risk` (`none`, `guarded`, `high`, `blocked`)
- `authority_coupling` (`inherit-narrow-only`, `inherit-rw`, `local-writeback`, `blocked`)
- `lifecycle_coupling` (`source-detach-detaches-target`, `source-detach-freezes-target`, `independent-after-apply`, `blocked`)
- `materialization_posture` (`source-full`, `source-partial`, `source-placeholder-heavy`, `target-cache-only`, `blocked`)
- `status` (`draft`, `preflighted`, `planned`, `applied`, `rejected`, `expired`)
- `review_model` nullable
- `compatibility_report_id` nullable
- `provenance_ref` nullable

### Topology review case

A durable plan-bearing record for accepting, rejecting, or repairing a graph relationship among shares, mounts, and local paths.
This exists so operators can inspect the difference between “another folder here” and “a new nested, overlapping, moved, or root-boundary-sensitive topology with specific propagation consequences.”

Fields:

- `topology_case_id`
- `primary_subject_ref`
- `related_subject_refs[]`
- `candidate_path` nullable
- `topology_kind` (`nested-share`, `overlap`, `parent-child`, `cross-share-move`, `same-host-self-edge`, `root-boundary`, `ambiguous`)
- `containment_relation` (`disjoint`, `child`, `parent`, `overlap`, `ambiguous`, `outside-allowed-root`)
- `propagation_shape` (`independent`, `double-indexed`, `piggyback-via-parent`, `self-edge`, `re-download-likely`, `blocked`)
- `path_continuity_posture` (`stable`, `rename-local-only`, `rebind-required`, `disconnect-reconnect-like`, `blocked`)
- `selective_sync_posture` (`allowed`, `disabled-required`, `blocked`, `n/a`)
- `root_boundary_posture` (`within-root`, `needs-root-expansion`, `violates-root-policy`, `unknown`)
- `status` (`draft`, `preflighted`, `planned`, `applied`, `rejected`, `expired`)
- `review_model` nullable
- `compatibility_report_id` nullable
- `provenance_ref` nullable

### Contention review case

A durable plan-bearing record for coordinating contested paths where another writer, degraded notifications, or mixed access means sync progress is no longer just “transfer activity.”
This exists so operators can inspect the difference between “retry later” and “a reviewed contention situation with specific quiesce, propagation, and freshness consequences.”

Fields:

- `contention_case_id`
- `primary_subject_ref`
- `path_refs[]`
- `trigger_kind` (`locked-files`, `delay-profile-hit`, `external-writer-suspected`, `notification-loss-with-write-pressure`, `smb-mixed-access`, `manual-quiesce`, `unknown`)
- `writer_posture` (`none-confirmed`, `likely-local-app`, `likely-network-client`, `likely-service-writer`, `mixed`, `unknown`)
- `lock_scope` (`none`, `path-set`, `subtree`, `share-wide`, `unknown`)
- `notification_posture` (`continuous`, `periodic-rescan`, `mixed`, `unknown`)
- `filesystem_risk_posture` (`local-native`, `network-reviewed`, `warning-tier`, `blocked`, `unknown`)
- `quiesce_posture` (`none`, `delay-profile-active`, `upload-hold`, `bidirectional-freeze`, `maintenance-freeze`, `reader-only-guard`, `blocked`)
- `propagation_risk` (`none`, `delayed-only`, `overwrite-risk`, `rollback-risk`, `corruption-risk`, `blocked`)
- `delay_profile_ref` nullable
- `status` (`draft`, `preflighted`, `planned`, `applied`, `released`, `rejected`, `expired`)
- `review_model` nullable
- `evidence_refs[]`
- `provenance_ref` nullable

### Contention receipt

A durable explanation record proving what coordination action was applied to a contested path and what propagation it intentionally held back.

Fields:

- `contention_receipt_id`
- `contention_case_ref`
- `action_kind` (`delay-profile-applied`, `upload-held`, `bidirectional-frozen`, `reader-guard-applied`, `escalated-review`, `released`, `cancelled`)
- `scope_ref`
- `effective_quiesce_posture`
- `propagation_expectation` (`local-writes-preserved`, `remote-writes-held`, `delete-propagation-held`, `rescan-required`, `review-pending`)
- `expires_at` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `released`, `cancelled`, `blocked`)
- `provenance_ref` nullable

### Capacity-fit review case

A durable plan-bearing record for deciding whether a host can honestly carry a subject and under what local mode.
This exists so operators can inspect the difference between “add the folder” and “accept this subject on this machine with specific RAM, watcher, indexing, storage, and freshness consequences.”

Fields:

- `capacity_fit_case_id`
- `primary_subject_ref`
- `candidate_path` nullable
- `requested_local_role` (`full-materialize`, `selective-materialize`, `metadata-only`, `receive-only`, `preseeded-adopt`, `cache-derivative`, `blocked`)
- `estimated_entry_count` nullable
- `estimated_total_bytes` nullable
- `memory_posture` (`comfortable`, `guarded`, `high-risk`, `blocked`, `unknown`)
- `watcher_posture` (`continuous-available`, `near-limit`, `rescan-fallback`, `unsupported`, `unknown`)
- `index_cost_posture` (`ordinary`, `heavy-initial-index`, `heavy-preseed-verify`, `parallel-index-risk`, `unknown`)
- `storage_headroom_posture` (`comfortable`, `warning`, `guarded`, `blocked`, `unknown`)
- `freshness_posture` (`continuous`, `mixed`, `periodic-rescan`, `blocked`, `unknown`)
- `portability_blocker_posture` (`none-known`, `path-length-risk`, `encoding-risk`, `merge-tree-risk`, `filesystem-error-risk`, `topology-coupled`, `unknown`)
- `admission_posture` (`full-ok`, `selective-preferred`, `metadata-only-preferred`, `narrow-scope-required`, `reclaim-first`, `reject-on-this-host`)
- `status` (`draft`, `preflighted`, `planned`, `applied`, `deferred`, `rejected`, `expired`)
- `review_model` nullable
- `evidence_refs[]`
- `provenance_ref` nullable

### Capacity-fit receipt

A durable explanation record proving how a host-fit decision was made for a subject and what local mode or degradation was knowingly accepted.

Fields:

- `capacity_fit_receipt_id`
- `capacity_fit_case_ref`
- `action_kind` (`accepted-full`, `accepted-selective`, `accepted-metadata-only`, `accepted-narrowed-scope`, `deferred-for-reclaim`, `escalated-review`, `rejected-host`)
- `scope_ref`
- `effective_local_role`
- `effective_freshness_posture`
- `accepted_limits[]`
- `follow_up_refs[]`
- `completed_at`
- `outcome` (`applied`, `deferred`, `rejected`, `blocked`)
- `provenance_ref` nullable

### Approval memory

A durable record that some future approvals may proceed without a fresh prompt, but only within bounded scope.
This exists so “approved before” is inspectable state rather than hidden certificate memory.

Fields:

- `approval_id`
- `subject_identity_ref`
- `granted_by_ref`
- `scope` (`share`, `share-tag`, `linked-group`)
- `scope_ref` nullable
- `max_role_id` nullable
- `max_permission` (`ro`, `rw`, `owner`, `encrypted-replica`)
- `approver_scope` (`origin-only`, `linked-group`, `named-devices`)
- `approver_devices[]`
- `expires_at` nullable
- `status` (`active`, `revoked`, `expired`)
- `last_used_at` nullable
- `provenance_ref` nullable

### Linked-group policy

A reusable policy that defines what linking should and should not imply.

Fields:

- `linked_group_id`
- `label`
- `default_mount_mode`
- `auto_grant_rule` (`none`, `prompt`, `tagged-shares-only`, `all-new-shares`)
- `max_permission` (`ro`, `rw`)
- `allow_share_visibility_without_mount` (`true`, `false`)


### Compatibility report

A durable preview object that explains whether a pending link, invite acceptance, grant, or adoption action is safe to commit.

Fields:

- `report_id`
- `target_action` (`link`, `invite-accept`, `grant`, `incoming-adopt`, `share-set`)
- `subject_refs[]`
- `status` (`ok`, `warning`, `blocked`)
- `blockers[]`
- `warnings[]`
- `downgrades[]`
- `authority_changes[]`
- `recommended_roles[]`
- `generated_at`
- `provenance_ref` nullable

### Publication profile

A first-class supported summary of what the daemon publishes about reachability.
This may exist as its own object or as a supported nested object inside discovery policy, but it must be inspectable directly.

Fields:

- `publication_profile_id`
- `scope_type` (`system`, `policy`, `share`)
- `scope_id` nullable
- `publish_presence_via[]` (`lan`, `private-discovery`, `public-tracker`, `tor-onion`, `i2p-destination`)
- `publish_endpoint_classes[]` (`lan-addresses`, `approved-known-hosts`, `tor-onion`, `i2p-destination`)
- `audience_classes[]` (`local-broadcast-domain`, `approved-peer`, `named-endpoint`, `private-infra`, `public-infra`)
- `published_identity_classes[]` (`device-stable-id`, `ephemeral-device-alias`, `share-membership`, `share-label`)
- `published_endpoint_classes_detail[]` (`listen-port`, `local-ip`, `public-ip`, `overlay-endpoint`, `known-host-address`)
- `share_membership_visibility` (`none`, `approved-peers-only`, `discovery-service-visible`)
- `endpoint_cache_policy` (`disabled`, `ephemeral`, `retained-with-ttl`, `retained-until-cleared`)
- `clear_cache_on_narrowing` (`true`, `false`)
- `residual_disclosure_policy` (`none`, `ttl-bound`, `provider-defined`, `until-cleared`, `rotate-required`)
- `provenance_ref` nullable

### Disclosure report

A supported preview/status object that answers what audience classes can currently learn which fact classes, by which mechanisms, and what residue may remain after a narrowing change.

Fields:

- `disclosure_report_id`
- `subject_type` (`policy`, `share`, `peer`, `route`, `constellation`)
- `subject_id`
- `baseline_publication_profile_ref`
- `effective_publication_profile_ref`
- `effective_audiences[]`
- `effective_fact_matrix[]`
- `residual_findings[]`
- `widening_steps[]`
- `narrowing_steps[]`
- `generated_at`
- `decision_trace_ref` nullable

### Disclosure receipt

A durable record proving that publication widened, narrowed, or residual disclosure was acknowledged or cleared.

Fields:

- `disclosure_receipt_id`
- `subject_ref`
- `action` (`widen-publication`, `narrow-publication`, `clear-residue`, `rotate-publication-endpoint`, `acknowledge-residual-risk`)
- `before_summary`
- `after_summary`
- `residual_delta_summary`
- `actor_ref`
- `created_at`

### Known-host record

A peer-pinned direct-path admission record.
This exists so “I trust this peer at this address” does not silently widen into “public direct is generally allowed now”.

Fields:

- `known_host_id`
- `peer_id`
- `address`
- `scope_type` (`system`, `policy`, `share`, `peer-share`)
- `scope_id` nullable
- `allowed_use` (`dial-only`, `dial-and-accept`)
- `origin` (`manual`, `recovery`, `import`, `policy-derived`)
- `created_by`
- `created_at`
- `expires_at` nullable
- `last_verified_at` nullable
- `health_state` (`unknown`, `reachable`, `stale`, `failed`)
- `provenance_ref` nullable

### Exposure report

A supported preview/status object that answers what reachability facts are currently being published and which steps would widen exposure.

Fields:

- `exposure_report_id`
- `subject_type` (`policy`, `share`, `peer`, `route`)
- `subject_id`
- `baseline_publication_profile_ref`
- `active_route_leases[]`
- `currently_published_to[]` (`lan`, `approved-peer`, `private-infra`, `public-infra`)
- `published_endpoint_classes[]`
- `candidate_route_classes[]`
- `widening_steps[]`
- `cached_endpoint_findings[]`
- `recommended_actions[]`
- `generated_at`
- `decision_trace_ref` nullable

### Discovery policy

How peers are found, what reachability is published, and how fallback is handled.
A serious operator surface must separate announcement from dialing.
It must also distinguish overlay-first privacy routing from faster clearnet direct options.

Fields:

- `discovery_policy_id`
- `announce_scope` (`off`, `lan-only`, `private-infra-only`, `public-ok`)
- `announce_via[]` (`lan`, `tracker`, `private-discovery`, `tor-onion`, `i2p-destination`)
- `dial_via[]` (`known-host-clearnet`, `lan-direct`, `public-direct`, `private-relay`, `public-relay`, `tor`, `i2p`)
- `tracker_mode` (`enabled`, `disabled`, `private-only`)
- `relay_mode` (`enabled`, `disabled`, `trusted-only`, `private-only`)
- `relay_pool` (`public`, `private`, `mixed`, `none`)
- `tor_mode` (`disabled`, `allowed`, `preferred`, `required`)
- `i2p_mode` (`disabled`, `allowed`, `preferred`, `required`)
- `lan_discovery` (`enabled`, `disabled`)
- `clearnet_direct_mode` (`disabled`, `manual-opt-in`, `allowed`)
- `manual_speed_override_scope` (`none`, `per-share`, `per-peer`, `per-device`, `per-policy`)
- `known_hosts[]`
- `listen_addresses[]`
- `fallback_order[]`
- `cache_public_endpoints` (`enabled`, `disabled`)
- `accept_inbound_from` (`approved-peers`, `known-hosts-only`, `policy-bound`)
- `transport_runtime_refs[]`
- `exposure_summary_ref` nullable
- `decision_trace_ref` nullable

Notes:

- the default WAN-oriented privacy policy should prefer Tor and/or I2P before any public direct path
- WAN clearnet direct should require manual enablement rather than silently participating by default
- a policy may still allow LAN direct as a normal local-network behavior without enabling WAN clearnet direct

### Transport runtime

A supported object describing one transport engine that the daemon can use or activate.
This exists so bundled privacy transports do not become hidden magic.

Fields:

- `transport_runtime_id`
- `engine` (`lan`, `clearnet`, `tor`, `i2p`)
- `integration_kind` (`native`, `embedded-helper`)
- `binary_origin` (`compiled-in`, `embedded-payload`, `system-external`)
- `lifecycle_state` (`off`, `lazy`, `warming`, `ready`, `degraded`, `failed`)
- `version`
- `runtime_path` nullable
- `payload_version` nullable
- `payload_digest` nullable
- `persistence_dir` nullable
- `update_mode` (`daemon-release-only`, `independent-payload`, `external-managed`)
- `provenance_summary` nullable
- `last_verified_at` nullable
- `policy_disable_reason` nullable
- `runtime_owner` (`daemon`, `external`, `shared`)
- `bootstrap_state` (`not-required`, `pending`, `in-progress`, `ready`, `degraded`, `failed`)
- `health_findings[]`
- `last_started_at` nullable
- `last_failed_at` nullable
- `decision_trace_ref` nullable

### Transport session

A public object describing how a transport runtime is currently being used for real route work.

This exists because an operator should be able to distinguish:

- “Tor is installed”
- “Tor is warm”
- “Tor is currently carrying these routes”
- “I2P is warm but only one long-lived session is being reused for this share class”
- “clearnet direct is active only because a manual speed override created a temporary route lease”

Fields:

- `transport_session_id`
- `engine` (`tor`, `i2p`, `clearnet`)
- `runtime_ref`
- `scope_type` (`system`, `policy`, `share`, `peer`)
- `scope_id` nullable
- `session_strategy` (`singleton`, `shared-pool`, `dedicated`)
- `privacy_class` (`overlay`, `local-direct`, `wan-direct`)
- `state` (`planned`, `opening`, `ready`, `active`, `cooling`, `degraded`, `failed`)
- `identity_scope` (`system`, `policy`, `share`, `peer`, `implementation-defined`)
- `endpoint_summary`
- `reuse_policy` (`reuse-preferred`, `reuse-required`, `ephemeral-ok`)
- `opened_at`
- `last_used_at` nullable
- `active_route_count`
- `reason`
- `decision_trace_ref` nullable

Notes:

- I2P should usually prefer a very small number of long-lived shared sessions rather than per-transfer session churn
- public WAN clearnet direct should normally appear only through an explicit override or policy exception
- LAN direct may still be ordinary and non-alarming within a local-only policy

### Decision trace

A structured explanation for why a high-signal outcome won.

Fields:

- `decision_trace_id`
- `subject_type` (`route`, `grant`, `approval`, `claim`, `restore`, `mount-bind`, `recovery`)
- `subject_id`
- `decision_kind` (`selection`, `authorization`, `adoption`, `restore-scope`, `rebind`)
- `selected_outcome`
- `candidate_outcomes[]`
- `rejected_candidates[]` with `reason_code`, `reason_text`
- `facts[]` (`policy`, `capability`, `cache`, `precondition`, `operator-choice`)
- `policy_refs[]`
- `cache_refs[]`
- `generated_at`
- `stale_at` nullable
- `provenance_ref` nullable

### Binding receipt

A durable audit record for one adopt/relocate/repair/detach/reconnect operation.

Fields:

- `binding_receipt_id`
- `share_ref`
- `mount_ref` nullable
- `action` (`adopt`, `relocate`, `repair`, `detach`, `reconnect`)
- `old_path` nullable
- `new_path` nullable
- `visibility_after_action` (`incoming`, `mounted`, `hidden-by-policy`)
- `comparison_report_ref` nullable
- `fs_compat_report_ref` nullable
- `preservation_report_ref` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `cancelled`, `blocked`, `reverted`)
- `provenance_ref` nullable

### Preservation set

A reusable summary of the currently available rollback surface for one share or mount.

Fields:

- `preservation_set_id`
- `share_ref`
- `mount_ref` nullable
- `current_binding_path` nullable
- `history_backend` (`local-store`, `replica-derived`, `mixed`, `none`)
- `retention_summary`
- `captures_local_changes` (`yes`, `no`, `peer-only`, `mixed`)
- `max_capture_size` nullable
- `known_plaintext_replicas`
- `known_encrypted_replicas`
- `coverage_confidence` (`high`, `guarded`, `low`)
- `last_verified_at`
- `provenance_ref` nullable

### Preservation report

A structured safety summary for a risky file mutation.

Fields:

- `preservation_report_id`
- `share_id`
- `path`
- `for_action` (`evict`, `remove-local`, `remove-share`, `restore-share`)
- `current_materialization` (`placeholder`, `partial`, `full`, `absent`)
- `local_state_after_action` (`placeholder`, `present`, `absent`)
- `known_plaintext_replicas`
- `known_plaintext_online`
- `known_encrypted_replicas`
- `history_candidates`
- `history_retention_summary` nullable
- `history_gaps[]` (`none-configured`, `ttl-short`, `size-cap`, `remote-only`, `offline-uncertain`)
- `risk_level` (`low`, `guarded`, `high`, `blocked`)
- `blockers[]`
- `recommended_safer_actions[]`
- `generated_at`
- `decision_trace_ref` nullable

### Full-copy witness

A concrete record that one subject currently witnesses durable full bytes for a file or subtree.
This exists so `available on demand` is not forced to stand in for the harder question of who actually still has the bytes.

Fields:

- `full_copy_witness_id`
- `share_ref`
- `path`
- `witness_subject_type` (`device`, `peer`, `mount`, `history-entry`)
- `witness_subject_ref`
- `witness_class` (`local-current`, `remote-confirmed`, `remote-last-known`, `history-backed`, `unknown-derived`)
- `byte_scope` (`file`, `subtree`, `partial-subtree`)
- `online_posture` (`online-now`, `offline-known`, `unknown`)
- `confidence` (`high`, `guarded`, `low`)
- `observed_at`
- `expires_at` nullable
- `provenance_ref` nullable

### Fetchability report

A reviewed answer for one file or subtree describing what is visible, what is local, who still witnesses full bytes, and which actions are honestly admissible.

Fields:

- `fetchability_report_id`
- `share_ref`
- `mount_ref` nullable
- `path`
- `scope_kind` (`file`, `subtree`)
- `requested_action` (`inspect-only`, `fetch`, `evict`, `pin`, `clear-local`, `retire-stale-announcement`)
- `visibility_posture` (`full-visible`, `placeholder-visible`, `names-only`, `announcement-only`, `suppressed-locally`)
- `local_residency_posture` (`full-local`, `partial-local`, `none-local`)
- `witness_summary` (`local-only`, `remote-confirmed`, `multi-source-confirmed`, `offline-only`, `history-backed-only`, `none-known`)
- `fetchability_posture` (`fetchable-now`, `guarded-fetch`, `local-last-copy`, `ghost-risk`, `not-fetchable`)
- `eviction_safety` (`safe`, `guarded`, `unsafe`, `not-applicable`)
- `witness_refs[]`
- `admissible_actions[]`
- `blocked_actions[]`
- `risk_findings[]`
- `recommended_next_step`
- `selection_summary` nullable (`uniform`, `safe-subset-only`, `mixed-risk`, `stale-only`)
- `primary_action_offer` nullable (`fetch-now`, `evict-safe-rows`, `pin-locally`, `create-witness`, `restore-from-history`, `retire-stale-announcement`, `keep-visible-with-warning`)
- `secondary_action_offers[]`
- `generated_at`
- `decision_trace_ref` nullable



### Availability action contract

A compact row-level contract describing which next action is honest for one visible file/subtree row.
This exists so clients do not improvise primary verbs from raw posture fields.

Fields:

- `availability_action_contract_id`
- `report_ref`
- `path`
- `selection_class` (`safe-now`, `re-witness-first`, `history-restore`, `stale-visibility`, `blocked`)
- `danger_class` (`none`, `guarded`, `high`, `stale`)
- `primary_action_offer` (`fetch-now`, `evict-safe-rows`, `pin-locally`, `create-witness`, `restore-from-history`, `retire-stale-announcement`, `keep-visible-with-warning`, `none`)
- `secondary_action_offers[]`
- `review_required`
- `receipt_kind` (`fetchability-receipt`, `file-intent-receipt`, `rollback-receipt`, `none`)
- `presentation_kind` (`inline-direct`, `inline-review`, `drawer-required`, `blocked`)
- `review_route` nullable
- `generated_at`
### Fetchability receipt

A durable record proving which fetchability/witness truth was reviewed when a file or subtree action completed, was blocked, or was retired as stale.

Fields:

- `fetchability_receipt_id`
- `report_ref`
- `share_ref`
- `mount_ref` nullable
- `path`
- `reviewed_visibility_posture`
- `reviewed_witness_summary`
- `reviewed_fetchability_posture`
- `reviewed_selection_summary` nullable
- `offered_primary_action` nullable
- `requested_action`
- `chosen_action`
- `outcome` (`applied`, `blocked`, `cancelled`, `retired-stale`, `deferred`)
- `created_at`
- `provenance_ref` nullable

### File-intent receipt

A durable record for one scope-sensitive file action.

Fields:

- `file_intent_receipt_id`
- `share_ref`
- `mount_ref` nullable
- `path`
- `intent` (`evict-local-bytes`, `remove-local-view`, `delete-from-share`, `restore-local`, `restore-share`, `resolve-deviation`)
- `scope` (`mount-local`, `device-local`, `share`, `share-plan`)
- `history_entry_ref` nullable
- `rollback_receipt_ref` nullable
- `deviation_case_ref` nullable
- `preservation_report_ref` nullable
- `fetchability_receipt_ref` nullable
- `decision_trace_ref` nullable
- `completed_at`
- `outcome` (`applied`, `blocked`, `cancelled`, `reverted`)
- `provenance_ref` nullable

### Route lease

A temporary route or exposure exception that sits on top of durable discovery policy.
This is narrower than the generic maintenance override because it exists specifically for transport/exposure changes such as temporary direct-speed windows.

Fields:

- `route_lease_id`
- `effect` (`allow-public-direct`, `prefer-known-host`, `prefer-overlay`, `suspend-public-discovery`, `drain-route-class`)
- `subject_type` (`system`, `policy`, `share`, `peer`, `peer-share`)
- `subject_id` nullable
- `peer_id` nullable
- `known_host_ref` nullable
- `reason`
- `created_by`
- `created_at`
- `expires_at` nullable
- `byte_cap` nullable
- `transfer_cap` nullable
- `exhaustion_policy` (`expire`, `re-evaluate`, `hold-until-cancelled`)
- `effective_state_ref`
- `provenance_ref` nullable

Notes:

- a direct-speed lease should normally have a TTL and may additionally have a byte cap
- route output should say whether a public-direct candidate is eligible only because of a route lease
- policy reads should distinguish durable baseline from lease-modified effective state

### Override lease

A temporary runtime change that sits **on top of** durable policy without silently rewriting it.

Fields:

- `override_id`
- `family` (`activity`, `route`, `diagnostic-depth`, `access-exposure`, `transfer-budget`, `fidelity-exception`, `implementation-test`)
- `target_type` (`system`, `device`, `share`, `mount`, `peer`, `policy`, `incident`, `endpoint`)
- `target_id` nullable
- `mode` (`pause-transfer`, `drain-egress`, `suspend-ingress`, `throttle`, `maintenance`, `allow-direct-route`, `raise-diagnostic-depth`, `temporary-listener`, `temporary-fidelity-downgrade`)
- `requested_effects[]`
- `effective_effects[]`
- `phase_controls[]` nullable
- `rate_caps` nullable
- `route_class_scope` (`all`, `internet`, `lan`, `overlay`, `clearnet-direct`)
- `schedule_window_ref` nullable
- `baseline_refs[]`
- `domain_refs[]`
- `reason`
- `provenance_kind` (`operator`, `plan-apply`, `incident-response`, `workflow-helper`, `auto-safety`)
- `risk_tier` (`low`, `reviewed`, `high-consequence`)
- `created_by`
- `created_at`
- `starts_at`
- `expires_at` nullable
- `exhaustion_mode` (`time`, `byte-cap`, `first-success`, `manual-only`, `plan-handoff`)
- `exhaustion_budget` nullable
- `status` (`pending`, `active`, `expiring-soon`, `exhausted`, `expired`, `canceled`, `superseded`)
- `renewable`
- `cancelable`
- `no_expiry_ack_ref` nullable
- `revert_behavior` (`restore-baseline`, `restore-next-schedule-window`, `hold-for-review`)
- `effective_state_ref`
- `receipt_refs[]`

### Override receipt

A durable record proving that a temporary exception was created, renewed, reviewed, exhausted, expired, canceled, or converted into durable policy.

Fields:

- `override_receipt_id`
- `override_ref`
- `action` (`create`, `review`, `renew`, `ack-no-expiry`, `exhaust`, `expire`, `cancel`, `convert-to-durable-policy`)
- `before_summary`
- `after_summary`
- `actor_ref`
- `created_at`

### Activity phase state

A first-class read object describing one runtime phase of one subject after baseline policy, overrides, and recurring windows are combined.

Fields:

- `activity_phase_state_id`
- `subject_type` (`system`, `device`, `share`, `mount`, `policy`)
- `subject_id` nullable
- `phase` (`scan-index`, `ingress-bytes`, `egress-bytes`, `delete-propagation`, `announce-discovery`, `dial-attempts`)
- `effective_mode` (`active`, `throttled`, `suspended`, `draining`, `degraded`, `blocked-pending-review`)
- `rate_caps` nullable
- `route_class_scope` (`all`, `internet`, `lan`, `overlay`, `clearnet-direct`)
- `baseline_ref` nullable
- `active_override_refs[]`
- `active_schedule_refs[]`
- `current_answer`
- `generated_at`

### Schedule window

A recurring time-bounded policy object that activates explicit phase controls without silently rewriting durable baseline policy.

Fields:

- `schedule_window_id`
- `target_type` (`system`, `device`, `share`, `mount`, `policy`)
- `target_id` nullable
- `preset` (`transfer-quiesce`, `egress-drain`, `metered-link`, `maintenance-freeze`, `custom`)
- `phase_controls[]`
- `route_class_scope` (`all`, `internet`, `lan`, `overlay`, `clearnet-direct`)
- `timezone`
- `recurrence_rule`
- `enabled`
- `created_by`
- `created_at`
- `next_activation_at` nullable
- `last_activation_at` nullable
- `provenance_ref` nullable

### Retirement record

A first-class record describing how a device or identity is being exited from the mesh.
This exists so cosmetic cleanup, ignored contact, trust revocation, successor replacement, and identity rotation are not conflated.

Fields:

- `retirement_id`
- `subject_type` (`device`, `identity`)
- `subject_id`
- `intent` (`hide`, `ignore`, `revoke`, `replace`, `rotate-identity`)
- `status` (`planned`, `active`, `completed`, `canceled`)
- `replacement_device_id` nullable
- `grant_action` (`none`, `freeze`, `revoke`, `rebind-to-successor`)
- `approval_action` (`none`, `freeze`, `revoke`)
- `publication_action` (`none`, `stop-announcing`, `clear-route-cache`)
- `recovery_bundle_id` nullable
- `created_by`
- `created_at`
- `completed_at` nullable
- `provenance_ref` nullable

### Transfer

A data movement operation tracked by the daemon.

Fields:

- `transfer_id`
- `share_id`
- `path`
- `direction`
- `source_device`
- `destination_device`
- `lane` (`interactive`, `normal`, `background`, `bulk`, `maintenance`)
- `priority`
- `selected_route_class` (`lan-direct`, `known-host-direct`, `overlay`, `public-direct`, `relay`)
- `selected_transport_kind`
- `policy_ref` nullable
- `budget_refs[]`
- `queue_state` (`running`, `queued`, `delayed`, `suspended`, `blocked`, `source-unavailable`, `completed`)
- `queue_position` nullable
- `bytes_done`
- `bytes_total`
- `state`
- `bottleneck_kind` nullable
- `explanation_ref` nullable
- `current_answer`

### Transfer policy

A durable ordering and preference policy for a transfer scope.
This exists so route preference, queue lane, fairness, and delay profile are public operator state instead of advanced-setting lore.

Fields:

- `transfer_policy_id`
- `scope_ref`
- `default_lane`
- `priority_policy`
- `preferred_route_classes[]`
- `discouraged_route_classes[]`
- `fairness_mode`
- `interactive_reserve` nullable
- `delay_profile_ref` nullable
- `relay_cost_posture` (`allowed`, `discourage`, `budgeted`, `blocked`)
- `disk_backpressure_posture`
- `created_by`
- `created_at`
- `status` (`active`, `shadowed`, `superseded`)

### Throughput budget

A public cap or reserve object for transfer throughput.
This exists so a metered link, hotspot window, or relay-cost ceiling is inspectable policy rather than an inferred side effect.

Fields:

- `throughput_budget_id`
- `scope_ref`
- `route_scope`
- `ingress_limit`
- `egress_limit`
- `burst_limit` nullable
- `concurrency_limit` nullable
- `relay_byte_budget` nullable
- `relay_time_budget` nullable
- `lan_exempt` boolean
- `effective_window` (`durable`, `lease`, `schedule-window`, `manual-override`)
- `origin_ref`
- `expires_at` nullable
- `status` (`active`, `scheduled`, `expired`, `superseded`)

### Transfer budget receipt

A durable record proving that effective throughput posture changed.
This exists so temporary caps and exemptions do not disappear into scheduler or preferences folklore.

Fields:

- `transfer_budget_receipt_id`
- `subject_ref`
- `budget_ref`
- `change_kind`
- `effective_route_scope`
- `effective_limits`
- `reason`
- `captured_at`

### Backup set

A portable, inspectable state bundle.

Fields:

- `backup_id`
- `created_at`
- `contains_identity`
- `contains_share_metadata`
- `contains_cached_endpoints`
- `encrypted`
- `format_version`

### Recovery bundle

A supported export of recovery prerequisites for one workflow such as encrypted offline decrypt, device replacement, or grant reconciliation.
This exists so operators do not have to rediscover hidden keys, database names, or log details under stress.

Fields:

- `recovery_bundle_id`
- `bundle_type` (`encrypted-offline-decrypt`, `device-replacement`, `grant-reconciliation`, `identity-rotation`, `state-root-rebind`)
- `subject_ref`
- `share_id` nullable
- `created_at`
- `custody_class` (`portable-secret`, `portable-metadata-only`, `daemon-bound-proof`, `split-secret-plus-metadata`)
- `contains_keys`
- `contains_wrapped_secrets`
- `contains_metadata`
- `contains_continuity_manifest`
- `db_dependency` (`none`, `optional`, `required`)
- `continuity_claims[]`
- `invalidated_at` nullable
- `superseded_by` nullable
- `sufficiency_status` (`unknown`, `sufficient`, `partial`, `insufficient`)
- `verification_findings[]`
- `encrypted`
- `format_version`

### Recovery receipt

A durable record proving that recovery posture changed, a bundle was verified or consumed, or continuity was explicitly narrowed.

Fields:

- `recovery_receipt_id`
- `action` (`export-bundle`, `verify-bundle`, `invalidate-bundle`, `consume-bundle`, `replace-device`, `rotate-identity`, `revoke-device`, `import-recovered-bytes`)
- `bundle_ref` nullable
- `subject_refs[]`
- `workflow_scope[]`
- `continuity_delta`
- `dependency_findings[]`
- `created_at`


### Release posture

A first-class summary of current release truth for one subject such as the daemon, a bundled transport runtime, or a peer constellation.
This exists so “update available”, “mixed-version”, and “safe to cut over” do not collapse into one ambiguous status hint.

Fields:

- `release_posture_id`
- `subject_ref`
- `subject_kind` (`daemon`, `transport-bundle`, `workbench-client`, `peer-constellation`)
- `installed_version`
- `edition_family`
- `release_channel` (`stable`, `candidate`, `nightly`, `pinned`, `vendor-packaged`, `local-build`)
- `schema_epoch`
- `api_epoch`
- `compatibility_family`
- `update_state` (`current`, `update-available`, `security-update-available`, `pinned-outdated`, `mixed-family`, `migration-blocked`, `unknown`)
- `downgrade_posture` (`safe-window`, `config-risk`, `schema-risk`, `unsupported`, `unknown`)
- `peer_skew_summary`
- `linked_constellation_state` (`uniform`, `mixed-version`, `mixed-edition`, `mixed-channel`, `unknown`)
- `last_checked_at` nullable
- `next_review_at` nullable

### Upgrade plan

A reviewed proposal to move one or more subjects across a release boundary.

Fields:

- `upgrade_plan_id`
- `subject_refs[]`
- `current_release_refs[]`
- `target_release`
- `channel_change` nullable
- `edition_change` nullable
- `required_cutover_scope[]` (`restart-only`, `drain-and-restart`, `plan-bearing-share-reopen`, `state-root-verify`, `manual-repair-followup`)
- `compatibility_findings[]`
- `schema_change_state` (`none`, `forward-only`, `reversible-window`, `unknown`)
- `rollback_posture`
- `blocked_by[]`
- `warnings[]`
- `preconditions[]`
- `expires_at` nullable

### Release receipt

A durable record proving that release posture changed, an upgrade plan was applied, or a compatibility boundary was explicitly accepted.

Fields:

- `release_receipt_id`
- `action` (`check-release`, `adopt-channel`, `apply-upgrade`, `complete-cutover`, `record-rollback`, `accept-compatibility-boundary`)
- `subject_refs[]`
- `from_release`
- `to_release`
- `channel_delta`
- `schema_delta`
- `compatibility_delta`
- `accepted_warnings[]`
- `created_at`


### Defaults profile

A named baseline bundle of policy defaults that can be attached to a link group, device class, share class, incoming class, or similar scope.
This exists so convenience presets stay explicit instead of becoming scattered hidden defaults.

Fields:

- `defaults_profile_id`
- `name`
- `scope_kind` (`link-group`, `device-class`, `share-class`, `incoming-class`, `operator-profile`, `global`)
- `domains[]`
- `default_values{}`
- `created_by`
- `created_at`
- `mutable` (`built-in`, `operator`, `imported`)
- `inherits_from[]`
- `notes` nullable

### Policy binding

A durable statement that one subject or scope follows one policy/default source for one domain.
This exists so inheritance can be inspected instead of inferred.

Fields:

- `policy_binding_id`
- `subject_ref`
- `subject_kind`
- `domain`
- `binding_mode` (`inherit`, `pinned-policy`, `pinned-value`, `profile-derived`, `imported`, `override-derived`, `schedule-derived`)
- `source_ref` nullable
- `field_mask[]` nullable
- `applies_to_future_subjects`
- `created_at`
- `updated_at`
- `created_by`

### Effective policy explanation

A read object describing resolved policy for one subject and one domain, including per-field origin.
This exists so the operator can answer `why this value?` without leaving the main surface.

Fields:

- `effective_policy_id`
- `subject_ref`
- `domain`
- `resolved_values{}`
- `field_origins[]`
- `surface_gaps[]`
- `warnings[]`
- `computed_at`

### Policy receipt

A durable record proving that default/inheritance/precedence state changed or was explicitly reviewed.

Fields:

- `policy_receipt_id`
- `action` (`create-defaults-profile`, `bind-policy`, `pin-field`, `return-to-inheritance`, `apply-defaults-change`, `accept-surface-gap`, `record-imported-policy`)
- `subject_refs[]`
- `domain`
- `changed_fields[]`
- `before_summary`
- `after_summary`
- `applied_scope` (`future-only`, `eligible-existing`, `selected-subjects`)
- `created_at`

### Diagnostic incident

A durable troubleshooting object for one problem statement or investigation window.
This exists so evidence collection is attached to an explicit incident instead of becoming a pile of files near the daemon.

Fields:

- `diagnostic_incident_id`
- `subject_refs[]`
- `headline`
- `reason_code`
- `incident_kind` (`connectivity`, `transfer-slow`, `path-binding`, `projection`, `storage-pressure`, `conflict`, `crash`, `performance`, `unknown`)
- `opened_from` (`report`, `workbench`, `cli`, `api`, `auto-health-trigger`)
- `diagnostic_depth` (`baseline`, `elevated`, `trace`, `forensics`)
- `requested_evidence_classes[]`
- `redaction_profile_ref`
- `retention_policy`
- `status` (`open`, `collecting`, `awaiting-redaction-review`, `sealed`, `expired`, `closed`)
- `opened_at`
- `last_collected_at` nullable
- `closed_at` nullable

### Evidence bundle

A reviewed, inspectable collection of incident-linked diagnostic material.
This exists so operators can answer what the bundle contains before anything is exported or destroyed.

Fields:

- `evidence_bundle_id`
- `incident_ref`
- `collection_scope`
- `diagnostic_depth`
- `included_classes[]`
- `excluded_classes[]`
- `redaction_profile_ref`
- `redaction_findings[]`
- `contains_sensitive_paths`
- `contains_peer_identifiers`
- `contains_secret_material` boolean
- `secret_handling` (`none-present`, `auto-redacted`, `manually-redacted`, `blocked-unsealed`)
- `event_window`
- `size_bytes`
- `retention_until` nullable
- `seal_state` (`staged`, `reviewed`, `sealed`, `exported`, `destroyed`)
- `export_targets[]`
- `created_at`

### Redaction profile

A named rule set describing how evidence is trimmed, tokenized, or blocked before sealing/export.

Fields:

- `redaction_profile_id`
- `name`
- `path_policy` (`full`, `basename-only`, `tokenized`, `blocked`)
- `peer_identity_policy` (`full`, `stable-token`, `role-only`, `blocked`)
- `address_policy` (`full`, `subnet-only`, `tokenized`, `blocked`)
- `secret_policy` (`block`, `auto-redact`, `manual-review-required`)
- `config_policy` (`summary-only`, `diff-safe`, `full-redacted`)
- `retention_default`
- `mutable` (`built-in`, `operator`, `incident-local`)
- `created_at`

### Evidence receipt

A durable record proving that diagnostic depth changed, a bundle was collected, redaction was reviewed, or evidence was sealed/exported/destroyed.

Fields:

- `evidence_receipt_id`
- `incident_ref`
- `bundle_ref` nullable
- `action` (`open-incident`, `raise-depth`, `lower-depth`, `collect-bundle`, `review-redaction`, `seal-bundle`, `export-bundle`, `destroy-staging`, `close-incident`)
- `before_summary`
- `after_summary`
- `actor_ref`
- `created_at`


### State root

A durable local control universe.
This exists so storage path, inventory, identity continuity, and service-profile binding are explicit operator state rather than startup trivia.

Fields:

- `state_root_id`
- `path`
- `status` (`active`, `attached`, `detached`, `maintenance`, `stale`, `superseded`)
- `identity_root_ref`
- `service_profile_ref`
- `share_count`
- `mount_count`
- `contact_count`
- `integrity_state` (`verified`, `needs-scan`, `drifted`, `partial`, `unknown`)
- `last_verified_at` nullable
- `provenance_ref` nullable

### Service profile

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

### Bring-up case

A reviewed first-open case for local control.
This exists so fresh initialization, attach/reopen, recover/import, successor-sensitive continuity, and first control exposure do not hide behind startup ritual.

Fields:

- `bringup_case_id`
- `host_role` (`workstation`, `background-service`, `local-web-appliance`, `recovery-bench`, `inspect-only`)
- `runtime_target_ref`
- `continuity_mode` (`new-state`, `attach-known-root`, `import-state`, `recover-bundle`, `successor-sensitive`, `inspect-without-open`)
- `candidate_state_root_ref` nullable
- `candidate_artifact_ref` nullable
- `identity_posture` (`new`, `retained`, `imported`, `successor-bound`, `inspect-only`)
- `control_posture` (`local-socket-only`, `loopback-workbench`, `ssh-forwarded`, `lan-reviewed`, `reverse-proxied`)
- `discovery_baseline_ref` nullable
- `blocker_refs[]`
- `risk_state` (`low-risk`, `reviewed`, `blocked`)
- `bringup_report_ref`
- `receipt_promise`
- `generated_at`
- `expires_at` nullable

### State snapshot

A compact attestation of one state root at a moment in time.
This exists so move/attach/export/profile-switch work can leave behind a before/after receipt.

Fields:

- `state_snapshot_id`
- `state_root_ref`
- `captured_at`
- `identity_fingerprint`
- `share_count`
- `mount_count`
- `contact_count`
- `service_profile_ref`
- `integrity_summary`
- `recovery_posture_summary`
- `drift_flags[]`

### State transition plan

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

### Subject alias record

A durable mapping between mutable labels, stable subject handles, and known authority continuity.
This exists so typo repair, peer-visible rename, alias history, and same-person continuity do not collapse into one hidden identity ritual.

Fields:

- `subject_alias_record_id`
- `subject_ref`
- `authority_identity_ref` nullable
- `current_label`
- `previous_labels[]`
- `peer_visible_label` nullable
- `label_scope` (`local-only`, `peer-visible`, `constellation-wide`, `mixed`)
- `continuity_class` (`same-authority`, `same-person-new-authority`, `authority-uncertain`, `authority-replaced`)
- `last_changed_at`
- `provenance_ref` nullable

### Identity-continuity review

A durable, reviewed case for relabeling a subject or comparing a new authority claim without guessing whether the same person story still preserves the same trusted subject.

Fields:

- `identity_continuity_review_id`
- `subject_ref`
- `requested_action` (`relabel-only`, `peer-visible-relabel`, `alias-add`, `same-person-new-authority`, `authority-replacement`, `inspect-only`)
- `current_authority_identity_ref` nullable
- `candidate_authority_identity_ref` nullable
- `continuity_expectation` (`same-authority`, `same-person-new-authority`, `authority-uncertain`, `authority-replacement`)
- `label_findings[]`
- `authority_findings[]`
- `grant_and_constellation_fallout[]`
- `action_options[]`
- `identity_continuity_report_ref`
- `generated_at`
- `expires_at` nullable

### Identity-label receipt

A durable record proving what label changed, what authority continuity was preserved or replaced, and what wider constellation or grant fallout was accepted.

Fields:

- `identity_label_receipt_id`
- `review_ref`
- `subject_ref`
- `authority_continuity_summary`
- `label_change_summary`
- `grant_scope_summary`
- `constellation_scope_summary`
- `actor_ref`
- `created_at`

### Plan

A durable preview of an intended mutation.

Fields:

- `plan_id`
- `action_type`
- `created_at`
- `created_by`
- `target_objects[]`
- `preconditions[]`
- `effects[]`
- `risk_flags[]`
- `provenance_ref`
- `expires_at` nullable

### Replica state

Per device, per share:

- `absent`
- `metadata-only`
- `partial`
- `complete`
- `encrypted-only`

### Review item

A derived queue card that points back to real objects requiring attention.
This exists so the operator can work from one high-signal attention surface without collapsing the underlying model.

Fields:

- `review_item_id`
- `lane` (`now`, `soon`, `quiet`)
- `reason_code`
- `headline`
- `subject_refs[]`
- `derived_from[]`
- `primary_action`
- `recommended_actions[]`
- `proof_refs[]`
- `worsens_at` nullable
- `dismiss_behavior` (`presentation-only`, `requires-subject-resolution`)
- `provenance_ref` nullable

### Attention policy

A durable rule set mapping report-backed conditions into workbench lanes, delivery channels, deduplication, and quiet-hour behavior.

Fields:

- `attention_policy_id`
- `scope` (`device`, `profile`, `user`, `subject-class`)
- `default_lane_map`
- `channel_rules[]`
- `quiet_hours` nullable
- `dedupe_window`
- `delivery_fallback_order[]`
- `headless_policy` (`workbench-only`, `webhook-first`, `local-log-plus-workbench`, `custom`)
- `created_at`
- `updated_at`

### Attention event

A durable attention object derived from one or more reports or review items.
This exists so urgency, channel delivery, and operator acknowledgement are inspectable state rather than a best-effort side effect.

Fields:

- `attention_event_id`
- `subject_refs[]`
- `report_refs[]`
- `review_item_ref` nullable
- `lane` (`now`, `soon`, `quiet`)
- `reason_code`
- `severity`
- `freshness_state`
- `headline`
- `delivery_targets[]`
- `delivery_outcomes[]`
- `operator_disposition` (`new`, `seen`, `acknowledged`, `snoozed`, `muted`, `resolved`)
- `first_observed_at`
- `last_reasserted_at`
- `worsens_at` nullable
- `expires_at` nullable

### Attention receipt

A durable record that an operator or policy changed how an attention event is presented or routed.

Fields:

- `attention_receipt_id`
- `attention_event_ref`
- `action` (`ack`, `snooze`, `unsnooze`, `mute-scope`, `delivery-test`, `delivery-failure-recorded`)
- `presentation_only` boolean
- `effective_until` nullable
- `channel_scope[]`
- `actor_ref`
- `created_at`

---

### Exit plan

A durable preview describing what a removal-style action would actually do across authority, visibility, byte-state, continuity, and residue.

Fields:

- `exit_plan_id`
- `subject_ref`
- `intent_class` (`hide`, `detach-local`, `ignore-future`, `revoke-authority`, `replace-with-successor`, `decommission`, `erase-local-residue`, `retire-share-presence`)
- `authority_effects[]`
- `visibility_effects[]`
- `byte_state_effects[]`
- `continuity_effects[]`
- `residue_findings[]`
- `requires_followup[]`
- `generated_at`
- `expires_at` nullable
- `decision_trace_ref` nullable

### Exit residue finding

A durable finding about what still remains after an exit action.

Fields:

- `exit_residue_id`
- `subject_ref`
- `residue_class` (`offline-peer-memory`, `remote-share-copy`, `cached-publication`, `local-history`, `recovery-material`, `waiting-for-peer-observation`, `intentionally-preserved-bytes`)
- `location_class` (`local`, `remote-peer`, `provider-cache`, `constellation-member`, `unknown-offline-peer`)
- `clearability` (`none`, `time-bound`, `operator-clearable`, `requires-peer-observation`, `rotate-required`)
- `evidence_summary`
- `ack_required` boolean
- `last_verified_at`

### Exit receipt

A durable record proving what kind of exit was actually applied and what remained afterward.

Fields:

- `exit_receipt_id`
- `subject_ref`
- `intent_class`
- `before_summary`
- `after_summary`
- `continuity_summary`
- `residue_summary`
- `applied_plan_ref` nullable
- `actor_ref`
- `created_at`



### Compromise case

A durable, reviewed incident object for suspected or confirmed compromise, leaked authority, stolen hardware, or unexpected identity reappearance.

Fields:

- `compromise_case_id`
- `trigger_refs[]`
- `subject_refs[]`
- `incident_posture` (`suspected`, `probable`, `confirmed`, `historical`)
- `freeze_effects[]`
- `revocation_effects[]`
- `rotation_effects[]`
- `continuity_options[]`
- `residue_findings[]`
- `generated_at`
- `expires_at` nullable
- `decision_trace_ref` nullable

### Compromise receipt

A durable record proving what immediate containment, revocation, rotation, continuity handling, and residue posture actually resulted from a compromise case.

Fields:

- `compromise_receipt_id`
- `case_ref`
- `subject_refs[]`
- `freeze_summary`
- `revocation_summary`
- `rotation_summary`
- `continuity_summary`
- `residue_summary`
- `actor_ref`
- `created_at`

### Re-entry case

A durable, reviewed case for a long-offline, chronology-uncertain, or otherwise stale-returning subject whose resumed authority cannot safely be treated as ambient “online again” state.

Fields:

- `reentry_case_id`
- `subject_ref`
- `related_share_refs[]`
- `dormancy_summary`
- `chronology_confidence` (`high`, `guarded`, `low`, `blocked`)
- `proposed_posture` (`resume-writer`, `resume-reader`, `quarantine`, `successor-only`, `blocked`)
- `divergence_findings[]`
- `availability_findings[]`
- `action_options[]`
- `generated_at`
- `expires_at` nullable
- `decision_trace_ref` nullable

### Re-entry receipt

A durable record proving what a reviewed stale-return decision actually allowed, blocked, quarantined, or escalated.

Fields:

- `reentry_receipt_id`
- `case_ref`
- `subject_ref`
- `dormancy_summary`
- `chronology_summary`
- `authority_summary`
- `divergence_summary`
- `outcome_summary`
- `actor_ref`
- `created_at`

### Destructive-replay case

A durable, reviewed case for high-signal remote delete, overwrite, or revert waves whose destructive effect should not be treated as ambient sync progress.

Fields:

- `destructive_replay_case_id`
- `share_ref`
- `trigger_kind` (`remote-delete-wave`, `remote-overwrite-wave`, `receive-only-revert`, `protected-scope-hit`, `archive-weak-replay`, `unknown`)
- `trigger_refs[]`
- `scope_summary`
- `effect_findings[]`
- `preservation_findings[]`
- `source_confidence` (`high`, `guarded`, `low`, `blocked`)
- `action_options[]`
- `generated_at`
- `expires_at` nullable
- `decision_trace_ref` nullable

### Destructive-replay receipt

A durable record proving what destructive propagation scope was accepted, frozen, narrowed, or diverted after review.

Fields:

- `destructive_replay_receipt_id`
- `case_ref`
- `share_ref`
- `scope_summary`
- `effect_summary`
- `preservation_summary`
- `authority_summary`
- `outcome_summary`
- `actor_ref`
- `created_at`

## Top-level groups

```text
anonsync init
anonsync daemon ...
anonsync device ...
anonsync constellation ...
anonsync contact ...
anonsync pending ...
anonsync review ...
anonsync attention ...
anonsync link ...
anonsync share ...
anonsync grant ...
anonsync incoming ...
anonsync ignore ...
anonsync layout ...
anonsync conflict ...
anonsync role ...
anonsync deviation ...
anonsync stewardship ...
anonsync preflight ...
anonsync mount ...
anonsync file ...
anonsync invite ...
anonsync claim ...
anonsync approval ...
anonsync policy ...
anonsync activity ...
anonsync schedule ...
anonsync space ...
anonsync override ...
anonsync route ...
anonsync explain ...
anonsync transfer ...
anonsync history ...
anonsync reentry ...
anonsync destructive ...
anonsync events ...
anonsync status ...
anonsync doctor ...
anonsync audit ...
anonsync plan ...
anonsync backup ...
anonsync recover ...
```

Rules:

- every mutable command supports `--yes` for non-interactive use
- every read command supports `--json`
- long-running commands support `--watch` or `--follow`
- destructive or global commands require an explicit flag rather than positional ambiguity
- every failed command should emit a short machine-readable error code in `--json` mode
- commands that can affect local bytes only vs replicated share state must require an explicit scope flag when the distinction matters
- read surfaces should report both durable policy and active override leases when temporary state changes the effective behavior

---

## Core commands

### `anonsync init`

Create local device identity and daemon state for the low-risk case: fresh local state with a clearly local control boundary.

```text
anonsync init --name laptop-ember
anonsync init --name archive-box --storage /srv/anonsync
anonsync init --name studio-nas --listen 127.0.0.1:4747
```

Output includes:

- device ID
- config path
- storage path
- local control socket path
- active discovery policy

Semantics:

- `init` is intentionally the compressed path for obviously fresh, local-only bring-up
- if the daemon detects ambiguous prior state, continuity-sensitive recovery/import, or reviewed remote-reachable control exposure, it should emit a bring-up case instead of silently continuing
- LAN-, proxy-, or continuity-sensitive first-open work should not masquerade as ordinary `init`


### `anonsync bringup`

Review and apply non-trivial first-open decisions.

```text
anonsync bringup review --host-role workstation --state new --name laptop-ember
anonsync bringup review --host-role background-service --attach /srv/anonsync/root --control loopback-workbench
anonsync bringup review --recover ./mesh.asb --host-role recovery-bench --plan
anonsync bringup review --attach /srv/anonsync/root --control lan-reviewed --listen 10.0.0.8:4747 --plan
anonsync bringup show brc_01J... --view review
anonsync bringup apply brc_01J...
```

Semantics:

- bring-up review exists so fresh start, attach existing state, recover/import state, successor-sensitive continuity, and first control exposure render through one public grammar
- review output should always answer: host role, state/continuity choice, identity posture, control/network posture, blockers/dependencies, and receipt promise
- `bringup apply` should emit a bring-up receipt that later proves which root or artifact was opened, under what identity posture, and with what initial control exposure
- low-risk local-only startup may compress back into `init`, but Linux/WebUI/headless paths may not silently hide continuity or exposure meaning behind startup flags or config files

### `anonsync daemon`

Manage the local daemon.

```text
anonsync daemon start
anonsync daemon stop
anonsync daemon restart
anonsync daemon status
anonsync daemon logs --follow
anonsync daemon capabilities
```

### `anonsync device`

#### Add known peer

```text
anonsync device add --name studio-nas --addr 10.0.0.8:4747
anonsync device add --invite ./peer.invite
```

#### Inspect and list

```text
anonsync device list
anonsync device show dev_01J...
anonsync device show dev_01J... --show-provenance
```

#### Modify trust posture

```text
anonsync device set dev_01J... --trust-class untrusted
anonsync device set dev_01J... --addr vpn.example.net:4747
anonsync device set dev_01J... --tag laptop
```

#### Retire / ignore / replace

```text
anonsync device retire dev_01J... --intent hide
anonsync device retire dev_01J... --intent revoke --plan --reason "stolen laptop"
anonsync device ignore dev_01J... --reason "unsolicited old identity"
anonsync device replace dev_old --successor dev_new --plan
anonsync device retirement show rtr_01J...
```

Important rules:

- adding or linking a device never replaces the current device identity
- conflicting identity data returns an explicit remediation error
- untrusted devices cannot receive plaintext for shares whose policy forbids it
- device add/link flows should expose compatibility warnings before commitment when version-family or capability mismatches are known
- retirement intent must be explicit: `hide`, `ignore`, `revoke`, and `replace` are distinct and must not be guessed from one overloaded remove action
- successor replacement should reference the reviewed continuity consequences for grants, approval memory, and recovery posture


### `anonsync constellation`

Inspect and change personal-constellation posture without pretending that convenience membership is the same thing as owner merge.

```text
anonsync constellation list
anonsync constellation show cst_01J...
anonsync constellation members cst_01J...
anonsync constellation member show mem_01J...
anonsync constellation authority show --share finance
anonsync constellation member class set mem_01J... --to appliance --plan
anonsync constellation visibility-default set mem_01J... --to incoming-only --plan
anonsync constellation receipt show csr_01J...
```

This group should answer:

- which members belong to the convenience-linked set
- what class and default visibility each member has
- whether a member can mutate, re-share, approve, or only review/adopt
- whether a pending action is local-only, member-wide, share-wide, or constellation-wide
- which receipt proves the latest membership or authority-boundary change

### `anonsync contact`

Review and manage relationship memory without silently granting or linking anything.

```text
anonsync contact list
anonsync contact show ctc_01J...
anonsync contact trust ctc_01J... --class collaborator
anonsync contact quarantine ctc_01J... --reason "unexpected fingerprint drift"
anonsync contact ignore ctc_01J... --reason "unsolicited peer"
anonsync contact set ctc_01J... --future-introductions share-scoped
```

Semantics:

- a contact record may exist before any share grant exists
- contact trust is not itself a share grant or mount adoption
- ignored and quarantined states must be visible and auditable
- successor continuity policy belongs here, not in hidden replacement folklore

### `anonsync pending`

Review unknown or newly introduced peers before they become ordinary trust state.

```text
anonsync pending peer list
anonsync pending peer show ppd_01J...
anonsync pending peer accept ppd_01J... --as-contact alex --plan
anonsync pending peer dismiss ppd_01J... --reason "not now"
anonsync pending peer ignore ppd_01J... --reason "unsolicited contact"
```

Semantics:

- pending peers are a first-class queue, not log archaeology
- accept may create a contact, a device record, or a claim plan, but must say which
- dismiss is temporary review state; ignore is durable future suppression
- linked-device introduction may surface a pending peer, but not silently create ambient trust

### `anonsync review`

Inspect or manage the derived attention queue without hiding the underlying object model.

```text
anonsync review list
anonsync review list --lane now
anonsync review home
anonsync review home --lane now
anonsync review show riv_01J...
anonsync review snooze riv_01J... --for 4h
anonsync review dismiss riv_01J...
anonsync review open riv_01J...
```

Semantics:

- review items summarize real objects such as pending peers, incoming shares, degraded transports, conflicts, stale plans, or successor reviews
- `review home` should return a workbench-style grouped projection with `now`, `soon`, and `quiet` lanes while still exposing underlying subject refs
- `review open` should jump to the underlying subject summary rather than mutate it
- dismissing or snoozing a review item should never silently approve, reject, revoke, or delete the underlying object
- the queue should clearly distinguish presentation-only dismissal from true resolution of the subject state


### Control access policy

A first-class policy describing how the daemon may be administered.

Fields:

- `control_access_policy_id`
- `primary_local_transport`
- `loopback_http`
- `allowed_exposure_classes[]`
- `authn_classes[]`
- `default_token_ttls`
- `default_session_ttls`
- `hostcheck_policy`
- `trusted_proxy_refs[]`
- `browser_session_policy`
- `created_at`
- `updated_at`

### Control endpoint

A first-class record describing one reachable control-plane endpoint.

Fields:

- `control_endpoint_id`
- `transport`
- `bind`
- `exposure_class`
- `authn_class`
- `tls_posture`
- `hostcheck_policy`
- `proxy_ref` nullable
- `state_root_ref`
- `risk_state`
- `active_session_count`
- `last_verified_at`

### Access token

A durable credential object for automation or interactive clients.

Fields:

- `access_token_id`
- `audience`
- `scope`
- `issuance_mode`
- `expires_at`
- `idle_timeout` nullable
- `last_used_at` nullable
- `revoked_at` nullable
- `bound_endpoint_refs[]`
- `actor_ref`
- `created_at`

### Control session

A first-class record describing one active or recent authenticated control session.

Fields:

- `control_session_id`
- `endpoint_ref`
- `token_ref` nullable
- `client_kind`
- `scope`
- `origin_summary`
- `proxy_chain[]`
- `issued_at`
- `last_seen_at`
- `expires_at`
- `revoked_at` nullable
- `csrf_or_hostcheck_state`
- `state_root_ref`

### Access receipt

A durable record that access posture changed.

Fields:

- `access_receipt_id`
- `action`
- `subject_ref`
- `actor_ref`
- `report_refs[]`
- `effective_delta`
- `created_at`

### Control capability manifest

A first-class record describing what one control action is, which channels may render it honestly, and why it may currently be unavailable.

Fields:

- `control_capability_id`
- `action`
- `subject_scope`
- `required_scope`
- `supported_channels[]`
- `currently_available_channels[]`
- `degraded_channels[]`
- `review_family`
- `semantic_parity_policy` (`must-match`, `inspect-only-allowed`)
- `denial_or_degradation_reason_refs[]`
- `fallback_channel_order[]`
- `last_evaluated_at`

### Control integrity report

A first-class report describing why browser-mediated control is degraded, distrusted, or incomplete.

Fields:

- `control_integrity_report_id`
- `class`
- `subject_ref`
- `affected_channel_refs[]`
- `affected_capability_refs[]`
- `operator_visible_effect`
- `safe_fallback_refs[]`
- `requires_repair_case`
- `severity`
- `freshness_state`
- `created_at`
- `updated_at`

### Auth repair case

A first-class case describing how control credentials, trust bootstrap, or browser/session authority will be repaired.

Fields:

- `auth_repair_case_id`
- `kind`
- `target_endpoint_ref`
- `target_session_or_token_ref` nullable
- `state_root_ref`
- `requested_effect`
- `collateral_delta_expected`
- `blocking_report_refs[]`
- `available_apply_channels[]`
- `receipt_promise`
- `created_at`
- `updated_at`

### Review handoff

A first-class object describing a safe cross-channel continuation of one reviewed action.

Fields:

- `review_handoff_id`
- `action`
- `subject_ref`
- `review_family`
- `source_channel`
- `target_channel`
- `capability_ref`
- `integrity_report_refs[]`
- `mutation_gate_ref` nullable
- `preserved_section_order[]`
- `requires_fresh_review`
- `expires_at`
- `consumed_at` nullable
- `created_at`

### Handoff receipt

A first-class receipt proving that one reviewed action was continued, refused, or reopened across channels without silently changing semantics.

Fields:

- `handoff_receipt_id`
- `review_handoff_ref`
- `result` (`continued`, `reopened-review`, `expired`, `refused`, `consumed-with-apply`)
- `source_channel`
- `target_channel`
- `preserved_subject_ref`
- `preserved_review_family`
- `gate_continuity_state`
- `created_at`

### Mutation gate result

A first-class gate evaluation describing what authority is currently required for one attempted mutation.

Fields:

- `mutation_gate_result_id`
- `action`
- `subject_ref`
- `current_session_ref` nullable
- `current_token_ref` nullable
- `required_authority`
- `gate_state`
- `acceptable_scope_summary`
- `blocking_reason_refs[]`
- `safe_next_actions[]`
- `evaluated_at`

### Mutation grant

A first-class short-lived authority object for reviewed interactive mutation.

Fields:

- `mutation_grant_id`
- `action_family`
- `subject_scope`
- `issuer_session_ref` nullable
- `issuer_token_ref` nullable
- `approved_channels[]`
- `approved_endpoint_refs[]`
- `state_root_ref`
- `user_presence_class`
- `batch_budget`
- `issued_at`
- `expires_at`
- `consumed_at` nullable
- `revoked_at` nullable
- `receipt_promise`

### Target custody record

A first-class object describing the currently known ownership and lineage posture of one local target.

Fields:

- `target_custody_record_id`
- `path`
- `storage_tier`
- `marker_state`
- `current_owner_subject_ref` nullable
- `current_owner_state_root_ref` nullable
- `current_owner_service_profile_ref` nullable
- `lineage_confidence`
- `collision_state`
- `preservation_requirement`
- `last_verified_at`

### Binding collision case

A first-class reviewed case describing why one requested path claim is guarded or blocked.

Fields:

- `binding_collision_case_id`
- `target_path`
- `requested_intent`
- `related_subject_refs[]`
- `related_state_root_refs[]`
- `risk_class`
- `safe_actions[]`
- `required_preservation_refs[]`
- `created_at`
- `updated_at`

### Custody receipt

A first-class receipt proving how target ownership or marker cleanup was reviewed and applied.

Fields:

- `custody_receipt_id`
- `target_path`
- `pre_state_summary`
- `applied_action`
- `post_state_summary`
- `lineage_claim`
- `evidence_preserved`
- `operator_acknowledgements[]`
- `recorded_at`

### `anonsync custody`

Inspect path ownership, discovered markers, and reviewed local target claims without reducing same-host safety to non-empty-path prompts or hidden-marker cleanup ritual.

```text
anonsync custody list
anonsync custody inspect --path /mnt/archive
anonsync custody inspect --path /srv/media --json
anonsync custody review --path /mnt/archive --intent attach
anonsync custody review --path /mnt/archive --intent successor-claim --plan
anonsync custody show bcc_01J...
anonsync custody receipt show cur_01J...
anonsync custody cleanup-plan --path /mnt/archive --reason abandoned-marker
anonsync custody cleanup-apply apl_01J...
```

Rules:

- a discovered managed marker is not just a fancy `folder not empty` state; it is a custody fact that may carry lineage, collision, or preservation consequences
- risky local target claims must distinguish same-lineage continuation, foreign-marker inspection, successor/re-home work, local derivation, and blocked collision
- cleanup of abandoned or degraded marker state should be reviewed and receipt-bearing whenever evidence or continuity could be lost
- removable media and same-host multi-profile reuse should surface current-owner lineage and collision state directly when the daemon can infer them
- one client may compress a low-risk same-lineage reuse path, but no client may silently coerce foreign or ambiguous marker state into ordinary `adopt here` behavior


### `anonsync attention`

Inspect or manage durable attention events, delivery policy, and acknowledgement receipts without hiding the underlying reports or subjects.

```text
anonsync attention list
anonsync attention list --lane now
anonsync attention show att_01J...
anonsync attention ack att_01J...
anonsync attention snooze att_01J... --for 4h
anonsync attention policy show
anonsync attention policy set --headless-policy webhook-first --channel webhook --severity guarded,high-risk,blocked
anonsync attention receipt show atr_01J...
```

Semantics:

- attention events are derived from reports and review items, but remain durable enough to explain channel delivery and acknowledgement later
- `ack` and `snooze` must state whether they change only presentation or also resolve a subject-owned workflow elsewhere
- channel delivery must never become the only semantic location of a condition; workbench, CLI, and headless surfaces must still point back to the same reports and subjects
- policy must support Linux-first/headless deployments without giving desktop toasts or browser banners exclusive meaning

### `anonsync access`

```text
anonsync access show
anonsync access endpoint list
anonsync access endpoint show cep_01J...
anonsync access capability list
anonsync access capability show ccp_01J...
anonsync access integrity list
anonsync access integrity show cir_01J...
anonsync access handoff create --action exit-share --subject share:shr_01J... --to cli
anonsync access handoff show rhf_01J...
anonsync access handoff consume rhf_01J...
anonsync access gate show --action control-expose --subject endpoint:cep_01J...
anonsync access grant list
anonsync access grant issue --action control-expose --subject endpoint:cep_01J... --ttl 10m
anonsync access grant show mgr_01J...
anonsync access grant revoke mgr_01J...
anonsync access expose plan --class ssh-tunnel-reviewed
anonsync access expose apply apl_01J... --grant mgr_01J...
anonsync access token issue --audience automation --scope mutate --ttl 8h
anonsync access token revoke tok_01J...
anonsync access session list
anonsync access session show css_01J...
anonsync access session revoke css_01J...
anonsync access repair open --kind session-rotate --endpoint cep_01J...
anonsync access repair show arc_01J...
anonsync access repair apply arc_01J...
anonsync access receipt show acr_01J...
```

Rules:

- local IPC remains the primary administrative surface
- any non-loopback exposure is plan-bearing and receipt-bearing
- browser/workbench sessions, CLI sessions, automation tokens, and short-lived mutation grants must remain visibly different
- ordinary browser/workbench inspection must not silently imply high-signal mutation authority
- every high-signal control action should have a server-declared capability record, an explicit gate outcome, and at least one browser-independent fallback channel
- browser/client incompatibility, content blocking, and trust/bootstrap failure must become explicit integrity findings rather than disappearing actions
- a degraded channel may point to fallback or emit a handoff, but it may not offer a weaker apply path than the real review family allows
- review handoff must preserve subject, review family, gate truth, and receipt promise unless the product explicitly reopens broader review
- session or token repair must not silently mutate unrelated daemon state such as identity, state root, or global preferences
- if a proposed repair would reset broader state or reopen a different control universe, it must hand off to reviewed bring-up or state-root transition instead of pretending to be ordinary auth repair



### `anonsync compromise`

Open, inspect, and apply incident-grade containment work without hiding whether the action froze, revoked, rotated, replaced, or merely acknowledged suspicion.

```text
anonsync compromise list
anonsync compromise open --subject device:dev_01J... --reason suspected-theft --plan
anonsync compromise open --subject access-token:tok_01J... --reason bearer-leak --plan
anonsync compromise show cpc_01J...
anonsync compromise add-subject cpc_01J... --subject offer:off_01J...
anonsync compromise apply cpc_01J...
anonsync compromise receipt show cpr_01J...
```

Rules:

- opening a case may freeze the safest immediate subjects, but must not pretend later revocation or rotation already happened
- device revocation, offer revocation, access-token revocation, route/publication narrowing, and successor preparation may appear in one case while remaining visibly distinct effects
- any non-trivial case should be previewable as one fixed review grammar: `trigger and scope`, `immediate freeze`, `revocation and rotation`, `continuity and successor`, `residue and observation`, `receipt promise`
- `recover rotate-identity`, `recover revoke-device`, and incident-sensitive `exit prepare` work may reference or emit the same case/receipt model when the operator-visible meaning is compromise containment
- hiding an offline device row can never satisfy a compromise case by itself

### `anonsync link`

Create and manage personal-device constellations.

```text
anonsync link create --label personal --auto-grant-rule prompt
anonsync preflight link --group personal --invite ./desktop.link
anonsync claim prepare --invite ./desktop.link --group personal --member-class appliance
anonsync claim show clm_01J... --view review
anonsync link add --group personal --invite ./desktop.link
anonsync link show personal
anonsync link set personal --auto-grant-rule tagged-shares-only --max-permission ro
anonsync link set personal --introduction-policy pending-only
```

Semantics:

- linking creates relationship state, not identity merger
- linking may install a default policy, but never implies `owner`
- broad share visibility is opt-in policy, not a hard-coded side effect
- visible shares can land in `incoming` state without creating local paths
- introductions are disabled or pending-only by default; any wider behavior must be explicit policy
- linked-group convenience must still respect role caps and compatibility blockers surfaced by preflight
- any non-trivial member-add should be previewable as a reviewed join, not just a blind pair action
- reviewed joins should make identity continuity, requested member class/defaults, visibility delta, authority delta, compatibility, and receipt promise explicit before apply

#### Profiles

Named profiles should exist for common cases.

Examples:

- `personal-easy`
- `personal-strict`
- `team-strict`
- `encrypted-cache`
- `lan-only`

Profile installation must be inspectable:

```text
anonsync link create --label personal --profile personal-strict --plan
anonsync plan show pln_01J...
```

The plan should show the exact linked-group and discovery-policy objects that would be created.

### `anonsync share`

#### Create

```text
anonsync share create ~/Documents/work --label workdocs
anonsync share create /srv/media --label media --mode selective
anonsync share create ./vault --label vault --encrypt-on-untrusted
```

Flags:

- `--label <name>`
- `--mode detached|selective|full`
- `--write-policy send-receive|send-only|receive-only`
- `--encrypt-on-untrusted`
- `--policy <discovery-policy-id>`
- `--ignore <pathspec>` repeated (bootstrap sugar for the share's ignore policy)

#### Inspect and mutate

```text
anonsync share list
anonsync share show workdocs
anonsync share show workdocs --show-provenance
anonsync share set workdocs --write-policy send-only
anonsync share set media --policy lan-only
anonsync share pause media
anonsync share resume media
anonsync share rescan media
```

Default semantic rule:

- creating a share does **not** automatically grant it to linked devices unless an explicit linked-group policy says so

### `anonsync grant`

#### Grant access

```text
anonsync grant create workdocs --device studio-nas --perm rw
anonsync grant create vault --device cache-vps --perm encrypted-replica
anonsync grant create receipts --group personal --role readonly-viewer
anonsync preflight grant receipts --group personal --role readonly-viewer
```

#### Inspect and modify

```text
anonsync grant list --share workdocs
anonsync grant set grt_01J... --perm ro --plan
anonsync grant revoke grt_01J... --plan
```

Permissions for v1:

- `ro`
- `rw`
- `owner`
- `encrypted-replica`

Notes:

- `owner` should be rare and auditable
- `encrypted-replica` means store/seed ciphertext only
- linked-group membership is not equivalent to owner capability
- role application must not exceed linked-group caps or target-device capabilities
- trust-expanding grants should support `--plan`
- trust-narrowing grants that touch active writers, delegated authority, or derived/local dependents should also support `--plan`

#### Authority-mutation review grammar

When `grant set`, `grant revoke`, or an imported-share authority migration is non-trivial, the product should expose one fixed review grammar in this order:

1. trigger and current authority
2. desired boundary delta
3. active subject state and coupled dependents
4. authority-substrate and compatibility effects
5. admissible mutations
6. receipt promise

That review should be available in CLI/workbench/API-backed surfaces without changing its meaning.
The operator should never need to guess whether a change means “write stops but bytes stay”, “delegation is stripped but reads remain”, “local derivatives narrow automatically”, or “this weaker/imported authority substrate cannot express the requested result without migration”.

### `anonsync incoming`

Inspect and adopt newly visible shares.

```text
anonsync incoming list
anonsync incoming show inc_01J...
anonsync incoming compare inc_01J... --path ~/Sync/workdocs
anonsync incoming reconcile inc_01J... --path ~/Sync/workdocs --plan
anonsync preflight adopt inc_01J... --role laptop-cache
anonsync incoming adopt inc_01J... --path ~/Sync/workdocs --mode selective --role laptop-cache
anonsync incoming defer inc_01J... --reason "wait for external disk"
anonsync incoming hide-local inc_01J... --reason "not for this laptop"
anonsync incoming withdraw inc_01J... --reason "constellation no longer needs this"
anonsync incoming reject inc_01J... --reason "wrong machine"
```

Semantics:

- an incoming item means the share is visible, not yet mounted
- `hide-local` is presentation and claim scope on this machine only; it must not pretend wider authority changed
- `withdraw` is a wider authority action and must stay visibly different from `hide-local`
- `compare` reports whether the target path is empty, already bound, or populated with identical/local-only/remote-only/same-path-divergent/colliding content
- `reconcile` opens the reviewed non-empty-target case when target lineage or same-path divergence is strong enough that compare counts alone are not an honest contract
- adopt chooses the local path and initial mount mode
- role choice can constrain permission, write policy, and plaintext access without changing the share model
- reject records operator intent and provenance instead of silently ignoring the share
- defer keeps the item visible without committing to a path yet
- policies may prefill safe defaults, but they may not silently collapse `visible here`, `claimed here`, and `bound here` into one unreviewed step
- policies may auto-adopt only when that behavior is explicit and reviewable
- adoption into a non-empty path should normally require a comparison report and often a plan
- same-path divergent bytes or encrypted-target mismatch should normally require a reconciliation case, not just compare counts
- handling one incoming share must not require changing a device-wide linked-folder default
- dense or textual clients should be able to render `announced-only`, `deferred-local`, `claim-in-review`, `claimed-and-bound`, and `hidden-local` without inventing local-only versus wider-withdraw meaning on their own

#### Reconciliation review grammar

When `incoming adopt`, `incoming reconcile`, `mount repair`, or `mount relocate` targets a non-empty path and comparison shows same-path divergence, ambiguous lineage, or encrypted-target mismatch, the product should expose one fixed review grammar in this order:

1. target lineage and operator intent
2. compared material classes
3. same-path divergent candidates and chronology posture
4. admissible reconciliation actions and non-actions
5. preservation, quarantine, and annex effects
6. receipt promise

That review should be available in CLI/workbench/API-backed surfaces without changing its meaning.
The operator should never need to infer whether a non-empty bind means “ordinary same-lineage reuse”, “harmless merge”, “remote replaces local because timestamp ranked higher”, or “this encrypted target is not an ordinary merge case at all”.

### `anonsync ignore`

Inspect and mutate ignore behavior without editing hidden service files.

```text
anonsync ignore list workdocs
anonsync ignore add workdocs '*.tmp'
anonsync ignore remove workdocs ign_01J...
anonsync ignore test workdocs build/output.log
anonsync ignore set-consistency workdocs --mode warn-on-drift
```

Semantics:

- ignore rules are first-class supported data
- rule additions/removals should be incremental, not whole-list replacement by default
- `test` explains why a path is or is not ignored
- consistency mode states whether peer-local drift is acceptable, warned on, or rejected
- a future UI may render these rules differently, but it should not invent a different model

### `anonsync projection`

Inspect and mutate namespace-announcement and mount-view projection behavior without guessing from hidden ignore timing, placeholder cleanup, or service-file folklore.

```text
anonsync projection show workdocs
anonsync projection show --mount mnt_01J...
anonsync projection test workdocs build/output.log
anonsync projection explain --share workdocs --path build/output.log
anonsync projection add workdocs --match 'build/**' --namespace hidden --announce suppress-new
anonsync projection add mnt_01J... --match 'build/**' --local omit
anonsync projection set-tighten-behavior workdocs --mode review-existing
anonsync projection prepare-tighten workdocs --path build/output.log --plan
anonsync projection receipt list --share workdocs
anonsync projection receipt show prc_01J...
```

Semantics:

- share selectors control namespace visibility / peer announcement; mount selectors control local projection and must not silently widen share namespace
- `test` should answer whether a concrete path is announced to peers, visible in namespace, omitted locally, placeholder-visible, metadata-only, fully materialized, or preserved-but-not-shown
- `explain` and `prepare-tighten` should surface visibility history when the path was already indexed or materialized, so the operator can see whether the change only affects future announcement or also requires retraction review
- tightening a rule must not silently strand already-indexed or already-materialized paths; the policy should say whether review, safe eviction, settlement barrier, or blocking is required
- `receipt show` must make clear whether the applied change was peer-facing, local-only, or both
- mount-view projection may hide a path locally without changing replicated share namespace, and placeholder disappearance during detach must not be rendered as share-wide suppression
- future UI/TUI layers may render projection differently, but they should not invent a different model

### `anonsync layout`

Inspect and mutate share-layout separation without using hidden service files as the operator model.

```text
anonsync layout show workdocs
anonsync layout show workdocs --mount mnt_01J...
anonsync layout compare workdocs --path ~/Sync/workdocs
anonsync layout prepare workdocs --annex /var/lib/anonsync/annex/workdocs --temp-residue external-only --history external-annex --plan
anonsync layout prepare workdocs --cleanup-class metadata-carry --plan
anonsync layout review show slr_01J...
anonsync layout apply slr_01J...
anonsync layout receipt list --share workdocs
anonsync layout receipt show lyr_01J...
```

Semantics:

- `show` should answer whether the live tree is clean, mixed-managed by explicit choice, legacy-imported, inspect-only, or blocked
- `compare` should surface whether current odd bytes are live data, history/temp residue, metadata-carry sidecars, or foreign/legacy managed state
- `prepare` should be used whenever annex migration, in-tree cleanup, or residue retirement could change what appears in the ordinary tree
- cleanup must be class-based and preservation-aware rather than generic hidden-file deletion
- receipts must prove whether the action cleaned the live tree, preserved legacy evidence, or accepted an explicit in-tree managed area
- future UI/TUI layers may render this differently, but they should not invent a different model

### `anonsync semantics`

Inspect and mutate semantic-impacting optimization posture without pretending that performance tuning and guarantee weakening are the same thing.

### Replica recall and retained-copy review

```text
anonsync replicas list --share shr_01J...
anonsync replicas show rrp_01J...
anonsync recall prepare --share shr_01J... --peer peer:dev_01J... --change revoke-future-updates --bytes attest-existing-copies --plan
anonsync recall prepare --share shr_01J... --peer-set linked:family --change retire-linked-presence --bytes future-stop-only --plan
anonsync recall show rcr_01J...
anonsync recall apply rcr_01J...
anonsync recall receipt show rcrp_01J...
```

Inspect and mutate retained-copy posture without pretending that revoking future participation and recalling already-delivered bytes are the same thing.

```text
anonsync semantics show workdocs
anonsync semantics show workdocs --mount mnt_01J...
anonsync semantics explain workdocs
anonsync semantics prepare workdocs --profile degraded-network-share --reason smb-fallback --plan
anonsync semantics prepare workdocs --profile full-verify --plan
anonsync semantics review show sor_01J...
anonsync semantics apply sor_01J...
anonsync semantics receipt list --share workdocs
anonsync semantics receipt show sorc_01J...
```

Semantics:

- `show` should answer which guarantees are currently strong, weak, or uncertain for detection, rename continuity, diff behavior, verification, and conflict honesty
- `prepare` should be required whenever a requested speed or compatibility change weakens one of those guarantees
- degraded-target acceptance should say whether the weakness is share-scoped, mount-scoped, seat-scoped, or host-scoped
- restoration back to a stronger profile should remain explicit rather than silently disappearing when conditions improve
- receipts must prove whether the result was harmless tuning, reviewed downgrade, or restored stronger guarantees
- future UI/TUI layers may render this differently, but they should not invent a different model

### `anonsync conflict`

Inspect and resolve conflicts as explicit cases.

```text
anonsync conflict list --share workdocs
anonsync conflict show cft_01J...
anonsync conflict show cft_01J... --history
anonsync conflict show cft_01J... --view review
anonsync conflict resolve cft_01J... --winner candidate_02 --plan
anonsync conflict defer cft_01J... --reason "need editor review"
anonsync rollback receipt list --subject cft_01J...
```

Semantics:

- conflicts have stable IDs, semantic classes, candidate records, and linked history refs where available
- non-trivial conflicts should expose one stable review model so CLI/workbench/API-backed clients render the same adjudication sections in the same order
- the operator should not need to infer the situation from a magic filename alone
- resolution output must explain local-only vs replicated consequences and loser handling
- destructive or share-wide resolutions should usually prefer `--plan`
- completed resolutions should emit rollback receipts that can later be queried directly


### `anonsync role`

Inspect and manage reusable least-privilege templates.

```text
anonsync role list
anonsync role show readonly-viewer
anonsync role create --name readonly-viewer --perm ro --write-policy receive-only --mode selective --deviation-policy mirror-flag
anonsync role create --name encrypted-cache --perm encrypted-replica --plaintext forbidden --mode detached
```

Semantics:

- roles are convenience bundles, not a second share type
- applying a role compiles to explicit grant and mount constraints
- roles should be reusable across link, grant, and incoming-adopt flows
- role output should explain any capability or policy constraints that could downgrade or block application

### `anonsync deviation`

```text
anonsync deviation create --name mirror-flag --for receive-only --on-add preserve-and-flag --on-modify preserve-and-flag --on-delete re-fetch
anonsync deviation show mirror-flag
anonsync deviation list
anonsync deviation update mirror-flag --on-modify conflict-copy
anonsync deviation case list --mount mnt_01J...
anonsync deviation case show devc_01J...
anonsync deviation case resolve devc_01J... --action revert-local
```

Deviation policies are reusable policy objects, not hidden side effects of a role or share type.
Deviation cases are concrete path-level drift records, not just warning strings.
They must be applicable from roles, mounts, or plans, and explain surfaces should always show which deviation policy is effective.
Resolving a deviation case should say whether local evidence survives and should emit a file-intent receipt.

### `anonsync stewardship`

```text
anonsync stewardship list
anonsync stewardship show <share>
anonsync stewardship plan-handoff <share> --to <device|identity> [--policy ...]
anonsync stewardship apply <plan_id>
anonsync stewardship cancel <plan_id>
```

Rules:

- handoff plans must say exactly which authority moves (`grant`, `revoke`, `delegate`, `data-write`)
- handoff preview must show what stays with the current steward and what becomes successor-only
- if retirement or recovery state blocks safe handoff, the command must say so explicitly

### `anonsync preflight`

Generate a compatibility/authority report before commitment.

```text
anonsync preflight link --invite ./desktop.link
anonsync preflight grant receipts --group personal --role readonly-viewer
anonsync preflight adopt inc_01J... --role laptop-cache
anonsync preflight show rpt_01J...
```

Semantics:

- preflight reports blockers, warnings, downgrade notes, and authority consequences
- it should be callable independently of the later mutation for review or automation
- accepted plans may embed a referenced preflight report when risk is high
- a future UI may render this differently, but it should not invent a different model

### `anonsync report`

Read or refresh any report-bearing object through one shared operator surface.

```text
anonsync report show rpt_01J...
anonsync report list --type convergence --severity guarded
anonsync report refresh rpt_01J...
anonsync report explain rpt_01J...
```

Semantics:

- `report show` should render a common envelope regardless of whether the underlying subject is `preflight`, `comparison`, `preservation`, `convergence`, `exposure`, or `plan-drift`
- `report list` is a projection for operators; it does not replace the type-specific resources
- `report refresh` should preserve lineage to the older report where possible instead of pretending nothing changed
- textual output should include current answer, severity, freshness, scope, safest next action, and unresolved aftermath

### `anonsync mount`

#### Attach share locally

```text
anonsync mount attach workdocs ~/Sync/workdocs --mode selective
anonsync mount attach media /mnt/media --mode full
```

#### Inspect and change mode

```text
anonsync mount list
anonsync mount show mnt_01J...
anonsync mount doctor mnt_01J...
anonsync mount set mnt_01J... --mode selective
anonsync mount set-deviation mnt_01J... --policy mirror-flag
anonsync mount detach mnt_01J... --keep-visible
anonsync mount compare mnt_01J... --path /Volumes/External/workdocs
anonsync mount reconcile mnt_01J... --path /Volumes/External/workdocs --plan
anonsync mount repair mnt_01J... --path /Volumes/External/workdocs --plan
anonsync mount relocate mnt_01J... /Volumes/External/workdocs --plan
```

Semantics:

- `detached`: share known locally, no file data materialized
- `selective`: metadata visible, fetch explicit files or directories on demand
- `full`: all reachable content replicated locally
- `doctor` explains current binding health, expected path, marker drift, recent binding receipts, and whether repair is possible
- `set-deviation` changes the active local-remediation policy without changing granted authority
- `detach --keep-visible` releases the local path while preserving incoming visibility and share continuity
- `compare` previews relocation or repair into a target path and reports identical/local-only/remote-only/same-path-divergent/collision classes
- `repair` is continuity-oriented rebind for an existing mount whose path moved, drifted, or lost trusted markers
- `relocate` changes the local binding path without pretending the share label changed everywhere
- repair or relocation into a non-empty path should usually require a comparison report and `--plan`
- same-path divergent bytes or encrypted-target mismatch should usually require `mount reconcile` before a final repair/relocate apply is admissible

### `anonsync preserve`

#### Inspect baseline preservation posture

```text
anonsync preserve show mnt_01J...
anonsync preserve show workdocs --path Reports/Q1.xlsx
```

Semantics:

- `preserve show` renders the reusable preservation baseline for one mount, share, or path
- output should make peer-only history capture, retention caps, and weak rollback posture obvious without forcing a delete preview first
- later destructive or repair plans may still require a fresh action-specific preservation report

### `anonsync file`

#### Fetch

```text
anonsync file fetch media Movies/2025/
anonsync file fetch workdocs report.pdf
anonsync file fetch vault --recursive Secrets/Taxes/
```

#### Evict local materialization

```text
anonsync file evict media Movies/2025/bigfile.mkv
anonsync file evict workdocs --recursive old-exports/
```

#### Remove with explicit scope

```text
anonsync file remove media Movies/2025/bigfile.mkv --scope local
anonsync file remove vault Secrets/Taxes/report.pdf --scope share --plan
```

#### Check preservation posture

```text
anonsync file check media Movies/2025/bigfile.mkv --for evict
anonsync file check vault Secrets/Taxes/report.pdf --for remove-share
```

#### Pin / unpin

```text
anonsync file pin media Podcasts/
anonsync file unpin media Podcasts/
```

#### Availability / fetchability

```text
anonsync file availability media Podcasts/
anonsync file availability media Episodes/ep001.mp3 --view review
anonsync file availability receipt list --path Episodes/ep001.mp3
anonsync file availability receipt show frc_01J...
anonsync file fetch media Episodes/ep001.mp3 --require fetchable-now
anonsync file evict media Episodes/ep001.mp3 --plan
```

#### History / restore

```text
anonsync file history media Movies/2025/bigfile.mkv
anonsync file history media Movies/2025/bigfile.mkv --show-provenance
anonsync file restore media Movies/2025/bigfile.mkv --entry hst_01J... --scope local
anonsync file restore vault Secrets/Taxes/report.pdf --entry hst_01J... --scope share --plan
anonsync rollback receipt list --path Movies/2025/bigfile.mkv
```

Semantics:

- `fetch` materializes content
- `evict` removes local content while preserving share state
- `remove --scope local` removes the local copy or local placeholder state only
- `remove --scope share` is a replicated delete and should usually prefer `--plan`
- `check --for ...` generates a preservation report before a risky file mutation
- local deviation on non-authoritative mounts should be inspectable as deviation cases rather than inferred from stalled sync
- `pin` means keep local data across space-reclamation passes
- `file availability` should render namespace visibility, local materialization, full-copy witness summary, fetchability posture, ghost/stale-announcement risk, and eviction safety for the selected path or subtree
- every serious availability view should be able to render one compact answer strip in this order: visibility, local residency, witness summary, fetchability, safest next step
- subtree availability should preserve mixed-risk rows instead of collapsing the whole selection into one optimistic bulk state
- `evict` should normally require `--plan` when the target may be the last known full-copy witness or when fetchability is only guarded
- `fetch --require fetchable-now` should fail closed when the path is only announcement-visible, ghost-risk, or backed only by offline/uncertain witnesses
- history-backed-only cases should surface `restore` as a distinct next step instead of pretending ordinary swarm `fetch` is still honest
- mixed selections should label only the safe subset they can mutate, for example `evict 24 safe rows`, rather than overclaiming with `apply to all`
- non-safe rows should expose a review trigger instead of pretending the same direct inline button still applies
- dense and mobile views should keep local truth, source/recovery truth, and next action adjacent on the row or collapsed card
- `history` lists restorable prior states with provenance, retention horizon, and allowed scope
- `restore --scope local` restores only on this device or mount
- `restore --scope share` writes a restored version back into replicated share state and should usually prefer `--plan`
- completed restore or conflict-resolution work should be queryable later through rollback receipts, not only generic audit text
- destructive plans should reference preservation evidence such as remaining plaintext replicas, encrypted-only remnants, and history gaps
- if preservation would become too weak, the command should block or require a more explicit acknowledgement than an ordinary local remove
- the CLI must never overload one ambiguous delete action to mean both local eviction and distributed delete
- the CLI must never require hidden archive-directory knowledge for ordinary restore workflows

### `anonsync rollback`

Inspect durable receipts for restore and conflict-resolution outcomes.

```text
anonsync rollback receipt list --path Movies/2025/bigfile.mkv
anonsync rollback receipt list --subject cft_01J...
anonsync rollback receipt show rrb_01J...
```

Semantics:

- receipts are timeline-grade records, not just convenience aliases for generic audit output
- receipt detail should name source object, action kind, winner/loser handling, scope, and attached settlement or file-intent proof
- rollback receipt surfaces should stay available even after short-lived event/history summaries age out

### `anonsync offer`

Create, inspect, revoke, and reissue capability-bearing artifacts.

#### Create

```text
anonsync offer create --kind device-link --group personal --delivery file --output desktop.aso
anonsync offer create --kind share-access --share vault --role encrypted-replica --delivery file --expires 7d --uses 1 --approval required --output vps.aso
anonsync offer create --kind share-access --share photos --role readonly-viewer --delivery qr --peer-pin fp_01J... --output ./photos-readonly.png
```

#### Inspect / manage

```text
anonsync offer show ./desktop.aso
anonsync offer show off_01J...
anonsync offer list --share vault
anonsync offer revoke off_01J...
anonsync offer reissue off_01J... --delivery uri --output ./vault-link.txt
anonsync claim receipt show clr_01J...
```

Semantics:

- offers are the public object model for portable capability-bearing artifacts
- file, URI, QR, clipboard, and local handoff are delivery encodings of the same underlying semantic object
- inspecting an offer should reveal scope, expiry, use budget, peer pinning, redelegation posture, suggested local outcome, and whether claim review is required
- `offer reissue` should preserve semantic identity unless the operator explicitly changes policy, scope, or role
- `offer revoke` ends future redemption without pretending already-applied local outcomes were undone
- later audit should be able to show claim receipts even if the original artifact was one-time or has already expired

### `anonsync invite`

`invite` may remain as ergonomic alias vocabulary for common share/linking flows, but it should compile to the same `offer` object model.
The interface must not hide different authority semantics behind “invite versus not-invite” product language.

### `anonsync claim`

Prepare and review acceptance of an invite, incoming share, or device-join claim before applying it locally.

```text
anonsync claim prepare --invite ./desktop.link --group personal --member-class appliance
anonsync claim prepare --incoming inc_01J... --path ~/Sync/workdocs --mode selective --role readonly-viewer
anonsync claim show clm_01J...
anonsync claim show clm_01J... --view review
anonsync claim apply clm_01J...
anonsync claim reject clm_01J... --reason "wrong machine"
```

Semantics:

- claim creation captures the operator's intended local outcome
- link-target claims may name a linked-group outcome and requested member class instead of pretending the action is only about local path acceptance
- a claim should restate the normalized offer manifest regardless of whether the source arrived as file, URI, QR, clipboard, or local handoff
- a claim may reference a preflight report or plan when risk is high
- claim history distinguishes offered access from accepted local state
- `claim show --view review` should render a stable review grammar chosen by target action
- ordinary adoption/grant claims should render (`source`, `local outcome`, `path and filesystem`, `authority delta`, `blockers`, `receipt promise`)
- link claims should render (`identity and continuity`, `membership and defaults`, `visibility delta`, `authority delta`, `compatibility and migration`, `receipt promise`)
- claim apply should fail safely if referenced invite/offer, incoming state, peer pinning, redemption budget, expiry, or compatibility facts have drifted
- successful apply should emit a durable claim receipt that survives after the original offer artifact expires or is deleted

### `anonsync approval`

Inspect and manage bounded future-approval records.

```text
anonsync approval list --peer alex
anonsync approval show apr_01J...
anonsync approval issue --peer alex --scope share-tag:photos --max-role readonly-viewer --approver-scope linked-group --expires 90d --plan
anonsync approval revoke apr_01J...
anonsync approval test --peer alex --share vacation-2026
```

Semantics:

- there is no hidden “approved before” state outside these records
- approval memory must be bounded by scope, approver scope, expiry, and maximum role
- broad identity-wide future approval should usually prefer `--plan`
- `approval test` explains whether a future share would be auto-approved and why
- audit must show when a later invite, share, or linked-device action consumed an approval record

### `anonsync policy`

```text
anonsync policy list
anonsync policy show lan-only
anonsync policy create --name lan-only --tracker disabled --relay disabled --lan enabled
anonsync policy create \
  --name privacy-mixed \
  --tor preferred \
  --i2p allowed \
  --clearnet-direct manual-opt-in \
  --dial-via lan-direct,tor,i2p,private-relay
anonsync policy cache clear --policy lan-only
```

Expectations:

- policy output should show live settings and retained cache effects separately
- policy output should say explicitly whether WAN clearnet direct is disabled, manual-only, or generally allowed
- cache-clear operations should say which learned routes or endpoints are being invalidated

### `anonsync exposure`

Preview or inspect what a policy/share/peer currently publishes about reachability.

```text
anonsync exposure show --policy privacy-mixed
anonsync exposure show --share media --effective
anonsync exposure show --peer laptop --json
```

Expectations:

- output distinguishes baseline policy from active route leases
- output shows which infrastructure classes can currently learn reachability
- output warns when cached endpoints may outlive a policy narrowing until explicitly cleared
- operators can tell whether a peer-pinned known-host path exists without confusing that with ambient public direct

### `anonsync transport`

Inspect, warm, cool, or verify the bundled transport engines.

```text
anonsync transport list
anonsync transport show tor
anonsync transport show i2p --json
anonsync transport warm tor
anonsync transport warm i2p
anonsync transport cool i2p
anonsync transport verify tor
anonsync transport verify i2p
anonsync transport session list
anonsync transport session show tss_01J...
```

Expectations:

- output should show whether the engine is compiled in or activated from an embedded payload
- output should show bootstrap state, health findings, any runtime path that was created locally, and any persistent state path the engine expects to reuse
- `verify` should expose payload/build version, digest, update mode, and provenance facts safe for local inspection
- operators should be able to tell whether a route was unavailable because policy forbade it, because the runtime was cold, because bootstrap failed, or because verification/provenance checks are degraded
- session output should show whether the daemon is reusing a long-lived shared overlay session or creating something more dedicated
- a future UI should not need a hidden transport model beyond what these commands already expose

### `anonsync activity`

Read the effective runtime phase state for a subject.

```text
anonsync activity show --share media
anonsync activity show --device laptop-ember --effective
anonsync activity explain --share media
```

This surface should say directly which phases are active, throttled, suspended, or draining.
It should also distinguish baseline policy from active overrides and recurring schedule windows.

### `anonsync schedule`

Manage recurring activity windows.

```text
anonsync schedule create --target device:laptop-ember --preset metered-link --route-class internet --down 2MiB/s --up 512KiB/s --rrule 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8,9,10,11,12,13,14,15,16,17'
anonsync schedule list
anonsync schedule show swn_01J...
anonsync schedule disable swn_01J...
anonsync schedule enable swn_01J...
```

Notes:

- recurring windows should compile to the same effective-state model as one-shot overrides
- output should make route-class scope explicit so LAN-vs-Internet behavior is never hidden
- stronger windows such as `maintenance-freeze` may require plan/apply

### `anonsync override`

Create or inspect temporary runtime overrides without rewriting durable grants, links, or discovery policy.

```text
anonsync override create --target share:docs --mode pause-transfer --ttl 2h --reason "metered uplink"
anonsync override create --target device:laptop --mode drain-egress --ttl 45m --reason "shutdown maintenance"
anonsync override create --target policy:travel --mode throttle --down 4MiB/s --up 1MiB/s --ttl 8h
anonsync override list
anonsync override show ov_01J...
anonsync override explain ov_01J...
anonsync override renew ov_01J... --ttl 2h
anonsync override cancel ov_01J...
anonsync override receipt show ovr_01J...
```

Rules:

- overrides are additive temporary leases, not hidden edits to the underlying policy object
- every override must either expire automatically or require an explicit `--no-expiry` acknowledgement
- `status`, `policy show`, `route`, `activity`, `diagnostic`, `access`, and `explain` should reveal the effective behavior together with contributing overrides and schedules
- renewal should preserve lease history instead of replacing it with a fresh unrelated object
- high-risk overrides that affect publication, access exposure, delete behavior, or redaction posture should require a reviewed plan before apply

### `anonsync route`

Inspect effective connectivity and route-decision traces.

```text
anonsync route list
anonsync route show --share workdocs
anonsync route show --peer laptop --explain
anonsync route show --share media --decision-trace
anonsync route known-host add --peer laptop --addr sync.example.net:3847 --share media --ttl 7d --reason "trusted home uplink"
anonsync route known-host list --peer laptop
anonsync route allow-clearnet-direct --share media --ttl 2h --byte-cap 250GiB --reason "trusted bulk transfer"
anonsync route allow-clearnet-direct --peer laptop --ttl 30m --reason "initial seed to trusted peer"
anonsync route lease list
anonsync route lease show rls_01J...
anonsync route lease cancel rls_01J...
```

Expectations:

- route output should show active path, viable candidates, and rejected candidates separately
- route output should show transport class (`lan-direct`, `tor`, `i2p`, `public-direct`, `private-relay`, etc.) and exposure class separately
- `--explain` should include the policy, cache, capability, and manual-override facts that made the current route win
- decision-trace output should say whether the explanation is current or derived from older policy/cache state
- operators should not need to infer relay/direct choice from icons alone
- if WAN clearnet direct is active, the output should say whether that happened because of a manual speed override and when that override expires
- route output should distinguish peer-pinned known-host direct from general public direct
- route and explain output should make it obvious when a temporary bulk-speed lease is the only reason a public-direct candidate is eligible
- when a byte cap exists, route/lease output should show remaining budget or the exhaustion reason after the lease ends

### `anonsync explain`

Generic decision-path inspection for high-signal objects.

```text
anonsync explain grant grn_01J...
anonsync explain claim clm_01J...
anonsync explain route --share workdocs
anonsync explain mount mnt_01J...
```

Expectations:

- output should summarize selected outcome, rejected alternatives, and decisive facts
- explanations should reuse stable reason codes so automation and future UIs can depend on them
- an object with no meaningful decision path should say so explicitly instead of inventing fake detail

### `anonsync plan`

```text
anonsync plan list
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync plan cancel pln_01J...
```

Plan objects are required for operations that:

- widen trust scope
- replace or rebind identities
- rewrite grants after recovery
- install multi-object policy bundles

### `anonsync transfer`

```text
anonsync transfer list
anonsync transfer show trf_01J...
anonsync transfer explain trf_01J...
anonsync transfer policy show --share media
anonsync transfer policy set --share media --priority newer-first --fairness per-peer-fair --prefer-route overlay
anonsync transfer budget show --share media
anonsync transfer budget set --share media --internet-up 2MiB/s --internet-down 8MiB/s --relay-byte-budget 10GiB/day --reason "hotspot week"
anonsync transfer set trf_01J... --lane interactive
anonsync transfer receipt show tbr_01J...
```

### `anonsync history`

Optional convenience group for operators who think in terms of version history rather than file actions.
It should be thin sugar over the same file-history model.

```text
anonsync history list --share media --path Movies/2025/bigfile.mkv
anonsync history show hst_01J...
```

### `anonsync status`

Status output should surface active deviation state for non-authoritative mounts, including whether local adds, edits, or deletes have been preserved, auto-remediated, or are blocking remote progress. Scope-sensitive file actions should also be able to reference the resulting file-intent receipts.


```text
anonsync status
anonsync status --json
anonsync status --watch
```

Human output should answer:

- which peers are online
- what newly needs attention now versus what can wait
- which shares are degraded
- which routes are active
- whether any linked-group or policy changes are pending apply
- whether compatibility warnings or role downgrades are pending review
- whether any share is only apparently idle versus actually converged with high confidence

### `anonsync converge`

Inspect or wait for settlement confidence instead of guessing from generic status output.

```text
anonsync converge show --share workdocs
anonsync converge show --share workdocs --intent cutover
anonsync converge wait --share workdocs --intent backup --timeout 10m
anonsync converge explain cvr_01J...
```

Semantics:

- convergence is stronger than “no transfer currently queued”
- reports should distinguish `converged` from `degraded-converged`
- source availability, watcher health, clock health, and hidden background work all affect confidence
- `wait` should return structured blocker information instead of sleeping blindly until timeout
- intent matters: a casual status check may accept lower confidence than relocation, backup, or cutover
- future UI/TUI layers should consume the same report rather than inventing their own readiness heuristic

### `anonsync settle`

Inspect and reuse explicit readiness barriers rather than translating convergence reports by hand.

```text
anonsync settle policy list
anonsync settle policy show cutover-strict
anonsync settle barrier create --share workdocs --intent cutover --policy cutover-strict
anonsync settle barrier show stb_01J...
anonsync settle barrier wait stb_01J... --timeout 10m
anonsync settle receipt show str_01J...
```

Semantics:

- settlement policy is distinct from current convergence evidence
- barriers should expose stable failed-clause codes, evidence age, quiet-window progress, and expiry
- high-signal actions may require a named barrier or emit a settlement receipt automatically
- later audit must be able to answer which readiness standard an action actually used
- future UI/TUI layers should consume the same barrier and receipt objects rather than inventing their own cutover heuristics

### `anonsync doctor`

```text
anonsync doctor
anonsync doctor --share media
anonsync doctor --device studio-nas
```

Doctor is the diagnosis surface, not a secret-debug fallback.
It should emit stable finding codes, including compatibility/preflight findings that explain blocked or downgraded actions.
It should also point at convergence reports when idle-looking state is degraded by watcher exhaustion, clock skew, hidden merge work, or missing sources.

### `anonsync audit`

```text
anonsync audit
anonsync audit --type grant.created
anonsync audit --subject shr_01J...
anonsync audit --correlation corr_01J...
```

### `anonsync backup` and `anonsync recover`

```text
anonsync backup create --output ./mesh.asb
anonsync recover posture show
anonsync recover bundle export --type encrypted-offline-decrypt --share vault --output ./vault.arb
anonsync recover bundle export --type device-replacement --device dev_01J... --output ./laptop.arb
anonsync recover bundle show ./vault.arb
anonsync recover bundle verify ./vault.arb
anonsync recover import ./mesh.asb
anonsync recover replace-device --old dev_dead --new dev_new --plan
anonsync recover rotate-identity --device dev_01J... --plan
anonsync recover revoke-device --device dev_01J... --plan
anonsync recover decrypt-replica --input /mnt/cache/vault --bundle ./vault.arb --output ./vault-restored
anonsync recover receipt show rcr_01J...
anonsync plan apply pln_01J...
```

Semantics:

- recovery should surface rewritten grants and policy consequences before apply
- replacement is distinct from linking
- offline encrypted-replica recovery should be possible without a running daemon when sufficient recovery material is available
- recovery bundles make prerequisites explicit and verifiable ahead of failure
- recovery posture should say whether a workflow is portable, split-secret, or still daemon-bound in an important way
- bundle verification should say whether decrypt can proceed, whether metadata is partial, and whether any hidden daemon-state dependency remains
- export, verification, invalidation, and consumption should emit recovery receipts rather than disappearing into a filesystem artifact alone
- rotation and revocation produce audit entries and events that are easy to query
- recovery plans should carry forward compatibility and role consequences where device capabilities changed
- incident-driven rotation or revocation should be able to reference the reviewed compromise-case model instead of forcing operators to reconstruct meaning from separate commands
- `recover replace-device --plan` and continuity-sensitive root/profile transitions should expose one stable cutover review model rather than generic migration prose
- that cutover review model should render (`predecessor and candidate`, `continuity carry-forward`, `state-root and runtime target`, `share/grant/authority rewrite`, `residue and revocation`, `receipt promise`)
- retirement records should show whether the action was cosmetic cleanup, active trust retirement, or continuity-preserving replacement


### `anonsync state`

```text
anonsync state show
anonsync state roots
anonsync state root show srt_01J...
anonsync state verify
anonsync state export --output ./mesh.asb
anonsync state attach --path ~/.config/anonsync/root-a --plan
anonsync state move-root --to /srv/anonsync/root --plan
anonsync state switch-profile --to background-service --plan
anonsync state replace-identity-root --from ./identity.asi --plan
anonsync plan apply stp_01J...
```

Semantics:

- `state show` reveals the active state root, active service profile, identity fingerprint summary, and verification freshness
- `state roots` lists known local roots and makes clear which one is active versus merely attachable or stale
- `state verify` produces a fresh attestation rather than only a boolean success/fail
- `attach`, `move-root`, `switch-profile`, and `replace-identity-root` should normally produce plans plus state-transition reports
- profile switches should say whether they keep the same root open or would land in a different root context
- move-root should require a credible rollback strategy and post-move verification receipt
- import/export should stay distinct from attach/move even when they touch similar files on disk

## Filesystem compatibility surfaces

The CLI should expose explicit filesystem-semantics inspection rather than leaving operators to infer behavior from later conflicts.

Suggested commands:

```text
anonsync fs profile <path>
anonsync fs profile <path> --json
anonsync fs support
anonsync fs support --path <target>
anonsync fs compare --share <share> --path <target>
anonsync fs compare --mount <mount> --path <target>
anonsync fs explain <report_id>
anonsync mount adopt <incoming> --path <target> --fs-report <report_id>
anonsync doctor <share-or-path> --include fs
```

Expected semantics:

- `fs profile` reports local path semantics and fidelity limits
- `fs support` reports the daemon's declared support tier for either the host generally or a specific target path
- `fs compare` generates a durable filesystem compatibility report
- `mount adopt` and `mount relocate` should be able to require a fresh fs compatibility report when risk is non-trivial
- `doctor` should surface runtime drift when a mounted path no longer satisfies expected semantics
- `explain` should say whether a rename, normalization rewrite, metadata strip, or symlink downgrade is expected and why


## Filesystem fidelity surfaces

Filesystem compatibility is not enough once a mount exists.
The CLI should also expose the durable portability/fidelity contract the mount is actually operating under.

Suggested commands:

```text
anonsync fs policy list
anonsync fs policy show <policy>
anonsync fs contract prepare --share <share> --path <target> --policy <policy>
anonsync fs contract show <mount|contract_id>
anonsync fs contract verify <mount|contract_id>
anonsync fs drift list
anonsync fs drift show <drift_case_id>
anonsync fs receipt list --mount <mount>
anonsync fs receipt show <fidelity_receipt_id>
```

Expected semantics:

- `fs contract prepare` previews the durable semantics contract the operator would be accepting
- `fs contract show` answers what pathname, metadata, notification, and support-tier semantics are promised on the mount right now
- `fs contract verify` re-checks whether the contract still matches current reality and emits drift if it no longer does
- `fs receipt show` proves which downgrade or warning-tier posture the operator knowingly accepted
- `mount adopt`, `mount relocate`, and certain repair flows should be able to require a referenced fidelity contract when portability risk is non-trivial


## Space, pressure, and retention surfaces

Space truth should not be trapped inside one low-disk warning or support article.
The CLI should expose explicit budget, pressure, reclaim, and receipt surfaces.

Suggested commands:

```text
anonsync space show
anonsync space show --mount <mount>
anonsync space classes --share <share>
anonsync space policy list
anonsync space policy show <policy>
anonsync space pressure list
anonsync space pressure show <pressure_case_id>
anonsync space reclaim prepare --mount <mount> --target-bytes 20GiB
anonsync space reclaim prepare --state-root <srt> --class logs,temp-downloads
anonsync space reclaim apply <reclaim_plan_id>
anonsync space receipt list --subject <mount>
anonsync space receipt show <reclaim_receipt_id>
```

Expected semantics:

- `space show` answers where local space is going by byte class rather than by hidden implementation path
- `space pressure show` explains why a pressure case fired and what safe-first reclaim options exist
- `space reclaim prepare` previews freed bytes, preserved bytes, and any retention or history consequences before apply
- `space reclaim apply` must never widen into replicated delete semantics; share-state mutation should require different verbs
- `space receipt show` proves what was actually reclaimed and whether rollback/history posture changed

### `anonsync claim receipt`

Inspect durable proof of offer consumption and resulting local outcome.

```text
anonsync claim receipt list --subject shr_01J...
anonsync claim receipt show clr_01J...
```

Semantics:

- receipts should prove which offer was consumed, under which policy, by whom, into which local outcome
- receipt detail should name delivery encoding, residual redemption state, referenced reports/plans, and resulting subject IDs
- later audit must not depend on the original portable artifact still existing on disk


## Policy origin and defaults surfaces

Once the archive has many first-class policy domains, the CLI also needs one cross-domain explanation surface.
Operators should be able to inspect effective policy, origin, inheritance state, and defaults/profile impact without reverse-engineering settings layers.

Suggested commands:

```text
anonsync defaults profile list
anonsync defaults profile show personal-strict
anonsync defaults profile apply personal-strict --to link:personal --future-only --plan
anonsync defaults profile apply travel-lite --to share-class:incoming --eligible-existing --plan
anonsync policy explain --share media
anonsync policy explain --share media --domain transfer
anonsync policy binding list --subject share:media
anonsync policy pin --share media --domain transfer --field priority --value newer-first --plan
anonsync policy inherit --share media --domain transfer --field priority --plan
anonsync policy receipt list --subject share:media
anonsync policy receipt show por_01J...
```

Expected semantics:

- `policy explain` answers both the effective value and the per-field origin chain
- `policy binding list` shows which domains are inheriting, pinned, imported, override-derived, or schedule-derived
- `defaults profile apply` previews whether the change affects future subjects only, all eligible inheriting subjects, or an explicit reviewed subset
- `policy pin` and `policy inherit` stay distinct so `return to inheritance` is never hidden behind ambiguous reset wording
- `policy receipt show` proves which fields changed, what the origin state was before, and whether the action touched future-only or existing subjects


## Exit and decommission surfaces

Use one explicit family for reviewed departure-style actions instead of overloading `remove`.

```text
anonsync exit prepare device dev_01J... --intent revoke-authority --plan
anonsync exit prepare daemon self --intent decommission --preserve recovery-only --plan
anonsync exit prepare share shr_01J... --intent retire-share-presence --scope constellation:travel --plan
anonsync exit show exp_01J...
anonsync exit apply exp_01J...
anonsync exit residue list --subject device:dev_01J...
anonsync exit residue show exd_01J...
anonsync exit receipt show exr_01J...
```

Rules:

- `hide`, `detach-local`, `revoke-authority`, `decommission`, `replace-with-successor`, and `erase-local-residue` must remain distinct intents
- domain-specific commands such as `device retire`, `mount detach`, `offer revoke`, `access token revoke`, and `recover invalidate-bundle` may remain, but they should compile to compatible exit plans or receipts when the operator outcome is “leave, stop, revoke, or clear”
- exit surfaces must always show **what stops now**, **what stays intentionally**, and **what residue still remains**
- local cleanup must never be presented as proof that remote or offline residue is gone
- continuity-preserving exits must say exactly what successor, recovery, or preservation claim survives the exit
- `exit show ... --view review` should render a fixed group order: `intent & scope`, `stops now`, `stays intentionally`, `residue after apply`, `follow-up options`, `receipt promise`
- every row in that review view should carry a scope chip such as `local`, `share`, `constellation`, `remote`, or `time-bound`
- the apply verb in rich or textual surfaces should inherit the reviewed intent label (`Revoke authority`, `Decommission`, `Bind successor`) instead of collapsing back to generic `Remove` or `Apply`


## Observer/read-only and local-write-containment surfaces

Use one explicit family for observer-style or read-only semantics instead of treating one label as self-explanatory.

```text
anonsync observer show --subject shp_01J...
anonsync observer show --mount mnt_01J...
anonsync observer prepare --share reports --peer dev_tablet --posture full-byte-observer --plan
anonsync observer prepare --share archive --peer dev_kiosk --posture names-only-observer --plan
anonsync observer prepare --derivative ldr_01J... --posture placeholder-observer --change change-local-projection --plan
anonsync observer repair --subject shp_01J... --mode path-revert --plan
anonsync observer review show orr_01J...
anonsync observer apply orr_01J...
anonsync observer receipt show orc_01J...
```

Rules:

- `observer`, `read only`, `viewer`, `receive only`, and `names only` must never be treated as interchangeable aliases unless the underlying bundle of visibility/write/serve/projection facts is actually the same
- every review must show four truths separately: what bytes or names are visible, what local edits do, whether the subject may serve bytes onward, and which parts of the posture are only artifacts of share class, derivation, runtime seat, or materialization mode
- repair helpers such as `path-revert` must stay explicit and must say when they are unavailable because of the current projection or local-mode choice
- a non-authoritative subject may still hold bytes useful for reseed, recall, or settlement, so `cannot write` must not imply `operationally irrelevant`
- `observer show ... --view review` should render a fixed group order: `requested posture`, `visibility reality`, `local-write and repair behavior`, `onward serving`, `projection/class limits`, `receipt promise`
- every row in that review view should carry a scope chip such as `authority`, `projection`, `local-bytes`, `serve-rights`, or `runtime-limit`
- the apply verb in rich or textual surfaces should inherit the reviewed posture label (`Make placeholder observer`, `Repair read-only path`, `Narrow to non-serving mirror`) instead of collapsing back to generic `Apply`

## Approval-seat and blast-radius surfaces

Use one explicit family for pending approvals and future-approval memory instead of letting `Approve` hide which member is speaking or how far the grant travels.

```text
anonsync approval queue
anonsync approval show <approval_request_id>
anonsync approval review prepare <approval_request_id> --seat <member_id> --scope this-subject --plan
anonsync approval review prepare <approval_request_id> --seat <member_id> --scope reviewed-future:<policy_or_share_class> --plan
anonsync approval review show <approval_review_id>
anonsync approval approve <approval_review_id>
anonsync approval deny <approval_request_id>
anonsync approval receipt show <approval_receipt_id>
```

Rules:

- `approve once`, `approve for reviewed scope`, `keep pending`, and `deny` must remain distinct intents
- every review must show four truths separately: requested subject, acting seat, approval horizon, and receipt promise
- a candidate seat switch must visibly recompute the admissible horizon; it is not only a cosmetic runtime choice
- any action that creates standing future approval memory must say so explicitly and must name its boundary (`this-share-class`, `named-members`, `reviewed-constellation-scope`, or narrower)
- `approval review show ... --view review` should render a fixed group order: `requested action`, `acting seat`, `approval horizon`, `share/constellation fallout`, `admissible actions`, `receipt promise`
- every row in that review view should carry a scope chip such as `this-subject`, `future-memory`, `seat-only`, `constellation`, or `blocked`
- the apply verb in rich or textual surfaces should inherit the reviewed intent label (`Approve once`, `Approve for reviewed scope`, `Deny request`) instead of collapsing back to generic `Approve`

## Standing-approval memory and matched-arrival guardrail surfaces

Use one explicit family for later arrivals that match remembered approval instead of letting `approved before` silently turn into `connect here now`.

```text
anonsync approval match queue
anonsync approval match show <approval_match_id>
anonsync approval match review prepare <approval_match_id> --mode suggest-claim --plan
anonsync approval match review prepare <approval_match_id> --mode require-fresh-review --plan
anonsync approval match review prepare <approval_match_id> --mode tighten-memory --scope this-share-class --plan
anonsync approval match review show <approval_match_review_id>
anonsync approval match apply <approval_match_review_id>
anonsync approval memory show <approval_id>
anonsync approval memory revoke <approval_id>
```

Rules:

- remembered approval, current arrival, local claim, path bind, and local materialization must remain distinct intents even when they are causally related
- a standing approval match may satisfy prior identity trust or move an arrival into a lower-friction queue, but it must not silently choose a path, create a bind, or materialize bytes
- every review must show six truths separately: current arrival, matched memory, narrow auto-admit boundary now, local claim/materialization effects, wider alternatives, and receipt promise
- any permitted auto-admit outcome must be named narrowly (`identity-only`, `queue-admitted`, `claim-suggested`) rather than hidden under `auto-connect`
- if the current arrival falls outside remembered scope, would widen rights, or would reuse stale memory after policy drift, the honest next step is fresh review
- `approval match review show ... --view review` should render a fixed group order: `arrival and match evidence`, `what prior trust actually covers`, `local claim and bind effects`, `admissible actions`, `memory tighten/revoke options`, `receipt promise`
- every row in that review view should carry a scope chip such as `matched`, `identity-only`, `claim-suggested`, `fresh-review`, `memory-drift`, or `revoked`
- the apply verb in rich or textual surfaces should inherit the reviewed intent label (`Suggest claim`, `Require fresh review`, `Tighten memory`, `Revoke memory`) instead of collapsing back to generic `Connect` or `Auto-approve`


## Approval-seat roster and active-request split surfaces

Use one explicit family for approval coordination instead of letting seat presence, completed review, and current live request collapse into one badge.

```text
anonsync approval coordination show <approval_request_id>
anonsync approval roster show <approval_request_id>
anonsync approval request open <approval_request_id> --seat <member_id> --basis <basis_id> --plan
anonsync approval request rerequest <approval_request_id> --seat <member_id> --basis <basis_id> --reason basis-drift --plan
anonsync approval request clear <approval_request_id> --seat <member_id> --reason reviewed-current --plan
anonsync approval coordination receipt show <approval_coordination_receipt_id>
```

Rules:

- `eligible seat`, `requested on current basis`, `reviewed current basis`, and `rerequest needed` must remain distinct public states
- seat-roster visibility may survive completed review; clearing a live request must not erase seat continuity if the seat still matters
- later basis drift must not silently reactivate an older request; the honest state is `rerequest-needed` until a fresh explicit ask targets the current basis
- queue rows and dense cards may not say `waiting on review` when no live request exists for the current basis
- `approval coordination show ... --view review` should render a fixed group order: `current basis`, `seat roster`, `active request state`, `latest review witness versus current basis`, `admissible actions`, `receipt promise`
- every row in that review view should carry a scope chip such as `eligible`, `requested-current`, `reviewed-current`, `rerequest-needed`, `blocked`, or `historical`
- the apply verb in rich or textual surfaces should inherit the reviewed coordination intent label (`Request review on seat`, `Re-request on current basis`, `Clear live request`, `Switch to narrower seat`) instead of collapsing back to generic `Request` or `Pending`


## Share-local presence and future-arrival policy surfaces

Use one explicit family for a seat's current local share posture and later-arrival defaults instead of letting one `mode` label answer both.

```text
anonsync presence show --share photos --seat self
anonsync presence review prepare --share photos --seat self --change current-posture:placeholder-view --plan
anonsync presence review prepare --share photos --seat self --change current-bind:relocate --target /srv/photos --plan
anonsync presence policy show --seat self --scope linked-arrivals:family
anonsync presence policy prepare --seat self --scope linked-arrivals:family --default announce-only --plan
anonsync presence policy prepare --seat self --scope linked-arrivals:family --default claim-suggested --path-template /srv/family/{{share_name}} --plan
anonsync presence review show <presence_review_id>
anonsync presence apply <presence_review_id>
anonsync presence receipt show <presence_receipt_id>
```

Rules:

- `announced`, `claimed`, `bound`, `placeholder-backed`, and `full-byte` must remain separate facts even when a client chooses a compact rendering
- `change current share here` and `change what future arrivals do here` must remain separate intents unless the review explicitly says both are changing
- any path template, default root, or collision rule must render as **future-arrival policy**, not as if it were already a fact about the current share
- path provenance (`reviewed`, `template-derived`, `collision-adjusted`, `operator-picked`, `restored`) must stay adjacent to local bind truth
- a dense/mobile surface may compress wording, but it may not collapse `this share is currently placeholder-backed` into `this seat will handle future arrivals as placeholders`
- `presence review show ... --view review` should render a fixed group order: `current posture now`, `future-arrival policy`, `path provenance and collision posture`, `byte posture and fetch policy`, `admissible transitions`, `receipt promise`
- every row in that review view should carry a scope chip such as `current-share`, `future-arrivals`, `path-provenance`, `byte-posture`, or `blocked`
- the apply verb in rich or textual surfaces should inherit the reviewed intent label (`Queue future arrivals here`, `Keep current share bound`, `Materialize full bytes here now`, `Change future arrivals to announce only`) instead of collapsing back to generic `Change mode`


## Placement-suggestion and collision-review surfaces

Use one explicit family for candidate paths and bind decisions instead of letting `Connect`, default roots, or suffix fallback hide why a path was suggested and whether it is truly safe.

```text
anonsync placement suggest show --share photos-2025 --seat self
anonsync placement review prepare --share photos-2025 --seat self --candidate /srv/family/Photos-2025 --plan
anonsync placement review prepare --share photos-2025 --seat self --candidate /srv/family/incoming/Photos-2025 --plan
anonsync placement review prepare --share photos-2025 --seat self --adopt-existing /srv/family/Photos-2025 --plan
anonsync placement review show <placement_review_id>
anonsync placement apply <placement_review_id>
anonsync placement receipt show <placement_receipt_id>
```

Rules:

- a suggested path must render as a candidate plus reason (`share-name-under-reviewed-root`, `scope-template`, `remembered-seat-preference`, `manual-draft`, `restored-bind`), not as if it were already the committed bind
- collision posture (`clear`, `occupied-empty`, `occupied-nonempty-unrelated`, `occupied-same-lineage-candidate`, `managed-bind-held`, `case-fold-collision`) must stay adjacent to the candidate path
- one-share alternate-path choice and future-template/default change must remain separate intents unless the review explicitly says both are changing
- a suffix-adjusted fallback path must never be silently chosen; if the product proposes `/srv/family/Photos-2025 (1)`, it must be shown as an explicit candidate with an explicit reason, never as invisible duplicate correction
- `placement review show ... --view review` should render a fixed group order: `subject and current bind truth`, `suggested path and why`, `collision class and evidence`, `admissible placement outcomes`, `future-default impact`, `receipt promise`
- every row in that review view should carry a scope chip such as `candidate-path`, `collision`, `same-lineage`, `alternate-path`, `defaults-unchanged`, or `blocked`
- the apply verb in rich or textual surfaces should inherit the reviewed intent label (`Bind at suggested path`, `Compare and adopt`, `Choose alternate path`, `Keep announced only`) instead of collapsing back to generic `Connect`


## Standing arrival-template governance surfaces

Use one explicit family for seat-level future-arrival templates instead of letting `mode`, `default folder`, or `Simple mode` stand in for durable policy.

```text
anonsync arrival-template list --seat self
anonsync arrival-template show --seat self --scope family-arrivals
anonsync arrival-template review prepare --seat self --scope family-arrivals --admission announce-only --path-template /tank/family/{{share_name}} --collision-default always-review --draft-refresh unchanged --plan
anonsync arrival-template review prepare --seat self --scope family-arrivals --admission claim-suggested --path-template /srv/family/{{share_name}} --collision-default propose-alternate --draft-refresh refresh-unclaimed --plan
anonsync arrival-template review show <arrival_template_review_id>
anonsync arrival-template apply <arrival_template_review_id>
anonsync arrival-template receipt show <arrival_template_receipt_id>
```

Rules:

- a standing arrival template must render as its own seat-scoped policy object, not as a hidden consequence of current-share placement or bind actions
- every review must show one fixed group order: `reviewed seat and governed scope`, `current standing template`, `proposed standing template`, `effect buckets`, `exceptions and pinned subjects`, `admissible actions`, `receipt promise`
- effect buckets must at least distinguish `future unseen arrivals`, `currently announced but unclaimed arrivals`, `currently claimed but unbound arrivals`, and `currently bound shares`
- the conservative default is `drafts unchanged`; refreshing existing unclaimed drafts to a new template must be explicit
- currently bound shares must never be moved, dematerialized, or re-bound by a standing-template change
- dense/mobile surfaces may compress wording, but they may not hide which governed scope changed or which current subjects stayed untouched
- the apply verb in rich or textual surfaces should inherit the reviewed intent label (`Change standing template`, `Also refresh unclaimed drafts`, `Keep current template`) instead of collapsing back to generic `Save defaults`


## Arrival explanation contract

Important later-arrival subjects should support one explanation projection that keeps the following adjacent:

- current local stage
- causal chain
- governing standing state
- explicit non-causes
- counterfactual differences
- next honest verbs
- supporting receipts

The operator should be able to move from `why is this subject here?` to `what prior trust or standing template influenced it?` without opening three unrelated pages.
Generic verbs such as `Connect` should be considered insufficient wherever the truthful next act depends on whether the subject is merely announced, claim-suggested, unbound, or already bound.


## Policy-delta preview and arrival-simulation contract

Important standing-policy edits should support one preview projection that keeps the following adjacent:

- governed seat and scope
- proposed delta
- effect buckets across future unseen arrivals, visible drafts, claimed-unbound subjects, bound shares, bytes, and approval memory
- named example subjects
- explicit non-effects
- honest apply labels
- supporting receipts

The operator should be able to move from `change this standing policy` to `what exactly will this touch?` without mentally simulating old mode/default/simple-mode folklore.
Generic verbs such as `Save settings` should be considered insufficient wherever the truthful next act depends on whether the change is future-only, draft-refreshing, subset-reviewed, or blocked.



## Standing-policy lineage and subject-attribution surfaces

Use one explicit family for effective standing-policy versions and per-subject attribution instead of expecting current settings plus old receipts to tell the whole story.

```text
anonsync policy lineage show --seat self --scope family-arrivals
anonsync policy lineage show --seat self --scope family-arrivals --history 10
anonsync subject policy show --subject incoming:photos-2026 --seat self
anonsync policy compare --current spv_01J... --applied spv_01H...
anonsync policy receipt show pdr_01J...
```

Rules:

- every meaningful standing-policy family must expose a durable current effective version with effective-from time and supersession links
- every arrival-worthy or draft-worthy subject must be able to show which standing-policy version handled it, or explicitly say `unknown`
- `matches current`, `grandfathered`, `draft-carried-forward`, and `memory-matched` must remain separate attribution classes even on compact surfaces
- a current policy view and a subject-attribution view must remain separate intents unless the interface explicitly says both are being shown together
- `policy compare` must render current-versus-applied differences semantically, not only as raw field diffs
- `subject policy show ... --view review` should render a fixed group order: `seat and current version`, `lineage`, `subject attribution`, `current-versus-applied compare`, `what did not change`, `admissible actions`, `receipts and proofs`
- every row in that review view should carry an attribution chip such as `matches-current`, `grandfathered`, `draft-carried-forward`, `memory-matched`, or `unknown`
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`View lineage`, `Compare versions`, `Refresh eligible draft`, `Keep grandfathered outcome`) instead of collapsing back to generic `Settings` or `Reconnect`



## Standing-policy drift and realignment surfaces

Use one explicit family for post-lineage operational drift instead of expecting `current policy` plus `applied policy then` to be enough by themselves.

```text
anonsync policy drift list --seat self --scope family-arrivals
anonsync policy drift show --subject incoming:photos-2026 --seat self
anonsync policy realignment review prepare --seat self --scope family-arrivals --subjects incoming:photos-2026 --outcome refresh-drafts --plan
anonsync subject exception pin --subject share:invoices-2025 --seat self --reason "legacy bind intentionally retained"
anonsync policy receipt show prr_01J...
```

Rules:

- every meaningful standing-policy family must expose a drift-population view keyed to one current effective target policy
- per-subject drift classes such as `matches-current`, `grandfathered`, `refresh-eligible`, `subset-review-required`, `pinned-exception`, `blocked`, and `unknown` must remain distinct even on compact surfaces
- `policy drift list` and `policy lineage show` must remain separate intents unless the interface explicitly says both are being shown together
- realignment batches must split safe refresh subjects from subset-review subjects before apply
- `keep grandfathered` and `pin exception` must remain separate verbs where the first preserves an allowed older outcome and the second creates a durable reviewed exception object
- `policy realignment review ... --view review` should render a fixed group order: `seat and target policy`, `drift population`, `per-subject classes`, `proposed effects`, `what stays grandfathered or pinned`, `admissible actions`, `receipts and proofs`
- every row in that review view should carry one explicit drift chip such as `refresh-eligible`, `grandfathered`, `subset-review`, or `pinned-exception`
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Refresh eligible drafts`, `Open subset review`, `Pin exception`, `Keep grandfathered`) instead of collapsing back to generic `Apply defaults` or `Reconnect`


## Exception-aging and re-review surfaces

Use one explicit family for long-lived intentional divergence instead of expecting `pinned exception` or `keep grandfathered` to remain honest forever on their own.

```text
anonsync policy exception review list --seat self --scope family-arrivals
anonsync policy exception review show --subject share:invoices-2025 --seat self
anonsync policy exception renew prepare --subject share:invoices-2025 --seat self --horizon 180d --plan
anonsync policy exception reconsider prepare --subject incoming:photos-2026 --seat self --outcome return-to-current-policy --plan
anonsync policy exception acknowledge-no-expiry --subject share:invoices-2025 --seat self --reason "legacy bind is long-term intentional"
```

Rules:

- every meaningful standing-policy family that allows `keep grandfathered` or `pin exception` must also expose an exception-aging view keyed to one reviewed seat and governed scope
- every intentional non-current subject must carry one explicit review-horizon class such as `healthy`, `due-soon`, `overdue`, `blocked`, or `no-expiry-acknowledged`
- reaching a review horizon must not silently refresh, rebind, rematerialize, or revoke the subject; it should instead create or refresh a review-required state
- `renew exception`, `return to current policy`, and `keep without expiry` must remain separate reviewed verbs
- `exception review show ... --view review` should render a fixed group order: `subject and current divergence`, `why this exception exists`, `review horizon and aging`, `what horizon reach does not do`, `admissible outcomes`, `receipts and proofs`
- every row in that review view should carry one explicit aging chip such as `due-soon`, `overdue`, or `no-expiry-acknowledged`
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Renew exception`, `Return to current policy`, `Acknowledge no expiry`, `Inspect drift`) instead of collapsing back to generic `Keep` or `Reconnect`

## Approval-memory freshness and touch-renewal surfaces

Use one explicit family for long-lived remembered approval instead of expecting `approved before` or `matched prior trust` to stay honest forever on their own.

```text
anonsync approval memory freshness list --seat self --scope family-arrivals
anonsync approval memory freshness show --memory apm_01J... --seat self
anonsync approval memory touch-renew prepare --memory apm_01J... --seat self --plan
anonsync approval memory narrow prepare --memory apm_01J... --scope seat:self/photos-only --plan
anonsync approval memory freeze apm_01J...
anonsync approval memory require-fresh-next-time apm_01J...
anonsync approval memory revoke apm_01J...
```

Rules:

- every meaningful remembered-approval family that can influence later arrivals must also expose a freshness view keyed to one reviewed seat and governed scope
- every remembered-approval row must carry one explicit freshness class such as `fresh`, `warm`, `cooling`, `stale`, `frozen`, `revoked`, or `unknown`
- every non-fresh class must carry one or more visible cooling reasons rather than asking the operator to infer why trust changed
- `touch-renew` must remain a reviewed trust-memory action; it must not silently claim, bind, materialize, or widen scope
- `freeze reuse`, `require fresh approval next time`, and `revoke memory` must remain separate verbs because they preserve different amounts of historical proof and future shortcut behavior
- `approval memory freshness show ... --view review` should render a fixed group order: `remembered approval and granted scope`, `freshness evidence`, `what this memory may still do now`, `touch-renewal and narrowing options`, `freeze / require-fresh / revoke options`, `receipts and proofs`
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Touch-renew`, `Narrow scope`, `Freeze reuse`, `Require fresh approval next time`, `Revoke memory`) instead of collapsing back to generic `Keep approved` or `Approve again later`


## Approval-memory lineage and authorization-trace surfaces

Use one explicit family for later trust provenance instead of expecting `approved before` or `matched prior trust` to explain which exact old approval act is being reused.

```text
anonsync approval memory trace list --seat self --scope family-arrivals
anonsync approval memory trace show --memory apm_01J... --subject incoming:photos-2026 --seat self
anonsync approval memory trace show --memory apm_01J... --lineage
anonsync approval memory trace show --memory apm_01J... --at 2026-03-01T12:00:00Z
```

Rules:

- every meaningful remembered-approval family that can influence later arrivals must also expose a trace view keyed to one reviewed seat and governed scope
- every trace surface must preserve an origin approval act, a current lineage head, and the later nodes that superseded the origin
- any later arrival, match, or shortcut suggestion that cites remembered trust must be able to point to one explicit authorization node; if the engine cannot prove it, the posture must become `unknown`
- `approval memory trace show ... --subject ...` must render a fixed group order: `remembered approval family and current head`, `origin approval act`, `lineage mutations since origin`, `which node authorized this later subject`, `how current trust differs now`, `receipts and proofs`
- trace inspection must never silently renew trust, claim a subject, bind a path, materialize bytes, or widen scope
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Show trace`, `Inspect lineage`, `Compare with current head`) instead of collapsing back to generic `Why approved?`

## Approval-memory constellation-mutation and family-rebase surfaces

Use one explicit family for remembered approval after identity/constellation mutation instead of expecting old lineage plus current device lists to tell the whole story.

```text
anonsync approval memory rebase list --seat self --scope family-arrivals
anonsync approval memory rebase show --memory apm_01J... --seat self
anonsync approval memory rebase prepare --memory apm_01J... --event cmt_01J... --outcome split-reviewed-branches --plan
anonsync approval memory rebase prepare --memory apm_01J... --event cmt_01J... --outcome require-fresh-for-selected-descendants --descendant tablet-citrine --plan
anonsync approval memory rebase apply aprb_01J...
```

Rules:

- every meaningful remembered-approval family that can outlive identity/constellation mutation must also expose a rebase view keyed to one reviewed seat and governed scope
- every rebase surface must preserve one triggering mutation class, one current family posture, one per-descendant inheritance posture, and one next honest action
- certificate takeover, hidden-device return, and identity-epoch change must never silently keep broad remembered-trust reuse without an explicit descendant outcome
- `approval memory rebase show ... --view review` must render a fixed group order: `remembered approval family and trigger`, `what constellation or identity changed`, `which descendants still inherit what`, `what definitely does not happen automatically`, `admissible outcomes`, `receipts and proofs`
- rebase inspection and rebase outcomes must never silently renew freshness, claim a subject, bind a path, or materialize bytes
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Rebase trust family`, `Split child families`, `Require fresh for descendants`, `Freeze descendant reuse`) instead of collapsing back to generic `Keep linked approval`

## Approval-memory descendant-liveness surfaces

Use one explicit family for current descendant reachability instead of expecting trust-family membership or placeholder visibility to imply who is alive enough for present-tense convenience.

```text
anonsync approval memory descendants list --seat self --scope family-arrivals
anonsync approval memory descendants show --memory apm_01J... --seat self
anonsync approval memory descendants show --memory apm_01J... --descendant tablet-citrine
anonsync approval memory descendants refresh --memory apm_01J... --descendant tablet-citrine --outcome freeze-reuse-until-live --plan
anonsync approval memory descendants apply apdl_01J...
```

Rules:

- every meaningful remembered-trust family that can influence later arrivals must also expose a descendant-liveness view keyed to one reviewed seat and governed scope
- every descendant-liveness surface must preserve one inheritance posture, one liveness class, one confidence class, and one current honest role per descendant
- family membership, placeholder visibility, or hidden-device memory must never silently imply current byte-source availability or approval-seat availability
- `approval memory descendants show ... --view review` must render a fixed group order: `descendant identity and family posture`, `current liveness and confidence`, `what roles this descendant may honestly fill now`, `what definitely is not being claimed`, `admissible reviewed outcomes`, `receipts and proofs`
- descendant-liveness review must never silently renew trust freshness, widen scope, claim a subject, bind a path, or materialize bytes
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Record live observation`, `Freeze reuse until live`, `Mark historical only`, `Require fresh approval on return`) instead of collapsing back to generic `Keep known device`

## Approval-memory descendant-capability surfaces

Use one explicit family for per-subject descendant action eligibility instead of expecting family membership, liveness, or linked ownership to imply who may act now.

```text
anonsync approval memory capability list --seat self --scope family-arrivals
anonsync approval memory capability show --memory apm_01J... --subject incoming:photos-2026 --seat self
anonsync approval memory capability show --memory apm_01J... --subject incoming:photos-2026 --descendant desktop-ash
anonsync approval memory capability prepare --memory apm_01J... --subject incoming:photos-2026 --descendant desktop-ash --outcome require-fresh-approval --plan
anonsync approval memory capability apply apdc_01J...
```

Rules:

- every meaningful remembered-trust family that can influence later arrivals must also expose a descendant-capability view keyed to one reviewed seat and one governed subject
- every descendant-capability surface must preserve one candidate role, one eligibility class, one proof basis, and one next honest action per descendant
- family membership, current liveness, or linked ownership must never silently imply byte-source eligibility or approval-seat eligibility for the governed subject
- `approval memory capability show ... --view review` must render a fixed group order: `governed subject and descendant identity`, `candidate role and current eligibility`, `proof basis and blockers`, `what definitely is not being claimed`, `admissible reviewed outcomes`, `receipts and proofs`
- descendant-capability review must never silently renew trust freshness, widen scope, claim a subject, bind a path, materialize bytes, or approve another peer
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Record byte-source proof`, `Record approval-seat proof`, `Require fresh approval`, `Freeze subject reuse`, `Mark explanation only`) instead of collapsing back to generic `Use this device` or `Known owner`


## Approval-memory reuse-policy surfaces

Use one explicit family for subject-level approval-reuse precedence instead of expecting standing remembered approval and share/offer security settings to explain themselves.

```text
anonsync approval memory reuse-policy list --seat self --scope family-arrivals
anonsync approval memory reuse-policy show --memory apm_01J... --subject incoming:photos-2026 --seat self
anonsync approval memory reuse-policy prepare --memory apm_01J... --subject incoming:photos-2026 --outcome require-fresh-approval --plan
anonsync approval memory reuse-policy apply aprp_01J...
```

Rules:

- every meaningful governed subject that may inherit remembered approval must also expose a reuse-policy view keyed to one reviewed seat and one governed subject
- every reuse-policy surface must preserve one standing reuse candidate, one subject reuse policy, one precedence outcome, and one next honest action
- standing approval memory, descendant capability, or linked ownership must never silently override a stricter subject-level fresh-approval rule
- `approval memory reuse-policy show ... --view review` must render a fixed group order: `governed subject and standing match candidate`, `subject reuse policy and current precedence outcome`, `winning rule and blocker details`, `what definitely is not being claimed`, `admissible reviewed outcomes`, `receipts and proofs`
- reuse-policy review must never silently approve the subject, widen future trust, claim a subject, bind a path, or materialize bytes
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Show reuse policy`, `Require fresh approval`, `Allow reuse for this subject`, `Narrow to reviewed seat`, `Keep explanation only`) instead of collapsing back to generic `Already approved` or `Auto-connect trusted peer`


## Offer-artifact trust-promotion surfaces

Use one explicit family for portable invitation afterlife instead of expecting `one-time link`, `expired invite`, or `approved before` to explain whether durable remembered approval was created.

```text
anonsync offer promotion list --seat self --scope recent-claims
anonsync offer promotion show --offer off_01J... --subject incoming:photos-2026 --seat self
anonsync offer promotion prepare --offer off_01J... --subject incoming:photos-2026 --outcome keep-subject-only --plan
anonsync offer promotion apply otp_01J...
```

Rules:

- every meaningful portable invitation that can outlive its own redemption as durable remembered approval must expose a trust-promotion view keyed to one offer and one governed subject
- every trust-promotion surface must preserve one artifact-lifetime fact, one claim-outcome fact, one promotion posture, one later-reuse posture, and one next honest action
- an offer that has expired, been exhausted, or been revoked may still retain historical claim receipts, but the surface must never imply that the portable artifact remains redeemable
- a successful claim from a one-time or expiring artifact must not silently promote broader remembered approval; the promotion posture must say `subject only`, `reviewed seat only`, `family reuse candidate`, `explanation only`, or another equally explicit state
- `offer promotion show ... --view review` must render a fixed group order: `offer artifact and current redemption posture`, `claim outcome and promotion candidate`, `current durable-trust posture and later reuse posture`, `what definitely is not being claimed`, `admissible reviewed outcomes`, `receipts and proofs`
- trust-promotion review must never silently approve a new subject, widen future trust, claim a path, or materialize bytes
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Keep this subject only`, `Promote to reviewed seat only`, `Promote to family reuse candidate`, `Freeze at explanation only`, `Require fresh approval next time`) instead of collapsing back to generic `Trusted now` or `Invite used`

## Offer recipient-intent and redeemer-identity surfaces

Use one explicit family for sender intent versus actual redeemer identity instead of expecting portable-offer possession or successful approval to imply who the sender meant the artifact for.

```text
anonsync offer recipient-intent list --seat self --scope recent-offers
anonsync offer recipient-intent show --offer off_01J... --seat self
anonsync offer recipient-intent show --offer off_01J... --subject incoming:photos-2026 --claim clm_01J...
anonsync offer recipient-intent prepare --offer off_01J... --subject incoming:photos-2026 --outcome accept-subject-only --plan
anonsync offer recipient-intent apply orp_01J...
```

Rules:

- every meaningful portable offer that can be forwarded, copied, or redeemed by possession must also expose a recipient-intent view keyed to one offer, one governed subject when relevant, and one actual redemption attempt when known
- every recipient-intent surface must preserve one sender-intent posture, one actual redeemer claim, one match class, one resulting trust boundary, and one next honest action
- portable possession, successful approval, or claim success must never silently imply that the sender's original intent was satisfied
- `offer recipient-intent show ... --view review` must render a fixed group order: `offer artifact and sender intent`, `actual redeemer and proof`, `mismatch outcome and trust boundary`, `what definitely is not being claimed`, `admissible reviewed outcomes`, `receipts and proofs`
- recipient-intent review must never silently bind a path, materialize bytes, widen remembered approval, or rewrite the offer artifact's own lifetime posture beyond the reviewed outcome
- the primary verb in rich or textual surfaces should inherit the truthful intent label (`Accept for this subject only`, `Reject mismatch`, `Reissue for named recipient`, `Freeze to explanation only`) instead of collapsing back to generic `Approve` or `Accept`


## Offer redemption-ledger and multi-redeemer trust-fanout surfaces

Use one explicit family for shared artifact budget versus per-attempt trust consequence instead of expecting operators to infer those facts from raw offer history.

CLI surfaces should include:

- `anonsync offer redemption-ledger show --offer <offer>`
- `anonsync offer redemption-ledger attempts --offer <offer>`
- `anonsync offer redemption-budget explain --offer <offer>`
- `anonsync offer trust-fanout prepare --offer <offer> --attempt <attempt> --outcome <outcome> --plan`
- `anonsync offer trust-fanout apply <plan>`

Rules:

- every redemption-ledger surface must preserve one artifact budget section, one ordered attempt ledger, one per-attempt trust-fanout section, and one safe next action
- `show` output must distinguish `partially consumed` from `active` even when remaining budget is nonzero
- `attempts` output must distinguish `budget denied`, `expired denied`, and reviewed `rejected`
- `show --view review` must render a fixed group order: `artifact budget and terminal posture`, `redemption attempt ledger`, `per-attempt trust fanout`, `what definitely is not being claimed`, `admissible reviewed outcomes`, `receipts and proofs`
- when mixed attempt history exists, clients must be allowed to recommend `Reissue new artifact` instead of flattening the next action to `Keep sharing`

## Offer redemption-equivalence and slot-accounting surfaces

Use one explicit family for repeated or familiar redemption attempts instead of expecting operators to infer slot treatment from raw use-count history.

```text
anonsync offer redemption-equivalence list --seat self --scope active-offers
anonsync offer redemption-equivalence show --offer off_01J... --attempt oat_01J...
anonsync offer redemption-equivalence show --offer off_01J... --subject incoming:photos-2026 --attempt oat_01J...
anonsync offer slot-accounting prepare --offer off_01J... --attempt oat_01J... --outcome collapse-into-earlier-slot --plan
anonsync offer slot-accounting apply osa_01J...
```

Rules:

- every meaningful portable artifact with bounded or inspectable reuse must also expose a redemption-equivalence view keyed to one offer, one current attempt, and one governed subject when relevant
- every redemption-equivalence surface must preserve one remaining-budget fact, one comparison-attempt fact, one equivalence class, one slot effect, and one next honest action
- `show --view review` must render a fixed group order: `artifact budget and current attempt`, `nearest comparable earlier attempt`, `equivalence class and accounting policy`, `what definitely is not being claimed`, `admissible reviewed outcomes`, `receipts and proofs`
- replay, same-seat repeat, same-family repeat, and new-subject-known-peer cases must not collapse into one vague `already approved` phrase
- slot-accounting review must never silently widen trust, silently consume budget, or silently rewrite the artifact's accounting policy without a dedicated receipt
- the primary verb in rich or textual surfaces should inherit the truthful accounting label (`Collapse into earlier slot`, `Consume new slot`, `Require new artifact`, `Deny as replay`) instead of collapsing back to generic `Accept` or `Use link`


## Offer reissue-lineage and successor-boundary surfaces

Use one explicit family for predecessor/successor artifact boundaries instead of expecting operators to infer what `new link` means from expiry, exhaustion, or remembered approval.

```text
anonsync offer reissue-lineage list --seat self --scope active-offers
anonsync offer reissue-lineage show --predecessor off_01J... --subject incoming:photos-2026
anonsync offer reissue-lineage prepare --predecessor off_01J... --subject incoming:photos-2026 --outcome issue-narrowed-successor --plan
anonsync offer reissue-lineage apply orl_01J...
```

Rules:

- every meaningful `reissue new artifact` action must also expose a reissue-lineage view keyed to one predecessor artifact and one governed subject when relevant
- every reissue-lineage surface must preserve one predecessor posture, one successor relation, one budget reset posture, one explicit non-carry summary, and one next honest action
- `new link` must never silently imply `fresh budget island`; the budget reset posture must say `fresh budget island`, `same budget family`, `carried cap with review`, `no budget until review`, or another equally explicit state
- `reissue-lineage show ... --view review` must render a fixed group order: `predecessor posture and why it stopped being the right artifact`, `successor scope and relation to predecessor`, `budget reset and carry-forward policy`, `what definitely is not being carried forward`, `admissible reviewed outcomes`, `receipts and proofs`
- `delivery-only-encoding` must render distinctly from `issue fresh successor`
- successor-boundary review must never silently widen audience, change sender-intent posture, reset expiry/use-count, or carry mismatch outcomes forward without explicit language
- the primary verb in rich or textual surfaces should inherit the truthful lineage label (`Issue fresh successor`, `Issue narrowed successor`, `Record delivery-only copy`, `Freeze predecessor and stop`) instead of collapsing back to generic `Copy link` or `Share again`


## Revision addendum — portable-offer delivery provenance and preview authority

Portable offers can now cross multiple surfaces before the real local inspection begins.
The interface contract must therefore preserve five adjacent truths wherever one portable offer enters the product:

- `Received via`
- `Preview said`
- `External touch`
- `Parsed locally`
- `Authoritative now`

A serious interface must be able to say:

- the browser landing page showed only hint metadata
- the authority-bearing fragment stayed local during landing-page fetch
- the browser auto-launched the app because the operator had previously allowed that protocol handoff
- the local app has now parsed the artifact, but claim/trust consequences still require later review

The operator must not need packet-capture lore, browser-memory guesswork, or support history to answer those questions.


## Revision addendum — canonical artifact identity must survive carrier changes

Portable offers can now cross browser wrappers, protocol URLs, QR codes, clipboard copies, and later file wrappers without changing what the offer *is*.
The interface contract must therefore preserve five adjacent truths wherever one portable offer is seen in more than one carrier:

- `Canonical artifact`
- `Carrier observed here`
- `Other aliases`
- `Why same/not same`
- `What definitely did not change`

A serious interface must be able to say:

- the browser wrapper is only a delivery shell
- the protocol URL is an authority-bearing alias of the same offer
- the QR export is another carrier of the same canonical artifact
- none of those alias changes minted new budget or new trust lineage
- a later narrowed invitation is a successor, not just another alias

The operator must not need browser history, screenshots, or support-lore reconstruction to answer those questions.


## Revision addendum — preview-visible hints must stay adjacent to sealed and authoritative field truth

Portable offers can now keep canonical identity stable across carriers without making every field equally visible or equally authoritative.
The interface contract must therefore preserve five adjacent truths wherever one portable offer is previewed or parsed:

- `Preview hints`
- `Sealed until parse`
- `Authoritative now`
- `Later actions may rely on`
- `What definitely may not be inferred`

A serious interface must be able to say:

- the landing page or QR caption showed only recognition hints
- authority-bearing fields stayed sealed until local parse
- local parse made some fields authoritative for later alias/claim review
- those authoritative fields still may not by themselves prove approval or byte availability
- any later claim/trust/budget decision can cite the field classes it actually relied on

The operator must not need browser memory, screenshots, or support lore to answer those questions.


## Requirement 87 — previews must publish decision sufficiency, not just field visibility

If a preview can show a label, approximate size, or other recognition hint before local parse, the interface must still publish whether that preview is sufficient for recognition only, routing only, or no meaningful decision beyond `inspect locally`.

The interface should therefore preserve at least:

- preview fields shown
- omitted governance-bearing fields
- recognition sufficiency
- routing sufficiency
- governance sufficiency
- trust sufficiency
- unsafe inferences refused
- next honest action

Dense surfaces should keep `Enough for` and `Not enough for` adjacent.
No surface should let `Preview: label, size` collapse into `Ready` or `Safe to connect`.
## Offer decision-ladder surfaces

Use one explicit family for the transition from preview to local parse to claim review instead of treating those as background steps that happen around `offer show` and `claim prepare`.

Illustrative commands:

```text
anonsync offer ladder list --state active-intake
anonsync offer ladder show --delivery dev_01J...
anonsync offer ladder explain --delivery dev_01J...
anonsync offer ladder prepare --delivery dev_01J... --outcome prepare-claim --plan
anonsync offer ladder apply oldp_01J...
anonsync offer ladder receipt show oldr_01J...
```

Rules:

- the ladder is keyed to one delivery event and later canonical offer identity
- preview, parse, claim, and apply remain separate rungs
- every textual projection must preserve `current rung`, `new at this rung`, `still blocked`, `enough for`, `not enough for`, and `next honest action`
- `offer show` may inline a concise ladder view, but it must not be the only way to access ladder truth

## Portable-offer card/detail projections

GUI, TUI, and textual clients need one explicit projection for dense-row and full-pane layout truth.
The daemon object model should therefore support a portable-offer card/detail projection that keeps the following adjacent:

- what arrived
- what is visible so far
- what is missing
- what this is enough for
- what this is not enough for
- what next action is honest now

This projection is not cosmetic sugar.
It is the contract that prevents preview familiarity and parsed-policy familiarity from being mistaken for claim or approval completion.


## Revision addendum — issuance and publication explicitness

### Additional design principles

32. **Issuance is a reviewed act.**
    A sender-facing `Share` affordance may be compact, but audience, preview contract, sealed governance fields, offered role, and redemption posture must still be inspectable before issue.

33. **Constellation publication is per-subject.**
    Membership in a personal constellation may make a member eligible for publication; it does not itself explain why a specific subject is visible there.

### Additional CLI expectations

Examples:

```text
anonsync offer compose --subject workdocs
anonsync offer review draft_01J...
anonsync offer issue draft_01J... --plan
anonsync publication review --subject workdocs --to member:travel-laptop
anonsync publication apply pubplan_01J...
```

These commands should make it easy to answer:

- who an offer is for
- what a preview will show before local parse
- what stays sealed until local parse
- what role is actually being offered
- which members a subject is published to and with what arrival posture


## Revision addendum — publication matrix and role-first arrival

### Additional design principles

34. **Living publication truth is a matrix.**
    The operator must be able to inspect current subject × member publication state with explicit lineage and unresolved-local-work truth.

35. **Role precedes path and bytes.**
    Any non-trivial arrival review must choose the member's role before it chooses path or materialization posture.

### Additional CLI expectations

Examples:

```text
anonsync publication matrix --subjects work,media --members all
anonsync publication matrix show --subject family-photos --member home-nas
anonsync publication override review --subject workdocs --member travel-laptop --posture announced-only
anonsync arrival review --subject family-photos --member travel-laptop
anonsync arrival adopt --subject family-photos --member travel-laptop --role observer --path /home/ben/Pictures/family-photos --materialization placeholders --plan
```

These commands should make it easy to answer:

- why a subject is visible on one member now
- whether the cell is direct, inherited, or overridden
- what local work is still unresolved there
- what role that member may honestly adopt before any path/byte decision is made


## Revision addendum — publication-delta and member-policy explicitness

### Additional design principles

36. **Future-arrival defaults are member policy, not ambient lore.**
    The operator must be able to inspect one member's future-arrival eligibility, default roots, auto-staging posture, and exceptions without reading hidden settings or decoding one compressed mode label.

37. **Policy edits must preview affected cells.**
    Any review that can change multiple `(subject, member)` outcomes must render exact counterfactual cell deltas before apply.

### Additional CLI expectations

Examples:

```text
anonsync publication delta --subject workdocs --to member-class:laptops --posture announced-only
anonsync publication delta --template travel-defaults --plan
anonsync member policy show --member travel-laptop
anonsync member policy review --member travel-laptop --default-root /srv/stage --future-arrivals staged --plan
```

These commands should make it easy to answer:

- what one member would receive by default in the future
- which existing subjects are unaffected by a default change
- which exact cells would change if one publication or template edit were applied
- whether the proposed edit widens only visibility or also authority


## Revision addendum — publication mutation ledgers and member-policy edit drafts

Suggested commands:

```text
anonsync publication history list
anonsync publication history show --mutation pmu_01J...
anonsync publication history show --subject workdocs
anonsync publication history receipt show --mutation pmu_01J...
anonsync member policy edit prepare --member travel-laptop --field default_root --set /Vault/Travel --plan
anonsync member policy edit prepare --member archive-vps --field future_default --inherit --plan
anonsync member policy edit show --plan mpe_01J...
anonsync member policy edit apply --plan mpe_01J...
```

These commands should answer:

- what reviewed publication mutation happened recently and what delta preview justified it
- which members have observed that mutation and which still have pending local work or offline uncertainty
- what stronger claims remain outside the mutation ledger, especially retained-copy recall
- which member-policy fields are being edited, how they inherit or pin, and whether a wider delta preview is required before apply


### Member-policy impact proof and explanation commands

The CLI should expose both the pre-commit blast-radius proof and the post-apply explanation object:

```text
anonsync member-policy plan show <member_policy_edit_plan_id>
anonsync member-policy impact <member_policy_edit_plan_id>
anonsync member-policy impact <member_policy_edit_plan_id> --json
anonsync member-policy explain <member_ref>
anonsync member-policy explain <member_ref> --field arrival.default_role
```

`impact` answers whether the edit is truly future-only and, if not, which current subjects are touched.
`explain` answers why the member currently has the effective defaults it has now.

Both commands should support `--json`, `--receipt`, and `--open-related` affordances so textual and richer clients can share the same semantics.


## Revision note — causality and future simulation

This revision sharpens two more interface obligations:

- any visible `(subject, member)` cell must be explainable through one supported causality surface rather than by reconstruction from member defaults, publication history, and later outcomes
- any semantic member-policy draft must be able to preview representative future-arrival outcomes rather than asking the operator to infer them from standing mode, path-root, or template names

The operator surface therefore needs first-class commands/views for:

- `arrival explain <subject> --member <member>`
- `member-policy simulate <member> --draft <draft>`

These are not optional diagnostics.
They are part of the primary contract for avoiding Resilio-style semantics-by-defaults.


## Revision note — convergence honesty and intervention discipline

The interface contract now extends one step beyond causality and future simulation:

- any unresolved `(subject, member)` post-change gap must be classifiable through one explicit convergence-window surface rather than being left as generic `pending` state
- convergence surfaces must classify expected delay, local-prerequisite blockage, route/liveness blockage, source absence, overdue divergence, policy impossibility, and supersession without promising fake ETAs
- when materially different next moves exist, the interface must be able to render one wait-vs-intervene decision sheet with a single strongest recommendation and explicit non-recommended alternatives

Representative commands:

```text
anonsync convergence show --subject family-photos --member travel-laptop
anonsync convergence list --verdict overdue-divergence
anonsync convergence explain --window cw_01J...
anonsync intervention review --subject family-photos --member travel-laptop
anonsync intervention review --window cw_01J...
```

Additional rules:

37. **Pending is not a sufficient state label.**
    The product must say whether a gap is expected, blocked, overdue, impossible, or superseded.

38. **Wait is a first-class reviewed action.**
    The interface must be able to recommend waiting positively when current evidence still supports ordinary convergence.


## Revision note — evidence bundles and post-action recompute

The interface contract now extends one step beyond convergence classification and next-action recommendation:

- any unresolved gap that still needs evidence gathering must be inspectable through one convergence evidence bundle with live hypotheses, grouped evidence families, missing/stale separation, and bounded probe rows
- any non-trivial intervention must be recordable as a durable attempt object with explicit scope, forbidden collateral changes, outcome artifacts, and mandatory post-action recompute

Representative commands:

```text
anonsync evidence show --window cw_01J...
anonsync evidence list --primary-uncertainty route-gap
anonsync evidence export --window cw_01J...
anonsync intervention attempt start --window cw_01J... --action refresh-source
anonsync intervention attempt show ia_01J...
anonsync intervention attempt recompute ia_01J...
```

Additional rules:

39. **Missing proof, stale proof, and negative proof are distinct states.**
    The interface must not collapse them into one ambiguous `unknown` row.

40. **Interventions are not complete until truth is recomputed.**
    Any material action against a pending gap must produce a before/after verdict comparison rather than disappearing into generic activity history.


## Revision note — diagnostic probe approval and disclosure packets

This revision extends the interface contract in two more places:

- any move from ordinary evidence refresh into heavier capture must open a first-class **diagnostic probe approval** object with explicit inclusions, exclusions, intrusiveness class, auto-stop boundary, and local-only default
- any move from sealed local evidence into outside disclosure must open a first-class **external escalation packet** with recipient-specific manifest, redaction review, recall-limit warning, and disclosure receipt

Minimal CLI affordances:

```text
anonsync diagnostic probe plan --incident dgi_01J... --kind debug-log-window --for 10m --plan
anonsync diagnostic probe show dpp_01J...
anonsync diagnostic probe approve dpp_01J...
anonsync escalation packet draft --incident dgi_01J... --recipient support-vendor --plan
anonsync escalation packet show eep_01J...
anonsync escalation packet seal eep_01J...
anonsync escalation packet send eep_01J...
```


---

## Cross-surface additions from rev0122

### Effective value contract

For any non-trivial effective setting, policy field, or derived runtime choice, clients should be able to render a common row object:

- `subject_ref`
- `property_key`
- `effective_value`
- `source_state` (`baseline`, `inherits`, `pinned-local`, `exception`, `temporary-override`, `copied-static`, `computed`, `unsupported-fallback`, `unknown-drift`)
- `source_ref` nullable
- `baseline_effect_if_changed` (`would-change`, `would-not-change`, `would-require-review`, `unknown`)
- `rejoin_posture` (`already-inheriting`, `restore-inheritance-direct`, `restore-on-lease-expiry`, `requires-exception-close`, `not-applicable`, `unknown`)
- `freshness`
- `explain_ref` nullable

This object exists because the current visible value is not enough.
Operators also need to know where the value came from and whether it is still following a parent.

### Shell contract

All interactive surfaces should preserve the same conceptual regions even if layout collapses:

- navigation chooser
- subject / page scope strip
- primary list or detail pane
- proof / explain drawer
- action tray
- queue / attention context

A client may stack or collapse these regions.
It may not silently omit their semantics.

### Default landing contract

The default Home landing should show:

- all `Now` items
- `Soon` items that are near-due or newly promoted
- a collapsed summary for `Quiet`

This is a deliberate choice.
The product should not default to either maximal noise or total silence.

### Batch mutation contract

Batch direct-apply should only be permitted when all selected rows share:

- one action kind
- one scope class
- one subject family
- one risk tier
- compatible proof freshness
- no outlier blockers or warnings that would materially change a safe recommendation

Otherwise the client must split the batch or fall back to draft/review objects.


## Cross-surface additions from rev0123

### Scope-pivot editor contract

For any non-trivial value mutation, clients should be able to render a common pre-edit object:

- `subject_ref`
- `acting_seat_ref`
- `property_key`
- `current_effective_value`
- `current_source_state`
- `allowed_instruments` (`edit-baseline`, `pin-here`, `temporary-override`, `durable-exception`, `restore-inheritance`, `inspect-only`)
- `blast_radius_summary`
- `future_baseline_effect_summary`
- `next_editor_ref` nullable
- `resulting_draft_ref` nullable

This object exists because editing the field is not the first decision.
Choosing the mutation instrument is.

### Draft-object contract

For any non-trivial mutation that does not direct-apply, clients should be able to render a common draft object:

- `draft_ref`
- `action_kind`
- `scope_class`
- `risk_tier`
- `subject_count`
- `apply_groups`
- `proof_freshness`
- `outlier_groups`
- `blocked_groups`
- `predicted_receipts`
- `status` (`assembled`, `needs-proof-refresh`, `basis-stale`, `blocked-partially`, `ready-to-apply`, `applied-partially`, `applied`, `superseded`, `cancelled`)

### Projection-capability contract

Every interactive projection should declare the same semantic capability classes:

- `read-state`
- `explain-state`
- `assemble-draft`
- `review-draft`
- `apply-authorized`
- `export-proof`
- `handoff-to-other-projection`

A client may render these classes differently.
It may not silently omit them as though they were product-optional.


## Cross-surface additions from rev0147

### Approval reapproval surface contract

For any remembered approval whose basis may have changed, clients should be able to render one common reapproval object:

- `approval_memory_ref`
- `current_lineage_head_ref`
- `trigger_refs[]`
- `clock_state`
- `reuse_posture_now`
- `requested_outcome` nullable
- `effect_summary`
- `counterfactual_if_unreviewed`
- `receipt_promise`

This object exists because freshness alone is not enough once a material trigger reopens remembered trust.



### Approval coordination surface contract

For any approval-worthy subject with more than one materially relevant seat, clients should be able to render one common coordination object:

- `approval_request_ref`
- `current_basis_ref`
- `seat_roster_rows[]`
- `active_request_rows[]`
- `reviewed_current_rows[]`
- `rerequest_needed_rows[]`
- `recommended_seat_ref` nullable
- `next_honest_action`
- `receipt_promise`

This object exists because `who could act`, `who is being asked now`, and `who must be re-asked after basis drift` are not the same answer.

### Shareable-head register contract

For any retained family of shareable artifacts, clients should be able to render one common head row:

- `artifact_family_ref`
- `artifact_kind`
- `tip_refs[]`
- `operational_head_ref` nullable
- `shareable_head_ref` nullable
- `warning_codes[]`
- `recommended_open_ref` nullable
- `next_honest_action`

This object exists because `latest`, `frozen`, and `current for sharing` are not the same answer.


### External-guidance frozen-basis surface contract

For any external instruction set that may lead to a local translation, clients should be able to render one common guidance-basis object:

- `guidance_intake_ref`
- `source_rows[]`
- `snapshot_refs[]`
- `frozen_basis_rows[]`
- `translation_refs[]`
- `latest_drift_check_ref` nullable
- `review_impact` (`none`, `followup-only`, `recheck-needed`, `basis-no-longer-trustworthy`, `unknown`)
- `next_honest_action`

This object exists because `which page did this come from?`, `what exact copy did we fetch?`, `what exact excerpt did we review?`, and `is upstream still the same now?` are not the same answer.


## Cross-surface additions from rev0150

### Runtime-status bridge surface contract

For any current seat or current subject that can answer an everyday readiness / health question without opening a full incident dossier, clients should be able to render one common bridge object:

- `runtime_status_bridge_ref`
- `seat_ref`
- `surface_class`
- `runtime_owner_kind`
- `bridge_verdict`
- `bridge_probe_rows[]`
- `strongest_blocker_class`
- `current_claim_boundary`
- `recommended_escalation_ref` nullable
- `next_honest_action`

This object exists because `healthy enough for ordinary use`, `cannot inspect from here`, `skipped for a known reason`, and `needs full incident escalation` are not the same answer.

### Follow-through coverage surface contract

For any repair or unblock path that may stop at partial outside progress, clients should be able to render one common follow-through object:

- `followthrough_case_ref`
- `promised_outcome_summary`
- `coverage_state`
- `requested_step_rows[]`
- `source_execution_rows[]`
- `effect_observation_rows[]`
- `current_fix_claim`
- `remaining_required_steps[]`
- `next_honest_action`

This object exists because `requested`, `executed`, `effect observed`, and `claim-ready` are not the same truth.

### Outbound channel execution surface contract

For any frozen shareable artifact that is being moved through a delivery channel, clients should be able to render one common execution object:

- `outbound_channel_execution_ref`
- `artifact_ref`
- `artifact_kind`
- `channel_kind`
- `surface_class`
- `execution_state`
- `claim_ceiling`
- `delivery_witness_rows[]`
- `forbidden_labels[]`
- `next_honest_action`

This object exists because `artifact ready`, `copied`, `saved locally`, `share invoked`, `passed to target`, and `recipient receipt imported` are not the same answer.

### Imported recipient-acknowledgment binding surface contract

For any retained outward artifact family whose acknowledgment may arrive through email, ticket, same-product successor, or another external lane, clients should be able to render one common acknowledgment-binding object:

- `recipient_ack_binding_row_ref`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `sender_match_verdict`
- `conversation_continuity`
- `acknowledged_object_kind`
- `binding_exactness`
- `claim_ceiling`
- `stronger_proof_needed`
- `next_honest_action`

This object exists because `recipient responded`, `same thread`, `family acknowledged`, and `exact replacement acknowledged` are not the same answer.

### Imported reply-series head-register surface contract

For any retained outward artifact family whose replies may accumulate over time in email, ticket, same-product successor, or another external lane, clients should be able to render one common reply-series head-register object:

- `recipient_reply_series_row_ref`
- `artifact_family_ref`
- `target_scope_ref`
- `represented_actor_scope_ref` nullable
- `latest_arrival_ref`
- `current_whole_artifact_head_ref` nullable
- `current_subset_head_refs[]`
- `superseded_reply_refs[]`
- `parallel_live_head_refs[]`
- `head_verdict`
- `contradiction_warning`
- `stronger_resolution_needed`
- `next_honest_action`

This object exists because `newest reply`, `current whole-artifact answer`, `current subset-safe answer`, and `older blocker still live` are not the same truth.

API rule:

- clients may render these rows with different density
- clients may not silently treat the newest imported reply as the current whole-artifact answer without one explicit reply-series head register

### Imported acknowledgment authorship surface contract

For any retained outward artifact family whose acknowledgment may arrive through email, ticket, same-product successor, or another external lane, clients should be able to render one common acknowledgment-authorship object:

- `recipient_ack_authorship_row_ref`
- `artifact_family_ref`
- `target_scope_ref`
- `ack_source_ref`
- `authorship_class`
- `automation_kind`
- `human_material_presence`
- `human_proof_strength`
- `authorship_claim_ceiling`
- `stronger_human_proof_needed`
- `next_honest_action`

This object exists because `reply-shaped artifact exists`, `lane reacted automatically`, `ticket opened`, and `a human reviewed and replied` are not the same answer.

API rule:

- clients may render these rows with different density
- clients may not silently upgrade auto-replies, ticket auto-create notices, rule-authored comments, or receipt-like signals into human acknowledgment without one explicit acknowledgment-authorship row

## Cross-surface additions from rev0153

### Startup-owner surface contract

For any node whose background return posture matters, clients should be able to render one common startup-owner object:

- `startup_owner_snapshot_ref`
- `node_ref`
- `requested_startup_posture`
- `candidate_owner_rows[]`
- `effective_owner_verdict`
- `effective_owner_row_ref` nullable
- `runtime_correlation_verdict`
- `drift_state`
- `recent_receipt_ref` nullable
- `next_honest_action`

This object exists because `installed`, `service promoted`, `running now`, and `will come back correctly later` are not the same answer.


## Cross-surface additions from rev0154

### Reviewed-action basis-guard surface contract

For any reviewed draft, packet, queue-worthy action, or apply-ready mutation that may outlive one immediate click, clients should be able to render one common basis-guard object:

- `action_ref`
- `action_family`
- `expected_basis_rows[]`
- `current_basis_rows[]`
- `guard_verdict`
- `current_authority_posture`
- `stale_attempt_receipt_ref` nullable
- `reissue_path_ref` nullable
- `receipt_promise`

This object exists because `reviewed` is not the same truth as `still valid against the current basis right now`.

API rule:

- clients may render these rows with different density
- clients may not silently inherit a newer head, policy version, approval basis, or shareable artifact while still claiming parity for reviewed-action surfaces


### Reviewed recipient-target guard surface contract

For any reviewed recipient-specific or target-scoped action that may outlive one immediate send gesture, clients should be able to render one common recipient-target guard object:

- `action_ref`
- `action_family`
- `expected_target_rows[]`
- `current_target_rows[]`
- `target_comparison_verdict`
- `equivalence_rule_refs[]`
- `stale_target_receipt_ref` nullable
- `retarget_reissue_path_ref` nullable
- `receipt_promise`

This object exists because `reviewed for one recipient` is not the same truth as `still valid for the current target now`.

API rule:

- clients may render these rows with different density
- clients may not silently inherit a newer recipient, wider audience, or different disclosure target while still claiming parity for reviewed-action surfaces
- clients may not silently upgrade generic recipient response into exact object acknowledgment without one explicit acknowledgment-binding row

### Artifact disclosure-register surface contract

For any retained shareable-artifact family that may be issued to one recipient or audience over time, clients should be able to render one common disclosure-register object:

- `artifact_family_ref`
- `target_scope_ref`
- `current_shareable_head_ref` nullable
- `queued_issue_item_ref` nullable
- `last_issue_execution_ref` nullable
- `current_issued_head_ref` nullable
- `current_issued_surface_snapshot_ref` nullable
- `delivery_claim_ceiling` nullable
- `disclosure_register_verdict`
- `next_honest_action`

This object exists because `current for reuse`, `queued for send`, `executed issue`, `currently outwardly in force`, and `recipient receipt imported` are not the same truth.

API rule:

- clients may render these rows with different density
- clients may not silently promote a newer frozen head or queued issue item into `current outward surface` before a concrete execution event updates that target-scoped register

### Issued-artifact correction surface contract

For any retained outward artifact family where an already-issued artifact may later be superseded, withdrawn, or explicitly caveated for one recipient or audience, clients should be able to render one common correction-register object:

- `artifact_family_ref`
- `target_scope_ref`
- `previous_issued_head_ref` nullable
- `current_issued_head_ref` nullable
- `active_correction_notice_ref` nullable
- `replacement_issued_head_ref` nullable
- `correction_mode`
- `residual_reliance_posture`
- `correction_claim_ceiling`
- `next_honest_action`

This object exists because `we have something newer now` is not the same truth as `the older outward artifact is now understood as superseded`.

API rule:

- clients may render these rows with different density
- clients may not silently let local supersession, a newer replacement artifact, or one correction draft impersonate recipient-side interpretation or successful recall

## Revision addendum — operational list rows are part of the interface contract

The archive now treats certain list rows as first-class semantic surfaces rather than thin browse scaffolding.

The rule is:

> if a row can reasonably invite action, that row must keep the minimum truth needed to judge that action honest.

For major operational lists, this means the row must keep adjacent:

- subject identity
- present local/posture truth
- strongest risk or blocker truth
- next honest action
- stable jump to proof or review

Dense layout is allowed.
Semantic amputation is not.

## Revision addendum — page contracts for clone-veto seams after rev0165

The archive now treats four more pages as first-class public objects because they answer the strongest still-current reasons not to clone Resilio wholesale.

### Control-trust page surface contract

Clients should be able to render one common `control_trust_page` object:

- `seat_ref`
- `endpoint_rows[]`
- `control_endpoint_class`
- `listener_binding_rows[]`
- `current_trust_grade`
- `warning_cause_rows[]`
- `allowed_upgrade_paths[]`
- `temporary_exception_rows[]`
- `certificate_or_pin_rows[]`
- `latest_control_trust_receipt_ref` nullable
- `next_safest_action`

API rule:

- clients may compress wording, but may not hide current trust grade, warning cause, or next safer upgrade path behind browser chrome or external help

### Artifact-import page surface contract

Clients should be able to render one common `artifact_import_page` object:

- `seat_ref`
- `artifact_source_kind`
- `handoff_health_verdict`
- `artifact_preview_rows[]`
- `parse_confidence`
- `candidate_target_seat_rows[]`
- `consequence_preview_rows[]`
- `manual_fallback_rows[]`
- `import_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may vary density, but may not collapse malformed artifact, browser/OS handoff failure, and unsupported target runtime into one generic `could not open` verdict

### Rate-policy page surface contract

Clients should be able to render one common `rate_policy_page` object:

- `seat_ref`
- `subject_ref` nullable
- `effective_upload_cap`
- `effective_download_cap`
- `wan_cap_rows[]`
- `lan_cap_rows[]`
- `winning_policy_layer_rows[]`
- `surviving_activity_rows[]`
- `upcoming_schedule_transition_rows[]`
- `mutation_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not render `paused` as fully inert if deletions, indexing, placeholder announcements, or other side effects still proceed

### Finish-setup page surface contract

Clients should be able to render one common `finish_setup_page` object:

- `seat_ref`
- `package_trust_rows[]`
- `os_warning_rows[]`
- `consent_gate_rows[]`
- `runtime_readiness_verdict`
- `listener_exposure_rows[]`
- `control_reachability_rows[]`
- `remaining_blocker_rows[]`
- `install_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let `installed`, `service created`, or `binary copied` impersonate `ready for safe participation`

## Revision addendum — page contracts for byte/custody/lineage/fetchability seams after rev0166

### Byte-posture page surface contract

Clients should be able to render one common `byte_posture_page` object:

- `seat_ref`
- `subject_ref`
- `announcement_posture`
- `claim_posture`
- `bind_rows[]`
- `path_provenance_rows[]`
- `byte_posture`
- `fetchability_hint`
- `future_default_scope_ref`
- `future_default_rows[]`
- `collision_default_rows[]`
- `mutation_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may compress wording, but may not let one `mode` label substitute for current bind truth, current byte truth, and future-default truth together

### Encrypted-custody page surface contract

Clients should be able to render one common `encrypted_custody_page` object:

- `seat_ref`
- `subject_ref`
- `custody_class`
- `capability_rows[]`
- `hard_ceiling_rows[]`
- `restoreability_ladder_rows[]`
- `current_restoreability_rung`
- `missing_prerequisite_rows[]`
- `risk_rows[]`
- `custody_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not render ciphertext presence as if it proved plaintext recovery without explicit restoreability rows

### Same-host-lineage page surface contract

Clients should be able to render one common `same_host_lineage_page` object:

- `host_ref`
- `family_ref`
- `member_rows[]`
- `rights_ceiling_rows[]`
- `topology_verdict`
- `topology_risk_rows[]`
- `source_health_rows[]`
- `child_dependence_rows[]`
- `reattach_status`
- `lineage_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let `same machine` or `local share` stand in for explicit lineage, topology, and reattach truth

### Fetchability page surface contract

Clients should be able to render one common `fetchability_page` object:

- `seat_ref`
- `subject_ref`
- `path_ref` nullable
- `requested_action`
- `visibility_rows[]`
- `local_residency_rows[]`
- `full_copy_witness_rows[]`
- `witness_quality_verdict`
- `restore_route_rows[]`
- `risk_verdict`
- `fetchability_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let placeholder visibility, Archive presence, or stale witness hope impersonate confirmed later recoverability


## Revision addendum — page contracts for join/intake/delegation/name-plane seams after rev0167

### Identity-join page surface contract

Clients should be able to render one common `identity_join_page` object:

- `local_seat_ref`
- `remote_family_ref` nullable
- `compatibility_verdict`
- `continuity_verdict`
- `local_population_rows[]`
- `remote_family_rows[]`
- `takeover_risk_rows[]`
- `admissible_join_rows[]`
- `preserved_evidence_rows[]`
- `join_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let `link device` or `join` stand in for safe-join versus takeover versus successor-import truth

### Existing-bytes-intake page surface contract

Clients should be able to render one common `existing_bytes_intake_page` object:

- `seat_ref`
- `subject_ref`
- `target_path_ref` nullable
- `target_occupancy_verdict`
- `reuse_evidence_rows[]`
- `duplicate_risk_rows[]`
- `merge_terms_rows[]`
- `predicted_bind_class`
- `bind_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let `non-empty folder` warnings or default-path suggestions substitute for typed reuse / merge / duplicate-risk truth

### Delegation page surface contract

Clients should be able to render one common `delegation_page` object:

- `subject_ref`
- `member_ref`
- `relationship_class`
- `effective_right`
- `rights_source_rows[]`
- `rights_ceiling_rows[]`
- `onward_power_rows[]`
- `local_drift_rows[]`
- `mutation_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not compress current right, strongest ceiling, onward delegation, and local read-only drift into one unlabeled permission chip

### Name-planes page surface contract

Clients should be able to render one common `name_planes_page` object:

- `subject_ref`
- `stable_title`
- `local_label_rows[]`
- `disk_name_rows[]`
- `peer_alias_rows[]`
- `artifact_label_rows[]`
- `propagation_scope_rows[]`
- `ambiguity_rows[]`
- `name_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let one generic `name` or `rename` field substitute for stable title, local label, disk basename, and outward artifact label truth


## Revision addendum — page contracts for service-material / exclusion / delay / download-queue seams after rev0168

### Service-material page surface contract

Clients should be able to render one common `service_material_page` object:

- `subject_ref`
- `seat_ref`
- `integrity_verdict`
- `continuity_verdict`
- `material_inventory_rows[]`
- `identity_bearing_rows[]`
- `damage_origin_rows[]`
- `repair_path_rows[]`
- `preserved_evidence_rows[]`
- `repair_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let hidden runtime directories, error strings, or repair folklore stand in for typed service-material and continuity truth

### Exclusion-policy page surface contract

Clients should be able to render one common `exclusion_policy_page` object:

- `subject_ref`
- `policy_revision`
- `exclusion_verdict`
- `portability_verdict`
- `effective_rule_rows[]`
- `matching_scope_rows[]`
- `accounting_impact_rows[]`
- `divergence_rows[]`
- `simulation_rows[]`
- `policy_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let hidden rule files or raw wildcard syntax substitute for live scope, matching, and accounting truth

### Mutation-delay page surface contract

Clients should be able to render one common `mutation_delay_page` object:

- `subject_ref`
- `path_ref` nullable
- `timing_verdict`
- `delay_source_verdict`
- `effective_delay_rows[]`
- `pending_mutation_rows[]`
- `lock_risk_rows[]`
- `action_rows[]`
- `delay_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let raw config files or restart ritual stand in for file-class timing and pending-delay truth

### Download-queue page surface contract

Clients should be able to render one common `download_queue_page` object:

- `subject_ref`
- `queue_verdict`
- `priority_source_verdict`
- `effective_priority_rows[]`
- `active_execution_rows[]`
- `exception_rows[]`
- `source_of_truth_rows[]`
- `action_rows[]`
- `queue_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let visible alphabetical order or generic transfer progress masquerade as authoritative execution order


## Revision addendum — page contracts for shell-capability / byte-action / history-access / filesystem-shape seams after rev0169

### Shell-capability page surface contract

Clients should be able to render one common `shell_capability_page` object:

- `seat_ref`
- `subject_ref` nullable
- `acceleration_verdict`
- `scope_verdict`
- `action_parity_rows[]`
- `health_blocker_rows[]`
- `fallback_rows[]`
- `diagnostic_rows[]`
- `shell_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let shell extension state or absent context menus stand in for typed action-parity truth

### Byte-action review page surface contract

Clients should be able to render one common `byte_action_review_page` object:

- `subject_ref`
- `path_rows[]`
- `requested_action_family`
- `danger_verdict`
- `current_witness_rows[]`
- `after_state_rows[]`
- `alternative_action_rows[]`
- `recovery_rows[]`
- `byte_action_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not collapse local evict, local presence drop, and global destruction into one generic `remove` or placeholder gesture

### History-access page surface contract

Clients should be able to render one common `history_access_page` object:

- `subject_ref`
- `path_ref` nullable
- `retention_verdict`
- `seat_access_verdict`
- `candidate_rows[]`
- `destination_review_rows[]`
- `after_restore_rows[]`
- `expiry_rows[]`
- `history_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not let hidden Archive folders or platform-specific shortcuts substitute for typed restore-parity and candidate-stack truth

### Filesystem-shape audit page surface contract

Clients should be able to render one common `filesystem_shape_audit_page` object:

- `subject_ref`
- `target_profile_ref`
- `fidelity_verdict`
- `risk_family_rows[]`
- `affected_object_rows[]`
- `action_rows[]`
- `validation_rows[]`
- `linked_detail_rows[]`
- `shape_audit_receipt_ref` nullable
- `next_honest_action`

API rule:

- clients may not force operators to reconstruct link / metadata / invalid-name / bundle risk by reading several specialist pages before getting one rollup verdict


## Revision addendum — infrastructure visibility and state-root page families after rev0170

The core interface grammar now also owes four ordinary page families:

- **Infrastructure visibility** — one page that projects observer classes, fact classes, plaintext ceilings, narrowing paths, and receipts for a subject or host
- **Service role** — one page that projects what an outside service can observe, what it can influence, what it can never do, and how disablement/replacement changes ordinary operation
- **State root** — one page that projects the active local world, runtime principal, identity/inventory custody, and clone/shadow/snapshot risk
- **Attach state** — one page that projects attach/import classification across same-world attach, successor import, stale backup, clean branch, foreign world, and clone-risk block

These pages are not merely `Settings` drill-ins.
They answer ordinary questions that arise during privacy review, service-profile changes, recovery, and host bring-up.



## Revision addendum — helper-policy and host-cadence page families after rev0171

The public interface grammar now also owes four more ordinary page families:

1. **Helper policy** — a page that compiles subject policy, seat posture, proxy constraints, overrides, and cache residue into one effective helper verdict
2. **Bootstrap source** — a page that shows helper-catalog provenance, learned residue, freshness, and override/clearance actions
3. **Helper dependence** — a page that explains pairwise helper need, relay inevitability, and directness counterfactuals
4. **Host cadence** — a page that keeps notification coverage, rescan cadence, helper refresh, settings-save cadence, logging cost, and sleep/freshness tradeoffs together

These pages are now part of the stable page grammar rather than optional troubleshooting annexes.

## Revision addendum — capability-source, compatibility-gate, alert-delivery, and subject-kind pages after rev0172

The public interface grammar now also owes four more ordinary page families:

1. **Capability source** — a page that compiles local activation, capability provenance, remote dependence, expiry posture, and recovery paths into one effective right-to-run verdict
2. **Compatibility gate** — a page that separates full compatibility, data-only compatibility, join risk, required upgrade, and hard block across cohort layers
3. **Alert delivery** — a page that keeps event origin, carrier, permission gates, suppression, and missed-event recovery together
4. **Subject kind chooser** — a page that compares `sync`, `backup`, `send`, `ciphertext custody`, and `same-host derivation` before a creation or intake commitment

These pages are now part of the stable page grammar rather than optional licensing, support, or onboarding annexes.

## Revision addendum — health/repair page families after rev0173

The public interface grammar now also owes four more ordinary page families:

1. **Issue home** — a page that compiles symptoms into one issue family, evidence floor, safe first action, and honest escalation path
2. **Environment conflict** — a page that keeps foreign-writer risk, lock pressure, notification confidence, and safe timing/topology changes together
3. **Repair plan** — a page that orders repair rungs by copy-safety proof and environment preconditions
4. **Crash capture** — a page that keeps local artifact inventory, capture prerequisites, origin/runtime provenance, and freeze/disclosure boundaries together

These pages are now part of the stable page grammar rather than optional troubleshooting archaeology.


## Revision addendum — path continuity page families after rev0174

The public interface grammar now also owes four more ordinary page families:

1. **Share path** — a page that keeps current bind, storage/volume facts, and relocation eligibility together
2. **Relocate review** — a page that separates same-lineage move, cross-domain rebind, path repair, and peer fallout before apply
3. **Disconnected share** — a page that explains pathless presence, remembered bind history, reconnect choices, and removal scope
4. **Rename / move explanation** — a page that keeps local action class, remote expectation, replay basis, and fallback together

These pages are now part of the stable page grammar rather than optional troubleshooting or FAQ annexes.


## Revision addendum — surface parity and mobile save-back page families after rev0175

The interface grammar must now also preserve four additional page families without semantic drift:

- **Surface capability** so every seat/surface pair can publish action parity, missing verbs, and reason-coded gaps
- **External edit review** so `open in another app` can publish copy-vs-live-bind, save-back contract, and duplicate risk
- **Background delivery** so unattended freshness, suspend gates, and catch-up risk have one stable grammar
- **Mobile storage** so sandbox, downloads, cleanup matrix, and reacquireability remain one answer instead of several scattered mobile views


## Revision addendum — execution principal and host-authority page families after rev0177

The interface grammar must now also preserve four additional page families without semantic drift:

- **Execution principal** so every seat publishes the acting OS principal, launch mode, storage root, and current disk-authority rollup
- **Filesystem grant** so any managed or blocked path can publish its exact owner/group/ACL/provider basis and the strength of its write proof
- **Principal switch review** so current-user, service-account, package-user, and storage-root changes publish same-world versus successor-world consequences before apply
- **Blocked-path repair** so missing grants, repair rungs, and operation-specific retests live on one stable page instead of host-specific troubleshooting folklore


## Revision addendum — route proof, listener truth, and endpoint-claim review

The interface corpus now explicitly requires four additional ordinary pages whenever network reachability matters:

1. **Listener endpoint** — binds, advertised endpoints, ingress-proof grade, mapping mechanism, and interface selection
2. **Peer route proof** — winning route, losing candidates, helper use, blocker matrix, and better-route counterfactuals
3. **Reachability repair review** — bootstrap/discovery/direct/relay/LAN failure family, least-destructive ladder, widening cost, retest, and rollback
4. **Advertised endpoint review** — manual pins, learned claims, trust scope, freshness, conflict, and residue clear actions

These are required because helper policy alone does not answer what is live, what won, or what is safe to trust.

## Revision addendum — chronology-authority page families after rev0179

The interface corpus now explicitly requires four additional ordinary pages whenever chronology is safety-relevant:

1. **Clock authority** — local time basis, peer skew, chronology-confidence grade, and consequence/repair ladder
2. **Offline replay review** — competing timelines, authority rule in force, overwrite risk, and loser-preservation promise
3. **Mtime integrity** — disk-write success, database fallback, truth divergence, and surface impact
4. **Restore replay review** — candidate version, runtime liveness, re-archive risk, replay scope, and apply-plan receipts

These are required because `invalid time`, `mtime fallback`, `offline overwrite`, and `restore from archive` are not support-only edge cases; they are ordinary operator truths.


## Revision addendum — semantic-tradeoff page families after rev0180

The interface corpus now explicitly requires four additional ordinary pages whenever convenience or optimization changes semantic behavior:

1. **Read-only divergence** — local drift classes, suspension scope, overwrite posture, and preserve-local actions
2. **Placeholder removal** — local evict versus global delete, guardrail policy, and last-full-copy risk
3. **Hash readiness** — scan/hash ladder, semantic capability loss, preseed holdbacks, and release proof
4. **Transfer method** — winning method, interruption cost, resource profile, and better-method counterfactual

These are required because destructive convenience and hidden optimization are not advanced-user trivia; they are ordinary operator truths.


## Revision addendum — accounting truth surfaces

Any interface surface that displays a size, count, `present`, `available`, `empty`, or `cleared` label must link to:

- a **metric contract** explanation if the surface shows a number
- a **footprint** explanation if residency matters
- a **completeness confidence** explanation if the answer may be provisional
- a **service residue** explanation if hidden managed bytes still exist

Compact UI is acceptable.
Implicit semantics are not.

## Revision addendum — topology/media-fit obligations

This revision adds four more public page obligations to the interface grammar:

- every bind/adopt/create flow must be able to emit a **topology-admission** page when parent/child/disjoint/duplicate relations are not trivial
- every same-host derivative must be able to emit a **local-edge** page that preserves self-route truth, rights ceiling, source dependence, and entitlement cliffs
- every removable/provider-backed target flow must be able to emit a **provider-grant** page that distinguishes root grant proof from path choice
- every returning removable or weakly bound target must be able to emit a **removable-target continuity** page that distinguishes resume, safe rebind, guarded adopt, and recreate

These pages are now part of the interface contract rather than optional troubleshooting prose.


## Revision addendum — capability/approval page families after rev0183

The interface corpus now explicitly requires four additional ordinary pages whenever share authority is issued, received, reviewed, or changed:

1. **Share capability** — artifact family, carrier equivalence, approval model, rights ceiling, and issuance inventory
2. **Incoming share request** — requester proof, policy basis, grant consequence, and response ladder
3. **Member access** — grant origin, editability fence, future-update revocation, and residual-copy follow-up
4. **Manual claim** — intake carrier, parsed artifact family, approval-path warning, and bind consequence review

These are required because `Share`, `Approve`, `Disconnect`, `Paste`, and `Scan` are not honest semantics by themselves.

## Revision addendum — performance-observability page families after rev0185

The interface corpus now explicitly requires four additional ordinary pages whenever live performance or slowness claims appear:

1. **Activity metrics** — graph window, scope, sample basis, and counter sufficiency
2. **Peer connection table** — route class, RTT, upload/download asymmetry, and winning bottleneck attribution
3. **Disk pressure** — queue depth, Sync-vs-host load, and safe relief ladder
4. **Throughput expectation** — workload shape, relay/directness, slow-source ceiling, and realistic recovery options

These are required because `speed`, `latency`, `queue`, and `slow` are not honest semantics by themselves.


## Revision addendum — evidence-custody page families after rev0186

The interface corpus now explicitly requires four additional ordinary pages whenever observation, incident capture, evidence send, or retention comes into view:

1. **Telemetry consent** — data families, default posture, possible carriers, and retention scope
2. **Profiler capture review** — purpose, cost, restart gate, and local artifact placement
3. **Diagnostic send** — bundle membership, excluded local artifacts, redaction choices, and send receipt
4. **Local evidence retention** — inventory, storage roots, rotation / expiry, and cleanup attestation

These are required because `Enable debug logging`, `Enable profiler`, `Send logs`, and `Clear logs` are not honest semantics by themselves.



## Revision addendum — control-surface page families after rev0187

The interface corpus now explicitly requires four additional ordinary pages whenever local control is entered, widened, distrusted, or recovered:

1. **Control launch** — current surface kind, runtime owner, endpoint reached, and fast-path/fallback parity
2. **Control listener** — loopback/LAN/proxy scope, bind survivability, widening/narrowing review, and listener receipts
3. **Browser trust recovery** — warning cause, endpoint proof, temporary exception, durable fix ladder, and residue
4. **Control access recovery** — preservation-grade chooser, state-change preview, session invalidation, and continuity attestation

These are required because `open in browser`, `Allow connection from this device only`, browser warning chrome, and password reset rituals are not honest semantics by themselves.

## Revision addendum — current-surface capability and reviewed continuation

The interface contract should now treat these as first-class public objects:

- `action_availability_review`
- `surface_mismatch_review`
- `review_handoff`
- `resume_action_receipt`

Minimum expectations:

- every serious action can publish whether the current channel is `fully-supported`, `inspect-only`, `handoffable`, `blocked-by-policy`, `blocked-by-role`, `surface-degraded`, or `artifact-invalid`
- surface mismatch can publish whether the fast-path failure is `direct-link-unsupported-here`, `protocol-registration-missing`, `browser-blocked-handoff`, `browser-compatibility`, `extension-interference`, `trust-gate`, `role-or-policy`, or `artifact-invalid`
- handoff can preserve subject, review family, gate/capability reference, completed sections, expiry, and target-channel choice as durable state
- target-side resume can publish `same-review-resumed`, `same-review-after-revalidation`, `broader-review-reopened`, `resume-blocked-by-drift`, or `handoff-expired`

A missing button, hidden affordance, or successful app launch must not be the authoritative source of action truth.

## Revision addendum — namespace-convergence page families after rev0193

The interface corpus now explicitly requires four additional ordinary pages whenever names, links, or path portability can stop honest convergence:

1. **Namespace blockage** — affected path family, blockage class, auto-repair already applied, safe repair ladder, and receipt promise
2. **Conflict evidence** — counterpart map, winner/loser basis, delete-risk verdict, and preserved-copy requirement
3. **Unsupported entry** — detected entry class, target inclusion truth, fidelity verdict, and safe substitution ladder
4. **Portability repair** — failing portability classes, resulting-name previews, propagation scope, and continuity verdict

These are required because `.Conflict`, `won't sync`, `unsupported`, and `rename it` are not honest semantics by themselves.
## Revision addendum — route truth and disclosure delta page families after rev0195

The interface corpus now explicitly requires four additional ordinary pages whenever peer discovery, directness, or route widening can materially change operator trust:

1. **Reachability basis** — discovery lane, current route class, publication audience, route residue, and next least-widening action
2. **Peer route** — pairwise discovery proof, active route verdict, attempted-rung ladder, degradation reason, and next repair rung
3. **Connectivity repair** — blocker family, evidence basis, least-widening repair ladder, widening delta, and receipt promise
4. **Exposure widening review** — requested route/discovery change, new observers and facts, newly eligible route classes, residue/rollback truth, and decision verdict

These are required because `Use tracker`, `Use relay`, `Search LAN`, `known host`, and `connected` are not honest semantics by themselves.

## Revision addendum — motion-truth page families after rev0196

The interface corpus now explicitly requires four additional ordinary pages whenever quiet, slow, or wake/resume state can materially change operator trust:

1. **Motion basis** — quiet verdict, cause decomposition, hidden work lane, next proof, and least-widening action
2. **Quiet window** — zeroed lanes, surviving semantic effects, origin/expiry, and resume preview
3. **Bottleneck cause** — strongest causal class, evidence sufficiency, least-widening repair ladder, and retest plan
4. **Resume catch-up** — trigger, prerequisites, catch-up buckets, residual risks, and explicit non-effects

These are required because `Paused`, `slow`, `background`, `wake later`, and `Some internal tasks...` are not honest semantics by themselves.


## Revision addendum — subject-spine and sidecar-authority page families after rev0197

The interface corpus now needs one more ordinary page family because hidden subject state is not implementation trivia.

Add four stable page contracts:

- **Subject spine** for payload vs service-namespace and move/rehome continuity truth
- **Sidecar policy** for Ignore / Streams class policy, locality, agreement, and accounting/fidelity effects
- **Spine integrity** for continuity-bearing ID authority, duplicate-runtime conflict, and preserve-vs-recreate repair review
- **Managed hidden bytes** for Archive / inflight / fallback-stub families and safe browse vs unsafe manual mutation

These pages close another clone-veto seam: the user should never need a hidden-folder browser tab just to understand the product's own state.

## Revision addendum — release-eligibility and cohort-cutover page families after rev0198

The interface corpus now explicitly requires four additional ordinary pages whenever install or update truth can materially change operator trust:

1. **Install target** — host role, usage class, supported line matrix, block/redirect reason, and least-misleading next action
2. **Linked cohort** — seat membership, version/family skew, strongest consequence, and move-together readiness
3. **Upgrade gate** — boundary verdict, continuity-survival matrix, rollback honesty, and exact apply/stop actions
4. **Package lane** — platform/architecture fit, maintenance owner, lane-switch consequence, and continuity-preserving update ritual

These are required because `Download`, `Update`, `Install`, and `linked devices` are not honest semantics by themselves.


## Revision addendum — advanced-override and precedence page families after rev0200

The interface corpus now explicitly requires four additional ordinary pages whenever hidden low-level policy can materially change operator trust:

1. **Advanced override inventory** — active overrides, source provenance, winning precedence, shadowed controls, and apply / restart / clearance boundaries
2. **Safety override** — hidden guardrail posture, warning suppression, stop floors, and honored-vs-ignored surface truth
3. **Peer memory override** — retained peer / route facts, expiry timers, refresh cadence, and explicit clearance review
4. **Runtime bias override** — active disk / network / indexing / integrity bias, intended benefit, and side-effect budget

These are required because `Advanced preferences`, `sync.conf`, and `more options` are not honest semantics by themselves.


## Revision addendum — external recipe and postcondition page families after rev0202

The interface now needs four more ordinary page families to keep external action from collapsing back into folklore:

- **External recipe** pages that preserve source, target tuple, invasiveness, and revertibility
- **Command step** pages that preserve literal action, stop conditions, and hazard classes
- **Off-product execution** pages that preserve browser / shell / admin-lane witness without confusing it for success
- **Postcondition verification** pages that reread product truth and classify the outcome honestly

These pages should appear wherever the product suggests steps like:

- create or remove hidden local support files
- edit or place config artifacts
- stop / start / restart a runtime or service
- use browser trust / cache workarounds
- run terminal measurements or copied commands

The archive should keep this split visible rather than letting recipe execution, lane witness, and postcondition proof collapse into one generic `advanced troubleshooting` panel.

## Revision addendum — warning ownership page families after rev0203

The interface corpus now explicitly requires four additional ordinary pages whenever a material warning, degraded status, or footer/banner error appears:

1. **Warning page** — kind, claim under test, honest severity, strongest evidence, and first safe next move
2. **Blocker scope** — seat / subject / item / hidden-state / identity blast radius and unaffected neighbors
3. **Recovery rung** — least-destructive ladder, proof before escalation, continuity cost, and verification receipt
4. **Warning history** — first seen / last seen / acknowledged / suppressed / cleared-with-proof lineage and reopen conditions

These are required because `warning`, `error`, `Ignore`, `Hide`, `Retry`, and related footer strings are not honest semantics by themselves.

## Revision addendum — mobile capture-source and reacquire page families after rev0204

The interface corpus now explicitly requires four additional ordinary pages whenever a mobile seat originates, stores, or clears bytes:

1. **Capture source** — source class, delete contract, return-path truth, and source authority witness
2. **Mobile path class** — sandbox/default/custom/SD/source-only storage-class truth and admission prerequisites
3. **Capture sink** — durable-copy target, sink authority, default landing root/name, and disconnect residue
4. **Mobile reacquire** — local-clear action matrix, surviving history/receipts, and honest reacquire path

These are required because `Add Backup`, `Camera Backup`, `Choose folder`, `Downloads`, `Shared links`, and `Clear local files` are not honest semantics by themselves.

## Revision addendum — compromised-seat and cutoff page families after rev0205

The interface corpus now explicitly requires four additional ordinary pages whenever a seat is missing, stolen, or no longer trustworthy:

1. **Compromised seat** — at-rest protection posture, live-authority claim, and safest immediate action floor
2. **Containment lane** — subject-local vs cohort-wide cutoff choices, strongest non-effects, and narrowest believable lane
3. **Rotation rebuild** — trusted-survivor cohort, ordered relink / reshare / reissue sequence, and continuity boundaries
4. **Residual authority** — already-landed bytes, future-update cutoff proof, pending observation, and accepted residual risk

These are required because `offline`, `unlink`, `reinstall`, `relink`, and `start over` are not honest incident semantics by themselves.

## Revision addendum — bounded handoff page families after rev0206

The interface now needs four more ordinary page families to keep convenient file send / receive from collapsing back into folklore:

1. **Bounded handoff** — snapshot-vs-live verdict, audience ceiling, expiry contract, and reissue threshold
2. **Redemption lane** — claim method, recipient power ceiling, path-choice availability, and collision result
3. **Receive inbox** — landing root, default-owner class, fixed-vs-configurable posture, and visibility mapping
4. **Transfer history** — row family, local-byte relationship, expired-row retention, and reissue consequence

These are required because `Share file`, `Send file`, `Downloads`, `Shared links`, and `Clear transfer` are not honest semantics by themselves.


## Revision addendum — support lane and crash-custody page surface contracts

Clients should be able to render four additional common objects:

- `support_lane_page`
- `log_capture_window_page`
- `report_send_page`
- `crash_artifact_page`

Each should preserve stable reading order, reviewed-route receipts, and post-send/post-export residue truth.
The daemon/API should therefore treat support entitlement, capture activation route, packet membership, route ceilings, artifact locality, and cleanup proof as first-class read objects instead of support-note folklore.


## Revision addendum — space-pressure and reclaim-proof page families after rev0208

The interface corpus now explicitly requires four additional ordinary pages whenever local storage cost, stop floors, or reclaim are under review:

1. **Space pressure** — active floor, storage-root basis, top contributors, and safe-first ladder
2. **Byte-class inventory** — payload, history, diagnostics, control-plane state, residue, and reclaimability
3. **Reclaim preview** — expected freed bytes, explicit non-effects, retention cost, and blockers
4. **Reclaim receipt** — observed byte delta, preserved truths, weakened truths, and residual blockers

These are required because `Low disk space`, `Cleanup`, `Remove local files`, and `Done` are not honest semantics by themselves.


## Revision addendum — network-path page families after rev0209

The interface corpus now explicitly requires four additional ordinary pages whenever a subject is bound to remote or service-sensitive storage:

1. **Network path class** — local vs mounted vs UNC-under-service truth, runtime identity, and watcher grade
2. **Protocol discipline** — authoritative mutation lane, alternate lanes, corruption/rollback risk, and mitigation ladder
3. **Detection grade** — notification coverage, rescan fallback, restart sensitivity, and freshness ceiling
4. **Network subject admission** — permission fitness, lock/daemon caveats, service-identity consequence, and admit/reject receipt

These are required because `Browse`, `Folder added`, `Permission denied`, and `Sync may take some time` are not honest semantics by themselves.
