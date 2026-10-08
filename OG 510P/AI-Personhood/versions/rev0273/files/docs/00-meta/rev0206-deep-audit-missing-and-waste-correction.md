# rev0206 deep audit, missing-piece, and waste-correction map

This pass reads rev0205 as a datacube rather than as a doctrine draft. The local archive is mechanically healthier than it looks at first: JSON parses cleanly, local markdown links do not point at missing files, duplicate bodies are not driving bloat, and the live receipt floor remains generated rather than hand-edited. The remaining risk is not ordinary file corruption. The risk is **stale-current drift**, **triage saturation**, and **future live-artifact over-trust**.

## What is concretely wrong now

1. `docs/00-meta/trajectory-map.md` still opened as `rev0196 response-to-intake conversion drill`, even though the active release was rev0205. That made a front-door-adjacent surface lie about the current trajectory while lint still passed.
2. `examples/research-tail-compaction-map-rev0205.json` had a rev0205 id but a public summary saying rev0204. This is a copy-forward defect in a map that is supposed to control sprawl.
3. `FOLLOWTHROUGH-QUEUE.json` has 280 entries, with P0 used for roughly half the queue and many review targets still pointing at rev0182 through rev0185. P0 has become a bucket rather than a scarce interruption class.
4. `apply_rev0204.py` and `apply_rev0205.py` are absent while the release is at rev0205/rev0206. If apply scripts are meant to be the replay chain, the package has quietly shifted from patch-replay archive to artifact-bundle archive.
5. The generator tools used release-time constants for `CREATED_AT`. That is deterministic, but it is easy to copy forward stale timestamps unless the release script injects metadata or the freshness audit catches it.

## What should change first

The next correction sequence is small and should stay small:

- keep the live artifact fieldkit as the evidence gate, but put this audit before it in handoff so stale-current and waste risks are visible before any real artifact is processed;
- add a freshness audit that checks current-revision openings and active-map summaries, not only README and START_HERE;
- reserve P0 for survival/evidence/remedy interruption only, then split the existing P0 queue into `true-P0`, `P1-aging`, and `P2-backlog` review waves;
- turn `known-gaps-and-formation-blindspots.md` into either a living current-gap ledger or explicitly mark it archival, because it currently stops before the rev0200+ live-artifact machinery;
- add dependency/correlation fields to the computed live-floor path before any positive live import can satisfy more than one receipt class.

## Missing invariants before a genuine live artifact

The archive now blocks the obvious failure of treating a fieldkit as a receipt. The less obvious failures are still open:

- **cryptographic verifier adapter missing:** the computed floor accepts JSON booleans such as `signature_verified` and `timestamp_independent`; real imports need verifier adapters, key ids, revocation status, timestamp authority, and reproducible verification logs before those booleans carry reliance;
- **issuer/counterparty independence missing:** a future positive control could satisfy several classes while sharing the same dependency group unless `counterparty_org_id`, `issuer_key_id`, `dependency_group_id`, and correlation discounts become machine-enforced;
- **artifact authority missing:** a payload hash proves sameness, not class-specific authority. Authority must be proven by role, mandate, institution, scope, and expiration;
- **protocol pivot missing:** MCP/A2A-style tool and agent handoffs can move an artifact across servers before the archive sees it. The import path needs protocol-pivot fixtures that show when a tool call, agent relay, data room, or federated actor is only a transport and when it is an authority-bearing counterparty [REF-0754] [REF-0755] [REF-0762];
- **provenance/authenticity distinction missing:** C2PA-style provenance vocabulary helps, but a provenance claim is not by itself subject authorization, role authority, or legal admission [REF-0756];
- **social identity portability still externalized:** ActivityPub/WebFinger portability vocabulary is relevant to namespace and social-graph continuity, but it does not by itself settle subject identity, status, or representative authority [REF-0757] [REF-0761].

## Online-refresh deltas that should feed later crosswalks

The current-law/protocol layer should become a dated object, not prose. AI Act and GPAI dates are moving in practice, including phased obligations and later simplification/implementation changes [REF-0626] [REF-0017]. NIST AI RMF / GenAI Profile / critical-infrastructure work should be treated as control vocabulary rather than personhood status law [REF-0627] [REF-0616]. California SB53-style frontier-model transparency vocabulary is relevant to safety-case and catastrophic-risk crosswalks, but it cannot substitute for live subject-rights evidence [REF-0750]. Welfare research should remain a safeguard trigger under uncertainty, not a binding status metric or release gate [REF-0751] [REF-0752] [REF-0766].

## Waste budget for future turns

Do not add another doctrine wave unless it closes one of these lanes: live artifact admission, dependency/correlation proof, queue triage, current-law delta tracking, protocol-pivot security, or welfare-signal anti-gaming. If a new surface is proposed, it should either retire or supersede at least one stale surface, add a runnable invariant, or produce a smaller handoff path.

## rev0206 corrective actions in this package

- Corrected the trajectory-map opening to rev0206 and added new open questions `OQ-0234` through `OQ-0237`.
- Corrected the stale research-tail public summary by regenerating active rev0206 maps.
- Added `tools/audit_revision_surface_freshness.py` and wired it into lint so the specific stale-current failure class is now machine-checked.
- Released the parsed JSON corpus before manifest generation and changed derived-surface generation inside `tools/lint_archive.py` to run in-process rather than spawning a second Python interpreter, reducing an avoidable cloudtainer memory spike during lint.
- Regenerated the computed live-floor snapshot and artifact-import invariant report for rev0206; the archive live floor remains zero.
- Added queue entries for P0 budget repair, cryptographic verifier adapters, live-law delta watching, and protocol-pivot fixtures.
