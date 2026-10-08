# Meta 0418 — Case-packet matrix, source-key registry, and middle-form dispatcher test

## One-line thesis

After the third applied cross-boundary packet, the archive should compare case packets through a generated matrix and a keyed source registry rather than forcing readers to reconstruct form-choice logic from prose alone.

## Why this matters

Rev0716 created a source / metadata spine and added the thin shared-service contrast. That made machine-readable status legitimate, but the applied packets still lived mostly as prose. Rev0717 adds a middle case and turns the first three applied packets into comparable matrix objects.

## Reconstruction rule

- Keep applied case-packet facts in `metadata/case_packets.json`.
- Render case comparisons into `generated/CASE_PACKET_MATRIX.json`.
- Render front-door, dispatcher, first-citation, and applied-case routing into `generated/CANON_MAP.json`.
- Keep source keys in `sources/source_keys.json` and require metadata source keys to resolve there.
- Use case-matrix recurrence before merging the `812`–`824` cross-boundary chain.

## Failure modes

- **prose-only routing**: requiring a reader to remember which case used which live chain notes.
- **loose source keys**: treating metadata source keys as labels without a registry.
- **premature chain merge**: collapsing `812`–`824` because three cases exist, before asset and contract packets test `822` and `823`.
- **form analogy drift**: copying the London verdict into basin or shared-service cases without re-running `848`.
- **matrix theater**: generating a comparison table that is not tied to actual note files, sources, and status metadata.

## Anti-theater tests

1. Does every case in the matrix point to a real archive note?
2. Does every case source key resolve in `sources/source_keys.json`?
3. Can the matrix show why `849`, `850`, and `851` choose different forms?
4. Can the canon map identify first-citation notes without rereading the archive?
5. Does lint fail when case, source, status, and archive surfaces drift apart?
