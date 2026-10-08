# OCI image-layout blob path / closure boundary excerpt — rev0069

Source: Open Container Initiative Image Specification v1.1.1, `image-layout.md`.  
Accessed: 2026-06-18T15:08:00-04:00.  
Web evidence reference: `turn766217view1`.

This is a bounded excerpt note, not a full or complete capture of the specification.

Bounded facts used:

- Image-layout blobs are stored beneath `blobs/<algorithm>/<encoded>` and their content must match the referenced digest.
- The algorithm and encoded names follow descriptor grammar.
- General OCI layouts may contain blobs not referenced by an index.

Project boundary: LLMPoetry’s D002 artifact rejects unreferenced blobs as a stricter closed-world poem constraint; that rule is not represented as an OCI-wide requirement. This snapshot supports path and provenance mechanics only.
