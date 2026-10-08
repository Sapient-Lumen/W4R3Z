# Cargo Workspace Toolchain Manifest Kit — component/fallback boundaries (2026-03-23)

This note keeps **P-0055** from flattening several adjacent truths into one fake “the tool ran” verdict.

## Keep these layers separate

1. **install-root posture**
   - workspace-local root,
   - shared user cache,
   - cargo-home bin,
   - ephemeral CI root,
   - custom path.

2. **command authority**
   - rustup proxy/component route,
   - Cargo external-subcommand route,
   - workspace-managed executable,
   - PATH fallback,
   - manual wrapper.

3. **component availability**
   - installed,
   - available but not installed,
   - missing for the checked toolchain,
   - not applicable.

4. **toolchain selection context**
   - `+toolchain`,
   - `RUSTUP_TOOLCHAIN`,
   - directory override,
   - toolchain file,
   - default toolchain.

5. **fallback ceiling**
   - component-backed claim,
   - subcommand-backed claim,
   - workspace-backed claim,
   - fallback-only claim,
   - manual-review-required claim.

## What must not be collapsed

Do not let any of the following stand in for an honest support claim:

- “the repo pins the tool,”
- “the command exists in `$CARGO_HOME/bin`,"
- “rustup has a proxy with that name,”
- “a PATH binary answered the request,”
- or “the same path showed up in CI and locally.”

Those can all be true while command authority, component availability, and claim ceilings still differ materially.
