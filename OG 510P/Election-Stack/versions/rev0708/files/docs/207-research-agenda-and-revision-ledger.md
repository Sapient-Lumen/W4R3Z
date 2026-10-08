# 207. Research agenda and revision ledger (compact)

**Track:** Shared

This doc is intentionally small. It is the **near-term work queue** that keeps the archive honest
without turning into a second archive.

**Rule of thumb:** if an agenda item cannot name (a) the claim boundary it touches, (b) the proof
obligation / hazard it advances, and (c) an artifact that would count as progress, it does not
belong here. Put it in `172` instead.

If you are advancing an item toward a stable surface, follow `229-experiment-to-spec-promotion-protocol.md`.

## 207.1 Near-term agenda (next 3–6 months)

1) **Public-surface authenticity in the AI era (Track A)**
   - **Touches:** `186–187`, `194–206`; hazards `HZ-020`/`HZ-021`; obligations `PO-011`/`PO-012`.
   - **What “progress” looks like:** one jurisdiction-grade reference checklist + a repeatable parity/freshness test plan for the declared official surfaces (operator artifact: `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md`).
   - **Artifacts:** extend checklists/templates (not new kinds) and publish *example* evidence packets for comms exercises.
   - Include results lifecycle labeling + correction discipline hooks (`234`) when publishing ENR updates.
   - Recent tightening: PublicNotice signing key allow-list (`208`) and keyset digest anchoring in discovery (`203–204`).
   - Recent tightening: comms/discovery example packets (feed/directory/.well-known) + tooling maturity intent registry (`212`).
   - Recent tightening: election-process milestone notices (canvass/certification/recount) as digest-first PublicNotices (`237`; `notice_type=election_milestone` + `milestone_id` registry).
   - Recent tightening: voter-facing public-surface trilogy for location / ballot-style / registration-status answers (`292–294`) so “where / what / am I registered?” disputes have explicit supersession and parity evidence.
   - Recent tightening: media in-player moment-jump alias / transcript-chapter-pick companion (`544`) so “the same object stayed current but playback jumped through transcript clicks, chapter picks, or other player-internal selections” is treated as a bounded chain/default-retention problem rather than false supersession, false explicit-offset classification, or generic seek-state drift.
   - Recent tightening: media transcript-pane-state / search-focus companion (`557`) so “the same object stayed current but the transcript pane was merely opened, searched, or left highlighting one line” is treated as a bounded chain/default-retention and minimization problem rather than false supersession, false transcript-edition promotion, or generic transcript-surface drift.
   - Recent tightening: media interaction-pane-state / social-tab-focus companion (`558`) so “the same object stayed current but comments, live chat, Q&A, polls, or another interaction pane was merely opened, tab-switched, feed-switched, or left foregrounding one item” is treated as a bounded chain/default-retention and minimization problem rather than false supersession, false social-answer promotion, or generic comment/chat drift.
   - Recent tightening: media live-position-state / behind-live-recovery companion (`559`) so “the same still-live object stayed current but the viewer was paused live, behind live, recovered to live, or watching from an earlier shown-live point” is treated as a bounded chain/default-retention problem rather than false supersession, false explicit-offset classification, or generic DVR/live-edge drift.
   - Recent tightening: media next-item-queue-state / up-next-foreground companion (`560`) so “the same current object still controlled but a queue, up-next slot, TV queue, or playlist-side pending item was foregrounded beside it” is treated as a bounded chain/default-retention problem rather than false supersession, false successor-handoff completion, or generic collection-context drift.
   - Recent tightening: media derivative-readiness-state / processing-lag companion (`561`) so “the same current object already controlled but higher qualities, captions/transcripts, chapter/key-moment layers, replay derivatives, or other ordinary layers were still settling” is treated as a bounded chain/default-retention problem rather than false supersession, false reviewed-edition promotion, or generic half-ready-route drift.
   - Recent tightening: the platform-media AI-answer tail is now treated as one bounded same-object subfamily rather than as serial one-off growth, and `582` now gives ledgers and entrypoints one compact **top-line defaults** pair-level reference instead of making them keep re-spelling the same entrypoint-versus-neighbor handoff posture.
   - Recent tightening: `523`, `527`, and `530` now route that family compactly — boundary routing, packet carry, and downstream citations no longer need to reopen `499` or serially restate the whole AI tail once the current media object is already settled.
   - Recent tightening: platform-media chain-heads / current-control / closeout companion (`529`) so “the same-object chain was valid but several packets still sounded current and reviewers lacked one bounded rule for the active head versus historical legs” is handled as compact governance discipline rather than as pressure to duplicate or overwrite packets.
   - Recent tightening: platform-media chain-citations / head-first-reference / historical-leg-scoping companion (`530`) so “the chain already had a valid head, but later notes still cited the whole chain or an older leg as if it were the current answer” is handled as compact downstream reference discipline rather than as pressure to reopen the chain, mint another surface, or treat missing later companion tags as if they proved a bounded fact had cleared.
   - Recent tightening: platform-media head-supersession notes / trigger-codes / demotion companion (`531`) so “reviewers could identify the new current head, but later readers still had to reconstruct why the previous head was demoted and what changed in the controlling route” is handled as compact governance-note discipline rather than as pressure to overwrite packets or mint another surface.
   - Recent tightening: platform-media head-volatility-labels / provisional-current-notes / review-window companion (`532`) so “reviewers could identify the current head, but open chains still sounded more settled than they really were because the next likely state crossing or publication trigger was left implicit” is handled as compact forward-looking governance discipline rather than as pressure to mint another surface.
   - Recent tightening: platform-media no-public-head states / headless-chain-notes / fallback-anchor companion (`533`) so “the same-object chain still existed historically, but no public media packet should remain current because the route was withdrawn, restricted, or never published” is handled as compact absence-governance discipline rather than as pressure to keep a stale replay leg sounding current or to mint another restriction surface.
   - Recent tightening: platform-media co-current aliases / sibling-routes / canonical-head-with-alias companion (`534`) so “the same-object chain still had one controlling answer, but more than one public route remained current for it” is handled as compact same-answer multi-route governance rather than as pressure to emit false supersession notes or demote still-current sibling routes into historical legs.
   - Recent tightening: platform-media audience-scoped current aliases / scope-labels / public-default-retention companion (`535`) so “the same-object chain still had one ordinary-public head, but a narrower attendee-, registrant-, or invitee-scoped route also remained current for a defined subset” is handled as compact subset-route governance rather than as pressure to blur public and audience-scoped currentness or to collapse the case into headless-chain handling.
   - Recent tightening: platform-media route-scope transitions / widening-narrowing / alias re-bucketing companion (`536`) so “the same route or answer family later moved from ordinary-public to subset-only, subset-only to public, or public to headless without becoming a different underlying object” is handled as compact scope-reclassification discipline rather than as pressure to invent a new chain, emit false supersession, or leave the old bucket label in place.
   - Recent tightening: platform-media capability-bearing current aliases / link-secret routes / redaction-default companion (`537`) so “the same-object chain still had a current bearer-style unlisted, privacy-hash, or other token-bearing route and reviewers kept blurring possession-based access into either ordinary-public aliases or identity-scoped audience routes” is handled as compact capability-route governance rather than as pressure to reproduce secret-bearing links, mislabel them as public, or invent another surface.
   - Recent tightening: platform-media player-host render aliases / direct-embed routes / watch-page-default companion (`538`) so “the same-object chain still had a direct embed/player-host path and reviewers kept treating that render shell like an ordinary watch-page alias or a new current head” is handled as compact render-path governance rather than as pressure to promote iframe/player-host routes into the public default, blur them into secret-bearing link classes, or invent another surface.
   - Recent tightening: platform-media entrypoint-offset aliases / current-time-start-at routes / full-object-default companion (`539`) so “the same-object chain still had a `Start at`, current-time, or similar landing-point link and reviewers kept treating that offset route like a new current head, a clip, or the new public default” is handled as compact arrival-point governance rather than as pressure to promote one quoted moment into a new surface or blur it into generic share/export provenance.
   - Recent tightening: platform-media notification carriers / reminder pointers / route-carrier separation companion (`540`) so “the same-object chain still had a reminder, notification, inbox entry, or delivery email and reviewers kept treating that carrier like the current route it merely pointed to” is handled as compact delivery-wrapper governance rather than as pressure to promote inbox surfaces into route classes or blur what recipients received into what actually controlled.
   - Recent tightening: bounded request-context discipline (`224`) + hashes-first redaction logs (`225`) for court-usable, size-disciplined public bundles.
   - Recent tightening: canonical compact `req[...]` / `vary[...]` / `age[...]` note encoding (224.2a) with stdlib tool support for parity/liveness capture distillation.
   - External anchors: `xref: c2pa_content_credentials_spec_2_2_pdf`; `xref: cisa_tactics_of_disinformation_508_pdf`; `xref: cisa_bod_18_01_page`.

2) **Remote return experiments with explicit non-claims (Track B)**
   - **Touches:** `167` (N‑1), Track B bundle, and `172`.
   - **What “progress” looks like:** experiment briefs that make risks *measurable* (suppression, malware UI drift, coercion signals), not “solved.”
   - **Artifacts:** bounded experiment packets + verifier report expectations for “what can be proven anyway.”
   - External anchors: `xref: cisa_electronic_ballot_risk_mgmt_2020_pdf`; `source: nasem_securing_the_vote_highlights_pdf`; `source: eac_e2e_protocols_draft_tgdc_2023_pdf`.

3) **Verifier ecosystem reproducibility and capture resistance (Shared)**
   - **Touches:** `176`, `188`, `190`, `193`; hazard `HZ-018`; obligation `PO-008`.
   - **What “progress” looks like:** more interop vectors + a minimal “policy profile” format so independent verifiers can explain (and compare) decisions.
   - **Artifacts:** vectors + registries + report pins; avoid new prose unless it deletes older ambiguity.
   - Add visible capacity/distribution surfaces so “who will look?” is answerable before the crisis (DOC:`241`; kind `hfv.verifier.capacity_roster`).
   - External anchors: `source: rfc8785_txt`; `source: rfc9162_txt`.

4) **Time + ordering anchors for low-bandwidth evidence (Track A)**
   - **Touches:** `192`, `206`; hazards `HZ-019`/`HZ-021` (deadline disputes); obligations `PO-010`/`PO-012`.
   - **What “progress” looks like:** a repeatable pattern for chaining digest cards and PublicNotice updates to independent time attestations.
   - **Artifacts:** one small template set + one minimal example packet (using existing kinds).
   - External anchors: `source: rfc3161_txt`; `source: draft_ietf_ntp_roughtime_17_txt`; `source: rfc9334_txt`.

5) **Operational rehearsal as publishable evidence (Track A)**

   - **Touches:** `86`, `90`, `187`; drill-scenarios registry; hazards `HZ-020`/`HZ-021`.
   - **What “progress” looks like:** drills that emit bounded, publishable artifacts (PublicNotice + coverage/compliance evidence) without leaking sensitive internals.
   - **Artifacts:** tighten drill templates + add one “comms exercise packet” example (no new schema required).
   - Add at least three human-pressure drills (conflicting reports, forged official statement time-to-refute, legibility-theater publication drop) and keep them in the drill registry (no new schema required).
   - Ship a minimal Track A pilot plan + adopter briefing template (translation layer) without expanding Track A claims.

6) **Cross-register consistency checks without privacy leakage (Track A)**
   - **Touches:** `69`, `73`, `77`, `209`; obligations `PO-004`.
   - **What “progress” looks like:** agreed scope alignment rules + bounded aggregate publication that avoids a turnout oracle.
   - **Artifacts:** small report template + one example computation, using `hfv.results.cross_register_consistency_report`.

## 207.2 Revision discipline (anti-bloat, pro-clarity)

- Treat `150` as the canonical change protocol and `183` as the long-horizon stewardship posture; this is only the **change budget reminder**.
- Prefer: registry/checklist/template/tool → then doc cross-link → then (only if needed) new prose.
- If you add prose, delete redundant prose elsewhere in the same change.
- Keep this doc “two screens”: if the agenda grows, move items down into `172`.
