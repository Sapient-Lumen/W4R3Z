# rev0008 U-123 socket/F-connection limbo probe

## Scope

Local non-network harness. It uses Nicotine+ source-lane code paths for `Downloads._transfer_request()`, `Downloads._file_transfer_init()`, `Downloads._file_download_progress()`, and `Downloads._file_connection_closed()`. It does not connect to the Soulseek network and it only opens temporary local incomplete-download files.

## Result matrix

| lane | duplicate requests accepted | second F socket attached | stale first timeout deleted second active mapping | later progress ignored | later close ignored / handle left open | distinct-token control survives |
|---|---:|---:|---:|---:|---:|---:|
| github-tag-3.3.10 | True | True | True | True | True | True |
| github-branch-3.3.x | True | True | True | True | True | True |
| github-branch-master | True | True | True | True | True | True |

## Interpreted invariant

The duplicate-token path is materially stronger than the rev0007 handler/timer proof. The later transfer can reach the F-connection stage and transition to `Transferring`; after the first transfer's stale timer fires, the shared `active_users[username][token]` entry is deleted. Subsequent progress and close callbacks for the second transfer lookup the same `username + token` key, find no active transfer, and return without cleaning the second socket/file session.

The distinct-token control demonstrates the stale first timeout does not inherently break unrelated second transfers: with token 4243 for the second request, the second mapping survives, progress updates `current_byte_offset`, and close cleanup closes/aborts the second session.

## Representative duplicate-token state sequence

The same shape appeared in all three lanes. Compact state for each lane:

### github-tag-3.3.10

| state | active identity for token | second status | second indexed | second socket | second file handle open | second offset |
|---|---|---|---:|---:|---:|---|
| after_second_transfer_request | second | Getting status | True | False | False | None |
| after_file_transfer_init_for_second_token | second | Transferring | True | True | True | None |
| after_stale_first_timeout | None | Transferring | False | True | True | None |
| after_progress_callback_for_second | None | Transferring | False | True | True | None |
| after_close_callback_for_second_socket | None | Transferring | False | True | True | None |

### github-branch-3.3.x

| state | active identity for token | second status | second indexed | second socket | second file handle open | second offset |
|---|---|---|---:|---:|---:|---|
| after_second_transfer_request | second | Getting status | True | False | False | None |
| after_file_transfer_init_for_second_token | second | Transferring | True | True | True | None |
| after_stale_first_timeout | None | Transferring | False | True | True | None |
| after_progress_callback_for_second | None | Transferring | False | True | True | None |
| after_close_callback_for_second_socket | None | Transferring | False | True | True | None |

### github-branch-master

| state | active identity for token | second status | second indexed | second socket | second file handle open | second offset |
|---|---|---|---:|---:|---:|---|
| after_second_transfer_request | second | Getting status | True | False | False | None |
| after_file_transfer_init_for_second_token | second | Transferring | True | True | True | None |
| after_stale_first_timeout | None | Transferring | False | True | True | None |
| after_progress_callback_for_second | None | Transferring | False | True | True | None |
| after_close_callback_for_second_socket | None | Transferring | False | True | True | None |

## Why this belongs with U-169/U-170 but is not identical

U-123 now proves an active transfer-session map integrity failure from a duplicate peer-supplied `TransferRequest` token. U-169/U-170 remain adjacent because F-connection attach/unknown-token behavior shares the same `username + token` lookup boundary. The coherent report should be one transfer-session integrity report, not three separate claims that ask for incompatible changes.

## Fix shape tested by implication

A single dictionary overwrite guard is not enough. The proof uses both activation and deactivation: activation overwrites the key, then stale deactivation deletes whatever object is now mapped at that key. The minimal coherent shape is:

```text
1. Reject or quarantine a second active TransferRequest for the same username+token unless it is demonstrably the same transfer generation.
2. Make _deactivate_transfer() identity-checked: delete active_users[username][token] only when the mapped object is the same transfer being deactivated.
3. Keep FileTransferInit/progress/close compatibility with username+token, but require the found transfer to be in the expected generation/socket state.
```

## Raw evidence

Raw JSONL: `evidence/rev0008-u123-socket-limbo-probe.jsonl`