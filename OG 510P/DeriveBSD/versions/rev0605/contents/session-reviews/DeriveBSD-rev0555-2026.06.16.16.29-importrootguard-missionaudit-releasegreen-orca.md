# DeriveBSD-rev0555-2026.06.16.16.29-importrootguard-missionaudit-releasegreen-orca

## Focus

This pass read the cube as a mission artifact, compared it against the current FreeBSD and adjacent supply-chain/security ecosystem, and then made one small corrective change in the cloudtainer rather than adding another doctrine surface. The concrete target was a release-critical gate that could describe the live checked-in FreeBSD proof import root as audited even when the directory itself was absent.

Generated at: `2026-06-16T20:29:30Z`

Source archive inspected: `DeriveBSD-rev0554-2026.06.16.15.54-exactrunreceipt-proofclaimguard-releasegreen-ibis(1).zip`

Internal cube cut observed: `2026-06-16r584`

Cloudtainer truth: this session ran on Linux, not on a real FreeBSD host. No non-simulated FreeBSD host proof is claimed here.

## Heart of the mission

DeriveBSD is best understood as a BSD-native evidence operating system, not merely as a package manager, installer, hypervisor wrapper, or documentation cube. The heart is a typed, digest-addressed derivation spine: `Spec -> Lock -> Plan -> Artifact -> Activate/Launch -> Receipt`. Its intended proof is not a persuasive narrative; it is a replayable receipt graph that binds build inputs, host authority, removable-media handling, isolation boundaries, support handoff, import, audit, switch, and rollback to real host behavior.

The project's strongest strategic bet is to combine Nix-like reproducible/declarative derivation discipline, Qubes-like compartmentalization instincts, and in-toto/SLSA/TUF/Sigstore-style supply-chain evidence with FreeBSD-native primitives: ZFS boot environments, jails, bhyve, pf anchors, Capsicum/Casper, rc integration, and now a FreeBSD 15-era packaged-base world. That synthesis is the mission. The danger is mistaking a well-described proof system for a proven one.

## What is still missing

1. A checked-in, non-simulated FreeBSD `real-host-proof` remains missing. The collector, preflight, receipt validator, finalizer, handoff verifier, importer, import auditor, proof-bundle validator, theatre gate, and collect/import run receipt machinery are much stronger than they were in older cuts, but the archive still contains no production real-host import under `validation/freebsd-host-proof-imports`.

2. The v0 vertical slice is still not the dominant artifact. There are many schemas, examples, docs, and checkers, but the product should be judged by one boring end-to-end path: manifest to lock, lock to plan, plan to artifact, artifact to host generation or workload image, activation or launch, rollback, and receipts for the whole path.

3. The FreeBSD target matrix needs an explicit decision. The cube's current host proof floor remains `14.3-RELEASE` / `kern.osreldate >= 1403000`; online release context now has FreeBSD 15.1 as production and 15.0/14.4/14.3 as legacy. Either the 14.3 floor is an intentional oldest-supported-host compatibility target, or 15.x should become first-class in the proof matrix.

4. The product cutline is still too easy to dilute. The cube has high schema/checker mass and a lot of receipt-family ambition. That is useful only where it collapses toward real proof, operator usability, or the v0 spine.

5. Operator proof ergonomics are not yet proven. A proof path can be exact and still fail in practice if a scarce FreeBSD host operator cannot run it, preserve the handoff on failure, and bring back the right files without improvisation.

## What changed in this revision

- Tightened `tools/check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate.py` so the live checked-in import root must exist, must not be a symlink, and must be a directory before the strict auditor is allowed to report success.
- Added the ZIP-level live import root directory `validation/freebsd-host-proof-imports/`, currently empty. This is not a real proof import; it is only the checked-in root that the stricter gate now requires.
- Refreshed `spec/examples/cube.hygiene.run.ledger.json` under the runner semantics expected by `tools/check_cube_hygiene_run_ledger.py`.
- Added this mission-audit session review, release-critical ledger, schema-cube-audit ledger, and summary JSON.

The essential code change is intentionally narrow:

```python
def live_import_root_errors() -> list[str]:
    import_root = ROOT / contract.DEFAULT_IMPORT_ROOT_REL
    if not import_root.exists():
        return [f"live checked-in import root does not exist: {contract.DEFAULT_IMPORT_ROOT_REL}"]
    if import_root.is_symlink():
        return [f"live checked-in import root must not be a symlink: {contract.DEFAULT_IMPORT_ROOT_REL}"]
    if not import_root.is_dir():
        return [f"live checked-in import root is not a directory: {contract.DEFAULT_IMPORT_ROOT_REL}"]
    return import_auditor.audit_import_root(import_root, allow_checker_simulation=False)
```

Patched checker digest: `sha256:6e44218ad96216db8fbb22f6c8ab402b20a265d2aeda5216d88b99f063e63fcf`

Canonical hygiene ledger digest after refresh: `sha256:fa7664f9c4ee802f2d99d4bb94952cfd60c43dcf3b0fa422434868c1f18f0dd5`

## What had gone wrong or wasteful

### Viciously plausible evidence theatre

The release-critical gate printed that it audited the live checked-in import root, but the path `validation/freebsd-host-proof-imports` was absent in the uploaded archive. The delegated auditor treats a missing import root as acceptable because an install may legitimately have no imports yet. That behavior is reasonable for a generic auditor, but it was too weak for a checked-in live-root gate whose job is to prove that the archive surface exists.

This was the most cloudtainer-correctable flaw I found because it was not a philosophical objection; it was a concrete vacuous-pass seam. The fix makes absence, symlink substitution, and non-directory replacement fail before the auditor runs.

### Schema gravity before physical proof

The cube is very good at defining receipt shapes, audit shapes, and guardrails. That becomes wasteful when new evidence surfaces outrun the one missing thing that would make the story materially stronger: a real FreeBSD host proof bundle collected, verified, imported, and audited.

Correction over time: until the real proof lands, net-new receipt families should require a specific exception: they must either reduce a live proof ambiguity, remove an operator failure mode, or advance the v0 vertical slice.

### Version and target tension

The cube correctly separates runner contract version from emitting cube cut in newer host-proof material, and the floor of FreeBSD 14.3 may be intentional. But with FreeBSD 15.1 current, the project should document whether 14.3 is a compatibility floor, a conservative first host, or merely stale inertia.

Correction over time: add `docs/current/freebsd-proof-target-matrix.md` with `15.1`, `15.0`, `14.4`, and `14.3` lanes, including what is required, optional, or deferred for each.

### Empty directory caveat

The new import-root directory exists in the ZIP package. If this cube is later moved through Git, an empty directory will not survive by itself. Avoid adding an arbitrary `.keep` file unless the importer/auditor contract is adjusted to allow it; a better long-term answer is either a typed root manifest/sentinel that auditors understand or a release-packaging check that materializes the empty directory in archives.

## Online research notes folded into this review

- FreeBSD release context moved forward: 15.1 is the production release on 2026-06-16, while 15.0, 14.4, and 14.3 are legacy releases.
- FreeBSD 15.0 introduced base-system management through `pkg(8)` and generated release artifacts without requiring root privilege; both are strategically relevant to a typed host-artifact project.
- FreeBSD jails, bhyve, and Capsicum remain a coherent substrate for this project: OS-level containment, microVM isolation, and capability-mode reduction all match the cube's least-authority goals.
- Adjacent ecosystems reinforce the same design pressure: Nix emphasizes isolated reproducible declarative builds; Qubes emphasizes compartmentalization through virtualization; in-toto/SLSA/TUF/Sigstore/Rekor/JCS/Reproducible Builds all strengthen the case for canonical, signed, replayable, independently verifiable evidence rather than trust-by-story.

## Validation

- `tools/check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate.py`: passed after the stricter root-existence patch.
- `release-critical`: `45 / 45` passed.
- `schema-cube-audit`: `3 / 3` passed.
- `check_cube_hygiene_run_ledger.py`: passed after canonical ledger refresh.
- `check_no_python_bytecode_artifacts.py`: clean before session artifacts were written.

Release-critical cube input: `sha256:333dbca1982f15ac63a703d0cef35126331fdf1d43d9b3662d1b5ee528e25cec` over `3069` files, scope `source-docs-spec-tools-fixtures-no-session-reviews-or-ledger-output`.

## Recommended next change

The next best revision should make the scarce-host import handoff harder to misuse: add a single-page real-host proof import packet that tells a FreeBSD operator exactly what to run, what three or four files to bring back, and how the cloudtainer importer/auditor will reject simulations by default. That packet should be short enough to print.

## Local structure snapshot

```json
{
  "file_count_after_session_files_started": 3277,
  "top_level_file_count_by_dir": {
    "CHANGELOG.md": 1,
    "README.md": 1,
    "adrs": 368,
    "docs": 822,
    "fixtures": 2,
    "rfcs": 184,
    "session-reviews": 189,
    "spec": 1277,
    "tools": 415,
    "validation": 18
  },
  "extension_count_top": {
    ".md": 1433,
    ".json": 1424,
    ".py": 407,
    ".sh": 3,
    ".txt": 2,
    ".bin": 1,
    ".c": 1,
    ".cfg": 1,
    ".h": 1,
    ".hujson": 1,
    ".jsonl": 1,
    ".pdf": 1
  },
  "total_bytes_after_session_files_started": 23069986
}
```
