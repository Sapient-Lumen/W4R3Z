# Risk register — rev0086

Main risks addressed:

- Native artifact selected because provenance/corpus/quarantine were each valid in isolation.
- Python fallback route missing at selection time.
- Fallback chosen but not journaled across restart.
- Quarantined native artifact rediscovered as fresh after restart.
- Promotion back to native dropping old fallback/quarantine memory.
- Digest drift between selection, corpus, quarantine, and budget evidence.
- Same-sequence fork or rollback in native selection / fallback / promotion memory.

Remaining risks:

- No production native ABI.
- No production loader.
- No sanitizer runner beyond toy posture checks.
- No live I2P/SAM transport.
