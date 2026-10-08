# OPEN QUESTIONS

## Identity questions

1. What is TimeSync, exactly?
2. What is the narrowest useful object it could define?
3. Is the core deliverable a protocol, an API, a state model, a profile, or a control plane?

## Scope questions

4. What does "global scale" mean here:
   - internet scale,
   - cross-sector critical infrastructure,
   - multinational federation,
   - or simply many-region, many-source systems?
5. Should the project include UTC/civil-time governance edges, or treat them as external inputs?

## Technical questions

6. What is the smallest legitimate "time state" object?
7. How should uncertainty be represented?
8. What source-diversity properties actually matter most?
9. How should clients distinguish authenticity, freshness, and bounded error?
10. What should a system expose when it is in holdover or degraded mode?

## Governance questions

11. Who is allowed to assert, override, or quarantine time authority?
12. What must be public and standardized, and what can remain implementation-specific?
13. How should downstream systems bind policy to timing confidence?

## Design-process questions

14. Which contradictions deserve a dedicated ledger immediately?
15. What empirical incidents and real deployments should anchor the next revision?
