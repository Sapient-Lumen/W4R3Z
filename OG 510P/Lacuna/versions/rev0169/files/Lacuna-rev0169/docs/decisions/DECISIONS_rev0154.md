# Decisions — rev0154

## D-0154-01 — model entrance is a separate layer from the turn packet

**Decision:** add a read-only `lacuna.model-brief.v1` entrance before the existing source-bound turn protocol.

**Reason:** a turn packet is an excellent execution contract after a host knows how to obtain one. It does not by itself route an ordinary utterance, resolve a campaign, disclose capability limits, verify readiness, or teach the host loop.

**Consequence:** `./lacuna model brief` may guide a model or human but grants no mutation authority. Only a fresh packet write grant authorizes turn operations.

## D-0154-02 — profiles describe capabilities, not products or subscriptions

**Decision:** use `chat`, `workspace`, and `orchestrated` profiles.

**Reason:** “ChatGPT,” “Pro,” “Claude,” “Gemini,” or “Codex” does not uniquely determine whether the current runtime can read local files, execute commands, or create bounded subagents.

**Consequence:** documentation and machine output must describe actual bridge/tool capability. A conversation-only premium product remains `chat`; a shell-capable runtime is `workspace`; use `orchestrated` only when bounded contexts can be created and the parent retains final authority.

## D-0154-03 — readiness includes deterministic verification

**Decision:** the model brief calls `cube.verify()` before declaring a cube ready for governed play.

**Reason:** successful opening is weaker than ledger integrity. A model should not continue a corrupted or inconsistent cube merely because SQLite is readable.

**Consequence:** the brief reports a coarse `cube-verification-failed` blocker and directs the operator to `./lacuna verify`. It does not expose unrestricted forensic details as part of every entrance.

## D-0154-04 — active player and narrator agents are entrance prerequisites

**Decision:** resolve audience/actor defaults from campaign metadata when available, then verify that both agents exist and are not retired.

**Reason:** a valid packet requires real perspective and actor identities. Falling back silently to absent or retired role names would defer a predictable failure until after the model has started play.

**Consequence:** missing roles are explicit readiness blockers. Bare cubes still default to `player` and `narrator`, but those defaults must be registered.

## D-0154-05 — exact player input is captured fail closed

**Decision:** generated packet commands require a nonempty shell variable:

```bash
"${PLAYER_INPUT:?set PLAYER_INPUT to the exact latest player message}"
```

**Reason:** prose telling a host to preserve exact input is insufficient. Empty input, paraphrase, or unsafe shell interpolation would break transcript/digest correspondence.

**Consequence:** an unset/empty variable aborts before packet mutation. Quoted expansion preserves shell metacharacters and newlines as data. Transcript bodies remain externally retained.

## D-0154-06 — a DM request routes the session but is not world evidence

**Decision:** treat utterances such as “Will you DM?” as play-workflow control.

**Reason:** session control and in-world action are different semantic classes. Treating the former as physical evidence would immediately contaminate the ledger.

**Consequence:** the model may start/resume play, but it must not infer that an in-world action succeeded from the request itself.

## D-0154-07 — first response should optimize for play, not ritual

**Decision:** when a reachable cube is ready, start or resume promptly. Ask at most one bundled preference question only when neither campaign premise nor user preference supplies a starting point; otherwise choose reversible defaults and open with a low-commitment scene.

**Reason:** the player should not need to learn ledger terminology or perform an interview before experiencing the game.

**Consequence:** infrastructure complexity is handled by the host/model brief. The first audience-facing response remains natural while semantic commitments stay conservative.

## D-0154-08 — chat-only play is permitted but must be honest

**Decision:** a conversation with no bridge may begin a playable scene, labelled once as chat-only/not yet committed.

**Reason:** refusing to play wastes a capable model; pretending that a local cube was updated is false.

**Consequence:** the session can later switch to governed mode when a human supplies a fresh brief/packet or a connected host becomes available. The model may not invent receipts or durable state.

## D-0154-09 — the default model proposal is valid narration-only JSON

**Decision:** replace fake claim/assertion example operations with an empty operation list and empty revealed-assertion list.

**Reason:** literal models may execute examples. The previous `replace.me` values were a contamination hazard even though humans could recognize them as placeholders.

**Consequence:** replacing narration alone produces a valid proposal. Typed mutations must be added deliberately when an observed or authored fact deserves custody.

## D-0154-10 — the turn response contract has one implementation source

**Decision:** centralize packet response-contract construction in `build_turn_response_contract()` and reuse it from `turns.py`.

**Reason:** independently maintained runtime templates and operator examples can drift in identity fields, operation rules, or safe defaults.

**Consequence:** model-facing packet behavior is generated through one helper and covered by entrance/turn tests. Documentation may explain the contract but should not invent a parallel executable template.

## D-0154-11 — accepted narration is read from the real top-level receipt field

**Decision:** operator guidance must present `/tmp/lacuna-turn-receipt.json` top-level `narration` only after acceptance.

**Reason:** earlier guidance incorrectly referred to `receipt.narration`. A host following that path could fail and substitute unaccepted proposal prose.

**Consequence:** tests compare the guidance with an actual committed receipt. A failed commit never authorizes presentation of the proposed narration as history.

## D-0154-12 — temporary handoffs use explicit files

**Decision:** standardize the portable loop on:

- `/tmp/lacuna-turn-packet.json`;
- `/tmp/lacuna-turn-proposal.json`; and
- `/tmp/lacuna-turn-receipt.json`.

**Reason:** weaker hosts should not need to remember which object in a long conversation is current. Explicit files reduce stale-object ambiguity.

**Consequence:** these paths are local conveniences, not permanent transcript custody. Hosts may substitute equivalent secure paths but must preserve freshness and exact object identity.

## D-0154-13 — multi-agent orchestration is information-flow separation, not voting

**Decision:** define planner, narrator, proposal-builder, and verifier roles with asymmetric inputs and outputs.

**Reason:** duplicating the same context across several agents creates consensus theater. The useful property is that the narrator cannot see hidden rationales, the serializer cannot widen authority, and the verifier diagnoses independently.

**Consequence:** role count alone is not a quality claim. Trivial narration-only turns may remain monolithic.

## D-0154-14 — the parent is the sole packet/commit authority

**Decision:** subagents never invoke `turn packet`, write the accepted proposal file, run `turn commit`, or present the receipt.

**Reason:** centralizing mutation makes stale-head handling, authority review, and receipt presentation auditable. It also prevents a subordinate context from treating its own output as accepted.

**Consequence:** subagents return plans, prose, JSON candidates, or diagnoses. The parent decides what to retain and owns all mutation commands.

## D-0154-15 — narrator context omits privileged planning state

**Decision:** the narrator receives exact player input, audience context, and a scrubbed observable beat plan, but not planner context, world identifiers/weights, hidden motives, or seal openings.

**Reason:** hidden-state leakage is a primary failure mode of monolithic LLM direction.

**Consequence:** the parent must strip hidden rationale rather than forwarding planner output wholesale. If the provider cannot enforce context isolation, the separation remains behavioral and must not be advertised as hard confidentiality.

## D-0154-16 — provider-native adapters inherit models and remain non-authoritative

**Decision:** check in Codex, Claude Code, and Gemini CLI project configurations plus ChatGPT instructions, but do not pin model names.

**Reason:** discovery conventions help a fresh agent enter, while model identifiers and configuration formats drift quickly.

**Consequence:** adapters inherit the active parent model where supported. Failure to load an adapter degrades to the portable `workspace` path, never to ungoverned mutation.

## D-0154-17 — provider tool restrictions are described exactly

**Decision:** document that Claude Code and Gemini CLI role files use empty tool sets, while Codex custom agents use read-only sandboxes that may still inspect readable files.

**Reason:** “read-only” is not synonymous with “cannot see secrets.” Overclaiming isolation would undermine fair-play opening custody and any scientific blind.

**Consequence:** unrevealed openings and other secrets stay outside readable workspaces unless a real host isolation boundary exists. Prompt separation is not a security proof.

## D-0154-18 — the model brief reports readiness separately from profile startability

**Decision:** expose both `cube_ready_for_governed_turn` and `selected_profile_can_start_without_bridge`.

**Reason:** cube integrity/role readiness and host capability answer different questions.

**Consequence:** a ready cube plus `chat` profile still requires a bridge. An orchestrated host cannot proceed against a failed cube.

## D-0154-19 — no database or event-schema bump

**Decision:** retain database schema 8 and event schema 1; add `model-brief.v1` only as an exchange schema.

**Reason:** the entrance reads status/verification and directs existing turn operations. The safe response-contract refactor changes generated interface content, not stored event semantics.

**Consequence:** schema-8 cubes remain directly usable. Exchange schema count increases by one.

## D-0154-20 — model entrance verification remains coarse by default

**Decision:** report pass/fail readiness and blockers, not the complete privileged verification report inside every brief.

**Reason:** the entrance should be legible and avoid accidentally broadening hidden forensic context.

**Consequence:** operators use the dedicated verifier for details. Future audience-specific verification summaries may be added only with explicit disclosure design.

## D-0154-21 — the datacube may serve as an executable context curriculum

**Decision:** document repeated, exact head-bound context walks as a first-class research direction.

**Reason:** deterministic projections and source-bound turns can compare providers, models, and role configurations without relying on conversational memory.

**Consequence:** a future scenario-capsule format should bind a seed cube, scripted inputs, role-specific contexts, expected mechanical outcomes, and external human scoring. Revision 0154 documents but does not implement that runner.

## D-0154-22 — ordinary provider instructions are behavior, not security

**Decision:** treat `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, custom-agent files, and ChatGPT instructions as navigation and behavioral context only.

**Reason:** a confused or adversarial model may ignore text. Vendor semantics may change.

**Consequence:** all durable mutation still passes through exact packet grants, validation, and atomic commit. No instruction file can grant authority absent a packet.

## D-0154-23 — examples and documentation are tested as interface artifacts

**Decision:** add tests for provider file presence/shape, forbidden stale guidance, schema validity, generated command execution, actual receipt shape, and safe proposal committability.

**Reason:** operator documentation directly controls model behavior and therefore deserves executable regression coverage.

**Consequence:** revision acceptance includes 158 tests, with dedicated model-entrance and provider-configuration suites.
