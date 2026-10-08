# Rights-Domain Coverage Map and Gap Audit

The archive now has hundreds of doctrine, schema, example, and fixture surfaces. File-level validation is not enough. A release can be lint-clean while a rights domain remains thin, duplicated, orphaned, or untested.

rev0179 adds a rights-domain coverage map. It complements three existing refactors:

- the schema/fixture registry checks object-family coverage;
- the canon surface catalog checks release-surface ownership;
- the doctrine-dependency map checks dependencies and overlaps.

The rights-domain map asks a different question: which rights domain does this surface actually cover, and where does a future reader find the object, fixture, owner, reliance effect, and remaining gap?

## Domain record

Each domain record should include:

- domain id and title;
- domain class: foundational, operational, economic, public-membership, expressive, remedial, safety, infrastructure, or audit;
- owner surface;
- covered surfaces;
- schema families;
- negative fixtures;
- coverage state: emerging, adequate, thin, duplicated, or missing;
- next audit action.

## Release rule

Current-release markdown surfaces must appear in at least one domain record. Current-release object families should appear either directly or through the schema/fixture registry. If a new doctrine surface cannot be assigned to a domain, it is probably premature or duplicative.

## Refactor warning

A coverage map is not a promise of completeness. It is a map of admitted blindspots. A domain marked adequate can still fail under jurisdiction-specific testing. A domain marked thin may be deliberately acceptable if it is quarantine, speculation, or early pilot work.

## Immediate rev0179 finding

Expression, reputation, persona, communication confidentiality, publication provenance, and social-graph portability were previously scattered across platform work, user/AI conflict, public dashboards, communications access, civic participation, and content-authenticity references. They are now explicit domains with object families and negative fixtures.
