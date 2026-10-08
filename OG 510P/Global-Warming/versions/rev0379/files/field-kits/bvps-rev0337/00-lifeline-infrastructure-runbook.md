# BVPS rev0337 lifeline infrastructure runbook

Collect lifeline packets before allowing branch-level readiness claims.

Minimum capture set:

1. Energy/fuel: generator load served, run-test, transfer-test, usable fuel, supplier allocation, delivery route, and verifier.
2. Communications: cellular, EAS/WEA/IPAWS path, LMR repeater, satellite fallback, PSAP/CAD/call-center dependency, and field radio check.
3. Water/wastewater: water pressure/status, advisory state, alternate water, wastewater/decon-water disposition, WARN/mutual aid state.
4. Transportation/public works: route status, bridge/flood/debris state, traffic control, heavy equipment, tow/snow/pump resources.
5. Hazmat/industrial: facility status, non-radiological plume conflicts, mixed-hazard PPE and message conflicts.
6. Restoration priority: conflict board, signed priority assumptions, CAP/retest/verifier.

Do not put sensitive infrastructure details in public surrogates. Use hashed local/anonymized packets and redacted public-safe descriptions.
