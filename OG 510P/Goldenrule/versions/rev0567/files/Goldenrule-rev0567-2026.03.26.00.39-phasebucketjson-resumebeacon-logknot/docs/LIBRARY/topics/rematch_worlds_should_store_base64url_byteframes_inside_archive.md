# Rematch worlds should store base64url byteframes inside the archive

## Claim

Once the archive already preserves the packed family10 decision-packet codec, the next smaller in-archive form is to serialize that packed payload as a raw byteframe in a base64url string rather than as a JSON numeric array.

## Why

The packed tier already removed most semantic redundancy:
- finite probe payloads already collapse to tiny codes,
- repeated decimal scalars already collapse to shared atoms,
- repeated-value weight profiles already collapse to grouped masks,
- and repeat prefixes already collapse to raw local-prefix bytes.

After that point, a noticeable fraction of the remaining durable size is just JSON wrapper overhead:
- list brackets,
- commas,
- and decimal integer text around payload bytes that are already semantically compressed.

A byteframe removes that wrapper while keeping the same underlying codec. The archive still needs only one executable expander path, because byteframes rehydrate back to the packed form exactly and then continue through the existing packed -> micro -> archive-local -> standalone expansion path.

## Operational rule for the inheritor

Inside this archive:
- use `byte_seed` for first writes when the byteframe codec is present **and** the measured codec frontier says it is actually smallest for the packet,
- use `byte_reference` for repeats when the byteframe codec is present,
- keep numeric packed arrays as the fallback tier for debugging or manual inspection,
- and keep standalone references only for export outside the archive.

## Practical consequence

This change is deliberately narrow. It does **not** add a new semantic representation. It only changes the local storage wrapper around the already-approved packed payloads, which is why it is worth keeping:
- smaller archive writes,
- exact round-trip reconstruction,
- and less new conceptual burden than inventing a fresh semantic codec.
