# Structural audit rev0331

## Focus

Rev0331 extends the emergency-preparedness operational proof spine from CRC/decon throughput into first-receiver and EMS/hospital surge.

## Substantive correction

CRC arrival and population monitoring are not sufficient to prove healthcare readiness. The cube now has independent P0 cutsets for direct ED self-presenters, ambulance contamination turnaround, first-receiver PPE/training/dosimetry, lifesaving trauma/burn/critical-care priority, transfer network proof, and radiation medicine consultation.

## Metadata correction

The rev0330 file-core row for file 537 contained blank evidence/route/tag fields while file.csv had populated values. Rev0331 regenerates file-core from file.csv and adds data-quality checks for file-core completeness at the latest revision.

## Claim control

All new validator states are rejected_closure_attempt, hold_no_upgrade, context_no_upgrade, accepted_reopen_signal, or candidate_for_adjudication. No auto-closure state exists.
