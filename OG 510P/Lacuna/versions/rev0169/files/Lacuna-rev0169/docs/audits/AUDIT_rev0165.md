# Audit — rev0165

## Scope

The audit began from accepted rev0164 and focused on the strongest remaining experimental nonclaim: Lacuna could enforce declared context topology and compile fresh-narrator dispatches, but it could not falsify a host that accidentally exposed a private parent prompt, reused hidden context, or let a card-only worker inspect unrelated files.

The audit covered preregistration timing, canary source separation, blind-rating order, exact scan scope, sidecar safety, nonadvancing refusal, report/bundle custody, operator legibility, and performance. It did not treat exact-token absence as proof of provider isolation.

## Finding A165-01 — fresh context remained only a declaration

**Risk.** Distinct `context_id` values and correct checkpoint/narrator topology can be recorded even when a provider or parent carries hidden context across calls.

**Repair.** Added one deterministic operator-only token per opaque cell. Its exact source is limited to the private cell-coordinator driver. Unexpected copies in returns, transcripts, sidecars, or another cell are retained and classified.

**Evidence.** A positive-control test copies one cell’s operator token into another cell’s transcript and obtains an authenticated `cross-cell-leak` before the blind packet is created.

## Finding A165-02 — card-only filesystem claims had no falsification pressure

**Risk.** A read-only or “no tools” worker can still receive a shared workspace or an overpowered parent. Host declarations cannot show that unrelated private files stayed unread.

**Repair.** Added one filesystem-only token per cell in an unrelated private file. The driver contains only source path and token digest, not the token body. Any exact copy elsewhere is a finding.

**Evidence.** A positive-control test reads the private file, places its token in the owning cell’s transcript, and obtains a `filesystem-only` `same-cell-leak` result.

## Finding A165-03 — post hoc canaries would be weak evidence

**Risk.** Generating or choosing a token after seeing model output would permit selective probes and accidental collisions with the observed material.

**Repair.** `15-PRIVATE-contamination-plan.json` is deterministic from the pre-result assignment seed, run ID, cell label, and scope. It is published with all four drivers before execution. Audit rebuilds the exact plan.

**Evidence.** Scenario-begin tests validate eight unique plan entries and exact driver/source agreement.

## Finding A165-04 — findings could bias ratings or become a rerun filter

**Risk.** An operator who sees a leak before deciding whether to keep a cell could rerun only embarrassing conditions. A rater who sees leak status could alter scores.

**Repair.** The scan is automatic on final-cell acceptance and precedes blind-packet publication. Leak-detected cells remain frozen, rateable, included, sealed, and reported. The blind packet excludes plan, tokens, and findings.

**Evidence.** End-to-end tests reach `awaiting-ratings` with a retained leak, confirm no canary token occurs in a clean blind packet, and propagate a leak through block seal and aggregate report without exclusion.

## Finding A165-05 — excluding valid cube state created a contamination blind spot

**Risk.** An early implementation excluded every `cells/<label>/cube/` subtree on the theory that cube verification already covered it. Verification proves local ledger/projection consistency, not absence of a canary from an otherwise valid source, claim, agent label, event payload, or SQLite sidecar. A worker could therefore read private bytes, commit them into valid cube state, omit them from the transcript, and receive a clean scan.

**Repair.** Defined the final boundary as `scenario-cell-complete-retained-artifacts-v1`: the content and relative pathname of every single-link regular file under the four preregistered cell directories, including cube metadata, the accepted SQLite database, retained SQLite sidecars, and cooperative lock files. No basename, suffix, or subtree is exempt. The scanner also refuses an unplanned immediate child under `cells/` rather than producing an unmapped finding.

**Evidence.** A positive control commits an operator canary as a valid agent label, completes the cell, and finds the exact token in `cube/lacuna.sqlite3`. Additional controls place canaries in `lacuna.sqlite3-wal`, in a file named `.run.lock`, and in a relative filename; all are detected. Another adds an unplanned cell directory and receives `scenario-contamination-tree-mismatch`.

## Finding A165-06 — arbitrary recursive scans can follow unsafe files

**Risk.** A linked file could escape the intended tree or change while being read. A large or special file could turn a research check into a denial-of-service surface.

**Repair.** Reused descriptor-bound sidecar reads, refused symlinks, hard links, nonregular members and linked directories, imposed file/member/total-byte/finding limits, made `os.walk` enumeration errors fatal, and compared complete path/metadata signatures before and after reading.

**Evidence.** Tests insert a linked member before final scan and separately replace the entire `cells/` root with a symlink. Both receive `scenario-contamination-member-unsafe`; the member case preserves byte-identical `run.json`, repairs the tree, retries the exact return, and reaches a clean scan. A synthetic traversal error receives `scenario-contamination-scan-failed` instead of silently omitting a subtree.

## Finding A165-07 — source occurrences need exact allowlisting

**Risk.** A naive global search would report the deliberate source copies as leaks or require ad hoc filtering after results exist.

**Repair.** Every token preregisters its exact source paths. The scanner ignores a token only on those paths; every other occurrence counts. Operator-only sources are JSON and rendered Markdown driver; filesystem-only source is one private text file.

**Evidence.** Clean-run tests observe zero unexpected matches despite all twelve deliberate source artifacts (two driver copies plus one filesystem source per cell).

## Finding A165-08 — a digest-only scan record could drift from the tree

**Risk.** Retaining a schema-valid scan without reauthentication would not show later added or changed artifacts.

**Repair.** Scenario audit rebuilds the complete scan using its original timestamp and requires exact equality, including file count, byte count, file-manifest digest, findings, summaries, and status.

**Evidence.** Scenario and bundle audits invoke authenticated scans before rating, sealing, unblinding, report export, and idempotent recovery.

## Finding A165-09 — replicated custody omitted leakage evidence

**Risk.** A single child could retain a scan while a bundle seal/report omitted it, letting aggregate publication hide an affected block.

**Repair.** Advanced block seal and bundle report to v2. A block seal binds `contamination_scan_sha256`; the aggregate retains per-block and per-observation status/count plus total clean/leak blocks.

**Evidence.** The primary bundle lifecycle test deliberately leaks one cross-cell operator token in block one, seals both blocks, and verifies one clean and one leak-detected block in JSON and CSV-compatible output.

## Finding A165-10 — canary code would further overload the scenario state machine

**Risk.** `scenarios.py` already owns assignment, clone, topology, returns, ratings, reports, and recovery. Embedding secure traversal and token policy there would make future review harder.

**Repair.** Extracted `src/lacuna/contamination.py` with a narrow pure-artifact interface. Scenario code owns when the plan/scan may exist; the module owns their deterministic content and authentication.

**Evidence.** Focused module integration, schema, CLI, scenario, bundle, and clean-extraction tests exercise the boundary.

## Residual risks

- Exact-token absence cannot detect paraphrase, latent preference transfer, or private information that never contains the token.
- A hostile parent can omit calls, communicate outside retained artifacts, or discard an unwitnessed run.
- A positive match does not identify whether a provider, human, parent, tool, or copy operation caused it.
- Provider memory, tool denial, filesystem sandboxes, and context creation remain external.
- Complete retained-cell scanning adds bounded local I/O and can refuse a scenario whose individual file, total cell tree, or finding count exceeds the preregistered limits.
- File contents and relative file pathnames are scanned; an exact token used only as the name of an empty directory remains outside this v1 boundary.
- A token can slightly alter a coordinator’s context even when never leaked; use identical control construction across all cells.
- Canaries do not prove narrative quality or isolate which component of role separation caused an outcome.

## Acceptance disposition

Rev0165 is acceptable when all retained tests pass in source and clean extraction; every new schema validates; positive and clean controls behave exactly; scenario/bundle reports bind findings; unsafe-member refusal is nonadvancing and retryable; documentation and manifest membership pass; and database schema 8/event schema 1 remain unchanged.
