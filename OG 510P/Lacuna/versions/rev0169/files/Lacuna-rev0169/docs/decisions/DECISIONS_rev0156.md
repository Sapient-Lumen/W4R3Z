# Decisions — rev0156

## D-0156-01 — add a request-scoped sidecar run

**Decision:** retain one turn’s exact input, packet, plan, staged cards/returns, proposal, verifier result, receipt, and status in a dedicated directory.

**Reason:** rev0155 could bind individual handoffs but required the coordinator to remember workflow state across model and CLI invocations.

**Consequence:** a later invocation can resume from one path and audit the entire chain without conversation memory.

## D-0156-02 — keep the run outside the event ledger

**Decision:** `lacuna.turn-run.v1` is a host sidecar, not a new durable event or projection.

**Reason:** prompts, rejected returns, provider routing, and workflow progress are useful custody but are not all semantic world state.

**Consequence:** database schema 8 and event schema 1 remain unchanged; run retention/privacy are host responsibilities.

## D-0156-03 — expose four public run operations

**Decision:** the normal interface is `begin`, `status`, `accept`, and `commit`.

**Reason:** a small state machine is easier for humans and weaker models to follow than a remembered packet/plan/card command chain.

**Consequence:** lower-level commands remain inspectable expert substrate, but active entrances converge on the run protocol.

## D-0156-04 — `run.json` is authoritative and `NEXT.md` is derived

**Decision:** machine state lives in a strict manifest; the human-readable next action is deterministically rendered and audited byte-for-byte.

**Reason:** models are likely to follow the legible pointer, so pointer tampering or drift must fail closed.

**Consequence:** hand-editing `NEXT.md` never changes the valid next action and instead blocks advancement until repaired from authoritative state.

## D-0156-05 — every state has one owner, one complete input, and one expected schema

**Decision:** `next_action` names exactly one owner, artifact path, return schema, command, and player-visibility rule.

**Reason:** multiple candidate files or implicit role selection disproportionately burden less capable models.

**Consequence:** the parent no longer needs to synthesize a role prompt or infer stage flags.

## D-0156-06 — preserve exact player text through a file boundary

**Decision:** implement mutually exclusive inline/file input, with `-` for standard input, and retain the exact decoded UTF-8 text in `00-player-input.txt`.

**Reason:** shell quoting, newlines, CRLF, and metacharacters should not be reinterpreted while entering a governed turn.

**Consequence:** text, packet body, and digest are audited for equality; arbitrary JSON formatting is not claimed as byte-exact custody.

## D-0156-07 — use canonical parsed-JSON digests for sidecar artifacts

**Decision:** hash canonical JSON values rather than raw file bytes.

**Reason:** object key order and insignificant whitespace should not create different semantic artifacts.

**Consequence:** digests prove continuity of parsed JSON under Lacuna’s canonicalization, not preservation of provider output formatting or remote authorship.

## D-0156-08 — enforce an exact artifact topology per state

**Decision:** every possible artifact has a fixed filename/metadata slot, and audit requires exactly the set allowed by topology and status.

**Reason:** a valid future-stage file, stale return, relabelled role, or hidden extra artifact can misdirect a coordinator even when individual schemas are valid.

**Consequence:** missing, unexpected, cross-stage, and metadata-substituted artifacts refuse.

## D-0156-09 — retain deterministic topology selection

**Decision:** continue using rev0155’s explicit packet-visible `solo`, `pair`, and `full` selection; store both requested and selected modes.

**Reason:** workflow storage should not introduce a new opaque policy or let a model silently escalate its own topology.

**Consequence:** manual overrides remain inspectable and `auto` remains reproducible.

## D-0156-10 — make safe drafts parent-owned

**Decision:** solo and pair proposal drafts use the packet-bound template, empty operations, empty reveals, and either the fail-closed placeholder or accepted narrator text.

**Reason:** a draft should be usable without inventing durable facts and must not look like model authority.

**Consequence:** the parent reviews/finishes these drafts; a full-mode builder return is separately labelled as builder-produced.

## D-0156-11 — reject the unchanged narration placeholder at the run boundary

**Decision:** final proposal acceptance refuses the exact fail-closed placeholder.

**Reason:** a literal model can return a structurally valid template without doing the work.

**Consequence:** both direct and run-mediated turn paths require actual narration before readiness.

## D-0156-12 — wrong-stage JSON refuses before role-specific validation

**Decision:** `accept` first compares the submitted root schema with the current expected schema.

**Reason:** a well-formed planner return is still invalid when the run expects a narrator or proposal.

**Consequence:** state transitions are explicit and accidental cross-stage reuse cannot be normalized into acceptance.

## D-0156-13 — a full-run verifier refusal closes the v1 run

**Decision:** `verifier-refused` has no in-place proposal-replacement transition.

**Reason:** overwriting the rejected chain would weaken audit custody and complicate version-1 state semantics.

**Consequence:** the parent inspects findings and begins a fresh run from the retained exact input.

## D-0156-14 — only the parent advances or commits

**Decision:** generated role actions return JSON only; checked-in workers forbid run control and commit.

**Reason:** least-context workers should not acquire authority merely because they can produce a valid artifact.

**Consequence:** subagents remain advisory; the parent owns acceptance, review, kernel commit, and player presentation.

## D-0156-15 — emit provider aliases in generated operational context

**Decision:** model briefs and delegated next actions map portable roles to Codex underscores, Claude/Gemini hyphens, and role-dedicated ChatGPT contexts.

**Reason:** provider naming differences are a practical source of failure for fresh coordinators.

**Consequence:** the cube can prompt the parent to invoke the appropriate role without making provider invocation part of the kernel.

## D-0156-16 — provider configuration is a preamble, not the per-turn prompt

**Decision:** native agent files contain stable role/authority constraints; the complete generated task card contains the actual turn data and exact output template.

**Reason:** hand-written provider prompts drift and tempt the coordinator to summarize or leak privileged input.

**Consequence:** adapter failure can downgrade to serial contexts while preserving the portable card protocol.

## D-0156-17 — ordinary ChatGPT may start play but must not fake persistence

**Decision:** “Will you DM?” begins or resumes play; without a bridge, ChatGPT discloses once that the chat is not yet committed to a Lacuna cube.

**Reason:** player usability and capability honesty are both necessary. Requiring CLI knowledge is bad UX; claiming local mutation is false.

**Consequence:** documentation distinguishes conversation-only, human bridge, bounded-role, and connected-host paths.

## D-0156-18 — do not include planner context in receipts by default

**Decision:** generated run entrances omit `--include-planner-context`; it remains an explicit operator option.

**Reason:** routine receipt enrichment would undermine least-context and expose privileged planning material after every turn.

**Consequence:** accepted narration remains easy to present while privileged receipt context requires deliberate authorization.

## D-0156-19 — describe provider separation as bounded context, not hard isolation

**Decision:** documentation uses capability-specific language and records provider isolation as a nonclaim.

**Reason:** prompt files, separate conversations, read-only sandboxes, and empty tool lists do not prove provider-internal noninterference or confidentiality.

**Consequence:** experiments can study practical leakage without overstating their security boundary.

## D-0156-20 — accept absolute-path, sequential v1 semantics explicitly

**Decision:** version 1 records absolute run/cube paths and assumes one parent advances a run at a time.

**Reason:** relocation and locking require additional identity/recovery design and should not be implied by local atomic file writes.

**Consequence:** moving runs/cubes or concurrent same-run writers is unsupported and documented as such.

## D-0156-21 — document begin and commit crash windows

**Decision:** do not claim a distributed transaction between SQLite and sidecar files.

**Reason:** request creation can precede complete run creation, and kernel commit can precede receipt/manifest persistence.

**Consequence:** operators must inspect identity/state before recovery; future work can add explicit idempotent recovery records.

## D-0156-22 — frame the Gwern gift as governance plus experiment design

**Decision:** state that Lacuna answers the commitment-budget and custody problem, while candidate generation, rollout, scoring, compression, and empirical quality evidence remain external.

**Reason:** this is both the strongest genuine contribution and the most falsifiable framing.

**Consequence:** the docs propose a forward-only/prompt-retcon/pair/full study instead of claiming success from architecture alone.

## D-0156-23 — treat model-facing documentation as tested interface

**Decision:** provider tests now enforce the run entrance, `NEXT.md`, human/connected bridge honesty, exact proposal/receipt shapes, and current provider mapping.

**Reason:** the prior bridge documented a nonexistent CLI flag, proving that prose drift is an executable defect.

**Consequence:** documentation and adapters are reviewed alongside source and exchange schemas.

## D-0156-24 — no database or event-schema bump

**Decision:** retain database schema 8 and event schema 1; add only `turn-run.v1` and extend `model-brief.v1` with provider aliases.

**Reason:** the revision changes host workflow custody, not durable semantic event meaning.

**Consequence:** existing schema-8 cubes remain directly compatible.
