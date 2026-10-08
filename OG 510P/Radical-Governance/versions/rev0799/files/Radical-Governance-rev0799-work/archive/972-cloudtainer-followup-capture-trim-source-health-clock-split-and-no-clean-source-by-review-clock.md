# 972 — Cloudtainer follow-up capture trim, source-health clock split, and no clean source by review clock

## One-line thesis

A source row can need a future review without needing capture repair: the archive must separate ordinary volatility clocks from blocked-page, PDF, sparse-route, search-index, and legal-text capture failures before it decides what risk remains.

## Why this matters

Rev0773 correctly closed the catalog-triage queue, but its first follow-up capture count was still too broad. The builder treated any `followup` token as a capture problem, so stable rows with an ordinary implementation or order clock could appear in the same queue as sources that still lacked page-level capture. That inflated the apparent danger in some places and made the real danger less visible.

The highest-risk maintenance task is therefore not another domain docket. It is a sharper boundary between:

- **review-clock risk**, where the source is captured but may be superseded or require periodic recheck;
- **capture risk**, where the route is blocked, sparse, search-index-only, PDF-level, or legally complex enough that it cannot support quote-level reliance yet;
- **outcome risk**, where a clean source still proves only publication, authorization, register posture, or guidance—not lived continuity.

## Pattern pack

### 1. A review clock is not a capture warning

A report can be stable and still have a future implementation clock. A watchlist can be captured and still need periodic recheck. A procurement memo can be opened and still require later supersession review. Those are real risks, but they are not the same as missing capture.

The generated source-health builder now reserves the follow-up capture queue for explicit capture-needed signals: blocked route, page-level capture required, search-only capture, PDF/search capture, or `direct_refresh_attempted_needs_followup_capture` status.

### 2. Close capture rows only when the evidence boundary is recorded

Rev0774 moved a large set of sources out of capture-required posture because the official or primary route was opened, the PDF/text route was captured, or the exact record route was resolved. The closure is still claim-limited:

- MWRA business-plan and board-document routes can prove publication and board-route availability, not affordability, capital delivery, or complaint repair.
- OMB AI acquisition and LLM transparency memoranda can prove federal governance direction, not procurement compliance or model-level safety.
- FATF increased-monitoring material can prove a time-bounded soft-law posture, not future list status or actual bank behavior.
- NAO and Ombudsman reports can prove audit findings and historical failure patterns, not current claimant-level outcomes.
- Detroit FRC material can prove waiver/handback record posture, not durable local fiscal capacity.
- UN, OECD, Council of Europe, World Bank, UN-Habitat, OHCHR, ICO, LINZ, and ReliefWeb routes can anchor mandate/guidance/monitoring claims, not implementation.

### 3. Keep a small hard queue instead of a flattering clean slate

Seven rows remain in capture-required posture after this pass. They are not failures of the whole archive; they are the rows where the maintainer should not quote or rely without better capture:

- UK flood legal-text routes requiring exact amendment/current-text capture;
- New Zealand legal-personhood statutory routes needing authoritative text capture;
- LAHSA audit material where the direct report route still needs page/PDF capture;
- OHCHR/BINUH Haiti materials where route barriers or capture limits remain.

A small hard queue is more useful than a broad soft warning queue.

### 4. Keep route absorption behind evidence parity

The service-home absorption work still should not be treated as done. The protected elements from note 615 remain only partially absorbed into the current route family. Source-health closure helps, but note retirement still requires generated test parity, source parity, and a surviving generic service-home route beyond the London/TfL example.

## Audit/refactor shipped

Rev0774 changes `tools/build_source_health.py` so generic `followup` strings no longer create capture warnings by themselves. It also refreshes source-health rows that had been left in capture posture despite official page/PDF/record capture in the session.

The resulting audit surface is harder to game:

- direct review means a maintainer reached or attempted the route;
- clean direct review means no explicit capture-required signal remains;
- follow-up capture means a specific page/PDF/search/blockage/legal-text problem still requires work before quote-level reliance.

## Failure modes blocked

- No source cleanliness by review-clock label.
- No legal reliance by search-index route.
- No AI safety by memorandum, register, or transparency page.
- No infrastructure continuity by board packet.
- No local handback by waiver row.
- No fragile-jurisdiction capacity by mandate, donor strategy, or humanitarian message.
- No route retirement by partial absorption without generated parity.

## Next move

Work the seven remaining capture-required rows with page-level captures or authoritative legal-text snapshots. In parallel, add service-home test parity before any route in the note-615 merge packet is marked deletion-ready.

## Governing rule

**No clean source by review clock.**
