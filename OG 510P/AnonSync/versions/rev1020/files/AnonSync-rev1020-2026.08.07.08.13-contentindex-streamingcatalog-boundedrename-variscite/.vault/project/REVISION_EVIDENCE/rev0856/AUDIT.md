# Rev0856 deep audit

## Mission-relevant finding

The conflict planner was locally deterministic but not viewpoint-independent. Its v1 conflict identity bound `local_version_digest` before `remote_version_digest`, and every divergent peer selected `RecordConflict`, whose apply semantics preserve local bytes and promote remote bytes. Two honest peers could therefore mint different conflict identities and finish with opposite primary values. This was a product-level convergence defect, not merely a naming inconsistency.

## Additional defects corrected

The preserved artifact was named with the remote device even though its bytes came from the local losing file. The artifact path also truncated `conflict_set_id` to 18 characters; because nine characters were the literal `conflict-` prefix, only 36 digest bits reached the filesystem namespace.

## Refactor

The deterministic policy is now a separately linked, dependency-light C++ leaf. It owns validated value kinds, winner/loser evidence, canonical kind/digest pairs, and v2 conflict identity generation. The large domain unit delegates policy rather than reproducing it. The leaf does not depend on SQLite, filesystem state, clocks, stream locale, device orientation, or the core monolith.

## Semantic result

Mixed file/tombstone races are remove-wins to prevent uncoordinated resurrection, while preserving a losing local file before applying the tombstone. Equal-kind races use a total order over immutable version digests. Complementary peer views select the same winner, the losing peer alone records preservation authority, and both orientations mint the same conflict-set identity.

The integration corpus exercises the production diff and apply planners, duplicate delivery, hostile global locale, and all six permutations of three-file, file/file/delete, and three-tombstone histories. Artifact paths now identify the actual losing publisher and retain the complete 128-bit conflict identity.

## Audit result

The new fail-closed source audit passes **31/31** checks. The final registered structural inventory passes **44/44** in four completed ranges. It verifies typed ownership, dependency direction, domain separation, length framing, locale independence, orientation independence, kind binding, full artifact identity, generated histories, duplicate delivery, and the rev0856 package gate.

## Remaining risk

This proves one deterministic conflict-primary slice, not whole-system strong eventual consistency. There is not yet one operation algebra for recreation epochs, renames, membership/key epochs, message omission, partitions, crashes across multiple resources, external effects, or Byzantine input. Conflict artifacts are modeled as ordinary set-union files after creation; multi-peer transport dissemination remains outside this oracle. The monolithic domain unit and broad lexical audit surface remain large change amplifiers.
