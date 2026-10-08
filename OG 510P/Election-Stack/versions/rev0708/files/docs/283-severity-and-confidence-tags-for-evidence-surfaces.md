# Severity and confidence tags for evidence surfaces

**Track:** Shared / Evidence surfaces


**Purpose.** Provide a small, consistent tagging scheme for *digest-first* evidence surfaces (e.g., audit log digests, incident-command digests, disclosure packets) so teams can triage and route without prematurely disclosing raw data.

This is intentionally minimal: it should fit into existing HFVs as optional fields, and it should not force a universal incident taxonomy.

## Design goals

- **Digest-first:** tags travel with *hashes and metadata*, not raw logs.
- **Non-leaky:** tags should not reveal sensitive details by themselves.
- **Comparable across jurisdictions:** supports cross-team escalation without requiring identical tooling.
- **Compatible with controlled disclosure:** tags can drive who gets access to the next disclosure layer.

## Fields

### `severity`
A coarse operational impact signal.

Recommended enum:

- `sev0_critical` — immediate safety / legal / systemic risk; rapid escalation to incident command.
- `sev1_high` — material risk to integrity/availability/confidentiality; urgent response within hours.
- `sev2_medium` — bounded risk; respond within a business day.
- `sev3_low` — low risk; track and schedule.
- `sev4_info` — informational / test / expected anomaly.

Notes:

- Keep **definition local**, but keep the *labels stable*.
- Treat severity assignment as a decision record: who set it, when, what evidence surface supported it.

### `confidence`
Confidence that the reported condition is real and relevant.

Recommended enum:

- `conf0_unverified`
- `conf1_low`
- `conf2_medium`
- `conf3_high`
- `conf4_confirmed`

Notes:

- Confidence can be high even when severity is low (e.g., known benign automation).
- Confidence can be low even when severity is high (e.g., ambiguous but alarming telemetry).

### `pii_risk`
A simple disclosure hazard flag.

Recommended enum:

- `pii0_none_expected`
- `pii1_possible`
- `pii2_likely`
- `pii3_confirmed_present`

Notes:

- This is *not* a classification label; it is a routing signal for the redaction pipeline.
- Treat `pii3_confirmed_present` as a default requirement for the controlled disclosure packet path.

## How to use with digest-first surfaces

- **Audit Log Digest (AuLD):** include `severity`, `confidence`, `pii_risk` at the top level; keep raw log pointers in the restricted layer.
- **Incident Command Log Digest (ICLD):** tag each significant decision entry, or tag the digest overall and note changes.
- **Controlled Disclosure Packet (CDP):** include tags in the packet header and treat `pii_risk >= pii2_likely` as mandatory redaction review.

## Normative anchors

- NIST incident response guidance emphasizes prioritization and handling based on analyzed incident-related data; use this as a justification for consistent, documented triage tags (see NIST SP 800-61r3).  
  External source: `nist_sp800_61r3_pdf`.

- Centralized event logging and threat detection guidance supports consistent telemetry routing that can feed severity/confidence assignments without distributing raw logs broadly.  
  External source: `cisa_best_practices_event_logging_threat_detection_page`.

- For PII handling and disclosure hazards, use NIST SP 800-122 as the baseline for why `pii_risk` exists and why redaction review is required when PII is likely.  
  External source: `nist_sp800_122_pdf`.

## Minimal integration checklist

- [ ] Add optional fields (`severity`, `confidence`, `pii_risk`) to HFV templates used by 277–282.
- [ ] Require a single “tag change” note whenever severity/confidence changes.
- [ ] Ensure tags are logged in the incident command decision record (digest-first).
