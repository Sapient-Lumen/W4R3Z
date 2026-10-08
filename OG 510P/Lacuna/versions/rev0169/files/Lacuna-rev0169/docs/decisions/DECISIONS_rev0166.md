# Decisions — rev0166

## D166-01 — ship separate player, researcher, and operator entrances

**Decision.** Keep `PLAY_NOW.md`, `FOR_GWERN.md`, and `OPERATE_LACUNA.md` distinct and route to all three before long reference documents.

**Why.** Their information needs conflict. Combining them makes the player learn protocol, the researcher reconstruct the claim, and a weaker operator infer capabilities.

## D166-02 — treat entrances and artifact identity as release invariants

**Decision.** Require every entrance in the tree and manifest; test route order, runtime/revision/root/filename coherence, and absence of preliminary markers.

**Why.** Documentation and onboarding claims are part of the delivered artifact. A checksum-valid archive can still describe the wrong gift surface.

## D166-03 — add a read-only artifact doctor, not a packaging authority

**Decision.** Expose `lacuna artifact check` for local extracted-release verification, including strict unlisted-member refusal, while keeping ZIP construction, signing, publishing, and trusted distribution outside the kernel.

**Why.** A recipient and a weaker model need one executable entrance to package truth. That does not justify release-management or network authority inside the story system.

## D166-04 — label explicit public history as partial unless a ledger census proves completeness

**Decision.** Keep both `history build` and `history complete`. The former authenticates an ordered supplied list and says `not-claimed`; the latter derives the denominator from one committed checkpoint boundary and says `complete` only after exact one-to-one matching.

**Why.** Transcript selection is itself an experimental variable. Calling a supplied subset “complete” would confound the post-checkpoint information-bottleneck test.

## D166-05 — make continuation public-context mode machine-readable

**Decision.** Continuation dispatch v2 declares `typed-only`, `bound-public-history`, or `complete-bound-public-history` and validates its history/view custody accordingly.

**Why.** A fresh narrator and later auditor should not infer which public information condition was used from filenames or prose.

## D166-06 — scan the complete retained cell tree

**Decision.** Search every retained regular-file body and normalized relative pathname beneath the exact planned cell trees, including cube databases, SQLite sidecars, locks, and unrelated retained files. Permit only exact preregistered source paths.

**Why.** Valid state can still contain contaminated bytes. Basename, suffix, binary, lock, and cube exclusions create silent channels precisely where a filesystem-capable worker might write.

## D166-07 — fail closed on traversal incompleteness and tree drift

**Decision.** Refuse unplanned cell directories, walk errors/skipped subtrees, links, nonregular or multi-linked members, oversize/change races, limit exhaustion, and different first/second enumerations.

**Why.** “No finding” is meaningful only when the promised denominator was actually traversed and remained stable.

## D166-08 — stream large-file scans through the shared descriptor boundary

**Decision.** Extract reusable open/post-read authentication helpers and compute content digest plus exact-token counts incrementally with boundary overlap.

**Why.** Whole-file buffering is unnecessary, while a second ad hoc file-security implementation would drift. The scan must detect tokens split across chunks without double-counting.

## D166-09 — retain detected cells and separate contamination from quality

**Decision.** A canary finding is recorded and propagated through bundle seals/reports; it never deletes, repairs, replaces, or reruns the cell. Blind ratings still occur.

**Why.** Otherwise the control becomes a new cherry-picking loop. Contamination status is a mechanical observation, not an aesthetic score.

## D166-10 — preserve kernel boundaries

**Decision.** Keep database schema 8, event schema 1, dependency-free runtime, and parent-only accept/review/recovery/commit/seal/unblind/presentation authority.

**Why.** These changes concern release custody, host context manufacture, and experimental auditing. They do not require another truth layer or broader worker powers.

## D166-11 — define “send-ready” as artifact acceptance, not efficacy

**Decision.** Designate the archive ready for Gwern only after source and clean-extraction tests, strict artifact audit, exact member comparison, manifest verification, and final digest/size metadata agree.

**Why.** That supports the claim that the instrument is runnable and honestly packaged. It must not be phrased as evidence that retcon planning improves fiction.
