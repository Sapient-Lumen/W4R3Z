# rev0122 audit note — chrony adapter/reference evaluator

The audit emphasis shifted from documentary completeness to an executable external boundary.

## Decisions

1. Use chrony first because its `tracking` output exposes offset, root delay, root dispersion, skew, stratum, and leap status in a compact operator-facing surface.
2. Use P1 first because it can be evaluated without pretending to prove regulated traceability or telecom/PTP behavior.
3. Use chrony's conservative clock-error bound and add skew-based replay growth.
4. Keep unsupported conditions in the explanation object instead of adding new TimeState fields.
5. Keep FT-0121 open because replay fixtures are not the same as live capture plus independent implementation comparison.

## Anti-bureaucracy constraint

No new evidence class, profile, transport adapter, or governance registry was added in this pass. The added surface is code plus fixtures.
