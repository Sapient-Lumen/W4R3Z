# Rev431 — exact docs inspection gets one tiny named row

## What changed

Micromax already had a good docs-discovery loop:

- `help docs TOPIC` opened one exact docs page
- `helppick` / `ed.doc-rows` / `ed.doc-section-rows` exposed searchable docs inventory
- rev430 made those docs rows summarize the document itself instead of leading with rev-note churn

But one tiny inspectability seam still remained: if a human, script, or future UI already knew the docs topic it cared about, there was still no tiny named exact-doc row. The only options were to open the page, search the whole docs inventory, or reimplement `find_doc_path()` + docs scanning locally.

Rev431 keeps the fix deliberately small:

- add `doc_detail_row(TOPIC)` in the editor core
- expose it as hostcall `ed.doc-detail-row`
- add plain `showdoc TOPIC` for humans
- reuse that same metadata for prompt completion of both `showdoc` and `help docs`

## Row shape

`doc_detail_row(TOPIC)` / `ed.doc-detail-row` return:

```
[topic title summary section path]
```

Example shape:

```
[
  "vision",
  "Vision",
  "**Micromax** is a small, embeddable, concatenative language intended to be a *sane* plugin/config/macro system.",
  "00–09 Project",
  "/.../docs/00-vision.md",
]
```

Returns `0` when the target does not resolve to a docs page.

## Why this matters

This is a small trust/flow improvement. If one docs page already matters enough to name explicitly, it should have one official machine-facing row instead of forcing callers to search `ed.doc-rows`, scrape picker text, or reopen the page just to inspect title/summary/section/path.

That keeps exact docs inspection aligned with the newer editor-side pattern already used by:

- `ed.command-detail-row`
- `ed.action-detail-row`
- `ed.word-detail-row`
- `ed.binding-detail-row`

## Focused tests

- `tests/test_editor_help_docs_buffers.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- generic `help` / `apropos` completion still does not advertise docs topics until a docs-specific path is chosen
- broader help/topic discovery is still stronger for search than for tiny grouped/count-aware script-facing snapshots
