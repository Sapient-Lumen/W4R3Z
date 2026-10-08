# Research — rev0165

## Research question

Can Lacuna make the context-isolation confound in its own Gwern-style experiment easier to falsify—without claiming that a clean local check proves provider forgetting or turning failed controls into an excuse to rerun unfavorable conditions?

## Result in this revision

Mechanically, yes.

Rev0164 made the strongest treatment explicit: fresh checkpoint roles, a compact winner-only capsule, optional bound public history, and one fresh source-bound continuation dispatch. The scenario runner could reject reused declared context IDs and malformed topology. It still had no positive control for two ordinary operational failures:

- the parent or coordinator copies private context into a nested model call; or
- a supposedly card-only worker reads an unrelated shared file.

Rev0165 preregisters one exact token for each channel in every cell, scans retained experiment artifacts before rating, and preserves the result through unblinding and replicated bundle sealing.

## Why two canaries

An operator-only canary tests whether exact bytes known to the cell coordinator appear in model-facing or transcript-bearing artifacts. It can reveal whole-driver pasting, accidental prompt assembly, cross-cell copying, or exact context carryover that surfaces in output.

A filesystem-only canary tests a stronger host claim. Its token exists only in an unrelated private file; the driver exposes only path and digest. Appearance in output is evidence that the bytes crossed the intended card-only boundary by some route.

The controls are deliberately semantically inert. They should not influence story reasoning except through their mere presence in private coordinator context. Every condition receives equivalent construction.

## Preregistered order

The relevant causal order is:

```text
assignment and tokens fixed
    → cells executed and exact outputs frozen
    → exact artifact scan frozen
    → blind packet compiled
    → ratings frozen
    → condition mapping and scan findings joined
```

This order prevents three easy cheats:

1. choosing a canary after seeing output;
2. deciding whether to scan after seeing ratings; and
3. rerunning only leak-detected conditions.

A replicated bundle additionally seals every child scan digest before any block unblinds.

## Mechanical endpoints

Rev0165 adds directly measurable outcomes:

- exact unexpected canary occurrence count;
- scope (`operator-only` or `filesystem-only`);
- owner and observed opaque cell;
- same-cell versus cross-cell classification;
- exact retained artifact path;
- per-cell own/foreign count and status;
- block-level clean/leak status;
- exact scan and file-manifest digests; and
- whether scan compilation refused due to an unsafe or changing artifact tree.

These endpoints complement, rather than replace:

- declared context/invocation identities;
- checkpoint/narrator topology;
- exact dispatch/capsule digests;
- cube verification and event-count outcomes;
- blind human ratings; and
- external cost/latency/provider logs.

## What a positive result means

An exact random token appearing outside its source allowlist is hard to explain as ordinary prose coincidence. It supports the statement:

> These exact preregistered private bytes crossed into this retained artifact.

It does not establish which component caused the transfer. A human could paste it; a parent could over-share; a tool could read it; a provider could retain context; or a test adapter could copy it.

The classification helps locate the boundary:

- same-cell operator leak: private coordinator bytes reached its own retained outputs;
- cross-cell operator leak: exact bytes crossed experimental cells;
- same-cell filesystem leak: unrelated file bytes reached its own outputs;
- cross-cell filesystem leak: both filesystem and cell boundaries were crossed.

## What a clean result means

Only this:

> No preregistered exact canary was found outside its allowlisted source in the frozen local experiment artifacts.

It does not rule out:

- semantic or paraphrased leakage;
- latent preferences carried in provider memory;
- a worker reading the file but not repeating the token;
- unrecorded calls or outputs;
- extra information sent outside retained dispatches;
- hidden provider tools/logs; or
- a falsified whole run before external commitment retention.

Canaries are asymmetric: strong when positive, weak when negative.

## Why keep contaminated cells

Dropping a leak-detected cell would condition the dataset on a post-treatment operational outcome. Rerunning it until clean would understate real protocol failure and could improve only the treatment with the most complicated orchestration.

Rev0165 therefore makes leakage an included result. Blind raters score the output without seeing the finding; later analysis can report all observations, stratify descriptively, or run a preregistered sensitivity analysis. Lacuna itself computes no causal correction.

## Scan scope as an experimental choice

The final scan covers the complete retained cell tree, including role sidecars, transcripts, cube metadata, accepted SQLite state, and database sidecars. This closes a false-negative channel: a private token can enter a mechanically valid claim, source, agent label, or event without appearing in the player transcript.

- kernel verification answers whether the represented state changed consistently;
- canary scanning answers whether exact private bytes occur anywhere in the retained cell evidence;
- the two checks are complementary rather than substitutes.

The scan includes cooperative lock files but still excludes empty-directory-only names, artifacts outside `cells/`, provider memory, and unretained transport. A future hostile-host study may add a broader filesystem image or provider-side telemetry. That would be a separate treatment and trust boundary.

## Hypotheses

H12. Operator-only canaries will reveal accidental whole-driver or parent-context over-sharing more often in human/weak-model orchestration than in a generated worker-safe dispatch workflow.

H13. Filesystem-only canaries will distinguish shared-workspace/read-only workers from card-only empty-directory workers in at least some live hosts.

H14. Role-separated conditions with fresh calls and card-only directories will have fewer exact findings than serial/shared-workspace conditions, while clean scans will remain insufficient to establish semantic independence.

H15. Automatically retaining leak-detected cells will produce a less flattering but more reproducible estimate of orchestration reliability than retry-until-valid practice.

H16. A small exact-token control will add little narrative-quality variance relative to the much larger context/topology interventions, but this should be checked rather than assumed.

These are hypotheses, not release findings.

## Recommended live pilot

For each preregistered scenario block, compare two host implementations while keeping the model and cards fixed:

1. shared repository, read-only worker, declared fresh context;
2. empty card-only directory, unchained fresh API/subagent call.

Retain:

- raw worker request/response bytes;
- provider response/thread IDs;
- tool and filesystem settings;
- scenario canary plan/scan;
- exact role dispatches;
- blind ratings; and
- whether a token appeared, whether the worker mentioned unrelated files, and whether semantic rejected-future canaries appeared.

The exact canary endpoint should be reported separately from semantic-leak judgments and narrative ratings.

## Gift relevance

For Gwern, this turns one of the essay’s central implementation caveats—“forget the detailed future plot”—into a more honest experimental boundary. Lacuna still cannot make ChatGPT forget. It can now expose some cases where a claimed reset plainly failed in retained bytes, and it prevents the experiment from quietly deleting those failures.

For an ordinary player, nothing changes. She still says “Will you DM?” The canaries exist only in a backstage research run.
