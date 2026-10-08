# 460 — Simulated evidence, live operational proof, and no promotion by proxy

## One-line thesis

Consequential public-AI governance should keep simulated, replayed, staged, shadow, and live evidence in explicitly separate lanes, and no cheaper lane should silently inherit the authority of live operational proof.

## Why this matters

Public-AI programs often produce many kinds of evidence that all look reassuring from a distance:

- benchmark scores,
- red-team results,
- tabletop drills,
- replay packets,
- staging-environment checks,
- shadow-mode runs,
- parallel comparisons,
- and live operational monitoring.

Those lanes are all useful. They are not interchangeable.

The archive already includes launch rehearsals, bounded beta, adversarial testing, and monitoring after deployment. What it still lacked was one explicit grammar saying that these are different proof lanes with different authority. Without that grammar, the institution starts laundering cheap evidence into stronger claims: a simulated drill becomes “operational readiness,” a shadow run becomes “production success,” a replay packet becomes “what the live system does,” and a staging restore becomes “service recovered.” The archive should therefore refuse promotion by proxy.

## Pattern pack

### 1. Classify evidence lanes before comparing results

At minimum, institutions should distinguish lanes such as:

- synthetic or simulated evaluation,
- replay or packet-based reconstruction,
- staging or preproduction validation,
- shadow or parallel observation,
- bounded live operation,
- and full live consequential use.

The point is not taxonomy for its own sake. The point is to keep one lane from silently impersonating another.

### 2. Require each lane to say what it can and cannot prove

Every lane should declare its proof boundary. For example:

- simulation may test logic, workflow, or edge-case handling,
- replay may test whether a preserved packet still supports later review,
- staging may test whether the assembled service starts and routes correctly,
- shadow mode may test comparison without live consequence,
- live operation proves behavior under real stakes, real users, and real environmental drift.

A lane that cannot prove live consequence should not be reported as if it did.

### 3. Keep predeployment and post-deployment evidence separate in public records

Assessment dossiers, status surfaces, review packets, and launch decisions should keep at least these distinctions visible:

- predeployment test results,
- deployment-like rehearsal results,
- post-deployment performance,
- and live incident or recovery evidence.

A green rehearsal should not overwrite a red live signal, and a later live improvement should not rewrite the historical limits of prelaunch evidence.

### 4. Block promotion by proxy

No team should be able to claim that a system is ready, recovered, fair, safe, or stable merely because a cheaper evidence lane looks good. Promotion to stronger claims should require evidence from the lane that actually bears the risk.

Typical examples:

- do not treat a sandbox success as proof of field readiness,
- do not treat shadow-mode agreement as proof of operator uptake,
- do not treat replay success as proof that the runtime service is healthy now,
- do not treat restored staging checks as proof that the live public surface is current.

### 5. Preserve lane labels in dashboards, queues, and release records

Metrics should carry lane identity instead of collapsing into one generic confidence score. Reviewers should be able to tell whether a number came from:

- lab evaluation,
- controlled rehearsal,
- live monitoring,
- incident recovery validation,
- or human appeal and override evidence.

If lane identity disappears during reporting, overclaim becomes the default.

### 6. Refresh lane authority after recovery, migration, or major environment change

A system that passed one lane yesterday may drop back to a weaker lane today after:

- infrastructure migration,
- recovery from damaged state,
- restoration from backups,
- substantial model or policy change,
- dependency substitution,
- or operator workflow change.

The archive should record when proof has moved from live back to staging, replay, or bounded operation.

### 7. Route weak proof to the next honest action

When only a weaker lane is available, the system should say what comes next:

- rehearse under deployment-like conditions,
- run a bounded live check,
- gather post-deployment monitoring,
- preserve a replay packet for dispute review,
- or pause stronger claims until live proof exists.

The next honest action is part of the governance surface.

## Guardrails

- Do not let a simulated or replayed result inherit live-operational authority by rhetoric.
- Do not collapse predeployment and post-deployment evidence into one status color.
- Do not report staging or recovery validation as if it proved current public-service performance.
- Do not hide lane identity inside internal tooling while publishing only blended outcomes.
- Do not promote a system to stronger claims without evidence from the lane that actually carries the civic risk.

## Failure modes

- **benchmark laundering**: lab metrics are presented as proof of live suitability.
- **shadow-mode overclaim**: comparison runs are mistaken for real operational readiness.
- **replay masquerade**: reconstructed packets are reported as runtime truth.
- **recovery theater**: a restored environment is called healthy before live proof exists.
- **lane collapse**: multiple evidence channels are blended into one status that cannot be challenged.

## Practical tests

A lane-honest evidence regime passes when it can answer yes to all of the following:

1. Are simulated, replayed, staged, shadow, bounded-live, and live-consequential evidence lanes explicitly distinguished?
2. Does each lane state what it can and cannot prove?
3. Are predeployment and post-deployment results kept separate in review and disclosure records?
4. Is promotion to stronger claims blocked unless the corresponding proof lane exists?
5. After recovery or material change, can the archive show whether the system has fallen back to a weaker proof lane?

## Compression rule for the archive

If an institution cannot say **which lane produced this reassurance and what that lane is actually allowed to prove**, then it is still letting **cheap evidence impersonate live truth**.
