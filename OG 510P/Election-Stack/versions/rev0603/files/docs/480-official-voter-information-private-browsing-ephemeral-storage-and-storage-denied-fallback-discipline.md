# 480 — Official voter-information private browsing, ephemeral storage, and storage-denied fallback discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose usability depends on browser-managed persistence or embedded state that may disappear, reset, or be blocked by privacy posture**:
public lookup/help pages that remember a selected jurisdiction, office, or election only in browser storage,
routes that expect cookies or local storage to preserve current step, current language, or current answer context,
embedded official widgets or vendor-hosted tools that rely on third-party cookies or unpartitioned state,
and similar public routes where the page can be current in principle yet still fail the voter because the browser will not keep or share the state the office assumed existed.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `406`, which governs same-URL request-context variance, personalization, and experiment boundaries,
- `409`, which governs public-read access, sign-in boundaries, and session-expiry recovery,
- `411`, which governs cookie/consent overlays and first-load answer-lane visibility,
- `414`, which governs embedded browsers, webviews, and constrained containers,
- `469`, which governs local-only saves, queued state, and office-acknowledged state truthfulness once something has actually been saved or queued,
- or `478`, which governs text assistance and composition posture before the route should treat an entered value as final.

It adds one narrow rule:
**if an official voter-information route depends on browser persistence or embedded cookie/state access, the office should keep the answer/help lane truthful when storage is ephemeral, denied, partitioned, or cleared; it should provide a bounded no-storage or credential-free fallback instead of a blank shell or reset loop; and it should not quietly confuse local convenience state with the current authoritative public answer.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, usability, accessibility, and accuracy. MDN’s current **Web Storage API** guidance says private/incognito browsing modes still expose the APIs but treat `localStorage` like `sessionStorage`, deleting stored data when the private tab or session ends. MDN’s current `localStorage` reference also says access can throw `SecurityError` when policy decisions prevent persistence and notes that browsers may interpret blocked cookies as an instruction to prevent the page from persisting data. MDN’s current **Storage quotas and eviction criteria** guidance adds that private-browsing modes can apply different quotas and usually delete stored data when the private session ends. And MDN’s current **Storage Access API** guidance makes the embedded case explicit: browsers commonly block third-party cookies and unpartitioned state by default, embedded resources may need explicit storage-access permission, and the first load may need to return a fallback version that works without those cookies before a later credentialed reload occurs. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `mdn_web_storage_api_page`; xref: `mdn_window_localstorage_property_page`; xref: `mdn_storage_quotas_and_eviction_criteria_page`; xref: `mdn_storage_access_api_page`)

That is enough to justify a compact control here.
A route may pass `406`, `409`, `411`, `414`, `469`, and `478` yet still fail the public because:
- a private-browsing tab silently drops the state the route expected to survive,
- a cookie-blocking or privacy setting turns storage writes into failures,
- an embedded official tool loads without the cookies or unpartitioned state it assumed would be present,
- the route loops back to an empty shell every time storage is cleared or denied,
- or the office treats “we remembered it locally once” as though that local memory were a durable or office-controlled public answer.

## This is not the same thing as request-context variance, login posture, or local-save truthfulness

`406` asks whether the same official URL changes meaning because of ambient request context such as cookies, geography, or experimentation.

`409` asks whether a public answer should have stayed anonymously readable instead of turning into a sign-in or expired-session shell.

`414` asks whether a constrained container or webview hides or breaks ordinary browser behavior.

`469` asks whether locally saved, queued, and office-acknowledged state are kept visibly separate **after** the route has something meaningful to save.

`480` asks a different question:
**even before any saved-vs-queued-vs-submitted story matters, does the route still tell the truth when the browser will not keep state, will keep it only temporarily, or will not share it with the embedded component the office relied on?**

A route may pass the earlier controls and still fail `480` if:
- the page is anonymously readable, but every meaningful choice resets because storage is unavailable,
- the embedded widget is inside the right official page, but its third-party state is blocked by default,
- the route labels something “saved” only because a local preference or selection once landed in storage that may disappear at tab close,
- or the office treats a no-cookie / no-storage first visit as too degraded to answer, even though it is often the exact first-contact condition a voter, crawler, or privacy-hardened browser will see.

## Private browsing can make persistence temporary even when APIs still exist

MDN’s current Web Storage guidance says private/incognito modes still provide the storage APIs, but `localStorage` is treated like `sessionStorage` and the stored data is deleted when the private tab or session ends. MDN’s current storage-quotas guidance separately says private-browsing modes may use different quotas and usually delete stored data when the private session ends. (xref: `mdn_web_storage_api_page`; xref: `mdn_storage_quotas_and_eviction_criteria_page`)

For this archive, that means the office should not quietly assume that “stored in the browser” means:
- durable across a browser restart,
- durable across closing the last private tab,
- equally sized across ordinary and privacy-hardened browsing,
- or proof that the office can recover the same state later.

This does **not** mean a route must forbid private browsing.
It means the route should remain honest about which conveniences are only local and temporary, and it should not make the current answer/help lane depend on persistence that privacy mode is designed to discard.

## Storage writes can fail or be denied; a public route should not collapse because of that

MDN’s current `localStorage` reference says storage access can throw `SecurityError` when policy decisions prevent persistence and notes that blocked cookies may be interpreted as an instruction to prevent the page from persisting data. (xref: `mdn_window_localstorage_property_page`)

That makes storage availability an explicit boundary, not a hidden implementation detail.
A public voter-information route should therefore review whether critical first-contact behavior still works when:
- local persistence is unavailable,
- the browser rejects a storage write,
- a persistence read returns empty because prior data was cleared,
- or the route is re-entered after privacy mode already erased the last local state.

What fails `480` is not merely “some preference did not stick.”
What fails `480` is when the route turns storage denial into:
- a blank shell,
- an unexplained reset loop,
- a silent drop back to the wrong jurisdiction or election,
- or a false implication that prior local state was somehow office-recorded.

## Embedded official tools need a credential-free fallback when third-party state is blocked

MDN’s current Storage Access API guidance says browsers commonly block third-party cookies and unpartitioned state by default in embedded contexts, that the API exists to let an embedded resource check or request access, and that an embed may first need to load a fallback version without cookies before later reloading a credentialed version after permission is activated. The same guidance also says the API is available only in secure contexts and that browser behavior differs. (xref: `mdn_storage_access_api_page`)

For election routes, that matters whenever an official page embeds:
- a vendor-hosted lookup tool,
- a shared sign-on or personalization component,
- a district/office finder loaded from another origin,
- or another answer-bearing frame that assumes cross-site cookie or state continuity.

This archive does **not** require every office to use the Storage Access API.
It does require the office not to act surprised when privacy posture blocks embedded state.
A bounded, safe public posture should therefore review whether the embed has:
- a legible no-cookie / no-credential fallback,
- a truthful explanation when extra permission is needed,
- and a first-party help or open-in-browser recovery lane if the embedded path cannot safely continue.

An official iframe that renders only an empty shell or infinite spinner until third-party state exists is not a minor product quirk here.
It is a public-answer integrity failure.

## Keep the no-storage / privacy-hardened path as a real public-answer lane

The office does not control whether a voter arrives with ordinary cookies, cleared storage, private browsing, tracker blocking, or stricter privacy settings.
So a compact public-service rule is:
- keep critical read-only answer/help routes workable without assuming durable client-side state,
- keep default selections and routing choices visible enough that the voter can reconstruct them after reset,
- prefer small visible recovery cues over silent storage dependence,
- and reserve storage-backed convenience for things that truly remain convenience rather than control.

A route may still use browser storage for:
- remembered language choice,
- office/jurisdiction convenience,
- non-sensitive draft convenience,
- or a recently viewed result shell.

But it should not quietly let those conveniences become the sole way to recover the current official answer when the browser is explicitly operating in a mode that is likely to discard them.

## Do not confuse local persistence with office-controlled truth

`469` already governs truthful labeling once a route has locally saved, queued, or office-acknowledged something meaningful.
`480` keeps a narrower but earlier boundary:
local persistence may help the route reopen in a familiar state, but local persistence is **not** proof that the office received, confirmed, or still controls that state.

For this archive, that means the route should avoid implying that:
- remembered jurisdiction = verified jurisdiction,
- remembered ballot-status lookup context = current office-known status,
- remembered language or district choice = governing official answer without re-check,
- or remembered embedded-session state = safe evidence that the same credentialed path will be available later.

The storage layer may remember context.
It must not silently mint authority.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **storage_dependent_routes_classified**
- **private_browsing_ephemerality_reviewed**
- **storage_denial_errors_handled**
- **no_storage_first_contact_lane_available**
- **embedded_third_party_state_dependencies_classified**
- **credential_free_embed_fallback_available**
- **storage_access_permission_path_reviewed**
- **local_convenience_not_treated_as_office_truth**
- **privacy_hardened_reentry_recovery_available**
- **storage_posture_review_current**

## Preserve bounded posture evidence, not individualized storage exhaust

What usually matters for accountability is small:
- which public routes depend on storage,
- whether private-browsing and storage-denial behavior were reviewed,
- whether embedded third-party state has a fallback path,
- whether the no-storage first-contact lane remains useful,
- and when that posture was last verified.

This archive does **not** need:
- raw cookies,
- individualized browser-storage dumps,
- per-user incognito histories,
- full local database exports,
- or invasive telemetry about every storage error merely to prove the route was reviewed.

Prefer bounded public evidence such as reviewed dependency classes, fallback classes, and last-verification timestamps.

## What to test

- Can a voter still reach the current answer/help lane when browser storage is empty, cleared, or unavailable?
- In private browsing, does the route stay honest about what will disappear at tab/session close?
- If a storage write fails, does the route recover visibly instead of dropping into an unexplained reset or blank shell?
- Are remembered selections and locally reopened states clearly subordinate to the current official source rather than treated as office-controlled truth?
- If an official embed relies on third-party cookies or unpartitioned state, is there a credential-free fallback or an explicit first-party recovery lane?
- When storage access permission is needed for an embed, does the page explain the extra step and remain useful before permission is granted?
- Does the route avoid turning privacy-hardened first contact into “you must turn off browser protections to continue” when a bounded public fallback exists?

## How this fits the family map

Private browsing, ephemeral storage, and storage-denied fallback is **not** a new underlying voter-question family bucket.
It is a delivery-layer boundary about whether the browser will preserve or share enough state for the already-modeled public-answer route to stay usable.

So the family question remains:
- `406` decides whether same-URL meaning silently varies by ambient context,
- `409` decides whether the route should have stayed publicly readable instead of requiring account state,
- `414` decides whether the containing browser shell itself is constrained,
- `469` decides what locally saved, queued, or office-acknowledged state labels mean,
- and the substantive voter-question family docs still decide the actual answer.

This document only says that, if the route relies on browser persistence or embedded shared state, the office should keep the no-storage / privacy-hardened path bounded, legible, recoverable, and clearly subordinate to the current official source rather than quietly assuming persistent state that the browser may never provide.

## Minimal companion artifacts

- Template payload: `artifacts/templates/official-voter-information-storage-availability-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-storage-availability-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- `eac_effective_design_for_the_administration_of_federal_elections_page`
- `mdn_web_storage_api_page`
- `mdn_window_localstorage_property_page`
- `mdn_storage_quotas_and_eviction_criteria_page`
- `mdn_storage_access_api_page`
