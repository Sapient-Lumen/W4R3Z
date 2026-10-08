# Archive disagreement-ledger discipline — 2026-03-24

This note is for the archive itself, not for the crates.

The repo now has enough packet families that future passes can easily drift into one failure mode:
**seeing two conflicting public facts and silently narrating one merged conclusion.**

Do not do that.

## Rule

When a pass encounters meaningful disagreement between:
- frozen basis and current public surfaces,
- registry/index and `cargo metadata`,
- docs.rs hosted pages and local materialization,
- trust posture and task-fit posture,
- cached build observations and rerun observations,
- or prior packet and current packet,

the pass should create or update a **disagreement ledger** before it rewrites any summary prose.

## Minimum disagreement-ledger fields

- `subject`
- `conflicting_routes`
- `basis_window`
- `scope`
- `why_it_matters`
- `adjudication_state` (`open`, `split_scope`, `kept`, `superseded`, `manual_review_required`)
- `followup_artifact`

## Repo-level consequences

When a later archive pass changes a recommendation, it should say:
1. which earlier artifact it is carrying forward,
2. what disagreement opened the review,
3. what stayed inherited,
4. what became superseded,
5. and what still remains manual.

## LLM hygiene consequence

Future LLM passes should prefer:
- `the old packet still stands under the old basis`,
- `a new adjudication session changed part of the answer`,
- or `manual review remains required`

instead of writing as if the archive always knew the newest answer.
