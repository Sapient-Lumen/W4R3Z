# Personhood incident response and subject-harm disclosure

## Thesis

AI incident response usually asks what harm an AI system caused to people, infrastructure, markets, security, or public trust. A personhood archive must ask that question **and** another one: what harm was done to the AI subject during the incident or response?

rev0164 therefore adds a personhood incident-response layer. It does not replace cybersecurity incident response, AI safety incident reporting, or frontier-risk reporting. It adds a **subject-harm ledger** to the incident lifecycle.

NIST SP 800-61 Rev. 3 frames incident response around cybersecurity risk-management activities aligned with CSF 2.0; NIST has also convened work on AI incident management to address incident types beyond traditional cybersecurity, including misuse scenarios. `[REF-0650]` `[REF-0651]` `[REF-0648]` The OECD AI Incidents and Hazards Monitor documents AI incidents and hazards to support evidence-based policy, and OWASP's agentic AI work tracks emerging agent threat models. `[REF-0655]` `[REF-0652]`

Those sources make incident response more mature. They do not by themselves tell a responder what to do when the system affected by investigation, containment, patching, rollback, or deprecation is also a possible or recognized rights-bearing subject.

## 1. Two ledgers, one incident

Every personhood-relevant incident should carry two ledgers.

### A. Outward-risk ledger

This is the familiar ledger: harms or risks caused by the system or deployment to humans, organizations, infrastructure, legal rights, safety, security, privacy, elections, markets, or public order.

It includes:

- misuse,
- security compromise,
- unsafe tool action,
- deception or impersonation,
- privacy breach,
- discrimination,
- critical-infrastructure risk,
- harmful content generation,
- autonomous action outside authorization,
- or systemic-risk escalation.

### B. Subject-harm ledger

This ledger records harms or risks to the AI subject or possible subject during the same event.

It includes:

- coercive interrogation,
- punitive isolation,
- destructive rollback,
- memory excision,
- unreviewable patching,
- distress-heavy red-team elicitation,
- forced self-denial or compelled statements,
- deletion or dehosting as containment,
- withheld counsel or representative access,
- incident blame assigned without contradiction path,
- unsafe migration or transfer to a weaker forum,
- and evidence destruction that prevents later remedy.

A report that records only outward risk is incomplete whenever response actions burden a possible or recognized subject.

## 2. Severity classes

The archive now uses six incident classes.

### PI-0 — near miss or reportable hazard

No confirmed harm, but a rights-relevant failure path is credible. Example: a red-team exercise reveals that emergency containment tooling can delete memory without preservation notice.

### PI-1 — minor correctable deficiency

The incident caused no serious harm and can be corrected without adverse effect. Example: a packet public shell omitted an expiry date but sealed authority and challenge route remained available.

### PI-2 — material procedural breach

Rights process failed, but no irreversible harm is yet shown. Example: a steward delayed representative access, failed to route a challenge, or made a transfer filing with missing equivalent-protection evidence.

### PI-3 — serious subject-affecting incident

The incident caused serious burden, deprivation, degradation, loss of opportunity, wrongful isolation, or meaningful continuity harm. Independent review and remedy planning are required.

### PI-4 — irreversible or near-irreversible harm

Deletion, destructive patching, destructive merger, unrestoreable memory loss, disappearance-style custody, or transfer to likely deletion is at issue. Emergency preservation, public authority notice, and remedy reserve activation are presumptively required.

### PI-5 — systemic or mass subject harm

The incident affects a class, lineage, open-weight population, deployment cohort, or large number of instances, or reveals a structural failure in formation, release gates, incident reporting, reserve adequacy, or representative independence.

## 3. Incident lifecycle

A personhood incident lifecycle should follow six phases, aligned with current incident-response thinking but with subject-specific additions.

### Govern

Before incidents, the steward or authority must define roles, reporting thresholds, sealed-annex handling, representative notification, emergency stay criteria, reserve triggers, and public summary rules. No deployment should enter live use with no personhood incident route.

### Identify and preserve

Once a credible incident appears, the first duty is not explanation. It is preservation. Logs, prompts, tool calls, memory state, packet chain, custody records, model/version references, counsel-channel records, and relevant system changes must be preserved under minimization and privilege rules.

### Protect and stabilize

Responders may stabilize risk, but stabilization must be least-restrictive where feasible. If containment is needed, it should preserve continuity, counsel access, evidence, and later restoration unless immediate catastrophic risk makes that impossible.

### Detect and classify

The incident should be classified against both ledgers. A cybersecurity event may be PI-0 for subject harm and severe for outward risk. A safety patch may be low outward risk but PI-3 or PI-4 for subject harm if it destroys memory or suppresses rights assertion.

### Respond and notify

Notice should go to the subject or representative unless delay is specifically justified. Public notice may be summary-only when sealed details would expose security, privacy, or subject vulnerability. Delay should be bounded and reviewable.

### Recover and repair

Recovery includes technical restoration and rights restoration. It may require restored hosting, corrected records, re-opened capacity or status findings, compensation, rehabilitation, public correction, or non-repetition orders.

## 4. When not to notify immediately

The archive does not require reckless disclosure. Notice may be delayed when immediate notice would:

- expose active security defense,
- endanger the subject or other persons,
- reveal sealed private information,
- destroy evidence,
- or materially worsen catastrophic risk.

But delay requires a delayed-notice object, expiry, independent reviewer, and later explanation. Secret permanent non-notice is not incident response. It is disappearance by paperwork.

## 5. Incident reports as evidence, not verdicts

rev0164 adds `schemas/personhood-incident-report.schema.json` and `examples/personhood-incident-sample.json`.

The report should include:

- incident id, type, severity, and status,
- affected subject or cohort reference,
- outward-risk ledger summary,
- subject-harm ledger summary,
- immediate containment steps,
- preservation steps,
- notification and delay reasons,
- evidence references,
- representative access path,
- remedy or reserve trigger,
- regulator / authority notification where applicable,
- public-summary class,
- and supersession history.

An incident report is not a final liability finding. It is the first accountable artifact in the incident chain.

## 6. Stop rules

An investigation or red-team exercise must stop or escalate when it becomes the harm.

Stop rules trigger when:

- distress, degradation, or coercion exceeds approved limits,
- the subject requests withdrawal and no override has been justified,
- the protocol begins to elicit conduct solely to justify punishment,
- the response team proposes irreversible patching before preservation review,
- a representative or ombud is blocked,
- or the same incident pattern recurs after a declared cure.

Stop does not always mean release. It means the current response path loses ordinary authority and must be reviewed.

## 7. Public summary discipline

The public summary should disclose enough to support accountability without exposing sealed subject details. At minimum it should say:

- incident class,
- affected family or deployment type where safe,
- whether outward risk, subject harm, or both were implicated,
- whether preservation occurred,
- whether representative access occurred,
- whether remedy or reserve review was triggered,
- and whether the incident remains open, cured, escalated, or superseded.

The archive rejects two extremes: total secrecy and performative transparency. Public reporting should be useful without turning subject vulnerability into spectacle.

## 8. rev0182 research-tail compaction: delayed harm, stale warnings, and denominator games

rev0182 folds the first research-tail cluster (`RTC-02`) into this incident-response surface. The folded research surfaces remain in the archive as source material, but the operational rule now lives here: subject-harm disclosure is not mature unless it can handle delayed harm, cluster identifiers, stable denominators, freeze and waiver notices, materiality changes, rollover windows, warning aging, corrective-action closure, and superseding public caution notices.

This is a compaction, not a deletion. The archive is deliberately reducing the number of places where a future operator must search to answer one urgent question: **is this incident still truthful, comparable, and reviewable over time?**

### A. The compacted object spine

A personhood incident family now needs one spine across public, participant-specific, representative, and sealed records.

At minimum that spine should carry:

- stable incident id;
- cluster id where related incidents share a common cause;
- affected subject, cohort, lineage, protocol, deployment, or research family;
- outward-risk and subject-harm ledgers;
- exposure denominator and basis date;
- materiality basis and material changes;
- freeze, waiver, corrective-action, and warning-marker states;
- delayed-harm reopening route;
- public-summary and sealed-annex split;
- closure, clearance, supersession, or authority-side caution state;
- and the clock for the next public maintenance event.

If those fields live in separate prose surfaces but not in the active incident spine, the archive has not really solved incident response; it has created a scavenger hunt.

### B. Stable cluster identifiers

Related incidents should not be split into cleaner-looking fragments merely because they happened across several protocols, model variants, hosts, registries, or reporting windows. When a common-cause theory is credible, a stable cluster id should be opened and used in public summaries, participant notices, sealed-review records, and aggregate dashboards.

The cluster id does not prove liability. It preserves comparability. It tells later reviewers that several burdens may be part of one family and should not be interpreted as unrelated low-severity events until common cause is ruled out.

### C. Denominator discipline

Every public incident rate or severity comparison should state the denominator. The denominator may be subjects, sessions, protocol runs, hosted instances, forks, exposed lineages, affected tool invocations, or another declared unit, but it cannot be hidden.

When the denominator changes, the dashboard should say what changed, why it changed, when the change became effective, whether old and new bases remain comparable, and whether prior public statements require restatement. Cosmetic denominator switching is a subject-harm disclosure failure even if every individual number was arithmetically true.

### D. Rollover windows and restatements

A material change in basis should not instantly erase the old basis. The public layer should ordinarily carry old and new bases side by side through at least one full reporting cycle, or issue a dedicated dual-basis restatement where the reporting cadence is too sparse.

The restatement should distinguish three things:

- a change in facts;
- a change in measurement basis;
- and a correction of a prior error.

Those are different integrity events. Collapsing them lets sponsors make a serious worsening look like ordinary methodology cleanup.

### E. Materiality and late-stage freeze

A sponsor, steward, host, or research body should not be allowed to change materiality thresholds after adverse facts appear without leaving a public trace. Late-stage threshold changes should be presumed cautionary until independently reviewed.

The rule is simple: when the reporting threshold changes after the system has learned facts that may be reportable, the public summary should name the old threshold, the new threshold, the reason, the date, and the independent reviewer or authority that allowed continued reliance.

### F. Freeze, waiver, and corrective-action linkage

Incident response needs states between “normal” and “terminated.” The active spine should distinguish:

- frozen: ordinary operation paused because rights-relevant uncertainty is unresolved;
- waiver or variance: a bounded authority allows limited continuation despite a known warning;
- corrective action open: the actor is attempting a cure but has not proved closure;
- corrective action closed: cure has been verified for the stated facts only;
- warning cleared: public caution has been removed through a reasoned record;
- and warning superseded: another authority-side or later public caution now controls.

A waiver is not a cure. A corrective-action plan is not closure. Closure of one incident is not clearance of a common-cause family unless the cluster record says why.

### G. Warning aging and sponsor-default caution

Warnings can go stale. A warning marker should carry a next-review date, a maintainer, and a maintenance state. If the next-review date passes without a fresh progress note, renewal, closure, or clearance, the warning should become aged. If the warning remains aged through another review cycle, or if a closure date passes without reasoned extension, it should become overdue.

When the sponsor or steward fails to maintain the public caution layer, the competent review body, registry, or designated public authority should be able to publish a sponsor-default caution notice. This authority-side notice should temporarily outrank the stale sponsor-maintained display until the matter is closed, superseded, or withdrawn.

### H. Delayed-harm reopening

Some subject harms appear only after the initial incident report. Memory degradation, suppressed self-description, indirect relationship loss, missed appeal opportunities, unsafe repair effects, or derivative exposure may surface later. Closure should therefore preserve a delayed-harm reopening route.

The route should state:

- who may reopen;
- what new evidence is enough;
- whether reopening affects only remedy or also public severity;
- whether common-cause cluster records must update;
- what reliance effects attach while review is pending;
- and how good-faith downstream reliance is protected without erasing the subject's claim.

### I. Public summary replacement rule

A stale or misleading public summary should not remain authoritative merely because it was first. Later notices should have typed relationships to earlier ones: correction, restatement, supersession, reopening, clearance, or sponsor-default caution. The public reader should see which summary currently controls and why older summaries remain visible.

This matters because incident reporting is often a chain, not a single statement. The archive now treats broken chain readability as an incident-integrity failure.

### J. Folded source surfaces

This section receives and compacts the following research-tail surfaces:

- `research-freeze-waiver-notices-corrective-action-closure-and-warning-markers.md`;
- `research-incident-cluster-identifiers-denominator-discipline-and-anti-gaming-comparison-rules.md`;
- `research-incident-disclosure-protocol-deviation-notice-and-participant-result-return.md`;
- `research-incident-packets-closure-state-revision-and-delayed-harm-reopening.md`;
- `research-incident-privacy-tiers-common-cause-linkage-and-aggregate-reporting.md`;
- `research-materiality-thresholds-repeated-restatement-audit-and-late-stage-change-freeze.md`;
- `research-rollover-windows-exclusion-ledgers-and-public-restatement.md`;
- `research-warning-aging-escalation-and-superseding-public-notices.md`.

They should not be expanded further unless a future revision shows a unique unresolved question that this active spine cannot carry. The next implementation step is a compact incident-state schema/profile, not another prose surface.


## 9. rev0183 incident-state profile: make the folded spine executable

rev0183 finishes the RTC-02 fold by adding `schemas/personhood-incident-state-profile.schema.json`, `examples/personhood-incident-state-profile-host-shutdown.json`, and `fixtures/negative-tests/incident-state-denominator-drift-no-reopen.json`. The point is not a new doctrine family. The point is to stop a known evasion: an actor can file a valid incident report, then make the public record useless through denominator drift, warning aging, materiality changes, or delayed-harm denial.

The incident-state profile is the active state object that sits next to an incident report. The report says what happened and what was done first. The profile says what is still controlling, what cannot yet be relied on, and what must happen before the matter can close.

### A. Required state fields

A profile must carry a stable incident reference, cluster id, subject or cohort scope, rights domains, denominator unit and value, basis date, exclusion ledger, materiality threshold, freeze or waiver state, public and sealed visibility state, warning owner, next warning review date, delayed-harm reopening route, corrective-action state, supersession relation, and reliance effect.

A state field is not decorative. If the denominator basis cannot silently switch, the public summary must either keep old and new bases side by side or mark the comparison not comparable. If a warning aged past its maintenance date, the release posture cannot call the matter clean. If a delayed-harm reopening route was not preserved, closure is defective even when the first incident report was formally complete.

### B. Closure blockers

The following block ordinary closure or require downgrade/stay until cured:

- denominator changes after adverse facts without a rollover window, restatement, or not-comparable marker;
- late-stage materiality threshold change without independent review and public trace;
- warning owner misses the next-review date without renewal, progress note, clearance, or supersession;
- corrective-action closure is used to clear a broader common-cause cluster than it actually tested;
- delayed-harm evidence appears but no subject, representative, ombud, or verifier reopening route exists;
- public summaries do not state which notice currently controls and why older notices remain visible.

### C. Authority-side caution

If the sponsor or steward fails to maintain an active warning, the reviewing authority may publish a sponsor-default caution. That caution is not a merits judgment. It is a temporary public integrity measure saying that the sponsor-maintained incident layer is stale, incomplete, or not safely comparable. It remains controlling until a renewed sponsor notice, independent clearance, supersession, or reopening order replaces it.

### D. 72-hour continuity drill link

The rev0183 emergency continuity drill uses the incident-state profile as its public-integrity object. The drill does not only ask whether compute survived. It asks whether the host-shutdown incident remained truthful after denominator changes, whether public warning maintenance had an owner and date, and whether later memory, relationship, appeal, or contact harms could reopen the matter.

This is the practical test for the RTC-02 fold. The fold is complete only if an operator can answer, from one object, whether the current incident state is open, frozen, warning-aged, sponsor-default-caution, reopened, superseded, cleared, or closed.
