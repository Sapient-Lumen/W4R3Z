# AnonSync rev0946

## Mission

Replace Resilio Sync with one practical C++ folder-synchronization product whose
shipping peer service works over direct TCP, Tor, and I2P. Rev0946 corrects a
production capacity composition defect and records the next scale blockers
without pretending that a larger constant is garbage collection, fairness, or a
finished replacement product.

## Product correction

- The shipping folder/catalog defaults admit 100,000 current paths, but the
  production payload store inherited the generic 4,096-entry test default.
  A valid many-small-file tree could therefore exhaust durable content storage
  long before the folder owner reached its advertised boundary.
- Production payload composition now explicitly admits 100,000 payload
  identities. The content-inventory hard bound is aligned with that production
  contract.
- The larger ceiling no longer forces every namespace scan to reserve 100,000
  vector slots up front. Ordinary stores retain a 4,096-entry initial reserve
  and grow only as entries are observed.
- Folder passes now validate local-entry and remote-path limits against both the
  retained catalog capacity and the actual payload-store capacity before any
  pass work.
- The linked peer service rejects configurations above the production durable
  capacity through the real `check-config` path.
- Compile-time composition checks bind the default catalog, local traversal, and
  remote-path limits to the production payload capacity.

## Honest boundary

The store is append-only and still has no reachability or garbage-collection
owner. Matching the current-path ceiling prevents the immediate 4,096-entry
composition failure, but a tree already containing 100,000 unique current
payloads has no version-churn headroom. This revision is a truthful capacity
contract, not a retention solution.

A second release-scale defect remains deliberately unfixed here: each folder
pass starts a bytewise-sorted traversal at the root and charges every classified
regular file against one aggregate byte budget. A tree larger than that budget
can repeatedly service the same prefix and never reach later paths. Because
absence authority requires a complete traversal, deletion repair can also stall
indefinitely. The next scale slice needs durable fair continuation and completed
scan epochs, not a larger default budget.

## Validation

See `REVISION_EVIDENCE/rev0946/validation/VALIDATION_SUMMARY.json`. The focused
payload, folder-owner, configuration-process, structural-audit, complete GCC,
and Clang ASan/UBSan gates are bound to the exact source in this archive.
