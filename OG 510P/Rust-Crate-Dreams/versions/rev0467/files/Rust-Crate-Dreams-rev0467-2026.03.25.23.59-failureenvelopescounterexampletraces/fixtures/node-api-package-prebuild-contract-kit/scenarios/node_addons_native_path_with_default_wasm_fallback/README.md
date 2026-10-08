# Scenario: `node-addons` native path with `default` WASM fallback

The package uses package `exports` to make native loading explicit for Node environments while keeping a more universal `default` route that loads a WASM build when addons are disabled.

This scenario exists to keep the shipkit from flattening:
- “Node native path”
- “universal fallback path”
- and “same support promise everywhere”

into one fake compatibility result.
