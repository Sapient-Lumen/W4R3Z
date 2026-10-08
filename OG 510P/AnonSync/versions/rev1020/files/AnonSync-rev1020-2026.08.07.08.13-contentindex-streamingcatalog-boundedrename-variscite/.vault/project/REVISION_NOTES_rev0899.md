# AnonSync rev0899 revision notes

## Store-attested common birth

Rev0899 closes the largest remaining rev0898 composition gap. Fresh bootstrap
now generates a checked 256-bit OpenSSL CSPRNG deployment ID, computes the exact
manifest digest before store creation, and persists the same deployment identity
inside every selected SQLite database and the product payload lease anchor.

The manifest is version 2 and commits role-specific SQLite application IDs,
required store-internal deployment binding, and fresh-only store adoption. The
new shared deployment-identity leaf prevents the manifest, SQLite binding, and
payload marker from growing incompatible validators.

## SQLite role and deployment gate

Every product SQLite database now has:

- one role-specific `application_id` (`0x41535201` through `0x41535204`);
- one exact STRICT singleton `anonsync_store_set_binding` table;
- a row binding deployment ID, manifest digest/path, role, database path, folder,
  local actor, application ID, and a length-framed domain-separated digest; and
- staged and post-commit attestation during bootstrap.

All normal database opens pass through one bound-open frontier before a role
owner is constructed. It verifies the exact opened main filename, application
ID, exact `sqlite_schema`, absence of temporary shadows, singleton row, every
field, and the independently recomputed digest.

## Fresh-only product bootstrap

Before any mutation, init now requires the manifest, every SQLite main file,
and every `-journal`/`-wal`/`-shm` sidecar to be absent, and requires the payload
and delivery roots to be empty. Product bootstrap refuses pre-existing namespace
adoption. This is intentionally not an in-place migration path for rev0898.

The product payload root uses identity marker v3, binding deployment ID,
manifest digest/path, folder, actor, and lease protocol. Existing-only operation
cannot create it, and snapshots bind the marker generation and digest.

## Audit/refactor

The process proof independently recomputes canonical manifest and binding
digests instead of trusting C++ output. It now rejects a canonical forged
manifest with a recomputed self-digest, same-role database substitution,
cross-role database substitution, foreign payload-root substitution, orphan
SQLite sidecars, pre-seeded payload roots, and pre-seeded files roots, while
retaining the real mutual-TLS delivery and settlement proof.

The database-open, bootstrap, and payload-store lexical audits were updated for
the bound-open architecture, and a new 20-check deployment-binding audit was
registered. The common binding namespace was added to the exact file-effect
schema inventory rather than duplicated into each owner.

## Validation

- Complete GCC 14 Debug build: passed.
- Bundled SQLite: 3.53.3; upstream 3.53.4 was released on 2026-07-24,
  so a pinned dependency refresh remains an explicit follow-up rather than an
  unreviewed last-minute amalgamation substitution.
- Full registered suite: 219/219 passed with 8 workers in 18.30 seconds.
- Focused product/authority lane: 9/9 passed.
- Database-open policy audit: 16/16.
- Bootstrap-authority audit: 19/19.
- Deployment-binding audit: 20/20.
- Payload-store source audit: 33/33.
- Direct process proof: passed.

## Highest remaining gaps

Interrupted init is fail-closed but stranded: there is no inspect/resume/
quarantine state machine. Whole-namespace preflight still has check-to-create
races against noncooperating writers. WAL does not make the separate databases
atomic as a set. The unkeyed binding does not resist a hostile writer who can
rewrite every deployment resource. Path authority is not yet rooted in one live
ancestor descriptor, and status still uses write-capable WAL owners.

The product also remains a bounded command spine without a supervisor, causal
filesystem semantics, chunking/resume, GC/indexing, at-rest encryption, or an
anonymity threat model. See
`STORE_SET_BIRTH_ATTESTATION_AND_FRESH_BOOTSTRAP_AUDIT_rev0899.md` for the full
mission analysis, research, speculation, build-cost findings, and recommended
sequence.
