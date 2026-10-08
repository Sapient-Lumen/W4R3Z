# Structural audit rev0333

Rev0333 adds a BVPS ingestion-pathway operational proof layer after the dose/PAR/field-monitoring spine.

## Main correction

The cube now separates public food/water/milk guidance from local ingestion-control closure. FDA, EPA, REMM, NRC, FEMA, and public agriculture materials can route, cap, demand, or reopen evidence. They cannot close local sampling, lab, embargo, release, alternate-water, producer/processor, or claims rows.

## Query route

`dose/field trigger -> sampling custody -> lab QA/QC -> DIL/PAG comparison -> embargo/hold/release order -> advisory -> producer/processor/retailer enforcement -> alternate water -> claims -> CAP/retest/verifier -> public claim gate`

## Compatibility

Generic ingestion and recovery tables remain present for compatibility. Rev0333 emergency-readiness queries route to the BVPS-specific sparse proof surfaces and validator.
