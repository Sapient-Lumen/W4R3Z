# Architecture — rev0155

## Architectural thesis

Lacuna is an epistemic custody kernel, not an LLM client, storyteller, or autonomous agent framework. Revision 0155 adds a deterministic **sidecar orchestration layer** between the existing source-bound turn packet and the existing atomic commit boundary.

The key change is architectural rather than cosmetic:

> Least-context delegation is now manufactured as exact, digest-bound role cards instead of being left as prose that a coordinator must interpret and redact correctly.

The ledger remains authoritative. Plans, task cards, worker returns, proposal preflight, and verifier opinions are read-only/advisory sidecars. They can make a host less likely to mix turns, leak privileged context, or omit a required step; none can commit state.

## Control planes

```text
player input
    ↓
turn packet (ledger mutation: exact input digest + grant + source custody)
    ↓
strict packet audit (read-only)
    ↓
orchestration plan: solo | pair | full (read-only)
    ↓
digest-bound role cards and exact JSON returns (read-only)
    ↓
packet-bound proposal + optional advisory verifier return
    ↓
parent/coordinator runs turn commit
    ↓
atomic kernel acceptance or structured refusal
    ↓
present accepted receipt narration only
```

The durable state plane is unchanged:

```text
immutable schema-1 events
    ↓ deterministic replay
schema-8 semantic projections
    ↓ access policy
perspective or planner context
    ↓ reviewed source-bound operations
atomic append or refusal
```

The orchestration plane consumes the durable plane but does not become part of it.

## System boundary

Lacuna owns:

- deterministic ledger and projection verification;
- request-source issuance and exact-head grants;
- strict packet, plan, card, and role-return exchange contracts;
- typed operation normalization and kernel validation;
- atomic commit/refusal and accepted receipts;
- access-scoped context projection; and
- replayable event custody.

The host owns:

- model/provider invocation;
- deciding whether a provider call is truly isolated;
- transcript and sidecar-file retention;
- secure/request-scoped temporary workspaces;
- model/version/tool provenance;
- choosing among worker advice;
- final proposal authorship; and
- presenting only accepted receipt narration.

## Strict packet audit

`turn plan` and every `turn card` begin by validating one complete `lacuna.turn-request.v2` object. The audit checks:

- exact field set and request schema/event identity;
- exact UTF-8 player-input SHA-256;
- cube ID and expected ledger head;
- audience and optional planner context bindings;
- audience/director access/profile agreement;
- write-grant shape and response-contract agreement;
- prebound identities and proposal-template bindings; and
- a safe default proposal with empty operations and disclosures.

This is an internal-consistency check over the supplied object. It is not a signature, trusted transport, or proof that the host obtained the packet from the claimed machine.

The canonical packet digest is SHA-256 over canonical JSON after validation. Every downstream task and return carries that digest.

## Deterministic topology selection

`./lacuna turn plan PACKET.json --mode auto` emits `lacuna.orchestration-plan.v1`.

Automatic policy is deliberately simple and inspectable:

| Packet-visible condition | Selected mode | Reason |
|---|---|---|
| audience-only packet | `solo` | no privileged hidden-state split is available |
| ordinary director packet | `pair` | separate privileged planning from audience prose |
| anchor authority, revision/repair custody, particle debt/reconciliation, or severe conflicts | `full` | separate planning, narration, serialization, and checking |

The operator may request `solo`, `pair`, or `full` explicitly. The plan records both requested and selected modes plus reasons and risk signals. It does not claim that the policy is empirically optimal.

Every selected worker stage includes:

- ordered stage number;
- role and action;
- required upstream artifact kinds;
- exact return schema;
- `may_commit: false`; and
- the exact next `turn card` command with named file placeholders.

This removes a hidden requirement that a weaker coordinator infer flags, dependencies, and filenames from prose.

## Task-card protocol

`./lacuna turn card` emits one strict `lacuna.turn-task-card.v1`. A card contains:

- deterministic `task_id`;
- role;
- turn identity and packet digest;
- ordered upstream artifact kinds/digests;
- one exact input payload;
- an explicit information boundary;
- role instructions;
- an exact JSON output schema and template;
- no commit authority; and
- nonclaims.

Task IDs are derived from:

```text
packet_sha256 + role + ordered(kind, sha256) upstream list
```

Changing the packet, role, upstream kind/order, or upstream content changes the task identity. A worker return is validated against the same derivation. Cross-turn reuse and post-card upstream edits therefore refuse instead of being silently rebound.

## Role topology and information flow

### Planner

Receives the complete audited packet, including privileged planner context when present. Returns `lacuna.planner-return.v1`:

- audience-observable plan;
- candidate operations within named grant kinds;
- preserved unknowns;
- commitment risks;
- leakage risks; and
- private notes.

The return is advice. It is not a proposal.

### Narrator

Receives only:

- exact player input and digest;
- audience identity;
- perspective-safe audience context; and
- the coordinator-approved observable plan from the exact planner return.

It does not receive the full packet, planner context, private notes, candidate operations, hidden-world diagnostics, or planner risks. It returns `lacuna.narrator-return.v1`, bound to both packet and planner-return digests.

The generated narration placeholder is fail-closed. Returning it unchanged is a structured refusal rather than a completed artifact.

### Proposal builder

Receives the fresh audited packet plus validated planner and narrator returns. Its output template is the packet’s exact source-bound `lacuna.turn-proposal.v2`, with narration from the narrator and candidate operations from the planner.

Local proposal preflight checks:

- immutable packet/proposal identity fields;
- operation/reveal cardinality limits;
- operation names against the grant; and
- canonical JSON shape.

Preflight does not run the full kernel and does not claim visibility, semantic, or commit validity.

### Verifier

Receives the exact audited packet and exact preflighted proposal. It returns `lacuna.verifier-return.v1`, bound to packet and proposal digests.

The template starts at `status: refuse` with an `unperformed-review` blocker. A return cannot claim `pass` while retaining that finding, even if its severity is cosmetically changed. A verifier pass remains advisory; only `turn commit` can accept state.

### Parent/coordinator

The parent alone:

- captures exact player input;
- issues the packet;
- chooses topology/worker advice;
- approves the observable planner material sent to narration;
- selects/writes the final proposal;
- invokes `turn commit`; and
- presents accepted top-level receipt narration.

No role card grants packet issuance, mutation, or presentation authority.

## Repeated invocations and the datacube walk

The sidecar chain does not require one long model conversation. A host may:

1. issue and save a packet;
2. generate/save a planner card;
3. call one model and save its exact return;
4. invoke the CLI again to generate a narrator card;
5. call another model and save its exact return;
6. continue through builder/verifier; and
7. commit through the parent.

Every reconstruction revalidates the packet and supplied upstream artifacts. The datacube therefore supplies deterministic context at each invocation while digests bind the sidecar chain. Lacuna does not store a durable sidecar workflow state machine; file lifecycle remains a host responsibility.

## Exchange schemas

Revision 0155 adds five Draft 2020-12 exchange schemas:

- `lacuna.orchestration-plan.v1`;
- `lacuna.turn-task-card.v1`;
- `lacuna.planner-return.v1`;
- `lacuna.narrator-return.v1`; and
- `lacuna.verifier-return.v1`.

They join, but do not change, existing `turn-request.v2`, `turn-proposal.v2`, `model-brief.v1`, change-set, campaign/library, and fair-play exchange contracts.

## Provider adapters

Codex, Claude Code, and Gemini CLI role definitions now consume the same full task-card contract. Their stable provider-specific preamble tells the role to:

- accept one complete task card;
- use only `input`;
- preserve task/request/digest bindings;
- return exactly the output template/schema object;
- refuse missing or mismatched cards;
- avoid tools, commit, and recursive delegation.

ChatGPT Project/custom-GPT instructions use the same role-card protocol. A conversation-only ChatGPT surface still lacks a local bridge; the card can be pasted into serial calls, while a human or connected host runs the CLI.

Provider files are behavioral adapters, not security boundaries. Read-only filesystem access may still expose secrets, inherited conversations may still leak context, and provider semantics may drift.

## Audit refactors

Two small API cleanups support the new layer without widening authority:

- `validate_turn_grant()` is now a public validator reused by strict packet audit;
- `Cube.has_active_agent()` is a public read-only predicate used by entrances/demos instead of private storage probing.

The CLI also uses a generic strict JSON-object reader rather than a change-set-specific private helper for all sidecar artifacts.

## Storage and migration

There is no database or event-schema change:

- database schema: **8**;
- event schema: **1**.

Plans, cards, and role returns are not events. Existing schema-8 cubes remain directly usable, and existing schema 1–7 migration custody is unchanged.

## Failure semantics

The sidecar layer fails closed on, among other cases:

- malformed or internally inconsistent packets;
- player-input digest mismatch;
- context/head/profile/grant/template mismatch;
- unknown mode or role;
- missing/unexpected upstream artifacts;
- edited or cross-turn worker returns;
- ungranted candidate/proposal operation names;
- unchanged narration template;
- verifier pass with a blocker or `unperformed-review` finding; and
- proposal identity drift.

No sidecar failure partially mutates the cube because sidecar commands are read-only. Ordinary packet issuance and final commit retain their existing atomic ledger semantics.

## Deliberate limits

Revision 0155 does not provide:

- actual model or subagent invocation;
- provider-independent hard context isolation;
- semantic proof that an observable plan contains no hidden rationale;
- model-quality or topology-optimality guarantees;
- request-scoped concurrent sidecar directories or cleanup;
- transcript/sidecar body custody in the ledger;
- authoritative verifier verdicts;
- checkpoint candidate generation, rollout, scoring, or compression;
- scenario-capsule execution or live cross-provider evaluation; or
- signatures, trusted time, or hostile-host non-equivocation.

The contribution is narrower: exact, inspectable information-flow contracts around an unchanged authoritative kernel.
