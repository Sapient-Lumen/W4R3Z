# Release readiness and bundle-integrity checks

## What this note is for

This archive already has rules for what earns bytes, which note governs, how revisions identify themselves, and when older notes stop being live.
This note is the shorter final gate: do not ship a bundle whose front door, receipt, and machine surfaces disagree.

Use this note with [`archive-policy.md`](archive-policy.md), [`archive-growth-budgets-and-refactor-triggers.md`](archive-growth-budgets-and-refactor-triggers.md), [`revision-chronology-and-bundle-naming-discipline.md`](revision-chronology-and-bundle-naming-discipline.md), and [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md).

## Release-gate rule

A revision is not release-ready merely because the changed note is written.
It is release-ready only when the archive's content, route surfaces, and machine-readable metadata agree closely enough that a later reader or tool does not have to guess which revision it is holding or which path governs.

## Hard-failure checks

Before writing the bundle, the archive should be able to answer **yes** to all of these.

### 1. Revision identity agrees everywhere

`VERSION`, `README.md`, `ARCHIVE_INDEX.json`, `REVISION-RECEIPT.json`, `CHANGELOG.md`, and the zip name should all identify the same live revision.
`START_HERE.md` and `ARCHIVE_INDEX.md` may stay generic, but if they mention bundle identity they must not contradict the current release.
Stale revision labels in the machine index, retained-ledger end marker, README revision block, or latest changelog entry are hard failures.

### 2. The front door and machine routing agree

`README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `ARCHIVE_INDEX.json` should not point readers down materially different canonical paths.
`entry_surfaces.human_default` and `entry_surfaces.human_sequence` should match the declared human role split, and `entry_surfaces.machine_sequence` should match any prose sentence that narrates post-`ARCHIVE_INDEX.json` fallback order.
Once `ARCHIVE_INDEX.json` is explicitly treated as the machine surface, do not quietly leave it embedded inside the human fallback order.
Once the archive has made the human/machine entry split explicit, the machine file catalog should mirror that split too: do not flatten the human entry notes and `ARCHIVE_INDEX.json` back into one generic entry status when the routing surfaces already treat them differently.
If the top-level file catalog is being used as a quick-scan entry map, its human entry notes should usually appear in the same order as `entry_surfaces.human_sequence` rather than a conflicting local order unless the catalog says plainly that it is sorted differently.
If `ARCHIVE_INDEX.md` offers named route summaries, they should either cover every currently named route or say plainly which names are intentionally omitted.
If `START_HERE.md` narrates the archive's top-level human role split, it should not silently omit `README.md` once `README.md` is a declared human entry surface.

### 3. Compact route surfaces are explicit and truthful

If the archive treats compact routes such as `direct_answer`, `implementation_core`, `prevention_response`, or `certification_core` as front-door-significant, their labels, ordered files, and route-choice cues should be explicit enough that later readers and tools do not have to reconstruct them from prose.
Human surfaces may summarize, but they should say so; machine surfaces should not regress into ref-only shells unless that choice is explicit.
If `README.md` or `START_HERE.md` renders compact preferred routes, it should usually use the live route labels directly and avoid making one route self-contained while another remains inferential. If the front door has already made compact certification language significant through pass bundles, verdict strips, or proof-debt caps, it should not leave the shortest measurement-and-verdict continuation route implicit once the archive has chosen to expose other compact continuations by name.
If top-level navigation surfaces render live named routes, the file catalog in `ARCHIVE_INDEX.json` should usually carry matching `route_refs` for those files so later tools do not have to infer route-bearing front-door notes from prose alone. The same goes for authoritative machine route-map surfaces: if a file directly carries the live route arrays, it should not appear locally route-unlinked in the catalog.

### 4. Measurement and answer surfaces do not hide settled qualifiers

If the front door states the target tuple or headline wealth shares, it should not silently drop settled measurement qualifiers that already matter doctrinally.
For this archive that means the tuple remains a map of **private wealth shares**, **public/social wealth** remains a separate required co-condition, and default comparison remains **household-based private net wealth shares** filtered through the archive's **person-level title, control, and exit screen**. If the front door states the headline tuple, it should also keep the archive's simultaneous pass-bundle warning close by so later readers do not mistake the tuple for a self-sufficient certification rule. If the front door compresses certification into a short answer, it should also keep the archive's settled anti-averaging qualifier that **aggregate improvement or a good national tuple does not override systematic excluded-group failure** on floor, foothold, title, control, or exit surfaces. If the front door compresses certification or a compact verdict strip, it should also keep the archive's settled bottleneck qualifier that **the verdict follows the weakest still-live decisive surface rather than an average across lanes**. If the front door compares nearby cases or nearby acceptable envelopes, it should also keep the archive's settled anti-numerology qualifier that **raw distance from `20 / 50 / 20 / 10` is at most a late tie-breaker after the constitutional screens rather than a freestanding justice score**. If the front door compresses near-ideal certification into a short answer or verdict strip, it should also keep the archive's settled durability qualifier that **near-ideal names a durable order backed by some real ratchet against reversal rather than a one-cycle snapshot or a survived window alone**. If the front door says the lower half has a real floor, it should also keep the archive's settled claimability qualifier that nominal legal generosity, weak take-up, slow claiming, churn-heavy renewal, or expert-dependent operability do **not** count as a real floor pass. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled present-accessibility qualifier that **future-only, hardship-gated, narrow-purpose, or sale-contingent claims do not count like present independence**. And if the front door says a floor is claimable or keepable in ordinary life, it should also keep the archive's settled protected-foothold qualifier that **basic support should not require near-assetlessness, forced liquidation of modest reserves, or spend-down of first footholds before help starts or continues**. And if the front door says a floor is claimable or keepable in ordinary life, it should also keep the archive's settled smooth-withdrawal qualifier that **modest earnings, hours, or savings gains should not trigger abrupt loss, delay, or heavy dilution of essential support instead of smooth tapers, grace periods, or partial disregards**. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled shock-survivability qualifier that short income loss, mild rate resets, modest local price corrections, or predictable repair or care expenses should not be able to wipe the apparent gain out again on ordinary timescales. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled net-holdability qualifier that recurring carrying costs, mandatory charges, upkeep burdens, or fee drag should not quietly eat the gain away even without a fresh shock. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled forced-self-insurance qualifier that unusually large private defensive buffers needed merely to survive predictable illness, care, housing, earnings interruption, or old-age risks count less like freedom and more like compensation for a weak or late common floor. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled anti-maze qualifier that ordinary holders should not need unusual legal, tax, or financial fluency, opaque option-decoding, or paid professional rescue just to preserve most of the claim's value. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled cheap-proof qualifier that ordinary holders should be able to retrieve and update the records, certificates, beneficiary entries, co-title evidence, or similar proof they need without repeated brokerage, long-distance travel, specialist help, or prohibitive fees when ordinary dispute or life change demands it. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled timely-remedy qualifier that ordinary disputes, clerical errors, status changes, or provider changes should not be able to interrupt practical control for so long that a formally available review or appeal arrives too late to preserve ordinary continuity. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled anti-reprisal qualifier that ordinary use, complaint, appeal, organizing, separation, or exit should not itself predictably trigger firing, eviction, benefit suspension, account lockout, household retaliation, blacklisting, or similar punishment before neutral protection can hold. And if the front door says a floor or foothold is real, usable, or keepable in ordinary life, it should also keep the archive's settled anti-seizure qualifier that modest reserves, essential-use assets, and first long-run claims should be protected enough to survive the first ordinary debt conflict rather than being easy to sweep, garnish, offset, intercept, or force-sell away, and that debt repair should still leave a meaningful restart minimum. And if the front door says footholds are person-level, portable, or keepable in ordinary life, it should also keep the archive's settled low-gatekeeper qualifier that ordinary exit, switching, separation, or movement should not let one employer, provider, household intermediary, or sponsor materially freeze, stall, or condition the claim. And if the front door says footholds are person-level or portable across ordinary life, it should also keep the archive's settled non-forfeiture qualifier that ordinary job, provider, place, or household change should not restart vesting clocks, strand records, wipe prior matches, force destructive liquidation, or impose large transition penalties just to preserve what is already supposed to belong to the holder. And if the front door says footholds are early, portable, or real in ordinary life, it should also keep the archive's settled territorial-access qualifier that cheap footholds in weak-opportunity places, or footholds that require punishing travel times, high transport costs, or brittle commuting chains to reach the main labor, education, care, or public-service nodes, do **not** count like secure access to the main compounding places. And if the front door says footholds are early, open, or portable across ordinary life, it should also keep the archive's settled anti-family-threshold qualifier that **ordinary early-adult entry should not still depend on parental deposits, guarantees, inherited housing position, or comparable family backing at the threshold moment**. And if the front door says public/common wealth is a real counterweight, it should also keep the archive's settled anti-patronage qualifier that broad access, continuity, and governance should be rule-bound enough that public/common provision does **not** become a substitute oligarchy routed through patrons, brokers, or local discretion. And if the front door says footholds or counterweights are broad, person-meaningful, or democratically governed, it should also keep the archive's settled anti-stewardship qualifier that apparently broad pooled or intermediated claims do **not** count fully when voting, stewardship, or practical control remains bottlenecked inside a narrow manager, trustee, or similar intermediary layer that ordinary holders cannot meaningfully inspect, direct, or replace. And it should also keep the archive's settled floor-coverage qualifier that the default reading is **supermajority plus cohort guardrails** rather than a bare-majority or flattering-average pass carried by older incumbents while younger adults or excluded groups lag badly behind. And if the front door says a floor or foothold is real, usable, or broad near the lower half, it should also keep the archive's settled per-person-adequacy qualifier that **one thin household foothold carrying too many adults or dependents does not count like several person-adequate footholds**, and that overcrowding, delayed independent exit, or claimant dilution should not be silently laundered into a broad floor pass. If the front door renders a compact verdict strip or status call, its **Near-ideal / acceptable** state should also keep that anti-averaging, bottleneck, durability, claimability, protected-foothold, smooth-withdrawal, present-accessibility, shock-survivability, net-holdability, forced-self-insurance, anti-maze, cheap-proof, timely-remedy, anti-reprisal, anti-seizure, low-gatekeeper, non-forfeiture, territorial-access, anti-family-threshold, anti-patronage, anti-stewardship, floor-coverage, and per-person-adequacy language explicit rather than silently reducing certification back to target-family-plus-pass-bundle language. And if the front door renders any sub-certification status such as **still failing**, **correction-required**, or **provisional near-pass**, it should also keep the archive's settled qualifier that the status travels with the **named live blocking surface or proof debt** rather than floating as generic improvement language. If the front door summarizes **prevention**, **correction**, or **anti-oligarchy response**, it should also keep the archive's settled qualifier that the constitutional target stays fixed across modes and posture choice mainly changes what has become non-deferrable.

### 5. The receipt truthfully describes the revision

`REVISION-RECEIPT.json` should name the real baseline, the live reopened bundle, the actual reason this revision exists, the files actually changed, and any anomaly or repair that matters for later trust.
Do not leave later readers to infer whether the bundle was self-read, whether the current bundle differs from the baseline, or why the revision was worth shipping.
A receipt that still describes an earlier plan is a release failure.

A receipt that still carries an earlier revision's codename, focus block, or why-now narrative is also a release failure.

### 6. The manifest pair is stable and honest

`MANIFEST.json` should inventory the released payload except the manifest pair itself.
`MANIFEST.sha256` should checksum the released non-self files and also checksum `MANIFEST.json`.
Do not let `MANIFEST.json` list itself, and do not let the payload carry undeclared bulky exports such as nested release zips.
If file times are normalized, the zip should not reintroduce a second competing chronology story through stray directory entries or stale internal timestamps.

### 7. The machine index is locally legible

`ARCHIVE_INDEX.json` should say locally what its route names mean, what shape the route map takes, what file-entry fields mean, what `route_refs` means, where entry surfaces live, where revision-memory surfaces live, what chronology order governs, where the compact front-door operator kit lives, and what syntax internal `*_ref` pointers use.
If later tools would need to reverse-engineer those basics from prose or distant notes, the machine index is still exporting guesswork.
Summary fields inside `ARCHIVE_INDEX.json` should describe the live structure briefly rather than accumulate revision-by-revision patch history once that history already lives in `CHANGELOG.md` and `REVISION-RECEIPT.json`.

### 8. CHANGELOG and receipt stay distinct

`REVISION-RECEIPT.json` is the full current-bundle receipt.
`CHANGELOG.md` is the thinner retained recent ledger.
If both surfaces start carrying the same current-state prose, the archive is wasting one of its few accumulating ledgers.
Once `ARCHIVE_INDEX.json` already carries authoritative retained-ledger scope, `CHANGELOG.md` should keep only a short human-readable scope preface or pointer rather than another long scope recap. If `CHANGELOG.md` carries that short scope preface, it should stay in top matter rather than drift into the live entry stream, and its retained-ledger end marker should not lag the authoritative `revision_memory_scope` end revision in `ARCHIVE_INDEX.json`. `revision_memory_scope.recent_revision_ledger_basis` and `revision_memory_scope_semantics` should each stay to one short structural sentence rather than regrowing into repair-by-repair prose once the same object already carries the live retained range, count, continuity, and inclusion flags. If that basis field says the retained ledger was extended through a named revision, that basis endpoint should not lag the same object's authoritative end revision once the current bundle has been added. If the retained ledger says it is contiguous across its declared range, it should not silently skip a revision number inside that range.

### 9. Front-door prose stays thin

`START_HERE.md` should usually carry the direct answer, the fastest human routes, and short pointers to authoritative routing surfaces.
`README.md` should usually stay the revision-aware release shell and top-level route map.
`ARCHIVE_INDEX.md` should usually stay the grouped human browsing surface and route-summary surface.
When authoritative machine surfaces already exist, prefer pointing to them over repeating long stable field families or full operator lists across multiple top-level notes.

## Recommended finishing order

A thin finishing order is usually enough:

1. finish the substantive file change,
2. update any affected route or front-door surfaces,
3. update `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `ARCHIVE_INDEX.json` if their role or routing truth changed,
4. write `REVISION-RECEIPT.json` and `CHANGELOG.md`,
5. set `VERSION`,
6. regenerate manifests,
7. run a local link / integrity check,
8. then write the zip.

This order is not sacred.
Its job is just to stop the archive from producing a clean new note inside a dirty release shell.

## No-silent-mismatch rule

If a revision knowingly ships with a remaining mismatch, the receipt should say so plainly.
A tight archive should carry its own warning labels when it is temporarily imperfect.

## Fast use rule

Use this note whenever a revision changes:

- top-level routing,
- machine-readable index structure,
- bundle identity,
- receipt structure,
- manifests,
- or any file the archive treats as part of its front door.

The archive should not need a forensic pass every time it writes a new bundle.
