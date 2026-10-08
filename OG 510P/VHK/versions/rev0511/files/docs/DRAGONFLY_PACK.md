# Dragonfly voice-command pack

`vhk gen-dragonfly-pack` generates a small, reviewable Dragonfly integration pack for a VHK project.

What it writes:
- `integrations/dragonfly/_vhk_<project>_commands.py` — Dragonfly command module
- `integrations/dragonfly/commands.json` — spoken-form / macro ledger
- `integrations/dragonfly/README.md` — local handoff notes

Design rules:
- Dragonfly is an **adapter**. The generated Python module only launches `vhk run ...`.
- VHK remains the only automation runner.
- Spoken phrases come from macro/preset `voice_phrases` when present; otherwise VHK derives fallback phrases from names.
- Prompt-overlay presets are skipped by default because spoken invocation plus an unexpected interactive form is a poor default operator experience. Use `--include-prompt-entries` when that tradeoff is actually desired.
- Macro/preset `voice_when` can now scope generated commands to Dragonfly `AppContext(...)` groups, but only for the subset VHK can translate honestly today (`class`, `title`, `instance`, `window_role`). Unsupported selector fields are skipped instead of silently widening scope.
- Repeated spoken phrases are deduped **per effective Dragonfly context**, not globally, and the generated module now uses stable command ids internally so the same phrase can exist in different Dragonfly grammars when the contexts are distinct.
- `vhk lint-project` now warns when two exported Dragonfly commands would still claim the same spoken phrase in the same effective context. It also now gives phrase-quality guidance when explicit `voice_phrases` normalize oddly, collapse to nothing, or stay as very short global commands.

Example:

```bash
vhk gen-dragonfly-pack /path/to/project
vhk gen-dragonfly-pack /path/to/project ./voicepack --command "python -m vhk.cli"
```

Macro metadata example:

```yaml
name: deploy_release
voice_phrases: [ship build, deploy build]
voice_when:
  class: Firefox
  title: CI Dashboard
presets:
  - name: prod
    voice_phrases: [deploy production]
    voice_when:
      class: Firefox
      title: Production
steps:
  - type: Return
    value: ok
```

This lane is intentionally Linux/X11-aware rather than magical: Dragonfly's own action stack is still X11-oriented, so this export is a useful optional route for X11-heavy environments, not a promise that VHK voice control is compositor-agnostic.

## Linting

`vhk lint-project` now emits `VOICE_CONTEXT_EXPORT_GAP` when a macro or preset uses `voice_when` fields that Dragonfly cannot export honestly. It also continues to emit `VOICE_PHRASE_COLLISION` when two spoken phrases still collide inside one effective Dragonfly context, plus `VOICE_PHRASE_EMPTY_AFTER_NORMALIZATION`, `VOICE_PHRASE_NORMALIZED`, `VOICE_PHRASE_REDUNDANT_VARIANT`, and `VOICE_PHRASE_SHORT_GLOBAL` for awkward literal-phrase cases that deserve review before export.
