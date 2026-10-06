# Renewal witnesses, fresh approval acts, and carryforward drift

This is the compact successor surface for `OQ-0123`.

## Practice / observation

DelayBasin now has one compact exception witness for honest temporary waiver.
That solved the question of whether a waiver is honest **now**.
A smaller but still live problem remained:
a later pass can preserve the old exception object, old expiry text, or old aggregate posture and still sound careful while never showing that the waiver was actually renewed.

The archive does not need a standing renewal board for that.
It needs one bounded witness that says whether the current waiver claim depends on a **fresh act** or only on copied-forward residue.

## External pressure from expiring preserved exemptions, updated exceptions, temporary ignores, and approval windows

1. Azure Policy preserves an exemption object for record-keeping after `expiresOn`, but the exemption is no longer honored. That pressures DelayBasin not to treat persistence of the old object as a renewal act. ([`REF-0820`](../00-meta/bibliography.md))

2. AWS Config says `PutRemediationExceptions` adds a new exception or updates an existing exception for a specified resource and that the exception blocks auto-remediation until cleared. That pressures DelayBasin to model renewal as an explicit update act, not mere continued presence of the old exception row. ([`REF-0829`](../00-meta/bibliography.md))

3. Snyk temporary ignores last only until the ignore period expires or the vulnerability becomes fixable, and the Web UI lets operators edit or unignore the issue. That pressures DelayBasin to distinguish a fresh refresh act from a stale ignore that merely used to be tolerated. ([`REF-0826`](../00-meta/bibliography.md))

4. GitHub deployment jobs awaiting required approval stay in `Waiting` and automatically fail if not approved within 30 days. That pressures DelayBasin to keep lapsed approval windows from silently acting like current authority. ([`REF-0830`](../00-meta/bibliography.md))

5. GitHub also keeps deployment review states explicit as `APPROVED` and `REJECTED`. That pressures DelayBasin to preserve fresh reapproval truth rather than inheriting a vague “still fine” gloss from older exception prose. ([`REF-0831`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **renewal witness / fresh-approval act card** whenever a current waiver claim depends on a prior exception window and later rereads could mistake surviving exception residue for renewed authority. Name the **governed obligation row**, the **prior exception witness and prior honor window**, the **renewal act / explicit approving or update surface if any**, the **current honor window**, the **renewal state**, the **aggregate continuity / same effect vs changed effect**, and the **fail-closed repair / revert-to-open vs issue-new-exception-witness vs quarantine-broadened-renewal consequence**. Keep `obligation_state` and the compact exception witness narrow. Do not let copied-forward timestamps, preserved old objects, unchanged default visibility, or stale aggregate posture silently count as renewal.

## Fresh renewal vs copied-forward residue vs changed basis

This is the heart of the successor surface.

- **fresh renewal** says there was a new approving or update act and a current honor window to point at.
- **copied-forward** says the prior exception object or prose survived, but no fresh act currently justifies calling the waiver renewed.
- **expired residue** says the old exception still exists for memory or record-keeping but no longer carries live authority.
- **basis changed** says the later pass is not really renewing the old waiver; it is issuing a meaningfully different exception posture and should say so directly rather than borrowing continuity theater.

So the witness does not create a standing renewal board.
It only says when “renewed” is honest and when the archive should fail closed instead.

## Countermodels / probes

1. **The exception witness is already enough countermodel**
   - Maybe rev0227 already gave the archive everything it needs, and later passes can reconstruct renewal truth from the exception witness plus nearby prose.
   - Probe: compare later rereads on rows with only the exception witness against rows that also carry the compact renewal witness and inspect whether later passes still call copied-forward exceptions “renewed.”

2. **A shifted expiry alone is enough countermodel**
   - Maybe seeing a later date is already sufficient proof of renewal.
   - Probe: inspect whether later passes can distinguish a genuinely reapproved waiver from manual carryforward, cloned old text, or hidden aggregate continuity when only the date changed.

3. **Every renewal needs standing governance countermodel**
   - Maybe renewal truth is too cross-cutting for one bounded witness and always needs a broader reapproval institution.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still overflow into genuine multi-row tenure governance rather than ordinary renewal exactness.

## Design consequences

- add one controlled `renewal_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `fresh-renewal`, `copied-forward`, `expired-residue`, and `basis-changed`;
- use the witness only where a current waiver claim depends on a prior exception window or prior accepted-risk act;
- keep exact approver identity, rationale prose, and neighboring mitigation detail outside the compact token itself;
- prefer `issue-new-exception-witness` when the later pass is really changing the exception basis or aggregate effect;
- and quarantine any stronger reapproval court, renewal senate, or tenure board unless repeated overflow shows that one bounded renewal witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact renewal witness is no longer enough — for example, if the archive honestly needs standing reapproval authority across many rows, tenure policy over renewal windows, or broad exception-scope governance that cannot be expressed as one bounded witness plus the existing exception witness.

Until then, prefer this compact successor surface over a reapproval court, renewal senate, or tenure board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the waiver is still there.”
It is also preserving whether a later pass can point to a fresh act that renews authority, or whether it is only inheriting old tolerated residue.
That matters because later stateless passes can preserve all the neighboring caveats and yet still silently reauthorize an exception just by sounding continuous.
