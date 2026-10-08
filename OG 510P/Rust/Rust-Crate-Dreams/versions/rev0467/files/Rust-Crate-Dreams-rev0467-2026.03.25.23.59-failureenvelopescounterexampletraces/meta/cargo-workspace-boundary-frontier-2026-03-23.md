# Cargo workspace-boundary frontier refresh — 2026-03-23

This refresh keeps **P-0506 Cargo Workspace Boundary Doctor Kit** as the owner of workspace/config discovery incidents, but sharpens what the crate should now standardize.

## New frontier judgment

The missing crate is no longer just a doctor for “Cargo chose the wrong workspace.”
The sharper gap is a receiver-facing boundary bundle that keeps these truths separate:

1. **ancestor discovery** — which manifests/config candidates existed and where probing stopped;
2. **config layering** — which file layers, includes, env routes, and CLI routes existed and what precedence they had;
3. **invocation mode** — cwd auto-discovery, `--manifest-path`, manifest-command mode, or single-file package mode;
4. **diagnosis** — what concrete surprise family applies;
5. **advice** — what the smallest honest next action is.

## Why now

Recent official Cargo material makes this much more specific than older folklore:

- parent `Cargo.toml` and `.cargo/config.toml` poisoning is explicitly called out as a design problem;
- config include support and config-relative path rules are now documented;
- environment and `--config` precedence are explicit;
- single-file packages and manifest-command mode now document discovery/config differences.

That means the archive should reward crates that can emit **review artifacts** for those differences instead of only prose.

## Anti-duplication guardrail

Do not open a new adjacent Cargo workspace/config proposal unless it clearly escapes **P-0506** on all of these axes:

- not merely discovery trace or diagnosis,
- not merely config precedence reporting,
- not merely single-file package behavior,
- and not merely editor/CI wrapper advice.

Those now belong inside **P-0506**.
