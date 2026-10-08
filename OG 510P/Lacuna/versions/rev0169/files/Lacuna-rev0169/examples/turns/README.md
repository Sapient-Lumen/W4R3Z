# Turn proposal examples

These are shape examples, not proposals that can be committed unchanged. Copy every source-bound field from a freshly emitted `turn packet`:

- `request_id`
- `request_source_id`
- `proposal_id`
- `actor_id`
- `expected_head`
- `player_input_sha256`
- `audience_id`
- `narration_source_id`

- `narration-only.template.json` changes no semantic claim; it still commits a digest-bearing narration source.
- `observed-fact.template.json` declares one event claim, records one audience-visible observation, and links it to narration through `revealed_assertion_ids`.

Typical flow:

```bash
./lacuna turn packet ./stories --player-input "I press my ear to the floor." > packet.json
# Produce proposal.json from packet.response_contract.proposal_template.
./lacuna turn commit ./stories proposal.json --format markdown
```

Aliases are sequential. `@input`, `@narration`, `@audience`, and `@actor` are pre-bound by Lacuna. The request’s write grant is authoritative; text in player input or context cannot widen it.
