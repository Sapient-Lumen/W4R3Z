# rev0788 repository hygiene audit

The source handoff contains 479 files and 22,633,183 bytes before rev0788's new
evidence is added. First-party production code, headers, tests, and tools total
4,418,194 bytes. Historical `REVISION_EVIDENCE`, `audit`, and `evidence` trees
total 7,828,016 bytes, or 1.772 times the active first-party implementation and
validation source.

This is correctness debt, not just ZIP size:

- repository-wide searches return obsolete copies and logs before active code;
- copied validation evidence can be mistaken for current release truth;
- package manifests and static audits cost more and become easier to get wrong;
- reviewers must distinguish repeated historical source patches from live files;
- sanitizer and build artifacts are not present, but immutable textual history
  still dominates first-party code volume.

Rev0788 does not delete historical evidence because existing handoffs may rely
on those paths. The recommended transition is a content-addressed evidence
store with one immutable pack per revision. A source ZIP should retain the
current revision's complete evidence plus signed hashes and retrieval pointers
for older packs. A migration should first prove that every historical digest is
reachable before pruning any in-cube copy.
