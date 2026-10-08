# AutoKey pack

`vhk gen-autokey-pack` generates a reviewable AutoKey/X11 adapter pack from a VHK project.

What it exports today:
- project `hotstrings:` as AutoKey **scripts** triggered by abbreviations
- project `bindings:` as AutoKey **scripts** triggered by simple hotkeys
- a `data/<project>/` tree of script files plus hidden sidecar metadata files
- `README.md` and `pack.json` so the resulting adapter lane is diffable/reviewable

Why scripts instead of phrases:
- VHK remains the execution engine
- generated AutoKey scripts shell back into `vhk run ...`
- return-mode hotstrings use `vhk run --print-return` and then re-insert the returned text through AutoKey's keyboard API

Example:

```bash
vhk gen-autokey-pack /path/to/project
vhk gen-autokey-pack /path/to/project ./build/autokey --return-send-mode shift-insert
vhk gen-autokey-pack /path/to/project ./build/autokey --allow-window-filter-approximation
```

Files written:
- `data/<project>/hotstrings/*.py` and matching `.*.json` sidecars
- `data/<project>/hotkeys/*.py` and matching `.*.json` sidecars
- `pack.json` manifest
- `README.md` import/review notes

Conservative boundaries:
- AutoKey is treated as an **X11 adapter lane**, not a compositor-neutral Linux backend
- only simple hotkeys are exported today
- AutoKey's window filter is one regex over window title **or** class, so VHK skips scoped selectors by default
- `--allow-window-filter-approximation` opts into that broader AutoKey behavior for simple `class`-only or `title`-only selectors
- selectors that would broaden scope even further (for example `class` + `title` intersections, `workspace`, or `app_id`) are skipped with explicit reasons
- invalid `title_regex` filters are skipped instead of emitting broken AutoKey metadata

Import workflow:
1. Review `pack.json` and the generated scripts/sidecars.
2. Point AutoKey at the generated `data/<project>/` folder.
3. Restart AutoKey after importing/copying the files because AutoKey does not monitor its directories live.

Return send modes:
- `keyboard`
- `ctrl-v`
- `ctrl-shift-v`
- `shift-insert`
- `selection`

These map onto AutoKey's documented keyboard send modes and let you choose whether returned text should be typed or pasted through one of AutoKey's clipboard/X11 insertion paths.

## Linting

`vhk lint-project` now warns before AutoKey export when a binding or hotstring `when:` selector would be skipped or widened in the AutoKey lane:

- `AUTOKEY_SCOPE_APPROXIMATION_REQUIRED` — the selector can only be exported behind `--allow-window-filter-approximation` because AutoKey matches one regex against title **or** class
- `AUTOKEY_SCOPE_EXPORT_GAP` — the selector uses fields AutoKey cannot express honestly in `windowInfoRegex`

That keeps the AutoKey pack reviewable *before* you write files, not only after you inspect `pack.json`.
