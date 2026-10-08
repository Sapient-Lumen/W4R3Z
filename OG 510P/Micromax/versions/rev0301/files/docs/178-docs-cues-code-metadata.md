# Rev236 — shared docs/help code-span metadata

Rev236 extends the shared `docs_cues_model(lines, cols)` / `ed.docs-cues`
snapshot with explicit parsed inline-code metadata.

## What is new

Per visible docs/help row, the model now also exposes:

- `code_entries`
- `code_count`

Each `code_entries` item includes:

- `kind` (`"code"`)
- `start`, `end`
- `body_start`, `body_end`
- `delimiter_length`
- `text`

Top-level docs-cues snapshots now also report:

- `code_rows`
- `code_entry_count`

## Why this exists

Micromax already used tiny inline-code parsing for markdown precedence and
visible source-view cues, but future UIs/scripts/LLMs still had to scrape raw
backticks to answer practical questions like:

- what inline code token is visible on this row?
- which visible span uses doubled backticks because the body contains a backtick?
- is this code text padded inside the delimiters in source view?

This keeps the policy tiny and inspectable:

- same shared equal-length backtick scan as the existing code-span helpers
- no richer markdown AST
- no renderer-only hidden state

## Example shape

```python
{
  "code_rows": 1,
  "code_entry_count": 2,
  "rows": [
    {
      "text": "Use `status` and ``tick`inside``",
      "code_count": 2,
      "code_entries": [
        {
          "kind": "code",
          "start": 4,
          "end": 12,
          "body_start": 5,
          "body_end": 11,
          "delimiter_length": 1,
          "text": "status",
        },
        {
          "kind": "code",
          "start": 17,
          "end": 32,
          "body_start": 19,
          "body_end": 30,
          "delimiter_length": 2,
          "text": "tick`inside",
        },
      ],
    },
  ],
}
```
