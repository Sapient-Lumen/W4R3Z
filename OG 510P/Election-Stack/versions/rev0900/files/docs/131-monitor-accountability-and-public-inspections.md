# Monitor accountability and public inspections

**Track:** A (Deployable core)


This pack already assumes **servers can be compromised** and relies on public verifiability (PBB + proofs). In practice, that verifiability can still fail if the *monitoring and checking ecosystem* becomes unreliable, captured, or simply absent.

Recent work on Certificate Transparency (CT) argues that CT’s trust model can overlook the **checking/monitoring phase** and that unreliable monitors can introduce meaningful security gaps (e.g., the system “looks transparent” but misbehavior is not actually caught). See: source: ndss_2024_public_inspections_monitors_pdf.

## Threats addressed
- **Unreliable monitors**: monitors do not check, check incompletely, or lie.
- **Captured monitors**: collude with an operator/attacker to suppress detection.
- **Verifier monoculture**: one implementation bug causes ecosystem-wide blind spots.
- **Suppression by omission**: “no news” (no alerts) is misinterpreted as safety.

## Design principle
Make monitoring itself **auditable**:
> “The monitor checked X and obtained result Y at time T using tool hash H” should be a *signed statement* that third parties can replay/verify.

## Requirements (normative)
1. **Multiple monitor classes**
   - **Operator monitors**: run by election operators (for rapid detection).
   - **Independent monitors**: run by stakeholders (parties/NGOs/universities/media).
   - **Public monitors**: community-run, with published code and datasets.


1b. **Public monitor profile (representation duty)**
   - Each independent monitor SHOULD publish a short human-legible profile (identity, COI/funding summary, what it checks, where it publishes replayable reports).
   - Profiles SHOULD include a short representation‑duty statement and material floor/accessibility commitments (usable for non‑experts).
   - Template: `artifacts/templates/witness-profile.md`.

2. **Monitor attestations (MAT)**
   - Each monitor MUST periodically publish a signed `MonitorAttestation` covering:
     - latest checkpoint(s) observed for PBB and ATL,
     - consistency checks performed since prior attestation,
     - inclusion sampling strategy + sample results,
     - tool/build identity (content hash), and
     - a timestamp and evidence bundle references.
   - Attestations MUST be **anchored** into the PBB/ATL (or cross-notarized) so they cannot be quietly backfilled.

3. **Public inspection challenges**
   - Any stakeholder SHOULD be able to issue a signed `InspectionChallenge` (optional object) that requires monitors to:
     - prove they can fetch specific artifacts,
     - validate specific inclusion/consistency proofs,
     - or re-run specified checks over a published window.
   - Monitors SHOULD respond with `InspectionResponse` objects (optional), anchored and replayable.

4. **Diversity and independence**
   - At least **two independent monitor implementations** MUST exist for core checks:
     - PBB inclusion/consistency
     - witness-quorum checkpoint validation
     - EPB / parameter pinning validation
     - results package and drift alert validation
   - Governance MUST define minimum diversity for “acceptable monitoring coverage” (e.g., N monitors across distinct org classes / jurisdictions / ASNs).

5. **“No silent failure” posture**
   - Client/verifier UX MUST NOT treat “absence of alerts” as evidence of safety.
   - The system MUST publish **coverage summaries** (who monitored what, and when).

## Implementation notes
- Keep monitor logic small and memory-safe where practical.
- Prefer deterministic, replayable pipelines:
  - every attestation should be reproducible from referenced artifacts + tool hash.
- Separate “high-frequency lightweight checks” (freshness) from “deep checks” (full consistency proof chains).

## Outputs
- `schemas/MonitorAttestation.json`
- `artifacts/checklists/monitor-accountability-checklist.md`
- `tools/monitor_attestation_checker.py`
