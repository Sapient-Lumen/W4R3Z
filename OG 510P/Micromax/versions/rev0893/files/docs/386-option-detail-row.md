# Option detail row (rev444)

Rev444 closes one small symmetry gap in Micromax's configuration-inspection loop.

Micromax already had the right **broad** option surface:

- plain `show` for humans
- `ed.option-inventory-rows` for scripts and future UIs
- ordinary command-bar completion for option names and likely values

But one small inspectability seam still lingered underneath that model: future humans/LLMs could answer *what options exist right now?* yet still had to reconstruct the next exact question by hand:

> tell me about **this one option** right now

That is exactly the kind of tiny follow-up that should have one stable named row.

## New shared row

```text
option_detail_row(NAME)
ed.option-detail-row
```

Returns:

```text
[query canonical value default kind local_override? doc] | 0
```

Where:

- `query` preserves the exact spelling the caller asked for
- `canonical` is the resolved canonical option name
- `value` is the current effective value in the active buffer context
- `default` is the canonical default value
- `kind` is the same tiny type label plain `show` already uses
- `local_override?` is `1` when the current buffer overrides the canonical option locally
- `doc` is the exact doc string attached to the queried spelling

The resolution policy stays intentionally small and honest:

- canonical names inspect themselves directly
- aliases stay explicit instead of silently disappearing
- unknown names return `0` / `showoption: no such option: NAME`

## New plain command

```text
showoption NAME
```

Examples:

```text
option readonly [bool] value=true default=false (local): disallow edits and saves in the current buffer unless locally overridden
option savehistory -> history.persist [bool] value=false default=false: remember prompt/command history between sessions (requires cap.persist)
```

## Why this helps

This is a trust/flow change, not a larger config redesign.

It keeps Micromax's option inspection surfaces structurally consistent:

- broad register: `show` / `ed.option-inventory-rows`
- exact register: `showoption NAME` / `ed.option-detail-row`

That means future humans, scripts, and LLMs no longer need to scrape command text or manually rejoin alias/default/local/doc state just to answer one small exact configuration question.
