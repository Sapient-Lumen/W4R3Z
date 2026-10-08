# Election administration / vote-continuity tests matrix

Generated for `rev0799` from `metadata/election_continuity_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `EC-01` Eligibility and registration-state continuity | Does the packet distinguish legal eligibility, registration route, active/inactive status, address, precinct, challenge, restoration, and voter-facing verification before treating a status row as suffrage? | `424`, `425`, `426`, `486`, `500`, `602`, `817`, `818`, `857`, `932`, `933` | Open an eligibility and registration-state docket before citing registration status as voting access. |
| `EC-02` Ballot style and channel entitlement | Can the packet prove the voter had the correct ballot style, district, party where relevant, language, accessible format, and channel route? | `424`, `426`, `482`, `500`, `602`, `817`, `818`, `932`, `933` | Do not treat a ballot request or polling-place lookup as ballot access until ballot style and channel are verified. |
| `EC-03` Mail, postmark, drop-box, and custody clock | Does the packet separate ballot issue, delivery, voter return, postal possession or postmark evidence, election-office receipt, signature/ID review, cure, acceptance, and counting? | `425`, `486`, `857`, `884`, `887`, `932`, `933` | Build a mail/custody clock and downgrade any claim that asks a scan or postmark to prove more than it can prove. |
| `EC-04` Polling-place, e-pollbook, and degraded-mode proof | If check-in, ballot-on-demand, vote center, equipment, power, network, staffing, or line management fails, is there a paper, emergency, staffing, or extension route? | `443`, `444`, `482`, `856`, `859`, `884`, `887`, `930`, `932`, `933` | Treat polling-place operations as incomplete until degraded-mode voting and reconciliation are shown. |
| `EC-05` Whole-process accessibility | Is access proven across registration, websites/apps, mail ballot applications, polling places, drop boxes, ballot marking, communication, assistance, privacy, and independence? | `424`, `426`, `817`, `818`, `856`, `857`, `932`, `933` | Do not accept an accessible-machine checkbox as proof of accessible voting. |
| `EC-06` Provisional, challenge, and cure ledger | Are provisional, signature, ID, eligibility, address, and challenge ballots tracked by reason, notice, proof route, deadline, outcome, and public denominator? | `424`, `425`, `482`, `857`, `884`, `932`, `933` | Open a cure ledger; do not treat provisional envelopes as suffrage protection without notice, proof, and outcome. |
| `EC-07` UOCAVA and remote-voter deadline lane | For military and overseas voters, are ballot-transmission date, allowed return methods, FWAB/emergency route, receipt, cure, and counting outcome visible? | `424`, `425`, `486`, `817`, `857`, `932`, `933` | Separate UOCAVA voters from domestic aggregate metrics when timing or transmission risk is live. |
| `EC-08` Tabulation, audit, canvass, recount, and certification ladder | Does the packet separate unofficial result, tabulation, adjudication, reconciliation, audit, canvass, certification, recount, contest, and finality boundary? | `421`, `425`, `484`, `857`, `884`, `932`, `933` | Do not treat unofficial results or certification as complete until audit, recount, contest, and discrepancy boundaries are visible. |
| `EC-09` Official source-of-truth and public communication | Can voters and observers tell which official source answers registration, ballot tracking, polling place, accessibility, results, meetings, certification, and correction questions? | `424`, `438`, `457`, `475`, `484`, `857`, `917`, `932`, `933` | Publish a source-of-truth map and downgrade third-party summaries or result dashboards that omit authority and finality labels. |
| `EC-10` Cyber, vendor, and physical-security dependency | Are election-management, voting-system, e-pollbook, website, reporting-feed, vendor-access, DDoS, ransomware, physical-security, and intimidation risks joined to voting-continuity fallback routes? | `443`, `444`, `452`, `856`, `859`, `884`, `887`, `917`, `930`, `932`, `933` | Join security evidence to election function and degraded mode before citing resilience or public confidence. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `933` | `EC-01`, `EC-02`, `EC-03`, `EC-04`, `EC-05`, `EC-06`, `EC-07`, `EC-08`, `EC-09`, `EC-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `421` | 1 |
| `424` | 6 |
| `425` | 5 |
| `426` | 3 |
| `438` | 1 |
| `443` | 2 |
| `444` | 2 |
| `452` | 1 |
| `457` | 1 |
| `475` | 1 |
| `482` | 3 |
| `484` | 2 |
| `486` | 3 |
| `500` | 2 |
| `602` | 2 |
| `817` | 4 |
| `818` | 3 |
| `856` | 3 |
| `857` | 7 |
| `859` | 2 |
| `884` | 5 |
| `887` | 3 |
| `917` | 2 |
| `930` | 2 |
| `932` | 10 |
| `933` | 10 |

## Use rule

Run election-continuity tests whenever voter registration, list maintenance, ballot style, mail or absentee voting, UOCAVA, drop boxes, polling places, e-pollbooks, voting systems, accessibility, provisional or challenged ballots, signature/ID cure, tabulation, audits, canvass, certification, recounts, contests, election websites, USPS Election Mail, or cyber/physical election-security services can determine whether an eligible voter cast a countable ballot and whether the result surface is administratively trustworthy. Separate eligibility, registration, ballot, channel, accessibility, custody, cure, count, audit, certification, contest, and remedy states before treating a status row, result feed, audit label, or certified total as election proof.
