# Audit — rev0155

## Scope

This pass audited the rev0154 model entrance and least-context orchestration proposal as an executable interface for fresh, cross-provider, and less capable models. It also reviewed sidecar/kernel boundaries, provider role contracts, documentation commands, private API usage, schema coverage, and failure defaults.

## Baseline

The extracted rev0154 parent passed all **158 tests** before modification. Database schema 8, event schema 1, ledger verification, and all prior custody protocols were retained.

## Findings and repairs

### A-0155-01 — least-context delegation existed only as prose

**Severity:** high

Rev0154 described asymmetric planner/narrator/builder/verifier roles, but the coordinator still had to hand-construct each prompt and redact privileged fields.

**Repair:** added deterministic `turn plan` and `turn card` sidecar commands plus strict `lacuna.orchestration-plan.v1` and `lacuna.turn-task-card.v1` schemas. Narrator context is now manufactured from allowed fields.

**Evidence:** orchestration tests assert absence of the full packet, planner context, private notes, and candidate operations from narrator cards.

### A-0155-02 — packets were not strictly audited before fan-out

**Severity:** high

A host could distribute a packet whose player-input body, context head, grant, response contract, or proposal template had drifted.

**Repair:** every plan/card begins with complete strict packet validation and canonical digest construction.

**Evidence:** tests alter input, context, grant, and template independently and require specific refusal codes.

### A-0155-03 — upstream artifacts could be mixed across turns or edited after card issue

**Severity:** high

Prose labels and request IDs alone did not establish exact artifact continuity.

**Repair:** deterministic task IDs and role returns bind packet SHA-256 plus ordered upstream artifact kind/digest pairs.

**Evidence:** cross-turn planner reuse and post-card planner edits refuse with `handoff-binding-mismatch`; task IDs change with upstream content.

### A-0155-04 — narrator redaction remained coordinator-dependent

**Severity:** high

A coordinator could accidentally forward private rationale or candidate operations while believing it had created an audience-safe prompt.

**Repair:** the narrator task-card constructor accepts a validated planner return but copies only `observable_plan`, exact player data, and audience context.

**Evidence:** canary private notes and candidate operations are absent from serialized narrator cards.

### A-0155-05 — unchanged output templates could masquerade as completed work

**Severity:** medium

JSON Schema validation would accept the narrator instruction string and the verifier fail-closed template as structurally valid returns. A literal model might return either unchanged.

**Repair:** narrator validation refuses the exact placeholder. Verifier `pass` refuses both blocker findings and any retained `unperformed-review` code, even after cosmetic severity edits.

**Evidence:** focused orchestration regression assertions cover both cases.

### A-0155-06 — provider-specific heading formats were incompatible with a machine chain

**Severity:** high

The native role files described useful roles but did not require one portable, digest-preserving JSON return format.

**Repair:** rewrote all Codex, Claude Code, and Gemini CLI role files around complete `lacuna.turn-task-card.v1` input and exact `output_contract` output. ChatGPT instructions use the same protocol.

**Evidence:** provider tests parse every configuration and assert task-card, output-template, no-tools/no-commit, and fail-closed requirements.

### A-0155-07 — the plan still required a weaker model to infer invocation details

**Severity:** high

An early rev0155 plan selected roles and dependencies but omitted exact downstream commands. The coordinator had to infer flags such as `--planner-return`, `--narrator-return`, and `--proposal`.

**Repair:** added `card_command` to every stage. Worker stages include exact command templates and named upstream files; parent stages use `null`.

**Evidence:** plan schema and tests require the commands and each dependent flag.

### A-0155-08 — local proposal checking risked overstating acceptance

**Severity:** medium

A builder/verifier needs early diagnostics, but duplicating full commit validation in the sidecar layer would drift or create a false “approved” state.

**Repair:** implemented narrowly named `validate_proposal_binding()` preflight for packet identity, grant names, and limits only. Documentation repeatedly states that commit remains authoritative.

**Evidence:** tests reject identity drift and ungranted operation names while role cards/nonclaims deny commit validity.

### A-0155-09 — entrance/demo code used a private storage predicate

**Severity:** low

Role readiness depended on private `_exists` probing.

**Repair:** added public, read-only, retirement-aware `Cube.has_active_agent()` and updated callers.

**Evidence:** tests verify active, missing, malformed, and read-only behavior.

### A-0155-10 — CLI JSON reading was coupled to change sets

**Severity:** low

New sidecar commands would otherwise reuse a private helper named and messaged for change-set files.

**Repair:** generalized the reader to strict JSON-object loading for packet and upstream artifacts.

**Evidence:** CLI plan/card end-to-end tests parse emitted objects and confirm no ledger change.

### A-0155-11 — orchestration nonclaims were underspecified

**Severity:** medium

Digest continuity, read-only sandboxes, and multiple agents could be misread as authentication, hard confidentiality, or independent verification.

**Repair:** expanded architecture, threat, provider, ChatGPT, model-entrance, multi-agent, glossary, and Gwern/research documentation.

**Evidence:** documentation now names host authentication, provider isolation, semantic correctness, concurrency, and verifier authority as explicit nonclaims.

## Refactor review

The new module is a pure sidecar layer over existing turn validators and context objects. It does not import provider clients, create threads/processes, or write to SQLite. Public helper extraction is limited to read-only validation/predicates. Storage schema and event projection code were not changed.

The role-card protocol uses strict field sets and canonical JSON digests. This reduces silent drift but deliberately avoids inventing a second mutation validator. Proposal preflight remains visibly narrower than `turn commit`.

## Test additions and changes

Revision 0155 adds an 11-test orchestration suite covering:

- strict packet audit;
- automatic topology routing and exact stage commands;
- narrator context firewall;
- cross-turn/edit digest refusal;
- full role chain and fail-closed verifier;
- proposal preflight;
- deterministic task IDs;
- operational Markdown;
- all new exchange schemas;
- read-only CLI behavior; and
- public active-agent predicate behavior.

Model-entrance, provider-configuration, and exchange-schema suites were expanded. The accepted total is **169 tests**.

## Residual risks

1. **Semantic transit leakage:** an observable plan can still contain hidden rationale in natural language; the parent approves it.
2. **No provider isolation proof:** prompt/tool settings do not prove separate memory, logs, files, or process boundaries.
3. **No model invocation:** cards describe work but Lacuna does not call or supervise a model.
4. **Sequential file examples:** shared `/tmp` names are not safe for concurrent turns without request-scoped host directories.
5. **Advisory verifier:** a pass does not authorize commit and a parent can ignore a refusal.
6. **Internal consistency, not authenticity:** packet audit does not sign or remotely authenticate artifacts.
7. **No durable sidecar workflow:** losing return files loses the chain even though the cube remains intact.
8. **No transcript-body custody:** input/narration bodies remain external and only their digests enter the ledger.
9. **No live provider conformance matrix:** configuration files are statically tested but not continuously exercised against current vendor runtimes.
10. **No retcon experiment runner:** candidate generation, rollout, scoring, checkpoint compression, and scenario capsules remain external.

## Conclusion

The audit converts the most consequential rev0154 orchestration assumptions into deterministic interfaces and structured refusals. The result is materially more legible to independent and less capable models without moving model policy or provider execution into the kernel. Remaining gaps are now explicit host/evaluation responsibilities rather than implied guarantees.
