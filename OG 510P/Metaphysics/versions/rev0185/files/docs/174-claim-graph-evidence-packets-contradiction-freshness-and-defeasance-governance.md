# 174. Claim Graph, Evidence Packets, Contradiction, Freshness, and Defeasance Governance

## Core thesis

A claim can be locally validated, queryable, traceable, and fixture-pressured while still hiding the most important question: **which exact assertion is warranted by which evidence, under what freshness window, against which contradiction state, and with what downstream withdrawal rule if the warrant is defeated?**

Rev0167 made release changes harder to launder by adding invariants, traceability rows, migration/deprecation semantics, impact rows, and representative negative fixtures. Rev0168 adds the next layer: claim graph governance, evidence-packet indexing, contradiction-state recording, freshness-window policy, and defeasance propagation. The goal is not to make the archive more confident. The goal is to make confidence easier to retract.

## What this release adds

Rev0168 adds five control surfaces:

1. `CLAIM_GRAPH.yml` names local claim nodes, their commitment status, evidence packets, source artifacts, freshness policies, and downstream dependence edges.
2. `EVIDENCE_PACKET_INDEX.yml` names local evidence packets and separates local validation output, current package artifacts, claim-language rows, provenance rows, and external-analogy notes from stronger source-current or domain-authoritative evidence.
3. `CONTRADICTION_LEDGER.yml` records incompatible claim pairs, forbidden upgrade claims, unresolved tensions, and the disposition needed before a claim may be repeated.
4. `FRESHNESS_POLICY.yml` defines local freshness windows and review triggers for validation reports, evidence packets, public-use claims, source-dependent claims, and external analogies.
5. `DEFEASANCE_PROPAGATION.yml` states what must be downgraded, blocked, or re-reviewed when a claim node, evidence packet, source artifact, status token, query result, or freshness policy is defeated.

These artifacts are local governance artifacts. They are not nanopublications, RDF assertions, a public knowledge graph, an evidence ontology deployment, a citation-typing ontology, a source-watch service, an annotation server, a legal/public safety case, or a claim of factual/domain authority.

## Claim-node rule

A claim node is not a paragraph. It must have a stable claim identifier, statement, claim kind, commitment status, evidence packet links, source artifacts, freshness policy, allowed language, forbidden language, and a defeasance profile. Claim nodes may summarize package-local facts, but they must not turn local structural evidence into source currency, external audit, public interoperability, or operational authority.

## Evidence-packet rule

An evidence packet is not simply a citation or a file path. It must state what kind of evidence it is, which claim it supports or constrains, which local artifacts are inspected, what freshness rule applies, which checks were run, what the packet cannot support, and what withdrawal trigger would make the packet unsafe to cite.

## Contradiction rule

Contradiction governance is not only about two ordinary claims disagreeing. The archive must also record contradictions between allowed local claims and tempting upgrade claims. For example, “the validator passed locally” contradicts “the archive has independent external QA.” The former may be true within this package; the latter remains forbidden unless independent evidence is added.

## Freshness rule

A source-dependent or public-use claim must not inherit indefinite life from a passing release. Rev0168 therefore distinguishes local package-current claims, source-current claims, external-analogy claims, public-use claims, and operational-reliance claims. Most current claims here are package-current only: they are fresh relative to the local package bytes and validator run, not relative to the outside world.

## Defeasance rule

A defeated claim must propagate. If a schema report is wrong, cube observations that depend on it must be downgraded. If a query regression fails, claims about queryability must be withdrawn. If evidence goes stale, source-current or public-use language must be blocked. If an external analogy is misread as compliance, affected front-door language must be repaired.

## Allowed claims after rev0168

The package may claim that it includes a local claim graph, local evidence-packet index, local contradiction ledger, local freshness policy, local defeasance-propagation rules, a local claim/evidence checker, current-release claim/evidence reports, and fresh-extraction validation that checks representative claim/evidence integrity.

## Forbidden upgrade claims

The package must not claim public nanopublication, RDF publication, external evidence ontology conformance, public knowledge graph publication, source-watch automation, independent fact-checking, current external source review, domain authority, legal/medical/financial/engineering guidance, public QA, operational readiness, or automatic truth maintenance.

## Open debt retained

- Claim nodes cover current governance claims only, not all metaphysical theses in the archive.
- Evidence packets are package-local and curated; they are not independent source reviews.
- Contradiction rows are representative, not exhaustive.
- Freshness windows are local policy windows, not automated watches.
- Defeasance propagation is checkable for named rows, not a complete truth-maintenance system.
- External analogues are design pressure only.

## Next likely layer

The next durable layer should be release-gate policy and acceptance-criteria governance: executable gates, required approvals, gate exceptions, risk acceptance signoff, policy-as-code boundaries, and red/amber/green release decisions. Rev0168 prepares for that by making release claims, evidence, contradictions, freshness, and defeat states explicit enough to feed a stricter gate.
