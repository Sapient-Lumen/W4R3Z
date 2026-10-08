# Cube deep audit rev0230: execution risk, assumption triage, and tag hygiene

Rev0230 treats the main risk as **non-completion of the first real import**, not lack of another
validator. Rev0230 proved that the JSON/schema and context-pack planes can be made more honest. The
next bottleneck is practical: `FT-0181` still needs a real `SRC2+` packet, and the archive's own
startup posture was still carrying too many historical assumptions as if they were equally live.

## Primary finding

The cube had a mature import gate but no operationally sharp first move. A future maintainer could
read many controls and still not know which pilot to request first, which fields to refuse, or how
to choose between a learning-rich but minor-facing hint tutor and a lower-learning but cleaner
action-boundary workflow.

Correction: `docs/30-operations/ft0181-first-pilot-sprint-execution-pack.md` now names the first
sprint posture:

- one service;
- one owner;
- one date range;
- minimized `SRC2+` packet;
- aggregate-only minor-facing data by default;
- field survival only when a field changes authority, evidence grade, construct, public claim,
  protected route, rollback, safety, or security decisions.

This is substance, not closure. If no owner-reviewed packet arrives, `FT-0181` remains live.

## Second finding

`ASSUMPTION_LEDGER.json` had the same problem that `context-pack.json` had before rev0229: it was
honest about memory but wasteful about priority. All 273 assumptions were marked `active`, so the
startup surface could not distinguish current evidence/import bets from old hot-exam, after-hours,
portable-packet, relapse, and tooling-refactor history.

Correction: `docs/00-meta/assumption-ledger-triage-rev0230.md` defines four states. The ledger now
keeps a small active set for decision-bearing assumptions, puts still-useful broad hypotheses on
`watch`, and moves historical branch/refactor rationale to `archived_context`. No assumption was
physically deleted. The archive now retrieves old branch judgment through `BRANCH_FAMILY_INDEX.json`
or the ledger rather than pretending it belongs in the first decision path.

## Third finding

The surface map still used a single `tags` list for both identity and incidental mentions. This was
much better than no map, but it made tags such as `hot-exam`, `service-intake`, `real-import`, and
`datacube` carry too much ambiguity. A canonical service-import surface and a meta-audit surface can
both mention the same terms while having very different identities.

Correction: `tools/gen_surface_map.py` now emits `primary_tags` and `mentioned_tags` in addition to
the backward-compatible `tags` union. `tools/check_surfaces.py` verifies the new fields. This is a
low-cost metadata refactor: existing contract checks still work, but future retrieval can prefer
`primary_tags` when asking what a surface **is** rather than what it merely mentions.

## External posture

Current external signals reinforce the priority change. Digital Promise's 2026 state-guidance
analysis says many AI-in-education evaluation efforts are still exploratory or pilot-stage, with
fewer systematic/evidentiary programs. The U.S. Department of Education's 2026 final priority keeps
AI education projects inside existing federal education, disability, civil-rights, accessibility,
and documentation obligations. FTC children's-privacy updates and guidance keep minor-facing data
minimization, retention, and deletion pressure alive. See `B284`, `B285`, and `B286`.

## What still should not happen

Do not respond to this pass by adding a second sprint pack, a new import schema, or another closure
validator. The next useful work is to obtain or simulate-with-owner-review a real minimized packet,
run the existing import path, and record which fields changed decisions. If no real packet is
available, the next best local work is to rehearse the sprint packet against an explicit fake source
and record exactly why it fails, not to widen the request.

## Closure boundary

Rev0230 does not import real pilot evidence and does not close `FT-0181`. It reduces the risk that
the next maintainer wastes another turn polishing controls while the first import remains unsent.
