# Cargo lock-contention frontier — 2026-03-22

## Main judgment

**P-0490 Cargo Lock Contention Witness Kit** now deserves the archive’s newer artifact-rich treatment.

The upstream direction is finally explicit enough that the missing crate is not another suggestion to “set a different target dir.”
It is a reviewable support bundle for:

1. **root authority**,
2. **actor command lanes**,
3. **wait windows**,
4. **blocker-identity exactness**,
5. **mitigation cost**.

## Why this frontier sharpened

- Cargo now documents `target-dir` and `build-dir` as separate user-facing roots.
- build-dir-layout-v2 explicitly targets more granular locking so rust-analyzer and `cargo test` stop blocking each other.
- Cargo 1.93 development notes explain that lock relief required splitting build-dir versus artifacts-dir concerns first.
- rust-analyzer now documents a target-dir escape hatch, explicit default command lanes, override commands, invocation strategies, and wrapper posture.
- Cargo exposes tool-only lanes like `--compile-time-deps` and imported build-analysis sessions.

Taken together, that means the receiver-facing value is now a crate that can say **what the actors really did** and **what the workaround really costs**.

## Best next implementation stance

The next implementation pass should freeze a small vocabulary before adding any orchestration:

- root-authority classes,
- actor command-lane classes,
- wait-window exactness classes,
- mitigation cost classes.

The crate should stay read-only and explanation-first.

## 2026-03-22 refinement — lock-mode truth and mitigation-outcome honesty are the next missing layer

The upstream substrate now makes two more receiver-facing gaps much sharper.

### 1. Package-cache lock mode needs its own receipt

Cargo’s current internal `cache_lock` docs now spell out `DownloadExclusive`, `Shared`, and `MutateExclusive`, and explicitly say `DownloadExclusive` does not interfere with `Shared`.

That means a worthy crate should promote **`package-cache-lock-mode.receipt.json`** into first-class status instead of collapsing every package-cache story into one vague `package_cache_lock` diagnosis.

### 2. Mitigations need residual-surface and outcome truth

The Cargo 1.94 development-cycle update says some contention still remains in easy-to-overlook but significant cases, especially around proc-macros, build scripts, and some non-workspace-member cases.

That means a worthy crate should promote:

- **`residual-contention.report.json`** — what still remains after the mitigation
- **`mitigation-outcome.diff.json`** — what actually changed before vs after

A serious bundle should be able to say “the broad shared-target-dir wait was reduced, but proc-macro/build-script overlap remains” instead of merely “we set a different target dir and things got better.”
