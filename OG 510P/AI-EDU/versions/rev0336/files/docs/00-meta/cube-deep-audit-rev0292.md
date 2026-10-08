# rev0292 cube deep audit

## Read of the cube

The cube is internally coherent and its live center is still `FT-0181`. The
archive is mature enough to block fake evidence, fake closure, copied fixtures,
old contact clocks, post-readout receipt laundering, and premature activation.
That maturity has created a different risk: the local control plane can become a
place where maintainers work hard without making field progress.

`rev0292` treats that as the primary risk. Rather than add another doctrine
surface, it refactors the executable seam immediately before owner contact. The
router can now be asked to perform only safe local work: if no packet exists, it
prepares the bounded first-contact packet and reruns itself. The result is a
prepared packet plus a post-prep field-next docket that exposes the real fork:
human send/adaptation or no-route block.

## Heart of the mission

The mission is to keep education answerable to learning, agency, access,
teacher capacity, provenance, contestability, and public-claim humility as AI
systems become ordinary infrastructure. That means the cube must not only prevent
false claims. It must also prevent governance work from displacing the owner
contact and field evidence that would make claims answerable.

## What was missing

The missing piece was not a new schema. It was a lower-friction bridge from
clean scratch to the first packet actually being ready for a human to use. The
previous rail was safe, but it still required manual command copying before any
human field action could happen.

## What changed

- `tools/decide_ft0181_field_next_action.py` gained `--execute-safe-local`.
- `Makefile` gained `owner-field-work`.
- `tools/check_ft0181_field_next_action.py` now validates that the safe local
  mode prepares only the packet, preserves no-evidence/no-closure boundaries,
  writes a session memo, and reroutes to the human-send/no-route fork.
- Re-entry docs now lead with `owner-field-work` while keeping the raw router
  available.

## Audit of what remains wasteful

The archive still carries a large body of historical surfaces, examples,
registries, and validators. That is useful as a safety lattice, but it remains
wasteful if the next maintainer reads it instead of using the live rail. The
right next trim is not deletion for its own sake. It is to freeze surfaces that
no longer change the next field decision and keep first-read navigation focused
on one executable action.

## Current decision

`FT-0181` remains live. The cube should not add another control layer until a
real returned owner packet exposes a concrete gap. The next substantive move is
outside the archive: a human sends/adapts the bounded packet to an accountable
owner route, or records that no such route exists.
