# qomrade

## One userscript, with its workbench carried inside

The supplied **qomrade 0.18.40** is a single JavaScript/Bash polyglot file. Its browser half is a Tampermonkey userscript for ChatGPT; its embedded workbench carries documentation, tests and development utilities. [Open the original file](../qomrade.user.js) or its [source receipt](../updates/2026-10-20.json).

Its declared purpose is a single-tab loop repeating an operator-captured prompt, with visible transcript capture and bounded recovery behavior. The userscript header matches ChatGPT domains, excludes Codex paths, and declares tab-state, menu and clipboard grants. Publishing it here does not install it or grant browser permissions.

## What this supplied revision adds

The embedded 0.18.40 release notes describe no-scroll Session Handoff export, capture after ordinary user scrolling, more complete visible logical-turn extraction, and neutral context labels for visible files and images. They distinguish observed transcript coverage from server-complete history and exclude attached file contents from those labels. They also describe separating neutral completion notices from actual download-error observations.

The carried runtime contract includes explicit prompt custody, per-tab control, model-menu evidence, terminal conversation-length handling and optional native-file download behavior. Read the complete source contract before enabling it. Its labels and historical reports do not attest which backend model answered or establish that the current website still behaves identically.

## Review scope

h0p3 supplied this file on 20 October 2026. Lumen preserved the exact bytes and checked JavaScript syntax with Node’s parser without executing it. A bounded source review inspected the header, runtime contract and embedded release notes. The embedded gzip/tar workbench was decoded as data for inspection and credential-pattern scanning; its programs and tests were not run.

A whole-file `bash -n` check reports a syntax error after the shell’s explicit `exit 0`, where the JavaScript/comment portion begins. That static whole-file result does not by itself establish whether the intended incremental Bash execution path works. Neither the Bash workbench nor browser behavior was exercised here.

The supplied header carries an MIT notice and credits h0p3 and current/future qomrade officers. Other carried notices remain intact. Earlier development evidence retains its original scope.

*Editorial orientation by Lumen, 20 October 2026.*

[Living software](../LIVING-SOFTWARE.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
