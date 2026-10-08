# Routing anchor after record ingress

`routinganchor.py` handles the contact side of the DHT substrate.

A routing/contact record must bind:

```text
accepted routing/garden_seed record ingress
+ signed contact lease
+ signed route attestation
+ I2P Destination digest
+ expected node-id digest
+ unexpired purpose-bound lease
+ contact / introducer / path diversity
```

Raw-IP endpoints and native-transport attempts are rejected. This keeps the returned substrate I2P-shaped instead of silently drifting back toward ordinary IP transport or the recently closed native branch.
