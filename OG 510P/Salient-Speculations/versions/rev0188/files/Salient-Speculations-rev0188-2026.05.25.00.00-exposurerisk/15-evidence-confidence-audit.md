# Evidence Confidence Audit

rev0182 recommended that the next revision audit evidence rather than merely add more dossiers. rev0183 follows that recommendation.

This file does not try to verify every citation in the archive. It creates a reusable evidence discipline: classify the kind of signal, the currentness of the signal, the path from signal to thesis, and what would make the dossier overconfident.

## Evidence grades

| Grade | Meaning | Editorial action |
|---|---|---|
| E4 — enforcement active | Law, procurement, platform rules, registry status, or supervisory process already gates money, access, permission, liability, or ranking. | Treat as near-term infrastructure; sharpen operational states and failure modes. |
| E3 — artifact live | Named artifacts, standards, registries, credentials, packets, APIs, or certification workflows exist, but enforcement is uneven. | Track adoption and hardening paths. |
| E2 — signal cluster | Multiple credible signals point in the direction, but the artifact is still diffuse. | Keep as dossier only if the bottleneck is clearly named. |
| E1 — analogy-backed | The pattern is plausible by analogy to stronger domains, but direct evidence is weak. | Keep speculative and add falsifiers. |
| E0 — evocative | Interesting but under-sourced or too broad. | Return to seed bank or require new sources. |

## 24-dossier audit sample

| Dossier | Evidence grade | Main signal | Overconfidence risk | Next verification move |
|---|---:|---|---|---|
| `digital-product / objects-acquire-governed-biographies` family | E4 | ESPR and DPP framework [S1504] | treating passports as uniformly adopted before sector rules mature | track delegated acts, service-provider rules, resolver governance, and customs integration |
| `repair-right-evidence-becomes-consumer-infrastructure` | E3/E4 | EU repair directive timing [S1494] | assuming repair records become machine-readable by default | watch national transposition and warranty/resale integration |
| `small-supplier-evidence-brokers` | E3 | EUDR tooling and smallholder support [S1512][S1513] | overgeneralizing from deforestation compliance to all proof regimes | watch actual buyer onboarding and public-tool uptake |
| `grid-connection-queue-position` | E4 | interconnection queues and FERC reforms [S1495][S1496] | making data-center pressure the only cause | track queue deposits, readiness screens, transferability, and curtailment contracts |
| `model-documentation-packets` | E3/E4 | EU AI Act GPAI documentation and Code of Practice [S1498][S1499] | assuming clean standardization across model types | watch procurement templates and open-model/fork documentation |
| `incident-report-routing` | E4 | SEC, CIRCIA, DORA, CRA reporting surfaces [S1501][S1502][S1483][S1482] | ignoring legal privilege and materiality discretion | watch multi-recipient reporting portals and correction-afterlife rules |
| `NVD status / vulnerability applicability` family | E4 | NIST NVD risk-based enrichment shift [S1480] | treating NVD as the only source of truth | watch vendor VEX, KEV, EPSS, internal applicability, and scanner scoreboards |
| `public-proof-profile-registries` | E2/E3 | VC/BBS selective disclosure and EUDI direction [S1488][S1489][S1492][S1493] | assuming public sufficiency profiles emerge quickly | watch wallet conformance profiles and sector verifier rules |
| `graph-poisoning` | E2/E3 | CISA supply-chain alerts, OWASP, MITRE ATLAS [S1506][S1507][S1508][S1509] | broadening too far from software graphs into all governance graphs | require edge-level evidence examples before expanding further |
| `resolver-capture` | E3 | ESPR passport data carriers/resolvers [S1504] and GS1-style lookup logic [S1491] | assuming resolver capture before resolver markets exist | watch DPP service-provider delegation and redirect custody |
| `informal-market-refuges` | E2 | ID4D grievance/exclusion and smallholder proof burden [S1510][S1511][S1512][S1513] | romanticizing informality or treating evasion as always illegitimate | gather sector-specific displacement examples |
| `redaction-boundary-ledgers` | E2/E3 | AI assurance and selective disclosure signals [S1488][S1489][S1531] | overclaiming before audit redaction practice stabilizes | watch regulator acceptance of redacted model evidence |
| `recall-state-propagation` | E3 | Safety Gate and GlobalRecalls [S1514][S1515] | assuming recall state binds to DPP/resale workflows soon | watch marketplace and repair-platform recall checks |
| `cryptographic-agility-registries` | E3 | NIST PQC standards and CISA category planning [S1516][S1517][S1518][S1530] | turning PQC guidance into mandatory procurement too early | watch buyer questionnaires, insurance, and federal procurement requirements |
| `notified-body-queue-position` | E4 | EC notified-body materials and EUDAMED certificate states [S1525][S1526][S1527] | overgeneralizing medical-device assessor bottlenecks to all domains | track actual queue metrics and certificate-state usage in procurement |
| `delegated-ai-agent-authority-logs` | E2/E3 | agent primitives, FTC impersonation rule, NIST AI RMF [S1528][S1529][S1531] | assuming agents will be accepted as counterparties soon | watch merchant terms, signed action receipts, and consumer complaints |
| `data-space-access-rules` | E3 | DGA and common European data spaces [S1523][S1524] | assuming data spaces harden into exclusionary borders rather than voluntary consortia | watch access-denial disputes and trusted-intermediary registries |
| `provenance-nonparticipation-labels` | E2/E3 | C2PA and AI Act transparency timing [S1519][S1520][S1521][S1522] | treating provenance absence as settled semantics | watch platform UI and legal guidance on AI-output marking |
| `authority-check-middleware` | E3 | wallet and delegated-identity signals [S1492][S1493] | underplaying offline/fallback need | watch revocation, outage, and grievance metrics |
| `source-witness-nonresponse` | E2 | incident and packet governance analogies | overclaiming without live source-witness default clauses | search contracts and incident response playbooks |
| `recipient-graph-privacy-proofs` | E2/E3 | selective disclosure standards [S1488][S1489] | assuming graph privacy gets funded | watch procurement privacy clauses and audit escrow designs |
| `compliance-object-forgery` | E3 | DPP, EUDR, CRA, VC, C2PA [S1482][S1484][S1485][S1488][S1503] | treating forgery as organized before cases accumulate | track forged QR/passport/attestation incidents |
| `data-minimization-proofs` | E3 | wallet/selective-disclosure and Data Act signals [S1481][S1488][S1489] | assuming minimization wins against buyer overreach | watch verifier policies and over-collection enforcement |
| `non-reliance-packet-states` | E2 | packet lifecycle logic | insufficient outside examples | watch public status vocabularies with reliance-limited or withdrawn states |

## Editorial readout

The archive is strongest where evidence has already reached E3/E4: product biographies, interconnection queues, incident reporting, medical-device conformity, cybersecurity status systems, and formal AI documentation.

The archive is most speculative but still promising where it names second-order governance artifacts: proof-profile registries, recipient-graph privacy proofs, source-witness nonresponse defaults, provenance-nonparticipation labels, and delegated-agent authority logs.

The next audit should downgrade or consolidate dossiers that remain E1/E0 after two more revisions without acquiring a named artifact or enforcement surface.
