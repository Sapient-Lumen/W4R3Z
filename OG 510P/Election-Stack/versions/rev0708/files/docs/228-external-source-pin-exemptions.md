# 228 — External source pin exemptions (explicit triage, bounded drift risk)

**Track:** Shared

This archive cites external standards, guidance, and research via the lockfile:

- `evidence/lock/external-sources.toml`

Most entries should be **pinned** (`sha256` present). But some sources cannot be pinned immediately
(e.g., automated retrieval blocked, or the upstream is a mutable HTML landing page).

To keep “unpinned” from becoming an invisible long‑term hazard, any entry with `sha256 = ""` MUST declare:

- `pin_exemption = "..."` — why it is unpinned
- `review_by = "YYYY-MM-DD"` — when a maintainer must revisit pinning or replacement

See: `docs/151` (policy) and `docs/191` (playbook).

## 228.1 Allowed exemption codes (keep small)

- `blocked` — automated retrieval is blocked (403/robots/network), but pinning is expected once bytes are obtained via a permitted channel. **Only use this after a real fetch attempt fails** (don’t mark stable public artifacts as `blocked` by default).
- `mutable` — upstream is a mutable HTML page or “living document” where pinning is optional; treat as informative unless you also cite a stable/pinned artifact.
- `temporary` — short‑lived placeholder; should be resolved (pinned or replaced) before the next release.

If a case doesn’t fit, prefer adding a short explanation in `note` and then map it onto one of the above codes (avoid growing the code set).

## 228.2 How to resolve an exemption

### `blocked` (pin from local bytes, don’t commit the bytes)

1. Obtain the artifact via a permitted channel (browser/VPN/offline transfer).
2. Pin it without bundling it:

```bash
python3 scripts/pin_source_sha256_from_file.py --id <source_id> --in-place /path/to/downloaded.file
```

This updates `sha256` + `retrieved` (and optionally `local_filename`) in the lockfile.

### `mutable` (prefer stable substitutes)

- Prefer a stable, versioned, or PDF equivalent (then pin that).
- If you must cite the mutable page, treat it as **informative** (`xref:`) and avoid making it the sole anchor for a normative requirement.
- If the page is load‑bearing and no stable substitute exists, record an ADR explaining the dependency and consider a **bounded** machine-checkable summary rather than bundling the whole page.

### `temporary` (don’t let it linger)

- Convert to `blocked`/`mutable` with a clear plan, or pin immediately.
- Avoid citing `temporary` entries in Track A; if you must, file an ADR and pin as soon as feasible.

## 228.3 Review cadence (minimal)

The goal is not perfection; it’s to keep drift risk **explicit** and prevent “unpinned forever.”

**Enforced by the release gate (deterministic, relative to `retrieved`):**
- `temporary`: `review_by` MUST be within **90 days** of `retrieved`.
- `mutable`: `review_by` MUST be within **180 days** of `retrieved`.
- `blocked`: `review_by` MUST be within **365 days** of `retrieved`.

**Recommended practice (often tighter than the cap):**
- Default: set `review_by` within ~90 days.
- In the 60 days before an election: review monthly.
## 228.4 Tooling (tight)

- `scripts/check_external_sources_lockfile.py` enforces that unpinned entries declare `pin_exemption` + `review_by`, and that `source:` citations only reference pinned bytes.
- `scripts/verify_external_sources_lock.py` is a best‑effort local verifier: it hashes pinned sources when you have the bytes locally and prints exemption + review‑by for unpinned entries.
- `scripts/gen_external_sources_index.py` regenerates `docs/214` and `docs/230` (no‑URL indexes) plus `docs/EXTERNAL_SOURCE_REVIEW_QUEUE.md` (a small maintainer queue sorted by `review_by`).
- `tools/pin_external_source.py` fetches a lockfile `url` and computes sha256 (no bytes committed); see `docs/233` for the end-to-end pinning workflow.

## 228.5 Tag conventions (keep triage searchable, prevent tag explosion)

- Tags MUST be **lower_snake_case** (`[a-z0-9_]+`). Avoid hyphens to reduce accidental tag-cardinality growth.
- Keep tags **short and stable** (usually 2–5). The first tag is treated as the **primary tag** for the generated grouped view (`docs/230`).
- Prefer intent tags (`cdf`, `audit`, `results_reporting`) plus authority tags (`nist`, `eac`, `cisa`) rather than one-off descriptors.
