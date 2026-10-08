# 490 — Official voter-information browser-managed reading lists, offline saved pages, and web-archive authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that voters may keep as browser-managed saved copies instead of revisiting only through the live current page**:
Reading List items that can be reopened offline,
“save page as” files,
web-archive captures,
and similar browser-managed or browser-exported page copies that preserve enough of the current page to be reopened later while the live official route may already have changed.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `368`, which governs print-first or downloadable official artifacts the office intentionally publishes as portable materials,
- `404`, which governs stale cache, service-worker updates, and rollback on the live current route,
- `438`, which governs whether the current official URL itself is safe to bookmark, copy, or forward,
- `467`, which governs mutable live pages versus explicit citation heads,
- `471`, which governs office-offered copy/share controls,
- `472`, which governs installable web apps and standalone app-shell identity,
- `489`, which governs browser page-audio narration while the official page is still being consumed as a live page,
- and `497`, which governs platform-managed Watch Later, saved-playlist, and offline-download surfaces for already-open official recordings rather than browser-kept page copies.

It adds one narrow rule:
**if an official voter-information page may realistically be reopened from a browser-managed saved copy, offline reading list item, or archived page file, the page should keep currentness, scope, and recovery cues visible enough inside the captured page that the saved copy does not quietly masquerade as the current live official answer after time passes.**

## Why this is a distinct surface

The EAC’s current election-design guidance treats online voter-information materials as core public communications whose clarity, usefulness, and accessibility matter operationally. Digital.gov’s current digital-first public-experience requirements likewise treat authoritative and understandable public digital delivery as a service responsibility rather than a cosmetic preference. Apple’s current Safari guidance says Reading List items can be saved for offline reading and that Safari can also save an entire webpage as a **Web Archive**. Chrome’s current desktop help says users can add a page to Reading List and can save a page to read offline by using **Save page as...**. Mozilla’s current Firefox support guidance says users can save a web page to the computer for offline access, including complete-page, HTML-only, or text-file variants. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `apple_support_safari_keep_reading_list_mac_page`; xref: `apple_support_safari_save_webpage_mac_page`; xref: `google_chrome_read_pages_later_offline_computer_page`; xref: `mozilla_support_how_to_save_web_page_page`)

That is enough to justify a compact control here.
A route may pass bookmark, cache, install-shell, and print-material review yet still fail first contact because:
- the voter reopens a browser-saved copy that still looks official but no longer reflects the current election or current deadline state,
- the page carried too little freshness/help context inside the saved copy, so the reopened copy reads like the live current page,
- the route assumed a browser-managed offline copy would magically pick up corrections that only exist on the live page,
- a saved copy preserves only part of the route’s dynamic behavior or linked assets and now presents a partial shell with no explicit recovery lane,
- or the office never distinguished “browser kept a copy of what you saw” from “the office intentionally published a portable current artifact.”

## This is not the same thing as bookmarks, caches, installed shells, or office-issued portable artifacts

`438` asks whether the **URL itself** is safe to keep, copy, or forward.

`404` asks whether the **live route** is replaying stale content from browser, CDN, or service-worker caches.

`472` asks whether an installed web-app shell stays subordinate and recognizable when relaunched from the device.

`368` asks whether the office’s intentionally published portable artifacts stay editioned and linked back to the current route.

`490` asks a different question:
**once the browser has kept or exported a copy of the already-open page, does that saved copy still carry enough currentness, scope, and recovery context that the voter can tell it is a kept page copy rather than the guaranteed current live official answer?**

A route may pass those neighboring controls and still fail `490` if:
- the bookmark URL is fine, but the voter reopens yesterday’s saved page file instead of the live route,
- the live cache is current, but the browser-managed offline Reading List item is old,
- the office published no print handout, yet a user-created browser archive now circulates like one,
- or the installed web app is well-behaved while a separately saved page copy still misleads about currentness.

## Browser-managed saved copies are captured states, not self-updating authorities

The important fact here is not generic “offline exists.”
It is that major browsers let users **capture and reopen** page material from the already-open official route.
That creates a public surface where the same official-looking content may later be encountered as:
- the live current page,
- a browser-managed offline Reading List copy,
- a locally saved page file,
- or a browser-specific archive format.

For this archive, that means the office should not quietly rely on the browser to communicate the difference.
The captured page itself should carry enough visible cues that the voter can recover:
- which office or jurisdiction the page belongs to,
- what election/date or scope qualifiers mattered when the copy was captured,
- whether the page should be rechecked because the answer is time-sensitive,
- and which current official help route or live page should be consulted when the saved copy may be stale.

## Saved copies do not guarantee live correction, live assets, or full route behavior

Apple’s current Safari guidance says Reading List items can be saved offline and that a webpage can be saved as a Web Archive. Chrome’s current help says a saved page opens as a file on the user’s computer. Firefox’s current guidance says a saved web page may be stored as a complete page with associated files, HTML only, or text only. Those facts matter because a reopened page copy is not the same thing as a live current route with guaranteed network access, current linked assets, or full dynamic behavior. (xref: `apple_support_safari_keep_reading_list_mac_page`; xref: `apple_support_safari_save_webpage_mac_page`; xref: `google_chrome_read_pages_later_offline_computer_page`; xref: `mozilla_support_how_to_save_web_page_page`)

For `490`, the public-safe posture is:
- the current authoritative answer still lives on the live official page/help lane,
- the saved copy is a convenience memory aid or local snapshot rather than a self-refreshing authority,
- if the page is time-sensitive, the saved copy should say so plainly inside the page content itself,
- and if a saved copy loses scripts, assets, or interactive behavior, the route should still fail open toward the current official help lane instead of leaving a generic dead shell.

## Currentness cues need to survive inside the captured page

A saved page copy often drops the surrounding live context that would otherwise help the voter notice staleness.
The browser might reopen the file in a different window, with reduced navigation context, or while the network is absent.
So freshness and recovery cannot live only in ephemeral chrome, transient banners, or assumptions that the user can simply reload.

For this archive, the captured page should keep enough in-page cues that a later reader can still see:
- when this answer was last reviewed or updated,
- whether the answer is safe only for a named election or date window,
- whether the page is a convenience copy rather than the current official confirmation,
- and where to go for the current official page/help lane before acting on a deadline, place, eligibility, ID, cure, or rights-sensitive question.

This does **not** require pages to become giant warning labels.
It requires time-sensitive pages to remain truthful when separated from the live site around them.

## High-risk topics should bias toward “recheck the live route”

Some voter questions are especially unsafe to answer from a saved copy alone.
Examples include:
- polling-place, drop-box, early-voting, or satellite-office locations and hours,
- registration status, cure status, or ballot tracking,
- deadline and receipt-rule pages,
- emergency updates, facility-specific instructions, or weather/disaster contingencies,
- and any route where the page should really move the voter into `305` ordinary office/help recovery.

For those topics, `490` does not require perfect offline authority.
It requires a visible **recheck-the-current-route** posture so a saved copy does not pretend it settled a volatile question by itself.

## The saved copy is not the office’s reviewed portable edition unless the office says it is

A browser-managed saved page can look durable and official simply because it reopens cleanly later.
That alone does **not** make it the office’s reviewed portable edition.
The office may separately publish a downloadable PDF, handout, postcard, or formal notice governed by `368`.
A user-created Reading List item, offline file, or Web Archive should stay visibly subordinate to that distinction.

The safe rule is:
- browser-kept copies are user-agent conveniences,
- office-issued portable artifacts are reviewed publication objects,
- and when the office wants the public to rely on a portable artifact, it should publish that artifact explicitly instead of letting accidental browser captures become the de facto edition.

## Evidence and privacy posture

The evidence posture here is small and policy-shaped.
Preserve:
- which current routes were reviewed for browser-managed saved-copy behavior,
- which saved-copy contexts were considered,
- what currentness/recovery/help cues were expected to survive inside the captured page,
- and the last review time.

Do **not** preserve by default:
- individualized Reading List contents,
- local file paths,
- personal browser histories,
- uploaded user-created saved-page artifacts,
- or large browser-specific archive files merely to prove the surface was reviewed.

## Claims this control should support

1. **Saved-copy boundary claim:** browser-managed saved copies are treated as convenience snapshots rather than silently promoted into current official authority.
2. **In-page freshness claim:** time-sensitive pages keep enough freshness/scope cues inside the page that a later reopened copy remains visibly bounded.
3. **Recovery claim:** saved copies preserve or point back to an ordinary current official help/live-route recovery path.
4. **Portable-edition distinction claim:** user-created browser captures stay distinct from office-issued portable artifacts the office actually publishes and versions.
5. **Degraded-copy claim:** if scripts, assets, or dynamic behavior do not survive capture, the reopened copy fails open toward current official help rather than pretending completeness.

## How this fits the family map

Use `490` when the right official page is already open, but the browser may later reopen that page from a Reading List item, offline saved file, or archived page copy that still looks official.

Use nearby controls when the problem is instead:
- whether the URL itself can be safely bookmarked, copied, or forwarded (`438`),
- whether live browser/CDN/service-worker caches are replaying stale answers (`404`),
- whether the office intentionally published a portable print/download artifact (`368`),
- whether the site is relaunched as an installed app-like shell (`472`),
- or whether the page is being transformed in-place through summary, translation, OCR, or narration while still consumed as a live page (`486`–`489`).

## Minimal operator artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-browser-saved-copy-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-browser-saved-copy-surface-checklist.md`
