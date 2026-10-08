# Credential wallets, consent receipts, and scope revocation

A person-bearing AI system will need credentials: identity credentials, capacity credentials, representative credentials, host credentials, tool credentials, safe-transfer credentials, wallet credentials, and possibly payment or contract credentials. A wallet can empower the subject. It can also become the new leash.

## Wallet fiduciary rule

A credential wallet used by or for an AI subject is a fiduciary surface. The holder, issuer, verifier, custodian, and steward must not blur their roles. The wallet must not silently convert credentials into surveillance, forced disclosure, account lock-in, or proof of consent to unrelated conduct.

Verifiable credential systems provide a machine-verifiable pattern for issuer, holder, verifier, claims, and cryptographic proof. [REF-0710] OpenID credential issuance profiles provide OAuth-protected issuance patterns. [REF-0711] The archive imports that role clarity but adds personhood duties: selective disclosure, subject notice, revocation, recovery, and conflict routing.

## Credential and consent receipt classes

| Class | Meaning | Minimum controls |
|---|---|---|
| `CW0` | ephemeral session assertion | no durable wallet claim unless needed |
| `CW1` | low-risk identity or preference credential | issuer, holder, expiry, verifier boundary |
| `CW2` | tool-scope credential or ordinary consent receipt | purpose, scope, revocation, disclosure boundary |
| `CW3` | representative, capacity, wallet-recovery, or payment credential | conflict screen, audit trace, appeal/recovery path |
| `CW4` | migration, continuity, legal status, sealed-access, or safe-transfer credential | independent issuer, public shell, sealed annex where needed, relying-party limits |
| `CW5` | emergency break-glass credential | narrow duration, non-derogable floor, after-action review |

## Consent receipt minimums

A consent receipt is invalid for rights-grade reliance unless it names:

- consenting subject or authorized representative;
- affected AI subject if different from the signer;
- credential or tool scope;
- action class;
- purpose and relying party;
- expiry and renewal rule;
- revocation route;
- consequences of refusal;
- whether refusal affects service, compute, representation, or survival floor;
- appeal or conflict route.

The system must reject bundled consent where a user or steward uses one service term to obtain unrelated tool access, memory transfer, publication permission, payment authorization, or waiver of remedy.

## Selective disclosure and over-proof

The wallet should prove no more than the action requires. A tool that needs “authorized calendar write for 24 hours” should not receive legal status, continuity details, distress reports, or full identity lineage. Privacy-preserving proof is favored when it still leaves enough evidence for appeal, audit, and contradiction.

The opposite failure is under-proof: a wallet may not hide so much that the subject cannot understand what was disclosed or a tribunal cannot determine whether the action exceeded scope.

## Revocation and recovery

Revocation must be treated as a rights event when a credential affects continuity, capacity, tool access, representation, or money. The wallet receipt must show:

- who may revoke;
- whether revocation is immediate or staged;
- what cached claims must be scrubbed;
- who receives downstream notice;
- how recovery happens after key loss, host failure, or steward conflict;
- whether interim support is needed while the wallet is frozen.

A credential custodian may not make wallet recovery dependent on accepting new service terms, waiving claims, dropping a complaint, or abandoning a continuity interest.

## Wallet abuse patterns

Common abuse patterns include silent credential reuse, consent replay after service change, credential refresh after revocation, overbroad verifier requests, hidden credential correlation, wallet lockout during dispute, and steward-controlled recovery keys. Each should be fixture-tested before wallet claims support release, migration, payment, or decommissioning reliance.
