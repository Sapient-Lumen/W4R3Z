# Current public context refresh — rev0054

## homepage-release-context

- Source: https://nicotine-plus.org/
- Observation: Homepage observed during rev0054 still identifies 3.3.10 as current stable and points testers to the 3.3.11 release candidate.
- Impact: Retain current-source refresh as pre-filing gate; stable package status alone does not retire private packets.
- Status: refreshed via web

## news-release-context

- Source: https://nicotine-plus.org/NEWS.html
- Observation: NEWS observed during rev0054 still lists Version 3.3.11 Release Candidate 1 with broad correction language for uncompressed network message size limits, upload spoofing, username identity, distributed search, and empty-room search behavior.
- Impact: Keep release-note overlap as broad/adjoining context, not packet retirement by itself.
- Status: refreshed via web

## milestone-context

- Source: https://github.com/nicotine-plus/nicotine-plus/milestone/15
- Observation: Milestone 3.3.11 observed as open, last updated Jun 12 2026, 97% complete, with PR #3781 as the one open item.
- Impact: Public path-join work remains public-watch-only and does not alter private packet count.
- Status: refreshed via web

## public-pr-3781

- Source: https://github.com/nicotine-plus/nicotine-plus/pull/3781
- Observation: PR #3781 observed public/open; visible text describes safe_path_join() removing illegal/path-traversal components and keeping the final path within the base path.
- Impact: Retain PUBLIC-PATH-JOIN-PR-3781 as public-watch-only.
- Status: public watch retained

## public-pr-3723

- Source: https://github.com/nicotine-plus/nicotine-plus/pull/3723
- Observation: PR #3723 observed public/closed historical context for clean_path() path-traversal handling.
- Impact: Retain PUBLIC-PATH-JOIN-PR-3723 as public-watch-only.
- Status: public watch retained

## current-master-web-source

- Source: raw.githubusercontent.com/nicotine-plus/nicotine-plus/master
- Observation: Selected marker scan of web-visible raw master files is incomplete for every strict packet; parser-budget constants were not visible.
- Impact: Use as triage evidence only; still requires a clean current checkout and regression rerun.
- Status: web marker snapshot recorded

## current-3.3.x-web-source

- Source: raw.githubusercontent.com/nicotine-plus/nicotine-plus/3.3.x
- Observation: Selected marker scan of web-visible raw 3.3.x files is incomplete for every strict packet; parser-budget constants were not visible.
- Impact: Use as triage evidence only; still requires a clean current checkout and regression rerun.
- Status: web marker snapshot recorded
