# Research — route drift and export surfaces

## Product lesson

The best Linux automation tools do not pretend one mechanism should own all automations.

- phrase/snippet tools emphasize text packages, app filters, and include/exclude scope
- remappers emphasize low-latency always-on key transforms close to input devices or compositor context
- watcher/service patterns separate event observation from macro execution
- Wayland helper/capture/injection edges remain conditional enough that they should stay explicit seams

## VHK implication

`macro_route_profiles` answered “who should own this macro?”

The missing follow-on question was: “what concrete Linux-native shipping surface should that macro promote into?”

That gap is now modeled as `macro_export_candidates`, which is intentionally practical:

- `text-package-export`
- `remapper-export`
- `watcher-service-export`
- `helper-route-dossier`
- `launcher-surface-export`

## Why lint should care

If route ownership only appears during design review, projects drift:

- key transforms stay trapped in generic runner YAML
- snippets stay character-replay macros instead of text-tier assets
- event-driven automations stay hidden inside trigger-owned macros
- Wayland capture/pointer flows overpromise portability

So VHK now surfaces route drift directly in `lint-project` as advisory feedback rather than waiting for a later planning pass.
