# Host adapter compatibility v0

Revision 176 adds a host-adapter compatibility lane to the executable ViewFS core. This lane models the surfaces that legacy applications and operating-system adapters expect: mounted projections, stat-like metadata, inode-like aliases, extended attributes, filesystem watcher events, advisory locks, rename and tempfile promotion flows, placeholder hydration, and external-app handoff.

The design rule is intentionally narrow: host compatibility artifacts are projections and adapters, not ViewFS authority. A FUSE mount, ProjFS virtualization root, File Provider placeholder, `stat` result, inode number, xattr, watcher event, advisory lock, pending rename, staged tempfile, hydration ticket, or open-with handoff may help a legacy tool interoperate. None of those artifacts may silently become a live handle, root namespace authority, canonical object identity, disclosure approval, policy label, write authority, durable grant, or proof that host effects have completed.

## Record families

| Record family | Minimal fields in fixtures | Anti-collapse rule |
|---|---|---|
| `adapter_mounts` | `id`, `status`, `provider`, `policy_epoch`, `current_epoch`, `sandbox_ok`, `authority` | mount/projector state is not root or ambient authority |
| `stat_projections` | `id`, `status`, `source_handle`, `fields`, `hidden_fields`, `authority` | stat-like metadata is not read authority or complete object truth |
| `inode_aliases` | `id`, `status`, `alias_epoch`, `current_epoch`, `target_handle`, `collision`, `authority` | inode numbers and aliases are not stable object identity by themselves |
| `xattr_parcels` | `id`, `status`, `name`, `allowed_names`, `sensitive_names`, `redacted`, `source_handle`, `authority` | xattrs are not policy, classification, or disclosure authority |
| `watcher_subscriptions` | `id`, `status`, `event_epoch`, `current_epoch`, `cursor_state`, `allowed_events`, `authority` | watcher events are notifications, not opens or authority refreshes |
| `lock_tokens` | `id`, `status`, `mode`, `target_handle`, `required_right`, `range_conflict`, `authority` | advisory locks coordinate writers; they do not grant write authority |
| `rename_plans` | `id`, `status`, `approval_cut`, `source_handle`, `target_parent_handle`, `cross_mount`, `authority` | rename plans do not prove atomic completion or bypass mount boundaries |
| `tempfile_leases` | `id`, `status`, `flush_proof`, `approval_cut`, `target_handle`, `authority` | staged tempfiles are not committed objects until promotion succeeds |
| `hydration_tickets` | `id`, `status`, `placeholder_epoch`, `current_epoch`, `network_verified`, `source_handle`, `result_handle`, `authority` | placeholder/hydration tickets are not read authority or network trust by themselves |
| `external_app_handoffs` | `id`, `status`, `portal_approved`, `redacted`, `target_handle`, `authority` | open-with/export handoff is scoped and does not become a persistent grant |

## Checked operations

The lane adds ten checked operations: `admit_adapter_mount`, `render_stat_projection`, `resolve_inode_alias`, `read_xattr_parcel`, `deliver_watcher_event`, `acquire_lock_token`, `execute_rename_plan`, `promote_tempfile_lease`, `hydrate_placeholder`, and `handoff_external_app`.

Each operation has one positive fixture and at least three refusal fixtures. The negative specimens are deliberately about laundering risks: root-authority claims, hidden metadata leaks, inode identity claims, xattr-as-policy claims, watcher-as-open claims, lock-as-write claims, rename completion claims, tempfile committed-state claims, hydration-as-read claims, and external-handoff persistent-grant claims.

## Design pressure

Host adapters are useful exactly because they make ViewFS look like an ordinary filesystem to ordinary tools. That is also their danger. The compatibility layer must therefore render host expectations as typed projections over current ViewFS authority rather than treating the host's path, inode, metadata, notification, lock, or handoff vocabulary as native authority.
