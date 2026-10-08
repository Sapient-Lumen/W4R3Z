# 278 — Litigation hold and evidence preservation (freeze the evidence plane without freezing the election)

**Track:** Shared

When results are contested, the outcome can hinge on **what can be produced, not what happened**.
A hostile actor (or just chaos) can “win” by degrading logs, overwriting systems, or making provenance unverifiable.

This doc defines a *minimal, spec-first* preservation protocol that treats **preservation itself as an evidence surface**:
a publishable, digest-first record that (a) a hold was triggered, (b) what it covered, and (c) how integrity was maintained.

> This is not legal advice. It is an engineering template meant to be reviewed with counsel and adapted to local law.

---

## 1) Threat model: “spoliation by entropy”
Preservation failures are often *banal*: log retention windows, vendor portals, device wipes, mailbox limits, staff turnover,
and “cleanup scripts” that run as designed.

Key failure modes:
- **Short retention**: SIEM / CDN / WAF / IdP logs roll off before dispute timelines.
- **Vendor black boxes**: managed services keep the only authoritative logs.
- **Reactive reimaging**: “fixing” an incident destroys the forensic record.
- **Ad hoc exports**: screenshots + PDFs without provenance; no hash chain; no chain-of-custody.
- **Selective preservation**: only the “good looking” systems are saved.

Engineering posture: assume disputes arrive *after* the default retention horizon unless you intervene immediately.

---

## 2) Hold trigger policy (engineering, not politics)
Define a narrow set of triggers that can be applied consistently:
- **Statutory / procedural**: recount threshold crossed; formal contest filed; court preservation order.
- **Operational**: credible intrusion indicator affecting election infrastructure; verified publication suppression.
- **Governance**: independent monitor requests preservation under pre-agreed policy.

Triggering a hold should be treated like declaring an incident:
a bounded scope, named owner, and an auditable record of actions.

(For incident comms discipline, see `186` and `259`.)
source: eac_incident_response_comms_guide_pdf

---

## 3) Preservation scope: the “evidence plane”
A litigation hold for elections should target **evidence planes**, not just devices.

Minimum planes (adapt to jurisdiction):
1. **Tabulation + reporting systems**
   - EMS, scanners, adjudication workstations, unofficial results pipeline.
2. **Voter registration + pollbooks**
   - registration DB exports, pollbook sync logs, check-in device images where applicable.
3. **Publication surfaces**
   - official websites, status boards, mirror indexes, social comms accounts used for notices.
4. **Identity + access**
   - IdP logs, admin actions, MFA changes, privileged access workflows.
5. **Network + perimeter**
   - firewall/WAF/CDN logs, VPN logs, DNS changes, BGP/anycast notes (if relevant).
6. **Third parties**
   - vendors, hosting providers, managed SOC/SIEM, ballot printers, courier logistics systems.

---

## 4) Minimal hold protocol (MHP): the 12 steps
**Goal:** preserve quickly, produce verifiable artifacts, minimize disruption.

1) **Declare Hold Capsule**
- Create a `HoldCapsule` record: trigger, timestamp, owner, scope planes, and initial retention overrides.
- Commit it to CommitLog / transparency log as a signed event.
(See `261` and `04`.)

2) **Stop destructive automation**
- Suspend auto-deletion, log rotation, “cleanup” jobs, device reimaging, mailbox purge rules (where possible).

3) **Extend retention**
- Apply retention extensions in SIEM/IdP/CDN/WAF and vendor portals immediately.

4) **Snapshot configurations**
- Export config + policy for critical systems (IdP, WAF, DNS, EMS configs) as signed, hashed bundles.

5) **Image high-risk endpoints**
- For key endpoints (EMS admin, adjudication, tabulation controllers): create forensic images or vendor-supported equivalents.

6) **Export canonical logs**
- Export logs with *original timestamps and identifiers*.
Avoid screenshots except as a fallback.

7) **Hash + seal exports**
- Every export gets:
  - content hash
  - signer identity
  - capture time window
  - tool/version metadata
  - chain-of-custody entry
(ISO guidance emphasizes identification/collection/acquisition/preservation activities as distinct steps.)
xref: iso_iec_27037_iso_page

8) **Write-once storage & multi-party escrow**
- Store bundles in WORM-capable storage where possible, plus at least one independent escrow.

9) **Access control hardening**
- Freeze privileged access: require break-glass with dual control and explicit logging.

10) **Provenance map**
- Record where the “authoritative copy” of each plane lives (including vendor custody).

11) **Public “Hold Notice” (optional but powerful)**
- Publish a minimal public notice: “hold triggered; scope planes; retention extended; how to request access”.
Keep it digest-first to avoid leaking sensitive details.
(See `195`, `200`, and `219`.)

12) **Hold review cadence**
- Set a review date; update scope when new systems are discovered; record every change as a signed delta.

---

## 5) Make preservation auditable: the HoldCapsule schema sketch
A HoldCapsule is intentionally small and linkable:

- `hold_id` (unique)
- `trigger` (policy code + free text)
- `declared_at` (timestamp)
- `owner` (role + key ID)
- `scope_planes[]` (enum + notes)
- `retention_overrides[]` (system, old→new window)
- `artifact_refs[]` (hashes/URIs to evidence bundles)
- `third_party_notices[]` (vendor ticket IDs, contact, requested actions)
- `access_policy` (who can request what, under what process)
- `supersedes` (optional)

This composes with:
- `225` (redaction logs when producing public subsets)
- `211` (court evidence bundle recipes)
- `247` (ops security controls, comms, chain-of-custody)

---

## 6) Legal alignment (high level)
Two practical anchors:
- **Duty to preserve ESI** can attach when litigation is reasonably anticipated, and courts evaluate “reasonable steps” to preserve.
xref: frcp_rule_37_lii_html
- **Forensic readiness**: integrate forensics into incident response planning so you don’t destroy evidence while restoring service.
source: nist_sp800_86_pdf

Again: adapt to jurisdiction; validate with counsel.

---

## 7) Deployment checklist (tight)
- [ ] Define triggers + owner roles in advance.
- [ ] Pre-negotiate vendor log retention + export rights + response SLAs.
- [ ] Pre-build export scripts / runbooks (with non-destructive defaults).
- [ ] Keep WORM storage and escrow keys ready.
- [ ] Practice: run a “tabletop hold” annually (like an incident drill), and publish the *exercise* HoldCapsule.

---

## See also
- `259-incident-reporting-and-coordinated-disclosure-as-evidence-surfaces.md`
- `261-public-commitments-and-transparency-logs-for-election-evidence.md`
- `211-court-evidence-bundle-recipes.md`
- `247-ops-security-controls-comms-and-chain-of-custody.md`
