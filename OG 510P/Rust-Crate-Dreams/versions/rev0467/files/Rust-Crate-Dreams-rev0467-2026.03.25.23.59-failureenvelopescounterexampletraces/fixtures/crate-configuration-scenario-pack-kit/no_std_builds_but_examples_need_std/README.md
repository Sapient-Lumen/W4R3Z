# no_std_builds_but_examples_need_std

A crate advertises a `no_std + alloc` lane and the library itself builds there, but its examples or helper binaries rely on `std` or host-only features.

This fixture exists to force the pack to keep separate:

- the **core library support claim**,
- the **example/bin/test surface**,
- and the **matrix fidelity** of what was actually observed.

Expected outputs:
- `minimal_supported` or `manual_review_required` scenario classification for the `no_std` lane
- fidelity notes showing examples/tests are only covered under `std`
- receiver-facing warnings rather than a fake blanket `no_std` success claim
