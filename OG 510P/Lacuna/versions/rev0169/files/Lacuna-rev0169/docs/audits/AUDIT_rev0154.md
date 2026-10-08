# Audit — rev0154

## Scope

Revision 0154 audits the boundary between a fresh model and Lacuna’s existing source-bound turn protocol. The review asks whether an unfamiliar or literal model can:

- distinguish play from repository development and inspection;
- discover the selected campaign/cube;
- state honestly whether it can reach local tools;
- verify readiness before play;
- preserve exact player input;
- create and consume a fresh turn packet;
- return a safe proposal without copying demonstration artifacts;
- use subagents without leaking hidden context or delegating commit authority;
- handle refusal/staleness; and
- present only accepted narration.

The audit also reviews provider-native configuration for Codex, Claude Code, Gemini CLI, and ChatGPT-style conversation setups. It does not audit provider infrastructure, model weights, billing, authentication, or hard sandbox implementation.

## Method

The audit combined:

1. static comparison of entrance/operator documentation with emitted CLI objects;
2. review of turn packet and receipt runtime structures;
3. adversarial execution of generated shell commands with unset input, spaces, newlines, quotes, substitutions, and metacharacters;
4. schema validation of the model brief;
5. lifecycle tests against a real temporary cube;
6. provider configuration parsing and invariant checks;
7. full regression testing of the retained epistemic kernel; and
8. clean-extract manifest, launcher, lifecycle, and test execution.

Findings are listed by severity of likely semantic or operational harm, not by implementation effort.

## Findings and repairs

### A-0154-01 — executable example could commit fake `replace.me` artifacts

**Severity:** high semantic integrity

**Before:** the model-facing turn response contract contained demonstration claim/assertion operations with placeholder identifiers such as `replace.me`.

**Risk:** a literal, hurried, or weaker model could return the example largely unchanged. Because the object was structurally close to valid, a host might commit meaningless claims or receive confusing downstream refusals. The example taught mutation even when narration-only was correct.

**Repair:** replace the example with a fully valid narration-only proposal containing empty `operations` and `revealed_assertion_ids`. Keep all packet-bound identity fields prefilled.

**Evidence:** entrance tests assert that no generated packet contains `replace.me`; a narration-only proposal built from the actual template commits successfully and returns accepted narration without semantic operations.

### A-0154-02 — host guidance named a receipt field that does not exist

**Severity:** high operational correctness

**Before:** guidance told hosts to read `receipt.narration` after commit.

**Risk:** the real emitted turn receipt exposes top-level `narration`. A literal host could fail to find the field and present unaccepted proposal prose, retry incorrectly, or stop play.

**Repair:** correct every active operator/provider surface to read `/tmp/lacuna-turn-receipt.json` top-level `narration` only after acceptance.

**Evidence:** a test performs an actual packet/commit round trip, asserts top-level narration, and checks that generated guidance contains no `receipt.narration` string.

### A-0154-03 — opening a readable cube could be mistaken for readiness

**Severity:** high ledger integrity

**Before:** entrance behavior could proceed from successful open/status without an explicit deterministic verification result.

**Risk:** a model might continue a cube whose projection, event chain, or invariants were corrupted.

**Repair:** `build_model_brief()` runs `cube.verify()`. Readiness is false when overall verification fails and exposes a coarse `cube-verification-failed` blocker.

**Evidence:** a projection-tampering test causes the brief to refuse readiness while remaining read-only.

### A-0154-04 — missing or retired role agents were not caught at entrance

**Severity:** medium operational correctness

**Before:** a host could assume default `player`/`narrator` or campaign bindings were usable without checking active registration.

**Risk:** play could begin in prose, then packet creation or semantic attribution would fail.

**Repair:** resolve campaign defaults and verify that audience and actor rows exist with `retired_seq IS NULL`.

**Evidence:** model-entrance tests cover ready campaign roles and readiness blockers; the active-agent query uses the same retirement convention as the kernel.

### A-0154-05 — exact player input was a prose promise, not a host guard

**Severity:** high provenance integrity

**Before during design:** generated instructions could have shown a placeholder or accepted an empty value, relying on the operator to substitute correctly.

**Risk:** the packet digest could bind a paraphrase, blank string, or shell-transformed text rather than the exact latest player message.

**Repair:** generate a shell command containing quoted required expansion:

```bash
"${PLAYER_INPUT:?set PLAYER_INPUT to the exact latest player message}"
```

**Evidence:** execution tests confirm that unset input aborts before the event count changes, while a value containing command substitution syntax, semicolons, quotes, spaces, and a newline is preserved as data and creates no injected side effect.

### A-0154-06 — product naming could overstate runtime capability

**Severity:** high trust/usability

**Before:** “use ChatGPT Pro,” “use Codex,” or similar labels could be interpreted as sufficient for local cube mutation.

**Risk:** an ordinary conversation might claim it committed state merely because it can read an uploaded archive or follow instructions.

**Repair:** define profiles by capabilities: `chat`, `workspace`, and `orchestrated`. Report cube readiness separately from whether the selected profile can start without a bridge.

**Evidence:** schema/tests validate all profiles; ChatGPT docs explicitly state that subscription tier and uploaded files do not create a durable local CLI bridge.

### A-0154-07 — a DM request could be misrouted as coding or world evidence

**Severity:** medium interaction correctness

**Before:** a repository agent might default to source-tree work, while a role-playing prompt might treat “Will you DM?” as content rather than session control.

**Risk:** the user would receive an implementation explanation instead of play, or the ledger would record an invented physical event.

**Repair:** add an intent router for play/DM, project development, and inspection. Explicitly state that the request selects a workflow and is not evidence of in-world success.

**Evidence:** the portable brief, `AGENTS.md`, provider imports, and ChatGPT instructions all carry the routing rule; provider tests assert the root instructions contain the play intent and parent-authority boundaries.

### A-0154-08 — chat-only operation lacked an honest fallback

**Severity:** medium trust/usability

**Before:** a model with no local tools faced two bad defaults: refuse to play or imply nonexistent durable state.

**Risk:** either the product is unusable for ordinary players or its custody claims become misleading.

**Repair:** permit immediate chat-only play with one clear label, reversible defaults, and no claim of cube mutation. Define human paste and connected-host bridges for governed transition.

**Evidence:** model brief profile contracts and ChatGPT integration docs distinguish chat-only, human bridge, and workspace operation.

### A-0154-09 — response-contract logic could drift between entrance and turns

**Severity:** medium maintainability/semantic integrity

**Before:** model-facing examples and runtime packet construction could be updated separately.

**Risk:** a documented “safe” object might differ from the real packet’s fields or rules; fixes could land in one surface only.

**Repair:** extract `build_turn_response_contract()` into `entrance.py` and call it from `turns.py`.

**Evidence:** original turn tests plus model-entrance tests pass through the shared helper; schema validation covers emitted packets and briefs.

### A-0154-10 — subagents could receive identical privileged context

**Severity:** high confidentiality/noninterference

**Before during design:** “use multiple agents” could be implemented as several copies of the same packet and hidden context.

**Risk:** narrator leakage remains unchanged, agreement becomes consensus theater, and no role independently checks serialization.

**Repair:** define asymmetric planner, narrator, proposal-builder, and verifier contracts. Narrator input explicitly excludes planner context, world IDs/weights, hidden motives, and seal openings.

**Evidence:** provider definitions and multi-agent docs encode distinct inputs/outputs; tests verify all four role files exist and preserve parent-only commit language.

### A-0154-11 — delegation could launder mutation authority

**Severity:** critical authority boundary

**Before during design:** a planner or proposal-builder might be told to run packet/commit commands for convenience.

**Risk:** subordinate contexts could create stale grants, commit their own unchecked outputs, or present proposals as accepted.

**Repair:** make the parent/coordinator the sole owner of packet creation, final proposal file, commit, and receipt presentation. Subagents return advisory artifacts only.

**Evidence:** portable delegation contracts and every provider role prohibit commit; provider tests check parent-only authority instructions. Kernel write grants remain the enforcing layer.

### A-0154-12 — provider “read-only” could be misrepresented as secret isolation

**Severity:** high confidentiality claim

**Before during design:** a read-only subagent sandbox might be described as unable to access hidden workspace material.

**Risk:** unrevealed fair-play openings, assessor keys, or scientific blinds stored in readable paths could leak to a narrator or verifier.

**Repair:** state the provider-specific distinction. Claude Code and Gemini CLI definitions use empty tool lists. Codex definitions use read-only sandboxes but may still inspect readable workspace files; therefore they are prompt-separated, not a hard confidentiality boundary.

**Evidence:** provider files and docs use the exact restriction appropriate to each runtime; threat-model text forbids placing secret openings in readable workspaces.

### A-0154-13 — provider configs could pin stale models or recurse without bound

**Severity:** medium portability/cost

**Before during design:** native agent files might hard-code current model names or allow uncontrolled delegation.

**Risk:** rapid provider drift would make the artifact fail or unexpectedly expensive; nested agents could widen context and authority.

**Repair:** inherit the active parent model, cap Codex depth at one/four threads, deny recursive delegation in role instructions, and use provider maximum-turn fields where supported.

**Evidence:** configuration tests parse TOML/frontmatter and assert role count, no stale model pin, bounded depth/turns, and conservative tools.

### A-0154-14 — a model brief could mutate while claiming to be inspection

**Severity:** high authority transparency

**Before during design:** generating readiness guidance might have reused turn-packet construction or written setup state.

**Risk:** an operator could alter custody merely by asking how to start.

**Repair:** implement model reference resolution, status, verification, and brief construction as read-only operations. Commands that later mutate are printed, not executed.

**Evidence:** tests compare head/event/change counts before and after brief generation for every profile.

### A-0154-15 — temporary object identity was underspecified

**Severity:** medium stale-context reliability

**Before:** a long conversation could contain several packets/proposals with no canonical handoff locations.

**Risk:** a weaker model or human might commit an old object or present narration from the wrong receipt.

**Repair:** use explicit packet/proposal/receipt filenames under `/tmp` in the portable loop and name each owner/input/output.

**Evidence:** the emitted brief contains all three paths; generated-command tests execute the packet path directly.

### A-0154-16 — model-facing schema lacked a strict machine contract

**Severity:** medium integration reliability

**Before:** entrance guidance existed only as prose concepts.

**Risk:** host adapters could guess field names, omit blockers, or conflate readiness and capability.

**Repair:** add strict Draft 2020-12 `model-brief.v1.schema.json` with no unknown fields at governed structural levels.

**Evidence:** concrete emitted briefs validate for all profiles; malformed profile/reference values are refused with typed errors; meta-schema validation passes.

### A-0154-17 — provider-native discovery was absent

**Severity:** medium usability

**Before:** even a shell-capable model might not know that “Will you DM?” should use Lacuna rather than edit the repository.

**Risk:** the correct protocol remained dependent on an unusually good initial prompt.

**Repair:** add root `AGENTS.md`, provider import files, native subagent definitions, and ChatGPT integration instructions/conversation starters.

**Evidence:** configuration tests verify file presence, imports, role identities, conservative tools, and forbidden stale guidance.

### A-0154-18 — documentation did not frame the cube as a repeatable context path

**Severity:** medium research utility

**Before:** deterministic projections and repeated CLI invocations were present, but the experimental consequence was not explicit.

**Risk:** future work might collapse back into one long prompt instead of using identical head-bound context walks across models and roles.

**Repair:** document the datacube as an executable context curriculum and specify a future scenario-capsule design.

**Evidence:** `BEYOND_RETCON_PLANNING.md`, `GWERN_GIFT_TEST.md`, research notes, and multi-agent docs now connect exact context slices to comparative fiction/science experiments.

## Refactor review

### Shared response-contract helper

The bounded code refactor moves only model-facing response-contract assembly into `src/lacuna/entrance.py`. It does not move storage, validation, or commit authority. `turns.py` continues to build the actual request/write grant and calls the helper with authoritative values.

Benefits:

- one safe default proposal;
- one ordered rule list;
- lower documentation/runtime drift risk;
- isolated testing of literal-model safety; and
- no event/database migration.

Risk considered: importing `entrance.py` from `turns.py` could create a cycle. `entrance.py` depends on `Cube` and utility modules but not `turns.py`; the import graph remains acyclic in execution and full tests pass.

### Private active-agent lookup

`_agent_exists()` uses `cube._exists()` because no public active-agent predicate currently exists. This is a small architectural smell rather than a functional defect. A future bounded refactor may expose a public read-only identity lookup, but doing so in this revision would widen scope without changing entrance semantics.

## Regression coverage

Revision 0154 adds:

- 12 model-entrance tests;
- 6 provider-configuration tests;
- 1 additional CLI end-to-end entrance test; and
- updates to schema coverage.

The complete suite contains 158 tests across campaigns, cardinality, CLI, commitment/revision, consequence repair, kernel behavior, model entrance, particle reconciliation, particle bank, projection hygiene, provider configs, relations/migration, schema lineage, exchange schemas, fair-play seals, and turns.

The retained schema-8 factor reconciliation, source-bound turn v2, fair-play seals, governed revision, consequence repair, campaign resolution, access-scoped contexts, and projection verification suites all pass unchanged.

## Residual risks

### A-0154-R1 — no automatic bridge for ordinary ChatGPT conversations

The artifact provides Project/custom-GPT instructions and a human paste workflow. It does not bundle an OpenAI Action, MCP server, daemon, or authenticated remote executor. A chat-only session cannot truthfully update a local cube by itself.

### A-0154-R2 — prompt role separation is not hard isolation

Even with empty tool lists, a provider may retain parent context or implement isolation differently than expected. Codex read-only agents may inspect readable files. Hosts must treat provider behavior as untrusted and keep secrets outside supplied contexts/workspaces.

### A-0154-R3 — no empirical usability study

The entrance is tested mechanically, not yet with independent players or deliberately weak models. “Hyperlegible” remains a design target until scenario-capsule trials measure routing, completion, error, and abandonment rates.

### A-0154-R4 — no semantic prose verifier

The verifier can inspect packet/proposal structure and declared disclosure, but Lacuna does not automatically prove that every sentence in narration is supported by the accepted semantic delta or audience context.

### A-0154-R5 — exact transcript bodies remain external

The packet stores a digest and provenance source, not the message body. A host that loses or normalizes the external transcript cannot later reconstruct exact bytes from the cube alone.

### A-0154-R6 — temporary files require host hygiene

`/tmp` paths are explicit and legible but may be observable to other local processes under some operating systems. A production host should use restrictive permissions and per-session directories.

### A-0154-R7 — provider formats will drift

Codex, Claude Code, Gemini CLI, and ChatGPT configuration behavior can change faster than Lacuna’s release cadence. Native files must be revalidated against official documentation; failure should degrade to portable instructions.

### A-0154-R8 — parent synthesis can still leak hidden rationale

The architecture tells the parent to scrub planner output before narrator handoff but does not supply an automatic scrubber. A careless parent can defeat the information-flow design.

### A-0154-R9 — subagent verification is advisory

A verifier’s `PASS` is not a proof. The kernel’s actual commit validation remains decisive. A model verifier may miss semantic contradictions or overreach.

### A-0154-R10 — model brief uses a private storage helper

The active-agent readiness check reaches a private `Cube` helper. This is covered by tests but should eventually be replaced by a small public read-only identity API.

### A-0154-R11 — no scenario-capsule runner yet

The cube can define exact context walks, but revision 0154 does not package seed states, scripted turns, expected classes, run metadata, or human evaluation forms into a first-class executable experiment.

### A-0154-R12 — no claim that multi-agent mode is better

The role split has a strong information-flow rationale, but cost, latency, synthesis errors, and provider behavior may outweigh benefits for simple turns. Comparative evidence is still required.

## Acceptance result

The rev0154 acceptance run covers read-only briefing, capability profiles, campaign/reference resolution, verification blockers, active-role checks, strict schema validation, exact-input command failure and injection resistance, safe narration-only commits, actual receipt shape, provider configuration parsing, parent-only authority, and all retained kernel behavior. Manifest verification and the full suite are repeated from a clean extracted artifact before release.
