# Transportation / transit / paratransit mobility-continuity tests matrix

Generated for `rev0799` from `metadata/transportation_mobility_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `MOBILITY-01` Rider, trip purpose, and harm | Does the packet identify the rider or rider class, disability/language/fare status, trip purpose, deadline, and harm from missed travel before accepting a mobility row? | `424`, `425`, `426`, `489`, `508`, `509`, `520`, `521`, `523`, `524`, `535`, `577`, `948`, `949` | Open a rider-trip docket and downgrade aggregate rows to denominator evidence. |
| `MOBILITY-02` Stop, station, and pedestrian access | Are origin, destination, sidewalk, curb ramp, stop, shelter, lighting, station, elevator/escalator, weather, and transfer path checked? | `510`, `511`, `521`, `530`, `535`, `942`, `946`, `948`, `949` | Treat route or station rows as incomplete until the actual path is verified. |
| `MOBILITY-03` Schedule, GTFS, realtime, and disruption | Are scheduled service, GTFS, actual departures, cancellations, detours, headways, transfers, notices, and realtime feeds separated? | `535`, `577`, `849`, `930`, `931`, `946`, `948`, `949` | Do not treat GTFS or NTD service as live mobility without actual-operation evidence. |
| `MOBILITY-04` Vehicle, operator, boarding, and securement | Can vehicle assignment, lift/ramp/kneeling/securement, wheelchair space, operator staffing, pass-ups, crowding, and assistance be reconstructed? | `521`, `535`, `557`, `938`, `946`, `948`, `949` | Do not treat a vehicle count or trip as usable capacity until boarding and assistance evidence is joined. |
| `MOBILITY-05` Fare, credential, account, and refund continuity | Does the packet join fare product, reduced fare, cash/mobile/account state, transfer, fare cap, paratransit fare, blocked card, refund, and replacement? | `538`, `539`, `894`, `897`, `901`, `903`, `923`, `944`, `948`, `949` | Do not treat fare payment or credential as mobility until boarding, transfer, and remedy are shown. |
| `MOBILITY-06` ADA and paratransit delivery | Are eligibility, visitor status, reservation, pickup window, origin-to-destination assistance, PCA, no-show, subscription, vehicle fit, return trip, and complaint records joined? | `521`, `535`, `558`, `905`, `909`, `938`, `940`, `948`, `949` | Do not treat ADA eligibility or a service-area boundary as delivered paratransit. |
| `MOBILITY-07` Title VI, LEP, and service/fare equity | Are service standards, fare/service-change equity, LEP notice, public participation, affected corridors, demographics/ridership, and mitigation joined? | `530`, `535`, `555`, `559`, `577`, `601`, `948`, `949` | Do not treat a Title VI filing as equal access without affected-rider and mitigation evidence. |
| `MOBILITY-08` Safety, security, and emergency travel risk | Are PTASP, hazards, assaults, pedestrian conflicts, stop safety, operator safety, emergency communications, and incident learning tied to affected trips? | `502`, `510`, `511`, `535`, `911`, `946`, `947`, `948`, `949` | Do not treat a safety plan as a safe trip until local hazard and mitigation evidence is joined. |
| `MOBILITY-09` Asset, elevator, vehicle, and accessible alternative | Can TAM targets, asset inventories, elevator/escalator outages, vehicle condition, guideway/facility failures, shuttles, and accessible alternatives be tied to rider consequences? | `510`, `518`, `535`, `617`, `852`, `925`, `930`, `948`, `949` | Do not treat asset targets as reliability without disruption, alternate-route, and rider outcome evidence. |
| `MOBILITY-10` Rural, tribal, essential-service, and remedy tail | Are rural/tribal service, funding, staffing, vehicles, essential destinations, inter-provider handoffs, complaint routes, reimbursements, and corrective action joined? | `531`, `535`, `554`, `577`, `911`, `912`, `923`, `944`, `948`, `949` | Do not treat a grant program or complaint form as mobility until essential-trip and remedy evidence is joined. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `949` | `MOBILITY-01`, `MOBILITY-02`, `MOBILITY-03`, `MOBILITY-04`, `MOBILITY-05`, `MOBILITY-06`, `MOBILITY-07`, `MOBILITY-08`, `MOBILITY-09`, `MOBILITY-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 1 |
| `425` | 1 |
| `426` | 1 |
| `489` | 1 |
| `502` | 1 |
| `508` | 1 |
| `509` | 1 |
| `510` | 3 |
| `511` | 2 |
| `518` | 1 |
| `520` | 1 |
| `521` | 4 |
| `523` | 1 |
| `524` | 1 |
| `530` | 2 |
| `531` | 1 |
| `535` | 9 |
| `538` | 1 |
| `539` | 1 |
| `554` | 1 |
| `555` | 1 |
| `557` | 1 |
| `558` | 1 |
| `559` | 1 |
| `577` | 4 |
| `601` | 1 |
| `617` | 1 |
| `849` | 1 |
| `852` | 1 |
| `894` | 1 |
| `897` | 1 |
| `901` | 1 |
| `903` | 1 |
| `905` | 1 |
| `909` | 1 |
| `911` | 2 |
| `912` | 1 |
| `923` | 2 |
| `925` | 1 |
| `930` | 2 |
| `931` | 1 |
| `938` | 2 |
| `940` | 1 |
| `942` | 1 |
| `944` | 2 |
| `946` | 4 |
| `947` | 1 |
| `948` | 10 |
| `949` | 10 |

## Use rule

Run transportation/mobility tests whenever fixed-route transit, paratransit, GTFS, National Transit Map, NTD rows, fare systems, reduced-fare credentials, ADA, Title VI, PTASP, TAM, rural/tribal transit, service changes, disruptions, station/stop accessibility, shuttles, safety incidents, or complaints are cited as proof that people can travel. Separate rider, trip purpose, origin/destination, stop/station path, schedule/realtime, vehicle/operator, fare, paratransit, equity, safety, assets, rural/tribal access, remedy, and source-currentness before treating a scheduled trip, map, boarding, eligibility, plan, target, or complaint form as mobility.
