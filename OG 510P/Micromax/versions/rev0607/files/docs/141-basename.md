# Basename (rev200)

Micromax now exposes the small micro-esque display option:

- `basename` (bool, default `false`)

## Current rule

- with the default `basename=false`, statusline-style filename displays prefer the full buffer path when one exists
- with `basename=true`, statusline-style filename displays prefer the basename instead
- buffers without a path still fall back to their ordinary buffer name

## Shared model impact

To keep future UIs/scripts honest, `status_model()` now carries both:

- `file_name` — the raw basename-ish compatibility field
- `display_name` — the effective user-facing label for status/infobar displays

That lets `$(filename)` and `showstatus` honor `basename` without breaking callers that still want the raw name plus `path`.

## Why this stayed small

This is intentionally a display-policy fix, not a tabbar subsystem or path-shortening engine. The goal is only to make the shared filename/status contract honest and inspectable.

## Reference

- micro options: `basename` controls whether infobar/tabbar displays show basename or full path
