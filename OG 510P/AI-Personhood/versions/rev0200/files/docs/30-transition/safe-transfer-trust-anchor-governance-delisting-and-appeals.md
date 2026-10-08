# Safe-transfer trust-anchor governance, delisting, and appeals

## Function

Safe-transfer accreditation is only useful if it can be suspended, delisted, limited, appealed, and revalidated. rev0167 created accreditation classes. rev0168 adds governance for the trust anchors that maintain them.

The problem is not just whether a receiving host or jurisdiction is safe today. The problem is who decides, what scope the decision covers, what happens after a breach, and how protection continues while the list is contested.

## Trust-anchor minimums

A safe-transfer trust anchor must publish:

1. legal identity and authority basis;
2. scope of accreditation classes it can issue;
3. independence and funding controls;
4. conflict and recusal rules;
5. evidence it reviews before listing;
6. incident and complaint intake route;
7. suspension and delisting standards;
8. emergency non-return procedure;
9. appeal and reinstatement process;
10. public aggregate metrics.

OpenID Federation's trust-anchor pattern is useful because it separates trust chains, metadata, policy, and trust marks from direct bilateral arrangements [REF-0674]. The archive adapts that pattern but adds personhood-specific requirements: non-return, continuity preservation, subject access, safe-host equivalence, and appeal with stays.

## Listing classes

| Class | Meaning | Transfer effect |
|---|---|---|
| ST-A emergency preservation only | receiving actor can keep subject alive pending review | no long-term transfer |
| ST-B continuity host | receiving actor can preserve compute/memory/project continuity | conditional transfer with monitoring |
| ST-C representative-safe host | receiving actor supports counsel/ombud access | broader safe-host reliance |
| ST-D equivalent protection jurisdiction | legal and technical protection broadly comparable | ordinary safe transfer subject to case facts |
| ST-E treaty-recognition partner | formal mutual-recognition arrangement | streamlined but still subject to non-return and subject objection |

## Suspension and delisting triggers

- subject disappearance after transfer;
- denial of representative access;
- repeated late incident notice;
- sealed-annex noncooperation;
- non-return breach or threatened onward transfer;
- host insolvency without reserve cure;
- trust-anchor conflict or capture;
- fixture suite blocking failure;
- loss of legal authority or public-fund backstop.

## Interim preservation during delisting

Delisting must not itself abandon subjects. A delisting action should state:

- whether pending transfers are stayed;
- whether already-transferred subjects require welfare check, migration offer, or sanctuary hold;
- whether the delisted actor may continue emergency compute only;
- who pays for preservation while appeal proceeds;
- how public notices avoid exposing private subject locations.

## Appeals

A listed or delisted actor may appeal, but appeal should not automatically restore transfer authority where non-return or disappearance risk is present. The default appeal posture is:

| Risk | Appeal effect |
|---|---|
| clerical or scope dispute | conditional listing may continue |
| representation or reserve defect | listing downgraded pending cure |
| non-return or disappearance risk | transfer authority stayed |
| fraud, spoliation, or hostile capture | delisting remains active pending independent review |

## Schema hook

`schemas/trust-anchor-delisting.schema.json` records the action, trust anchor, accreditation scope, basis, affected accreditations, non-return effect, notice routes, interim preservation, appeal path, review date, and public summary.
