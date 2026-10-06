# Portable home areas and embedded user records (systemd-homed lesson)

Most systems treat “user accounts” as *host configuration* and “home directories” as *mutable state*.
That split makes roaming users, laptop recovery, and multi-machine personal workflows awkward — and it also
creates a security footgun: **admins can often read user data at rest** simply because the home directory is always mounted.

systemd-homed popularized a different framing: a *human account* can be represented by a **portable home area** that
encapsulates both:
- the user’s **data store** (the actual home contents)
- an embedded **user record** (identity metadata)

DeriveBSD can steal the high-level lesson without importing Linux-specific plumbing.

## Concept

Define a first-class artifact family:

- **`home.area`**: a portable, encrypted home storage object (ZFS dataset, file image, or other backend)
- **`user.record`**: a canonical, signed identity record embedded in (or bound to) the `home.area`

The key property is: **the home area is self-describing**.

Portability goal:
- A user can move a `home.area` between machines (or restore from backup) and the system has enough metadata to
  mount/unlock it and present the identity.

Security goal:
- When the user is not logged in, their home area can be **unmounted + keys unloaded**.

## How this fits DeriveBSD

### 1) Host remains boring
The host only needs:
- a minimal “home area manager” (activation-time + login-time glue)
- a policy rule for *where* home areas may be attached/unlocked

Everything else is artifacts:
- `home.area` creation/format selection
- user environment generation (packages/dotfiles)
- optional backup/replication plans

### 2) Lock/Plan integration
Treat a `home.area` as a policy-governed attachment:
- **Spec** chooses backend (`zfs-dataset`, `file-image`, `remote-mounted`) and encryption posture
- **Lock** pins key sources and identity anchors
- **Plan** produces:
  - the creation/attach steps
  - expected dataset properties / filesystem UUID
  - the `user.record` digest
- **Artifact** is the portable home object + signed metadata

### 3) Evidence and explainability
On every attach/unlock/lock, emit receipts:
- `home.attach.receipt` (what was attached, where, and under which policy)
- `home.unlock.receipt` (key source used, *not* the key)
- `home.lock.receipt` (keys unloaded, dataset unmounted)

`derive explain user <name>` should answer:
- “where does this user record come from?”
- “is the home area locked right now?”
- “what key sources are allowed by policy?”

### 4) Relationship to UserEnv
UserEnv (`docs/162-user-environments.md`) is the *derived contents* (dotfiles, per-user packages, user services).

Portable home areas are the *storage + identity container*.

Recommended structure:
- `home.area` provides `/home/$USER`
- UserEnv activation mounts/symlinks derived profiles inside the home area (or provides an overlay view)

Accepted default boundary note:
- profile B now treats portable homes as the preferred human-state default, but still forbids ambient whole-home mounts into general interactive AppVMs by default (`docs/463-human-identity-and-home-state-posture-by-profile.md`).

## Design constraints (don’t let this become a backdoor)

- **No privilege smuggling:** the `user.record` cannot grant system authority; it only describes identity.
- **No ambient unlocks:** policy should forbid “unlock all homes at boot.” Unlock should be tied to user login/consent.
- **Separation from host secrets:** key handling flows through the credential broker / key management lane.

## Open questions

- Do we want a single canonical `user.record` schema (portable between hosts) or a small adapter layer?
- Do we support “detached homes” (USB, network) as first-class backends, or treat them as transports?
- How do we represent group membership and per-machine exceptions without making `user.record` non-portable?

## References

- systemd “Home Directories” (systemd-homed overview): https://systemd.io/HOME_DIRECTORY/
- systemd user record format (embedded JSON user metadata): https://github.com/systemd/systemd/blob/main/docs/USER_RECORD.md
- homectl(1) (management interface): https://www.freedesktop.org/software/systemd/man/homectl.html
- Android file-based encryption / Direct Boot (credential-encrypted vs device-encrypted storage): https://source.android.com/docs/security/features/encryption/file-based

See also:
- Human identity + home-state posture by profile: `docs/463-human-identity-and-home-state-posture-by-profile.md`
- ZFS native encryption for state/generations: `docs/146-zfs-native-encryption-for-generations.md`
- Sealed secrets + attested unsealing (TPM policy lane): `docs/272-sealed-secrets-attested-unsealing.md`
- User environments (Home-Manager analogue): `docs/162-user-environments.md`
- Desktop AppVM stance: `docs/268-desktop-appvms-and-portalized-apps.md`

Last updated: 2026-03-06r192
