# Postcard stable-wire claim versus serde-shape guard

Simulates a crate that persists bytes through Serde, but only some surfaces are backed by a stable external wire specification while others are merely “whatever Serde currently emits”.

Why this matters:
- Postcard documents a **stable wire format** as of `1.0.0`.
- `serde-reflection` can keep format descriptions under version control and catch unintended changes, but that is still a different kind of authority than a published external spec.
- Plain Serde derive attributes (`rename`, `alias`, `default`, `deny_unknown_fields`) help, but by themselves they do not automatically create a stable compatibility contract.

What this scenario should force:
- a `compatibility-authority.policy` entry that distinguishes `stable_external_spec`, `schema_snapshot_guarded`, and `serde_shape_best_effort`
- an honest compatibility summary that does not let one stable-wire surface masquerade as proof for all persisted bytes
- a doctor warning such as `stable_wire_claim_without_compatibility_authority`
