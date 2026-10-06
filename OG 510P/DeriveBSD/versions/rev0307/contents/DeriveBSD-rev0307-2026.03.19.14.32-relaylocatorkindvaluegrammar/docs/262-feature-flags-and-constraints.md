# Feature flags and constraints (Gentoo USE lessons, but typed)

Optional features are where “a clean store” projects become messy:
- forks proliferate (“this build has X enabled”)
- dependency graphs become implicit
- cache hits drop because feature choices are not represented uniformly

Gentoo solved this socially and mechanically with **USE flags**: build-time feature switches that also control optional dependencies.

DeriveBSD should steal the *outcome*, but not the ad‑hoc ergonomics.

## DeriveBSD target

Make feature selection a **first-class, typed input** that flows through:

**Spec → Lock → Plan → Artifact identity**

So that:
- feature choices are reviewable (diffs)
- they are cache keys (no spooky mismatches)
- they are policy-governed (licenses, crypto, FIPS-ish modes, hardening)

## Model

### 1) Feature sets are explicit data
A package (or service bundle, or workload) declares a *finite* set of feature keys:

- `gui`
- `openssl`
- `ldap`
- `systemd-compat` (example; likely forbidden on BSD hosts but may exist in compat views)
- `minimal`

Each feature:
- has a meaning (docstring)
- may imply dependencies
- may be mutually exclusive with others

### 2) Constraints are separate from preferences
Keep three layers distinct:

1. **Provider defaults** (like Gentoo profiles)
2. **Site policy constraints** (hard requirements / forbiddances)
3. **Project preferences** (requested features for this build)

The Plan computation resolves them into an **effective feature set** and records the decision.

### 3) Features belong in the Plan (not hidden in build scripts)
Builders must not “discover” features from ambient environment.
If a feature changes the output, it must be in:
- the Plan
- the artifact identity (directly or via Plan digest)

### 4) Feature diffs are authority diffs when they change permissions
Some flags are just “extra codecs”; others change blast radius:
- `net` / `dbus` / `ipc`
- `jit`
- `debug`

Treat these like capability changes:
- show in `derive diff --blast-radius`
- require explicit approval in policy when sensitive

## UX sketch

- `derive explain <artifact>` shows:
  - effective features
  - which layer set each feature (default / policy / project)
  - why a requested feature was dropped (constraint conflict)

- `derive lint` warns when:
  - a package declares too many feature keys
  - feature interactions are under-specified
  - features are used for “non-optional” deps (anti-pattern)

## What this buys (concretely)

- Less “overlay culture” and fewer bespoke forks
- Higher cache hit rates (feature sets are normalised)
- Cleaner review surface: “this update enabled OpenSSL3 and disabled LDAP”

## References
- Gentoo Development Manual — USE flags (optional dependencies/settings, avoiding flag explosion): https://devmanual.gentoo.org/general-concepts/use-flags/index.html

Last updated: 2026-02-25
