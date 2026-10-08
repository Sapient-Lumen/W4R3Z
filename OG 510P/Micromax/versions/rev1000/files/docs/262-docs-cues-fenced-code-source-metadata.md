# Rev320 — docs-cues fenced-code source metadata

Rev320 extends `docs_cues_model(lines, cols)` / `ed.docs-cues` with one more
small source-view inspectability win for docs/help buffers: visible fenced-code
rows can now report both the fence-marker family they belong to and whether the
owning fenced block carries a language/info string.

## What is new

Each visible docs/help row now also includes:

- `backtick_fenced_code_entries`
- `tilde_fenced_code_entries`
- `language_fenced_code_entries`
- `bare_fenced_code_entries`
- matching row-local `*_count` fields

Each `fenced-code` entry now also carries:

- `marker_kind` — `backtick` or `tilde`
- `has_language` — `1` or `0`

For fenced body/closer rows, Micromax now also propagates the opener's tiny
block-level metadata so those rows still expose the owning block's:

- `marker`
- `marker_kind`
- `marker_count`
- `info_string`
- `language`
- `has_language`

Top-level docs-cues snapshots now also report:

- `backtick_fenced_code_rows`
- `tilde_fenced_code_rows`
- `language_fenced_code_rows`
- `bare_fenced_code_rows`
- `backtick_fenced_code_count`
- `tilde_fenced_code_count`
- `language_fenced_code_count`
- `bare_fenced_code_count`

## Why this matters

Rev310 already made visible fenced/html/indented block rows inspectable and
already exposed opener-level fence details. But future UIs/scripts/LLMs still
had to re-filter generic `fenced_code_entries` and special-case opener rows to
answer source-view questions like:

- is this visible fenced row backtick-based or tilde-based?
- which visible rows belong to language-tagged fenced blocks rather than bare
  fences?
- does this body/closer row still belong to the same `python` fence that opened
  above it?

Rev320 keeps the parser/policy small:

- no richer markdown AST
- no renderer-only hidden state
- same shared fence scan the docs/help renderer already trusts

## Example

```python
{
  "backtick_fenced_code_rows": 3,
  "tilde_fenced_code_rows": 3,
  "language_fenced_code_rows": 3,
  "bare_fenced_code_rows": 3,
  "rows": [
    {
      "text": "```python",
      "fenced_code_count": 1,
      "backtick_fenced_code_count": 1,
      "language_fenced_code_count": 1,
      "backtick_fenced_code_entries": [
        {
          "role": "opener",
          "marker": "`",
          "marker_kind": "backtick",
          "marker_count": 3,
          "info_string": "python",
          "language": "python",
          "has_language": 1,
        },
      ],
    },
    {
      "text": "print(\"hi\")",
      "fenced_code_count": 1,
      "backtick_fenced_code_count": 1,
      "language_fenced_code_count": 1,
      "backtick_fenced_code_entries": [
        {
          "role": "body",
          "marker_kind": "backtick",
          "language": "python",
          "has_language": 1,
        },
      ],
    },
    {
      "text": "~~~",
      "fenced_code_count": 1,
      "tilde_fenced_code_count": 1,
      "bare_fenced_code_count": 1,
      "tilde_fenced_code_entries": [
        {
          "role": "opener",
          "marker": "~",
          "marker_kind": "tilde",
          "language": "",
          "has_language": 0,
        },
      ],
    },
  ],
}
```

## Contract shape

This metadata is built from the same tiny fenced-block scan Micromax already
used for visible docs/help block cues. Rev320 simply promotes two common
source-view questions into first-class shared fields:

- fence family (`backtick` vs `tilde`)
- block info presence (`language` vs bare)

That keeps future archive-first inspection honest without turning docs/help
parsing into a full markdown tree.
