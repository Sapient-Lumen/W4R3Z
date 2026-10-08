# Mission and waste audit — rev0071

## Heart of the mission

The cube is trying to convert a broad, noisy Nicotine+ audit into a small set of maintainer-usable hardening packets. The project under audit is a GTK/Python client for the Soulseek peer-to-peer network, so the high-value boundary is not abstract code style; it is hostile or confused peer/server input crossing into transfer state, search response parsing/admission, connection ownership, file paths, and local media/share metadata.

The strongest mission sentence is:

> Help Nicotine+ maintainers preserve usability and protocol compatibility while removing peer-controlled state confusion, unbounded parsing, source/scope spoofing, and path/file handling surprises with minimal, reviewable patches and regressions.

This is why the seven strict/front packets are the right *shape* of work:

```text
U-123                        transfer token / active download ownership
PB-01                        peer primary election / connection generation binding
SEARCH-RESP-01A              user-scoped search-response source binding
SEARCH-RESP-01B-BUDDY        buddy-scoped response source-set model
SEARCH-RESP-01C-ROOM         room-scoped response source-set model
SEARCH-RESP-PARSE-BUDGET-A   search response parser prefix budget
SEARCH-RESP-PARSE-BUDGET-B   search response result-count budget
```

## What is missing

1. **Live-current source closure.** The cube has repeatedly preserved the warning that a fresh current checkout or maintainer-provided current tarball must be rerun before external filing. That remains the decisive missing gate. rev0070 proves archived-source patched full-tree syntax, not current-source correctness.

2. **Current upstream delta classification.** Online context changed after the rev0003 source bundle. Public Nicotine+ materials still list 3.3.10 as the stable release, 3.3.11 RC1 is public, and PR #3781 is open around `safe_path_join()` path traversal hardening. That means path/file handling must be treated as public-overlap/watch context before any adjacent packet is framed as private.

3. **Maintainer empathy and presentation compression.** There are enough artifacts to satisfy an auditor, but too many to satisfy a maintainer. The cube needs a two-page packet map and one command per packet, not a maze of historical gates.

4. **Runtime and integration proof.** Static compile and clean-room fixture proof are valuable, but GTK/runtime behavior, test-suite integration, and current branch CI-equivalent runs remain separate.

5. **Exit criteria.** The cube needs a rule saying when to stop adding proof layers. A good rule: no more archived-source hardening layers until the current-source gate is closed or explicitly replaced with maintainer-supplied source.

## What should change

- Stop opening new private packets until current source is refreshed.
- Convert source identity from a basename claim to a hash claim. In this session the uploaded source is `Nicotine-source(2).zip`, and it matches the expected archived source SHA256:
  `feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b`.
- Treat old `Nicotine-source(1).zip` references as historical labels, not operational requirements.
- Promote `workspace/NEXT-REVISION-QUEUE.md` from a note into a hard policy: current-source closure first, then packet retarget/retire/adapt.
- Replace repeated full ranked-audit snapshots with a baseline-plus-delta chain in future revisions.
- Keep one canonical copy of large evidence tables and use pointers from `evidence/`, `handoff/`, and `manifests/` unless a handoff export must be self-contained.

## Places where something has gone severely wrong or wasteful

The severe waste is not the upstream source. The source ZIP is external and intentionally not embedded. The waste is the cube's append-only proof history:

```text
data/ dominates the extracted cube.
ranked-audit-queue history dominates data/.
exact duplicate files exist between data/evidence/manifests/handoff/maintainer_artifacts.
many revisions after rev0053 add valid archived-source gates while the live-current blocker remains open.
```

This is understandable because the cube was built as an audit trail. It becomes harmful when the trail obscures the decision. The corrective path is not immediate deletion; it is a measured compaction gate that first proves what can be canonicalized.

## rev0071 correction

rev0071 adds a machine-readable cloudtainer waste/source-alias audit:

```text
tools/probe_rev0071_cloudtainer_waste.py
data/rev0071_cloudtainer_waste_summary.json
data/rev0071_cloudtainer_duplicate_groups.csv
data/rev0071_cloudtainer_file_inventory.csv
evidence/rev0071-cloudtainer-waste-audit.md
```

The probe verifies the uploaded source by SHA256, inventories payload size, identifies exact duplicates, quantifies ranked-audit-queue growth, and records stale `Nicotine-source(1).zip` references as historical references.

## Speculative diagnosis

The cube appears to have shifted from “produce maintainer-actionable packets” to “produce increasingly strong proof that older archived packets are coherent.” That is not useless; rev0064–rev0070 are defensible gates. But continuing in that direction would be diminishing returns. The next high-leverage step is not another syntax/static gate; it is current-source classification and packet retirement/adaptation.

A reasonable operating rule for future turns:

> One turn, one closure: either current-source identity, one packet rerun, one packet adaptation, or one compaction deletion set with a reversible manifest.
