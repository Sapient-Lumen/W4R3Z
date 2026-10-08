# Proof obligations rev0032

rev0032 must show:

- scopeledger accepts diverse exact-scope joined observations;
- scopeledger rejects replay, cross-scope joins, failed probe ledgers, and open proof debt unless explicitly watch-listed;
- storedebt accepts sufficient diverse storage evidence;
- storedebt preserves replica debt, custody debt, tombstone pressure, replay pressure, and fork pressure;
- samtrace accepts scope-bound shadow sends and rejects cross-request, cross-object, and rejected-egress sends;
- scopefold keeps rev0032 surfaces visible and preserves the rev0031 foldmap predecessor.
