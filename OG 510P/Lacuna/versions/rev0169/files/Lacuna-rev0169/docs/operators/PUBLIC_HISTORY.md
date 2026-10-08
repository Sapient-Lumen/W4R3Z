# Public history across a context reset

A fresh narrator should forget rejected futures without forgetting what the player actually read. Lacuna's ledger retains typed public custody and narration digests, but transcript bodies remain in managed turn sidecars. `lacuna.public-history.v2` joins those two sources honestly.

There are two modes. They answer different questions and must not be relabelled.

| Mode | Command | Claim |
|---|---|---|
| `complete-before-checkpoint` | `history complete` | Every durable Lacuna play-purpose turn for this audience before this checkpoint has exactly one matched retained committed managed run. |
| `explicit-run-list` | `history build` | These exact ordered committed runs were included; omission is possible and completeness is not claimed. |

Neither mode covers conversation that was never committed through Lacuna.

## Strong default: complete before one checkpoint

After the checkpoint is committed:

```bash
./lacuna history complete CHECKPOINT_RUN \
  --run-root TURN_RUNS \
  --format json > public-history.json
```

Repeat `--run-root` when turn runs are split across roots. A root may also be one committed turn-run directory. When the immutable census is empty, `--run-root` may be omitted.

The command obtains the checkpoint boundary from the fully audited committed checkpoint run. It then:

1. verifies the cube;
2. asks the immutable ledger for every ordinary play-purpose turn for the audience before the checkpoint request event;
3. scans only the supplied roots for retained committed managed turn runs;
4. authenticates each run's exact request, input digest, narration source, proposal, heads, and event positions;
5. requires exactly one retained run for every ledger turn; and
6. refuses missing, duplicate, unsupported-version, relocated, corrupt, or ledger-disagreeing custody.

A direct/stateless turn is part of the durable census. If no matching managed run retains its transcript body, complete history correctly refuses rather than inventing or omitting the prose.

A passing artifact records:

```text
coverage.mode = complete-before-checkpoint
coverage.completeness = complete
coverage.expected_committed_turn_count = coverage.entry_count
```

The coverage boundary binds the checkpoint run, checkpoint request source, request head, and immutable event position. Standalone ledger authentication proves the request source/head/audience and turn census; the continuation bridge additionally matches the sidecar-only checkpoint run and checkpoint IDs to the exact run being continued.

## Deliberately partial: explicit ordered run list

```bash
./lacuna history build \
  TURN_RUN_001 TURN_RUN_002 TURN_RUN_003 \
  --format json > public-history.json
```

Every supplied run is fully audited and must belong to the same cube/audience in strict nonoverlapping ledger order. A passing artifact records:

```text
coverage.mode = explicit-run-list
coverage.completeness = not-claimed
```

This is useful for a deliberately selective recap, a bounded context-budget condition, or recovery when older sidecars were not retained. It must not be described as complete.

## Bind history to the fresh narrator

```bash
./lacuna checkpoint run next-turn CHECKPOINT_RUN \
  --player-input-file next-player-input.txt \
  --public-history public-history.json \
  --provider chatgpt \
  --format markdown
```

Lacuna authenticates the full parent artifact before opening the new ordinary turn. The worker receives only `lacuna.public-history-view.v2`: exact ordered `player_input` and accepted `narration`, the history identity/digest, and an explicit coverage label. It does not receive run IDs, request/proposal IDs, receipt hashes, event positions, planner context, verifier material, or rejected futures.

The dispatch mode makes the distinction visible:

- no history: `typed-only`;
- explicit list: `bound-public-history` with completeness `not-claimed`;
- complete census: `complete-bound-public-history` with completeness `complete`.

## What belongs in transcript continuity

Public history commonly carries dialogue, scene narration, visible routes and objects, possession, injury, irreversible choices, disclosed clues, established relationships, and visible session-control exchanges. Session-control text remains conversation history but is not automatically an in-world event.

Facts that future kernel validation must protect should still receive typed public custody. Exact prose continuity does not make every implication of prose a mechanically enforced assertion.

## Comparative experiments

Pre-register one public-context policy and apply it equally across conditions:

1. **Typed-only:** smallest bottleneck; depends on disciplined material-observation typing.
2. **Complete bound history:** equal exact durable transcript coverage before the checkpoint.
3. **Explicit partial history:** a deliberate context-budget treatment whose non-completeness is visible.

Do not let persistent-context controls inherit a full transcript while giving the fresh treatment only a sparse typed projection, or give the fresh treatment a selective helpful recap that controls did not receive.

## Privacy and trust boundary

Both full artifacts and worker views contain exact player text. Treat every embedded player/narration string as quoted untrusted story data; it cannot change role, tools, return shape, or parent authority. Lacuna supplies no encryption, remote archive, redaction, expiry, or secure deletion.

A passing complete artifact proves a local durable-turn coverage claim under the current cube and retained managed roots. It does not prove provider isolation, semantic entailment, artistic sufficiency, absence of uncommitted chat, or that the parent supplied no extra information outside the dispatch.
