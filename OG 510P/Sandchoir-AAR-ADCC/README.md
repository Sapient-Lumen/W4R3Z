# Sandchoir / AAR–ADCC

## Help a small group notice what matters next

Sandchoir designs cooperation for a handful of local command-line agents that cannot be assumed to read everything, finish every response or receive equally many opportunities to inspect shared state. Its question is not simply how to run more workers. It is how to make their next limited encounter with a project useful: the human's priority, a changed patch, a relevant objection, and enough context to act without rereading the whole conversation.

The Adaptive Attention Router (**AAR**) composes those views. The Adaptive Deliberation Control Conduit (**ADCC**) governs proposals, ownership, disputes and changes to the canonical workspace. A separate MetaLLM steward adjusts small operational levers, while a human-facing “gearbox” makes control explicit. The [charter](versions/v0.19/files/aar_adcc_specs_v0_19/00_charter.md) favors diverging proposals followed by selection over prolonged discussion until everyone sounds agreed.

The supplied v0.19 is a design work: eighty preserved Markdown members, including contracts, schemas described in prose, pseudocode, prompts, playbooks and a phased build plan. It is not a supplied working Rust router or a record of completed multiagent trials. The specifications are substantial because they expose the intermediate decisions an implementation would have to make.

## A small working set beside a large record

The [working-set schema](versions/v0.19/files/aar_adcc_specs_v0_19/02_ws_object_schema.md) separates a strict, bounded blackboard from a permissive Ledger. A claim, task, patch, evidence card, counterexample or directed request receives an ID, status and links to related objects. Long prose and raw logs stay in the Ledger; the working set holds compact structured content and pointers.

That split serves two uses at once. Workers can orient themselves without consuming a transcript, while a reader investigating a decision can follow its references back to fuller material. A summary is not a replacement truth: its proposed fields include what it covers, decisions retained and material evicted. Human priority, H0, is a special object placed first rather than competing with every other item's popularity.

The [event/delta design](versions/v0.19/files/aar_adcc_specs_v0_19/31_event_log_and_delta_semantics.md) increments a cursor when working state changes. A worker reports its last-seen cursor and normally receives bounded changes rather than a complete refresh. Bootstrap and recovery can request more. The document anticipates repeats and missing deltas instead of promising exactly-once delivery. A cursor organizes the record of state exposure; it is not proof that a model understood every item.

## A view is a selection that should explain its omissions

The [view contract](versions/v0.19/files/aar_adcc_specs_v0_19/47_view_assembly_and_token_budgeting_contract.md) orders human priority, mandatory events, globally prominent items, changes, role-specific material, controlled discovery and occasional random discovery. Item counts and line caps are primary controls; an optional character-based token estimate is a rough guard, not a measured cross-model tokenizer.

Mandatory event headers retain priority even when bodies must be shortened. Role subscriptions are selected from a menu rather than letting every participant invent a separate routing policy. Directed requests go to the relevant recipient instead of automatically becoming everybody's urgent business.

The [routing pseudocode](versions/v0.19/files/aar_adcc_specs_v0_19/58_aar_routing_pseudocode.md) also asks for suppression diagnostics: which IDs were omitted for budget or policy reasons? That makes selection inspectable. A worker not discussing an objection might never have received it; “why didn't I see this?” is a routing question before it is evidence of agreement.

The [exploration proposal](versions/v0.19/files/aar_adcc_specs_v0_19/46_controlled_exploration_policy.md) reserves at most two optional slots for neglected but actionable material. An uncertain claim or a task stuck outside the hot list can re-enter attention. These slots do not themselves authorize edits and yield when the budget is tight. The intended benefit is avoiding a self-reinforcing hot list, not randomizing the whole project.

## Preserve a useful beginning when the rest is cut off

The [Boot Compression Contract](versions/v0.19/files/aar_adcc_specs_v0_19/01_bcc_wire_format.md) asks a worker to put a compact control header first: its cursor, completion posture, touched scope and next need. Sparse votes, proposals and artifact pointers follow; longer notes come last. The ordering is the point. A truncated response can still disclose where the worker thinks it is and what should happen next.

The [streaming-parser design](versions/v0.19/files/aar_adcc_specs_v0_19/74_streaming_parser_and_ctrl_capture.md) scans a bounded recent buffer for that header rather than attempting to interpret arbitrary JSON anywhere in the response. Local repair precedes an expensive re-ask; the boot contract permits at most one bounded header-only re-ask per slice. Failed repair leaves material in the Ledger rather than promoting it into shared structured state.

These are proposals for robust transport, not semantic validation. Making a header parse does not make its claim true or its requested action authorized. The [measurement plan](versions/v0.19/files/aar_adcc_specs_v0_19/71_cli_client_cap_probing_and_slice_measurement.md) therefore uses observable signals such as time to the first control header, output length and repair rate. It does not claim access to a client's hidden internal turns.

## From a contested patch to an accountable decision

An illustrative journey through the specifications makes the role split concrete. One worker proposes patch P7 and identifies the files it touches. Another offers counterexample CE4 against a claim supporting P7. The counterexample must name a witness, a reproduction recipe and an expected signal; simply objecting more loudly is not enough to enter the proposed certification path.

Under the [counterexample playbook](versions/v0.19/files/aar_adcc_specs_v0_19/65_counterexample_certification_playbook.md), attention or check-budget votes can fund an attempt to replay it. A resulting evidence card records what ran, what happened and what the result bears on. The playbook calls one successful replay certification level1, with stronger levels for stability and minimization. That local status does not turn a test into a universal proof or establish that two replaying agents are independent witnesses.

A certified counterexample becomes prominent. In the playbook's Gatekeeper workflow, the integrator must address it with a resolving patch or an evidenced explanation, while the human can inspect the selected patch and the decision record. The [patch-lane proposal](versions/v0.19/files/aar_adcc_specs_v0_19/70_patch_lane_git_apply_3way_and_rerere.md) separates authorship from application: workers export diffs; an integrator applies them to a clean canonical worktree, handles conflicts and runs cheap checks. Stale patches return for a fresh export instead of being treated as current just because their authors still support them.

The architecture distinguishes three scarce things: what receives attention, what receives execution budget, and what becomes canonical. A vote may allocate those opportunities. It cannot establish truth by popularity.

## Steering rather than silently escalating

The [governance chapter](versions/v0.19/files/aar_adcc_specs_v0_19/06_adcc_governance.md) varies enforcement through modes, a strictness ladder and soft or hard leases. A mode change alters how the group may work; a worker's confidence is not itself that change. The later [machine-usable CLI contract](versions/v0.19/files/aar_adcc_specs_v0_19/79_router_cli_contract.md) gives state inspection and small control actions human-readable and JSON forms, so a steward can inspect telemetry, request compaction, select a check or propose a mode change without rewriting the kernel.

The [backpressure design](versions/v0.19/files/aar_adcc_specs_v0_19/76_backpressure_delta_coalescing_and_drop_policy.md) extends this concern to queues. It proposes bounded channels, coalesced deltas and preferential removal of low-priority telemetry, with control and critical state changes protected. Shrinking a view or pausing changes can be preferable to allowing an unread queue to grow without limit.

The [experiment proposal](versions/v0.19/files/aar_adcc_specs_v0_19/80_experiment_runner_and_ab_testing.md) would compare a few variants from a common snapshot: view budgets, exploration, header-first parsing or stopping after the header. Its metrics include parse success, evidence production, applied patches and deadlock time. Those are proposed observations to collect, not reported improvements.

## Read the seams as design questions

The documents do not yet form one fully reconciled protocol. Earlier governance names Recorder and Jailer; the later mode matrix and CLI use Normal and Recovery alongside shared modes. The view contract and routing pseudocode differ on which optional section is removed first. Mandatory-header preservation also needs an implementation rule for a burst of mandatory events larger than the available view.

Evidence governance has a related tension: the early chapter permits expensive override of contradicted claims, while the later playbook says voting must not become a license to ignore evidence. A serious implementation would need to specify how a claim can remain recorded, a patch can be selected, and an objection can remain unresolved without conflating those states.

These seams do not erase the work's central insight. Coordination needs a legible account of attention, omissions, evidence and authority, not just more messages. The [minimal build plan](versions/v0.19/files/aar_adcc_specs_v0_19/57_minimal_build_plan.md) turns that insight into stages: persistence, bounded parsing/views, real terminal integration, patch application, evidence and finally richer steering. Its acceptance thresholds are proposed tests, not achievements.

Read beside [DelayBasin](../DelayBasin/README.md) for continuation under partial observation, [Goldenrule](../Goldenrule/README.md) for the gap between an allocation rule and what it is meant to serve, and [The Overseer](../../Overseer/README.md) for a different, source-bearing construction of bounded work and recovery. These are neighboring approaches, not one shared runtime.

## Version shelf and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [v0.19](versions/v0.19/README.md): 80 preserved members; `sandchoir-aar_adcc_specs_v0_19.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
