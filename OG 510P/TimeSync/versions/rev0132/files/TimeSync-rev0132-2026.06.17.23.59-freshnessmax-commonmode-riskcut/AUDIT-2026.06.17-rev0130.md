# TimeSync rev0130 audit — shared bound and adapter equivalence

## Riskiest seam addressed

After rev0129, TimeSync had two NTP-family adapter surfaces, but each still computed the conservative interval with local helper code. That was the next high-risk drift point: chrony and ntpq could silently disagree for the same offset, root delay, root dispersion, rate error, collection instant, and evaluation instant.

## Refactor performed

Added `tools/ntp_bound.py` and routed the primary chrony evaluator, independent chrony observation evaluator, and ntpq evaluator through it. The module owns:

- exact RFC 3339 instant parsing to fractional seconds;
- rejection of evaluation before collection;
- negative-root-delay clamping;
- conservative root bound calculation;
- rate-error holdover growth;
- nanosecond floor/ceil interval endpoints.

## Executable audit added

Added `tools/adapter_equivalence.py` plus `tests/adapter-equivalence.yaml`. The harness feeds paired chrony and ntpq text fixtures that represent the same NTP-family state and fails if the emitted six-field state or P1 decision differs.

## Waste reduced

The duplicated arithmetic in three evaluator paths no longer has to be audited separately. The old helper wrappers remain only as adapter API compatibility shims; their bodies delegate to the shared module.

## What remains risky

- The equivalence case is sanitized replay, not live chronyd/ntpd capture.
- The ntpq parser covers a narrow readvar/peers dialect surface.
- Authentication posture is still reported-only unless cryptographic packet/session verification is added.
- Named UTC realization, leap-smear discovery, and PTP comparison remain open.
- The shared P1 lane table still has the legacy filename `p1-chrony-policy.json`; renaming should wait until enough downstream references can be updated without churn.
