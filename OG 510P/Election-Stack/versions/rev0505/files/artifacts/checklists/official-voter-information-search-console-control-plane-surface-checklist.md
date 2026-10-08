# Official voter-information Search Console control-plane checklist

Use this quickcheck when an election office depends on search-side recovery actions such as recrawl requests, move support, or coverage inspection to keep current voter-information pages discoverable and stale results suppressible.

## Property coverage

- Confirm that Search Console property coverage matches the hostnames the public is actually taught to use.
- Confirm whether a domain property, URL-prefix properties, or both are needed for the current primary host.
- Confirm whether legacy hosts, temporary replacement hosts, or critical subdomain branches still need verified property coverage.
- Do not assume one narrow URL-prefix property covers every public host or protocol variant the office still circulates.

## Verified-owner continuity

- Confirm that at least one verified owner still exists for each critical property.
- Avoid depending on only one person or one fragile verification method.
- Add a secondary verified-owner path when the current setup relies on one template tag, one HTML file, or one staff account.
- Confirm that emergency operators know which accounts actually have owner or full-user permissions for urgent actions.

## Token and user hygiene

- Review visible owners/users after staff, contractor, or vendor changes.
- Review the underlying verification methods too; removing a user is not the same thing as retiring the token.
- Remove stale verification files, tags, or DNS methods that should no longer authorize prior operators.
- Record only the bounded review state, not the secret token values.

## Migration and hosting continuity

- Before a host or infrastructure change, verify the old and new sites and relevant variants where the search-side move flow depends on them.
- During CMS or hosting moves, make sure HTML-file or template-tag verification survives into the new environment.
- If a temporary hostname is used for testing or emergency replacement, decide whether it also needs verified property coverage.
- Re-check control-plane access before decommissioning the old environment.

## Emergency operability

- Confirm who can request URL Inspection indexing for managed URLs.
- Confirm who can review or perform owner-grade actions needed during a migration or stale-result incident.
- Rehearse the path for urgent search-side recovery before a deadline-sensitive period rather than during it.
- Keep the public office/help lane ready even if the search-side control plane is degraded.

## Evidence posture

- Preserve only the intended property scopes, owner-continuity class, stale-token review state, migration-review state, emergency-operability state, and last review time.
- Do not preserve raw verification tokens, DNS record values, private admin email rosters, or full Search Console exports when bounded policy reconstruction is sufficient.
