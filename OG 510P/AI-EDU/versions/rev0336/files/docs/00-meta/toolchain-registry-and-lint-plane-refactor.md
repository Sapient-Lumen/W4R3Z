# Toolchain registry and lint-plane refactor

Lint plane note: rev0226 moves the lint suite from an implicit hardcoded list into `CUBE_TOOLCHAIN_REGISTRY.json`. Rev0227 keeps that registry as the tool source of truth and adds `tools/check_schema_registry.py` to the lint order for JSON-plane coverage. Rev0230 extends that coverage into schema-instance validation and compactness checks for `context-pack.json`. Rev0230 keeps the registry but shifts generator coverage toward execution-risk needs: active-assumption context packs and surface `primary_tags` / `mentioned_tags` hygiene.
The registry is now the machine-readable source of truth for which tools run during lint, which
canonical artifacts are generated, and which Python files are utilities rather than validators.
Rev0253 adds registry-driven lint lanes so changed field-path work can run through `make lint-owner-reply` or `make lint-fast` before the full release gate. Rev0254 extends the owner-reply lane to cover the local owner-contact status clock, including sent, re-ask, and `NO-OWNER-PACKET` outcomes. Rev0256 adds the runnable field next-action router to the same lane so packet, contact, returned-CSV, intake, seed, and no-packet scratch states route to one bounded command. Rev0258 extends that lane with returned-CSV source/smoke firebreak checks so archive fixtures and copied smoke CSVs cannot become the next field action. Rev0260 adds fixed-output collision and nonscratch archive-output leakage checks for returned-CSV intake, receipt, staging, workbench seed, and field-next routing.

## Problem found in the audit

The archive had a valid control plane, but the toolchain itself had become an unregistered control
surface. `tools/run_lint_suite.py` carried the lint order as code. Several validators checked whether
other validators were "wired into lint" by searching that file as plain text. That worked while the
suite was small, but it created three failure modes:

1. a new validator could be added to `tools/` without being run;
2. a utility could be mistaken for a missing lint gate;
3. validators could disagree about what "wired into lint" means.

Those are refactor risks, not evidence risks. They do not affect whether `FT-0181` can close, but
they do affect whether a future maintainer can trust the release controls.

## New registry surfaces

| Surface | Role |
|---|---|
| `CUBE_TOOLCHAIN_REGISTRY.json` | Lint order, generated-artifact list, utility-tool list, and coverage rules. |
| `schemas/toolchain-registry.schema.json` | Shape contract for the registry. |
| `tools/check_toolchain_registry.py` | Fails if a `check_*.py` is not linted, if a tool is uncovered, if generated artifacts lack checks, or if the registry revision drifts from the receipt. |
| `tools/run_lint_suite.py` | Now reads the registry and `lint_lanes` instead of carrying a hardcoded validator array. |
| `tools/check_reentry_navigation.py` | Guards re-entry link budgets and the rev0230 active-assumption compact-context-pack contract. |
| `tools/gen_surface_map.py` and `tools/check_surfaces.py` | Generate and verify `primary_tags`, `mentioned_tags`, and the backward-compatible `tags` union. |

## Lint lanes

| Lane | Command | Use |
|---|---|---|
| `owner-reply-field` | `make lint-owner-reply` | Field next-action routing, first-contact packet prep, owner-contact status, owner-reply triage, intake, staging, smoke, and workbench-seed checks. |
| `fast-changed` | `make lint-fast` | Changed navigation, registries, owner-field/owner-contact/owner-reply tooling, watchlists, and generated maps. |
| `release-controls` | `make lint-release-controls` | Release-control examples and slower closure/claim/custody gates. |
| `full-release` | `make lint-full` | Complete release gate; also used by `make lint`. |

The lane split is a cloudtainer-time refactor. It does not weaken the release gate; it just prevents small field repairs from forcing a monolithic run during every edit.
Rev0253 also runs selected validators in-process through `runpy`, which keeps the registry order authoritative while avoiding a subprocess per check during focused lanes.

## Refactor rule

When adding a tool:

- add every new `check_*.py` to `CUBE_TOOLCHAIN_REGISTRY.json` under `lint_order`;
- add every non-linted tool to `utility_tools` with a role;
- add every canonical generated artifact to `generated_artifacts` with its generator and check;
- do not edit `run_lint_suite.py` to append a one-off list entry; update `lint_order` or `lint_lanes` in the registry instead.

When adding a release-control validator that references "wired into lint," use the registry's
`lint_order`, not a text search over the runner. When that validator governs structured JSON, also register its schema and instance globs in `CUBE_SCHEMA_REGISTRY.json` and expect those instances to validate against the declared schema. When changing generated startup or surface metadata, keep the toolchain registry aligned with `context-pack.json` and `SURFACES.json` generator/checker pairs.

## What this does not prove

The registry proves tool coverage, not service effectiveness. It does not import real pilot data,
validate learning outcomes, close `FT-0181`, or replace human review. It only prevents the audit
plane from becoming a hidden manual checklist.
