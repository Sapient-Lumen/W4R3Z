# Current removable-media post-detach redaction surfaces

The post-detach lane now uses an allowlisted support projection rather than relying only on forbidden token searches.

## Support-visible fields

Allowed support fields are:

- lane family and phase;
- reason code;
- state label;
- digest facts;
- bounded retry guidance;
- fresh-authority instruction;
- explicit false booleans for forbidden surfaces.

## Forbidden surfaces

The support projection must not expose raw media paths, raw locators, raw handles, untrusted filenames, host identity, body text, full text, or secret material. Backend evidence may record FreeBSD control digests and boolean posture, but it also stays out of raw path/device reopen authority.


r529 adds `removable.media.local.post_detach.export.bundle.deletion.receipt` so export cleanup is a terminal, CAS-ledgered transition rather than a flag on access.

Last updated: 2026-05-30r521
