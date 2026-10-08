# Upstream AI contribution boundary — rev0073

## The policy that changes the cube's operating model

Nicotine+'s current `CONTRIBUTING.md`, observed June 17, 2026, says that contributions generated or co-authored by language models or AI coding tools are not allowed. It permits AI assistants only for learning, guided codebase research, and concept exploration, and says an upstream contribution must not contain generated code, text, images, or other media.

The same document asks contributors to discuss non-trivial changes in an issue or discussion before opening a pull request. The project's `SECURITY.md` routes actual vulnerabilities through the repository Security tab and identifies `3.3.x` as the supported release series.

## Consequence for this cube

This cube is a **research-only instrument**. It can:

```text
- map code and protocol state;
- construct local hypotheses;
- run disposable experiments and witnesses;
- compare source revisions;
- identify contradictory evidence;
- help a human decide where to investigate independently.
```

It cannot supply material for direct upstream submission. In particular, a user must not copy or lightly rewrite generated:

```text
- patches or diffs;
- test code;
- issue or vulnerability-report text;
- pull-request descriptions;
- comments, documentation, or images.
```

The human-safe workflow is:

1. Use the cube to choose a question worth investigating.
2. Independently reproduce it from upstream source without relying on the generated implementation.
3. Personally understand the behavior and decide whether it is actually a bug.
4. Discard the cube's proposed wording and code.
5. Write, test, and explain an original solution personally.
6. Follow upstream's discussion, issue, pull-request, or Security-tab process as appropriate.

## What was wrong in earlier revisions

Earlier cube files repeatedly described generated packets with labels implying that they were ready to be sent to maintainers or filed. Even where individual documents included caveats, the aggregate navigation encouraged a submission pipeline. That is incompatible with the current upstream policy.

Rev0073 does not rewrite historical evidence because doing so would corrupt provenance and old manifests. Instead it:

```text
- replaces current entrypoint language;
- adds explicit landing-page warnings for report drafts and maintainer artifacts;
- inventories historical readiness labels;
- marks all generated code/text as research-only;
- changes the queue from “prepare a filing” to “resolve a research question.”
```

Historical filenames containing readiness labels remain as archival facts. Their names are not authorization to submit their contents.

## Boundary linter

`tools/audit_rev0073_research_boundary.py` checks that the current surfaces do not carry the old readiness labels and that the research-only/human-authorship boundary is visible. It inventories the historical occurrences without failing merely because archived evidence exists.

This split is intentional:

```text
current navigation: policy-gated
historical evidence: immutable and inventoried
```

## Security-report nuance

The AI prohibition applies to generated content regardless of whether the upstream route is public or private. A vulnerability report is still contribution text. The cube may help a human learn where to look, but a human who chooses to report must independently establish the facts and author the report.

## Mission correction

The heart of the cube is no longer “produce packets to submit.” It is:

> Reduce uncertainty about peer/server-controlled state transitions, preserve a reproducible research record, and hand a human a smaller set of questions they can independently verify and solve within upstream's rules.
