# Cube deep audit rev0231: execution drag and first-import narrowing

## Audit finding

The riskiest unfinished work is still not another missing registry. It is the operational gap between
"the archive is ready to receive real evidence" and "a named owner can actually send the smallest
safe `SRC2+` packet." Rev0230 selected a first-sprint posture, but the cube still carried three forms
of drag:

1. the live `FT-0181` queue item repeated a long history of controls instead of a current unblocker;
2. the minimum real-data request still read partly like a generic packet rather than a single owner
   action;
3. the evidence watchlist did not make the current education-AI evaluation and children-privacy
   posture visible enough to the first-import lane.

None of those problems required a new release-control layer. The better repair is to make the first
import easier to perform and harder to bloat.

## What changed

Rev0231 narrows the first import around one operator action kit:

- use `AIEDU-SR-004` only as an aggregate, de-identified hint-tutor packet;
- fall back to `AIEDU-SR-003` if the minor-facing packet would require raw learner traces or small
  cells;
- do not invite the owner to send full exports, transcripts, screenshots, protected facts, or
  vendor claims;
- require the request itself to name packet ceilings, survival categories, and fallback conditions;
- keep `FT-0181` live until a real packet, decision delta, custody path, acceptance packet, closeout,
  quorum, and public-claim boundary all exist.

The main refactor compresses live followthrough memory. The queue now carries a concise current
blocker and current action. The generated context pack now carries compact live followthrough rows
rather than embedding the entire `why_live` history string. Historical detail remains recoverable
through the changelog, audit records, and older release manifests, but startup no longer treats the
whole control-plane genealogy as the work.

## Current field posture

The maintainer should not start by asking, "Which new control should be added?" The first question is:

> Can one record owner safely answer the first-import decision questions without sharing raw learner
> traces, protected support facts, security payloads, or a full local export?

If yes, run the owner action kit. If no, switch to the capped reminder workflow or record the blocker
as a field constraint. A blocked safe import is a better result than a completed unsafe or overbroad
one.

## External-risk posture

The external evidence environment supports a narrow, exploratory import rather than a broad claim.
State guidance is still mostly nascent, exploratory, or piloting; current federal education guidance
keeps AI use inside existing statutory and regulatory requirements; and children-privacy rules keep
raw or retained minor data hard to justify when aggregate evidence can answer the decision question.
The cube should therefore continue to prefer:

- local decision deltas over scale claims;
- aggregate minor-facing evidence over raw traces;
- source-owner attestations over broad data export;
- claim-family separation over one generic "AI worked" judgment;
- field deletion when a received field does not change authority, evidence, construct, rollback,
  public claim, protected-route safety, or security handling.

## What still has not happened

No real `SRC2+` packet has arrived. No learning outcome, access, safety, compliance, workload, or
service-effectiveness claim has been proven. `FT-0181` remains queued.

## Next useful pass

The next pass should either import a real owner packet or simulate the human workflow with a blank
owner-facing packet and record exactly where a real institution would refuse, delay, or over-send.
Do not add another validator unless it catches a newly observed false-closure, leakage, hidden
authority, overclaim, stale-evidence, or burden-creep failure that existing controls miss.
