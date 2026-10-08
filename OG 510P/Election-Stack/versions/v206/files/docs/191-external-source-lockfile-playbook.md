# 191 — External source lockfile playbook (cite, don’t bloat)

**Track:** Shared

This archive cannot afford to embed large third‑party PDFs, specs, or web pages.
Instead, we **cite** external material via a small lockfile:

- `evidence/lock/external-sources.toml`

The lockfile gives each external source a stable **ID** so documents can reference it as:

- `source: <id>`

…and so a maintainer can later pin (or re‑pin) its `sha256` without hunting down scattered URLs.

## 191.1 The rule

1. **Prefer citations over bundling.** Only bundle third‑party artifacts when they are both:
   - essential for offline verification *and*
   - small enough to fit the size budget.
2. **Do not paste large excerpts.** Quote only what is necessary to define a rule, a term, or an interface.
3. **For newer evidence docs (≥170), do not use raw external URLs.** Use `source: <id>` instead.

## 191.2 Adding a new external source (minimal process)

1. Add a new `[[source]]` block to `evidence/lock/external-sources.toml` with:
   - `id` (stable, snake_case)
   - `url`
   - `retrieved` (YYYY-MM-DD)
   - `sha256` (recommended; may be blank only with explicit triage: `pin_exemption` + `review_by` (bounded window relative to `retrieved`; see `docs/228`))
   - a short `note` (why it matters here)
   - optional `tags`

2. In the doc that needs the reference, cite it inline:
   - `source: <id>`

3. Run the release gate (`docs/162`) to ensure citations resolve.

## 191.3 Pinning sha256

Use the helper script:

```bash
python3 scripts/fetch_source_sha256.py '<url>'
```

- It streams the URL and prints the `sha256` digest and byte count.
- Update the lockfile with the digest.

Or, if the `url` is already in the lockfile, use the maintainer helper:

```bash
python3 tools/pin_external_source.py <source_id>
```

See `docs/233` for the full pinning workflow.

If a source is intentionally unpinned (e.g., automated retrieval blocked), leave `sha256 = ""` and explain why in `note`.

### When fetch is blocked (pin from local bytes)

If you can download the source via a permitted channel (browser, VPN, offline transfer), pin it without committing the bytes:

```bash
python3 scripts/pin_source_sha256_from_file.py --id <source_id> --set-local-filename /path/to/downloaded.file
```

To update the lockfile entry in place (sha256 + retrieved + local_filename):

```bash
python3 scripts/pin_source_sha256_from_file.py --id <source_id> --set-local-filename --in-place /path/to/downloaded.file
```

### Optional: `local_filename`

If the URL basename is unstable (or two URLs collide on the same basename), add:

- `local_filename = "..."`

This tells `scripts/verify_external_sources_lock.py` what filename to look for in `evidence/cache/` (or your downloads dir) when verifying pinned sources.

## 191.4 When pinning is not enough

Some sources change URLs, disappear, or get “content negotiation” surprises.
If a source is mission‑critical for offline adjudication, consider (sparingly):

- storing a **small** excerpt under `evidence/snapshots/` with a digest pointer, or
- storing a **machine-checkable** summary (tables, IDs, constraints) rather than the whole doc.

If you do bundle anything, treat it as evidence: content-address it and include it in `MANIFEST.sha256`.

## 191.5 Keeping the lockfile lean

During reviews, use:

```bash
python3 scripts/report_source_usage.py
```

This prints unused lockfile IDs and where each `source: <id>` is referenced.
Prune unused entries or add the missing citations (prefer the latter if the source is truly relied on).

**Release gate note:** the gate now fails if any lockfile ID is unused (`scripts/check_unused_sources.py`). This prevents slow lockfile bloat.
