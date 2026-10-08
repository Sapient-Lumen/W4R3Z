# Matter object model

A matter object is the first durable object above a source-row. It exists because a source-row is too weak to support department display, while a department claim would be too strong.

## Authorized fields

A matter object may carry:

- matter label from source page;
- source owner and source page;
- agencies named by the source row;
- state or territory label;
- source-page status label;
- document-label count;
- normalized document-class list;
- jurisdiction edge-case flags;
- warnings and next actions.

## Forbidden fields in rev0004

A matter object may not carry:

- named officer allegations;
- civilian identifiers;
- incident facts;
- lawsuit merits conclusions;
- settlement amount claims;
- current legal-status synthesis;
- ratings, grades, or risk scores.

## Why the model exists

The corpus will eventually need department pages. Department pages need source inventories. Source inventories need stable matter objects. This model lets the archive become useful without leaping into dangerous person-level claims.

## Split and merge behavior

Matter objects are not final department entities. A matter can later split into child agency-status objects if the source row contains multiple agencies, subunits, or statuses. It can also attach to a canonical department entity after denominator and jurisdiction checks.
