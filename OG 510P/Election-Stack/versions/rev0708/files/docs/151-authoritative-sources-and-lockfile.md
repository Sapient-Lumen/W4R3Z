# 151. Authoritative sources, pinning, and drift tracking

**Track:** Shared


This spec pack cites many external standards, regulations, and research artifacts.
To prevent **silent drift** and “source substitution” attacks (or simple link rot), all external dependencies should be pinned in a lockfile.

## 151.1 Precedence order (recommended)

When sources conflict, the preferred precedence is:

1. Statutory law / binding regulations for the jurisdiction.
2. Election authority standards and certification materials (e.g., EAC/VVSG in the U.S.).
3. NIST publications and Common Data Formats.
4. IETF RFC Editor publications (normative protocol specs).
5. Peer-reviewed academic publications.
6. Vendor whitepapers / blogs (informative only).

## 151.2 External sources lockfile

See `evidence/lock/external-sources.toml`.

**Citation roles (tight):**
- Use `source: <id>` for *pinned* artifacts that are load-bearing for a normative requirement.
- Use `xref: <id>` for informative background or for sources that are present in the lockfile but currently unpinned (sha256 empty).

The release gate treats any `source:` citation as a promise that the cited artifact is pinned; use `xref:` for unpinned/informative refs. Track A also runs a dedicated drift firewall (`scripts/check_track_a_pinned_sources.py`) to keep deployable controls from accidentally leaning on unpinned artifacts.
A compact, no-URL index of the lockfile IDs is generated at `docs/214-external-sources-index.md`.
A second generated view groups sources by primary tag (first tag) for reading/triage: `docs/230-external-sources-by-primary-tag.md`.
Each entry should include:

- stable URL (and archive URL when possible)
- publication date
- sha256 of the retrieved bytes
- for unpinned entries: explicit triage (`pin_exemption`, `review_by`; see `docs/228`) (bounded window relative to `retrieved`; enforced by the release gate)
- a short “why it matters” note
- a **non-empty** tag list for triage/search (e.g., `vvsg`, `cdf`, `ct`, `ohttp`)

## 151.3 Drift monitoring

At a minimum, run a quarterly drift review (monthly in the 60 days before an election).
When drift triggers fire, follow `150-maintainer-bootstrap-and-change-protocol.md` and record an ADR.

## 151.4 Unpinned sources (triage + caution)

Some lockfile entries may remain **unpinned** (sha256 empty) temporarily, especially when:
- the upstream is a mutable HTML page (high drift risk),
- automated retrieval is blocked (403/robots), or
- the artifact is only informative background and not load-bearing.

Unpinned entries must declare `retrieved` + `pin_exemption` + `review_by` (see `docs/228`) so drift risk is explicit and time-bounded.

**Rule:** an unpinned source MUST NOT be the sole anchor for a normative requirement.
If a claim depends on it, prefer a pinned equivalent (PDF/standard), an archived snapshot, or record an ADR explaining the dependency.

Pin triage (recommended):
- **MUST pin:** law/regulation, election authority standards, NIST/IETF normative specs, and any source used to justify a Track A deployable control.

Release gate: in numbered docs whose **Track:** includes `A`, any `source: <id>` citation MUST be pinned (sha256 non-empty). Use `xref: <id>` for unpinned/informative references (see `scripts/check_track_a_pinned_sources.py`).
- **SHOULD pin:** incident/comms guidance that is frequently cited operationally (e.g., CISA/EAC playbooks).
- **MAY remain unpinned:** landing pages and mutable summaries when they are cited only as informative context.

See `docs/214` for a compact list of current unpinned entries (with exemptions) and a small “pin-first” shortlist.
