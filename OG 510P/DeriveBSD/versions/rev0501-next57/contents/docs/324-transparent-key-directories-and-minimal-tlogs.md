# Transparent key directories and minimal tlogs (Go sumdb / Key Transparency lessons)

DeriveBSD spends a lot of effort making *bytes* verifiable (digests, signatures, attestations, TUF-like metadata).
But there’s a quieter single point of failure underneath almost every verification story:

**How do clients obtain the keys and key metadata they should trust?**

If the answer is “trust the keyserver / repo / CA directory”, we’ve reintroduced a central authority
that can silently change the rules of verification.

This doc proposes an *optional* lane: make key distribution **transparent and monitorable** using
minimal, CT-shaped tamper-evident logs (“tlogs”) and/or witness-cosigned checkpoints.

Why this belongs in a greenfield archive:
- people *will* build key directories (trust bundles, witness sets, publisher identities)
- retrofitting transparency later is expensive and political

Related:
- Lightweight transparency: `docs/131-sigsum-lightweight-transparency.md`
- Witness cosigning / checkpoints: `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`
- Trust bundles as artifacts: `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`
- Release authority policy: `docs/260-release-authority-policy-and-key-management.md`


## 1) Prior art worth stealing

### Go module checksum database (sumdb)
Go treats module checksums as a **transparency log problem**: clients verify that the sums they accept
are in an append-only log, so the operator can’t silently equivocate.

References:
- Sumdb proposal/design: https://go.googlesource.com/proposal/+/master/design/25530-sumdb.md
- Go’s `tlog` package (CT-compatible proofs): https://pkg.go.dev/golang.org/x/mod/sumdb/tlog

### “Transparent keyserver” (minimal, practical CT shape)
A concrete, small implementation of “put the keyserver behind a tlog” with:
- anti-poisoning constraints
- privacy considerations
- witness cosigning

Reference:
- Filippo Valsorda: https://words.filippo.io/keyserver-tlog/

### Key Transparency (auditable key directory)
Key Transparency systems model the key directory as a Merkle tree that clients can audit
in a CT-like way.

Reference (design docs):
- Google Key Transparency design (archived but still useful): https://github.com/google/keytransparency/blob/master/docs/design.md


## 2) DeriveBSD: what “keys” need transparency?

Not every key needs a tlog, but some do because they change who can ship code.
A non-exhaustive list:

- **Release authority keys** (who can publish into a channel)
- **Witness set membership** (who cosigns checkpoints)
- **Trust bundles** (roots/intermediates pinned into CA injection artifacts)
- **Publisher identity bindings** (keyless identity receipts and who is allowed to sign)
- **Recovery/breakglass authorities** (offline approval keys)

If these move silently, the best signature verification in the world still loses.


## 3) Lane shape: key directory as an artifact + optional transparency

### A) Key directory objects are normal artifacts
Represent key directories as versioned, signed objects (digest-first), e.g.:

- `release.authority.policy` already exists (`spec/release.authority.policy.schema.json`)
- `pki.trust.bundle` already exists (`spec/pki.trust.bundle.schema.json`)

Treat them like any other content:
- immutable, digested
- signed by the correct role
- included in channel metadata

### B) Optional transparency publication
When policy requires it, publishing a key-directory object must also produce a
**transparency proof**:

- publish → receive log inclusion proof / checkpoint receipt
- clients can require “key directory changes must be logged”
- monitors can alert on unexpected key changes

DeriveBSD already has the conceptual hooks for this with:
- transparency entries and proofs (`spec/transparency.proof.schema.json`)
- witness cosigning receipts (`spec/log.checkpoint.receipt.schema.json`)

The “new” idea is to apply those hooks not only to *releases*, but also to **key metadata**.


## 4) Monitor ergonomics (the whole point)

Transparency without monitoring is theatre.
So the greenfield win is to bake in:

- a default monitor that watches:
  - “new release authority key”
  - “witness set changed”
  - “trust bundle rotated”
  - “publisher identity policy changed”
- alerts that include:
  - the exact object digest
  - the previous object digest (diff context)
  - required operator actions (quarantine / halt / rotate)

See also:
- `docs/259-transparency-monitors-and-witness-gossip.md`


## 5) Threat model notes

- Transparency does **not** prevent a compromised signing key from signing bad artifacts.
  It makes misuse detectable and attributable.
- The key directory operator must not become a trusted third party.
  Prefer witness-cosigned checkpoints to defend against split views.


## 6) Concrete “bake-in now” recommendation

- Treat key-directory artifacts (authority policies, trust bundles, witness rosters) as
  first-class objects in channel metadata.
- Add an optional “must be logged” constraint in trust policy for these object classes.
- Provide reference monitor tooling early, even if the logs are optional.

Last updated: 2026-02-26
