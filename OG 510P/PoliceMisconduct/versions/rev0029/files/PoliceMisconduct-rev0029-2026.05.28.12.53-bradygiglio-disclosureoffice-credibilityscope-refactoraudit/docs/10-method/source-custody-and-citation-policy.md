# Source custody and citation policy

A police misconduct datacube is only as trustworthy as its source custody. Every future source record should answer:

1. What kind of carrier is this?
2. Who produced it?
3. When was it produced, filed, released, corrected, or accessed?
4. Is the artifact version-pinned?
5. What exact fields does it support?
6. What does it not support?
7. What privacy or sealing constraints govern it?
8. What rollback happens if it is corrected, withdrawn, sealed, or contradicted?

## Carrier before claim

A field cannot become a corpus assertion until it has at least one source carrier row. A claim cannot borrow authority from adjacent sources.
A news report about a lawsuit may support “news report says lawsuit was filed,” but the court docket supports the filing itself.

## Versioning

Mutable webpages require access date and, when possible, archived copy or digest. Court records require court, case number, document number if available,
filing date, and access route. FOIA releases require request/release metadata where available.

## Extracted facts

Extraction notes must preserve source wording when it matters, especially for contested terms such as “officer-involved,” “resisting,” “excited delirium,”
“less-lethal,” “exonerated,” and “unfounded.” The normalized field may be clearer than the source wording but must not hide the source wording.
