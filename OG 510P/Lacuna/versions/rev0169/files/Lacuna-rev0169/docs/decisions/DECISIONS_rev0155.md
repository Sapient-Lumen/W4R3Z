# Decisions — rev0155

## D-0155-01 — orchestration remains a sidecar, not ledger state

**Decision:** plans, task cards, worker returns, proposal preflight, and verifier returns are read-only exchange artifacts.

**Reason:** model workflow is host policy. Recording every attempted delegation as canon would confuse execution telemetry with world custody and require unnecessary schema mutation.

**Consequence:** only packet issuance and accepted `turn commit` mutate the cube. Hosts retain sidecar files externally when reproducibility matters.

## D-0155-02 — audit the complete packet before any fan-out

**Decision:** every plan/card constructor strictly validates the exact turn packet first.

**Reason:** distributing an internally inconsistent packet multiplies an upstream defect across workers and makes failures difficult to attribute.

**Consequence:** input digest, context/head binding, access/grant agreement, response contract, and safe template must all pass before role-specific data is emitted.

## D-0155-03 — canonical JSON SHA-256 binds sidecar continuity

**Decision:** compute packet and upstream artifact digests over canonical JSON.

**Reason:** repeated CLI/model invocations need a deterministic identity independent of whitespace or key order.

**Consequence:** edited or cross-turn objects change task bindings. The digest is not a signature, host authentication, or semantic certificate.

## D-0155-04 — automatic topology uses only explicit packet-visible signals

**Decision:** `auto` selects `solo`, `pair`, or `full` from access mode and explicit high-impact custody indicators.

**Reason:** hidden heuristics or model self-assessment would make the route irreproducible and difficult to audit.

**Consequence:** selection reasons and risk summaries are emitted. The policy may be empirically revised without changing ledger semantics.

## D-0155-05 — manual topology overrides remain visible

**Decision:** permit explicit `--mode solo|pair|full` and record requested versus selected mode.

**Reason:** operators and experiments need controlled ablations, and no static auto policy is universally optimal.

**Consequence:** override is transparent rather than silently changing the chain.

## D-0155-06 — task identity binds packet, role, and ordered upstream artifacts

**Decision:** derive each `task_id` from packet SHA-256, role, and ordered `(kind, sha256)` upstream list.

**Reason:** a role label alone cannot distinguish turns or pre/post-edit versions of an artifact.

**Consequence:** downstream returns refuse after upstream edits, swaps, or ordering changes.

## D-0155-07 — narrator least-context input is manufactured

**Decision:** generate the narrator input from exact player data, audience context, and approved observable planner beats only.

**Reason:** asking a coordinator to redact a privileged packet is an error-prone policy suggestion, not an enforceable interface.

**Consequence:** full packet, planner context, candidate operations, private notes, and risks are absent from the card by construction. Semantic leakage through an overbroad observable plan remains possible.

## D-0155-08 — the observable plan is the coordinator-approved transit boundary

**Decision:** only `planner_return.observable_plan` crosses into the narrator card.

**Reason:** the parent must retain editorial responsibility for what privileged reasoning is safe to translate into audience-visible beats.

**Consequence:** Lacuna can bound the field but cannot prove that its natural-language contents contain no hidden rationale.

## D-0155-09 — provider workers return exact JSON, not provider-specific headings

**Decision:** all native role adapters consume a complete task card and return one object matching its `output_contract`.

**Reason:** prose headings and bespoke provider formats cannot participate reliably in a digest-bound cross-provider chain.

**Consequence:** stable provider preambles become thin adapters; the portable task card is the authoritative worker prompt contract.

## D-0155-10 — proposal preflight is deliberately weaker than commit validation

**Decision:** sidecar preflight checks packet identity, grant names, and cardinality, but does not claim kernel acceptance.

**Reason:** early diagnostics help builders/verifiers without duplicating or drifting from authoritative commit semantics.

**Consequence:** only `turn commit` validates visibility, references, state-dependent invariants, and atomic mutation.

## D-0155-11 — verifier templates fail closed

**Decision:** verifier output starts at `refuse` with an `unperformed-review` blocker; `pass` cannot retain that finding.

**Reason:** a literal model may return an output template unchanged or change only one conspicuous field.

**Consequence:** completion requires an explicit review artifact. A pass remains advisory.

## D-0155-12 — narrator templates also fail closed

**Decision:** reject the unchanged narration instruction sentinel as a narrator return.

**Reason:** valid JSON Schema alone cannot distinguish a completed narration from a copied template.

**Consequence:** a worker must supply actual audience prose before the chain can advance.

## D-0155-13 — packet issuance and commit remain parent-only

**Decision:** no role card authorizes `turn packet`, `turn commit`, accepted-file selection, or player presentation.

**Reason:** centralizing authority preserves stale-head handling, grant review, and receipt custody.

**Consequence:** subagents provide bounded artifacts only; the coordinator owns all mutation and display decisions.

## D-0155-14 — each selected stage emits its exact next command

**Decision:** add nullable `card_command` to every plan stage; worker stages contain complete CLI command templates and required upstream filenames.

**Reason:** role selection without operational invocation still forces weaker coordinators to infer flags and dependency order.

**Consequence:** the plan is directly walkable. Hosts replace only named file placeholders.

## D-0155-15 — repeated invocations are digest-linked, not workflow-stored

**Decision:** allow each card to be generated in a later CLI process from packet and exact upstream files, without writing workflow state to the cube.

**Reason:** deterministic reconstruction supports cross-model experiments while keeping orchestration policy outside the kernel.

**Consequence:** hosts must retain and lifecycle-manage sidecars; missing files are not recoverable from ledger events alone.

## D-0155-16 — provider prompt separation is not hard isolation

**Decision:** describe provider role files as behavioral context only.

**Reason:** provider runtimes may share memory, logs, or readable files, and configuration semantics may drift.

**Consequence:** secrets remain outside readable workspaces unless the host supplies a real isolation boundary.

## D-0155-17 — fixed temporary filenames are sequential examples

**Decision:** retain legible example filenames while explicitly deferring a request-scoped workspace protocol.

**Reason:** the current entrance optimizes for one local turn and human comprehensibility; silently implying concurrency safety would be false.

**Consequence:** concurrent hosts must create per-request directories and cleanup policy externally.

## D-0155-18 — ChatGPT uses the same card protocol without assuming Codex-style subagents

**Decision:** document conversation, Project/custom-GPT, human-bridge, connected-host, and single-role-card paths separately.

**Reason:** product labels do not imply shell access or a programmable subagent runtime.

**Consequence:** ChatGPT may execute cards in serial calls, while a human/host runs local commands. No Pro-subscription capability is invented.

## D-0155-19 — expose public read-only helpers instead of private storage probing

**Decision:** make `validate_turn_grant()` and `Cube.has_active_agent()` public and generalize CLI JSON-object reading.

**Reason:** entrance/orchestration code should not depend on private implementation details or change-set-specific readers.

**Consequence:** behavior is easier to test and reuse without widening mutation authority.

## D-0155-20 — no database or event-schema bump

**Decision:** retain database schema 8 and event schema 1; add five exchange schemas only.

**Reason:** sidecar orchestration does not change durable event semantics or projections.

**Consequence:** existing schema-8 cubes remain directly compatible and migration lineage is unchanged.

## D-0155-21 — documentation is part of the model-facing interface

**Decision:** test generated plan commands, provider card contracts, schema validity, narrator firewall, and refusal semantics alongside code.

**Reason:** a model follows operator text and adapter files as executable guidance; drift there is a protocol defect.

**Consequence:** rev0155 acceptance includes dedicated orchestration, model-entrance, provider, and exchange-schema suites.
