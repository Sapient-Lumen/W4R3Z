# meta-0436 — Credential access and digital identity gate note

## Summary

Rev0735 adds a credential-access / digital-identity gate layer to the archive. The new rule is: **no public service by login**. A public authority must separate person, credential, account, session, mandate, entitlement, proofing success, fallback, recovery, delegated authority, privacy, and service-owner duties.

## Added archive notes

- `901` — identity credential access and delegated authority dockets.
- `902` — Login.gov IAL2 assurance repair case packet.
- `903` — IRS Online Account / ID.me case packet.
- `904` — GOV.UK One Login case packet.

## Added generated layer

- `metadata/credential_access_tests.json`
- `schema/credential_access_tests.schema.json`
- `tools/build_credential_access_tests.py`
- `generated/CREDENTIAL_ACCESS_TESTS.json`
- `generated/CREDENTIAL_ACCESS_TESTS.md`

## Design reason

The archive already had supplier dependency, platform migration, entitlement continuity, and payment redress. It still needed the access gate between a person and those systems: login, identity proofing, federation, recovery, and delegated authority. Rev0735 adds that layer and tests it across a federal shared identity provider, a private tax credential gate, and a central-government single sign-on service.
