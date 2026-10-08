## Continuity-escrow review

### Review question
What present-day operator action would silently destroy a later encrypted-backup rescue path even though bytes still appear to exist?

### Required review axes
- **Folder continuity**: original encrypted share still lives in the same Sync state, or the product only sees a later re-add / rebind.
- **Storage-root continuity**: the database world stayed attached to the same storage root and seat, or storage migration / service-account change may have severed it.
- **Secret continuity**: RW and RO secrets are escrowed outside the failing source, or only the encrypted capability is known.
- **Locator continuity**: the product can point to the exact database artifact now, or only promises that it may be discoverable later through logs / support.
- **Failure trigger**: source-peer loss, delete-state convergence, service migration, folder removal, storage cleanup, or unknown.
- **Latent salvage loss**: the recovery option is silently gone even though ciphertext bytes still remain.

### Required warnings
- Removing an encrypted folder from Sync must warn that **future salvage continuity may be destroyed even if encrypted bytes remain on disk**.
- Re-adding the same ciphertext directory must warn that **same-looking path is weaker than same database continuity**.
- Service-account or storage-root migration must warn that **same machine is weaker than same recovery world**.
- Clearing logs or losing storage visibility must warn that **later db-path discovery may collapse even when bytes survive**.

### Output
One reviewed branch sentence: what continuity survived, what continuity was severed, which salvage lane still exists, and which stronger rescue sentence remains blocked.
