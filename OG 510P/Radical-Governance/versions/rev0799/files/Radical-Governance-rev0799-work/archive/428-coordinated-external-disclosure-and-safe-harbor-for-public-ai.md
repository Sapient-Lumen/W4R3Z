# 428 — Coordinated external disclosure and safe harbor for public AI

## One-line thesis

Public bodies running consequential AI should publish a safe external reporting path that authorises good-faith disclosure of security, safety, bias, and rights harms, with response clocks and named remediation ownership.

## Why this matters

Many consequential failures are first seen from the outside.

An affected person may notice an unfair denial before the operator does. A security researcher may discover prompt injection, data leakage, or model abuse before the internal team sees it. A civil-society group may detect a pattern of discriminatory outcomes before any dashboard flags drift.

But outside reporting often fails because the public body has not clearly said:

- where reports should go,
- what kind of testing or reporting is permitted,
- whether good-faith researchers or affected people will face retaliation,
- how quickly the institution will acknowledge and triage the report,
- how the report will connect to actual remediation.

Official practice already supports a stronger norm. CISA’s Vulnerability Disclosure Policy platform exists to give agencies a primary entry point for public researchers and BOD 20-01 requires agencies to develop and publish a vulnerability disclosure policy and maintain handling procedures. NIST’s AI RMF Playbook says feedback processes for end users and impacted communities should be integrated into evaluation metrics and says post-deployment monitoring should include mechanisms for input from users and other relevant actors, incident response, recovery, change management, and sharing information about errors, near-misses, and attack patterns.

The archive should therefore generalise vulnerability disclosure into **public AI disclosure**: not only cyber flaws, but also harms in safety, rights, bias, explanation, and misuse resistance.

## Pattern pack

### 1. Publish one reporting path that outsiders can actually find

Every consequential public AI system should have a clearly published reporting path for:

- security findings,
- privacy or data leakage issues,
- harmful outputs,
- discriminatory or inconsistent outcomes,
- explanation or notice failures,
- misuse or gaming of the system,
- unsafe deployment behavior.

The contact path should appear in public records, service notices, and oversight materials rather than being buried in a generic webform.

### 2. Grant safe harbor for good-faith reporting

The policy should state that the institution welcomes good-faith reporting and explain:

- permitted research behavior,
- systems or environments in scope,
- prohibited destructive actions,
- expectations around data handling,
- non-retaliation or safe-harbor terms for authorized good-faith activity,
- how affected individuals and advocates may report non-technical harms.

Without safe harbor, many serious problems stay private until after harm compounds.

### 3. Accept sociotechnical harms, not only classic vulnerabilities

A public AI disclosure channel should not pretend that all important failures look like CVEs. Reports should be triaged even when they concern:

- discriminatory patterns,
- inaccessible interfaces,
- unsafe escalation logic,
- explanation that is misleading or false,
- broken appeal routes,
- model behavior that encourages harmful action,
- feedback loops that intensify exclusion.

The institution can separate workflows internally while still offering one legible path from the outside.

### 4. Put reports on clocks with severity and ownership

Reports should move through a visible handling workflow:

- acknowledgement,
- triage,
- severity assignment,
- evidence preservation,
- responsible owner assignment,
- mitigation or containment,
- closure or longer-term remediation.

Not every case belongs on a public incident page, but every serious case should be owned, timed, and reviewable.

### 5. Link external reports to incident command and monitoring

A disclosure channel is not a side mailbox. It should feed the same governance machinery used for:

- incident command,
- production monitoring,
- drift tracking,
- complaints and appeals telemetry,
- post-incident review,
- reapproval and rollback decisions.

This is how “someone emailed a concern” becomes operational evidence rather than folklore.

### 6. Preserve evidence and communicate with the reporter

Teams should preserve relevant logs, prompts, outputs, model/version information, and workflow traces once a credible report arrives. Reporters should receive enough feedback to know:

- the report was received,
- whether it was understood,
- whether it is in scope,
- whether mitigation has begun,
- whether further information is needed.

Silence teaches the public not to report.

### 7. Share fixes and recurrent lessons across similar systems

When a report reveals a meaningful pattern, the institution should push the lesson outward:

- refresh transparency records,
- update training and runbooks,
- strengthen tests or filters,
- share relevant near-miss patterns across peer systems,
- revise procurement or supplier requirements where the issue originated upstream.

A disclosure program matures when it turns individual reports into class-wide hardening.

## Guardrails

- Do not force outsiders to guess the right inbox.
- Do not punish affected users or researchers for good-faith reporting that follows stated boundaries.
- Separate lawful safe-harbor from permission for harmful or destructive testing.
- Preserve evidence before remediation overwrites the trace.
- Use one intake path even if internal teams later split cases by type.

## Failure modes

- **mailbox theater**: a reporting address exists but no one owns triage or response.
- **cyber-only blindness**: the institution ignores rights, bias, or explanation failures because they are not classic security bugs.
- **retaliation chill**: reporters fear legal, contractual, or reputational punishment for good-faith disclosure.
- **orphan report**: a serious report never reaches incident command or change control.
- **silent fix**: the issue is patched locally but no record, lesson, or public refresh follows.

## Practical tests

A disclosure regime passes when it can answer yes to all of the following:

1. Can outsiders easily find one reporting path for public AI harms and vulnerabilities?
2. Does the policy explain safe-harbor terms for good-faith reporting?
3. Can the intake process handle both cyber and sociotechnical harms?
4. Are serious reports placed on explicit clocks with named owners and preserved evidence?
5. Do validated reports feed incident handling, monitoring, and record refresh rather than dying in email?

## Compression rule for the archive

If outsiders can see a serious failure but cannot safely report it into a governed response path, the system is still operating without a real **public early-warning channel**.
