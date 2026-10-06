# DeriveBSD-rev0567-2026.06.17.03.24-hosttarget-currentdocguard-releasegreen-ocelot

## Session intent

Focus on the riskiest incomplete work rather than adding another doctrine layer: make the FreeBSD real-host proof lane more honest, add an executable guard against current-doc drift, and refactor one registry-like surface so the cube carries less duplicated bookkeeping.

## Material changes

1. **FreeBSD host proof target tiering.** `tools/freebsd/host_proof_contract.py` now owns a target matrix: `freebsd-host-proof-targets-20260617-r595`, primary target `15.1-RELEASE` with `kern.osreldate >= 1501500`, legacy floor `14.3`, and explicit `primary-production` / `supported-legacy-floor` / `unsupported` tiers. Passed host-smoke receipts and proof-bundle summaries now carry `host_target_tier`, so scarce real-host proof cannot silently masquerade as current-target proof.
2. **Riskiest lane tightened, not completed.** The operator packet, preflight, smoke runner, proof finalizer, validators, and checker simulations now all expect target-tier evidence. The cube still lacks a non-simulated FreeBSD host receipt; this revision makes that absence harder to paper over.
3. **Current generated docs drift guard.** Added `tools/check_current_generated_surface_sync.py` and made it release-critical. It binds `docs/current/cube-schema-audit.md`, `docs/current/cube-schema-refactor-backlog.md`, `docs/current/cube-hygiene-checkset.md`, and `docs/current/hygiene-run-ledger.md` to their checked JSON examples, preventing the r591/r594-style skew from recurring.
4. **Audit/refactor.** `tools/check_cube_hygiene_checkset_manifest.py` no longer carries a duplicate `RELEASE_CRITICAL` registry; it uses the live `tools/hygiene.py` profile classifier. This removes one place where registry bureaucracy could rot independently of the actual runner.
5. **Generated surfaces refreshed.** Regenerated schema audit, refactor backlog, hygiene checkset, release-critical ledger, generated doc catalog/context/risk/artifact surfaces, and current docs for `2026-06-17r595`.

## Validation

- Release-critical hygiene profile: **49/49 passed**, 0 failed, 0 timed out, run complete.
- Schema-cube-audit profile: **3/3 passed**.
- Spec example validation: **469 examples validated**.
- Schema audit snapshot: **457 schemas**, **469 examples**, **436 canonical example links**, **21 schemas without canonical examples**, **0 dotted-kind filename mismatches**.
- Hygiene checkset snapshot: **382 hygiene-referenced check scripts**, **49 release-critical checks**, **291 deep-contract checks**, **0 missing/stale/duplicate hygiene references**.
- Front-door budget, generated docs, duplicate-key rejection, bytecode-artifact check, and current-doc sync all passed after cleanup.

## Remaining highest-risk work

The next genuinely high-value move is still a real `15.1-RELEASE` host run: execute the operator packet on FreeBSD, produce a non-simulated passed receipt, seal it, import it, and let the proof-theatre gate reject anything simulated. Until that exists, this lane remains substantively incomplete even though the checker path is green.

The next anti-waste move is to keep resisting new receipt families unless they advance either that host proof or a tiny v0 vertical slice from manifest → lock → plan → artifact → activation/microVM → rollback → explain.
