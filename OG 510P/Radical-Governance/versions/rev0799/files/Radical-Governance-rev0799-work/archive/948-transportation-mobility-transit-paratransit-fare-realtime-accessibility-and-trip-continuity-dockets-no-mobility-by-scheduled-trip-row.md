# 948 — Transportation, mobility, transit, paratransit, fare, realtime, accessibility, and trip-continuity dockets: no mobility by scheduled trip row

## One-line thesis

Mobility continuity is not a scheduled trip, GTFS feed, NTD boarding, route map, fare product, elevator status, paratransit eligibility row, call-center reservation, safety plan, Title VI program, or asset target. A rider can appear inside a valid transportation system while the stop, sidewalk, elevator, vehicle, operator, fare media, paratransit pickup, transfer, language access, safety condition, rural/tribal connection, or complaint remedy is broken. The archive should join person, origin/destination, route, stop, vehicle, fare, accessibility, safety, realtime, disruption, and remedy records before treating a trip row as mobility.

## Why this matters

The archive already had transport and logistics by scope, a metropolitan transport authority case, emergency-response continuity, disability access, food, health, housing, custody, education, water, and long-term care. It still lacked a direct rider-level mobility packet. That was a dangerous gap because many other rights assume movement: medical appointments, school attendance, court appearances, food access, work, shelter, voting, family visits, evacuation, and crisis response all fail if the transportation chain breaks.

The governing repair phrase is **no mobility by scheduled trip row**.

## Pattern pack

- **No mobility by scheduled trip row.** A scheduled trip, GTFS feed, or NTD service row is denominator evidence, not proof that a person could travel.
- **No access by route map.** A route line does not prove reachable stops, sidewalks, elevators, boarding, fares, transfers, language access, safety, or operating reliability.
- **No paratransit by eligibility.** Eligibility approval does not prove booking, pickup window, no-show fairness, same-day disruption, vehicle fit, driver assistance, return trip, or complaint repair.
- **No equity by Title VI file.** A Title VI program, service standard, or equity analysis does not prove that service changes, fares, headways, stops, and transfers worked for affected riders.
- **No reliability by asset target.** State-of-good-repair and asset-management measures must be joined to breakdowns, cancellations, crowding, elevator outages, and rider consequences.
- **No safety by agency plan.** PTASP and safety-plan evidence must be joined to actual hazards, assaults, pedestrian conflicts, operator availability, and incident learning.
- **No trip planning by open data.** GTFS and National Transit Map rows support analysis; they are not realtime navigation, disruption, fare, crowding, or accessibility proof.
- **No mobility by fare payment.** A card, pass, wallet, fare-capping row, or reduced-fare credential cannot prove boarding, transfer, paratransit payment, refund, or account repair.

## Continuity docket

| Ledger | What it must preserve | Bad shortcut |
|---|---|---|
| Person and trip purpose | Rider, companion/PCA, disability, language, age, income, custody/care/shelter status, trip purpose, appointment/deadline, and risk if missed. | Treating boardings as access. |
| Origin, stop, and path | Origin, destination, sidewalks, curb ramps, stop location, shelter, lighting, snow/heat, elevators/escalators, and pedestrian transfer path. | Treating a route line as reachable service. |
| Schedule and realtime | Scheduled service, headways, actual departures, cancellations, detours, realtime feed, customer notices, and missed connections. | Treating GTFS as live service. |
| Vehicle and operator | Vehicle availability, accessible features, securement, kneeling/lift/ramp, crowding, operator staffing, operator instructions, and pass-up records. | Treating vehicle count as usable capacity. |
| Fare and credential | Fare product, reduced fare, cash/access, account lock, mobile wallet, card replacement, transfer rules, paratransit fare, and refund/remedy. | Treating payment as travel. |
| ADA and paratransit | Eligibility, visitor status, reservation, pickup window, origin-to-destination assistance, PCA, no-show, subscription, will-call, return trip, and complaint. | Treating eligibility as delivered paratransit. |
| Title VI / equity | Service standards, fare/service-change equity, LEP notice, affected riders, census/ridership denominators, and mitigation. | Treating program filing as equal access. |
| Safety and security | PTASP, assaults, pedestrian/bus conflicts, stops, lighting, operator safety, emergency communications, and incident learning. | Treating safety plan as safe trip. |
| Asset and disruption | State of good repair, maintenance, elevators, escalators, vehicles, track/guideway, closures, bridge/shuttle buses, and alternate accessible routes. | Treating asset target as reliability. |
| Remedy and after-action | ADA/Title VI/local complaint, service guarantee, reimbursement, missed appointment harm, public dashboard, and corrective action. | Treating aggregate performance as repair. |

## Minimum joined record

A serious mobility-continuity packet should contain at least:

1. **Rider/trip file.** Person or rider class, disability/access need, language, fare eligibility, companion/PCA, appointment/deadline, and harm from missed travel.
2. **Origin/destination file.** Address, stop/station, pedestrian path, curb ramps, elevator/escalator, shelter, lighting, weather, and safe approach.
3. **Fixed-route service file.** Schedule, GTFS, actual service, cancellation, detour, headway, missed connection, crowding, and customer notice.
4. **Vehicle/operator file.** Vehicle assignment, lift/ramp/kneeling/securement state, operator availability, pass-up, wheelchair space, assistance, and incident logs.
5. **Fare file.** Product, reduced-fare credential, cash/mobile/account status, transfer, fare cap, paratransit fare, blocked card, refund, and replacement.
6. **ADA/paratransit file.** Eligibility, reservation, trip negotiation, pickup/dropoff, on-time window, origin-to-destination assistance, no-show, visitor rules, and complaint.
7. **Equity/language file.** Title VI service standards, fare/service-change analysis, LEP notice, rider demographics, affected corridors, mitigation, and public participation.
8. **Safety/disruption file.** PTASP hazards, assaults, collisions, emergency response, service disruption, shuttles, accessible alternatives, and incident learning.
9. **Rural/tribal/funding file.** Service area, funding route, staffing, vehicle age/condition, grant constraints, rural/tribal provider coordination, and access to essential services.
10. **Source-currentness boundary.** Mark whether each source is national reporting, map/feed, rule/guidance, plan, complaint route, performance data, local operational record, or rider outcome proof.

## Upgrade triggers

Route to the full mobility continuity docket when any of these appear:

- a route, GTFS, NTD, boarding, paratransit, fare, asset, safety, Title VI, or ADA row is cited as proof that people could travel;
- a missed trip can affect medical care, work, school, voting, food access, court, shelter, family contact, evacuation, or benefits;
- disability, language, rural/tribal geography, age, income, custody/care setting, heat/smoke/snow, or station accessibility changes the travel risk;
- a service change, fare change, strike, vehicle shortage, elevator outage, detour, shuttle, cyber outage, payment outage, or staffing shortage can strand riders;
- a complaint, civil-rights route, performance dashboard, or NTD metric could hide rider-level harm.

## Downshift conditions

A lighter treatment is acceptable only when the source is used as pure national transit background and no rider, trip, missed deadline, service change, fare, paratransit, disability, safety, rural/tribal, or remedy consequence is live. Once a person or class may lose practical mobility, open the full packet.

## Failure modes

- **No mobility by scheduled trip row:** service appears on a schedule but does not operate or cannot be reached.
- **No access by route map:** the map shows a route but stop approach, transfer, fare, or vehicle access fails.
- **No paratransit by eligibility:** a rider is approved but cannot book, ride, return, or repair a trip.
- **No equity by Title VI file:** a service/fare change is filed but affected riders lose access.
- **No reliability by asset target:** assets meet a target while elevator, vehicle, or guideway failures strand riders.
- **No safety by PTASP:** a plan exists while assaults, conflicts, or stops remain dangerous.
- **No trip planning by GTFS:** open data exists but does not include realtime disruption, accessibility, or fares.
- **No remedy by complaint form:** the rider can complain but the missed trip, fare loss, or appointment harm is not repaired.

## Audit questions

- Which rider, trip, appointment, deadline, route, stop, station, fare account, or paratransit booking is at risk?
- Is the cited source a schedule, map, GTFS feed, NTD statistic, ADA rule, Title VI filing, safety plan, asset target, complaint record, or live operational log?
- Can the stop/station be reached by the person with the actual sidewalk, elevator, weather, lighting, and safety conditions?
- Did the scheduled service actually operate, arrive, board the person, transfer, and complete the trip?
- Did the rider have usable fare media, reduced-fare authority, cash/mobile fallback, paratransit payment, and refund/remedy if payment failed?
- For paratransit, did eligibility, booking, pickup, assistance, vehicle fit, no-show policy, return trip, and complaint remedy all work?
- Did Title VI, ADA, language, rural/tribal, disability, age, income, or safety analysis reach affected riders rather than only the filing shelf?
- What local operational, complaint, incident, and rider-outcome evidence is needed before mobility can be scored as delivered?

## Source posture

Use FTA NTD, BTS National Transit Map, FTA ADA, Title VI, PTASP, TAM, and GAO rural/tribal and asset-management sources as official evidence lanes for national reporting, rules, data architecture, and oversight concerns. Do not treat any one source as live trip proof without local agency service records, GTFS-realtime/AVL/APC where available, stop/station access records, fare-account records, ADA/paratransit logs, complaints, and rider outcome evidence.
