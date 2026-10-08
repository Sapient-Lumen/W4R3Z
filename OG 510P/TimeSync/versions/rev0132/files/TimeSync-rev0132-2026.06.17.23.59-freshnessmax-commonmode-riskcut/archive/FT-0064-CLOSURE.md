# FT-0064 closure — cross-operator profile catalog interoperability

FT-0064 asked for the smallest way independently operated TimeSync profile catalogs could identify compatible profile rules and evidence policies without centralizing profile distribution, creating negotiation, or exchanging broad catalog manifests.

rev0065 closes the frontier with profile compatibility statements.

## Added

```text
spec/27-profile-catalog-compatibility.md
schema/profile-compatibility-statement.schema.json
profiles/compatibility/p3-exact-equivalent-self.json
examples/negative/profile-compatibility-*-invalid.json
```

## Decision

A compatibility statement is a detached, signed, expiring policy artifact. It compares two explicit profile references by authority, id, version, and normative profile-rule digest.

```text
exact_equivalent  digest equality, deterministic
compatible_with   authority assertion
supersedes        authority assertion
alias_for         authority assertion by one of the involved profile authorities
```

The statement does not update catalogs, negotiate profiles, or override local policy acceptance.

## Preserved boundaries

- No central registry.
- No transport negotiation.
- No profile distribution service.
- No broad manifest exchange.
- No global applicability vocabulary.
- No upgrade of operator aliases into profile references.
