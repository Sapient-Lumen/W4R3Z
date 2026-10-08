# rev0018 web/public-overlap notes — TRANSFER-SIZE-PROVENANCE-01

Scope:

```text
U-69  — peer-controlled TransferRequest filesize replacing queued download size.
U-107 — upload sender reads not clamped to advertised remaining transfer size.
U-198 — upload authorization/readability checks path-based rather than opened-inode/handle-bound.
```

## Searches performed

Representative targeted searches:

```text
site:github.com/nicotine-plus/nicotine-plus upload sender reads not clamped advertised size FileOffset UploadFile size
site:github.com/nicotine-plus/nicotine-plus transfer-start filesize expand queued download TransferRequest filesize
site:github.com/nicotine-plus/nicotine-plus upload file inode path replacement shared file race
site:github.com/nicotine-plus/nicotine-plus FileOffset upload size EOF short read transfer
site:github.com/nicotine-plus/nicotine-plus "FileOffset" "upload"
site:github.com/nicotine-plus/nicotine-plus "TransferRequest" "filesize"
site:github.com/nicotine-plus/nicotine-plus "symlink" "shared" "file not shared"
```

## Direct-match result

No direct public Nicotine+ report was found in this pass for the combined invariant:

```text
replacement shared-file path opened at F-init + advertised size retained from earlier state + upload read not clamped to remaining advertised bytes
```

No direct public report was found for the narrower exact phrase shapes:

```text
unclamped UploadFile read
peer TransferRequest filesize expands queued download size
opened upload inode/handle not bound to authorization
```

## Public-adjacent material

Public transfer-lifecycle adjacency exists and prevents any "clean novelty" wording.

- Nicotine+ issue #2447 describes upload-completion anomalies where uploads can appear complete on one side while failing or aborting near completion on the other side.
- Nicotine+ issue #653 describes transfer initiation/queue-response timing and transfer connection negotiation behavior.
- Nicotine+ issue #3638 shows current public filesystem/share-adjacent behavior around symlink/NFS shares.
- Nicotine+ issue #48 shows older public file-not-shared/permissions/folder-download symptoms.

## Decision

```text
U-69: candidate no direct public match found / transfer-lifecycle adjacent.
U-107: public-adjacent transfer completion/FileOffset robustness.
U-198: public-adjacent filesystem/share behavior, no direct inode-binding report found.
```

rev0018 therefore retains TRANSFER-SIZE-PROVENANCE-01 in the audited backlog. It is not promoted into the strict/high-quality document.
