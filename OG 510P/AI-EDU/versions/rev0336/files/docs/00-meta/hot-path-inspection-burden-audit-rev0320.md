# rev0320 hot-path inspection burden audit

## Finding

Rev0319 reduced concept-design burden, but it left a packet-inspection burden: an operator had to
open the owner plan, session log, readout, measure card, decision memo, and manifest to know whether
a run was still blank, partially completed, unsafe, or locally reviewable.

## Correction

Rev0320 consolidates that inspection into `tools/score_teacher_tutor_micro_pilot_readiness.py`. The
tool is registered as a utility, not a release-control validator. Its outputs stay in scratch.

## Waste avoided

The correction avoids a new governance branch, a new schema family, and a new evidence-status ladder.
It turns an existing run decision into an executable local check.

## Remaining waste

The archive still has large governance and meta tails. They should be consulted only through the
indexes or after real evidence or a validator failure creates a concrete need.
