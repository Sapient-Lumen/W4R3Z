# Continuous fuzzing farm (syzkaller-style) as evidence: corpora, crash cases, and promotion gates

Long-running fuzzing is one of the **highest ROI** ways to improve kernel + parser security — but only if it is
**operable** and produces evidence objects that can be reviewed, reproduced, and gated on.

DeriveBSD already treats provenance/SBOM/tests as digestable evidence.
Fuzzing should follow the same pattern.

Related: `docs/166-test-receipts-and-promotion-gates.md`, `docs/234-anykernel-and-rump-kernels.md`,
`docs/194-debugging-by-lease-and-replay-capsules.md`.

## The concept: `fuzz.receipt` + `crash.case` + `corpus.set`

The gate posture is now explicit: required target classes and explicit `crash.case` state matter most; coverage percentages are advisory and remain guidance rather than authority.

### 1) `fuzz.receipt`
A canonical object emitted by a fuzzer runner compartment (microVM/jail) that binds:
- `target_digest` (what is being fuzzed: kernel build / subsystem / userland parser)
- `harness_digest` (syzlang-like schema, wrappers, syscalls description, or parser harness)
- `runner_digest` (fuzzer runner image + toolchain)
- `sandbox_profile_digest` (authority boundary)
- `seed_inputs_digest` (if any)
- `corpus_set_digest` (the corpus snapshot used at start)
- `time_budget` / `exec_count`
- `coverage_summary_digest` (optional; summarized)
- `result_summary` (no-crash / crash signatures)
- pointers to content-addressed artifacts (logs, crash reproducers, corpus delta)

The receipt is signable and attachable as an in-toto-style attestation.

In v0, `fuzz.receipt` should also summarize reproducibility pressure directly: separate reproducible crash-case counts from flake-suspect counts so dashboards and promotion gates do not silently collapse them into one number.

### 2) `crash.case`
A crash is only useful if it is **portable** and **minimized**.
A crash case is a content-addressed bundle that contains:
- minimized reproducer(s) (program/input)
- the exact target build + config
- the VM profile / device model used
- a normalized crash signature (backtrace hash + faulting PC + sanitizer tag)
- artifacts needed for replay (e.g., snapshot, symbol map pointers)
- a suggested safe replay profile (default: disposable no-network compartment)
- an explicit reproducibility state (`stable`, `flaky`, `unreproduced`)

### 3) `corpus.set`
Corpora are **state** — treat them as first-class artifacts.
A corpus set is:
- immutable and content-addressed
- built by merging deltas from `fuzz.receipt`s
- publishable (with policy) as a “known-good fuzzing state” for regression checks

## Runner topology: isolation by default

Fuzzers are untrusted code that drives the kernel into weird states. Run them like attackers:

- fuzzer runner lives in a **microVM** (preferred) or jail with strict caps
- no ambient network; only an explicit ingest/export channel
- storage is ephemeral; only **content-addressed exports** survive

Use `docs/121-jailed-hypervisor-workers.md` and the injection/export channels in `docs/72-bhyve-io-channels.md`.

## Targets and harnesses (recommended set)

Treat fuzzing targets as a registry: ideally the fuzz farm targets are keyed by the same ids used in `parser.registry` / `uapi.registry`.

For kernel UAPI fuzzing, standardize syzkaller-shaped interface descriptions as a registry-aligned artifact lane (so harness identity and linkage are reviewable):
- `docs/406-uapi-fuzz-descriptors-and-conformance.md`.

1) **Kernel syscall surface**
- mainline kernel build(s) for each supported platform posture
- optional sanitizer kernels (KASAN/UBSAN-style) as separate targets

2) **Kernel-adjacent parsers**
- filesystems, packet decoders, ioctl parsers, image loaders
- when possible, run as rump/anykernel in userspace first (`docs/234-…`)

3) **Userland parsers / importers**
- archive extractors, document importers, pkg/metadata parsers
- integrate with the sanitization portal lane (`docs/267-…`) for “real-world” inputs

## Policy hooks: fuzzing as a promotion gate (optional)

Policies can require:
- “required target classes emitted fresh `fuzz.receipt`s for this release candidate”
- “no open `crash.case` matching this target digest range and severity scope”
- “regression fuzz pass using last known `corpus.set`”
- “crash cases above severity threshold must be bisected” (see `docs/275-…`)

Coverage summaries may still be retained and reviewed, but coverage percentages are advisory rather than the core gate surface. This keeps fuzzing from being a nice-to-have dashboard.

## Operational ergonomics

- A fuzz farm should be **boring**:
  - scheduled runs
  - clear storage budgets
  - stable crash dedup keys
  - reproducible replay
- Make “download crash case → replay” a one-command path:
  - `derive fetch crash.case:<digest>`
  - `derive replay --case <digest>`

## Open questions

- How do we represent coverage summaries in a stable, privacy-safe, digestable way?
- What is the default retention policy for corpora and crash cases (by target class)?
- Which targets are “must-run before promotion” for DeriveBSD’s stated posture?

Last updated: 2026-03-07r228
