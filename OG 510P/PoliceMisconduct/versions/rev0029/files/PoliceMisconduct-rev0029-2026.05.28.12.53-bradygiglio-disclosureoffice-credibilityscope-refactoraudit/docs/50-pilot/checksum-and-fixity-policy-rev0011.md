# Checksum and fixity policy — rev0011

Rev0011 introduces checksum debt rather than checksum claims.

A payload hash is required before any payload-derived claim, summary, excerpt, or status proof can become public. The required default hash algorithm is SHA-256. When payload capture is impossible, a future operator must create an explicit no-fixity exception receipt and a public missingness warning.

## Do not silently overwrite

If a URL returns different bytes later, the cube must create a new source-version event. The old payload hash, old citation context, and any downstream dependency edges remain part of the record.

## Why no hashes yet?

This revision intentionally does not download or bundle public PDFs. The cube first establishes the ethical and operational gate: public records may contain names and facts that are legal to access but unsafe to mirror or summarize without privacy review.
