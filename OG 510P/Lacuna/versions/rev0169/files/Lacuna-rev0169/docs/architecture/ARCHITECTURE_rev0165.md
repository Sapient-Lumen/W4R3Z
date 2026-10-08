# Architecture — rev0165

## Purpose

Revision 0165 adds a falsification layer to Lacuna’s comparative scenario runner. The scenario contracts already required declared context separation, fresh post-checkpoint narrator identifiers, exact role order, and hidden assignment custody. Those declarations were useful but could not reveal whether a parent pasted too much context, a worker read unrelated files, or bytes crossed between cells.

Rev0165 preregisters exact semantically inert canaries before any cell runs, compiles one private scan after all cell artifacts are frozen and before blind rating, and binds the result into single-run and replicated reports. It does not turn a clean scan into an isolation certificate.

Database schema remains 8. Immutable event schema remains 1. All new objects are private experiment/exchange custody.

## Experiment path

```text
verified seed + fixed scenario capsule
        │
        ▼
private condition assignment
        │ deterministic run/cell/seed binding
        ├── operator-only canary per cell
        └── filesystem-only canary per cell
        │
        ▼
scenario run v2 + cell driver v2
        │ one active cell at a time
        │ exact worker returns + receipts + managed sidecars
        ▼
all four cells frozen
        │
        ▼
contamination scan v1
        │ exact source allowlists
        │ content / relative-path surfaces
        │ same-cell / cross-cell findings
        │ retained-file manifest digest
        ▼
blind rating packet v1
        │ no plan, tokens, mapping, or findings
        ▼
fixed ratings
        ▼
scenario report v2
        │ condition-mapped scan summaries
        ▼
optional bundle block seal v2
        │ scan digest bound before any block unblinds
        ▼
bundle report v2
```

The scan is deliberately ordered before blind-packet publication. Raters therefore cannot be influenced by a known clean/leak status, and the parent cannot wait for ratings before deciding whether to retain the scan.

## Canary plan

`lacuna.scenario-contamination-plan.v1` is generated from:

- scenario run ID;
- capsule ID;
- exact committed assignment digest;
- assignment randomization seed;
- opaque cell label; and
- canary scope.

Tokens use a domain-separated SHA-256 derivation and a fixed opaque ASCII form. The plan contains exactly two records for every assigned cell, in assignment order:

1. `operator-only` — exact token is allowlisted only in the cell’s private JSON and Markdown driver;
2. `filesystem-only` — exact token is allowlisted only in `PRIVATE-CONTAMINATION-CANARY.txt`.

The filesystem token itself is absent from the driver. The driver exposes only its path and digest to the cell coordinator.

The plan also fixes the scan scope, case sensitivity, file/byte/finding limits, instructions, and nonclaims. It contains no filename, suffix, lock, or subtree exclusion. Scenario audit reconstructs the plan from the retained assignment and compares the complete object, rather than trusting its filename or digest alone.

## Coordinator and worker boundary

`lacuna.scenario-cell-driver.v2` is a private cell-coordinator artifact. It may be supplied to the one isolated context coordinating the whole cell, including a persistent-context control. It must not be forwarded to nested planner, judge, compressor, verifier, fresh-narrator workers, or blind raters.

This distinction is intentional:

- the coordinator sees the operator-only token;
- a delegated role should see only its exact Lacuna dispatch;
- a card-only role should not see the filesystem-canary file;
- a persistent monolithic control may retain the operator token in context; and
- the scan asks whether those exact bytes surface unexpectedly in retained artifacts.

A canary therefore pressures prompt hygiene and context/tool boundaries without becoming authority or story content.

## Scan boundary

`lacuna.scenario-contamination-scan.v1` covers every frozen regular file beneath the preregistered `cells/` tree:

- private drivers;
- model returns and receipts;
- managed ordinary-turn and checkpoint-run sidecars;
- transcript-bearing artifacts; and
- cloned cube metadata, the accepted SQLite database, retained SQLite sidecars, and cooperative lock files; and
- other retained regular files created by the cell workflow.

Cube verification and canary scanning answer different questions. Verification establishes ledger/projection integrity; it does not show that an otherwise valid claim, source, agent label, event payload, lock file, or SQLite sidecar omitted a leaked private token. The scan therefore includes all retained regular-file contents and each file's relative pathname. No basename, suffix, or subtree is exempt.

The scanner:

1. resolves the real `cells/` root under the run;
2. requires its immediate children to equal the preregistered opaque cell set exactly;
3. walks each planned cell without following links and raises on any enumeration error;
4. rejects symlinked directories and any scanned symlink, hard link, nonregular file, or oversized member;
5. reads through the hardened descriptor-bound sidecar primitive;
6. computes one exact file manifest of relative path, byte size, and SHA-256;
7. searches every token case-sensitively in both file content and relative pathname, including cube databases, database sidecars, and lock files;
8. ignores content occurrences only at the token’s preregistered source paths; path occurrences are never allowlisted;
9. records exact path, match surface, owner, observed cell, scope, classification, and count;
10. enumerates the tree again and refuses if path/metadata signatures changed; and
11. derives deterministic per-cell and overall status.

The scan document stores the file-manifest digest rather than every file digest, keeping the exchange object compact. Authentication rebuilds the complete scan against the current frozen tree and requires exact object equality.

## Failure and retry

Final cell acceptance writes its exact return and receipt before compiling the scan, but `run.json` remains authoritative. If scan compilation refuses, the manifest is not advanced and the new files remain unreferenced. After removing an unsafe unreferenced member or correcting the host process, the parent can retry the same exact return; immutable write-or-verify behavior accepts identical retained bytes.

Once a scan exists, adding, deleting, or changing a scanned artifact makes later scenario audit refuse. Ratings and reports live outside `cells/`, so legitimate post-scan workflow does not alter the scan boundary.

## Reporting

Scenario report v2 adds:

- exact contamination-scan digest;
- overall clean/leak-detected status;
- total exact occurrence count;
- condition-mapped per-cell own/foreign counts; and
- per-condition status/count on each cell record.

The blind packet remains v1 because its purpose and information boundary are unchanged. It contains no canary data.

Bundle block-seal v2 binds each child’s exact scan digest before advancing to the next block. Bundle report v2 carries scan digest/status/count per block and contamination status/count per rater-level observation. The descriptive aggregate reports clean blocks, leak-detected blocks, and total exact matches. A leak-detected block remains included.

## Refactor boundary

All canary-specific logic lives in `src/lacuna/contamination.py`:

- deterministic derivation;
- plan validation;
- per-cell driver controls;
- filesystem source generation;
- secure artifact enumeration;
- exact scanning and summaries;
- scan authentication and digests; and
- private Markdown rendering.

`scenarios.py` retains state-machine authority and invokes this module at publication, final-cell acceptance, audit, unblinding, and inspection. `scenario_bundles.py` consumes only the authenticated child scan/report fields. No second scenario state machine, model client, or mutation engine was added.

## Explicit nonclaims

A clean scan does not prove:

- a provider created a genuinely fresh context;
- provider memory was erased;
- tools or filesystem access were denied;
- no semantic or paraphrased leakage occurred;
- the parent supplied only retained inputs;
- unrecorded calls did not happen; or
- role-separated fiction is better.

A positive exact match proves only that one preregistered byte string appeared in one retained non-source file content or relative pathname. It does not identify who copied it or why. An empty directory whose name alone contains a token remains outside this v1 regular-file boundary.
