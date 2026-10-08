# Bridge shadow final side-effect gate

`bridgeshadow.py` treats public bridge publication as a separate boundary after earlier reports passed.

The gate requires four component reports:

```text
publication_guard
publication_ledger
audit_quorum
bridge_quench
```

The component reports must all bind to the same:

```text
profile_id
service_name
scope_digest
request_digest
```

The bridge-shadow capsule then signs:

```text
intent
profile/service/scope/request
publication payload digest
component-root digest
sequence
previous shadow digest
validity window
TTL
family/path hints
```

This catches a class of subtle mistakes where each component is locally valid but the final side effect accidentally combines a policy report from one request, a quench report from another, and a publication payload from a third.

The cube still does not send anything to SAM/I2P.  This is a no-network side-effect shadow.
