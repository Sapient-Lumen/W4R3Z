# Declarative image pipelines (apko/melange/Wolfi lessons)

One of the easiest ways to accidentally explode your trusted computing base is to make the
build language “just a shell script”. Nix/ports *work*, but they also enable an unbounded
surface area (and make policy reasoning harder).

Chainguard’s **apko** and **melange** are interesting because they push toward:
- declarative configuration
- reproducibility by default
- minimal “distroless” images

They are not BSD-native, but the *shape* of the idea is valuable for DeriveBSD.

References:
- apko (OCI image builder from apk packages; reproducible by default): https://github.com/chainguard-dev/apko
- apko file format (YAML; no arbitrary command execution): https://github.com/chainguard-dev/apko/blob/main/docs/apko_file.md
- melange (declarative pipelines to build apk packages): https://github.com/chainguard-dev/melange
- Wolfi overview (container-first “undistro”): https://edu.chainguard.dev/open-source/wolfi/overview/

## Lesson worth stealing

DeriveBSD should consider an optional **restricted recipe lane**:

- a build recipe is a typed, structured pipeline (not a freeform shell)
- each step’s inputs/outputs are explicit store objects
- network is denied by default; fetch is a separate capability
- the recipe itself becomes easier to lint, diff, and policy-check

This lane would not replace “full power” builders immediately, but it can become a
high-assurance path for critical base components.

## Possible DeriveBSD mapping

### 1) “Pipeline derivations” as a first-class kind

Introduce a derivation kind where:
- allowed steps are limited (unpack, configure, compile, test, install, strip, sign)
- each step can be backed by a tool capsule (known toolchain closure)
- the Plan records the step graph so `derive explain` can answer “why did this file exist?”

### 2) Minimal runtime images

Borrow the “distroless” posture:
- artifact targets can declare *only* the runtime closure they need
- optional: emit a “debug extension” as a separate artifact (see `docs/122-system-extensions.md`)

### 3) Interop adapter (optional)

DeriveBSD could optionally:
- import apko/melange outputs as foreign artifacts (policy-gated)
- attach DeriveBSD attestations/provenance to those bytes

This provides a pragmatic bridge for orgs with existing container build pipelines.

See RFC-0091.

Last updated: 2026-02-23
