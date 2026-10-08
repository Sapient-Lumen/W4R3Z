# Rev319 — shared docs/help inline-code delimiter metadata

Rev319 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small source-view inspectability win: visible docs/help rows can now report
which inline-code tokens used ordinary single backticks versus multi-backtick
delimiters.

## What is new

Each visible docs/help row now also includes:

- `single_backtick_code_entries`
- `multi_backtick_code_entries`
- `single_backtick_code_count`
- `multi_backtick_code_count`

Each `code_entries` item now also includes:

- `delimiter_kind` — `single-backtick` or `multi-backtick`

Top-level docs-cues snapshots now also report:

- `single_backtick_code_rows`
- `multi_backtick_code_rows`
- `single_backtick_code_count`
- `multi_backtick_code_count`

## Why this matters

Rev236 already made inline-code tokens inspectable, but future UIs/scripts/LLMs
still had to re-filter raw `delimiter_length` values to answer source-view
questions like:

- is this visible code span ordinary single-backtick markdown?
- which visible row contains a multi-backtick escape case because the body
  itself contains a backtick?
- how many visible code entries here still use ordinary single-backtick style?

Rev319 keeps the model tiny and inspectable:

- no richer markdown tree
- no renderer-only hidden state
- same shared equal-length backtick matcher the docs/help renderer already trusts

## Example

```python
{
  "code_rows": 1,
  "single_backtick_code_rows": 1,
  "multi_backtick_code_rows": 1,
  "single_backtick_code_count": 2,
  "multi_backtick_code_count": 1,
  "rows": [
    {
      "text": "Use `status`, ``tick`inside``, and `  padded  `.",
      "code_count": 3,
      "single_backtick_code_count": 2,
      "multi_backtick_code_count": 1,
      "code_entries": [
        {
          "delimiter_kind": "single-backtick",
          "delimiter_length": 1,
          "text": "status",
        },
        {
          "delimiter_kind": "multi-backtick",
          "delimiter_length": 2,
          "text": "tick`inside",
        },
        {
          "delimiter_kind": "single-backtick",
          "delimiter_length": 1,
          "text": "  padded  ",
        },
      ],
      "single_backtick_code_entries": [
        {"text": "status"},
        {"text": "  padded  "},
      ],
      "multi_backtick_code_entries": [
        {"text": "tick`inside"},
      ],
    },
  ],
}
```

## Contract shape

This metadata is built from the same tiny equal-length backtick scan Micromax
already used for visible docs/help inline-code cues and rev236's row-local
`code_entries`. Rev319 simply promotes the common single-vs-multi delimiter
question into a first-class shared surface instead of making future consumers
re-filter generic code entries by hand.
