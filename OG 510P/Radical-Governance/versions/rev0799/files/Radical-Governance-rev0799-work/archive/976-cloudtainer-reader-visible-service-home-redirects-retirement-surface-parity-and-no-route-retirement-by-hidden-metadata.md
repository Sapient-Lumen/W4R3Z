# 976 — Cloudtainer reader-visible service-home redirects, retirement-surface parity, and no route retirement by hidden metadata

## One-line thesis

A protected-element redirect ledger only reduces route-retirement risk when ordinary readers can see it from the old route, the successor route, the generated retirement audit, and the generated redirect surface; otherwise the archive has merely moved deletion pressure into hidden metadata.

## Why this matters

Rev0777 created the right machine-readable protection for note `615`: every protected service-home element was mapped into note `974`, `SERVICE_HOME_TESTS`, source keys, and applied examples. But a metadata ledger can still fail at the point where the archive actually gets read. If note `615` still looks like a standalone current route, note `974` still talks as if the ledger is unfinished, and retirement surfaces only report counts, a future maintainer can miss the live redirect boundary.

That is the risky unfinished work. The archive should not be able to retire or downgrade a route because the metadata target exists, and it should not be able to preserve a route in name while hiding the successor path from readers. A real redirect patch has to change the route surfaces that people touch.

This revision therefore makes the note-`615` service-home redirect visible in the old note, the successor note, `ROUTE_REDIRECT_LEDGER`, `RETIREMENT_CANDIDATES`, and the release front doors. Note `615` remains active.

## Pattern pack

### 1. Put the redirect where the old route begins

A reader should not need to know that `metadata/route_redirect_ledger.json` exists. When an old route has a protected-element redirect ledger, the old route itself should show the redirect status near the top:

- successor route;
- generated redirect ledger;
- generated service-home tests;
- retirement status;
- and the limits on use.

For note `615`, the visible instruction is simple: use note `974` for new shared-territorial service-home packets, use the redirect ledger to trace protected elements, and keep `615` active for lineage until the archive records a later status change.

### 2. Put the redirect where the successor route claims inheritance

A successor note should not say only that it can receive older material. Once a redirect ledger exists, the successor should name the source note and the generated ledger. It should also say what the ledger does not prove: deletion, outcome continuity, or complete cross-sector absorption.

This blocks the failure mode where a strong successor route becomes a quiet deletion warrant.

### 3. Put the redirect in generated retirement surfaces

`RETIREMENT_CANDIDATES` should report more than a row count. For any merge-reviewed candidate with a redirect ledger, it should expose the reader-visible surfaces and the reader status. The row should tell a maintainer whether the redirect is hidden, visible, partial, or deletion-authorized.

In this archive posture, the deletion-authorized count stays zero.

### 4. Put the redirect in generated redirect surfaces

`ROUTE_REDIRECT_LEDGER` should be both machine-readable and reader-actionable. It should show where to go next, not just which element maps to which test. The generated Markdown should therefore list reader-visible routes: old note, successor note, current audit note, service-home tests, retirement audit, and generated redirect ledger.

### 5. Treat source parity as claim-bound, not route-clean

The service-home route uses official and institutional sources with different proof powers. TfL governance material supports statutory authority and decision structure, London TravelWatch supports unresolved complaint escalation, MWRA material supports authority powers and wholesale water/sewer service scope, and OECD material supports metropolitan-governance typology. None of those sources proves lived continuity by itself.

The redirect must keep those proof boundaries visible whenever it points from `615` to `974`.

### 6. Keep the status conservative

Reader visibility is not deletion readiness. It is a repair to route navigation. The honest state after this patch is:

`reader_redirect_visible_keep_active`.

That means the old route is easier to navigate, not retired.

## Audit/refactor shipped

This revision adds reader-visible redirect surfaces for `MP-003-615-to-974` and makes the builder/lint path enforce them. The route redirect ledger now records concrete reader surfaces, the redirect builder emits those surfaces in generated Markdown, the retirement audit exposes reader status and surface counts, and lint checks that any ledger claiming reader-visible status points to real files and real notes.

It also patches note `615` and note `974` directly, so the redirect is visible from both ends of the route.

## Failure modes blocked

- No route retirement by hidden metadata.
- No reader redirect by generated JSON only.
- No successor-route inheritance by implication.
- No retirement-surface parity by row count.
- No service-home source parity by unbounded source list.
- No deletion authorization by reader-visible redirect.

## Next move

Rev0779 performs the final note-`615` preservation review and does **not** authorize deletion. The next useful work is now either a cross-sector applied service-home packet outside the strongest transport/water examples, or a second absorption/redirect package for another merge candidate.

## Governing rule

**No route retirement by hidden metadata.**
