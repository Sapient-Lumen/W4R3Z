# PKT-011 — EAS-WEA — WEA console/export

Owner: alert_system_admin  
Backup: county_warning_point  
Capture window: T+0 to T+4h  
Artifact ID pattern: `BVPS-2026EX-EAS-WEA-PKT-011-{YYYYMMDDTHHMMSS}-{HASH8}`

Minimum check-in contents:

original artifact hash; redacted surrogate hash or sensitive-annex reason; owner; timestamp; source clock; custody event; counterevidence path

Loss default cap:

blocks alert-channel claim

Claim boundary: this packet skeleton and any completed form are not readiness closure. A packet may become a candidate for adjudication only after hashing, custody, redaction/surrogate pairing, quality gate, counterevidence path, and claim-board routing.
