# Archive hygiene (how we avoid a monster)

This repo must grow over time, but not explode.

## Rules

1) Prefer **RFCs** for proposals, then accept via **ADRs**.
2) Keep docs small:
   - “one concept per file”
   - link out to RFCs/ADRs instead of duplicating content
3) Any new subsystem must pass the **design review rubric** (copy the template into the RFC):
   - contract surface (typed, digest-bound)
   - authority changes (attenuation + revocation + diff surfaces)
   - threat model impact + trust boundaries
   - failure modes + rollback behavior
   - evidence outputs + retention budget

See: `docs/348-design-review-rubric-and-feature-intake.md`.

4) Add references as links; avoid copying external text.
5) When a topic becomes stale, move it to `docs/attic/` and leave a one-line pointer.

## Checks

- Quick path: `python3 tools/hygiene.py` runs the lightweight checks below in one go.

- Run `python3 tools/check_consistency.py` before committing:
  - missing RFC/ADR ids
  - broken backticked repo paths
  - broken internal markdown links (repo-relative or relative-to-file links)
  - rejects accidental ChatGPT citation markers (use explicit URLs in docs)

- Run `python3 tools/check_discovery.py` before committing when you added/renamed docs or changed the reading paths:
  - ensures `docs/00-index.md` contains a `New in <version>` section for the newest CHANGELOG entry
  - ensures the newest `New in <version>` block is the **first** `New in ...` section (prevents stale top-of-file release notes)
  - ensures `docs/00-index.md` has `Last updated: <version>` matching the newest release
  - ensures critical “amnesia-resistor” entry points remain wired (LLM runbook, product profiles, etc.)
  - ensures numbered docs mentioned in the newest CHANGELOG entry are wired into discovery surfaces (index vs juicy lessons)
  - ensures those docs also appear in the matching `New in <version>` block (so release notes don't go stale)
  - ensures repo paths mentioned in the newest CHANGELOG entry actually exist

- Run `python3 tools/check_changelog_format.py` to keep release notes compact and diff-friendly:
  - enforces that `CHANGELOG.md` has minimal leading whitespace after the top heading
  - rejects trailing whitespace (prevents noisy diffs)

- Run `python3 tools/check_changelog_artifact_mentions.py` to prevent 'paper artifact' drift in the newest release:
  - for docs mentioned in the newest CHANGELOG entry, ensures any backticked `*.plan`/`*.receipt`/etc artifact kinds have a matching schema under `spec/` (e.g. `spec/mirror.import.receipt.schema.json`)

- Run `python3 tools/check_release_last_updated.py` to keep release-touched docs stamped:
  - for docs mentioned in the newest `CHANGELOG.md` entry, requires `Last updated: <version>` matches the newest release
  - keeps doc changes mechanically visible without forcing retroactive churn


- Run `python3 tools/check_must_read_set.py` to prevent 'must-read' drift:
  - ensures the runbook’s mandatory refresh list keeps the canonical start-here docs
  - keeps the generated context pack’s must-read section complete (since it is derived from the runbook)

- Run `python3 tools/check_doc_metadata.py` when editing docs in the meta-engineering range (>=397):
  - enforces a tiny Tier/Profiles/Pillars metadata block near the top of the doc
  - validates Tier/Profiles/Pillars values against the allowed enums

- Run `python3 tools/check_meta_doc_discoverability.py` when adding/moving meta-engineering docs (>=397):
  - ensures every meta doc remains linked from either `docs/00-index.md` or `docs/110-juicy-os-lessons.md`
  - prevents quiet drift where the "design law" docs exist but are unreachable


- Run `python3 tools/check_diff_surface_registry.py` when adding or refactoring diff artifacts:
  - enforces that every `*.diff` schema under `spec/` is listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`)
  - prevents quiet review-surface drift where new diffs exist but aren’t discoverable

- Run `python3 tools/check_diff_surface_registry_wiring.py` when editing the diff surface registry table:
  - enforces that each `*.diff` row includes at least one backticked wiring-doc pointer (e.g. `docs/428-...`)
  - prevents “registry lists a diff but nobody can find the gate semantics” drift

- Run `python3 tools/check_diff_review_docs.py` when adding or refactoring per-diff review-surface docs:
  - enforces that each `*diff-as-*surface*.md` doc declares Tier placement
  - requires the canonical pattern token `Registry→Diff→Gate`
  - requires schema + example pointers so reviewers can jump directly to contracts
  - keeps the family of “diff review surface” docs uniform (reduces amnesia drift)


- Run `python3 tools/check_diff_wiring_risk_flags.py` when adding new diff wiring docs:
  - incrementally requires wiring docs listed in `docs/430-diff-surface-registry.md` to declare a `## Risk flags` section (or be explicitly allowlisted under `tools/baselines/`)
  - keeps `risk_flags` reason codes as a stable jump-to review surface for UI + policy gates

- Run `python3 tools/check_juicy_lesson_references.py` when adding new external URLs to the juicy lessons index (`docs/110-juicy-os-lessons.md`):
  - blocks new uncataloged citations without forcing retroactive churn (uses a baseline allowlist)
  - prefer adding new URLs to `docs/32-curated-references.md`; extend the allowlist only for historic gaps

- Run `python3 tools/check_risk_flag_registry.py` when introducing or renaming `risk_flags` reason codes:
  - enforces that a canonical risk flag registry exists as a typed artifact (`risk.flag.registry`)
  - ensures spec examples and gate docs use canonical kebab-case ids (prevents ad-hoc flag drift)

- Run `python3 tools/check_risk_flag_typical_sources.py` to keep risk flag metadata wired to real artifacts:
  - ensures each `typical_sources` entry in `risk.flag.registry` refers to a real schema under `spec/`
  - requires diff kinds referenced as typical sources are listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`)

- Run `python3 tools/check_doc_patterns.py` for meta docs (>=397):
  - requires a `**Patterns:**` metadata line near the top
  - forces new ideas to explicitly map to existing patterns (reduces design sprawl)

- Run `python3 tools/check_curated_references.py` when introducing new external work in meta docs (>=397):
  - ensures each external URL in meta docs is listed in `docs/32-curated-references.md`
  - keeps citations centralized and reduces long-term “link drift”

- Run `python3 tools/check_release_curated_references.py` when cutting a release that introduces new numbered docs:
  - for numbered docs mentioned in the newest `CHANGELOG.md` entry, ensures any external URLs are also listed in `docs/32-curated-references.md`
  - prevents new “uncataloged citations” without forcing retroactive churn across the full archive


- Run `python3 tools/check_generated_docs.py` to ensure generated discovery docs are up to date:
  - checks `docs/412-product-profile-matrix.md`
  - checks `docs/420-context-pack.md` and `docs/_generated/context_pack.json`
  - checks `docs/414-doc-catalog.md` and `docs/_generated/doc_catalog.json`
  - checks `docs/415-risk-register-index.md` and `docs/_generated/risk_register.json`
  - checks `docs/418-artifact-index.md` and `docs/_generated/artifact_index.json`
  - fix by running:
    - `python3 tools/gen_product_profile_matrix.py --write`
    - `python3 tools/gen_context_pack.py --write`
    - `python3 tools/gen_doc_catalog.py --write`
    - `python3 tools/gen_risk_register_index.py --write`
    - `python3 tools/gen_artifact_index.py --write`

- Run `python3 tools/check_risk_register.py` when editing the open questions/risk register:
  - enforces that each numeric item in `docs/266-open-questions-and-risk-register.md` contains an explicit `Risk:` line

- Run `python3 tools/check_schema_kind_matches_filename.py` when adding or renaming dotted-kind schemas:
  - enforces that schemas with dotted `kind` names (e.g. `mirror.import.receipt`) keep a stable filename mapping (e.g. `spec/mirror.import.receipt.schema.json` for kind `mirror.import.receipt`)
  - prevents quiet drift where docs/tooling refer to one kind while the schema declares another

- Run `python3 tools/check_spec_example_coverage.py` when adding or refactoring artifacts:
  - ensures each critical artifact schema (plan/receipt/event/report/registry/diff) has a matching example in `spec/examples/`

- Run `python3 tools/check_version.py` before committing if you touched discovery surfaces or version stamps:
  - ensures README + docs/00-index + docs/110 last-updated tags match the newest CHANGELOG entry

- Run `python3 tools/lint_spec_schemas.py` when touching `spec/` schemas:
  - checks schema convention drift (kind/version/id/timestamp fields; catches copy/paste errors)

- Run `python3 tools/validate_spec_examples.py` when touching `spec/`:
  - validates examples under `spec/examples/` against schemas under `spec/`
  - catches schema/example drift early
  - if an example is intended as a long-lived contract, add a matching schema (even a thin `$ref` wrapper)
  - if you want multiple long-lived variants for a single contract, suffix the example filename (e.g. `microvm.stop.receipt.denied.json`) **and** add a matching wrapper schema (e.g. `spec/microvm.stop.receipt.denied.schema.json`) that `$ref`s the base schema and pins the variant semantics

## Document lifecycle

- `rfcs/` = debate + iteration
- `adrs/` = decisions (append-only)
- `docs/` = current truth (concise, updated when ADR lands)

Last updated: 2026-03-04r185