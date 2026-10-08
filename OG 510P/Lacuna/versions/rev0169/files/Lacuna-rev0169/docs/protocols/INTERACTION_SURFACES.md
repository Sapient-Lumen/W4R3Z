# Interaction surfaces and host drive loop

## One kernel, several entrances

Lacuna is not an application shell or model vendor client. It exposes a deterministic custody kernel that can be wielded through several surfaces without changing the semantic rules underneath.

### One-sentence play entrance

A tool-capable host can treat an unmistakable invitation as session control and open a governed run directly:

```bash
./lacuna play start .lacuna-play --bootstrap --profile orchestrated --format markdown
```

This command safely resolves or creates one campaign, retains the exact sentence, emits request v4 with `input_kind = session-control` and `request_purpose = play`, and selects a topology from the declared capability profile. It invokes no model and commits no narration.

### Human campaign entrance

A person creates and selects campaigns in a library:

```bash
./lacuna campaign create ./stories lantern-room --title "The Lantern Room"
./lacuna campaign list ./stories
./lacuna campaign select ./stories lantern-room
./lacuna status ./stories
```

A bare cube directory also works. Library selection is convenience metadata outside the story event chain; the selected campaign’s cube remains the semantic authority.

### Administrative host entrance

The CLI and Python API can perform explicit campaign administration:

- register agents and sources;
- author claims, constraints, candidate worlds, commitments, and manual base weights;
- review and apply revisions, consequence repairs, complete-bank evidence updates, or factor-ledger reconciliations;
- prepare and operate fair-play seals;
- verify and rebuild projections;
- export snapshots, contexts, explanations, and receipts.

Secret-custody operations belong here, not in an ordinary model turn.

### Portable model entrance

Before a fresh model opens a turn, a host may emit a capability-specific, read-only entrance:

```bash
./lacuna model brief ./stories --profile chat --format markdown
./lacuna model brief ./stories --profile workspace --format markdown
./lacuna model brief ./stories --profile orchestrated --format markdown
```

The brief resolves a bare cube or selected campaign, performs deterministic verification, checks active audience/actor roles, distinguishes play from repository and inspection intent, states what the selected execution surface does and does not provide, and emits the exact governed loop. It does not grant mutation authority and does not change the head.

The profiles are deliberately not model brands:

- `chat` means conversation-only, with optional human/action bridge;
- `workspace` means one model can read files and execute the local host loop;
- `orchestrated` means a parent can also isolate bounded subagents.

Provider files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and the checked-in agent definitions) are discovery adapters for this portable contract. They are not a second authority system.

### Human-or-model turn entrance

The normal host entrance is a request-scoped state machine over the same two-phase packet/proposal contract:

```text
play start or turn run begin
    -> audited next owner/artifact
    -> optional self-contained dispatch
    -> one exact accept per stage
    -> exact kernel preparation
    -> turn run commit
```

`play start` opens typed session control; `turn run begin --input-kind play-turn` opens later in-fiction input. The run retains exact bytes, selects a topology, and manufactures the first safe draft or role card. `turn run dispatch` embeds the complete delegated card in a provider-routed envelope without invoking the provider. `turn run accept` strictly audits and advances one stage. `turn run recover` repairs only deterministic `NEXT.md` after authoritative audit. `turn run commit` replays the exact rollback-tested preparation and atomically records the narration source plus typed semantic operations. Lower-level `turn packet`, `turn plan`, `turn card`, and `turn commit` remain available to custom hosts.

The committed turn receipt already provides the combined result a ChatGPT-like host usually needs:

- accepted narration for immediate display;
- exact new ledger head;
- change-set receipt;
- resolved IDs;
- disclosed assertions;
- latest audience context;
- optional planner context only when the original request granted it.

A host should display narration only after acceptance. On refusal, it should regenerate from a fresh packet rather than pretending rejected prose occurred.

### Retcon-checkpoint entrance

A parent opens a backstage comparison with `checkpoint run begin`, not by smuggling planning instructions into a player turn. The command binds the exact open cube path, freezes protected state and a least-authority checkpoint grant, fixes one provider route for each role, and opens a private managed run. `run.json` is authoritative; `NEXT.md` names one current owner and command. `checkpoint run dispatch` embeds the exact current card and fixed route but invokes nothing. The parent records failed attempts or accepts exactly one validated output, after which Lacuna manufactures the next least-context card.

The judge sees candidate content and exact rollout beats but not generator provenance or notes. The compressor sees only the selected candidate, protected state, judgment, and narrow grant. The verifier sees proposal-visible custody only. A refusal is terminal for that run; a pass triggers parent-only kernel review and `ready-to-commit`. Only `checkpoint run commit` may apply or exactly recover the transition. Rejected candidates are omitted from later ordinary context while exact experiment and invocation artifacts remain external to the event ledger.

The lower-level `checkpoint begin`, `checkpoint card`, `checkpoint dispatch`, `checkpoint assemble`, `checkpoint review`, and `checkpoint commit` commands remain available to custom hosts. They expose the same source-bound exchange chain but do not provide an authoritative resume state or invocation custody. A serial single-context fallback is valid under either surface, but the host must not claim isolation or independent judging.

### Read-only inspection entrance

A UI, debugger, observability process, or model tool may call:

- `status`, `head`, `changes`, and `verify`;
- `snapshot` and perspective context;
- `worlds`, `particle-bank`, `particle-updates`, `particle-reconciliations`, `unknowns`, `canon`, and conflict reports;
- revision, consequence-repair, particle-update, and particle-reconciliation reviews;
- explanations;
- visible fair-play seals and receipts.

Read access must still be perspective-scoped. “Read-only” does not mean “safe to expose every hidden record.”

## Recommended ChatGPT-style host loop

A thin host wrapper can keep the model replaceable:

1. Route intent first. “Will you DM?” is session control; an action such as “I open the door” is a `play-turn`.
2. Resolve the selected campaign and emit the appropriate model brief when a fresh host needs orientation.
3. Verify the cube and require role readiness.
4. Capture the exact input bytes; never paraphrase them before request issuance.
5. Use `play start` for direct session control or `turn run begin` for a later turn.
6. Read `run.json.next_action` or audited `NEXT.md`. For a delegated owner, render `turn run dispatch --provider chatgpt` and deliver the complete embedded card to one role-dedicated context.
7. Save exactly one JSON object and call `turn run accept`; repeat from the newly audited state. Do not expose unrelated run files merely because the model asks.
8. Let only the parent call `turn run commit` when the status is `ready-to-commit`.
9. If accepted, display the receipt’s top-level `narration`; retain the run and invocation custody according to host policy.
10. If `NEXT.md` alone is damaged, call `turn run recover`. If an authoritative member, digest, head, or cube binding fails, stop; never hand-reconstruct the chain.
11. If refused or stale, do not present proposal text; begin a fresh run from retained exact input when the refusal requires it.
12. Periodically run `verify`; rebuild only from a passing ledger-only verification.

A connected Action/App/MCP/HTTP host can expose the same narrow state machine. Lacuna does not need to invoke the model itself to support a one-sentence player experience.

## Recommended managed checkpoint host loop

1. Decide backstage that a comparison is warranted; do not expose the checkpoint machinery as a player turn.
2. Run `checkpoint run begin` with the exact cube, trigger, run root, policy bounds, and complete per-role provider routes.
3. Read audited `NEXT.md` or `run.json.next_action`. Do not choose a different role or silently change a provider after begin.
4. Render `checkpoint run dispatch` and give its complete embedded card to exactly one role-dedicated context. A single-context fallback may execute the same cards serially, with no independence claim.
5. On provider/transport/timeout/refusal/invalid-output failure, call `checkpoint run record-failure`; the role remains current. On a candidate JSON return, save exactly one object and call `checkpoint run accept` with honest host-declared model metadata.
6. Repeat from the newly audited next action. Never give a worker the whole run directory merely because it can read files.
7. Stop on `verifier-refused`. Begin a fresh source-bound run after correcting the process or proposal rather than editing the old chain into a pass.
8. On `ready-to-commit`, let only the parent call `checkpoint run commit`. Readiness is an exact rollback-tested review, not a head reservation.
9. Present only the committed receipt’s top-level narration when appropriate. Retain, redact, archive, or delete the private run under explicit host policy; Lacuna supplies no automatic retention guarantee.

If `NEXT.md` alone is missing or altered, `checkpoint run recover` may recreate only that deterministic pointer after full authoritative audit. Any missing or mismatched request, card, output, invocation receipt, proposal, review, cube binding, or commit receipt is a stop condition, not a hand-repair invitation.

## Particle-bank wielding patterns

### Human adjudication

A human can inspect `particle-update-review`, supply one likelihood and optional rationale per required world, and apply the result through `particle-update` or a typed change-set. The CLI’s compact `world=likelihood` syntax omits per-world rationale; high-assurance hosts should prefer the typed JSON operation.

### Model-assisted assessment

A host may issue an unscoped director packet, ask a model to assess the complete bank, and commit `update_particle_bank` in the same turn as narration. The model does not get to alter the denominator, reuse a factor, or smuggle selection/pruning into the update. The host should retain the packet, proposal, and receipt because Lacuna stores arithmetic and provenance metadata, not the model’s private reasoning.

### Factor-ledger repair

When an applied assertion ends, a host can inspect `particle-bank` for `reweighting_debt`, request `particle-reconciliation-review`, and commit the returned head-bound replay through the CLI, direct Python, change-set JSON, or an unscoped director turn. The repair replays every still-active factor from the immutable epoch baseline in log space and preserves ended factors as excluded custody. It does not let the host edit likelihoods or author a new prior under the name of repair.

### External planner

A search process can call the direct Python/JSON interface, create or revise candidate worlds through separate governed operations, request a fresh bank review, and then reweight. It may also use reconciliation as deterministic reason maintenance after factor withdrawal. General proposal policy, stochastic sampling, factor-dependence modeling, and aesthetic validity remain outside the kernel. The checkpoint exchange now governs exact candidate/judgment/compression custody and narrow accepted mutation, but it does not generate candidates or certify their quality.

### Read-only observability

Dashboards may display normalized attention, ESS, entropy, maximum mass, valuation duplicates, divergent assessments, factor epochs, reconciliation readiness/history, and debt to authorized planners. They must label these as diagnostics and must not expose them to audience perspectives by treating “read-only” as “non-secret.”

## Why no bundled model client

Embedding one provider SDK in the cube would couple custody semantics to:

- rapidly changing API contracts;
- credential handling;
- retry and timeout policy;
- content retention policy;
- streaming behavior;
- model-specific tool syntax;
- deployment and billing concerns.

Those are host responsibilities. The stable seam is typed JSON plus process exit status. A local model, remote API, human editor, test fixture, or future MCP adapter can all use the same packet and proposal contract.

## Authority profiles

### Audience profile

An audience turn can record audience-visible epistemic changes such as claims, assertions, and questions. It cannot mutate hidden-world machinery.

### Director profile

A director receives separately labelled planner context and may use the ordinary hidden-world, constraint, commitment, and consequence operations authorized by the packet. An **unscoped** director may also submit one reviewed complete-population particle update or factor-ledger reconciliation. A world-scoped director cannot mutate the global bank because a filtered view is not a valid normalization or replay denominator. Every update remains subject to active single-use evidence, exact bank digest, complete assessment coverage, stale-state checks, and atomic rollback. Every reconciliation remains subject to epoch, baseline, complete factor-selection, log-replay, stale-review, and no-repeat checks.

A director is **not** a seal custodian. Fair-play seal creation, reveal, and void remain host-only even for privileged model turns.

### Administrative host

The host can invoke the full direct change-set/CLI surface. This is the highest-authority local role and must be kept out of player-controlled prompt text. Lacuna validates operation semantics; it cannot stop an authorized host from making a bad artistic or governance decision.

## Campaign UX that belongs above the kernel

A complete application may add:

- campaign templates and onboarding;
- player/character roster editing;
- visual clue and relationship maps;
- transcript retention and search;
- model selection and prompt assembly;
- streaming presentation;
- save/export/import workflows;
- external receipt anchoring;
- multiplayer authentication and permissions.

Those should call the same kernel rather than create a second informal canon store.

## Output discipline

For machine use, prefer JSON and treat `schema`, `event`, `overall_status`, `head`, and identifiers as protocol fields. For humans, use the Markdown renderers as views, not as authoritative storage.

The executable should continue to produce complete accepted-state receipts rather than vague “success” text. Conversely, it should not dump privileged state into a player-facing response merely because the host requested Markdown.

## Future adapters

Useful future adapters can remain thin:

- an MCP server exposing model brief, turn-run begin/status/accept/commit, managed checkpoint begin/status/dispatch/accept/failure/commit, context, visible receipt, and verification tools;
- an HTTP service that maps authenticated roles to existing perspective/host entrances;
- a game-engine bridge where the engine owns physical simulation and Lacuna owns epistemic custody;
- a transcript service that retains exact bytes and verifies Lacuna source digests;
- an external witness adapter that anchors fair-play receipt digests.

Each adapter should preserve the kernel’s distinctions and refusal behavior. It must not silently convert prose into canon, planner preference into truth, or model privilege into secret custody.


### Fresh-narrator handoff

A committed managed checkpoint exposes one normal source-bound continuation command:

```bash
./lacuna checkpoint run next-turn RUN_PATH \
  --player-input-file next-player-input.txt \
  --provider portable \
  --format markdown
```

It authenticates the checkpoint, requires the live checkpoint head, opens one audience-only solo ordinary turn, and emits `lacuna.checkpoint-continuation-dispatch.v2`. The parent gives that complete dispatch to a new narrator context. The narrator returns one exact ordinary turn proposal and has no accept, recovery, commit, or presentation authority. `checkpoint run continuation` binds an already-open qualifying turn, while `checkpoint run narrator-capsule` remains the checkpoint-only read-only compiler.

A parent may add `--public-history` using `lacuna.public-history.v2`. `history complete` binds a ledger-censused complete durable-turn set to the checkpoint; `history build` binds an explicit possibly partial ordered run list. Both are exact visible-text custody rather than ledger events, and neither covers uncommitted external chat.
