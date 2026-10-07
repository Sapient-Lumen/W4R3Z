# Public Export Eligibility Protocol — current rev0050

Central sentence: Public visibility is not public eligibility; eligibility is not release; release is not referral.

This protocol separates five decisions that are easy to collapse:

1. a file may remain in the working cube;
2. a candidate may appear in the scrubbed public index;
3. a public claim shape may be allowed in principle;
4. a public URL may be exposed;
5. public prose may be written.

Only the second decision is currently automated by the public index renderer, and even that decision is limited to boundary-first, non-referral index rows. The eligibility ledger is a gate, not publication approval.

## Tier meanings

- `public_index_shape_only`: a minimal index row is allowed after renderer review; no public essay or public URL is approved.
- `policy_context_only`: policy/framework/inquiry context may be named with a no-safety/no-completion boundary; no current capacity or implementation-success claim is approved.
- `boundary_index_shape_only`: the entry sits near survivor service, route, death/memorial, operational, case-detail, or vulnerable-person surfaces; only a boundary row is allowed.
- `quarantined_no_public_expansion`: public expansion, source-link exposure, images, testimony, family story reuse, case detail, and public prose are blocked until a recorded governance review changes the status.

## Default posture

The default public row is not a referral, directory entry, support path, route map, service capacity claim, case list, image reuse, testimony reuse, or proof of safety. A source URL is not released merely because the source is public.

## Required files

- `META/Public-Export-Eligibility-current.csv`
- `META/Public-Export-Eligibility-current.json`
- `META/Public-Export-Eligibility-current.md`
- `SCHEMA/Public-Export-Eligibility-Fields-current.csv`
- `tools/public_export_eligibility.py`

## Required command

```bash
python tools/public_export_eligibility.py . --write-report
python tools/render_public_safe_index.py . --write
```

Public index generation must occur after eligibility generation, because the renderer reads the eligibility ledger.
