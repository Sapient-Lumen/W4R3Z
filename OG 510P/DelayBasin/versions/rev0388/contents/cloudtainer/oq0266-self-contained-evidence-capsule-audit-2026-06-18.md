# OQ-0266 self-contained evidence-capsule audit — 2026-06-18

## Executive finding

Rev0387 froze the response-set lock, policy-verification receipt, and all four response/custody/score triplets into one deterministic ZIP. That removed the result-changing path-reopen defect found in rev0386, but the artifact described as a “portable” completed run was not independently replayable.

The final scorer still opened the assignment plan, commitment, scoring policy, dispatch manifest, responder packets, response templates, scorer intakes, custody templates, score-sheet templates, batch manifest, and validator surfaces from the ambient pilot tree. Those files were not members of the final bundle. Deleting the ambient `cloudtainer/oq0266-isolated-semantic-pilot/` directory from an otherwise valid verifier extraction made an untouched rev0387 bundle unscoreable:

```text
missing assignment plan: .../cloudtainer/oq0266-isolated-semantic-pilot/assignment-plan.json
```

This was more than an inconvenience. Replay depended on mutable state outside the claimed final evidence boundary. A later operator could lose the static files, mix them with another build, or silently consult changed policy and packet material. The internal dynamic-artifact manifest could not detect that dependency.

Rev0387 also reported an outer bundle hash but did not require final aggregation to know an independently preserved expected value. An internally valid replacement bundle could therefore become the new apparent completed run if its own self-reported identity was accepted.

## Repair

Rev0388 replaces the dynamic-only run bundle with `isolated-run-evidence-capsule-v2`. The deterministic capsule now contains:

- the exact original prefreeze dispatch kit;
- the exact original postfreeze batch/scoring kit;
- the response-set lock;
- the postfreeze policy-verification receipt; and
- all four final response, custody, and score-sheet triplets.

`run-manifest.json` binds the SHA-256 and canonical member name of both source kits and every dynamic artifact. Final aggregation now accepts only two run-specific inputs: the capsule path and a separately supplied expected capsule SHA-256. The expected digest is checked against the raw outer bytes before the ZIP or any JSON member is interpreted.

The trusted verifier then parses the captured source kits, verifies their exact relation, materializes a temporary read-only replay root, and injects only the exact responder bundles captured in the prefreeze kit. It revalidates the complete response/custody/score chain against those frozen surfaces. Code stored inside the capsule is retained as hashed evidence but is not imported or executed; verifier trust remains outside the evidence object.

## Reproduced and permanent canaries

The ordinary checker now exercises four positive properties:

1. a responder clock fifteen minutes ahead remains acceptable because causal artifact receipts, not cross-machine clock comparison, establish order;
2. the capsule reaches the same decision after the entire ambient pilot data directory is deleted;
3. mutation of an original source score sheet after capsule assembly does not change replay; and
4. the separately preserved outer digest accepts the exact intended capsule.

The negative suite now contains fourteen attacks. Two are new in this revision:

- **Whole-capsule replacement.** The checker builds a second, internally valid capsule with a result-changing compact score. That alternate capsule is accepted under its own digest, proving it is structurally coherent, but is rejected before interpretation when presented with the original separately preserved digest.
- **Unsafe nested ZIP member.** A prefreeze source kit containing `../escape.json` is rejected before assembly. No capsule and no escaped file are published.

All prior attacks against response-lock bypass, missing or substituted prerequisite receipts, outcome-adaptive plan/policy/stimulus substitution, responder self-scoring, duplicate responders, strict-JSON overflow, and postassembly member replacement remain active.

## Audit and refactor

### One current evidence-capsule contract

`cloudtainer/tools/oq0266_isolated_run_bundle_lib.py` now owns the current capsule contract, exact member topology, deterministic ZIP metadata, outer-digest verification, inner-member verification, and bounded nested-ZIP parser. The assembler, scorer, builder, checker, generated policy, batch-contract lint, and cloudtainer preflight import or assert the same identifiers rather than carrying parallel notions of a “completed run.”

### Root-injected external replay validation

The conventional external-response scorer previously resolved static surfaces only from its module-global repository root. Its file and scorer-intake loaders now accept an explicit root. The isolated verifier can therefore apply the same mature response/custody/score validation against a temporary source tree reconstructed from the capsule, without changing process working directories or copying mutable ambient files into place.

### Bounded archive handling

Every nested ZIP is read as bytes and checked before materialization. The current parser rejects absolute paths, `..`, backslashes, non-canonical names, directories, symlinks, encryption, duplicate names, ZIP comments, oversized members, excessive member counts, excessive total uncompressed size, and CRC/header failures. The outer capsule additionally requires stored compression, fixed timestamps, Unix read-only regular-file metadata, exact ordering, and a maximum raw size.

This is a deliberately small refactor around an execution boundary. It adds no new registry, ledger, or doctrinal gate.

## External design pressure

The repair borrows three narrow principles rather than claiming conformance with a larger standard:

- RFC 8493 defines manifests as mappings from paths to checksums and distinguishes corruption detection from protection against active attack. That distinction is why an internal manifest is not treated as sufficient custody for the outer capsule.
- The OCI descriptor model treats a digest as the content identifier and recommends verifying raw content against an independently communicated digest before consuming it from an untrusted source. Rev0388 performs that outer check before ZIP interpretation.
- Python’s `zipfile` documentation warns that untrusted archives require inspection and identifies path traversal and decompression-resource exhaustion as hazards. Rev0388 therefore does not call `extractall()` on nested source kits and enforces explicit path and resource bounds.

References:

- RFC 8493, *The BagIt File Packaging Format (V1.0)*: https://www.rfc-editor.org/rfc/rfc8493.html
- OCI Image Specification, *Descriptor*: https://github.com/opencontainers/image-spec/blob/main/descriptor.md
- Python Standard Library, `zipfile`: https://docs.python.org/3/library/zipfile.html

## Speculation and next pressure

A self-contained capsule changes the likely next failure mode. The remaining evidence risk is less likely to be accidental file loss and more likely to be weak custody of the one expected outer digest or trust in the verifier implementation itself. A future real run may justify one independently timestamped or signed digest receipt and a minimal verifier release hash. It does not justify building those systems before any genuine response batch exists.

The next mission-bearing action is still external execution: one real conventional OQ-0266 triplet or one genuinely isolated four-responder batch. Internal hardening should stop unless the execution attempt exposes another concrete failure.

## Remaining limits

- No genuine conventional OQ-0266 response/custody/score-sheet triplet exists.
- No genuine four-person isolated batch exists.
- The expected capsule SHA-256 is still an unsigned string unless a separate human or service preserves it.
- The trusted verifier and its release identity are outside the capsule; source code included in the capsule is evidence, not executed authority.
- String identifiers do not prove distinct humans, non-collusion, or absence of out-of-band disclosure.
- One responder per arm cannot identify causal operator burden, and the trace condition remains a bounded excerpt rather than a measured full archive.

The internal canonical head remains `rev0374`; rev0388 is a cloudtainer working overlay.
