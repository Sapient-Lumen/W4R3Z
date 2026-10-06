# Lineage and recovery boundary

## Canonical release inputs

1. Upstream bzip3 1.5.3 source revision `53984ef`.
2. User-supplied rev0019 evidence archive, SHA-256
   `4a20ea247787f92ba60fe437ce18fcd11868bd3c70844bc12d5a0b3cb36ad844`.
3. rev0020, SHA-256
   `3647e48bf963ba928099f0d66dbc3ce578ac49d7a12468d601cffe9727ff0f76`.
4. rev0021, SHA-256
   `3acaba78afe7a3f333670a7a028a048ef5257cea480afdefad60c8492f9c6e69`.
5. rev0022, SHA-256
   `821fb29fcd7587c25c86204ab5f6ce529cac8dbffe35c26f1ba36e913a2b5716`.
6. rev0023, SHA-256
   `0f4e9e93282cc8902f0a4478a04a89be474df51897ec43eaef1f709b3cb194fe`.
7. rev0024, SHA-256
   `b60ddfb8fcc50e77cda064ed643e224c36eca14ee92d52a6741604261ab1e9ff`.
8. rev0025, SHA-256
   `428fcb6d7d6df521a5d61af85232482dd127036d51ef42406b9eadcbeb5c11ba`.
9. rev0026, SHA-256
   `83531439efe80951ac6cb5bfe35fc48af299a97368dff628e196bbe180f84c1d`.
10. rev0027, SHA-256
    `d2c03b847a0a508d3d8ea4ab756a922cb2774da0512e4b9698f98a19214d1c62`.
11. Published rev0028, SHA-256
    `292eb03d4cf86ab611cfae3a7637f6cd22d1670d9e0445ffd9930dd754687008`.
12. Published rev0029, the direct rev0030 parent, SHA-256
    `f7ffab4486aa84bef8bcb544dbca2f0f62cf91ddc211cdc667081a38085cfd9c`.
13. Published rev0030, the direct rev0031 parent, SHA-256
    `b4d9ac0e9e5c6f38c5e09336bea2b5ebd3e3525b3f0227e9008359c67852ba78`.
14. Published rev0031, the direct source parent supplied for rev0033, SHA-256
    `d793ec59d6b5f7d9c3ceac3bbcb8946b5aa3c339de463461a1f385eca401bf6c`.
15. A transcript described a rev0032 archive with SHA-256
    `2d0ecb8c332596a84d01c8705a47a0b11a257c3e50eb41c6da1284b04c5e8252`,
    but that archive was not supplied in this session. It is documentary input,
    not a source-tree ancestor claimed by rev0033.
16. Published rev0033, the direct rev0034 parent, SHA-256
    `c33c266aff3f4143696cca02eb22247b58531657b0dda99d116d5422c0c9f9c2`.
17. The supplied Datacube rev0117 artifact and rotating representative cubes are
    external analysis and validation inputs only. Their payloads are not release
    dependencies.

## Recovery boundary

The supplied rev0019 archive contained evidence but not a buildable codec,
scheduler, spool, or test tree. rev0020 reconstructed a source-bearing baseline
from pinned upstream and preserved the small rev0019 evidence payload without
claiming absent transient implementations had been recovered.

rev0021 onward is cumulative from that source closure. No release invents
missing rev0012–rev0019 code. Decoder, frame streaming, pinned input, atomic
output, ZIP preflight, retained parallel encode/decode, workspace contraction,
and entropy work are present as source and executable tests in their release
archives.

rev0029 uses published rev0028 as its canonical parent. A local, previously
unpublished decoder-hardening branch was used only as a patch source. Its changes
were reconciled onto the published tree, combined with rev0028's entropy alias
and libsais repairs, and revalidated against the published rev0028 binaries and
pristine upstream oracle. The unpublished branch is not treated as a release
ancestor.

rev0030 uses the published rev0029 archive above as its canonical parent. A local
advanced ZIP64 prototype was treated only as a patch source: its ideas were
audited, corrected for the local two-size rule, reconciled with the published
source closure, and revalidated. The prototype is not represented as a published
ancestor.

rev0031 uses the published rev0030 archive above as its canonical parent. The
payload-nomination lane and compact local-span refactor were implemented and
validated directly on that extracted source closure. No unpublished worktree is
represented as an ancestor.


rev0033 uses the supplied rev0031 archive above as its direct buildable source
parent. The session transcript reports rev0032 design and measurement results,
but no rev0032 source archive was available for extraction or comparison.
rev0033 therefore reconstructs the documented speed/memory direction on rev0031
and adds new resource-fit commands, tests, static binaries, and current-session
evidence. It does not claim byte lineage from unseen rev0032 code. The skipped
revision number preserves the user's published naming sequence without
inventing an absent source ancestor.

rev0034 uses the published rev0033 archive above as its direct source parent.
The named profile registry, matched compiler matrix, Clang static binaries,
effectiveness scorecard, and prediction register were implemented and validated
on that extracted closure. Current-session cube payloads informed measurements
but are not carried dependencies.

## Active versus oracle code

- `src/libbz3.cpp`, `src/common.h`, and `src/libsais.h` are the active C++20
  codec translation.
- `upstream/bzip3-1.5.3-53984ef/` is immutable reference material.
- Tests compile the pristine C codec with renamed public symbols, creating an
  independent valid-stream oracle without linking C into production.

## Contracts carried forward

- floor semantics for minimum blocks and bytes per active lane;
- explicit active-only versus all-retained wake accounting;
- corrected exact-multiple frame splitting;
- complete envelope and cumulative-output preflight;
- descriptor-pinned range input and atomic output publication;
- bounded ZIP central/local reconciliation, including unsigned descriptors
  whose CRC equals `0x08074b50`;
- exact smallest legal decoder workspace from validated block extents; and
- no ratio or speed promotion without exact reconstruction, final size, time,
  memory, variance, and cohort evidence.

## Cumulative release map

- rev0021: decoded-block length, constant-metadata scanning, pinned reads,
  atomic publication, and initial low-level hardening.
- rev0022: range-backed frame I/O and complete local/central extra-field TLV
  validation.
- rev0023: retained-lane parallel encoder and incremental central parsing.
- rev0024: retained parallel decoder and shared frame-source cursor.
- rev0025: generation-bounded borrowed block views, exact inverse-BWT workspace
  initialization, and workspace-poison proof.
- rev0026: checksum fusion and hardened high-level C whole-frame contract.
- rev0027: canonical envelope validation and compact exact-size decoder lanes.
- rev0028: alias-audited entropy addressing and defined libsais marker transfer.
- rev0029: low-level adoption of the canonical envelope, fail-fast arithmetic
  underflow, exact LZP/mRLE terminals, grouped compatible APM locality, and ZIP
  member-type admission policy.
- rev0030: complete bounded single-disk ZIP64 end-record resolution, exact local
  two-size semantics, impossible-count preallocation guard, contiguous central
  name arena, compact entry descriptors, and schema-v6 retention telemetry.
- rev0031: opt-in CRC/size content nomination, same-representation grouping,
  incremental SHA-256 screening, exact payload-range verification, whole-group
  read budgets, compact payload-aware local spans, and schema-v7 probe telemetry.
- rev0033: allocation-free compression/decompression resource planning,
  workspace-fitted scheduling-only lane selection, strict-versus-fit CLI
  separation, optional IPO, static no-PT_INTERP Linux tools, speed-first block
  frontier and direct-final-binary evidence, explicit high-level-versus-CLI
  BZ3v1 envelope accounting, Datacube rev0117 weldpoint analysis, and a defined
  modulo-32-bit repair for the imported branchless libsais compaction decrement.
- rev0034: immutable named codec profiles and profile-aware CLI planning,
  incompatible-profile no-publication enforcement, matched GCC/Clang bzip3
  comparison, Clang static convenience tools, corrected ratio-metric reporting,
  effectiveness and compiler/libsais audits, and a falsifiable prediction
  register.

Datacube carrier admission, a controlled current-libsais branch, PGO,
retained-service integration, and any new BZ4 ratio format remain roadmap work
until similarly present, bounded, and tested.
