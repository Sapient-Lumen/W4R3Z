# FOLDER-RESP-01 — FolderContentsResponse token and parser-ordering proof (rev0014)

## Decision

**U-167 is source-confirmed and maintainer-test confirmed, but not promoted to the strict document in rev0014.**

The root is real: a `FolderContentsRequest` carries a local token, and `FolderContentsResponse` echoes a token, but the download-side request-consumption path is keyed on claimed username plus folder path rather than the stored local request token. The supporting parser/control-flow rows are also real. The family remains in the audited backlog because its current impact is availability / folder-download integrity / confusing stale-response behavior, and because public folder-download issues plus master/future allowed-response gating make the novelty/priority less clean than U-123, PB-01, or SEARCH-RESP-01.

## Scope

```text
Lead row:     U-167  FolderContentsResponse accepted by username+folder while ignoring request token.
Support row:  U-255  All returned folders are materialized before requested-folder filter.
Support row:  U-260  Nonmatching response can consume/cancel a pending request without queueing files.
Support row:  U-268  Rejected/unmatched response still processes a peer-controlled directory prefix.
Separate:     U-256  FolderContentsRequest request-to-response echo/budget family.
Alias:        U-272  Duplicate/alias of U-256.
```

## Source-lane result

```text
github-tag-3.3.10: affected; handler ignores msg.token and queues files for matching username+folder.
github-branch-3.3.x: affected; same handler behavior, with broader 128 MiB uncompressed parser cap.
github-branch-master: partially gated; parser requires allowed username+folder, but still does not bind response token to local request token and still preserves wrong token in an allowed response.
```

## Current-behavior tests

The rev0014 reproducer ran against all three source lanes:

```text
github-tag-3.3.10: 5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

Test file:

```text
maintainer_artifacts/folder-resp-01/test_folder_contents_response_binding_and_parse_order_reproducer.py
```

The witness proves current behavior, not desired fixed behavior:

- A peer-controlled response token is parsed and preserved without comparison to the local requested-folder token.
- Pending folder responses with the wrong token are consumed by claimed username plus folder path.
- 3.3.10/3.3.x enqueue the returned matching files from such a response; master consumes the request and leaves parsed contents for the download-dialog/UI path.
- Nonmatching returned folders are decompressed and materialized before the later requested-folder filter ignores them.
- A response with no matching returned folder cancels the pending request and does not queue files.
- Rejected/unmatched responses still process a compressed peer-controlled directory prefix before rejection.

## Impact boundary

This is **not code execution** and not a standalone confidentiality bug. It is best framed as request/response binding and parser-ordering hardening for peer-driven folder-download behavior. The practical impact is stale/malformed response acceptance, confusing folder-download state, premature pending-request consumption, and avoidable parse/allocation work while a folder request is pending or partially accepted.

## Public-overlap status

Targeted public searching found folder-download bug and UX history, including reports where right-click folder download did nothing or only selected one file. I did not find a direct public report of the exact `FolderContentsResponse` token-nonbinding invariant. Treat this as **public-adjacent / no direct exact match found**, not as proven novel.

## Fix shape

A coherent fix should not be just "check token somewhere". It should preserve current direct/indirect compatibility and master's allowed-response improvement while reducing stale-response and parser-ordering effects:

```text
1. Store requested-folder generation/token per username+folder request.
2. Bind FolderContentsResponse acceptance to username + folder + token + request-generation where compatibility allows.
3. Keep master's AddAllowedResponse source/folder gate, but extend or pair it with local token/generation checks.
4. Treat wrong-token responses as rejected without consuming the pending request; optionally log and wait for timeout/retry.
5. Do not cancel a pending request merely because a response contains no matching returned folder.
6. Add a prefix budget for the response directory before allocating large directory strings.
7. Avoid materializing all returned folders when only one requested folder is needed, or add folder/file/component budgets before full materialization.
8. Preserve legacy latin-1 empty-response retry semantics.
```

## Evidence files

```text
evidence/rev0014-folder-response-reproducer-run.txt
evidence/rev0014-folder-response-probe.jsonl
evidence/rev0014-folder-response-source-trace.md
evidence/rev0014-web-public-overlap-folder-response.md
data/rev0014_folder_response_probe_summary.csv
data/rev0014_folder_response_coherence_refactor.csv
```
