# Remedy-lifecycle refactor report

rev0185 performs a focused audit/refactor of the appeal, grievance, dispute, stay, correction, and administrative-repair cluster.

## Why this refactor was needed

The cube had accumulated a strong but diffuse remedy family:

- appeal-stay labels;
- identity-match appeals;
- scoreboard appeal workflows;
- correction-materiality thresholds;
- split/merge correction notices;
- source-witness nonresponse defaults;
- cross-registry record repair;
- human fallback;
- remedy budgets;
- complaint telemetry;
- restriction objects;
- non-reliance states.

These were not wrong. But the cluster was beginning to repeat the same implicit lifecycle without naming it. rev0185 normalizes that lifecycle.

## Audit result

- Existing dossiers tagged with `refactor_cluster: remedy-lifecycle`: **26**.
- New dossiers promoted by the audit: **5**.
- New remedy-specific index artifacts: **4**.
- Primary consolidation risk: overproducing named appeal artifacts without specifying clocks, standing, interim effect, and propagation.

## What changed in metadata

Tagged files now carry:

- `refactor_cluster: remedy-lifecycle`;
- `remedy_role`;
- `remedy_stage`;
- `state_family: remedy`;
- `consolidation_status`.

The goal is not to flatten the archive. It is to show which dossiers remain standalone mechanisms and which should become substates inside `22-dispute-and-remedy-lifecycle.md`.

## Standalone mechanisms after audit

The following should remain standalone because they define reusable mechanisms:

- appeal-stay labels;
- correction-materiality thresholds;
- identity-match appeals;
- machine-readable restriction objects;
- non-reliance packet states;
- source-witness nonresponse defaults;
- remedy-clock orchestration;
- adverse-action explanation packets;
- standing and representation proofs;
- remedy-abuse rate limits;
- human-review capacity.

## Likely substates or bridge dossiers

The following should be watched for consolidation:

- gate-expiry disputes;
- re-review trigger grammars;
- proceed-before-convergence waivers;
- escalation-path liveness checks;
- delegate propagation delays;
- complaint telemetry;
- remedy budgets.

These are useful, but future revisions should avoid multiplying them unless they add a new domain or hard enforcement surface.

## Next audit target

The next overloaded part of the cube is likely **authority and delegation**: delegated representation, authority-check middleware, authority freshness, delegate-change propagation, agent authority logs, safeguarded delegation, and standing proofs. That family now touches identity, AI agents, public benefits, healthcare, procurement, and consumer redress.
