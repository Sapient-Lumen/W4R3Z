# Decisions — rev0158

## D158-01 — Type session control instead of inferring it downstream

**Decision.** Add `input_kind` to request v3 and source protocol v2 with exactly `session-control` and `play-turn`.

**Reason.** “Will you DM?” and “I open the door” have different operational meanings even when both are untrusted exact user text. The distinction must survive repeated model and CLI invocations.

**Consequence.** New hosts declare the kind at issuance. Historical v2 requests remain valid and default to `play-turn`; no old record is rewritten.

## D158-02 — Make one-sentence start an executable composition

**Decision.** Add `play start` above existing campaign resolution and turn-run creation rather than teaching each model a shell ritual.

**Reason.** Hyperlegibility requires removing predictable coordination work, especially for weaker models.

**Consequence.** The command may bootstrap only an absent/empty path and may select only an unambiguous campaign. It invokes no model and creates no fictional fact.

## D158-03 — Map capability profiles to topology, not provider brands

**Decision.** `chat` and `workspace` start in solo mode; `orchestrated` uses deterministic auto selection.

**Reason.** The relevant question is whether a parent can manufacture bounded worker contexts, not which logo appears on the model.

**Consequence.** Provider adapters remain optional routing conveniences. A host downgrades honestly when subagents are unavailable.

## D158-04 — Embed the exact card in every portable dispatch

**Decision.** `lacuna.agent-dispatch.v1` carries the complete task card as `input_document`, not merely a path and digest.

**Reason.** Remote chats cannot be assumed to read local files, and path-only handoffs invite prompt reconstruction and context widening.

**Consequence.** Envelopes are larger but self-contained. The retained path/digest still anchors the embedded object to the audited run.

## D158-05 — Keep provider routing outside authority

**Decision.** Provider and alias fields select a destination context only. They do not authorize mutation or attest identity/isolation.

**Reason.** Codex, Claude Code, Gemini CLI, ChatGPT, API calls, and humans can all consume the same semantic card while their execution guarantees differ.

**Consequence.** The parent always saves and accepts the return. Only the kernel can commit.

## D158-06 — Refuse dispatch from parent-owned states

**Decision.** Generate dispatches only for planner, narrator, proposal-builder, and verifier states.

**Reason.** A universal “send next thing to a model” command would blur parent review/serialization authority and let workers accept their own work.

**Consequence.** Solo/pair proposal review, recovery, preparation, commit, and presentation remain explicit parent actions.

## D158-07 — Centralize authoritative member reads behind descriptor verification

**Decision.** All run JSON/text readers use one bounded descriptor-stable primitive.

**Reason.** Digest validation without file-identity validation can authenticate bytes from an unintended linked or substituted object.

**Consequence.** Single-link regular files are required, with a 16 MiB read bound. This is local integrity hardening, not hostile-host security.

## D158-08 — Treat `NEXT.md` as replaceable derived state

**Decision.** Allow explicit recovery to regenerate only `NEXT.md` after authoritative audit.

**Reason.** The pointer is deterministic and useful, but making it irreparable encourages hand edits or needless abandonment.

**Consequence.** Ordinary audit remains strict. Recovery cannot reconstruct or alter authoritative members.

## D158-09 — Preserve exact historical receipt recovery

**Decision.** Pointer recovery is additive and must not simplify rev0157’s later-head post-commit recovery.

**Reason.** The two mechanisms solve different failure classes: a derived file versus a split durability window after an actual ledger commit.

**Consequence.** Receipt recovery still reconstructs the historical request-head prefix, verifies exact preparation, and never reapplies events.

## D158-10 — Preserve request v2 as a read/commit compatibility contract

**Decision.** Orchestration, run audit, and commit accept both request v2 and v3.

**Reason.** Exchange evolution should not strand already issued requests or force ledger mutation merely to add an input label.

**Consequence.** New packets use v3. Compatibility code has an explicit default and separate field sets rather than silently accepting arbitrary hybrids.

## D158-11 — Keep the model client external

**Decision.** Dispatch renders a complete invocation envelope but does not call a provider.

**Reason.** Credentials, billing, retry policy, network behavior, retention, streaming, and model discovery are host concerns with fast-moving contracts.

**Consequence.** Lacuna can be used by a human bridge, local agent runner, API host, or future MCP/Action adapter without coupling the kernel to one SDK.

## D158-12 — Record provider documentation drift as an operational risk

**Decision.** Keep checked-in provider adapters and primary documentation references, but state that discovery syntax may change.

**Reason.** Provider-specific files are useful entrances for current hosts but cannot be treated as stable semantic law.

**Consequence.** The portable dispatch remains the fallback contract and conformance should be rechecked before changing native configuration.

## D158-13 — Keep the gift claim falsifiable

**Decision.** Frame rev0158 as a stronger experimental and operational substrate, not proof that retcon planning or multi-agent play improves fiction.

**Reason.** The implemented contribution is typed custody, context manufacture, exact handoff, and executable acceptance. Generation and aesthetic evaluation remain external.

**Consequence.** Current research records propose matched scenario and topology ablations rather than reporting unperformed results.
