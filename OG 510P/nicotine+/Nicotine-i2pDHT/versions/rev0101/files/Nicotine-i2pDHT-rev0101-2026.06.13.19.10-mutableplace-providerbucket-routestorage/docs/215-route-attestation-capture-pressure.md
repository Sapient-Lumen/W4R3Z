# Route attestation and contact lease pressure

Contact leases make entrances fresh and bounded, but a fresh lease does not prove an independent path. A captured garden can hand out many fresh contacts and still dominate the introduction channel.

`routeattest.py` adds signed attestations that are:

- bound to a contact lease hash,
- purpose-bound,
- monotonic per attester/lease/purpose,
- fresh with a bounded TTL,
- checked against the lease book,
- pressure-tested for contact-family, attester-family, and path-family diversity.

Attestations are still evidence, not truth. Same-sequence forks, rollback, missing leases, invalid signatures, and path monoculture all trigger continued lookup or quarantine pressure rather than easy acceptance.

Important rule:

```text
Many entrances are not resilient if one path family introduced them all.
```
