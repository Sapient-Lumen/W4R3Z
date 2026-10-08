# Watchlist / border / law-enforcement automation tests

Generated for `rev0799` from `metadata/watchlist_border_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `WB-01` Match-state decomposition | Can each alert distinguish nomination, dissemination, screening hit, biometric candidate, possible match, negative match, positive match, inconclusive match, officer confirmation, and action taken? | `856`, `857`, `863`, `874`, `915`, `916` | Do not allow watchlist, biometric, or risk matches to support action until match state and action state are separated. |
| `WB-02` Nomination, modification, and deletion evidence | Can the record show nomination source, sufficient identifying information, later modification, merge, deletion, and review clock without exposing protected intelligence unnecessarily? | `813`, `818`, `820`, `915`, `916` | Add a protected-evidence lane and source-owner review clock before treating list status as stable. |
| `WB-03` Screening-context boundary | Does the system distinguish travel screening, border inspection, visa or passport use, NCIC encounter, immigration enforcement, criminal investigation, mobile field capture, and partner screening? | `813`, `815`, `819`, `823`, `915`, `916` | Require a fresh context label and authority before porting a match result into a new use setting. |
| `WB-04` Officer reliance, training, and call-back control | Can operators and nonfederal users prove training, message wording, call-back instructions, positive / negative match handling, and prohibited reliance states? | `815`, `816`, `819`, `915`, `916` | Do not let downstream users act on alerts without tested training, message wording, and call-back protocols. |
| `WB-05` Redress and correction propagation | Does redress track outcome, correction / deletion / non-correction basis, and propagation to every system that caused the burden? | `821`, `857`, `915`, `916` | Treat redress as incomplete until correction propagation or protected non-correction is visible to an independent reviewer. |
| `WB-06` Biometric candidate lead limits | Are face, fingerprint, document-image, liveness, and gallery-search results labeled as candidate leads unless independently confirmed under the relevant authority? | `874`, `901`, `915`, `916` | Block coercive action based on biometric output until lead limits, manual confirmation, and legal authority are recorded. |
| `WB-07` Nonfederal user and partner governance | Are state, local, carrier, airport, foreign partner, contractor, and vendor users covered by training, dissemination, feedback, misuse, and correction rules? | `816`, `819`, `823`, `915`, `916` | Map downstream users and partner stores before scoring the federal system as governed. |
| `WB-08` Disclosure and safe-explanation lane | Where full disclosure is barred, does the system still provide safe reason classes, receipts, independent review, and correction evidence? | `818`, `821`, `857`, `915`, `916` | Replace blanket secrecy with safe explanation and independent-review surfaces. |
| `WB-09` AI inventory, privacy, and civil-rights evidence | Does each public AI or biometric inventory entry link to deployment authority, impact assessment, privacy / civil-rights review, monitoring protocol, incident handling, and redress readiness? | `410`, `857`, `876`, `910`, `915`, `916` | Do not treat inventory listing as authorization; require deployment-specific evidence. |
| `WB-10` Paired utility and harm metrics | Do public and oversight metrics pair security, identity, and throughput benefits with false hits, delays, secondary referrals, denials, redress outcomes, subgroup burden, and correction latency? | `816`, `817`, `915`, `916` | Publish paired utility / harm metrics before claiming watchlist or biometric screening repair. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `916` | `WB-01`, `WB-02`, `WB-03`, `WB-04`, `WB-05`, `WB-06`, `WB-07`, `WB-08`, `WB-09`, `WB-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `410` | 1 |
| `813` | 2 |
| `815` | 2 |
| `816` | 3 |
| `817` | 1 |
| `818` | 2 |
| `819` | 3 |
| `820` | 1 |
| `821` | 2 |
| `823` | 2 |
| `856` | 1 |
| `857` | 4 |
| `863` | 1 |
| `874` | 2 |
| `876` | 1 |
| `901` | 1 |
| `910` | 1 |
| `915` | 10 |
| `916` | 10 |

## Use rule

Use these tests when watchlists, border screening, biometric candidates, NCIC / nonfederal alerts, mobile field capture, DHS TRIP redress, or AI / facial-recognition inventories shape liberty, travel, immigration, police, or public-safety consequences. A match opens an inquiry lane; it does not itself prove identity, threat, authority, or remedy completion.
