# Wake from amnesia — rev0046

rev0046 continues the public-bridge side-effect line from rev0045.

Remember:

- `bridgeepoch` decides whether public bridge epoch windows are locally plausible.
- `keyreceiptlane` checks local authority/key receipt pressure.
- `shadowfire` joins bridge epoch, key receipts, policy, authority receipts, and announcement repair.
- `moderationquarantine` adds subjective scoped blocks/watches/warnings.
- `redresslane` adds scoped appeal/counter-evidence receipts.
- `bridgeledger` records the exact joined boundary before future side effects.

Core rule:

> subjective policy and redress are local evidence surfaces, not DHT consensus.
