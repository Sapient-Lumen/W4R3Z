# Campaign library protocol

## Why campaigns exist

A cube is a precise storage object; it is not a pleasant thing for a person to browse. A campaign supplies the smallest human-facing wrapper that answers:

- What story am I opening?
- Which campaign is currently selected?
- Which agent IDs represent the operator, player, and narrator?
- Where is the underlying cube?

It does not answer what is true inside the story. That remains the cube’s job.

## Create and select

```bash
./lacuna campaign create ./stories lantern-room \
  --title "The Lantern Room" \
  --summary "A bell, a broken cup, and three surviving explanations."

./lacuna campaign create ./stories glass-house --title "The Glass House"
./lacuna campaign list ./stories
./lacuna campaign select ./stories glass-house
./lacuna campaign show ./stories
```

The first campaign is selected automatically. Later campaigns are explicit choices.

A campaign is addressable by exact slug or campaign ID. Lacuna does not fuzzy-match titles; ambiguity should be visible rather than guessed through.

## Use a selected library as a cube

After selection, normal commands accept the library directory directly:

```bash
./lacuna status ./stories
./lacuna context ./stories --agent-id player
./lacuna turn packet ./stories --player-input "I open the red door."
./lacuna verify ./stories
```

`campaign path` prints the exact cube directory for integration with tools that do not understand libraries.

## Default participants

Campaign creation registers four agents:

- `system` — the Lacuna runtime;
- `user` — the operator/owner;
- `player` — the default audience and player perspective;
- `narrator` — the default actor for turn proposals.

All IDs and labels are configurable during creation. IDs must be distinct.

## Custody boundary

`campaign.json` and `lacuna-library.json` are strict, atomically replaced JSON manifests. They are not ledger events. Renaming a campaign must never be mistaken for changing world history.

A future application may event-source campaign administration separately. It should not insert UI preference changes into the story’s epistemic ledger.
