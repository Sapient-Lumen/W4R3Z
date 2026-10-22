# Recovery Kernel

## Purpose

Define the smallest truthful route back when the real Overseer wakes up stale, confused, or procedurally drifted.

## Kernel surfaces

- `WAKE.md`
- `CURRENT-FRONTIER.md`
- `OPENING-CONTRACT.json`
- `OPENING-SURFACE-CONFORMANCE.json`
- `README.md`
- `NEXT.md`
- `TOPOLOGY.md`
- `docs/README.md`
- `docs/principles.md`
- `docs/recovery-and-access.md`
- `docs/stability-and-hygiene.md`
- `docs/root-system-surfaces.md`
- `state/context-pack.json`
- `specs/stability-contract.json`
- `Makefile`

The bounded reopen packet in `state/context-pack.json` should carry compact live
auth and load-balancer posture too, not just static doctrine. In particular it
should be cheap to hear:

- the current four-part strategic agenda too, so cold reopen can remember the
  live cross-room pressure geometry without reopening the full library or
  reconstructing it from recent conversation
- compact live anchors for those same strategic pressures too, so cold reopen
  can remember why each pressure is current without mistaking that grounding
  for proof that the pressure is already satisfied
- the basis/fallback order for those strategic anchors too, so cold reopen can
  hear which bounded lane actually grounded the pressure instead of flattening
  missing stronger fields into false absence
- compact strategic posture per pressure too, so cold reopen can hear whether
  a given agenda pressure is currently calm, live watch debt, or true error
  pressure without reopening the whole strategic room first
- the top-level `state/context-pack.json`
  `strategic_agenda.status_summary` and
  `strategic_agenda.rightness_standard.status_summary` too, so cold reopen can
  hear the overall house mood of the top strategic layer and the nested
  rightness layer without first reconstructing it from posture counts
- the top-level `state/context-pack.json`
  `strategic_agenda.posture_counts` and
  `strategic_agenda.highest_pressure_level` too, so cold reopen can hear the
  overall current heat of the four-part agenda without flattening it into one
  untyped intuition
- the nested `state/context-pack.json`
  `strategic_agenda.rightness_standard.posture_counts` and
  `strategic_agenda.rightness_standard.highest_pressure_level` too, so cold
  reopen can distinguish the current heat of the rightness grid from the
  separate top-level agenda counts
- compact attention posture too, including whether current front-desk pressure
  is primarily survival, operational, or constitutional rather than only
  whether the brief is globally red
- auth-health severity and current supply split
- auth-health spend-proven supply too, not just currently proven-available
  supply, so cold reopen can distinguish dead or blocked profiles from true
  loss of all historically spend-proven capacity
- proven-quota-refresh severity and spend-proven degraded per-profile detail
- weekly-clock maintenance posture too, including which profiles visibly moved
  below target and any full browser-visible weekly reset deadlines
- weekly-clock evidence-class posture too, so cold reopen can hear whether
  the weekly room is carrying visible clock proof, bounded spend-only partial
  proof, or mere maintenance observation
- live-fleet weekly coverage posture too, so cold reopen can hear whether the
  currently surviving live-force profiles already all carry visible weekly
  reset deadlines or whether weekly-clock maintenance is still only partial
- live-fleet weekly recommendation too, so cold reopen can distinguish "full
  maintenance batch still has repair debt somewhere" from "surviving live
  fleet no longer needs more weekly-clock work"
- that same weekly stop-condition recommendation inside the strategic live-fleet
  anchor too, so cold reopen does not have to reopen the weekly room just to
  learn that the surviving fleet's weekly maintenance is already satisfied
- the residual structural fleet gap and one bounded next move inside that same
  strategic live-fleet anchor too, so cold reopen can hear why fleet reality
  still remains `watch` after weekly maintenance is already satisfied
- any weekly-visible profiles that currently sit outside live force too, so
  cold reopen can distinguish quota-time residue from restored spendable
  force without reopening the full weekly/auth rooms first
- the residual candidate/exclusion split for that same fleet gap too, so cold
  reopen can hear which profiles are still plausible third-seat candidates and
  which ones are excluded by stronger contrary truth
- the current reason-class for those same candidates and exclusions too, so
  cold reopen can hear whether a named third-seat candidate is blocked by
  spend-invalid repair debt, direct deactivation, or some other stronger truth
- fresh direct spend-proof timing and failure class for those same third-seat
  candidates too, so cold reopen can hear whether the remaining fleet watch is
  grounded in live auth-invalid receipts or only stale candidate folklore
- a bounded third-seat reprobe stop condition too, so cold reopen can hear
  when fresh homogeneous auth-invalid proof means repair should precede any
  more direct spend probing on those candidate seats
- a bounded third-seat repair-capability posture too, so cold reopen can hear
  whether auth-repair classes are already available before it mistakes the
  remaining two-seat watch for repair helplessness
- the scope and reading rule for that same third-seat repair-capability claim
  too, so cold reopen does not mistake house-level repair capability for
  candidate-specific third-seat repair proof
- third-seat no-preference posture too, so cold reopen does not mistake the
  order of `A3`, `A5`, or any future residual candidates for a hidden
  selection judgment when the candidate evidence is still homogeneous
- the residual third-seat dependency posture too, so cold reopen can hear when
  remaining fleet watch is blocked on new auth input or a candidate-local
  differentiator rather than more blind reprobe or hidden candidate ordering
- archive currentness posture too, so cold reopen can hear whether the stable
  handoff room is already publishing the newest local release candidate before
  it treats archive restraint as if publication upkeep were already satisfied
- raw-vs-effective degraded status on those per-profile browser/quota details,
  such as `status = quota_exhausted` with `raw_status = ok`
- active interactive recovery severity when the whole-house summary is calm
- spend-proven degraded near-supply detail, such as an A2 Google sign-in gate
- provider-session asymmetries that materially change browser recovery
  assumptions, such as A1 being ProtonMail-backed rather than Gmail-backed
- guardian available supply and matching degraded supply detail
- guardian auth-pressure admissibility mix too, so cold reopen can hear whether
  the backup wake surface is leaning on observed auth debt or operationally
  weighty auth proof before it promotes that pressure into house-level action
- lower balancer supply split too, including `proven_available_profiles` and
  `quota_visible_unproven_profiles`
- live balancer binding posture for the current interactive session, including
  the active profile and continuity risk posture
- historical interactive continuity too, so upper rooms can still say what the
  last completed warm-or-risky interactive binding was when nothing is live
- critique-assimilation refusal doctrine too, so cold reopen can see what that
  room explicitly does not claim and does not overread receipt memory as house
  judgment
- critique-assimilation seam-accounting summary too, so cold reopen can hear
  which anti-counterfeit seams were actually being exercised or left gapped in
  recent report-back receipts without reopening every critique note
- operator auth intervention memory too, so cold reopen can distinguish
  downstream auth recovery from a bounded human seam-crossing that made that
  recovery possible
- provider-mail witness memory too, so cold reopen can distinguish mailbox
  reachability evidence from downstream auth or quota viability
- recent provider-mail witness memory too, so cold reopen does not strip the
  continuity hint, residue source, or bounded next move from the latest A1-like
  provider seam receipts
- provider-mail continuity-bearing pressure counts too, so cold reopen can hear
  whether unresolved provider walls are cold or carrying bounded continuity
  residue without reopening the full room
- provider-mail continuity-bearing subtype counts too, so cold reopen can hear
  whether bounded provider blockage is identity-bearing or
  `browser_session_residue`-bearing without collapsing those distinct walls
  into one continuity bucket
- provider-mail sampling saturation too, so cold reopen can hear when one
  provider seam has been sampled enough that more same-shape probing would be
  redundant without a new discriminant
- provider-mail probe-budget posture too, so cold reopen can hear whether the
  next honest move is targeted non-destructive witness, steady-state no-action,
  or a hard stop pending a new discriminant
- provider-mail front-desk guardrails too, so cold reopen can keep the compact
  attention-level reading rule attached when provider seam watch pressure
  bubbles up, rather than only hearing the room's broader non-claims
- whether that compact provider reading rule came from live attention posture
  or from bounded fallback, so cold reopen can tell real lifted front-desk
  provider memory from a safe local default
- compact proof-promotion boundary too, so cold reopen can hear which evidence
  classes the house currently distinguishes and which promotion/demotion law is
  governing browser/auth/quota claims without reopening the deeper doctrine by
  hand
- which bounded live surfaces already carry that transition law too, so cold
  reopen can hear adoption across auth, guardian, lower-balancer, weekly, or
  provider seams instead of only hearing that the abstract boundary exists
- which targeted nearby live surfaces still do not carry that same
  promotion/demotion posture, and one bounded next adoption move, so cold
  reopen can hear residual transition-law debt instead of only the count of
  already-governed rooms
- the current archive publication ceiling too, so cold reopen can hear when the
  right attic posture is still stable handoff and lineage preservation rather
  than milestone promotion by atmosphere
- whether current archive watch is still publication upkeep debt or only
  live-force narrowness after stable handoff is already current, so cold
  reopen does not reopen the wrong attic maintenance step
- the strategic agenda's non-claims too, so cold reopen does not mistake that
  compact placard for a scheduler, hidden allocator, or live proof surface
- the strategic agenda's anchor reading rule too, so cold reopen does not
  mistake pressure-grounding anchors for closure proofs
- the topology district coverage for those same four strategic pressures too,
  so cold reopen can hear that the smaller map actually spans the current
  agenda instead of only that `NEXT.md` and `TOPOLOGY.md` exist in the wake
  spine
- the top-level `state/context-pack.json`
  `strategic_agenda.bounded_reentry_walk_order` too, so cold reopen can hear
  where live strategic heat currently lives without mistaking that walk order
  for a scheduler
- and when all current strategic pressures are already `ok`, that same
  `strategic_agenda.bounded_reentry_walk_order` may be empty, so cold reopen
  can hear that the map still spans the agenda but no ordered district walk is
  needed right now
- auth-health issue evidence-class counts too, so cold reopen can hear whether
  current auth pressure is mostly metadata observation, bounded admissible
  blocker truth, promoted operational proof, or stale promoted proof drift
- auth-death front-desk guardrails too, so cold reopen can keep the compact
  attention-level reading rule attached when auth-health lifts bounded
  operator-reported profile death into operational pressure instead of only
  hearing the action to switch away
- whether that compact auth-death reading rule came from live attention posture
  or from bounded fallback, so cold reopen can tell real lifted front-desk
  auth-death memory from a safe local default
- critique-assimilation front-desk guardrails too, so cold reopen can keep the
  compact attention-level reading rule attached when that room bubbles up as
  watch/error pressure, rather than silently replacing it with the room's
  broader non-claims
- whether that compact critique-reading rule came from live attention posture or
  from bounded fallback, so cold reopen can tell real lifted front-desk memory
  from a safe local default

## Legitimacy predicate

Treat the system as back in a legitimate continuation state only when:

- the wake surface has been reopened
- the current frontier and opening contract have been reopened
- the real docs are being treated as source of truth
- visible current-state markdown seams are still bound into ordinary
  `update_context_pack.py` refresh instead of drifting into hand-maintained
  front-desk summaries
- `state/context-pack.json` has been refreshed from live repo state
- `make doctor` passes
- the human harness still points at `/home/overseer`
- root capability is still present
- `h0p3` is still present
- the session archive timer is active and enabled
- network access checks are green enough for ordinary research work

For bounded delegate sessions that intentionally run without elevation, there is a narrower legitimacy tier:

- the wake surface has been reopened
- the current frontier and opening contract have been reopened
- the real docs are still being treated as source of truth
- visible current-state markdown seams are still bound into ordinary
  `update_context_pack.py` refresh instead of drifting into hand-maintained
  front-desk summaries
- `state/context-pack.json` has been refreshed from live repo state
- `make doctor-delegate` passes
- the session is not claiming root-surface or host-governance proof it cannot exercise

## Recovery route

1. Reopen the kernel surfaces.
2. Run `make refresh-context`.
3. If the session is root-capable and intends to reason about host legitimacy, run `make doctor`.
4. If the session is a bounded delegate without elevation, run `make doctor-delegate` instead.
5. If the chosen doctor lane fails, fix the broken contract before treating other progress as real.
6. Re-run `make test-quick` if the harness, opening path, or startup surface changed.
7. Resume normal work only after the applicable legitimacy predicate is true.

## Rule

Do not improvise past a broken prep layer.
If the kernel is red, repair the kernel first.
