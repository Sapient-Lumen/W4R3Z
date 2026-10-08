# Archive exception-budget discipline — 2026-03-24

This note is for the archive itself, not for the crates.

The repo now has enough packet families that future passes can easily drift into another failure mode:
**accepting a temporary exception somewhere in the story and then narrating it later as if it were the stable answer.**

Do not do that.

## Rule

When a pass encounters or recommends meaningful temporary relief — for example:
- a local Cargo Vet exemption,
- a cargo-deny ignore entry,
- a semver override path,
- a docs/support caveat accepted for one target or profile,
- or a safety/interop exception pending replacement,

create or update an **exception budget** record before rewriting summary prose.

## Minimum exception-budget fields

- `subject`
- `scope`
- `owner`
- `authority`
- `why_exception_exists`
- `evidence_basis`
- `removal_path`
- `expires_at_or_trigger`
- `state` (`open`, `renewed`, `removed`, `transitioned`, `manual_review_required`)
- `followup_artifact`

## Repo-level consequences

When a later archive pass changes a recommendation, it should say:
1. whether the old answer stood cleanly or only under an exception,
2. whether that exception has been renewed, removed, or transitioned,
3. what evidence was missing before,
4. and what new evidence or change closes the gap now.

## LLM hygiene consequence

Future LLM passes should prefer:
- `the old decision stood only under a bounded exception`,
- `the exception was renewed with the same ceiling`,
- `the exception expired and opened transition review`,
- or `manual review remains required`

instead of writing as if a temporary exception was the archive’s stable recommendation all along.
