# Closure diffs: make “new code ingestion” reviewable

When you update a system generation, you don’t just change *configuration*.
You often ingest **new code**: packages, libraries, interpreters, firmware blobs, etc.

Real-world lesson: a large fraction of security incidents start with “a dependency update changed behavior”.
If the system can’t answer “what new code did we add?”, review becomes vibes.

Greenfield advantage: treat “new code ingestion” as a first-class diff artifact: `closure.diff`.

## Background: closures are the unit of reality

In Nix-like systems, a build result has a **closure**: the set of store paths it depends on.
Nix exposes this directly (requisites / closure queries), e.g. `nix-store --query --requisites`.  
Reference: https://nix.dev/manual/nix/2.26/command-ref/nix-store/query

In OSTree/rpm-ostree ecosystems, deployments are content-addressed trees and you can diff the package set between commits (e.g. `rpm-ostree db diff`).  
Reference: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/composing_installing_and_managing_rhel_for_edge_images/edge-terminology-and-commands_composing-installing-managing-rhel-for-edge-images

DeriveBSD already has `closure.manifest` (what is in the generation).
A `closure.diff` compares two manifests and emits a compact “what new code appeared?” summary.

## The `closure.diff` artifact

A closure diff should answer:

- What roots changed? (top-level packages/services/images)
- What store paths were added/removed?
- What new origins appeared? (new channels, new publishers, new upstreams)
- What *risk tags* entered the build? (new `untrusted-bytes` parsers, new JITs, new crypto libs)
- What evidence is attached? (rebuilders, fuzz receipts, policy test reports)

Schema: `spec/closure.diff.schema.json`  
Example: `spec/examples/closure.diff.json`

## How this plugs into review

### 1) Complement to `blast_radius.diff`

Authority diffs answer: “what can the new thing do?”

Closure diffs answer: “what new code is now present?”

A common pattern is:
- closure diff flags “new code: libX + parserY”
- parser registry/diff flags “new parser surface: parserY”
- authority diff flags “new broker edges created by serviceZ”

Review becomes a cross-check rather than guesswork.

### 2) Gating ideas

- Require `closure.diff` for any promotion that changes the host generation.
- Require an additional reviewer if `closure.diff` introduces new `risk_tags` like:
  - `untrusted-bytes`
  - `crypto`
  - `jit`
  - `kernel-crossing`

### 3) Tooling hooks

- `derive diff --closure <from> <to> --json` → emits `closure.diff`
- `derive diff --bundle <from> <to> --json` → includes `closure.diff` when present

See also:
- `docs/395-drift-bundles-and-review-summaries.md`
- `docs/379-surface-registry-pattern.md`
