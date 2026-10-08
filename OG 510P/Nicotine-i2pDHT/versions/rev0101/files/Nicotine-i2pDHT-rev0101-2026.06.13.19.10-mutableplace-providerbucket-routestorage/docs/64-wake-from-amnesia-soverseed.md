# Wake from amnesia — rev0007 `soverseed-bridgeban-mutualaid`

The cube is a Python-first DHT design lab for an application DHT over I2P.
rev0007 reintroduces the distant Nicotine/legacy-network use case as a pressure source, not as implementation scope.

Remember these decisions:

1. **Clients should become entrance distributors.** Each willing client can hold an I2P Destination, DHT signing key, and signed contact card.
2. **The central path is an entrance ramp, not an authority.** While it exists, clients can exchange DHT contact cards through buddies, rooms, searches, and direct contact.
3. **I2P-only mode should exist and be default off.** It must mean no silent central login.
4. **Garden nodes can bridge back to classic clients.** Bridge service is mutual aid, not new truth authority.
5. **Maintainers can ban keys from official surfaces via signed policy capsules.** This is scoped, subjective, expiring, replaceable policy — not protocol truth.
6. **Mutable records remain central.** Contact-card feeds, seed lists, policy capsules, sync heads, and bridge catalogs can all ride signed mutable slots.

Read next:

```text
docs/56-rev0007-sovereignty-bridgeban-dream.md
docs/57-contact-cards-and-entrance-seeding.md
docs/58-i2p-only-mode-default-off.md
docs/59-classic-client-bridge-from-the-other-side.md
docs/60-subjective-key-ban-and-authority.md
docs/63-python-surface-sovereignty-bridgeban.md
```

Verification lane:

```bash
python scripts/evidence/check_surfaces.py
python scripts/evidence/run_micro_simulation.py
python -m pytest -q
python -m compileall -q src tests scripts
```
