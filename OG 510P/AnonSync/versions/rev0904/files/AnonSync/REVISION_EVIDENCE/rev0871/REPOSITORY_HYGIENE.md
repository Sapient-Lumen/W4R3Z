# Repository hygiene and scope audit

The sealed parent contained 337 active files under the verifier's v2 projection.
Rev0871 still contains 337. Exactly nine active files differ; no active file was
added or removed.

During validation, a delayed side branch wrote delivery-protocol files, CMake
targets, and public owner APIs into the mutable worktree after an earlier clean
scan. Removing only the new files exposed a mismatched owner source/header,
proving the branch had partially landed. The branch had no integrated vertical
slice and initially no exercised behavior. Retaining it would have expanded the
assurance, migration, and maintenance burden while weakening build coherence.

The final publication directory was therefore created anew from the verified
rev0870 extraction. Only the nine intended active files and the rev0871
narrative were overlaid. It was configured, built, tested, analyzed, sanitized,
audited, patch-replayed, manifested, and packaged independently. No build tree,
VCS metadata, Python bytecode/cache, symlink, object, library, executable, or
other generated artifact belongs in the release package.
