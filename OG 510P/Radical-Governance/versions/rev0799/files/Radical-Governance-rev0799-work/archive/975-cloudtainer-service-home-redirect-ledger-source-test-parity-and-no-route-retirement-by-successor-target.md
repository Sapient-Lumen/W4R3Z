# 975 — Cloudtainer service-home redirect ledger, source/test parity, and no route retirement by successor target

## One-line thesis

A successor route is not a retirement: note `615` can move toward absorption only when each protected service-home element has a redirect row into note `974`, a generated service-home test, source keys, and an applied example, while any unmapped behavior keeps the old route active.

## Why this matters

Rev0776 did the right next thing: it created note `974` as the generic successor route for shared territorial service homes. But that was still not enough. A successor route can become a new kind of theater if it lets the archive say “absorbed” merely because a better note exists.

The risky unfinished work was therefore the redirect ledger. Note `615` carries generic service-home grammar: service maps, operator chains, complaint handoffs, continuity duties, and the upgrade trigger from loose cooperation into real service government. Those elements must not disappear into a broad successor note unless the archive can show exactly where they went.

This revision adds that mapping. It still does not retire note `615`.

## Pattern pack

### 1. Treat successor creation as a beginning, not an end

A successor route can collect stronger doctrine, but it does not prove absorption by existing. The archive should ask four questions before lowering an older route’s status:

- Which protected element is being moved?
- Which section of the successor route carries it?
- Which generated test keeps it executable?
- Which source keys and applied examples prove that the element survives outside prose?

If any answer is missing, the older route remains active.

### 2. Redirect each protected element, not the note title

The redirect unit is a protected behavior, not a title similarity. For note `615`, the ledger maps six protected elements:

- generic role split among authority, operator, regulator, commissioner, contractor, and local entry points;
- territorial service map;
- continuity, substitution, reserve-capacity, and failure-takeover tests;
- near-to-person entry and complaint handoff;
- operator-chain public service constitution; and
- the upgrade trigger from cooperation to real service government.

A route is not absorbed until those behaviors are live in the successor route and generated tests.

### 3. Require source parity by claim strength

Source parity is not a list of URLs. The ledger has to say why each source key is enough for the redirected element and where it is weak.

A governance page can support authority existence, not delivered service. A complaint page can support escalation-path existence, not remedy success. A business plan can support planning posture, not water continuity. A metropolitan-governance report can support cross-sector concept, not local implementation.

The redirect ledger therefore records source keys as route supports, not outcome proof.

### 4. Require generated test parity before retirement pressure

`SERVICE_HOME_TESTS` now exists and note `974` uses it, but retirement pressure should remain blocked unless each protected element maps to one or more test IDs. The test matrix makes the successor route executable; the redirect ledger makes the older route traceable.

The two have different jobs:

- test parity checks whether a new packet can pass service-home tests;
- redirect parity checks whether an older route’s protected elements survived;
- source parity checks whether the successor claims have bounded evidence.

### 5. Keep applied examples plural

London transport is a strong applied example, but it is still transport. Note `615` is broader. The redirect ledger therefore points to London transport for a mature functional authority and to utility, intermunicipal, metropolitan-governance, local-self-government, and basic-service sources for cross-sector stress.

The purpose is not to overclaim those sources. The purpose is to keep the service-home route from collapsing into one attractive case.

### 6. Use the ledger to reduce route mass slowly

A redirect ledger changes the work queue. It lets future revisions stop asking whether note `615` overlaps note `974` and start asking what remains unabsorbed.

The honest next states are:

- `redirect_mapped_keep_active` when protected elements are mapped but the old note remains useful;
- `redirect_mapped_needs_reader_redirect` when note status cannot change until reader routes and generated surfaces make the redirect visible;
- `absorption_ready_but_not_deleted` when tests, source keys, examples, and redirects all pass but a human still needs to check narrative loss;
- `retired_with_redirect` only when the old file is preserved or redirected without breaking lineage.

Rev0777 only reaches the first state.

### 7. Block retirement by target existence

The anti-pattern is simple: “We have a new route, so the old route can go.” That is not governance. It is cleanup theater.

The archive should reject route retirement whenever the merge packet lacks:

- source file and successor file;
- protected-element rows;
- successor section references;
- generated test references;
- source-key support;
- applied examples;
- reader-facing redirect instructions; and
- a preservation finding explaining what still cannot be retired.

## Audit/refactor shipped

This revision adds a machine-readable redirect ledger for `MP-003-615-to-974` and generated `ROUTE_REDIRECT_LEDGER.*` surfaces. The ledger maps all six protected service-home elements from note `615` into note `974`, `SERVICE_HOME_TESTS`, source keys, and applied examples.

The route-merge packet for note `615` now records the ledger and keeps status at `redirect_ledger_created_not_deletion_ready`. Lint validates that the ledger file exists, that each redirect row has test IDs, source keys, applied examples, and successor sections, and that packet claims line up with real notes and generated surfaces.

## Failure modes blocked

- No route retirement by successor route.
- No absorption by title overlap.
- No service-home parity by one London transport case.
- No source parity by untyped URL list.
- No generated test parity without protected-element redirect rows.
- No cleanup by deleting the awkward older route before proving what survived.

## Next move

The next meaningful step is a reader-facing redirect patch: add visible references from note `615`, note `974`, generated retirement surfaces, and service-home tests so maintainers can navigate from the old route to the successor route without depending on hidden metadata. Only after that should note `615` move toward a lower active status.

## Governing rule

**No route retirement by successor target.**
