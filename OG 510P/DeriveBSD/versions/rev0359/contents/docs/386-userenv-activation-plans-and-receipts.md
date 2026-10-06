# UserEnv activation plans and receipts (profiles, generations, atomic switch)

DeriveBSD already treats host activation as a derived operation with receipts.
The *user environment* should get the same treatment:
- reversible (generations)
- atomic activation (pointer flip)
- no ambient authority escalation
- evidence for “what changed?”

This doc tightens `docs/162-user-environments.md` by defining a minimal **plan/receipt** surface.

## Design goals

- **Atomic switch**: activation is a single pointer update (symlink flip or mount switch).
- **No privilege creep**: UserEnv can only touch user-scoped paths.
- **Receipted activation**: success/failure is recorded with enough context for debugging.
- **Composable**: UserEnv can be derived from project DevShells, but remains user-scoped.

## The objects

### 1) `userenv.activate.plan`
A plan that states *exactly* what activation will do:
- which user (uid/name)
- which UserEnv generation digest
- activation mode (symlink/mount)
- profile path(s)
- which entrypoints are updated (PATH, shell rc hooks, desktop integration)

Schema: `spec/userenv.activate.plan.schema.json`
Example: `spec/examples/userenv.activate.plan.json`

### 2) `userenv.activate.receipt`
A receipt emitted after attempting activation:
- previous generation digest (if any)
- new generation digest
- outcome + error codes
- linkage to the triggering change set (if any)

Schema: `spec/userenv.activate.receipt.schema.json`
Example: `spec/examples/userenv.activate.receipt.json`

## Recommended activation model (Nix-style)

Borrow the ergonomic win from Nix profiles:

- A stable per-user pointer (e.g., `~/.derive/profile`) points to the current generation.
- A new generation is materialized as an immutable store-backed environment.
- Activation updates the pointer **atomically**.

This keeps rollback trivial:
- `derive user rollback --to <generation>` is just another pointer update, with a receipt.

## Safety defaults

- UserEnv activation must not:
  - write outside user-owned datasets
  - add new device/network authority
  - bypass portals/brokers for dynamic access

UserEnv is “what tools and dotfiles exist”, not “what authority exists”.
Authority changes remain governed by:
- promise profiles
- portal grants
- network leases
- device grants

## Integration points

- User record + portable homes: `docs/269-portable-home-areas-and-user-records.md`
- AppVM storage contract (private/volatile/home): `docs/270-appvm-storage-private-volatile-and-home-areas.md`
- Pins/roots/GC (user env generations as GC roots): `docs/175-pins-roots-and-garbage-collection.md`
- Permission Center (visibility into grants independent of UserEnv): `docs/371-permission-center-and-authority-introspection.md`

## References

- Nix manual: profiles and user environment generations (atomic symlink flip):
  - https://nix.dev/manual/nix/2.33/package-management/profiles.html
- Nix Pills: user environments and profile generations:
  - https://nixos.org/guides/nix-pills/03-enter-environment.html

Last updated: 2026-02-27r109
