# Clean default startup

Before rev328, the editor could open files and still feel slightly broken on first run.

The concrete problem was small but user-visible: the default `core` plugin contained one nested paren comment in `plugins/core/init.mx`, and Micromax paren comments are intentionally non-nesting. The file still parsed, but the `init` lifecycle later tripped over a stray `)` token, so normal startup surfaced a `plugin load failed: core: Unknown word: )` warning even though the editor could keep running. That was exactly the wrong default feel for the current product direction.

## What changed

Rev328 makes the default startup path boring again.

- the broken nested paren comment in the core plugin was flattened
- the default plugin tree now loads cleanly during normal startup
- success-path plugin lifecycle chatter was removed from the default `core` and `capdemo` plugins, so startup infobars are reserved for user-relevant information instead of internal "loaded" noise
- focused tests now pin down that the repo's default plugin set loads without `load_errors`, and that `python -m micromax_editor --dump-screen ...` no longer surfaces default plugin chatter or failure warnings

## Why this matters

This is a small trust win, but it is a real one.

The taste/trust/flow note already says **trust first** and describes startup as something that should be boring. That does not only mean "avoid crashes." It also means avoiding startup states that ask the user to mentally downgrade the product on first contact. A prototype can absolutely be minimal; it should not look half-broken by default.

A clean startup also improves **taste**. When the bottom chrome is quiet unless something actually needs attention, the UI feels more intentional.

## What this does *not* solve yet

Rev328 is intentionally tiny. It does **not** yet provide:

- a first-class plugin health inspector
- a richer degraded-mode startup summary when an optional plugin fails
- an explicit enable/disable workflow for individual plugins
- a more polished theme/status treatment for warnings vs ordinary info

Those are still good follow-up trust tasks.

## Practical rule going forward

For default startup surfaces:

- success should usually be silent
- degradation should be explicit but calm
- failures should name the thing, the file, and the next action when possible

That rule is small, but it aligns the repo with the editor's actual goal: not merely "it worked once," but "it feels safe to begin here."
