# Common Data Formats interoperability checklist

## Ballot Definition (BD)
- [ ] Use NIST SP 1500-20 BD CDF for ballot styles and contest structure.
- [ ] Hash and bind BD into EPB.

## Cast Vote Records (CVR)
- [ ] CVRs (if produced) link to BD hash and device identifiers.
- [ ] CVRs are hash-chained and committed to the transparency log.

## Election Results Reporting (ERR)
- [ ] Results published in a structured ERR format.
- [ ] DisclosurePolicy enforces minimum cell sizes / privacy budget.

## Election Event Logging (EEL)
- [ ] Election event logs are produced and hashed.
- [ ] Sanitized logs and hash commitments are published.

## Cross-referencing
- [ ] All published artifacts use content-addressed hashes.
- [ ] Evidence bundles include hashes + inclusion proofs.
