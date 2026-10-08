# Software / cyber incident public-service continuity tests matrix

Generated for `rev0799` from `metadata/software_cyber_continuity_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `SC-01` Critical public-function map | Can the packet name the claims, payments, diagnostics, appointments, records, benefits, notices, filings, appeals, or access functions that would fail if the cyber/software dependency failed? | `544`, `621`, `692`, `848`, `859`, `867`, `884`, `901`, `923`, `930`, `931` | Add a public-function map tying each dependency to concrete service outcomes before scoring resilience. |
| `SC-02` Runtime provenance and SBOM boundary | Does the packet distinguish procured product, deployed version, component list, hosting path, managed-service role, and live runtime exposure? | `443`, `444`, `452`, `621`, `692`, `792`, `917`, `930`, `931` | Do not treat product name, SBOM, or attestation as continuity evidence until it is joined to deployed runtime exposure. |
| `SC-03` Supplier, identity, and privileged-access docket | Are vendor accounts, service accounts, administrative consoles, MFA posture, logging, break-glass roles, and revocation routes documented? | `428`, `443`, `444`, `621`, `692`, `848`, `884`, `917`, `930`, `931` | Open a privileged-access docket and require containment authority before accepting supplier-security claims. |
| `SC-04` Vulnerability, KEV, and exception triage | Does the packet join known exploited vulnerability status, patch timing, exception approvals, compensating controls, and public-function blast radius? | `443`, `452`, `621`, `692`, `848`, `867`, `884`, `887`, `917`, `930`, `931` | Attach every unresolved high-risk exposure to the affected public function and degraded-mode plan. |
| `SC-05` Degraded-mode continuity proof | Did a manual, alternate, paper, emergency, mutual-aid, or substitute route actually keep service running for affected people? | `544`, `621`, `692`, `856`, `857`, `859`, `867`, `884`, `901`, `917`, `923`, `930`, `931` | Treat restoration as incomplete until degraded-mode service and reconciliation are proven. |
| `SC-06` Incident command and reporting clock | Are detection, containment, agency notification, contractor notification, public update, breach notice, regulator report, and ransom decision clocks recorded? | `443`, `544`, `621`, `692`, `792`, `848`, `859`, `867`, `884`, `917`, `930`, `931` | Create a timeline that separates incident command, legal notification, and affected-service duties. |
| `SC-07` Data-exposure and downstream-fraud tail | Does the packet track exposed data classes, affected-party notice, credit/fraud risk, record correction, and downstream screening or denial risks? | `544`, `621`, `692`, `792`, `859`, `867`, `884`, `887`, `901`, `917`, `930`, `931` | Do not close the incident on breach count alone; add the downstream data-rights and repair tail. |
| `SC-08` Service, payment, clinical, or access outcome | Does recovery evidence show that the affected service actually reached people after the incident? | `544`, `621`, `692`, `856`, `857`, `859`, `867`, `884`, `901`, `917`, `923`, `930`, `931` | Replace uptime-only recovery with outcome evidence for the affected public function. |
| `SC-09` Backup, rebuild, restoration, and integrity proof | Were backups, rebuild paths, integrity checks, restored records, and reconciliation tested against the actual incident? | `443`, `444`, `544`, `621`, `692`, `859`, `867`, `884`, `917`, `923`, `930`, `931` | Keep recovery open until rebuilt systems, records, and queues are reconciled, not just online. |
| `SC-10` Post-incident contract and concentration consequence | Did the incident produce contract, exit-right, supplier-concentration, architecture, logging, identity, or assurance changes? | `443`, `444`, `452`, `621`, `692`, `792`, `848`, `884`, `887`, `917`, `923`, `930`, `931` | Do not accept lessons learned unless they change procurement, architecture, identity, observability, or concentration risk. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `931` | `SC-01`, `SC-02`, `SC-03`, `SC-04`, `SC-05`, `SC-06`, `SC-07`, `SC-08`, `SC-09`, `SC-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `428` | 1 |
| `443` | 6 |
| `444` | 4 |
| `452` | 3 |
| `544` | 6 |
| `621` | 10 |
| `692` | 10 |
| `792` | 4 |
| `848` | 5 |
| `856` | 2 |
| `857` | 2 |
| `859` | 6 |
| `867` | 7 |
| `884` | 9 |
| `887` | 3 |
| `901` | 4 |
| `917` | 9 |
| `923` | 5 |
| `930` | 10 |
| `931` | 10 |

## Use rule

Use when a cyber incident, ransomware event, software supply-chain assurance claim, SBOM, secure-software attestation, hardware/software inventory, privileged supplier access, cloud/runtime dependency, KEV/vulnerability exposure, breach notification, degraded mode, public-service outage, payment/clinical/access disruption, recovery statement, or supplier concentration risk can affect service continuity.
