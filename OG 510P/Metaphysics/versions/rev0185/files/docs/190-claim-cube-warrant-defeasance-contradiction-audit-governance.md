# 190 — ClaimCube warrant, defeasance, contradiction, and audit governance (rev0184)

This layer refactors the local ClaimCube from a broad list of allowed and forbidden claim-language rows into a more inspectable claim-observation, claim-relation, and claim-audit surface.

The motivating defect in the previous package was not row scarcity. The ClaimCube already had many observations. The defect was relational shallowness: allowed language, forbidden upgrades, claim-graph nodes, evidence packets, contradiction states, and defeasance rules were present in the archive, but their links were not first-class cube observations. A reader could see that claims were bounded, but could not query how a claim was supported, blocked, withdrawn, or audited.

## Local refactor

rev0184 adds and checks:

- `CLAIM_OBSERVATION_INDEX.yml`
- `CLAIM_RELATION_MAP.yml`
- `CLAIM_AUDIT_LEDGER.yml`
- `CUBE/observations/claims.yml`
- `CUBE/observations/claim_relations.yml`
- `CUBE/observations/claim_audit.yml`
- `tools/generate_claim_observations.py`
- `tools/check_claim_cube_refactor.py`
- `tools/check_claim_audit.py`

The refactor distinguishes at least these claim surfaces:

1. current-record allowed local claims;
2. current-record forbidden upgrade claims;
3. claim-language-ledger allowed clusters;
4. claim-language-ledger forbidden clusters;
5. claim-graph nodes;
6. current-release allowed and forbidden claims;
7. relation rows connecting claims to evidence packets, source artifacts, contradiction states, and defeasance rules;
8. local audit rows describing row counts, duplicate IDs, coverage of graph nodes, and retained debt.

## Allowed claim

The package may say that rev0184 locally normalizes ClaimCube observations, adds claim relation and claim audit observations, and checks representative claim/evidence/contradiction/defeasance coverage.

## Forbidden upgrades

The package may not infer:

- claim truth;
- external philosophical review;
- external audit;
- complete claim graph coverage;
- complete source-to-claim warrant scoring;
- automatic truth maintenance;
- contradiction completeness;
- defeasance completeness;
- public RDF/SHACL claim graph publication;
- legal, accessibility, source-currentness, or public-support conformance.

## Why this matters

The archive has become good at warning against overclaiming. This layer makes those warnings more queryable. A blocked claim should not be only a phrase in a ledger; it should become an observation that can be counted, related to source artifacts, related to evidence, and inspected as part of the cube.

## Remaining debt

The refactor is still local YAML. The claim graph remains representative. The relation map records structural links, not philosophical truth. Evidence packets remain package-local. No external reviewer has certified that the allowed and forbidden claim boundaries are complete, fair, or semantically adequate.
