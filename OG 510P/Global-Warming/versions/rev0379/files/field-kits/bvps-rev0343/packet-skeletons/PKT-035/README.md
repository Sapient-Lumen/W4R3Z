# PKT-035 — FIRST-RECEIVER — ED triage

Owner: healthcare_coalition_lead  
Backup: EMS_medical_backup  
Capture window: T+2h to T+48h  
Artifact ID pattern: `BVPS-2026EX-FIRST-RECEIVER-PKT-035-{YYYYMMDDTHHMMSS}-{HASH8}`

Minimum check-in contents:

original artifact hash; redacted surrogate hash or sensitive-annex reason; owner; timestamp; source clock; custody event; counterevidence path

Loss default cap:

blocks hospital surge claim

Claim boundary: this packet skeleton and any completed form are not readiness closure. A packet may become a candidate for adjudication only after hashing, custody, redaction/surrogate pairing, quality gate, counterevidence path, and claim-board routing.
