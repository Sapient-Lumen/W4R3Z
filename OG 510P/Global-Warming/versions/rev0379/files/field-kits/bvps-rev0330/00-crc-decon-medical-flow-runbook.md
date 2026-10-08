# BVPS rev0330 CRC/decon/medical-flow field capture runbook

Purpose: capture enough local or anonymized evidence to adjudicate CRC throughput and medical/decon readiness without exposing PII, PHI, security-sensitive details, or exact vulnerable-facility details.

Minute-zero capture:
1. Start station clocks and confirm device time sync.
2. Record station staffing and instrument IDs in sensitive annex; write public-safe surrogate hashes.
3. Capture arrivals, triage decisions, screening readings, decon lane times, post-decon rescreen, medical transfers, registry counts, family reunification exceptions, waste/water custody, and release instructions.
4. Preserve evaluator observations with station/time/objective links.
5. Do not mark any packet closed in the field. Field packets are candidates for adjudication only.

Required public-safe outputs: station counts, time-window summaries, hashed artifact manifest, redaction map, exceptions count, CAP/retest linkage, and public-claim gate state.
