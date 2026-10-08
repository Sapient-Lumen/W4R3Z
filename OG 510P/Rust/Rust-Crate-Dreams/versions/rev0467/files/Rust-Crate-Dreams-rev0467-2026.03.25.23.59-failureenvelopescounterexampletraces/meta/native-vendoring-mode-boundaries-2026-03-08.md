# Native-deps mode / vendoring boundaries — 2026-03-08

This note sharpens **P-0058 native-deps-kit** around one concrete missing layer: **mode and policy truth** for system vs vendored vs override resolution.

## Main judgment

The native-deps frontier is no longer best described as “Rust needs another pkg-config wrapper.”

Current substrate is already meaningful:

- `system-deps` gives declarative manifest metadata, feature-specific deps, target-specific deps, build-flag overrides, and explicit env controls for internal builds and static linking.
- Cargo already exposes build-script results through `--message-format=json`.
- Cargo config already supports `target.<triple>.<links>` overrides that skip a build script entirely.
- Cargo is actively looking for ways to reduce the need for handwritten build scripts.

But that substrate still leaves a receiver-facing gap:

> who decided that we would use the system library, build internally, or rely on an override — and was that choice explicit, forced by additive features, or blocked by policy?

That is the sharper missing crate layer.

## Why this boundary matters

The best current evidence comes from the `system-deps` standardization discussion itself.

That issue explicitly calls out that:

- imperative `build.rs` probe logic is widely copied and under-tested,
- `vendored` Cargo features are additive and can silently force source builds across a dependency graph,
- this silent vendoring is hard to detect,
- and air-gapped or distro-managed environments may need the developer or CI to have the final say instead.

At the same time, current `system-deps` docs already expose real per-library and global mode knobs:

- `SYSTEM_DEPS_$NAME_BUILD_INTERNAL=auto|always|never`,
- `SYSTEM_DEPS_BUILD_INTERNAL=...`,
- `SYSTEM_DEPS_$NAME_NO_PKG_CONFIG`,
- and `SYSTEM_DEPS_$NAME_LINK=static`.

So the gap is not “there is no control surface.”
The gap is that the control surface is still mostly implicit to other people unless a crate emits a **portable lock/report** describing what was requested and what won.

## Design implications for P-0058

P-0058 should now be read as having four minimal layers:

1. **native contract** — declared library/version/backend intent
2. **resolution mode lock** — requested system / vendored / override posture and why
3. **backend-attempt receipt** — what probing or handoff actually ran
4. **doctor / policy report** — what another person should do next

This keeps the crate honest:

- do not promise one universal cross-platform package-manager story,
- do not treat “vendored feature exists” as an adequate explanation,
- do not hide additive-feature forcing behind a happy-path success report,
- and do not force all users into one package-management ideology.

## Recommended first scenarios

The best next fixture bundles in this frontier are now:

1. **feature unification forces vendoring, but policy blocks it**
2. **env or CI explicitly forces internal-build mode**
3. **override/handoff preempts live probing**
4. **system-only policy blocks automatic fallback**

These are stronger than another generic “pkg-config missing” example because they freeze the policy and support truth, not only the probe failure.

## Anti-goals

- Do not design P-0058 as a universal distro replacement.
- Do not pretend Windows, macOS, Linux distros, Homebrew, vcpkg, and custom SDK layouts can all be normalized into one tiny backend without loss.
- Do not collapse buildscript UX, test harnesses, linker-lane diagnosis, and native mode policy into one giant “Cargo doctor.”

## Sources

- `system-deps` docs: https://docs.rs/system-deps/latest/system_deps/
- `system-deps` `Config` docs (`add_build_internal` and mode env): https://docs.rs/system-deps/latest/system_deps/struct.Config.html
- `system-deps` issue on becoming a standard: https://github.com/gdesmott/system-deps/issues/97
- Cargo external tools / JSON messages: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo config (`target.<triple>.<links>` override): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo tracking issue on reducing handwritten build scripts: https://github.com/rust-lang/cargo/issues/14948
- Cross-platform external dependency discussion: https://internals.rust-lang.org/t/external-dependencies-in-crates-and-cross-platform-development/23154
