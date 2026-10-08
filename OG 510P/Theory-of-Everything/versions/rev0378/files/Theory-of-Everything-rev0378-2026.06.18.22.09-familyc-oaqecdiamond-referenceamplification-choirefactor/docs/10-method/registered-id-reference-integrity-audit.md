# Registered ID-reference integrity audit

This audit scans registered executable ledgers for list-valued ID references and checks whether each referenced ID exists in the registered route-support stack or core archive ledgers. It was added after a stale perturbative resummation reference used an old `LOP-*` prefix while the live loop/counterterm rows used `LCT-*`.

The audit is archive-control only. It does not promote any route; it prevents stale handles from hiding in otherwise schema-valid ledgers.
