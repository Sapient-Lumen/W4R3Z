# Storage and GPU lanes

Storage and GPU are lanes, not afterthoughts.

## Storage lane

The storage lane starts as a block store:

- append blocks;
- checksum blocks;
- write journal entries;
- swap manifests atomically where possible;
- recover or fail closed after interruption;
- monitor quota;
- compact only through maintenance tasks.

## GPU lane

The GPU lane is optional acceleration:

- detect adapter/device availability;
- cache shader and pipeline handles;
- track upload/readback cost;
- trace dispatches;
- recover from device loss;
- use CPU fallback when GPU is unavailable or not worth it.

## Non-claim

The baby cube does not implement either lane. It only freezes the expectation
that these lanes have first-class contracts before code arrives.
