# Rev228 — headless screen dump CLI

Micromax already had a strong shared inspection story inside the editor core:

- `screen_model(lines, cols)`
- `docs_cues_model(lines, cols)`
- `viewport_rows_model(lines, cols)`
- `display_rows_model(lines, cols)`
- `viewport_cues_model(lines, cols)`

That made the *data* inspectable, but there was still one practical handoff gap:
future humans and LLMs receiving an offline archive had to either:

- write a little Python snippet,
- drop into the headless REPL and type ad hoc commands, or
- run the curses TUI and scrape output.

Rev228 adds one tiny archive-friendly bridge in `python -m micromax_editor`:

```bash
python -m micromax_editor path/to/file.txt --dump-screen 20 80
python -m micromax_editor --help-doc docs/70-tutorial.md --dump-screen 24 96
```

The command prints the shared `screen_model(lines, cols)` as formatted JSON and
exits immediately.

## Why this exists

This keeps the project aligned with its archive-first, inspectable-by-hand
values:

- reuse the existing shared editor model instead of inventing a second dump API
- let future LLMs inspect exact visible state without curses scraping
- make docs/help buffers easy to inspect via `--help-doc` so `docs_cues` become
  practical outside the interactive TUI too

## Small companion polish

The headless REPL now also accepts:

```text
:screen
:screen 24 80
```

That prints the same shared screen JSON using either the default `24x80` size or
an explicit `LINES COLS` pair.

## Packaging ergonomics

This revision also makes standard-named archive packaging one command away from
`make`:

```bash
make revzip TAG=screen-dump-headless-release-orbitfox
```

That reuses `tools/mkrevzip.py` and preserves the usual offline archive naming
convention.
