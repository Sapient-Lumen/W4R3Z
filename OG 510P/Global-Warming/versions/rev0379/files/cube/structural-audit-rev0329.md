
# Structural Audit rev0329

## Highest-risk gap addressed

Rev0328 made receipt/geofence/nonreceipt first-class. Rev0329 addresses the next operational failure: messages can be received but misunderstood, ignored, contradicted by rumors, or acted on incorrectly.

## Main model correction

The emergency path now separates receipt, comprehension, intended action, observed action, rumor/call-center correction, CAP/retest, independent verification, and public claim gating.

## Refactor finding

The base package had a stale root-level duplicate validation report for rev0328 even though the cube-level report passed. Rev0329 records and corrects this. The source canonicalization map also no longer collapses all blank URLs into one source cluster.

## Compatibility

Legacy crossproduct and prior rev files are retained for compatibility. Rev0329 adds sparse operational proof surfaces; it does not rewrite old consumer contracts.
