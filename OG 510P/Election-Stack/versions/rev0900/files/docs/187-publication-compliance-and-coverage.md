# 187 — Publication compliance and coverage (from promises to measurable outcomes)

**Track:** A (Deployable core)

This project assumes attackers may win by **corrupting the verification ecosystem** rather than the tally:
they delay, suppress, or selectively disclose evidence and communications so different audiences see different realities.

Docs/181 introduces *PublicationContract* (promises). This doc adds a minimal mechanism to make those promises
**measurable** and to make "missingness" both provable and mirrorable.

## Core objects (new)

1) **PublicationTriggerEvent** (`hfv.publication.trigger_event`)

A signed/gossiped declaration that a deadline trigger occurred at a specific time.
It is a *deadline anchor* that can be mirrored and audited.

Payload schema: `schemas/PublicationTriggerEvent.json`

Typical issuers:
- operator (declared incident, polls open/close, ENR generation start)
- watcher/monitor (observed incident, detected deadline breach, detected rumor/attack)

2) **PublicationCoverageReport** (`hfv.coverage.publication_report`)

A computed report that summarizes (for a time window) whether required publications occurred on time
for each contract rule, given a set of TriggerEvents.

Payload schema: `schemas/PublicationCoverageReport.json`

This report is itself a public evidence artifact and is (per registry) **receipted + gossiped**.

## How compliance is computed (reference semantics)

Given:
- a `PublicationContract` (docs/181),
- a set of `PublicationTriggerEvent`s,
- the set of published `EvidenceEnvelope`s,

then for each TriggerEvent and each contract rule with a matching trigger_id:

- compute: `deadline = occurred_at + max_delay_seconds`
- satisfied iff there exists at least one envelope of the rule's `kind`
  with `issued_at` in `[occurred_at, deadline]`

This is deliberately simple:
- it avoids fragile semantic coupling early (v0),
- it is enough to measure **selective delay** and **selective omission** in practice.

Future work can strengthen linkage (e.g., requiring PublicNotices to cite the event_id).

## Public notices and narrative integrity

Public communications are evidence objects (docs/186).
To make narrative suppression measurable, jurisdictions SHOULD:

- include a contract rule for `hfv.public.notice` triggered by `incident_declared`,
- publish a TriggerEvent when an incident is declared or detected,
- publish a PublicNotice within the contract delay,
- publish a PublicationSuppressionReport if the deadline is missed.

This turns "they didn't tell us" into a portable, cryptographically bound statement.

## Tooling (stdlib-only reference)

`tools/publication_compliance.py` computes a PublicationCoverageReport from an evidence packet directory:

```bash
python tools/publication_compliance.py artifacts/examples/evidence_packet_publication_compliance_minimal
```

This tool is intentionally conservative: it treats `issued_at` as publication time and checks for existence.

Operator helper (bounded card, copy/pasteable):
- `python3 tools/publication_coverage_report_card.py --packet <packet_dir>`

## Anti-gaming notes

- TriggerEvents MUST be receipted + gossiped (registry) to prevent **suppression of the anchor**.
- Multiple issuers are expected; conflicting TriggerEvents are *useful evidence* and should not be normalized away.
- Coverage reports should be published by multiple watchers; "watchers inspecting monitors" is a core stance.
- Where suppression of publication evidence is suspected, independent watchers SHOULD also publish receipted+gossiped **LivenessBeacons** (`hfv.coverage.liveness_beacon`, docs/210) that record reachability and observed digests for the public pointer surfaces.



## Adversarial publication test (defense against “legibility theater”)

A common institutional failure mode is **minimal‑effort compliance**: publishing something that is technically “public”
but operationally useless (e.g., a PDF scan, an unstable link, or a huge dataset without an index).

The design goal is **not** “make it impossible to be bad.” It is: make the **least‑effort compliant publication still useful**
to third parties under time pressure.

### MAPT: the minimal adversarial publication test

Treat a publication requirement as *not met in practice* unless a skeptical third party can do all of the following from a normal laptop
(without private credentials) during an incident window:

1) **Fetch** the authoritative bytes quickly  
   - stable pointers (`.well-known`, official directory, feeds) (`200–205`),
   - bounded response sizes for pointer surfaces (JSON, not HTML/JS apps),
   - no “PDF as API” for machine‑facing data.

2) **Verify** the claim within minutes  
   - digest‑first artifacts (`PublicNotice`, packet manifests, short digest cards),
   - schemas / machine‑checkable formats (JSON/CSV with declared schema; not scans),
   - link‑forward to prior versions so “correction” is legible (`234–236`).

3) **Mirror + compare** (so disagreement becomes evidence, not vibes)  
   - content‑addressed objects + manifests (portable),
   - parity snapshots / liveness beacons when audiences report divergence (`221–222`),
   - low‑bandwidth fallbacks if the main site fails (`206`).

4) **Stay usable under stress**  
   - predictable naming, small indexes, sharding when datasets are large,
   - published deadlines measured as coverage reports, not prose promises.

If an artifact fails MAPT, treat it as a **publication incident** even if it “exists somewhere on a website.”

For hazard tracking, treat recurring MAPT failure (“legibility theater”) as **HZ‑027** in the hazard register.

**Operator artifact:** use `artifacts/checklists/minimal-adversarial-publication-test.md` as the bounded checklist.

**Recordkeeping (bounded):** when MAPT is run for a drill/pilot/release, add a row to `artifacts/registries/mapt-evaluations.csv` that points to the relevant digest(s) (AAR, packet manifest, parity snapshot), rather than pasting long notes into the archive.


## Adversarial publication failure modes (what attackers actually do)

The compliance mechanism above measures whether an artifact was published **on time**.
Adversaries also attack *how* publication works so that “it exists” but key audiences cannot fetch, verify, or compare it.

Treat the following as first‑class incidents (capture as evidence; don’t litigate them as vibes):

- **Selective delivery / A/B content:** different bytes by geo, language, UA, cookies, or WAF policy.  
  Capture with `hfv.public.surface_parity_snapshot` + bounded request-context notes (`201`, `223–224`, `232`).
- **Pointer churn / moving targets:** redirect chains, unstable URLs, “latest” rewrites without correction semantics.  
  Prefer stable `.well-known` + directory pointers (`203–204`) and link‑forward corrections (`220`, `234`).
- **Throttling / CAPTCHA / auth walls:** evidence reachable for some but not independent monitors.  
  Publish liveness beacons + parity snapshots and treat as a publication incident (`210`, `201`).
- **Unindexable dumps (“PDF as API”):** technically public but operationally unusable during a dispute.  
  Fails MAPT; fix by publishing bounded indexes + digest cards (`206`).
- **Paywalls / proprietary portals:** “public” only through a vendor platform.  
  Treat as vendor‑capture signal; deploy procurement guardrails (`183.6.2`, procurement template).

**Drill it:** `selective_delivery_split_view` in `artifacts/registries/drill-scenarios.csv`.

## Related docs

- docs/181 — PublicationContract and deadline breach proofs
- docs/184 — Trigger vocabulary registry (drift firewall)
- docs/186 — Incident communications as evidence (PublicNotice)
- docs/174 — Coverage accounting and representativeness
