# SWHID fallback + long-term source availability (greenfield advantage)

**Tier:** C (Optional lane)  
**Profiles:** A, C, D  
**Pillars:** supply-chain, reproducibility
**Patterns:** Quarantine→Promote, Registry→Diff→Gate  

Reproducible builds fail in practice when **sources disappear**: tarballs get deleted, domains expire, VCS hosting changes, or “latest” URLs drift.
A Nix-successor that ignores URL-rot will eventually grow a shadow ecosystem of ad-hoc mirrors and tribal knowledge.

DeriveBSD should treat long-term availability as a **first-class supply-chain property**.

## Goals

- Builds remain possible years later *given the lockfile* and a policy-approved mirror set.
- Every fetch is **hash-verified** and emits a receipt recording *which origin actually served bytes*.
- Air-gapped environments can import source bundles as part of mirror kits.

## Key idea: lockfile carries both hash + archival identity

For each source, `derive.lock` can carry:

- `content_hash` (authoritative; fixed-output)
- `origins[]` (URLs / VCS origins; non-authoritative)
- optional `archive_hint`:
  - **SWHID** (SoftWare Hash IDentifier) for the intended artifact, when available
  - optional “origin snapshot” pointer (e.g., a Software Heritage snapshot SWHID for a repo state)

SWHIDs are **intrinsic identifiers** for software artifacts; a resolver can fetch an artifact and verify the core identifier matches the SWHID.  
See: https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html and https://www.swhid.org/specification/v1.0/0.Introduction/

## Fetch policy: multi-origin, hash-first

A v1 fetcher should try, in order:

1) **Primary origin(s)** (the URLs recorded in the lock)
2) **Policy-approved mirrors**
   - org mirror, distfiles cache, “mirror kit” import, etc.
3) **Software Heritage fallback** (optional lane)
   - resolve via SWHID directly (preferred), or resolve an origin to a snapshot and then retrieve an artifact bundle
   - bundles can be produced via the Software Heritage “Vault” (cooking a bundle) when needed

The fetcher must always:
- verify `content_hash`
- emit a `fetch.receipt` recording:
  - source id + hash
  - which origin succeeded (URL / mirror id / SWHID)
  - resolver evidence (TLS/PKI summary, quarantine status, retries, time authority used)
  - any redactions applied (if exporting support bundles)

## Why Software Heritage (SWH) is worth baking in

GNU Guix integrated SWH fallback so builds can continue when upstream URLs disappear.  
See: https://guix.gnu.org/en/blog/2019/connecting-reproducible-deployment-to-a-long-term-source-code-archive/ and Software Heritage notes about Nix/Guix origins: https://docs.softwareheritage.org/user/software-origins/nixguix.html

DeriveBSD can do better than “manual rescue” by:
- letting publishers attach SWHIDs at lock time (or CI-enrich the lock)
- treating “archival presence” as a policy gate for high-value channels
- including “archived-by” evidence in receipts

## Suggested UX (v0-compatible)

- `derive lock enrich --swhid`
  - resolves lock sources against SWH and stores SWHID hints where possible
- `derive fetch <source-id> --prefer swh`
  - diagnostic fetch route selection; still hash-verified
- `derive mirror make --include sources`
  - mirror kits can carry sources needed for local rebuilds

## Scope/tiering

Recommended default:
- SWHID support is **Tier C optional** in v0 (default-off) but should have a stable schema and receipts now.
- Some deployments (regulated / archival) can make “SWHID required” a policy rule for promoted channels.

## References

- SWHID overview: https://www.softwareheritage.org/software-hash-identifier-swhid/
- SWHID spec: https://www.swhid.org/specification/
- Software Heritage API getting started: https://docs.softwareheritage.org/devel/getting-started/api.html
- Software Heritage Vault: https://docs.softwareheritage.org/devel/swh-vault/index.html and API: https://docs.softwareheritage.org/devel/swh-vault/api.html

See also: `docs/14-supply-chain.md`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/255-policy-constrained-transports.md`.

Last updated: 2026-02-27r117
