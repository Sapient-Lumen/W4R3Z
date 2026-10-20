# c-toxcore 0.2.22 to 0.2.23 provider-state evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

The exact previous stable c-toxcore provider produced two distinct, mutually friended savedata
profiles. The exact current IoTox provider loaded both without changing Tox identity, profile state,
or friendship, rewrote both, and the old provider read the rewritten semantic state exactly. The
actual source-linked IoTox product then started and stopped cleanly from each old savedata profile,
preserved the same state, and produced saves readable by both provider fixtures. Both fixtures
refused malformed savedata.

The qualification check built old and current sources separately with warnings-as-errors and linked
the product-pinned libsodium. Its output contains no disposable keys, addresses, or savedata. Two
manual runs and `nix build --rebuild` produced the same canonical receipt. The retained receipt is
`2026-08-24-toxcore-provider-upgrade.json`, SHA-256
`0398fb2cc4843a0656644f3cdfeda3e4b81fb35faed3b671aa2aa8799d95a818`.

## Reproduction

```sh
nix build .#toxcoreProviderUpgrade
cat result/provider-upgrade.json
nix build --rebuild --no-link .#toxcoreProviderUpgrade
```

The ordinary full flake check also builds this result as `toxcore-provider-upgrade`.

## Exact nonclaims

This is savedata and product-load compatibility, not a live mixed-provider route. It does not
authorize downgrade, test public bootstrap/relay behavior, cover every historical savedata shape,
qualify a future provider, or replace the remaining two-guest Sandwurm rolling-upgrade cell.

Follow-up: ADR 0153 and `2026-08-24-sandwurm-provider-rolling.md` subsequently accepted that separate
live cell on direct UDP and forced TCP. The nonclaim above remains true of this flake receipt when it
is considered alone.
