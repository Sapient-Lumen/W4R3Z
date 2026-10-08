# PKT-002 — ALERT-AUTH — user role export

Owner: IPAWS_originator  
Backup: alert_system_admin  
Capture window: T-72h to T+0  
Artifact ID pattern: `BVPS-2026EX-ALERT-AUTH-PKT-002-{YYYYMMDDTHHMMSS}-{HASH8}`

Minimum check-in contents:

original artifact hash; redacted surrogate hash or sensitive-annex reason; owner; timestamp; source clock; custody event; counterevidence path

Loss default cap:

blocks any alert-readiness claim

Claim boundary: this packet skeleton and any completed form are not readiness closure. A packet may become a candidate for adjudication only after hashing, custody, redaction/surrogate pairing, quality gate, counterevidence path, and claim-board routing.
