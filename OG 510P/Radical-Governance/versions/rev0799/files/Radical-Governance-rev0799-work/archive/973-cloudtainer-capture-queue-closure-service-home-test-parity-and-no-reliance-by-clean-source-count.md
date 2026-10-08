# 973 — Cloudtainer capture queue closure, service-home test parity, and no reliance by clean-source count

## One-line thesis

Closing the capture queue is not the same as making every source quote-ready or every route retirement-safe: the archive must keep limited-reliance rows visible, add service-home test parity before absorption, and treat clean-source counts as a maintenance signal rather than a proof of continuity.

## Why this matters

Rev0774 narrowed the source-health problem to seven hard rows. That was useful, but it left a subtle danger: a future maintainer could either keep the seven rows as an eternal red queue, or close them by calling them clean. Both moves would be wrong.

The better repair is to split three states that had been compressed together:

- **capture-required**, where the archive still lacks a usable page, PDF, blocked-route, or legal-text capture;
- **limited-reliance direct review**, where the official or primary route is identified well enough for route-level use, but not enough for unsourced quotation, legal reliance, or outcome proof;
- **clean direct review**, where the route is usable for its bounded publication, register, report, or law-text function but still does not prove lived continuity.

The second lane is the important one. It lets the archive stop treating a source as unresolved without pretending that it has become dispositive evidence.

## Pattern pack

### 1. Close capture only into a named reliance tier

The seven remaining rows are moved out of the capture-required queue only because their official or primary route has been identified, indexed, or bounded well enough for route-level use. They are not promoted to broad reliance.

The source-health ledger now uses a limited-reliance tier for these rows. That means:

- legal-text routes may support the existence and identity of the statutory route, but exact section-level claims still need authoritative text capture;
- official UN and BINUH Haiti routes may support a monitoring-route or event anchor, but operational claims still need dated report context and supersession checks;
- the LAHSA audit route may support the existence of the County Auditor review, but page-specific findings still require PDF/page capture before quote-level reliance.

### 2. Keep the service-home absorption work testable

The note-615 merge packet has been saying the same thing for several revisions: London transport is not enough to absorb the generic service-home doctrine. This revision turns that into generated test parity rather than another prose reminder.

`metadata/service_home_tests.json` and generated `SERVICE_HOME_TESTS.*` now define the reusable checks that a surviving service-home route must carry:

- service map;
- authority, operator, regulator, commissioner, and contractor split;
- lawful delivery instrument;
- near-to-person front door and complaint handoff;
- continuity, substitution, and failure-takeover duty;
- operator-chain disclosure;
- source-boundary and outcome proof;
- route-absorption parity.

This is not deletion authorization. It is the test scaffold required before deletion can even be discussed.

### 3. Separate clean source count from reliance readiness

A clean direct-review count is still only a count. It does not show that a dashboard is current tomorrow, a rule has not been amended, a compensation scheme paid, a legal person has functioning guardians, a flood plan worked, a homeless-service authority repaired contracts, or a Haiti security mission has capacity.

The generated source-health surface now reports limited-reliance rows separately so the archive cannot claim source cleanliness merely because the explicit capture queue is empty.

### 4. Retire routes only after source/test parity, not after queue closure

Capture closure helps the maintainer trust the source ledger. It does not absorb protected grammar. The service-home packet remains not deletion-ready until:

- a surviving generic route carries the protected tests;
- generated surfaces route those tests;
- source keys and case examples are linked; and
- the retirement packet records where each protected element moved.

## Audit/refactor shipped

Rev0775 changes the source-health builder so it reports a **limited-reliance direct-review lane** in addition to clean direct review and capture-required follow-up. The remaining seven rows are no longer listed as capture-required, but they remain visible as limited reliance.

Rev0775 also adds service-home test parity through the common test-matrix builder. This is a concrete absorption prerequisite for `MP-003-615-to-849`: the route now has generated tests, but note `615` remains active because no successor route has yet absorbed all protected elements.

## Failure modes blocked

- No evidence closure by clean-source count.
- No legal reliance by indexed statutory route.
- No fragile-jurisdiction capacity by UN press route.
- No homelessness-governance repair by audit PDF existence.
- No legal-personhood implementation by Act title.
- No route retirement by source-health closure.
- No service-home absorption without generated test parity.

## Next move

Use the limited-reliance queue to decide where exact page/PDF/legal-text capture is still worth doing, then work `MP-003-615-to-849` from test parity into a true successor route. The archive can now stop chasing a red counter and start asking which source limits actually block a claim or route retirement.

## Governing rule

**No reliance by clean-source count.**
