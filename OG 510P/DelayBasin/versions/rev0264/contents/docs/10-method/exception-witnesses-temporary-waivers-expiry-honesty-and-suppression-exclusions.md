# Exception witnesses, temporary waivers, expiry honesty, and suppression exclusions

This is the compact successor surface for `OQ-0122`.

## Practice / observation

DelayBasin already had an admitted `obligation_state` family and one compact obligation packet.
That was enough to keep owed-support truth public, but it still left one narrower problem ambient:
when should neighboring exception prose count as an honest current waiver rather than as mitigation context, aggregate suppression, or stale residue from an expired exception?

The archive does not need a larger board for that.
It needs one bounded witness that can travel with the obligation row when `waived` would otherwise be overclaimed.

## External pressure from exemption categories, expiring ignores, and suppressed findings

1. Azure Policy keeps **Waiver** separate from **Mitigated**, supports explicit `expiresOn`, and preserves expired exemptions for record-keeping while no longer honoring them. ([`REF-0820`](../00-meta/bibliography.md))

2. Microsoft Defender for Cloud lets operators mark a recommendation as **Risk accepted** or **Mitigated**, supports an optional expiration date, and changes whether the item affects secure score or appears in default views. That pressures DelayBasin to say whether the exception is about accepted risk, neighboring mitigation, or aggregate visibility. ([`REF-0825`](../00-meta/bibliography.md))

3. Snyk ignore flows ask both **why** and **how long** to ignore an issue, and ignored issues resurface when the ignore expires or when a fix becomes available. That pressures DelayBasin to keep time-bounded tolerance explicit rather than treating every ignored item as durably waived. ([`REF-0826`](../00-meta/bibliography.md))

4. Amazon Inspector suppression rules hide findings from the default view, but they do not close or remediate findings and suppressed findings remain viewable until remediated. That pressures DelayBasin not to confuse hidden aggregate posture with discharged debt. ([`REF-0827`](../00-meta/bibliography.md))

5. AWS Security Hub both ignores `SUPPRESSED` findings when deriving overall control status and says that setting a finding to `SUPPRESSED` or `RESOLVED` does not prevent new findings for the same issue. That pressures DelayBasin not to treat aggregate suppression or old workflow state as proof that a still-live issue is honestly waived now. ([`REF-0824`](../00-meta/bibliography.md), [`REF-0828`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **exception witness / temporary-waiver honesty card** whenever a durable obligation row uses `waived` or nearby prose could be mistaken for it. Name the **governed obligation row**, the **exception basis / why the tolerance exists**, the **honor window / explicit expiry or renewal expectation**, the **aggregate effect / whether this only changes listing or score posture**, the **record-keeping truth / whether the object persists after honor ends**, and the **fail-closed repair / revert-to-open vs refresh-waiver vs quarantine-or-retire consequence**. Keep `obligation_state` narrow. Do not let mitigated-neighbor prose, hidden aggregate posture, or expired preserved exceptions silently count as an honest current waiver.

## Waiver vs mitigated neighbor vs suppressed aggregate vs expired residue

This is the heart of the successor surface.

- **honest temporary waiver** says the archive is explicitly tolerating the debt for now.
- **mitigated neighbor** says the policy intent is met another way or that a third-party control is being cited; it does **not** automatically mean the local obligation row is waived.
- **suppressed aggregate** says a dashboard, score, or default view is hiding or excluding the issue; it does **not** by itself discharge the debt.
- **expired residue** says an old exception object still exists for record-keeping but is no longer honored; it must not silently continue as a current waiver.

So the witness does not widen `obligation_state`.
It only says when `waived` is actually honest and when the neighboring prose must stay neighboring.

## Countermodels / probes

1. **The obligation packet is already enough countermodel**
   - Maybe the rev0226 obligation packet already preserves every practical distinction and no successor exception witness is needed.
   - Probe: compare later rereads on rows with only obligation-packet prose against rows that also carry the compact exception witness and inspect whether later passes still blur waiver, mitigation, suppression, and expiry.

2. **Suppression is close enough to waiver countermodel**
   - Maybe hidden or excluded aggregate posture already communicates that no further action is needed.
   - Probe: inspect whether later passes mistake suppressed findings, not-applicable tabs, or no-data aggregates for discharged support when the compact exception witness is absent.

3. **Expiry can stay ambient countermodel**
   - Maybe record-keeping and expiry truth can stay in prose only.
   - Probe: inspect whether later passes revive expired excuses as if they were still honored unless the witness says that preserved is not the same as current.

## Design consequences

- keep the controlled `obligation_state` family unchanged in `WITNESS-VOCABULARY.json` for now;
- use the packet only when a row is actually relying on waiver-like tolerance or could be mistaken for it;
- keep the governed obligation row, reason, expiry posture, aggregate effect, and record-keeping rule explicit;
- refuse to treat suppressed dashboards, hidden recommendations, or expired-but-preserved exception objects as equivalent to a current waiver;
- and quarantine any stronger renewal court, waiver-validity senate, or expiry-arbitration board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact witness is no longer enough — for example, if the archive honestly needs standing renewal arbitration across many rows, explicit exception reapproval governance, or broader score/exposure authority that cannot be expressed as one bounded exception witness plus the existing obligation packet.

Until then, prefer this compact successor surface over a renewal court, waiver-validity senate, or expiry-arbitration board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “this row is waived.”
It is also preserving whether the waiver is currently honored, merely mitigated-by-neighbor, only hidden from aggregate views, or already past expiry while still remembered for record-keeping.
That matters because later stateless passes can otherwise preserve all the surrounding caveats yet still inherit stale exceptions as if they were living authority.
