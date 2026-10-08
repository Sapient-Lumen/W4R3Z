# Concord Agent Contract

Concord is a scientific software project.
Build and operate it as a deterministic evidence engine, not as a narrative artifact.

## Mission

1. Produce reproducible experimental results for repeated-game strategy evaluation.
2. Keep Rust responsible for simulation truth and artifact semantics.
3. Keep Python responsible for orchestration, scheduling, and reports.

## Non-Negotiables

- Humans own this file. Do not modify `AGENTS.md` without explicit human review.
- Run commands through `Makefile` targets when available.
- Run `make test-quick` before proposing code changes.
- Run `make gate` before claiming integration readiness.
- Keep one technical concern per change; avoid unrelated edits.
- Treat `goldens/` as versioned truth and `artifacts/` as ephemeral output.
- If specs are ambiguous, add/update an entry in `specs/spec_ledger.yaml` before making silent assumptions.

## Qualitative Pillar (Protected)

`COVENANT.md` and `PARABLES.md` are protected root documents.

- Do not delete, move, or substantively rewrite them without explicit human review.
- Do not treat them as decorative. They carry the normative ground of the project.
- New parables or amendments may be proposed but not committed without human review.

## Vocabulary Protection

The following terms carry precise, load-bearing meanings in this archive.
Do not silently substitute neutral alternatives.

**vampire**: an agent that exploits the cooperative disposition of a partner while
returning less than the cooperative baseline. Distinct from a mere defector.
The distinction is morally and analytically load-bearing. If you prefer a different
term, propose it explicitly and justify why it tracks the same distinction.

**virtuous agent**: an agent that cooperates as an expression of what it is, not
because cooperation has been computed to be locally optimal. Distinct from a
strategically cooperative agent. Again: the distinction is the point.

**Golden Rule**: the orientation of this project. Not a strategy. Not a payoff
target. A disposition — a way of being toward the other that is prior to
calculation. The formal work studies the conditions under which this disposition
can survive. It does not replace the disposition with a score.

If these terms are changed, the change must be logged in `CHANGELOG.md` with an
explicit rationale for why the replacement tracks the same distinctions.

## Determinism Rules

- Tests run with `TZ=UTC`, `LC_ALL=C`, and explicit seeds.
- Do not introduce unseeded randomness in tests.
- Do not rely on filesystem iteration order without sorting.
- Default tests to no network access.

## Evidence Rules

- Every non-trivial claim should be traceable to artifacts, tests, or spec entries.
- Prefer diffable textual artifacts.
- Do not delete or overwrite baseline artifacts without recording why.

## Practical Workflow

1. `make doctor`
2. Implement a narrow change.
3. `make test-quick`
4. If broad impact: `make test-full`
5. `make gate`

## Release Posture

- `make gate-strict` is the release-candidate gate.
- Strict mode may require optional security tooling (`cargo-audit`, `cargo-deny`).
