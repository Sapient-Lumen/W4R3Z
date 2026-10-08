# 216 — Incident triage & evidence quickmap (symptom → packet)

**Track:** A (Deployable core)


This doc is a **tight dispatch map** for when something “feels wrong” (results, comms, availability, closeout).
It is *not* a full incident response manual. Its job is to reduce the time from:

- **complaint** → **bounded evidence objects** → **publishable statement tied to digests**.

Related:
- Lifecycle alignment (what exists when): `215`
- Court-usable bundle recipes (bounded): `211`
- Request-context variant probing (split-view root causes): `224`
- Redaction logs for transformed exhibits (hashes-first): `225`
- PublicNotice divergence dispute bundle minspec: `222` (checklist: `artifacts/checklists/publicnotice-divergence-dispute-bundle-checklist.md`)
- Claim cards (bounded dispute framing): `217` (template: `artifacts/templates/claim-card.md`)
- Epistemic tags + confidence rubric (for public statements): `218`
- Uncertainty-safe update structure (tags + commitments): `219` (quickcheck: `artifacts/checklists/public-update-epistemic-quickcheck.md`)
- PublicNotice + rumor response template: `artifacts/playbooks/public-notice-and-rumor-response.md`


## 216.1 The default loop (size-disciplined)

1. **Name the disputed surface** (results / comms / pointer freshness / closeout / registration).
2. **Classify the worst-credible catastrophe class** (C1..C5) before optimizing for convenience.
   - Registry: `artifacts/registries/catastrophe-classes.csv`
   - Threat framing: `171`
3. **Capture *digests*, not bodies** whenever possible.
   - Prefer: `hfv.public.surface_parity_snapshot` + `hfv.coverage.liveness_beacon` (`201`, `210`)
   - Use the stdlib distillers to avoid hand-editing digests: `tools/http_capture_to_parity_observation.py` (for `201`) and `tools/http_capture_to_observation.py` (for `210`). If request context matters, pass flags to emit a compact `req[...]` note (see `224.2a`).
   - Avoid bundling large screenshots/HTML unless strictly necessary (`205`, `211`)
   - If you retain raw HTTP captures to defend a digest computation, ship a small `capture-note.md` per `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`.
   - Record a bounded request-context line (UA class / language / cache-bypass / cookie presence) per `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`.
   - If any capture note or exhibit is edited/redacted for publication, ship `redaction-log.md` per `DOC:docs/225-redaction-logs-and-transformation-accountability.md`.
4. **Publish a bounded PublicNotice early** that states what is known/unknown and commits to the next update.
   - Canonical comms artifact: `hfv.public.notice` (`186`)
   - Templates: `artifacts/templates/public-notice-*.json`
5. **Assemble the smallest packet/bundle that makes the dispute legible offline**.
   - Packets: `173`, `176`, `177`
   - Minimal verifier path: `188` → publishable verifier report: `193`


## 216.2 “First 30 minutes” minimum (operator)

If you do nothing else:

- ☐ Issue a short **PublicNotice (incident advisory)** that includes `next_update_at`.
- ☐ Start **two independent vantage captures** for the disputed surface(s):
  - `hfv.coverage.liveness_beacon` (reachability + freshness headers + observed digests)
  - and/or `hfv.public.surface_parity_snapshot` (portable split-view proof)
- ☐ If impersonation is plausible: publish/refresh the **PublicNotice signing keyset** (`208`).
- ☐ Mirror the packet(s) to ≥2 independent mirrors (bounded discovery: `200`, bootstrap: `204`).

(If you have more time: run the relevant checklist in `artifacts/checklists/` and produce a verifier report packet.)


## 216.3 Symptom → evidence objects → checklists (quickmap)

This table is intentionally compact. When in doubt, prefer *missingness/split-view evidence* over verbose narratives.

| Symptom / allegation | Worst-credible risk | Minimum evidence objects (kinds) | Operator artifacts (examples) | Follow-on packet/bundle recipe |
|---|---|---|---|---|
| **“The official site says X, social says Y”** (or audiences see different statements) | C1/C3 (equivocation; irrecoverable ambiguity) | `hfv.public.notice` • `hfv.public.surface_parity_snapshot` • `hfv.coverage.liveness_beacon` | `artifacts/playbooks/public-notice-and-rumor-response.md` • `artifacts/checklists/audience-parity-monitoring-checklist.md` | `222` (divergence handoff) and/or `211.B` (fork/equivocation) or `211.D` (impersonation) |
| **“The feed/.well-known changed; some networks still see old values”** | C2/C3 (audience-targeted suppression; replay-by-proxy) | `hfv.coverage.liveness_beacon` • `hfv.public.surface_parity_snapshot` • `hfv.public.notice` | `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md` • `artifacts/checklists/unreachability-proof-checklist.md` | `211.E` (stale pointer / cache split-view) |
| **“ENR totals drifted / changed unexpectedly”** | C1/C3 (silent manipulation; ambiguity) | `hfv.results.enr_update` • `hfv.public.notice` (announce + pin) • optional `hfv.public.surface_parity_snapshot` | `artifacts/checklists/enr-drift-monitoring-checklist.md` • `artifacts/checklists/enr-security-checklist.md` | `211.B` (if equivocation) or `211.C` (if cross-register breach) |
| **“Some precinct closeout evidence is missing”** | C3 (selective omission) | `hfv.results.closeout_index` • `hfv.public.notice` • optional `hfv.publication.suppression_report` | `artifacts/checklists/precinct-closeout-evidence-capture-checklist.md` | `211.A` (publication suppression / missingness) |
| **“Official comms are impersonated / keys compromised”** | C1/C2 (capture; impersonation) | `hfv.public.notice_signing_keyset` • `hfv.incident.key_compromise_event` (if confirmed) • `hfv.public.surface_parity_snapshot` | `artifacts/checklists/official-communications-channels-hardening-checklist.md` • `artifacts/checklists/key-compromise-response-checklist.md` | `211.D` (impersonation / compromise) |
| **“Official endpoints are down / blocked / censored”** | C3/C4 (availability; missingness) | `hfv.coverage.liveness_beacon` • `hfv.public.notice` • optional `hfv.publication.suppression_report` | `artifacts/checklists/availability-response-checklist.md` • `artifacts/checklists/ripe-atlas-automated-urp-checklist.md` | `211.A` (suppression/missingness) |
| **“Ballot definition / style appears wrong”** | C1 (silent outcome manipulation) | `hfv.election.parameters_bundle` (commitments) • `hfv.public.notice` • (jurisdiction-specific) additional ballot-definition evidence | `artifacts/checklists/ballot-definition-incident-checklist.md` | Claim-first bundle per `211` + `60–61` |


## 216.4 Publishable comms rule (do not overfit)

- Prefer a **sequence** of small, linked PublicNotices over one large statement.
  - Use `supersedes_notice_id` for updates; `correction_of_notice_id` for corrections.
- Put **digests first**:
  - include packet digest(s) and the relevant pointer-surface digest(s) in the notice subject/body.
- If you cannot yet back a statement with evidence, say so explicitly and commit to a timestamp for the next update.


## 216.5 Verifier alignment (make disputes comparable)

When you publish a packet/bundle during an incident, try to also publish:

- `hfv.verifier.packet_verification_report` (for the packet) (`193`)
- verifier profile ID pins (`docs/VERIFIER_PROFILES.md`) and the policy-profile digest pin (`188`, `193`)

The point is not “one true verifier” — it is **comparable, bounded claims** across independent implementations.