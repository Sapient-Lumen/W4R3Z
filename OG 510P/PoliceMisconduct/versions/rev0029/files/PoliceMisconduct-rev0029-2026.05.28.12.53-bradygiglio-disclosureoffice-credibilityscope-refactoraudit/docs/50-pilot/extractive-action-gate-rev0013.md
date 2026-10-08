# Extractive action gate — rev0013

Rev0013 separates transport/fixity work from content extraction.

Transport/fixity work includes fetching bytes into quarantine, recording redirect chains, observing MIME type, and computing SHA-256. Extractive work includes text extraction, OCR, named-entity recognition, legal-effect extraction, content summary, and public display.

The cube may eventually perform transport/fixity work before content review. It may not perform extractive work until privacy and claim gates open.

Hard stops remain active for person records, incident records, lawsuit merits records, settlement amounts, and public current-status claims.

