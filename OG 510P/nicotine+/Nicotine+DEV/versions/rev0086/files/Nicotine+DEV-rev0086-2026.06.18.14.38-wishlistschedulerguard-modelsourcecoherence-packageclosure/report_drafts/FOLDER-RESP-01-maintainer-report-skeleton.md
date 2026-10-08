# FOLDER-RESP-01 maintainer report skeleton — audited backlog, not strict-front in rev0014

## Summary

`FolderContentsResponse` carries a response token, but current folder-response acceptance is effectively keyed on claimed username plus folder path. In 3.3.10 and 3.3.x this can queue files for a matching pending folder request even when the response token is wrong. In master, an allowed-response gate by username+folder exists, but the response token is still not compared to the local request token/generation.

## Current behavior witness

```text
maintainer_artifacts/folder-resp-01/test_folder_contents_response_binding_and_parse_order_reproducer.py
```

Observed result:

```text
github-tag-3.3.10: 5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

## Boundary

Peer-driven folder-download integrity / stale-response / availability hardening. Not code execution and not standalone file disclosure.

## Suggested regression direction

- Store and check request token/generation for pending folder requests.
- Keep source/folder allowed-response gating.
- Reject wrong-token responses without consuming the pending request.
- Avoid materializing irrelevant returned folders before request/scope checks.
- Preserve legacy empty-response fallback.

## rev0014 presentation decision

Keep in audited backlog. Do not use as a strict/front-lane report unless a stronger current-master consequence is later proven and public/maintainer overlap is rechecked.
