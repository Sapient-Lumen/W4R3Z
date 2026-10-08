# `pluginpick` missing-manager feedback (rev582)

Rev582 closes one small trust seam in the plugin inspection loop: grouped `pluginpick` submit failures now distinguish **an unavailable plugin subsystem** from **a real zero-match plugin query**.

## What changed

Before rev582, `pluginpick QUERY` already did the right thing when a real plugin manager existed and the query matched nothing:

- `pluginpick QUERY: 0 plugin(s)`

But the exact same zero-count fallback also fired when **no plugin manager existed at all**. That was less honest than the surrounding plugin loop, which already kept absent-manager failures explicit in:

- `plugin reload: no plugin manager`
- `plugin info: no plugin manager`
- `plugin errors: no plugin manager`
- rev581's command-bar previews like `showplugins` -> `plugin manager not available`

## New behavior

`pluginpick` still opens the familiar grouped picker prompt, but submit now keeps the missing subsystem typed:

- no manager: `pluginpick: no plugin manager`
- empty configured manager + unmatched query: `pluginpick QUERY: 0 plugin(s)`

## Why it matters

This is tiny, but it improves trust in the calm headless/safe-startup case:

- future humans/LLMs no longer have to guess whether plugin search failed because the query missed or because plugins are unavailable entirely
- grouped plugin inspection now stays aligned with the rest of the plugin runtime dialect
- headless tests and logs preserve the failed surface name and the real subsystem state

## Checks

Focused tests now pin both states:

- unavailable manager -> `pluginpick: no plugin manager`
- empty configured manager miss -> `pluginpick QUERY: 0 plugin(s)`
