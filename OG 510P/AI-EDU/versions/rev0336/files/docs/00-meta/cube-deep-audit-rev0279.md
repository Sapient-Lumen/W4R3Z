# Cube deep audit rev0279

Rev0279 reads the cube as a mature control archive with a thin live field rail.
The strongest part is the refusal to launder local artifacts into real evidence:
owner packet prep, send logs, contact-status notes, returned-CSV triage, intake,
workbench seed/review, first-packet decisions, post-decision tickets, and
live-window cards remain below acceptance gates.

## Heart of the archive

The heart is a claim-boundary system for AI in education. Its deepest bet is
that schools and public learning systems need a reliable way to say: this tool
may assist, this evidence is weak, this authority is capped, this learner-facing
claim is forbidden, this record is not yet real, and this change must remain
reversible.

That bet is aligned with the external direction of travel: teacher competency,
student AI literacy, high-risk education use controls, provenance/security, and
causal learning evidence are converging. The cube already has most of those
concepts; its risk is operational sprawl.

## What is missing

The missing object is still not another policy. It is a real owner-attested
packet and a short human-readable execution path. The archive has many surfaces
for what should happen after evidence arrives, but it still lacks the evidence
itself and a brutally simple operator-facing route from first contact to readout.

The second missing object is a compression budget. There are 100 branch-family
surfaces across 12 families and a long release-control plane. Some of that is
useful memory, but some is now attention debt. The archive needs a standard for
when a surface should be summarized, frozen, or demoted to background memory.

## Severe wrongness found

The active queue was stale. `FT-0181` still described rev0276 first-packet
decision work as the current action after rev0278 had already made live-window
card gating current. Because `context-pack.json` is generated from the queue,
the stale live state propagated into the re-entry context while all lints still
passed. That is exactly the kind of waste the archive is designed to prevent:
internal consistency without current truth.

Rev0279 repairs the queue and hardens `check_followthrough_receipt.py` so the
live item must name the current revision and an existing current-revision next
surface. This is a small guard, not a new doctrine family.

## Next high-risk seam

The next seam is the end-of-window readout. A clean live-window card could tempt
the operator to claim service effectiveness, learning impact, safety, access,
workload reduction, or compliance. The readout must stay aggregate, claim-family
bounded, and explicit about what it does not close.

## Refactor direction

The cube should stop growing sideways until field evidence forces it. Use the
router, run the packet, record the send log, and let real owner response decide
which surfaces earn attention. Where possible, compress branch-tail surfaces into
indexes and keep only the live rail in the first-read path.
