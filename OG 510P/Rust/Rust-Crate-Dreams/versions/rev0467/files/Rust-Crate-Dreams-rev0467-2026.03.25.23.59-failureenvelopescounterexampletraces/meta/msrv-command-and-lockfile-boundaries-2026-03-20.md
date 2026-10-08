# MSRV command and lockfile boundaries — 2026-03-20

This note exists so future passes do **not** flatten all MSRV support into one fake “minimum Rust version”.

## Keep these lanes separate

1. **Declared support-promise lane**
   - what `package.rust-version` and repo policy say is supported.

2. **Policy-activation lane**
   - whether the intended resolver/MSRV policy is actually active at the workspace root.
   - especially important for virtual workspaces and root-only settings.

3. **Command-family floor lane**
   - whether `build`, `metadata`, `doc`, `clippy`, `update`, `generate-lockfile`, or `package` succeed at the same floor.

4. **Pinned-lockfile build lane**
   - whether the repo still builds from the committed lockfile on an older toolchain.

5. **Lockfile-authoring lane**
   - whether reading/writing/updating the lockfile path needs a newer floor than the pinned build lane.

6. **Workspace-coupling lane**
   - whether one older member drags shared dependency selection for another newer member.

## Working rule

Do not let the archive imply that any of the following are equivalent:

- `rust-version = X`,
- resolver `fallback` was active,
- `cargo build` succeeded on `X`,
- `cargo metadata` succeeded on `X`,
- `cargo update` or `cargo generate-lockfile` succeeded on `X`,
- `cargo package` could safely regenerate or include the lockfile on `X`.

A worthy crate in this lane should report:

- what policy was declared,
- whether the policy was active,
- which command family was checked,
- whether the lane depended on an already-committed lockfile,
- and whether ongoing authoring/update support matches the build promise.

## Anti-collapse reminder

Future revisions must not collapse:

- policy intent,
- policy activation,
- command-family floors,
- pinned-lockfile buildability,
- lockfile-authoring compatibility,
- and workspace dependency coupling

into one fake “MSRV result”.
