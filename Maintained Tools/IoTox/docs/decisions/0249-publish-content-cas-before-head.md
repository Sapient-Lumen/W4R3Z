# ADR 0249: Publish the complete content CAS before signed HEAD

Status: accepted local product prerequisite; remote bootstrap, reconstruction, activation, and
genuine-provider evidence remain open, 2026-08-29.

## Context

ADRs 0244–0248 froze content-v2 framing, coordination, storage, commit, and restart-attempt
boundaries, but every successful construction test began with synthetic manifest/CAS fixtures. The
live `sync-publish` command could build only range-v1 and treepack-v1 revisions. Enabling transport
against that boundary would therefore have moved test fixtures rather than a revision the product
could create, persist, and serve.

A content publication is also wider than the flat two-object transaction. It may name thousands of
deduplicated chunks plus paged metadata, while its root manifest and signed HEAD are the only compact
entry points. Publishing either entry point before the complete immutable fabric exists would turn a
local cancellation, quota refusal, or crash into signed incomplete truth.

## Decision

`sync-publish NAMESPACE ABSOLUTE_PATH` now supports `content-v2` file namespaces through one
transaction-bound local publisher. It:

1. rejects a non-writer device, a foreign-writer predecessor, an unsafe/nonregular source, and an
   impossible memory configuration before content-store mutation;
2. builds a bounded toxsync flat or paged fabric in an exact random mode-0700 workspace beneath
   `ROOT/staging/content-v2/publications`, selecting flat automatically only when the conservative
   manifest/object estimate fits policy;
3. walks the generated root, pages, and chunks, canonicalizes the complete digest/size set, checks
   source metadata remained stable, and applies both scratch-staging and combined flat-plus-CAS quota
   admission before the first product CAS commit;
4. imports every unique object through ADR 0247's verified-copy, no-replace, prospective-quota
   commit; and
5. publishes the stable-device-signed HEAD only after every object is present and verified.

Cancellation is checked before build, admission, every object commit, and HEAD. Cancellation or an
I/O failure after some objects land may leave immutable unreachable CAS objects, but never publishes
a HEAD that names an incomplete fabric. Exact duplicate publication reuses verified CAS and signed
HEAD truth.

The namespace transaction remains held through the local build and commit sequence. This is
deliberately conservative: one publisher, startup cleanup, and other namespace mutations cannot race
the workspace or its complete-set quota decision. Bounded random publication workspaces are never
network-attempt staging. Normal completion removes the exact workspace; startup removes only exact
owner-private `local-<16 lowercase hex>` directories and refuses any foreign or unsafe entry.

Agent startup now performs that cleanup and CTA1 recovery for content namespaces. The local control
command renders the resulting generation, signed record, artifact/root identities, format,
chunk/page counts, and installed/reused object totals without advertising content-v2 to peers.

## Qualification

The owned registry now has 651 checks. Flat and paged tests build real files, import the complete CAS,
resolve a chunk/page through the signed HEAD, advance an exact parent-linked successor, and reuse an
exact duplicate. Negative tests prove whole-set quota refusal before CAS/HEAD, unauthorized-writer
and impossible-workspace refusal before namespace creation, cancellation after one CAS commit with
HEAD still absent, exact abandoned-workspace cleanup, and foreign-entry refusal. A full Agent test
reaches `sync-publish` through the Unix control socket, reloads the signed content-v2 HEAD, and
resolves a committed chunk after shutdown.

## Consequences

- IoTox can create real flat or paged content-v2 revisions through its ordinary product command; the
  next transport work no longer depends on synthetic publisher fixtures.
- The root manifest already resides in the canonical CAS, but a subscriber still needs an
  authenticated bootstrap request for that root before page/chunk scheduling can begin.
- Content-aware accepted reachability, reconstruction into an activatable immutable artifact,
  rollback-guard integration, repair/quarantine roots, and genuine Sandwurm evidence remain open.
- Files are indexed by pathname through toxsync. The pre/post metadata fence detects ordinary
  concurrent change, but this is not a hostile same-user snapshot primitive.
- Feature bit 29 remains dark.
