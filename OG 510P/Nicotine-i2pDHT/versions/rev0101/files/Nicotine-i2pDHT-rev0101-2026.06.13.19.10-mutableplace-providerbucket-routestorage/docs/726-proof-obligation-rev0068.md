# Proof obligations — rev0068

rev0068 expects local verification to show:

- archive journal accepts only when settlement/archive/prune agree;
- archive journal rejects contradiction drops and digest drift;
- prune replay rejects generation rollback and memory drops;
- closure audit rejects boundary drift and same-sequence forks;
- archivejournalfold passes and preserves the rev0067 predecessor audit.

These are baby-cube obligations, not production guarantees.
