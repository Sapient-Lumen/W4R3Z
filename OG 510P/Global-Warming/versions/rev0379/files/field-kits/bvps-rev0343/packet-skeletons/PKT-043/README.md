# PKT-043 — REENTRY — access control

Owner: recovery_branch  
Backup: claims_registry_backup  
Capture window: T+24h to T+120d  
Artifact ID pattern: `BVPS-2026EX-REENTRY-PKT-043-{YYYYMMDDTHHMMSS}-{HASH8}`

Minimum check-in contents:

original artifact hash; redacted surrogate hash or sensitive-annex reason; owner; timestamp; source clock; custody event; counterevidence path

Loss default cap:

blocks recovery/reentry claim

Claim boundary: this packet skeleton and any completed form are not readiness closure. A packet may become a candidate for adjudication only after hashing, custody, redaction/surrogate pairing, quality gate, counterevidence path, and claim-board routing.
