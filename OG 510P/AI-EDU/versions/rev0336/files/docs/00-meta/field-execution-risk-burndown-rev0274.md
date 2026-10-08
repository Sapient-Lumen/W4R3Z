# Field execution risk burndown rev0274

| Risk | Before rev0274 | Rev0274 correction | Still not solved |
|---|---|---|---|
| forged workbench seed | A `PROCEED-STAGED` bundle could seed the workbench without revalidating its contact-clock source | seed creation revalidates the referenced scratch contact-status artifact and writes `revalidated_for_seed: true` | does not prove the owner reply is truthful |
| old seed reuse | router could open manual workbench from a weak or older local seed with only `NOT_ACCEPTED/live` fields | router now applies a shared workbench-seed integrity guard before manual-review routing | a valid seed still requires human workbench review |
| contact-detail leakage | seed provenance could grow toward route details | seed records only contact-status class/date fields and explicitly does not copy contact details | external send records remain outside the archive |
| doctrine drift | adding more audits could bury the operator path | change is enforced in tools and validators; this note exists only to document the narrow refactor | the external owner step is still pending |

## Immediate next executable path

Run the router. In a clean extract it should prepare a first-contact packet. After a human send/adaptation, record the send log, record the bounded sent clock, route any returned CSV through `owner-field-next`, let intake build the bundle, and then let the router create a source-clock-revalidated `NOT_ACCEPTED` workbench seed if and only if triage is `PROCEED-STAGED`.

## Refactor performed

The source-clock logic is no longer split across intake and seed routing. The shared guard now covers contact-status use by returned CSV intake and workbench seed routing, reducing the chance that one local tool accepts a weaker artifact than another.
