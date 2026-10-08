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
   - Recent tightening: PublicNotice signing key allow-list (`208`) and keyset digest anchoring in discovery (`203–204`).
   - Recent tightening: comms/discovery example packets (feed/directory/.well-known) + tooling maturity intent registry (`212`).
   - Recent tightening: publishable surface anomaly code registry for parity/liveness notes (`docs/SURFACE_ANOMALY_CODES.md`).
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

6) **Cross-register consistency checks without privacy leakage (Track A)**
   - **Touches:** `69`, `73`, `77`, `209`; obligations `PO-004`.
   - **What “progress” looks like:** agreed scope alignment rules + bounded aggregate publication that avoids a turnout oracle.
   - **Artifacts:** small report template + one example computation, using `hfv.results.cross_register_consistency_report`.

## 207.2 Revision discipline (anti-bloat, pro-clarity)

- Treat `150` as the canonical change protocol and `183` as the long-horizon stewardship posture; this is only the **change budget reminder**.
- Prefer: registry/checklist/template/tool → then doc cross-link → then (only if needed) new prose.
- If you add prose, delete redundant prose elsewhere in the same change.
- Keep this doc “two screens”: if the agenda grows, move items down into `172`.

