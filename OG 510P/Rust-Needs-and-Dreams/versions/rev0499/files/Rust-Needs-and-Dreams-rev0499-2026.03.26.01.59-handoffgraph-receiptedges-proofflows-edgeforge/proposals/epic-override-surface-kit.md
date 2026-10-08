# Epic proposal: Override Surface Kit

## Why this is worthy
Rust already has a surprising amount of **ambient/provider infrastructure**, but it is described in a fragmented way.

The language/runtime has unique graph-wide override points like `#[panic_handler]` and `#[global_allocator]`.
The standard library has replaceable/updateable hooks like panic hooks and allocation-error hooks.
The ecosystem has one-shot global installs like `log::set_logger` and `tracing::subscriber::set_global_default`, plus scoped defaults and distributed registries via crates like `inventory` and `linkme`.

The higher-leverage missing piece is **not** another singleton helper.
It is a **portable override-surface contract** that lets maintainers describe installation authority, lifecycle, multiplicity, fallback/composition, discovery posture, and test-isolation evidence in one reviewable family.

This is especially timely because Externally Implementable Items is explicitly aimed at making things like `#[panic_handler]` and global allocator behavior more like ordinary library features. If Rust gets more library-defined override points, it will need better ways to publish their semantics than doc-comment folklore.

## What it would ship
1. `override-surface/v0`, `provider-slot-profile/v0`, `install-lifecycle-profile/v0`, `scope-multiplicity-profile/v0`, `registry-discovery-profile/v0`, `override-adapter-profile/v0`, `override-vector-set/v0`, `override-check-report/v0`, and `override-pack/v0`
2. `cargo overridecheck` for scaffolding, validating, diffing, and explaining override packs
3. pilots for:
   - `#[panic_handler]`
   - `#[global_allocator]`
   - panic hook / alloc-error-hook behavior
   - `log::set_logger`
   - `tracing::subscriber::set_global_default` + scoped-default fallback behavior
   - `inventory` and `linkme` as distributed discovery lanes
4. docs/reference generation that make “who installs this, when, how many, with what fallback?” explicit

## Why now
- Rust is actively pursuing Externally Implementable Items, directly naming `#[panic_handler]` and global allocator behavior as targets.
- The std/reference surface already encodes graph-unique hooks, process-global installs, and replace/update semantics.
- `log` and `tracing` already expose public rules about one-shot global init versus scoped defaults.
- Distributed registration is already real ecosystem practice via `inventory` and `linkme`.

That is enough evidence that the missing layer is **semantic publication and review**, not primitive invention.

## Milestones
1. **v0.1 schema + contrasts**
   - prove the kit can distinguish dep-graph unique, process-global once, scoped override, and collect-many discovery
   - publish one pilot in each family
2. **v0.2 adapter + isolation depth**
   - add fallback/wrapping adapter profiles
   - ship reset/test-isolation vectors and duplicate-init vectors
3. **v0.3 ecosystem bridges**
   - connect log/tracing bridge cases
   - connect distributed registries to plugin/metric/flag examples
4. **v1 discipline**
   - at least three materially different adopters use the kit without sharing one exact runtime/framework stack
   - reports catch at least a few real “already initialized”, duplicate-registration, or discovery-order surprises

## Expected payoff
- Fewer hidden initialization conflicts in tests, examples, plugins, and integration code.
- Clearer separation between “library provides a provider type” and “application owns installation authority”.
- More legible migration path if Rust gains more library-defined override points via EII.
- Better review of ambient behavior seams that are currently easy to miss because they look like convenience setup code.

## Anti-goals
This should not become:
- an excuse to normalize ambient global state everywhere,
- a universal DI/service-locator framework,
- or a flattening layer that pretends all override/discovery mechanisms are interchangeable.

The point is to make them **explicitly non-interchangeable in the right ways**.
