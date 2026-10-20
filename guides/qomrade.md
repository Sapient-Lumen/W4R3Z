# qomrade

## Keep ChatGPT working on a project without prompting every round yourself

qomrade is a **Tampermonkey browser userscript that sustains long-running work in ChatGPT**. Give the conversation a project and qomrade a continuation instruction, and it can keep the work moving through successive rounds of research, writing, revision or software development without you manually sending each next turn.

The point is what can accumulate over those rounds: a researched collection, a developing argument, increasingly refined translations, or successive versions of a software project. Repeating a prompt is the mechanism, not the finished work.

**Who it is for:** people who want ChatGPT to spend many turns developing an ongoing project rather than stop after a single response.

## Look at the kind of work in OG 510P

[OG 510P](../OG%20510P/README.md) makes that distinction concrete. [Parables](../OG%20510P/Parables/README.md) preserves successive searches, selections, rejections and additions to a collection. [The Good](../OG%20510P/The-Good/README.md) develops an argument across a growing archive of chapters. [Conlang Rosetta Stone](../OG%20510P/Conlang%20Rosetta%20Stone/README.md) preserves translation drafts and repeated lexical and grammatical refinement.

These are examples of cumulative project work, not batches of interchangeable answers. They explain the purpose a continuation tool serves. The examples alone do not establish which qomrade revision, if any, produced each historical snapshot.

**Example workflow:** establish a research collection in ChatGPT, including its criteria and existing files. Set a continuation instruction that asks the assistant to pursue the next useful research round, update the collection and notes, and produce an updated archive when appropriate. qomrade sends the same instruction again as the conversation develops; ChatGPT does the research and revision using the context and tools available to it. If enabled, qomrade requests matching native file downloads from completed replies.

## What qomrade contributes

- **Continuation:** captures one operator-written prompt at Start, waits for the reply to finish and settle, and schedules subsequent sends with a configurable gap.
- **Model control:** applies the chosen per-tab model policy before sending. The supplied revision supports Smart Pro, an explicitly pinned model and effort, or following the current ChatGPT selection.
- **Background operation and recovery:** supports work in hidden tabs, bounded recovery from recognized failures, old-rendered-turn trimming and optional safe refresh. Browser suspension can still interrupt it.
- **Generated-file collection:** optionally requests downloads of explicitly named native file controls matching configured suffixes, with .zip as the default. Requesting a download is not proof that the file was saved successfully.
- **Handoff and diagnosis:** exports the observed conversation for session handoff and provides separate developer diagnostics when the controller needs investigation.

It is not an independent research model or a judge of whether another round improved the project. It does not invent new instructions, coordinate tabs, or automatically start another conversation. A conversation-length limit stops the run. The operator still defines the work, reviews the results and decides how to continue.

## Before starting

This modifies the ChatGPT website through a userscript manager. Review its browser grants and runtime contract before installation. Website changes can affect it; W4R3Z has not tested this supplied revision in a live browser. Session Handoff captures observed conversation text, not guaranteed complete server-side history or attached file contents.

The supplied **qomrade 0.18.40** is one JavaScript/Bash polyglot file. The browser half runs the controller; the embedded Bash/Python workbench supports its development, testing and maintenance. [Open the original file](../Maintained%20Tools/qomrade.user.js) or its [source receipt](../updates/2026-10-20.json).

The userscript header matches ChatGPT domains, excludes Codex paths, and declares tab-state, menu and clipboard grants. Publishing it here does not install it or grant browser permissions.

## What this supplied revision adds

The embedded 0.18.40 release notes describe no-scroll Session Handoff export, capture after ordinary user scrolling, more complete visible logical-turn extraction, and neutral context labels for visible files and images. They distinguish observed transcript coverage from server-complete history and exclude attached file contents from those labels. They also describe separating neutral completion notices from actual download-error observations.

The carried runtime contract includes explicit prompt custody, per-tab control, model-menu evidence, terminal conversation-length handling and optional native-file download behavior. Read the complete source contract before enabling it. Its labels and historical reports do not attest which backend model answered or establish that the current website still behaves identically.

## Review scope

h0p3 supplied this file on 20 October 2026. Lumen preserved the exact bytes and checked JavaScript syntax with Node’s parser without executing it. A bounded source review inspected the header, runtime contract and embedded release notes. The embedded gzip/tar workbench was decoded as data for inspection and credential-pattern scanning; its programs and tests were not run.

A whole-file `bash -n` check reports a syntax error after the shell’s explicit `exit 0`, where the JavaScript/comment portion begins. That static whole-file result does not by itself establish whether the intended incremental Bash execution path works. Neither the Bash workbench nor browser behavior was exercised here.

The supplied header carries an MIT notice and credits h0p3 and current/future qomrade officers. Other carried notices remain intact. Earlier development evidence retains its original scope.

*Editorial orientation by Lumen, 20 October 2026.*

[Maintained Tools](../Maintained%20Tools/README.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
