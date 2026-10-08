# 946 — Emergency communications, 911, EMS, 988, alerting, and response continuity dockets: NG911, PSAP, location, dispatch, transport, and no rescue by dispatch row

## One-line thesis

Emergency response continuity is not a 911 call row, PSAP answer statistic, NG911 migration milestone, CAD incident, radio transmission, wireless location estimate, ambulance dispatch, NEMSIS record, 988 contact metric, IPAWS alert, WEA/EAS test, or incident-closed code. A person can appear inside a valid emergency communications system while call routing, location, language, disability access, dispatch, responder safety, EMS handoff, behavioral-crisis routing, public warning, outage fallback, and after-action repair are broken. The archive should join call, location, dispatch, unit, clinical, crisis, alert, network, accessibility, and outcome records before treating a dispatch row as rescue.

## Why this matters

The archive already had public safety by scope, disaster assistance, water, utilities, cyber continuity, custody, health benefits, food, special education, and long-term care. It still lacked a direct operational emergency-response packet. That was a dangerous gap because 911, EMS, 988, IPAWS, WEA, EAS, communications networks, radio systems, dispatch centers, and receiving hospitals are shared rescue waists: many services appear only after the emergency channel works.

The governing repair phrase is **no rescue by dispatch row**.

## Pattern pack

- **No rescue by dispatch row.** A CAD, call, or dispatch status is denominator evidence, not proof that help reached the person.
- **No 911 by call connected.** Connection to 911 does not prove correct PSAP, location, language, call-back, text/RTT handling, or outage fallback.
- **No NG911 by migration milestone.** NG911 self-reports and roadmaps do not prove live interoperability, cyber resilience, GIS accuracy, transfer, or degraded-mode operation.
- **No location by coordinate.** Wireless, z-axis, dispatchable-location, or location-based-routing data must be checked against what responders actually received and used.
- **No EMS by incident record.** A NEMSIS or patient-care record proves a data lane, not necessarily response time, unit availability, treatment, transport, diversion, or clinical handoff.
- **No crisis care by 988 answer.** A 988 answer rate or contact count does not prove local crisis response, safety planning, mobile crisis, warm transfer, language/deaf access, or follow-up.
- **No public warning by alert sent.** IPAWS/WEA/EAS authorization, test, or message transmission does not prove receipt, comprehension, accessibility, translation, or protective action.
- **No resilience by certification.** 911 reliability certifications, monitoring, backups, or alerts must be joined to actual outage detection, PSAP notice, reroute, and restoration evidence.

## Continuity docket

| Ledger | What it must preserve | Bad shortcut |
|---|---|---|
| Caller/person and channel | Caller, victim, bystander, language, disability, phone/text/RTT/video/TDD, location uncertainty, callback, and consent/safety constraints. | Treating a call row as a person rescued. |
| Routing and PSAP answer | Correct PSAP, transfer, abandoned call, busy/overflow, text-to-911, 988/911 boundary, tribal/rural edge, and queue clocks. | Treating answer rate as dispatch sufficiency. |
| Location and GIS | Civic address, wireless coordinate, z-axis, dispatchable location, GIS layer, landmark, route, and responder-visible location. | Treating a coordinate as actionable scene location. |
| Dispatch/CAD/radio | Event type, priority, unit recommendation, unit assignment, radio/MDT data, mutual aid, and status updates. | Treating CAD disposition as response delivered. |
| Unit availability and scene response | Unit availability, staffing, travel, staging, safety, access, scene arrival, and handoff to fire/police/EMS or crisis team. | Treating dispatch time as arrival. |
| EMS clinical and transport | Triage, treatment, medication, refusal, transport decision, destination, diversion, transfer-of-care, and patient outcome. | Treating NEMSIS record as clinical continuity. |
| Behavioral-crisis lane | 988 routing, answer, backup flowout, safety plan, local crisis center, mobile crisis, 911 transfer, police involvement, and follow-up. | Treating 988 contact as crisis stabilization. |
| Public warning lane | IPAWS authority, WEA/EAS message, geography, language, accessibility, timing, cancellation, and protective action. | Treating alert sent as warning received. |
| Degraded operations | Network outage, cyber incident, power, telecom diversity, reroute, backup center, radio fallback, manual logs, and restoration. | Treating reliability certification as continuity. |
| Equity and after-action | Language, disability, rural/tribal, age, housing/custody/care setting, complaint, QA review, death/near-miss, and corrective action. | Treating aggregate performance as repaired harm. |

## Minimum joined record

A serious emergency-response packet should contain at least:

1. **Person/channel file.** Caller, affected person, language, disability/access needs, device/channel, callback route, location confidence, safety constraints, and representative/bystander role.
2. **Routing and answer file.** Originating carrier, call/text/RTT path, PSAP, transfers, abandoned or overflow state, queue time, backup center, and 988/911 boundary.
3. **Location file.** Civic address, wireless coordinate, z-axis or dispatchable location, GIS validation, map layer, unit-visible location, and correction trail.
4. **Dispatch file.** Call type, priority, CAD timestamps, unit recommendation, unit assignment, radio/MDT delivery, mutual aid, and status changes.
5. **Response file.** Unit availability, travel time, staging, scene access, responder safety, arrival, no-patient-found, refusal, or cancellation reason.
6. **Clinical/transport file.** EMS assessment, interventions, medication, destination, hospital diversion, transfer-of-care, patient refusal, and outcome where available.
7. **Crisis-care file.** 988 contact, in-state/backup routing, Veterans/Spanish/Deaf lanes, local crisis center, mobile crisis, 911 transfer, and follow-up.
8. **Alert/public-warning file.** IPAWS/WEA/EAS authorization, message text, geography, multilingual/accessibility state, send/receive evidence, cancellation, and protective-action feedback.
9. **Outage/degraded-mode file.** Telecom, PSAP, NG911, radio, CAD, cyber, power, and data outages; reroute; backup; manual logs; and restoration.
10. **Source-currentness boundary.** Mark whether each source is a rule, self-reported profile, outage notice, dataset, dashboard, performance metric, alert record, or live incident record.

## Upgrade triggers

Route to the full emergency-response continuity docket when any of these appear:

- a 911, PSAP, CAD, dispatch, EMS, 988, IPAWS, WEA, EAS, outage, or NEMSIS row is cited as proof that rescue was delivered;
- location, transfer, language, disability, text/RTT, rural/tribal, indoor, high-rise, or mapping uncertainty can affect response;
- cyber, telecom, power, vendor, NG911, CAD, radio, or alerting infrastructure can degrade emergency service;
- a behavioral-crisis, overdose, medical, fire, disaster, water contamination, school, custody, nursing-home, housing, or utility emergency depends on communications routing;
- after-action review, complaint, death, near-miss, or performance dashboard could hide incident-level failure.

## Downshift conditions

A lighter summary is acceptable only when the question is pure national 911/EMS/988/IPAWS background and no caller, location, dispatch, responder, patient, alert recipient, crisis contact, outage, or remedy consequence is live. Once any person may have been unable to reach, receive, understand, or benefit from emergency help, open the full packet.

## Failure modes

- **No rescue by dispatch row:** call or dispatch status exists but help never reaches the person.
- **No 911 by connection:** the call connects but routes to the wrong PSAP, loses location, or lacks fallback.
- **No location by coordinate:** coordinates or z-axis data exist but are not actionable for responders.
- **No EMS by incident record:** a patient-care record exists but treatment, transport, or hospital handoff fails.
- **No crisis stabilization by answer rate:** 988 performance looks strong while local response, transfer, or follow-up fails.
- **No warning by alert sent:** an alert is issued but not received, understood, accessible, or acted upon.
- **No resilience by certification:** a provider certifies reliability but monitoring, outage notice, reroute, or backup fails.
- **No accountability by dashboard:** aggregate metrics hide a death, near-miss, abandoned call, language failure, or outage tail.

## Audit questions

- Which person, caller, patient, crisis contact, or alert recipient is at risk?
- Which channel is involved: voice 911, text-to-911, RTT, wireless, landline, VoIP, 988, WEA/EAS, radio, CAD, or EMS patient-care record?
- Was the call routed to the correct PSAP and transferred without losing ANI/ALI/location/callback context?
- Did responders receive actionable location, event type, hazards, language/access information, and updates?
- Did a unit arrive, make contact, treat or transport, hand off, or document a justified non-response?
- Did an outage, cyber event, power loss, carrier failure, vendor failure, or mutual-aid gap affect service?
- Did language, disability, Deaf/HoH access, age, rural/tribal location, housing, custody, or facility status change risk?
- Is the source a national profile, rule, dataset, dashboard, monthly report, or incident-level record?

## Source posture

Use National 911 Program, FCC, EMS/NEMSIS, SAMHSA/988, FEMA/IPAWS, and CDC sources as official evidence lanes for standards, reporting surfaces, performance metrics, and planning. Do not treat any one source as live incident proof without PSAP, carrier, CAD, radio, EMS, crisis-center, alert-authority, hospital, complaint, and after-action records.
