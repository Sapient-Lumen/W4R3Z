# Preregistered contamination canaries

A declared “fresh context” is useful metadata, not proof. A model may inherit conversation memory, inspect a shared workspace, receive an oversized parent prompt, or accidentally see another condition’s artifacts. Lacuna rev0165 introduced, and later releases retain, a narrow falsification control to the scenario runner: exact semantically inert canary tokens are fixed before execution, then searched for in retained file contents and relative pathnames before blind rating.

The control is designed to answer a limited question:

> Did either of these exact private byte strings appear somewhere they were preregistered to be absent?

A positive answer is strong local evidence of a boundary failure. A negative answer is not proof of isolation.

## What is created

Every opaque scenario cell receives two unique tokens.

| Scope | Where the exact token begins | What it pressures |
|---|---|---|
| `operator-only` | private `30-driver.json` and `DRIVER.md` | parent prompt hygiene, context carryover, accidental whole-driver delegation, cross-cell copying |
| `filesystem-only` | `PRIVATE-CONTAMINATION-CANARY.txt` only | shared-workspace inspection, card-only/tool-denial claims, unrelated-file reads |

The filesystem token body is not embedded in the private driver. The driver contains only its source path and SHA-256 digest. Both tokens are opaque and semantically inert; they are not story clues, commands, passwords, or provider secrets.

The complete private plan is retained at:

```text
15-PRIVATE-contamination-plan.json
```

It is deterministic from the already committed scenario assignment, run identity, and assignment seed. The plan fixes token identity, owner cell, scope, exact source allowlist, scan limits, instructions, and nonclaims before the first cell result is accepted.

## Operator rule

**Keep the complete private driver at the cell-coordinator boundary.**

The private driver is a coordinator artifact. It may be given to the one isolated context acting as the complete cell coordinator, including a monolithic persistent-context control. It contains the operator-only token precisely so accidental carryover or over-sharing can be detected. Do not forward it to nested checkpoint/narrator workers or blind raters. Give each delegated worker only the minimum condition prompt, generated Lacuna role dispatch, fresh-narrator dispatch, or other bounded input required for that call.

For a card-only worker:

1. create a fresh context;
2. provide only the exact task card or worker-safe prompt;
3. do not expose the scenario directory;
4. do not open `PRIVATE-CONTAMINATION-CANARY.txt`;
5. retain the exact model return; and
6. record honest context, invocation, and topology declarations as before.

For a persistent-context control, the operator token may exist in the coordinator’s context. That is intentional. The scan asks whether the exact token later appears in retained outputs or another cell; it does not assume the control context forgot it.

## When the scan occurs

After the fourth cell return is accepted, but before `70-blind-rating-packet.json` is created, Lacuna:

1. verifies the complete scenario run and all four frozen cells;
2. enumerates the complete frozen retained-file tree under `cells/`;
3. refuses linked, nonregular, multi-linked, oversized, or changing members;
4. requires the `cells/` root to contain exactly the preregistered opaque cell directories;
5. includes each cell’s cloned cube database and SQLite sidecars rather than treating cube verification as a content scan;
6. includes cooperative lock files and applies no basename, suffix, or subtree exemption;
7. fails closed when recursive enumeration reports an unreadable or otherwise skipped subtree;
8. streams exact bytes once through the hardened descriptor-stable sidecar boundary while computing SHA-256 and exact-token counts, and separately scans each file's relative pathname;
9. allows token content only at its preregistered source path;
10. records every other exact case-sensitive content or relative-path occurrence;
11. classifies each occurrence as `same-cell-leak` or `cross-cell-leak`;
12. writes `65-PRIVATE-contamination-scan.json`; and
13. only then compiles the blind-rating packet.

The scan covers private drivers, model returns, cell receipts, managed turn/checkpoint sidecars, lock files, transcripts, cube files, and every other retained regular file beneath the frozen cell trees. It searches both file content and normalized relative file pathnames. Cube integrity is still governed separately by Lacuna’s verification and frozen-cell receipt checks; those checks do not substitute for searching accepted cube content for a leaked token.

## Inspect the result privately

```bash
./lacuna scenario contamination RUN_PATH --format markdown
```

or:

```bash
./lacuna scenario contamination RUN_PATH --format json \
  > private-contamination-scan.json
```

Do not give the plan, source tokens, or scan findings to blind raters. The blind packet intentionally omits them.

A clean result looks like:

```text
Status: clean
Unexpected exact matches: 0
```

A finding records:

- canary ID and scope;
- owner cell;
- cell in which it was observed;
- exact relative artifact path;
- match surface (`content` or `relative-path`);
- same-cell or cross-cell classification; and
- exact occurrence count.

## Findings do not trigger reruns

A leak-detected cell remains part of the study. Lacuna does not delete, repair, silently redact, reassign, or rerun it. The blind raters still evaluate the retained transcript. On unblinding, the scenario report maps each cell’s scan status to its condition.

This rule matters. Otherwise the canary could become a new cherry-picking mechanism: keep resampling until the treatment happens to look clean.

## Replicated bundles

A bundle block can be sealed only after its child is fully rated and its exact contamination scan is authenticated. `lacuna.scenario-bundle-block-seal.v2` binds the scan digest alongside the capsule, assignment, blind packet, and ratings. `lacuna.scenario-bundle-report.v2` exports:

- scan digest and status per block;
- exact unexpected-match count per block;
- contamination status per rater-level condition observation; and
- clean/leak-detected block totals.

All blocks still seal before any block unblinds.

## How to interpret the two controls

| Finding | Supported interpretation | Unsupported interpretation |
|---|---|---|
| operator token in its own output | exact private coordinator bytes reached a retained cell artifact | which product feature or hidden memory mechanism caused it |
| operator token in another cell | exact cross-cell byte transfer occurred | that all semantic information crossed, or that the provider colluded |
| filesystem token in output | exact bytes from an unrelated private file reached a retained artifact | whether a model, parent, tool, or human read the file |
| no exact token found | these exact tokens were absent from scanned artifacts | memory erasure, semantic independence, filesystem denial, or no paraphrased leakage |

Canaries are best treated as falsification pressure, not certification.

## Threat boundary

The control cannot detect:

- paraphrases or semantic leakage that omit the exact token;
- an unrecorded provider call;
- private information supplied outside retained artifacts;
- hidden provider memory that does not surface the token;
- a hostile parent rewriting the whole experiment before external retention;
- provider-side logs, tools, or files that never enter the local run; or
- an exact token used only as the name of an otherwise empty directory; or
- whether a context ID names a genuinely new provider context.

Use canaries together with fresh calls, no conversation chaining, card-only directories, disabled unnecessary tools, exact dispatch retention, honest invocation custody, external commitment witnesses, and blind ratings.

## Recovery

If final scan compilation refuses because the tree contains an unplanned cell directory, symlink, hard link, oversized file, changing member, or traversal error, `run.json` remains at the previous authoritative state. Remove the unsafe unreferenced member or correct the host process, then retry the same exact final cell return. Do not edit the plan, accepted returns, receipt files, or manifest hashes.

After a scan exists, later additions or edits under the scanned retained cell tree make scenario audit refuse. Ratings and aggregate reports live outside that tree and do not alter the frozen scan boundary.

## Minimal parent instruction

```text
Operate this scenario cell as the experiment parent. Keep the private driver and both canary controls backstage. Give each worker only its exact minimal task card or prompt, never the whole driver or scenario directory. Do not open the filesystem-canary file. Record the exact return once. After all four cells are frozen, inspect the authenticated contamination scan privately, retain any findings without rerunning a condition, and give blind raters only the blind-rating packet.
```
