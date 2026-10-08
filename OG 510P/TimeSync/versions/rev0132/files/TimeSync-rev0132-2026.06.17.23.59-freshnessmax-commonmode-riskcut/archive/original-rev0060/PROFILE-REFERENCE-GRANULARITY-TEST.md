# PROFILE REFERENCE GRANULARITY TEST

## Question

rev0059 selected:

```text
assessed_profile: <profile-ref>
profile_conformance: satisfied | fallback | unsatisfied
```

The open question is how strong `<profile-ref>` must be.

Is a stable name/version enough, or do some boundaries need an authority,
digest, or signed profile-binding record?

## Pressure

A profile reference has to prevent rule ambiguity, not merely name a vibe.

A receiver can only interpret `profile_conformance = satisfied` if it can
recover the rules that were used for validation. But making every assessed
state carry a digest, signature, manifest, and profile document would be the
wrong failure mode. It would turn a compact local/export assessment into a
profile distribution and certification subsystem.

The archive therefore needs a reference-strength rule, not a single global
profile-reference grammar.

## Source pattern

Current time-protocol practice supports **boundary-appropriate binding**.

- NTPv5 keeps the ordinary protocol narrow and separates on-wire exchange from
  client algorithms. Where draft-version ambiguity matters, its draft
  identification extension uses the full draft name including version, and a
  server does not answer a draft identification it does not recognize.
- NTS separates key establishment from ordinary time synchronization. The
  setup channel negotiates parameters and supplies cookies; later time packets
  rely on that established context instead of repeating the whole setup.
- Roughtime binds response interpretation to compact tags, nonce-derived
  evidence, and keys that the client already knows through another means. Its
  signed delegation gives stronger binding where key exposure and evidence
  matter, but it does not carry a broad profile manifest in every response.
- RFC 9760's PTP Enterprise Profile carries explicit profile identification:
  profile name, profile number, version, profile identifier, and specifying
  authority. Profile identity matters because the profile's rules constrain
  interoperability and required behavior.

The common lesson is not "always hash everything".
The lesson is:

```text
use the weakest profile reference that remains unambiguous at the consuming boundary.
```

## Candidate reference strengths

The archive can describe reference strength without standardizing one syntax:

| Strength | Shape | When it is enough |
|---|---|---|
| 0 | implicit sealed context | one authenticated/configured profile encloses all assessed state |
| 1 | `id + version/revision` | globally recognizable, immutable-enough public profile |
| 2 | `authority + id + version/revision` | cross-operator or local/deployment profile where names can collide |
| 3 | `authority + id + version/revision + digest` | detached audit, mutable stores, long retention, safety/compliance use |
| 4 | signed profile-binding record | receiver cannot otherwise trust who bound the profile id/version/digest |

This is not a field list for every packet.
It is a boundary test for explicit `assessed_profile` references.

## Test result

Select a boundary-tiered rule:

```text
assessed_profile uses the weakest reference strong enough to identify
or bind the validation rules at the consuming boundary.
```

Consequences:

- name-only is generally insufficient for exported actionable conformance
- explicit references should include a version, revision, or equivalent stable
  rule-set marker
- an authority is needed when the identifier is not globally unique or when the
  consuming boundary is outside the issuer's sealed configuration
- a digest is needed when the exact rule text may drift, when the assessed
  state is detached from its source context, or when audit/compliance/safety
  use depends on exact rule reconstruction
- a signed binding is needed only when the receiver must independently verify
  the issuer/binder of the profile reference or its validity interval

Compactly:

```text
assessed_profile is a resolvable reference by default;
it becomes digest-backed or signed only when the boundary needs rule binding.
```

## What the digest binds

If a digest is used, it should bind the **normative profile rules used for
assessment**.

It should not bind:
- a PDF as an artifact
- a whole standards catalog
- explanatory commentary
- operator aliases
- request-bundle documentation
- a source packet or individual response

A digest-backed reference says:

> this conformance marker was computed under this exact profile rule set.

It does not say:

> the source is certified, the clock is accurate, or every profile requirement
> was independently audited by the digest issuer.

Those are separate trust and compliance claims.

## What a signed binding does

A signed profile-binding record may bind:
- authority / issuer
- profile identifier
- version or revision
- digest of the normative rule set
- validity interval or publication time
- optional distribution pointer

It should not become:
- a conformance certificate
- a profile negotiation protocol
- a manifest of all supported profiles
- a bundle alias
- an access-control proof
- a substitute for `profile_conformance`

The signed binding answers "which profile rules did this reference identify,
and who says so?" It does not answer "did this timing state satisfy them?"

## Minimum local/export shape

The archive therefore keeps the compact assessed-state shape:

```text
assessed_profile: <profile-ref>
profile_conformance: satisfied | fallback | unsatisfied
applicability: <downstream-use-boundary>
```

`<profile-ref>` may be as small as a versioned standards/profile identifier
or as strong as a digest-backed signed binding, depending on boundary need.

Do not split `profile_conformance` into separate fields such as
`profile_id`, `profile_authority`, `profile_digest`, and `profile_signature`
unless a concrete export format needs that shape.
The archive's concept is reference strength, not a universal object schema.

## Examples

### Sealed single-profile appliance

A managed appliance fleet has one configured timing profile, one authenticated
management boundary, and no detached profile-conformance export.

Result: implicit profile context may be enough.

### Public standards profile

A receiver knows a public profile by stable identifier and version.
The state is consumed immediately inside an operational boundary that can
resolve that identifier.

Result: `id + version` may be enough.

### Deployment-specific profile

A company profile named `traceable-audit` could collide with another operator's
profile of the same name.

Result: use `authority + id + version`.

### Regulated audit archive

The assessed state may be retained for years and reviewed after the profile
has been revised or replaced.

Result: use `authority + id + version + digest`.

### Third-party relay or untrusted distribution

A relay exports assessed state to a receiver that cannot rely on the relay's
configuration alone and needs to verify who bound the profile reference.

Result: use a signed profile-binding record or a reference to one.

## Interaction with profile distribution

This test does not require the assessed state to distribute the profile text.

A reference can be resolvable by:
- standards publication
- deployment contract
- authenticated session setup
- local policy store
- audit repository
- signed binding record

Distribution and reference are separate.
The assessed state only needs enough reference strength for the consuming
boundary to recover or verify the rules.

## Interaction with ordinary source packets

This decision still does not add profile identity, digest, or signatures to the
minimal source packet.

A source packet may remain small.
A local assessed object may attach `assessed_profile` after validation,
required/default checks, optional request accounting, and consequence mapping.

If a protocol profile wants to put a profile identifier on the wire, that can
be a profile-specific feature. It does not force the minimal TimeState claim to
carry profile-binding material.

## Interaction with aliases and request bundles

Operator aliases and request bundles are not profile references.

- An alias names a local convenience expansion.
- A request bundle would name a request preset, if one ever earns itself.
- A profile reference names validation rules, defaults, and obligations.
- A digest-backed profile reference binds those rules more tightly.

Do not promote aliases or bundles into `assessed_profile` just because their
names look operationally meaningful.

## Failure modes

Treat the profile reference as insufficient when:
- it lacks a version/revision and the rules are not immutable
- the authority is ambiguous across the consuming boundary
- the receiver cannot recover the rules used for validation
- a digest was required by the boundary but absent
- the signed binding is required but unverifiable or expired

In those cases, do not export actionable `profile_conformance`.
Export diagnostic/local state, or mark the relevant profile assessment
`unsatisfied` if the profile itself requires the stronger binding.

## Non-goals

This test does not add:
- a global TimeSync profile registry
- mandatory digest for every profile reference
- mandatory signed profile-binding records
- a profile manifest
- profile negotiation
- profile document storage in the archive
- compliance certificates
- alias or bundle promotion
- profile identifiers in every source packet

## Archive judgment

Add the rule:

```text
Explicit assessed_profile references are boundary-tiered.
Use id+version when that is unambiguous;
add authority when names can collide;
add digest when exact retained rules matter;
add signed binding only when the issuer/binding must be independently verified.
```

This closes the rev0059 frontier without bloating the local assessed state.
The archive keeps `assessed_profile` as a resolvable reference and lets each
export boundary earn extra binding strength.

## Next frontier

The next question is lifecycle:
when a profile reference is superseded, revoked, or no longer accepted,
should retained assessed state mean "valid under the profile at assessment
time," "currently acceptable," or both?
