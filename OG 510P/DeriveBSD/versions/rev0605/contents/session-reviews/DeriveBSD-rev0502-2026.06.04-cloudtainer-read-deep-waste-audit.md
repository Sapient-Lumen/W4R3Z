# DeriveBSD rev0502 cloudtainer read-deep waste audit

Generated: 2026-06-04 02:43 EDT.
Input archive: `DeriveBSD-rev0501-next57-2026.05.30-post-detach-terminal-closure-successor-cutover-successor-index-cutover-schema-split-r533(1).zip`.
Output intent: keep the cube revisioned, inspectable, and safer to iterate in this cloudtainer.

This pass combined targeted reading of the front-door docs, current cube audit files,
release hygiene logs, and mechanical scans across the extracted tree. It was not a
line-by-line semantic review of every one of the roughly three thousand files.

## Corrected in this revision

The r533 generated cube metadata still used r532 suffixes in three durable IDs:

- `spec/examples/cube.schema.audit.report.json` used `cube-schema-audit-20260530-r532`.
- `spec/examples/cube.schema.refactor.backlog.json` used `cube-schema-refactor-backlog-20260530-r532`.
- `spec/examples/cube.hygiene.checkset.manifest.json` used `cube-hygiene-checkset-20260530-r532`.

The corresponding checkers had the same stale hard-coded expectations, so equality
checking did not catch the mismatch. The examples and these tools were updated:

- `tools/check_cube_schema_audit_report.py`
- `tools/check_cube_schema_refactor_backlog.py`
- `tools/check_cube_hygiene_checkset_manifest.py`

Immediate follow-up recommended: add a semantic invariant that every generated
ID suffix must agree with `generated_for_version` and the release cut recorded in
`README.md`. Equality against a generated fixture is not enough.

## Validation run after the patch

The following checks passed after regenerating the affected artifacts:

- `python3 tools/check_cube_schema_audit_report.py`
- `python3 tools/check_cube_schema_refactor_backlog.py`
- `python3 tools/check_cube_hygiene_checkset_manifest.py`
- `python3 tools/validate_spec_examples.py`
- `python3 tools/check_generated_docs.py`
- `python3 tools/check_consistency.py`
- `python3 tools/check_validation_logs_clean.py`
- `python3 tools/check_version.py`

The existing r533 hygiene log already says that focused shards completed cleanly,
but that full all-profile hygiene was not marked complete in the interactive run.
A fresh wrapper run in this cloudtainer again behaved like a poor interactive fit:
individual checks completed, while the wrapper became hard to trust under the
session runner. Treat this as process debt rather than proof of a broken cube.

## Mechanical scan highlights

Approximate extracted tree shape before packaging:

- 3,025 source files in the original zip.
- Largest areas: `spec`, `docs`, `adrs`, `tools`, and `rfcs`.
- Markdown files dominate the human surface; JSON examples and schemas dominate
  the contract surface.
- `docs/00-index.md`, `CHANGELOG.md`, `docs/110-juicy-os-lessons.md`,
  `docs/99-llm-runbook.md`, `docs/266-open-questions-and-risk-register.md`,
  and `docs/98-archive-hygiene.md` are very large front-door or governance files.
- The scan found many lines longer than 500 characters, including extreme lines
  over 10,000 characters in `README.md`, `docs/457-*`, `docs/266-*`,
  `docs/99-*`, and `docs/410-*`.
- Common helper functions are copied across the tools tree many times, including
  `load_json`, `jcs_bytes`, `digest`, `validate`, and `fail`.
- Root log files include exact duplicate groups, especially older hygiene logs
  and check-run tails.
- Repeated placeholder-like `sha256:` values are widespread. The cube already
  distinguishes some historical placeholders from computed joins, but the visual
  risk remains high for future reviewers.

## What is severely wrong or wasteful

### 1. Guardrail monoculture

The cube has many good checks, but too much checker behavior appears copied
script-by-script. That gives local clarity at the cost of global maintenance.
When a semantic rule changes, dozens of checkers may need the same edit. The
r532/r533 ID issue is a symptom: fixture equality can be locally green while a
release-level invariant is wrong.

Correction path:

- Add `tools/cube_check_lib.py` for JSON loading, canonical JSON, schema
  validation, release-ID derivation, digest helpers, report printing, and
  standard exit behavior.
- Move the ten hottest duplicated checkers first, not all 350 at once.
- Add a small red-corpus case for version/ID skew.
- Emit per-check JSON results with duration and max RSS.

### 2. The front door is too heavy

The runbook and index are built to fight amnesia, but the current scale makes
new sessions pay an excessive context tax. A session can waste a large fraction
of attention deciding which massive file is the real entry point.

Correction path:

- Keep a tiny front door: latest cut, invariants, current next action, and links.
- Move old release prose into generated release notes or changelog shards.
- Add a `check_frontdoor_budget.py` gate with byte count, line count, and long-line
  ceilings for `README.md`, `docs/00-index.md`, and `docs/99-llm-runbook.md`.

### 3. Placeholder digest ambiguity

Repeated fake-looking `sha256:` values are useful in fixtures, but risky in a
security-shaped OS project. Humans and LLMs can mistake placeholder evidence for
cryptographic evidence.

Correction path:

- Require explicit placeholder mode fields in every new fixture receipt.
- Reject placeholder-looking hashes in runtime-shaped examples unless the field
  name says it is a fixture or historical placeholder.
- Add an allowlist for legacy examples and shrink it each revision.

### 4. Full hygiene is too hard to trust interactively

The project has release-critical, post-detach, generated-surface, schema-audit,
and deep-contract profiles. That is good. The weak point is operational: a human
session needs an execution summary that proves which shards completed and where
time was spent.

Correction path:

- Make the hygiene wrapper write a durable machine-readable run ledger.
- Include `tool`, `profile`, `return_code`, `elapsed_seconds`, `max_rss_kb`,
  `stdout_digest`, and `stderr_digest`.
- Fail the wrapper if a shard is skipped, killed, or times out without being
  recorded as such.

### 5. Schema-split work is correctly identified but should become the mainline

The current cube already identifies const-heavy schemas and fixture-vs-runtime
splits. The waste would be adding new receipt families before reducing the open
const-heavy backlog.

Correction path:

- Freeze new lifecycle receipt families until the highest-risk post-detach split
  items are done.
- Prefer generic runtime schemas plus exact fixture schemas.
- Preserve exactness in fixtures, but never let fixture exactness masquerade as a
  runtime contract.

## What appears missing

### 1. A runnable vertical slice

The cube has strong data and evidence modeling. It needs one end-to-end runnable
slice that proves the model is implementable, preferably on FreeBSD:

1. detect removable media,
2. classify filesystem,
3. mount read-only or decline,
4. isolate the reader worker with Capsicum/Casper where possible,
5. emit a post-detach receipt,
6. validate that receipt against the cube schemas,
7. replay a red-corpus failure.

### 2. A concrete Workstation B remoting plan

The desktop viability checklist is candid that exact GUI remoting, damage
tracking, video/audio, IME, accessibility, accelerated paths, and seamless window
mode still need implementation detail. That should become a milestone plan with
explicit components, protocols, fallback behavior, and security boundaries.

### 3. Hardware qualification evidence

The cube talks about hardware and profiles, but a project like this needs a small
machine-readable hardware evidence set: boot results, device IDs, GPU mode,
network mode, storage mode, suspend/resume, removable-media behavior, and known
failures.

### 4. Threat model matrix

The cube has many invariants but would benefit from a short adversary matrix:
malicious guest, malicious display stack, compromised cache, compromised build
worker, malicious update mirror, malicious support engineer, hostile removable
media, clock rollback, disk firmware lies, and host-user mistakes.

### 5. Performance budgets

Receipt-heavy systems can become slow because every action produces evidence.
Add budgets for receipt size, validation time, release-check time, storage
retention, log compression, and startup cost.

### 6. Profile acceptance tests

Profiles A through D should have acceptance manifests: required features,
forbidden features, security expectations, expected hardware assumptions, and the
minimum check bundle that must pass before each profile is advertised.

## Online calibration notes

Current upstream context strengthens several existing DeriveBSD instincts:

- FreeBSD 15.0 made pkgbase a major installation path and treats base-system
  packaging as a first-class concern.
- The FreeBSD Foundation has recently emphasized reproducible and rootless
  release-build work.
- FreeBSD continues to expose bhyve virtualization and Capsicum/Casper primitives
  that fit DeriveBSD's compartment and authority model.
- SLSA 1.2, in-toto attestations, Sigstore transparency logs, TUF metadata roles,
  and Uptane-style recovery patterns all remain useful reference frames for
  DeriveBSD's evidence, update, and authority surfaces.

## Recommended next cuts

### rev0503 candidate

Add release-ID consistency checks so generated IDs cannot drift from
`generated_for_version` again. Include a negative fixture or self-test proving
that r532/r533 skew fails.

### rev0504 candidate

Add a hygiene run ledger and runtime-budget report. Do not depend on terminal
scrollback or a human remembering which wrapper shard completed.

### rev0505 candidate

Start `tools/cube_check_lib.py` and port the first duplicated checker cluster.
The goal is less checker code, not fewer checks.

### rev0506 candidate

Add the front-door budget gate and start splitting the largest human-entry files
without deleting their historical content.

### rev0507 candidate

Implement the smallest removable-media local fallback vertical slice, even if it
is initially a stubbed FreeBSD integration harness running inside the cloudtainer.
