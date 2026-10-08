# Rev0945 focused audit

## Mission guard

AnonSync exists to replace Resilio Sync. The revision changes the shipping C++
folder/payload path. It adds no daemon, sync engine, policy taxonomy, pairing
format, or mandatory operator knob.

## Severe provenance defect corrected

Two sibling worktrees had accumulated different rev0945 implementations while
build-directory names suggested a single lineage. One branch's status text
claimed cache promotion that its source did not contain; another branch contained
that implementation but not the first branch's configuration expansion. Build
results from directories configured against discarded sources were invalid for
publication.

The correction was source diff against the retained rev0944 baseline, followed
by fresh source-bound GCC and Clang build directories. Every retained result
checks the configured source path. Publication claims are never aggregated from
sibling worktrees.

## Bootstrap/code drift corrected

After lineage reconciliation, the visible bootstrap and this audit still claimed
that likely same-size no-ops released the mutation batch before hashing, but the
canonical folder owner had not implemented that transition. That was a release
blocking truth defect, not a documentation nicety. The owner now performs the
catalog/extent hint check before source preparation, the runtime work accounting
requires the following no-op to contribute no mutation work, and the structural
audit requires the release to precede the batch-crossing/preparation path. The
complete GCC and sanitizer gates were rerun after this correction.

## Premature configuration rejected

The discarded branch promoted payload-batch count/byte frontiers into CLI,
service configuration, provisioning, and share setup. No target workload had
justified those values as a user contract. The final implementation keeps one
internal 256-put/256-MiB exact-work scheduler boundary and exposes only diagnostic
results. Operator configuration remains focused on product behavior rather than
implementation churn.

## Exclusive lease horizon reduced

A changed path could leave its batch live while the next cataloged no-op was
opened and completely hashed. The final folder owner looks up the catalog hint
before preparation. If the path is a cataloged file with the same classified
extent, it releases the unrelated batch first. Exact post-open content still
determines no-op versus same-size edit; the hint grants no synchronization
authority.

Runtime accounting proves a changed path in a many-file tree now charges only
its own mutation source/work rather than the following no-op. Mixed local/remote
coverage proves remote apply retains no exclusive batch.

## Cache lifetime and teardown audit

A mutation batch owns a shared process-local cache capability instead of a raw
pointer to its creator store. It may therefore outlive the creator safely. On
successful non-poisoned teardown it performs a final lease/root proof, swaps the
complete verified index into the cache, and records the exact marker observation.
Failure is swallowed because caching is acceleration only.

The exclusive `StoreLease` is declared last in batch state. After the destructor
body, it is destroyed before the displaced old index vector, releasing the flock
before potentially large metadata reclamation.

## Release-boundary contamination rejected

After validation, a fresh internal `.git` directory and Python bytecode cache
appeared inside the working wrapper. They were quarantined outside the release,
not treated as source. The first staged verifier then rejected the active
projection because the earlier projection had counted the bytecode file under
`tools/`. The projection and manifest were regenerated only after the clean
boundary was frozen. No VCS metadata, Python cache, build output, binary, socket,
or symlink is present in the release stage.

## Remaining boundary

Every segment still performs a complete namespace metadata traversal. A cold
process hashes all payload bytes. No durable exact index, rotating scrub,
wall-clock lease deadline, reachability, or reclamation exists. These are the
next measured scaling boundaries.
