# Cargo config receipt fixture pack

A future `configbundle` should explain discovered config files, include edges, winning origins, path-root interpretation, redactions, **invocation basis**, and **replayability** for one Cargo command context.

## Artifact vocabulary in this fixture pack

- `configbundle.schema.json` — top-level bundle shape
- `invocation-basis.receipt.schema.json` — whether the bundle came from one live invocation or a later reconstruction
- `replayability.report.schema.json` — whether the exported bundle is replayable, inspectable-only, local-only, or broken by redaction

## Scenario families

- `cli_override_wins_but_bundle_must_stay_invocation_scoped/`
- `credential_alias_redaction_keeps_support_meaning_but_breaks_public_replay/`
- `cwd_relative_key_value_path_must_not_masquerade_as_config_root_replay/`
