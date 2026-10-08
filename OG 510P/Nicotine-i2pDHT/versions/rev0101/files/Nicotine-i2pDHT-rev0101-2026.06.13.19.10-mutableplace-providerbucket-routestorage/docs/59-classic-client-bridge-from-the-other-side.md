# Classic-client bridge from the other side

A healthy I2P DHT should eventually serve people who have not migrated.
That does not require pretending to be the original central service.
It means offering a compatibility bridge that classic clients can knowingly point at.

## Bridge modes

```text
OFF
LOCALHOST_COMPAT_SHIM
PRIVATE_INVITE_GATEWAY
PUBLIC_GARDEN_GATEWAY
```

### Localhost compat shim

A local process speaks enough of a classic server/client protocol to an old client running on the same machine and translates requests into DHT lookups.
This is the safest first bridge.
It avoids public exposure and gives old clients a testing path.

### Private invite gateway

A garden node accepts a small number of invited classic clients.
This is useful for communities and friends.
Write surfaces require invites.
The bridge can rate-limit, tag translated results, and refuse bad keys.

### Public garden gateway

A high-resource garden runs a public compatibility surface.
This is valuable but dangerous.
It needs rate limits, policy capsules, logs/receipts for operator diagnostics, refusal semantics, and abuse handling.

## Translation surface

| Classic-ish operation | DHT translation guess | Risk |
|---|---|---:|
| login compat | local/session identity only | Low |
| search | provider lookup + optional garden aggregation | Medium/high |
| browse | contact/card lookup + peer connection | Medium |
| peer connect | I2P stream to DHT contact | Medium |
| chat relay | optional, metadata-heavy | High |
| provider announce | signed provider record, invite-gated | High |

Search and provider announce are the dangerous parts.
A bridge that lets arbitrary classic clients inject provider records will become poison bait.
The first public bridge should probably be read-mostly.

## Guardrails

```text
bridge is optional and default off
bridge answers are translated gateway results
bridge is not DHT truth
public write surfaces need invite/rate limits
policy capsules may refuse bridge access
classic clients should see that they are using a gateway
I2P-only mode never requires a bridge
```

## Why this is mutual aid

The DHT asks legacy users to seed entrances.
In return, gardens can serve legacy clients from the DHT side.
That pays down the original sin without destroying the thing that still works.
