# Serde unknown-field policy narrowing

Simulates a versioned config surface that used to ignore unknown fields and later adds a stricter policy like `deny_unknown_fields`.
The config may still look “Serde based”, but the compatibility window has narrowed in an operationally important way.

Why this matters:
- Serde documents that unknown fields are ignored by default for self-describing formats like JSON unless `deny_unknown_fields` is used.
- A persistence-surface crate should make that compatibility drift reviewable instead of hiding it in implementation details.

What this scenario should force:
- a compatibility-window change or manual-review boundary
- an explicit migration note when old configs can fail after upgrade
- a doctor warning such as `serde_unknown_field_policy_narrowed`
