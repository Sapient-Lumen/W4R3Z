# Audit — rev0156

## Scope

This pass audited rev0155 as an entrance for three concrete users: a researcher evaluating Gwern’s retcon-planning proposal, an ordinary player asking ChatGPT to DM, and a fresh or less capable model coordinating Lacuna across repeated CLI/model invocations. It reviewed source, schemas, root/provider instructions, ChatGPT bridge documentation, least-context handoffs, filesystem custody, state transitions, failure defaults, and release packaging.

## Baseline

The uploaded rev0155 archive contained 197 ZIP entries and had SHA-256 `b0dc77c47f1199e02777014f11c3ce3a5f2163653076213c9e59821730a1b0ba`.

The archive extraction did not retain the POSIX executable bit on `lacuna` in this environment. After restoring that bit, the source behavior was testable. The modified worktree initially reached 175 collected tests; the final acceptance result is recorded in `docs/acceptance/ACCEPTANCE_rev0156.json`.

Database schema 8, event schema 1, event-ledger semantics, and prior custody protocols were retained.

## Findings and repairs

### A-0156-01 — the documented ChatGPT exact-input path did not exist

**Severity:** high

The rev0155 ChatGPT bridge told the operator to run `turn packet --player-input-file`, but the CLI accepted only inline `--player-input`. The safer path was documentation fiction.

**Repair:** implemented mutually exclusive `--player-input`/`--player-input-file` support for packet and run entrances, including `-` for standard input and newline-preserving UTF-8 reads.

**Evidence:** CLI end-to-end coverage preserves shell metacharacters and exact line endings through request, packet, run, proposal, and receipt.

### A-0156-02 — orchestration had artifact binding but no workflow custody

**Severity:** high

Rev0155 could generate plans and cards, but a coordinator still had to remember which files belonged to the current request and which command came next over multiple invocations.

**Repair:** added the request-scoped `turn run` state machine with strict `run.json`, staged filenames, deterministic `NEXT.md`, and begin/status/accept/commit operations.

**Evidence:** a run can be resumed from its directory alone; audit recomputes packet, plan, cards, state, and next action.

### A-0156-03 — a valid artifact could be wrong for the current stage

**Severity:** high

JSON Schema validity and packet binding do not prove that a planner return is appropriate when the run expects a narrator return, proposal, or verifier result.

**Repair:** `accept` requires the exact root schema expected by the current status before stage-specific validation and writes.

**Evidence:** adversarial tests submit valid wrong-stage objects and require structured refusal without state advance.

### A-0156-04 — manifest metadata could be relabelled

**Severity:** high

A digest can still point to the correct JSON while the manifest lies about its schema, role, media type, or path. A literal coordinator might trust the label.

**Repair:** every artifact key now has fixed filename and metadata; proposal role is additionally derived from topology.

**Evidence:** relabelled role/schema and substituted path tests refuse even when the underlying JSON remains valid.

### A-0156-05 — the human-readable next pointer could misdirect a weaker model

**Severity:** high

A tampered `NEXT.md` could name a different role, input, or command while `run.json` remained valid.

**Repair:** render `NEXT.md` deterministically from audited state and compare it byte-for-byte on every status/accept/commit operation.

**Evidence:** pointer tampering blocks advancement with `turn-run-next-pointer-mismatch`.

### A-0156-06 — active docs still taught the fragile low-level chain

**Severity:** high

Several primary entrances continued to make packet → plan → card → return sequencing the default. This expected a new model to reconstruct the protocol rev0156 was meant to make explicit.

**Repair:** converged `README.md`, `START_HERE.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, ChatGPT instructions, and operator guides on the four-command run protocol. The low-level interfaces remain documented as expert substrate.

**Evidence:** provider tests require `turn run begin`, `NEXT.md`, `accept`, and `commit` in the root adapter and reject the old root default.

### A-0156-07 — solo instructions named more context than they pointed to

**Severity:** medium

An intermediate solo next action referred to both packet and safe draft while identifying only one complete input artifact. That is a small ambiguity for a frontier model and a material one for a literal model.

**Repair:** the action now points to the complete packet and explicitly names its embedded `response_contract` proposal template as the starting shape.

**Evidence:** turn-run tests assert one complete path and the exact embedded-template instruction.

### A-0156-08 — generated entrances routinely requested privileged planner context

**Severity:** high

The model brief’s run command included planner-context return by default, creating a routine post-commit leakage path inconsistent with least-context design.

**Repair:** removed the default flag. Explicit operator opt-in remains available.

**Evidence:** model-entrance tests assert that generated commands omit `--include-planner-context` while the CLI option remains functional.

### A-0156-09 — player start and durable mutation were conflated

**Severity:** high

“Can ChatGPT DM?” has two different answers: it can begin narrative play immediately, but ordinary chat cannot claim to have changed a durable local cube.

**Repair:** documented and configured five capability-specific paths: chat-only, Project/instructions, human bridge, bounded role context, and connected host. “Will you DM?” routes to play rather than repository work.

**Evidence:** ChatGPT adapter tests require the one-time noncommit disclosure, human/connected bridge language, exact proposal shape, and correct top-level receipt narration path.

### A-0156-10 — provider role discovery still required implicit name translation

**Severity:** medium

Portable hyphenated role names differ from Codex’s configured underscore names, and ChatGPT does not expose the same project subagent mechanism.

**Repair:** model briefs and generated next actions include provider-specific aliases and ChatGPT role-dedicated-context guidance.

**Evidence:** schema/provider tests validate alias maps and all checked-in custom-agent files.

### A-0156-11 — run privacy and concurrency could be overstated

**Severity:** high

A `0700` directory and atomic individual writes can sound stronger than they are. There is no same-run lock, distributed transaction, hostile-host protection, or provider confidentiality proof.

**Repair:** expanded the threat model, architecture, operator runbook, changelog, and manifest nonclaims with absolute paths, sequential ownership, begin/commit crash windows, retention, canonical-JSON semantics, and provider-isolation limits.

**Evidence:** current docs do not call the sidecar a security boundary or atomic cross-store transaction.

### A-0156-12 — the gift framing risked overclaiming a complete retcon system

**Severity:** medium

Lacuna strongly addresses commitment and custody but does not yet generate/roll out/select candidate futures or prove improved fiction.

**Repair:** created `THREE_SERIOUS_QUESTIONS.md`, strengthened the Gwern gift test, and defined a falsifiable four-condition study.

**Evidence:** current design records map implemented, partial, and external parts of the essay and list explicit success/failure measures.

### A-0156-13 — release tests retained obsolete interface assertions

**Severity:** low

After the root docs were correctly moved to the run protocol, two tests still demanded the old `turn plan`/`turn card` text and an obsolete ChatGPT receipt phrase.

**Repair:** updated the tests to enforce the new entrance, deterministic pointer, bridge honesty, and exact receipt contract.

**Evidence:** provider suite passes against the current interface rather than preserving stale prose.

## Refactor review

The new `turnruns.py` module is a sidecar coordinator over existing public packet, orchestration, proposal, verifier, and commit validators. It does not add provider clients or bypass kernel validation.

Positive properties:

- state derives from accepted artifacts rather than trusting the manifest status;
- every operation audits before transition;
- accepted artifacts are rewritten atomically and referenced by canonical digest;
- role/schema/path metadata are fixed rather than model-supplied policy;
- cards are rebuilt from packet and accepted upstream returns during audit;
- proposal drafts remain visibly non-authoritative;
- parent-only mutation authority is preserved;
- full verification is required by workflow but remains explicitly advisory relative to the kernel.

The module intentionally does not attempt distributed locking, provider invocation, transcript encryption, or automatic crash recovery. Those would require additional host and identity policy rather than a silent local abstraction.

## Test additions and changes

Revision 0156 adds five dedicated turn-run tests covering:

- solo exact-input round trip and commit;
- pair/full stage progression and provider-facing next actions;
- cross-turn, wrong-stage, edited, and placeholder refusal;
- manifest/artifact metadata and `NEXT.md` tamper refusal;
- verifier refusal and parent-only closure behavior.

CLI end-to-end coverage grows from 9 to 10 tests. Provider assertions are updated to the current run entrance. The total collection is 175 tests across 18 suites.

## Residual risks

1. **Same-run races:** two parents can audit the same state and race writes; there is no run lock or generation compare-and-swap.
2. **Begin orphan:** a request can be created before a run directory is fully materialized.
3. **Commit split-brain:** the cube can commit before receipt/manifest persistence; blind retry may encounter a closed request or stale head.
4. **Absolute paths:** run v1 is not relocatable and can expose local directory structure.
5. **Sensitive sidecars:** planner cards, exact player text, and model returns may contain private material; no encryption or cleanup policy is provided.
6. **Host authenticity:** local digests do not prove who produced a return or whether a provider altered/logged context.
7. **Semantic leakage:** a formally audience-safe observable plan can still encode hidden rationale in natural language.
8. **Verifier limitations:** a passing advisory verifier does not prove correctness, quality, fairness, or noninterference.
9. **Provider drift:** custom-agent formats and behavior can change; static configuration tests do not constitute live conformance testing.
10. **No model invocation:** the parent or external host must actually dispatch roles and preserve exact outputs.
11. **No full retcon loop:** candidate proposal, rollout, scoring, resampling, checkpoint optimization, and forgetting remain future/application work.
12. **No empirical quality result:** the architecture has not yet been compared in a blinded narrative study.

## Conclusion

Revision 0156 repairs the entrance rather than expanding the truth kernel. A player can ask to play without learning the protocol; a ChatGPT user receives an honest path to persistence; a subagent-capable parent is told exactly which bounded role to invoke and what artifact to provide; and a later model invocation can resume from one audited run path.

This materially strengthens Lacuna as a gift and research platform because the commitment-budget machinery is now not only inspectable but traversable. The remaining gaps—provider invocation, concurrency/recovery, scenario capsules, candidate rollout, and empirical evaluation—are explicit next layers rather than hidden assumptions.
